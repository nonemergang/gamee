import pygame
from ecs.components.components import Player, Position, Velocity, Sprite, Collider, Health, Weapon

def create_player_texture():
    """Создает текстуру игрока"""
    size = 32
    texture = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Основное тело (синий круг)
    pygame.draw.circle(texture, (50, 100, 200), (size//2, size//2), size//2 - 2)
    
    # Внутренний круг (светлее)
    pygame.draw.circle(texture, (70, 120, 220), (size//2, size//2), size//3)
    
    # Детали (глаза, оружие и т.д.)
    # Оружие (направлено вправо)
    pygame.draw.rect(texture, (100, 100, 100), (size//2, size//2 - 3, size//2, 6))
    
    return texture

def create_player(world, x, y):
    """
    Создает сущность игрока
    :param world: Мир ECS
    :param x: Начальная позиция X
    :param y: Начальная позиция Y
    :return: ID созданной сущности
    """
    # Создаем сущность
    player_id = world.create_entity()
    
    # Создаем текстуру игрока
    player_texture = create_player_texture()
    
    # Добавляем компоненты
    world.add_component(player_id, Player())
    world.add_component(player_id, Position(x, y))
    world.add_component(player_id, Velocity(0, 0))
    world.add_component(player_id, Sprite(image=player_texture, width=32, height=32, layer=10))
    world.add_component(player_id, Collider(width=28, height=28))  # Коллайдер немного меньше текстуры
    world.add_component(player_id, Health(100, 100))
    world.add_component(player_id, Weapon("pistol", 10, 2.0, 500, 12, 12))
    
    return player_id 