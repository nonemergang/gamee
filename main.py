import pygame
import sys
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
from ecs.components.components import Position, Tile

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = "Top Down Shooter - Maze"
TILE_SIZE = 32

# Настройка экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Создание мира ECS
world = World()

# Инициализация систем
render_system = RenderSystem(world, screen)
movement_system = MovementSystem(world)
player_control_system = PlayerControlSystem(world)
collision_system = CollisionSystem(world)
enemy_system = EnemySystem(world)
weapon_system = WeaponSystem(world)
camera_system = CameraSystem(world, SCREEN_WIDTH, SCREEN_HEIGHT)

# Добавление систем в мир
world.add_system(player_control_system)
world.add_system(movement_system)
world.add_system(enemy_system)
world.add_system(weapon_system)
world.add_system(collision_system)
world.add_system(camera_system)
world.add_system(render_system)

# Размеры лабиринта
MAZE_WIDTH = 61
MAZE_HEIGHT = 41

# Создание игровых объектов
level_entities = create_level(world, MAZE_WIDTH, MAZE_HEIGHT)

# Находим вход в лабиринт для размещения игрока
entrance_pos = None
exit_pos = None

# Ищем тайлы входа и выхода
for entity_id in level_entities:
    if world.has_component(entity_id, Tile):
        tile = world.get_component(entity_id, Tile)
        pos = world.get_component(entity_id, Position)
        
        if tile.type == "entrance":
            entrance_pos = (pos.x, pos.y)
        elif tile.type == "exit":
            exit_pos = (pos.x, pos.y)

# Создаем игрока у входа в лабиринт
player = None
if entrance_pos:
    player = create_player(world, entrance_pos[0], entrance_pos[1])
else:
    # Если вход не найден, создаем игрока в центре
    player = create_player(world, MAZE_WIDTH * TILE_SIZE // 2, MAZE_HEIGHT * TILE_SIZE // 2)

# Создаем врагов в случайных местах лабиринта
def find_empty_spaces(num_spaces):
    """Находит пустые места для размещения врагов"""
    empty_spaces = []
    
    for entity_id in level_entities:
        if world.has_component(entity_id, Tile):
            tile = world.get_component(entity_id, Tile)
            pos = world.get_component(entity_id, Position)
            
            # Используем только проходимые тайлы, которые не вход и не выход
            if tile.walkable and tile.type not in ["entrance", "exit"]:
                empty_spaces.append((pos.x, pos.y))
    
    # Перемешиваем и берем нужное количество
    import random
    random.shuffle(empty_spaces)
    return empty_spaces[:min(num_spaces, len(empty_spaces))]

# Создаем врагов
enemy_positions = find_empty_spaces(10)  # Создаем 10 врагов
for i, pos in enumerate(enemy_positions):
    # Чередуем типы врагов
    enemy_type = "basic"
    if i % 3 == 1:
        enemy_type = "fast"
    elif i % 3 == 2:
        enemy_type = "tank"
    
    create_enemy(world, pos[0], pos[1], enemy_type)

def main():
    running = True
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        # Обновление систем
        world.update(clock.get_time() / 1000.0)
        
        # Отрисовка
        screen.fill((0, 0, 0))
        world.render()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 