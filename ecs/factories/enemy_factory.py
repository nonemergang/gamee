import random
import pygame
from ecs.components.components import Position, Velocity, Enemy, Sprite, Collider, Health, Weapon
from ecs.utils.sprite_manager import sprite_manager

def create_enemy_texture():
    """
    Возвращает текстуру врага из менеджера спрайтов или создает дефолтную
    """
    return sprite_manager.get_sprite("enemy")

def create_enemy(world, x, y, health_multiplier=1.0, damage_multiplier=1.0, speed_multiplier=1.0):
    """
    Создает врага
    :param world: Мир ECS
    :param x: Позиция X
    :param y: Позиция Y
    :param health_multiplier: Множитель здоровья
    :param damage_multiplier: Множитель урона
    :param speed_multiplier: Множитель скорости
    :return: ID созданного врага
    """
    # Создаем сущность
    enemy_id = world.create_entity()
    
    # Базовые характеристики врага
    base_health = 50
    base_damage = 10
    base_speed = 80
    
    # Применяем множители
    health = int(base_health * health_multiplier)
    damage = int(base_damage * damage_multiplier)
    speed = base_speed * speed_multiplier
    
    # Добавляем компоненты
    world.add_component(enemy_id, Position(x, y))
    world.add_component(enemy_id, Velocity())
    world.add_component(enemy_id, Enemy(speed=speed, damage=damage))
    
    # Получаем текстуру врага
    enemy_texture = sprite_manager.get_sprite("enemy")
    
    # Добавляем спрайт
    world.add_component(enemy_id, Sprite(image=enemy_texture, width=32, height=32, layer=2))
    
    # Добавляем коллайдер
    world.add_component(enemy_id, Collider(width=28, height=28))
    
    # Добавляем здоровье
    world.add_component(enemy_id, Health(maximum=health, current=health))
    
    # Некоторые враги могут иметь оружие (с вероятностью 30%)
    if random.random() < 0.3:
        weapon = Weapon(damage=int(5 * damage_multiplier), fire_rate=1, bullet_speed=150)
        weapon.cooldown = 0
        world.add_component(enemy_id, weapon)
    
    return enemy_id 