import pygame
import sys
import random
import time
from pygame.locals import *
from ecs.world import World
from ecs.systems.render_system import RenderSystem
from ecs.systems.movement_system import MovementSystem
from ecs.systems.player_control_system import PlayerControlSystem
from ecs.systems.collision_system import CollisionSystem
from ecs.systems.enemy_system import EnemySystem
from ecs.systems.weapon_system import WeaponSystem
from ecs.systems.camera_system import CameraSystem
from ecs.factories.player_factory import create_player
from ecs.factories.level_factory import create_level
from ecs.factories.enemy_factory import create_enemy
from ecs.components.components import Position, Tile, Player, GameProgress
from ecs.systems.enemy_ai_system import EnemyAISystem
from ecs.systems.health_system import HealthSystem
from ecs.systems.lighting_system import LightingSystem
from ecs.systems.portal_system import PortalSystem
from ecs.systems.direction_indicator_system import DirectionIndicatorSystem
from ecs.systems.minimap_system import MinimapSystem
from ecs.utils.sprite_manager import sprite_manager

# Инициализация Pygame
pygame.init()

# Настройки окна
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Рогалик в лабиринте")

# Загружаем спрайты
sprite_manager.load_sprites()

# Создаем мир ECS
world = World()

# Создаем системы
camera_system = CameraSystem(world, screen_width, screen_height)
render_system = RenderSystem(world, screen, camera_system)
movement_system = MovementSystem(world)
player_control_system = PlayerControlSystem(world)
collision_system = CollisionSystem(world)
enemy_system = EnemySystem(world)
weapon_system = WeaponSystem(world, screen)
enemy_ai_system = EnemyAISystem(world)
health_system = HealthSystem(world, screen)
lighting_system = LightingSystem(world, screen)
portal_system = PortalSystem(world)
direction_indicator_system = DirectionIndicatorSystem(world, screen, camera_system)
minimap_system = MinimapSystem(world, screen)

# Добавляем системы в мир в порядке их выполнения
world.add_system(player_control_system)
world.add_system(enemy_ai_system)
world.add_system(movement_system)
world.add_system(collision_system)
world.add_system(enemy_system)
world.add_system(weapon_system)
world.add_system(health_system)
world.add_system(portal_system)
world.add_system(camera_system)
world.add_system(lighting_system)
world.add_system(direction_indicator_system)
world.add_system(minimap_system)
world.add_system(render_system)

# Устанавливаем систему оружия для PlayerControlSystem
player_control_system.set_weapon_system(weapon_system)

# Создаем шрифт для отображения FPS и прогресса
fps_font = pygame.font.SysFont(None, 24)
ui_font = pygame.font.SysFont(None, 32)

def reset_game():
    """Сбрасывает игру и создает новый уровень"""
    # Удаляем все сущности
    world.clear_entities()
    
    # Создаем новый уровень (лабиринт)
    level_width = 30  # Увеличенный размер лабиринта для гарантированного создания выхода
    level_height = 30
    level_entities = create_level(world, level_width, level_height)
    
    # Находим начальную позицию (вход в лабиринт)
    entrance_pos = None
    for entity_id in level_entities:
        if world.has_component(entity_id, Tile):
            tile = world.get_component(entity_id, Tile)
            if tile.name == "entrance":
                entrance_pos = world.get_component(entity_id, Position)
                break
    
    # Если не нашли вход, ищем любую проходимую позицию
    if not entrance_pos:
        walkable_positions = []
        for entity_id in level_entities:
            if world.has_component(entity_id, Tile):
                tile = world.get_component(entity_id, Tile)
                if tile.walkable:
                    pos = world.get_component(entity_id, Position)
                    walkable_positions.append((pos.x, pos.y))
        
        if walkable_positions:
            # Выбираем случайную проходимую позицию
            x, y = random.choice(walkable_positions)
            entrance_pos = Position(x, y)
        else:
            # Если не нашли проходимых позиций, используем дефолтную
            entrance_pos = Position(100, 100)
    
    # Создаем игрока
    player_id = create_player(world, entrance_pos.x, entrance_pos.y)
    
    # Создаем врагов в случайных местах
    enemy_count = 3  # Начальное количество врагов
    floor_tiles = []
    
    # Собираем все проходимые тайлы
    for entity_id in level_entities:
        if world.has_component(entity_id, Tile):
            tile = world.get_component(entity_id, Tile)
            if tile.walkable and tile.name == "floor":
                pos = world.get_component(entity_id, Position)
                floor_tiles.append((pos.x, pos.y))
    
    # Создаем врагов на случайных проходимых тайлах
    if floor_tiles:
        for _ in range(enemy_count):
            # Выбираем случайную позицию
            x, y = random.choice(floor_tiles)
            
            # Проверяем, что позиция достаточно далеко от игрока
            player_pos = world.get_component(player_id, Position)
            distance = ((x - player_pos.x) ** 2 + (y - player_pos.y) ** 2) ** 0.5
            
            # Если позиция слишком близко к игроку, пробуем другую
            attempts = 0
            while distance < 200 and attempts < 10:
                x, y = random.choice(floor_tiles)
                distance = ((x - player_pos.x) ** 2 + (y - player_pos.y) ** 2) ** 0.5
                attempts += 1
            
            # Создаем врага
            create_enemy(world, x, y)
    
    # Устанавливаем камеру на игрока
    camera_system.follow(player_id)
    
    # Создаем компонент прогресса игры
    game_progress = GameProgress()
    
    # Передаем компонент прогресса в систему порталов
    if hasattr(portal_system, 'game_progress'):
        portal_system.game_progress = game_progress

