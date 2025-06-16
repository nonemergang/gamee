import pygame
from ecs.components.components import Position, Velocity, Player, Sprite, Collider, Health, Weapon

def create_player_texture():
    """Создает текстуру игрока"""
    size = 24
    texture = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Основное тело (синее)
    pygame.draw.circle(texture, (50, 100, 200), (size//2, size//2), size//2)
    
    # Глаза (белые с черными зрачками)
    eye_size = size // 6
    eye_offset = size // 4
    
    # Левый глаз
    pygame.draw.circle(texture, (255, 255, 255), (size//2 - eye_offset, size//2 - eye_offset), eye_size)
    pygame.draw.circle(texture, (0, 0, 0), (size//2 - eye_offset, size//2 - eye_offset), eye_size // 2)
    
    # Правый глаз
    pygame.draw.circle(texture, (255, 255, 255), (size//2 + eye_offset, size//2 - eye_offset), eye_size)
    pygame.draw.circle(texture, (0, 0, 0), (size//2 + eye_offset, size//2 - eye_offset), eye_size // 2)
    
    # Рот (черный)
    pygame.draw.arc(texture, (0, 0, 0), (size//4, size//2, size//2, size//2), 0, 3.14, 2)
    
    return texture

def create_player(world, x, y):
    """
    Создает игрока
    :param world: Мир ECS
    :param x: Позиция X
    :param y: Позиция Y
    :return: ID созданного игрока
    """
    # Создаем сущность
    player_id = world.create_entity()
    
    # Создаем текстуру игрока
    player_texture = create_player_texture()
    
    # Добавляем компоненты
    world.add_component(player_id, Position(x, y))
    world.add_component(player_id, Velocity())
    world.add_component(player_id, Player(speed=150))
    world.add_component(player_id, Sprite(image=player_texture, width=24, height=24, layer=4))
    world.add_component(player_id, Collider(width=20, height=20))
    world.add_component(player_id, Health(maximum=100, current=100, regeneration_rate=5, regeneration_interval=3.0))
    world.add_component(player_id, Weapon(damage=20, fire_rate=5, bullet_speed=400, max_ammo=30))
    
    return player_id 