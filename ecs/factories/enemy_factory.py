import pygame
from ecs.components.components import Position, Velocity, Enemy, Sprite, Collider, Health
from ecs.utils.sprite_manager import sprite_manager

def create_enemy_texture():
    """
    Возвращает текстуру врага из менеджера спрайтов или создает дефолтную
    """
    return sprite_manager.get_sprite("enemy")

def create_enemy(world, x, y, enemy_type="basic"):
    """
    Создает врага
    :param world: Мир ECS
    :param x: Позиция X
    :param y: Позиция Y
    :param enemy_type: Тип врага (basic, fast, tank)
    :return: ID созданного врага
    """
    # Создаем сущность
    enemy_id = world.create_entity()
    
    # Определяем параметры в зависимости от типа врага
    if enemy_type == "fast":
        speed = 150
        damage = 5
        health = 50
        detection_radius = 400
        attack_radius = 40
        color = (255, 100, 100)
        sprite_name = "enemy_fast"
    elif enemy_type == "tank":
        speed = 80
        damage = 20
        health = 200
        detection_radius = 300
        attack_radius = 60
        color = (150, 50, 50)
        sprite_name = "enemy_tank"
    else:  # basic
        speed = 100
        damage = 10
        health = 100
        detection_radius = 350
        attack_radius = 50
        color = (200, 50, 50)
        sprite_name = "enemy"
    
    # Пытаемся получить специфичный спрайт для типа врага
    enemy_texture = sprite_manager.get_sprite(sprite_name)
    
    # Если не нашли специфичный спрайт, используем дефолтный
    if enemy_texture is None:
        enemy_texture = create_enemy_texture()
    
    # Добавляем компоненты
    world.add_component(enemy_id, Position(x, y))
    world.add_component(enemy_id, Velocity())
    world.add_component(enemy_id, Enemy(speed=speed, damage=damage, detection_radius=detection_radius, attack_radius=attack_radius))
    world.add_component(enemy_id, Sprite(image=enemy_texture, width=32, height=32, layer=3))
    world.add_component(enemy_id, Collider(width=28, height=28))
    world.add_component(enemy_id, Health(maximum=health, current=health))
    
    return enemy_id 