# Инициализация игры
reset_game()

# Основной игровой цикл
clock = pygame.time.Clock()
running = True
show_fps = True
show_help = False
target_fps = 60
frame_times = []  # Для расчета скользящего среднего FPS

while running:
    # Замеряем время начала кадра
    frame_start_time = time.time()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Сброс игры при нажатии R
                reset_game()
            elif event.key == pygame.K_F1:
                # Включение/выключение режима отладки
                player_control_system.debug_mode = not player_control_system.debug_mode
                print(f"Режим отладки: {'включен' if player_control_system.debug_mode else 'выключен'}")
            elif event.key == pygame.K_F2:
                # Включение/выключение отображения FPS
                show_fps = not show_fps
            elif event.key == pygame.K_h:
                # Включение/выключение справки
                show_help = not show_help
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                # Увеличение масштаба камеры
                current_zoom = camera_system.get_zoom()
                camera_system.set_zoom(current_zoom + 0.5)
                print(f"Масштаб камеры: {camera_system.get_zoom():.1f}x")
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                # Уменьшение масштаба камеры
                current_zoom = camera_system.get_zoom()
                camera_system.set_zoom(current_zoom - 0.5)
                print(f"Масштаб камеры: {camera_system.get_zoom():.1f}x")
        elif event.type == pygame.VIDEORESIZE:
            # Обновляем поверхность затемнения при изменении размера окна
            render_system.update_darkness_surface()
    
    # Получаем время, прошедшее с последнего кадра
    dt = clock.tick(target_fps) / 1000.0  # Конвертируем миллисекунды в секунды
    
    # Обновляем все системы
    world.update(dt)
    
    # Отрисовываем все системы
    screen.fill((0, 0, 0))  # Очищаем экран
    
    # Вызываем методы render для всех систем
    for system in world.systems:
        if hasattr(system, 'render'):
            system.render(camera_system)
    
    # Отображаем FPS
    if show_fps:
        # Вычисляем скользящее среднее FPS
        frame_time = time.time() - frame_start_time
        frame_times.append(frame_time)
        if len(frame_times) > 30:  # Усредняем по последним 30 кадрам
            frame_times.pop(0)
        avg_frame_time = sum(frame_times) / len(frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Отображаем FPS
        fps_text = f"FPS: {fps:.1f}"
        fps_surface = fps_font.render(fps_text, True, (255, 255, 255))
        screen.blit(fps_surface, (10, 10))
    
    # Отображаем прогресс игры
    if hasattr(portal_system, 'game_progress'):
        progress = portal_system.game_progress
        
        # Отображаем информацию о прогрессе в верхнем правом углу
        level_text = f"Уровень: {progress.level}"
        score_text = f"Счет: {progress.total_score}"
        kills_text = f"Убито: {progress.enemies_killed}"
        
        level_surface = ui_font.render(level_text, True, (255, 255, 255))
        score_surface = ui_font.render(score_text, True, (255, 255, 255))
        kills_surface = ui_font.render(kills_text, True, (255, 255, 255))
        
        screen.blit(level_surface, (screen_width - 200, 10))
        screen.blit(score_surface, (screen_width - 200, 40))
        screen.blit(kills_surface, (screen_width - 200, 70))
    
    # Отображаем справку
    if show_help:
        help_texts = [
            "Управление:",
            "WASD - Движение",
            "ЛКМ - Стрельба",
            "R - Перезапуск игры",
            "F1 - Режим отладки",
            "F2 - Показать/скрыть FPS",
            "H - Показать/скрыть справку",
            "+/- - Изменить масштаб",
            "ESC - Выход"
        ]
        
        # Создаем полупрозрачный фон для справки
        help_surface = pygame.Surface((300, 30 * len(help_texts)), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 180))
        
        # Отрисовываем текст справки
        for i, text in enumerate(help_texts):
            text_surface = ui_font.render(text, True, (255, 255, 255))
            help_surface.blit(text_surface, (10, 10 + i * 30))
        
        # Отображаем справку в правом нижнем углу
        screen.blit(help_surface, (screen_width - 310, screen_height - 10 - 30 * len(help_texts)))
    
    # Обновляем экран
    pygame.display.flip()

# Завершение работы
pygame.quit()
sys.exit() 