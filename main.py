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
from ecs.components.components import Position, Tile, Player, GameProgress, Health, Velocity
from ecs.systems.enemy_ai_system import EnemyAISystem
from ecs.systems.health_system import HealthSystem
from ecs.systems.lighting_system import LightingSystem
from ecs.systems.portal_system import PortalSystem
from ecs.systems.direction_indicator_system import DirectionIndicatorSystem
from ecs.systems.minimap_system import MinimapSystem
from ecs.systems.menu_system import MenuSystem
from ecs.utils.sprite_manager import sprite_manager

# Состояния игры
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2

# Инициализация Pygame
pygame.init()

# Настройки окна
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Рогалик в лабиринте")

# Загружаем спрайты
sprite_manager.load_sprites()

# Создаем мир ECS
world = World()

# Создаем компонент прогресса игры (должен быть доступен глобально)
game_progress = GameProgress()

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
portal_system = PortalSystem(world)
direction_indicator_system = DirectionIndicatorSystem(world, screen, camera_system)
minimap_system = MinimapSystem(world, screen)
lighting_system = LightingSystem(world, screen, camera_system)

# Создаем систему меню
menu_system = MenuSystem(screen)

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
world.add_system(direction_indicator_system)
world.add_system(minimap_system)
world.add_system(render_system)
world.add_system(lighting_system)

# Устанавливаем систему оружия для PlayerControlSystem
player_control_system.set_weapon_system(weapon_system)

# Создаем шрифт для отображения FPS и прогресса
fps_font = pygame.font.SysFont(None, 24)
ui_font = pygame.font.SysFont(None, 24)

# Текущее состояние игры (начинаем с меню)
game_state = GAME_STATE_MENU
menu_system.show_start()

