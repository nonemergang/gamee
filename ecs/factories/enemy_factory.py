import pygame
from ecs.components.components import Enemy, Position, Velocity, Sprite, Collider, Health

def create_enemy_texture(enemy_type):
    """
    Создает текстуру врага в зависимости от типа
    :param enemy_type: Тип врага (basic, fast, tank)
    :return: Текстура врага
    """
    size = 32
    texture = pygame.Surface((size, size), pygame.SRCALPHA)
    
    if enemy_type == "basic":
        # Основной враг (красный)
        pygame.draw.circle(texture, (200, 50, 50), (size//2, size//2), size//2 - 2)
        # Внутренний круг
        pygame.draw.circle(texture, (220, 70, 70), (size//2, size//2), size//3)
        # Глаза
        pygame.draw.circle(texture, (255, 255, 255), (size//2 - 5, size//2 - 5), 3)
        pygame.draw.circle(texture, (255, 255, 255), (size//2 + 5, size//2 - 5), 3)
        pygame.draw.circle(texture, (0, 0, 0), (size//2 - 5, size//2 - 5), 1)
        pygame.draw.circle(texture, (0, 0, 0), (size//2 + 5, size//2 - 5), 1)
        # Рот
        pygame.draw.arc(texture, (0, 0, 0), (size//4, size//2, size//2, size//3), 0, 3.14, 2)
    
    elif enemy_type == "fast":
        # Быстрый враг (оранжевый)
        pygame.draw.circle(texture, (255, 150, 0), (size//2, size//2), size//2 - 2)
        # Внутренний круг
        pygame.draw.circle(texture, (255, 180, 50), (size//2, size//2), size//3)
        # Глаза
        pygame.draw.circle(texture, (255, 255, 255), (size//2 - 4, size//2 - 4), 2)
        pygame.draw.circle(texture, (255, 255, 255), (size//2 + 4, size//2 - 4), 2)
        pygame.draw.circle(texture, (0, 0, 0), (size//2 - 4, size//2 - 4), 1)
        pygame.draw.circle(texture, (0, 0, 0), (size//2 + 4, size//2 - 4), 1)
        # Рот (ухмылка)
        pygame.draw.arc(texture, (0, 0, 0), (size//4, size//2 - size//6, size//2, size//3), 0, 3.14, 2)
    
    elif enemy_type == "tank":
        # Танк-враг (темно-красный)
        pygame.draw.circle(texture, (150, 30, 30), (size//2, size//2), size//2 - 2)
        # Внутренний круг
        pygame.draw.circle(texture, (170, 40, 40), (size//2, size//2), size//3)
        # Глаза
        pygame.draw.circle(texture, (255, 255, 255), (size//2 - 6, size//2 - 6), 4)
        pygame.draw.circle(texture, (255, 255, 255), (size//2 + 6, size//2 - 6), 4)
        pygame.draw.circle(texture, (0, 0, 0), (size//2 - 6, size//2 - 6), 2)
        pygame.draw.circle(texture, (0, 0, 0), (size//2 + 6, size//2 - 6), 2)
        # Рот (злой)
        pygame.draw.line(texture, (0, 0, 0), (size//3, size//2 + 5), (size*2//3, size//2 + 5), 2)
    
    else:
        # Стандартный враг
        pygame.draw.circle(texture, (200, 50, 50), (size//2, size//2), size//2 - 2)
    
    return texture

def create_enemy(world, x, y, enemy_type="basic"):
    """
    Создает сущность врага
    :param world: Мир ECS
    :param x: Начальная позиция X
    :param y: Начальная позиция Y
    :param enemy_type: Тип врага (basic, fast, tank)
    :return: ID созданной сущности
    """
    # Создаем сущность
    enemy_id = world.create_entity()
    
    # Настройки в зависимости от типа врага
    if enemy_type == "basic":
        speed = 100
        health = 30
        damage = 10
        width = 32
        height = 32
    elif enemy_type == "fast":
        speed = 150
        health = 20
        damage = 5
        width = 24
        height = 24
    elif enemy_type == "tank":
        speed = 70
        health = 60
        damage = 15
        width = 40
        height = 40
    else:
        # Стандартный враг
        speed = 100
        health = 30
        damage = 10
        width = 32
        height = 32
    
    # Создаем текстуру врага
    enemy_texture = create_enemy_texture(enemy_type)
    
    # Добавляем компоненты
    world.add_component(enemy_id, Enemy(enemy_type, speed, health, damage))
    world.add_component(enemy_id, Position(x, y))
    world.add_component(enemy_id, Velocity(0, 0))
    world.add_component(enemy_id, Sprite(image=enemy_texture, width=width, height=height, layer=5))
    world.add_component(enemy_id, Collider(width=width-4, height=height-4))  # Коллайдер немного меньше текстуры
    world.add_component(enemy_id, Health(health, health))
    
    return enemy_id 