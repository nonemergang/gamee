import random
from ecs.components.components import Position, Sprite, Collider, Tile

def create_level(world, width, height):
    """
    Создает уровень игры
    :param world: Мир ECS
    :param width: Ширина уровня в тайлах
    :param height: Высота уровня в тайлах
    :return: Список ID созданных сущностей
    """
    tile_size = 32
    level_entities = []
    
    # Генерируем карту уровня
    level_map = _generate_level_map(width, height)
    
    # Создаем тайлы
    for y in range(height):
        for x in range(width):
            tile_type = level_map[y][x]
            
            # Пропускаем пустые тайлы
            if tile_type == 0:
                continue
            
            # Создаем сущность тайла
            tile_id = world.create_entity()
            
            # Определяем параметры тайла
            if tile_type == 1:  # Стена
                color = (100, 100, 100)
                walkable = False
                layer = 1
                tile_name = "wall"
            elif tile_type == 2:  # Пол
                color = (200, 200, 200)
                walkable = True
                layer = 0
                tile_name = "floor"
            else:
                color = (150, 150, 150)
                walkable = True
                layer = 0
                tile_name = "unknown"
            
            # Добавляем компоненты
            world.add_component(tile_id, Tile(tile_name, walkable))
            world.add_component(tile_id, Position(x * tile_size + tile_size / 2, y * tile_size + tile_size / 2))
            world.add_component(tile_id, Sprite(width=tile_size, height=tile_size, color=color, layer=layer))
            
            # Если тайл непроходимый, добавляем коллайдер
            if not walkable:
                world.add_component(tile_id, Collider(width=tile_size, height=tile_size))
            
            level_entities.append(tile_id)
    
    return level_entities

def _generate_level_map(width, height):
    """
    Генерирует карту уровня
    :param width: Ширина карты
    :param height: Высота карты
    :return: Двумерный массив с типами тайлов
    """
    # Создаем пустую карту
    level_map = [[0 for _ in range(width)] for _ in range(height)]
    
    # Заполняем карту полом
    for y in range(height):
        for x in range(width):
            level_map[y][x] = 2  # Пол
    
    # Добавляем стены по периметру
    for x in range(width):
        level_map[0][x] = 1  # Верхняя стена
        level_map[height-1][x] = 1  # Нижняя стена
    
    for y in range(height):
        level_map[y][0] = 1  # Левая стена
        level_map[y][width-1] = 1  # Правая стена
    
    # Добавляем случайные стены внутри уровня
    for _ in range(int(width * height * 0.1)):  # 10% от общего количества тайлов
        x = random.randint(2, width - 3)
        y = random.randint(2, height - 3)
        
        # Создаем небольшие кластеры стен
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if random.random() < 0.7:  # 70% шанс создания стены в кластере
                    nx, ny = x + dx, y + dy
                    if 0 < nx < width - 1 and 0 < ny < height - 1:
                        level_map[ny][nx] = 1
    
    return level_map 