def reset_game():
    """Сбрасывает игру и создает новый уровень"""
    global game_progress
    
    # Удаляем все сущности
    world.clear_entities()
    
    # Сбрасываем прогресс игры
    game_progress.reset()
    
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
    
    # Передаем компонент прогресса в систему порталов
    portal_system.game_progress = game_progress
    
    # Помечаем кэш стен как устаревший, чтобы обновить его
    if hasattr(lighting_system, 'wall_cache_dirty'):
        lighting_system.wall_cache_dirty = True
        
    print(f"Игра сброшена. Прогресс: уровень={game_progress.level}, счет={game_progress.total_score}, убито={game_progress.enemies_killed}")

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
    
    # Получаем список событий
    events = pygame.event.get()
    
    # Обработка событий выхода из игры
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    
    # Обработка меню
    if game_state == GAME_STATE_MENU:
        menu_action = menu_system.update(events)
        
        if menu_action == 'start_game':
            # Начинаем игру
            reset_game()
            game_state = GAME_STATE_PLAYING
            menu_system.hide()
        elif menu_action == 'exit_game':
            # Выходим из игры
            running = False
        
        # Отрисовываем меню
        menu_system.render()
        pygame.display.flip()
        continue  # Пропускаем остальную часть цикла
    
    # Обработка экрана окончания игры
    elif game_state == GAME_STATE_GAME_OVER:
        print("Отображаем экран Game Over")
        menu_action = menu_system.update(events)
        
        if menu_action == 'restart_game':
            # Перезапускаем игру
            reset_game()
            game_state = GAME_STATE_PLAYING
            menu_system.hide()
        elif menu_action == 'exit_game':
            # Выходим из игры
            running = False
        
        # Отрисовываем экран окончания игры
        menu_system.render()
        pygame.display.flip()
        continue  # Пропускаем остальную часть цикла
    
    # Игровой процесс
    elif game_state == GAME_STATE_PLAYING:
        # Обработка событий
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Вместо выхода из игры показываем меню
                    game_state = GAME_STATE_MENU
                    menu_system.show_start()
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
                # Настройка фонарика
                elif event.key == pygame.K_1:
                    # Увеличение угла обзора фонарика
                    if hasattr(lighting_system, 'fov'):
                        lighting_system.fov = min(360, lighting_system.fov + 10)
                        lighting_system.update_ray_angles()
                        print(f"Угол обзора фонарика: {lighting_system.fov}°")
                elif event.key == pygame.K_2:
                    # Уменьшение угла обзора фонарика
                    if hasattr(lighting_system, 'fov'):
                        lighting_system.fov = max(30, lighting_system.fov - 10)
                        lighting_system.update_ray_angles()
                        print(f"Угол обзора фонарика: {lighting_system.fov}°")
                elif event.key == pygame.K_3:
                    # Увеличение дальности фонарика
                    if hasattr(lighting_system, 'max_ray_length'):
                        lighting_system.max_ray_length += 50
                        print(f"Дальность фонарика: {lighting_system.max_ray_length}")
                elif event.key == pygame.K_4:
                    # Уменьшение дальности фонарика
                    if hasattr(lighting_system, 'max_ray_length'):
                        lighting_system.max_ray_length = max(100, lighting_system.max_ray_length - 50)
                        print(f"Дальность фонарика: {lighting_system.max_ray_length}")
                elif event.key == pygame.K_5:
                    # Увеличение интенсивности мерцания
                    if hasattr(lighting_system, 'flicker_intensity'):
                        lighting_system.flicker_intensity = min(0.5, lighting_system.flicker_intensity + 0.05)
                        print(f"Интенсивность мерцания: {lighting_system.flicker_intensity:.2f}")
                elif event.key == pygame.K_6:
                    # Уменьшение интенсивности мерцания
                    if hasattr(lighting_system, 'flicker_intensity'):
                        lighting_system.flicker_intensity = max(0, lighting_system.flicker_intensity - 0.05)
                        print(f"Интенсивность мерцания: {lighting_system.flicker_intensity:.2f}")
                elif event.key == pygame.K_7:
                    # Увеличение затемнения
                    if hasattr(lighting_system, 'darkness_alpha'):
                        lighting_system.darkness_alpha = min(255, lighting_system.darkness_alpha + 10)
                        print(f"Затемнение: {lighting_system.darkness_alpha}")
                elif event.key == pygame.K_8:
                    # Уменьшение затемнения
                    if hasattr(lighting_system, 'darkness_alpha'):
                        lighting_system.darkness_alpha = max(0, lighting_system.darkness_alpha - 10)
                        print(f"Затемнение: {lighting_system.darkness_alpha}")
                elif event.key == pygame.K_9:
                    # Переключение режима "только свет вокруг игрока"
                    if hasattr(lighting_system, 'use_only_player_light'):
                        lighting_system.set_player_light_only(not lighting_system.use_only_player_light)
                        mode = "включен" if lighting_system.use_only_player_light else "выключен"
                        print(f"Режим 'только свет вокруг игрока': {mode}")
                elif event.key == pygame.K_0:
                    # Увеличение радиуса света вокруг игрока
                    if hasattr(lighting_system, 'player_light_radius'):
                        lighting_system.increase_player_light_radius(20)
                        print(f"Радиус света вокруг игрока: {lighting_system.player_light_radius}")
                elif event.key == pygame.K_BACKSPACE:
                    # Уменьшение радиуса света вокруг игрока
                    if hasattr(lighting_system, 'player_light_radius'):
                        lighting_system.decrease_player_light_radius(20)
                        print(f"Радиус света вокруг игрока: {lighting_system.player_light_radius}")
                # Тестовая кнопка для проверки экрана смерти
                elif event.key == pygame.K_F12:
                    # Тестовое убийство игрока
                    player_entities = world.get_entities_with_components(Player, Health)
                    if player_entities:
                        player_id = player_entities[0]
                        player_health = world.get_component(player_id, Health)
                        player_health.current = 0
                        print("Тестовое убийство игрока")
            elif event.type == pygame.VIDEORESIZE:
                # Обновляем поверхность затемнения при изменении размера окна
                render_system.update_darkness_surface()
        
        # Получаем время, прошедшее с последнего кадра
        dt = clock.tick(target_fps) / 1000.0  # Конвертируем миллисекунды в секунды
        
        # Обновляем все системы
        world.update(dt)
        
        # Проверяем, жив ли игрок
        player_entities = world.get_entities_with_components(Player, Health)
        if player_entities:
            player_id = player_entities[0]
            player_health = world.get_component(player_id, Health)
            
            if player_health.current <= 0:
                # Игрок умер, показываем экран окончания игры
                print("Обнаружена смерть игрока! Переключаем на экран Game Over")
                game_state = GAME_STATE_GAME_OVER
                menu_system.show_game_over_screen(
                    game_progress.total_score, 
                    game_progress.level, 
                    game_progress.enemies_killed
                )
                print(f"Установлен game_state={game_state}, show_game_over={menu_system.show_game_over}")
                # Убедимся, что игрок не может двигаться после смерти
                if world.has_component(player_id, Velocity):
                    velocity = world.get_component(player_id, Velocity)
                    velocity.dx = 0
                    velocity.dy = 0
                continue
        
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
        
        # Отображаем справку, если она включена
        if show_help:
            help_texts = [
                "Управление:",
                "WASD - движение",
                "ЛКМ - стрелять",
                "R - сбросить игру",
                "F1 - режим отладки",
                "F2 - показать/скрыть FPS",
                "H - показать/скрыть справку",
                "+/- - изменить масштаб",
                "",
                "Настройка фонарика:",
                "1/2 - увеличить/уменьшить угол обзора",
                "3/4 - увеличить/уменьшить дальность",
                "5/6 - увеличить/уменьшить мерцание",
                "7/8 - увеличить/уменьшить затемнение",
                "9 - включить/выключить режим 'только свет вокруг игрока'",
                "0/Backspace - увеличить/уменьшить радиус света вокруг игрока"
            ]
            
            y_offset = 50
            for text in help_texts:
                help_surface = ui_font.render(text, True, (255, 255, 255))
                screen.blit(help_surface, (screen_width - 350, y_offset))
                y_offset += 25
    
    # Обновляем экран
    pygame.display.flip()

# Завершение работы
pygame.quit()
sys.exit() 