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

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = "Top Down Shooter"

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

# Создание игровых объектов
level = create_level(world, 50, 50)
player = create_player(world, 400, 300)
for i in range(5):
    create_enemy(world, 600 + i * 100, 400)

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