from ecs.components.components import Enemy, Position, Velocity, Sprite, Collider, Health

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
        color = (255, 0, 0)
        width = 32
        height = 32
    elif enemy_type == "fast":
        speed = 150
        health = 20
        damage = 5
        color = (255, 100, 0)
        width = 24
        height = 24
    elif enemy_type == "tank":
        speed = 70
        health = 60
        damage = 15
        color = (150, 0, 0)
        width = 40
        height = 40
    else:
        # Стандартный враг
        speed = 100
        health = 30
        damage = 10
        color = (255, 0, 0)
        width = 32
        height = 32
    
    # Добавляем компоненты
    world.add_component(enemy_id, Enemy(enemy_type, speed, health, damage))
    world.add_component(enemy_id, Position(x, y))
    world.add_component(enemy_id, Velocity(0, 0))
    world.add_component(enemy_id, Sprite(width=width, height=height, color=color, layer=5))
    world.add_component(enemy_id, Collider(width=width, height=height))
    world.add_component(enemy_id, Health(health, health))
    
    return enemy_id 