from ecs.components.components import Player, Position, Velocity, Sprite, Collider, Health, Weapon

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
    
    # Добавляем компоненты
    world.add_component(player_id, Player())
    world.add_component(player_id, Position(x, y))
    world.add_component(player_id, Velocity(0, 0))
    world.add_component(player_id, Sprite(width=32, height=32, color=(0, 255, 0), layer=10))
    world.add_component(player_id, Collider(width=32, height=32))
    world.add_component(player_id, Health(100, 100))
    world.add_component(player_id, Weapon("pistol", 10, 2.0, 500, 12, 12))
    
    return player_id 