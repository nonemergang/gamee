import pygame
from ecs.components.components import Position, Velocity, Player, Sprite, Collider, Health, Weapon
from ecs.utils.sprite_manager import sprite_manager

def create_player_texture():
    """
    Возвращает текстуру игрока из менеджера спрайтов или создает дефолтную
    """
    return sprite_manager.get_sprite("player")

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
    
    # Получаем текстуру игрока
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