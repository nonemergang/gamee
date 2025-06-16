import pygame
import sys
import random
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
from ecs.components.components import Position, Tile, Player
from ecs.systems.enemy_ai_system import EnemyAISystem
from ecs.systems.health_system import HealthSystem

# Инициализация Pygame
pygame.init()

# Настройки окна
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Лабиринт с ECS")

# Создаем мир ECS
world = World()

# Регистрируем системы
camera_system = CameraSystem(world, screen_width, screen_height)
render_system = RenderSystem(world, screen, camera_system)
movement_system = MovementSystem(world)
collision_system = CollisionSystem(world)
player_control_system = PlayerControlSystem(world)
enemy_ai_system = EnemyAISystem(world)
weapon_system = WeaponSystem(world)
health_system = HealthSystem(world)

world.add_system(movement_system)
world.add_system(collision_system)
world.add_system(player_control_system)
world.add_system(enemy_ai_system)
world.add_system(camera_system)
world.add_system(render_system)
world.add_system(weapon_system)
world.add_system(health_system)

def reset_game():
    """Сбрасывает игру и создает новый уровень"""
    # Удаляем все сущности
    world.clear_entities()
    
    # Создаем новый уровень (лабиринт)
    level_width = 41  # Увеличенный размер для более сложного лабиринта
    level_height = 41
    level_entities = create_level(world, level_width, level_height)
    
    # Находим начальную позицию (вход в лабиринт)
    entrance_pos = None
    for entity_id in level_entities:
        if world.has_component(entity_id, Tile):
            tile = world.get_component(entity_id, Tile)
            if tile.name == "entrance":
                entrance_pos = world.get_component(entity_id, Position)
                break
    
    # Если не нашли вход, используем случайную позицию
    if not entrance_pos:
        entrance_pos = Position(100, 100)
    
    # Создаем игрока
    player_id = create_player(world, entrance_pos.x, entrance_pos.y)
    
    # Создаем врагов в случайных местах
    enemy_count = 10  # Больше врагов для более сложной игры
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

# Инициализация игры
reset_game()

# Основной игровой цикл
clock = pygame.time.Clock()
running = True

while running:
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
    
    # Получаем время, прошедшее с последнего кадра
    dt = clock.tick(60) / 1000.0  # Конвертируем миллисекунды в секунды
    
    # Обновляем все системы
    world.update(dt)
    
    # Проверяем, жив ли игрок
    player_entities = world.get_entities_with_components(Position, Player)
    if not player_entities:
        # Если игрок умер, сбрасываем игру
        reset_game()
    
    # Обновляем экран
    pygame.display.flip()

# Завершение работы
pygame.quit()
sys.exit() 