import random
import pygame
from ecs.components.components import Position, Sprite, Collider, Tile, Portal, Minimap
from ecs.factories.prim_maze_generator import generate_prim_maze
from ecs.utils.sprite_manager import sprite_manager

# Загружаем текстуры или создаем их
def get_textures():
    """
    Возвращает словарь текстур для тайлов
    """
    textures = {}
    
    # Получаем текстуры из менеджера спрайтов
    textures["wall"] = sprite_manager.get_sprite("wall")
    textures["floor"] = sprite_manager.get_sprite("floor")
    textures["entrance"] = sprite_manager.get_sprite("entrance")
    textures["exit"] = sprite_manager.get_sprite("exit")
    
    # Декоративные элементы
    textures["crack"] = sprite_manager.get_sprite("crack")
    textures["moss"] = sprite_manager.get_sprite("moss")
    
    return textures

def create_level(world, width, height):
    """
    Создает уровень игры
    :param world: Мир ECS
    :param width: Ширина уровня в тайлах
    :param height: Высота уровня в тайлах
    :return: Список ID созданных сущностей
    """
    print(f"Создание уровня {width}x{height}")
    tile_size = 32
    level_entities = []
    
    # Загружаем текстуры
    textures = get_textures()
    
    # Генерируем карту лабиринта с использованием алгоритма Прима
    # Используем базовый лабиринт без расширения коридоров
    level_map = generate_prim_maze(width, height, corridor_width=1)
    
    # Передаем карту уровня в систему ИИ врагов
    enemy_ai_system = next((system for system in world.systems if hasattr(system, 'set_level_map')), None)
    if enemy_ai_system:
        enemy_ai_system.set_level_map(level_map, width, height)
    
    # Подсчитываем типы тайлов в карте
    wall_count = sum(row.count(1) for row in level_map)
    floor_count = sum(row.count(2) for row in level_map)
    entrance_count = sum(row.count(3) for row in level_map)
    exit_count = sum(row.count(4) for row in level_map)
    print(f"Типы тайлов в карте: стены={wall_count}, пол={floor_count}, вход={entrance_count}, выход={exit_count}")
    
    # Проверяем, есть ли выход в карте
    if exit_count == 0:
        print("ОШИБКА: В сгенерированной карте нет выхода! Принудительно создаем его.")
        # Создаем выход принудительно в правом нижнем углу
        x = width - 2
        y = height - 2
        level_map[y][x] = 4  # Устанавливаем тип тайла "выход"
        print(f"Создан выход в позиции ({x}, {y})")
        
        # Убеждаемся, что путь к выходу проходим
        level_map[y-1][x] = 2  # Делаем соседние клетки проходимыми
        level_map[y][x-1] = 2
        exit_count = 1
    
    # Повторно проверяем количество тайлов после возможного исправления
    if exit_count != 1:
        print(f"ВНИМАНИЕ: После проверки количество выходов = {exit_count}")
    
    # Сохраняем координаты входа и выхода для мини-карты
    entrance_pos = None
    exit_pos = None
    
    # Создаем тайлы
    walls_created = 0
    floors_created = 0
    exits_created = 0  # Счетчик созданных выходов
    
    # Выводим карту для отладки
    print("Карта уровня:")
    for row in level_map:
        print(''.join(str(cell) for cell in row))
    
    for y in range(height):
        for x in range(width):
            if y < len(level_map) and x < len(level_map[y]):
                tile_type = level_map[y][x]
            else:
                # Если выходим за пределы карты, создаем стену
                tile_type = 1
            
            # Пропускаем пустые тайлы
            if tile_type == 0:
                continue
            
            # Создаем сущность тайла
            tile_id = world.create_entity()
            
            # Определяем параметры тайла
            if tile_type == 1:  # Стена
                texture = textures["wall"]
                # Добавляем мох к некоторым стенам для разнообразия
                if random.random() < 0.1:
                    texture = texture.copy()
                    texture.blit(textures["moss"], (0, 0))
                walkable = False
                layer = 1
                tile_name = "wall"
                walls_created += 1
            elif tile_type == 2:  # Пол
                texture = textures["floor"]
                # Добавляем трещины к некоторым плиткам пола для разнообразия
                if random.random() < 0.05:
                    texture = texture.copy()
                    texture.blit(textures["crack"], (0, 0))
                walkable = True
                layer = 0
                tile_name = "floor"
                floors_created += 1
            elif tile_type == 3:  # Вход в лабиринт
                texture = textures["entrance"]
                walkable = True
                layer = 0
                tile_name = "entrance"
                entrance_pos = (x, y)  # Сохраняем координаты входа
            elif tile_type == 4:  # Выход из лабиринта (портал на следующий уровень)
                texture = textures["exit"]
                walkable = True
                layer = 0
                tile_name = "exit"
                exit_pos = (x, y)  # Сохраняем координаты выхода
                exits_created += 1  # Увеличиваем счетчик созданных выходов
                
                # Выводим отладочную информацию
                print(f"Создаем портал в позиции ({x}, {y})")
                
                # Увеличиваем размер портала для лучшей видимости
                sprite_width = tile_size * 2
                sprite_height = tile_size * 2
                
                # Add portal component to exit tiles
                portal_component = Portal(destination="next_level", active=True)
                world.add_component(tile_id, Portal(destination="next_level", active=True))
                
                # Добавляем компоненты
                world.add_component(tile_id, Tile(tile_name, walkable))
                position_component = Position(x * tile_size + tile_size / 2, y * tile_size + tile_size / 2)
                world.add_component(tile_id, position_component)
                
                # Создаем увеличенный и яркий спрайт портала
                portal_sprite = Sprite(image=texture, width=sprite_width, height=sprite_height, layer=layer)
                # Делаем портал ярко-фиолетовым для лучшей видимости
                portal_sprite.color_overlay = (255, 0, 255)  # Яркий розовый цвет
                world.add_component(tile_id, portal_sprite)
                
                # Проверяем, добавились ли компоненты
                if world.has_component(tile_id, Portal) and world.has_component(tile_id, Position):
                    print(f"Портал успешно создан. Компоненты: Portal={portal_component}, Position={position_component}")
                else:
                    print("ОШИБКА: Не удалось добавить компоненты к порталу!")
                
                # Пропускаем добавление стандартного спрайта
                level_entities.append(tile_id)
                continue
            else:
                texture = None
                color = (150, 150, 150)
                walkable = True
                layer = 0
                tile_name = "unknown"
            
            # Добавляем компоненты
            world.add_component(tile_id, Tile(tile_name, walkable))
            world.add_component(tile_id, Position(x * tile_size + tile_size / 2, y * tile_size + tile_size / 2))
            
            # Если есть текстура, используем её, иначе используем цвет
            if texture:
                sprite = Sprite(image=texture, width=tile_size, height=tile_size, layer=layer)
            else:
                sprite = Sprite(width=tile_size, height=tile_size, color=color, layer=layer)
            
            world.add_component(tile_id, sprite)
            
            # Если тайл непроходимый, добавляем коллайдер
            if not walkable:
                world.add_component(tile_id, Collider(width=tile_size, height=tile_size))
            
            level_entities.append(tile_id)
    
    # Создаем мини-карту, если найдены вход и выход
    if entrance_pos and exit_pos:
        create_minimap(world, level_map, entrance_pos, exit_pos, width, height)
    
    print(f"Создано тайлов: стены={walls_created}, пол={floors_created}, выходы={exits_created}, всего={len(level_entities)}")
    
    # Проверяем, есть ли порталы в мире
    portal_entities = world.get_entities_with_components(Portal)
    print(f"Порталов в мире после создания уровня: {len(portal_entities)}")
    for portal_id in portal_entities:
        portal = world.get_component(portal_id, Portal)
        position = world.get_component(portal_id, Position)
        print(f"Портал: destination={portal.destination}, active={portal.active}, position=({position.x}, {position.y})")
    
    # Если порталы не были созданы, создаем его принудительно
    if len(portal_entities) == 0:
        print("Порталы не были созданы! Создаем портал принудительно.")
        
        # Создаем сущность для портала
        portal_id = world.create_entity()
        
        # Определяем позицию портала (в правом нижнем углу карты)
        portal_x = (width - 2) * tile_size + tile_size / 2
        portal_y = (height - 2) * tile_size + tile_size / 2
        
        # Добавляем компоненты порталу
        portal_component = Portal(destination="next_level", active=True)
        world.add_component(portal_id, portal_component)
        world.add_component(portal_id, Position(portal_x, portal_y))
        
        # Создаем яркий спрайт для портала
        texture = textures["exit"]
        sprite_width = tile_size * 3  # Делаем портал еще больше для заметности
        sprite_height = tile_size * 3
        portal_sprite = Sprite(image=texture, width=sprite_width, height=sprite_height, layer=2)  # Повышаем слой для отображения поверх других объектов
        portal_sprite.color_overlay = (255, 0, 255)  # Яркий розовый цвет
        world.add_component(portal_id, portal_sprite)
        
        # Добавляем сущность в список
        level_entities.append(portal_id)
        
        print(f"Портал принудительно создан в позиции ({portal_x}, {portal_y})")
        
        # Обновляем список порталов для проверки
        portal_entities = world.get_entities_with_components(Portal)
        print(f"Порталов в мире после принудительного создания: {len(portal_entities)}")
    
    return level_entities

def create_minimap(world, level_map, entrance_pos, exit_pos, width, height):
    """
    Создает мини-карту для игрока, показывающую расположение портала
    :param world: Мир ECS
    :param level_map: Карта уровня
    :param entrance_pos: Координаты входа (x, y)
    :param exit_pos: Координаты выхода (x, y)
    :param width: Ширина карты
    :param height: Высота карты
    """
    # Размеры мини-карты
    minimap_width = 150
    minimap_height = 150
    
    # Создаем поверхность для мини-карты
    minimap_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    minimap_surface.fill((0, 0, 0, 150))  # Полупрозрачный черный фон
    
    # Масштабирование карты для мини-карты
    scale_x = minimap_width / width
    scale_y = minimap_height / height
    
    # Рисуем вход и выход на мини-карте
    # Вход - зеленый круг
    entrance_x = int(entrance_pos[0] * scale_x)
    entrance_y = int(entrance_pos[1] * scale_y)
    pygame.draw.circle(minimap_surface, (0, 255, 0), (entrance_x, entrance_y), 5)
    
    # Выход (портал) - яркий розовый круг
    exit_x = int(exit_pos[0] * scale_x)
    exit_y = int(exit_pos[1] * scale_y)
    pygame.draw.circle(minimap_surface, (255, 0, 255), (exit_x, exit_y), 8)
    
    # Добавляем текст "Вы здесь" и "Портал"
    font = pygame.font.SysFont(None, 16)
    entrance_text = font.render("Вы здесь", True, (0, 255, 0))
    exit_text = font.render("Портал", True, (255, 0, 255))
    
    minimap_surface.blit(entrance_text, (entrance_x - entrance_text.get_width() // 2, entrance_y - 20))
    minimap_surface.blit(exit_text, (exit_x - exit_text.get_width() // 2, exit_y - 20))
    
    # Рисуем линию от входа к выходу
    pygame.draw.line(minimap_surface, (255, 255, 0), (entrance_x, entrance_y), (exit_x, exit_y), 2)
    
    # Создаем сущность для мини-карты
    minimap_id = world.create_entity()
    
    # Добавляем компоненты для мини-карты
    world.add_component(minimap_id, Minimap(surface=minimap_surface))
    
    print(f"Создана мини-карта с входом ({entrance_pos[0]}, {entrance_pos[1]}) и выходом ({exit_pos[0]}, {exit_pos[1]})")

def _generate_prim_maze(width, height, corridor_width=3):
    """
    Генерирует лабиринт с использованием алгоритма Прима
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :param corridor_width: Ширина коридоров (в тайлах)
    :return: Двумерный массив с типами тайлов
    """
    print(f"Генерация лабиринта по алгоритму Прима: {width}x{height}")
    
    # Убедимся, что размеры нечетные для правильной генерации лабиринта
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1
    
    # Создаем карту, заполненную стенами
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    # Функция для проверки, находится ли клетка в пределах лабиринта
    def is_in_bounds(x, y):
        return 0 <= x < width and 0 <= y < height
    
    # Множество ячеек, которые уже являются частью лабиринта
    in_maze = set()
    
    # Список "границ" (стен между ячейками)
    walls = []
    
    # Начинаем с случайной точки (с нечетными координатами)
    start_x = random.randrange(1, width-1, 2)
    start_y = random.randrange(1, height-1, 2)
    
    print(f"Начальная точка: {start_x}, {start_y}")
    
    # Добавляем начальную точку в лабиринт
    in_maze.add((start_x, start_y))
    maze[start_y][start_x] = 2  # Помечаем как проход
    
    # Добавляем стены начальной точки в список
    directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Верх, право, низ, лево
    for dx, dy in directions:
        nx, ny = start_x + dx, start_y + dy
        if is_in_bounds(nx, ny):
            # Добавляем стену и координаты ячейки между текущей и соседней
            walls.append((nx, ny, start_x + dx//2, start_y + dy//2))
    
    print(f"Начальные стены: {len(walls)}")
    
    # Пока есть стены в списке
    while walls:
        # Выбираем случайную стену
        wall_index = random.randint(0, len(walls) - 1)
        cell_x, cell_y, wall_x, wall_y = walls.pop(wall_index)
        
        # Если только одна из ячеек уже в лабиринте
        if (cell_x, cell_y) not in in_maze:
            # Добавляем новую ячейку в лабиринт
            in_maze.add((cell_x, cell_y))
            maze[cell_y][cell_x] = 2  # Помечаем как проход
            
            # Убираем стену между ячейками
            maze[wall_y][wall_x] = 2
            
            # Добавляем стены новой ячейки
            for dx, dy in directions:
                nx, ny = cell_x + dx, cell_y + dy
                if is_in_bounds(nx, ny) and (nx, ny) not in in_maze:
                    # Проверяем, что стена еще не в списке
                    wall_coord = (cell_x + dx//2, cell_y + dy//2)
                    if maze[ny][nx] == 1:  # Если это стена
                        walls.append((nx, ny, wall_coord[0], wall_coord[1]))
    
    print(f"Ячеек в лабиринте: {len(in_maze)}")
    
    # Проверяем, что лабиринт не пустой
    wall_count = sum(row.count(1) for row in maze)
    passage_count = sum(row.count(2) for row in maze)
    print(f"Стен: {wall_count}, Проходов: {passage_count}")
    
    if passage_count < width * height * 0.3:
        print("ВНИМАНИЕ: Лабиринт слишком пустой, используем запасной алгоритм")
        return _generate_maze(width, height)
    
    # Расширяем проходы для создания более широких коридоров
    wide_maze = _widen_corridors(maze, width, height, corridor_width)
    
    # Добавляем комнаты и расширяем некоторые коридоры
    maze = _add_rooms_and_widen_corridors(wide_maze, width, height)
    
    # Создаем вход и выход в лабиринте
    # Ищем проходы по периметру для размещения входа и выхода
    perimeter_passages = []
    
    # Верхняя и нижняя стороны
    for x in range(1, width-1):
        if maze[1][x] == 2:
            perimeter_passages.append((x, 0))
        if maze[height-2][x] == 2:
            perimeter_passages.append((x, height-1))
    
    # Левая и правая стороны
    for y in range(1, height-1):
        if maze[y][1] == 2:
            perimeter_passages.append((0, y))
        if maze[y][width-2] == 2:
            perimeter_passages.append((width-1, y))
    
    # Если не нашли проходы по периметру, создаем их
    if not perimeter_passages:
        print("Не найдены проходы по периметру, создаем искусственно")
        # Создаем вход сверху
        x = random.randrange(1, width-1, 2)
        maze[0][x] = 2
        maze[1][x] = 2
        perimeter_passages.append((x, 0))
        
        # Создаем выход снизу
        x = random.randrange(1, width-1, 2)
        maze[height-1][x] = 2
        maze[height-2][x] = 2
        perimeter_passages.append((x, height-1))
    
    print(f"Найдено проходов по периметру: {len(perimeter_passages)}")
    
    # Выбираем случайные точки для входа и выхода, но убедимся, что они находятся далеко друг от друга
    entrance_candidates = []
    exit_candidates = []
    
    # Разделяем перименты на две половины для входа и выхода
    for pos in perimeter_passages:
        x, y = pos
        # Вход в верхней или левой части
        if x < width // 2 or y < height // 2:
            entrance_candidates.append(pos)
        # Выход в нижней или правой части
        else:
            exit_candidates.append(pos)
    
    # Если одна из групп пуста, перераспределяем кандидатов
    if not entrance_candidates:
        # Берем половину из exit_candidates
        middle = len(exit_candidates) // 2
        entrance_candidates = exit_candidates[:middle]
        exit_candidates = exit_candidates[middle:]
    elif not exit_candidates:
        # Берем половину из entrance_candidates
        middle = len(entrance_candidates) // 2
        exit_candidates = entrance_candidates[middle:]
        entrance_candidates = entrance_candidates[:middle]
    
    print(f"Кандидаты для входа: {len(entrance_candidates)}, для выхода: {len(exit_candidates)}")
    
    # Выбираем случайные точки для входа и выхода
    entrance_pos = random.choice(entrance_candidates)
    exit_pos = random.choice(exit_candidates)
    
    # Устанавливаем вход и выход
    maze[entrance_pos[1]][entrance_pos[0]] = 3  # Вход
    maze[exit_pos[1]][exit_pos[0]] = 4  # Выход
    
    print("Лабиринт успешно сгенерирован")
    return maze

def _widen_corridors(maze, width, height, corridor_width):
    """
    Расширяет коридоры в лабиринте до указанной ширины
    :param maze: Исходный лабиринт
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :param corridor_width: Желаемая ширина коридоров (в тайлах)
    :return: Лабиринт с расширенными коридорами
    """
    print(f"Расширение коридоров до ширины {corridor_width}")
    
    # Создаем копию лабиринта
    wide_maze = [row[:] for row in maze]
    
    # Половина ширины коридора (для расширения в обе стороны)
    half_width = corridor_width // 2
    
    # Проходим по всем клеткам лабиринта
    for y in range(height):
        for x in range(width):
            # Если текущая клетка - проход
            if maze[y][x] == 2:
                # Расширяем проход в обе стороны
                for dy in range(-half_width, half_width + 1):
                    for dx in range(-half_width, half_width + 1):
                        nx, ny = x + dx, y + dy
                        # Проверяем, что не выходим за границы
                        if 0 <= nx < width and 0 <= ny < height:
                            # Превращаем стену в проход
                            wide_maze[ny][nx] = 2
    
    # Подсчитываем количество проходов до и после расширения
    passages_before = sum(row.count(2) for row in maze)
    passages_after = sum(row.count(2) for row in wide_maze)
    print(f"Проходов до расширения: {passages_before}, после: {passages_after}")
    
    return wide_maze

def _add_rooms_and_widen_corridors(maze, width, height):
    """
    Добавляет комнаты и расширяет коридоры в лабиринте
    :param maze: Исходный лабиринт
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :return: Модифицированный лабиринт
    """
    print("Добавление комнат и дополнительное расширение коридоров")
    
    # Создаем копию лабиринта
    modified_maze = [row[:] for row in maze]
    
    # Добавляем комнаты
    num_rooms = random.randint(2, 4)  # Меньше комнат для более компактного лабиринта
    print(f"Добавляем {num_rooms} комнат")
    
    for i in range(num_rooms):
        # Случайный размер комнаты
        room_width = random.randint(3, 5)  # Уменьшаем размеры комнат
        room_height = random.randint(3, 5)
        
        # Случайная позиция комнаты (не слишком близко к краям)
        room_x = random.randint(2, width - room_width - 2)
        room_y = random.randint(2, height - room_height - 2)
        
        print(f"Комната {i+1}: позиция ({room_x}, {room_y}), размер {room_width}x{room_height}")
        
        # Создаем комнату
        for y in range(room_y, room_y + room_height):
            for x in range(room_x, room_x + room_width):
                if 0 <= x < width and 0 <= y < height:
                    modified_maze[y][x] = 2  # Проход
    
    # Соединяем комнаты с основным лабиринтом
    # Для этого проходим по всем стенам и с некоторой вероятностью превращаем их в проходы,
    # если рядом есть как минимум два прохода
    connections_made = 0
    for y in range(1, height-1):
        for x in range(1, width-1):
            # Если текущая клетка - стена
            if modified_maze[y][x] == 1:
                # Проверяем соседние клетки
                neighbors = [
                    modified_maze[y-1][x], modified_maze[y+1][x],  # Верх, низ
                    modified_maze[y][x-1], modified_maze[y][x+1]   # Лево, право
                ]
                
                # Если рядом как минимум два прохода, с некоторой вероятностью превращаем стену в проход
                if neighbors.count(2) >= 2 and random.random() < 0.3:
                    modified_maze[y][x] = 2
                    connections_made += 1
    
    print(f"Сделано {connections_made} дополнительных соединений")
    
    # Подсчитываем количество проходов до и после модификации
    passages_before = sum(row.count(2) for row in maze)
    passages_after = sum(row.count(2) for row in modified_maze)
    print(f"Проходов до модификации: {passages_before}, после: {passages_after}")
    
    return modified_maze

def _generate_maze(width, height):
    """
    Генерирует лабиринт с использованием алгоритма Recursive Backtracking (устаревший метод)
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :return: Двумерный массив с типами тайлов
    """
    # Убедимся, что размеры нечетные для правильной генерации лабиринта
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1
    
    # Создаем карту, заполненную стенами
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    # Функция для проверки, находится ли клетка в пределах лабиринта
    def is_in_bounds(x, y):
        return 0 <= x < width and 0 <= y < height
    
    # Функция для получения соседей клетки с шагом 2
    def get_neighbors(x, y):
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Верх, право, низ, лево
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_in_bounds(nx, ny) and maze[ny][nx] == 1:  # Если сосед - стена
                neighbors.append((nx, ny, x + dx//2, y + dy//2))  # (nx, ny, wx, wy) - координаты соседа и стены между ними
        
        return neighbors
    
    # Функция для рекурсивного прохода по лабиринту
    def carve_passages_from(cx, cy):
        maze[cy][cx] = 2  # Помечаем текущую клетку как проход
        
        neighbors = get_neighbors(cx, cy)
        for nx, ny, wx, wy in neighbors:
            if maze[ny][nx] == 1:  # Если сосед еще не посещен
                maze[wy][wx] = 2  # Убираем стену между текущей клеткой и соседом
                carve_passages_from(nx, ny)
    
    # Начинаем с случайной точки (с нечетными координатами)
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    
    # Генерируем лабиринт
    carve_passages_from(start_x, start_y)
    
    # Создаем вход и выход в лабиринте
    # Ищем проходы по периметру для размещения входа и выхода
    perimeter_passages = []
    
    # Верхняя и нижняя стороны
    for x in range(1, width-1):
        if maze[1][x] == 2:
            perimeter_passages.append((x, 0))
        if maze[height-2][x] == 2:
            perimeter_passages.append((x, height-1))
    
    # Левая и правая стороны
    for y in range(1, height-1):
        if maze[y][1] == 2:
            perimeter_passages.append((0, y))
        if maze[y][width-2] == 2:
            perimeter_passages.append((width-1, y))
    
    # Если не нашли проходы по периметру, создаем их
    if not perimeter_passages:
        # Создаем вход сверху
        x = random.randrange(1, width-1, 2)
        maze[0][x] = 2
        maze[1][x] = 2
        perimeter_passages.append((x, 0))
        
        # Создаем выход снизу
        x = random.randrange(1, width-1, 2)
        maze[height-1][x] = 2
        maze[height-2][x] = 2
        perimeter_passages.append((x, height-1))
    
    # Выбираем случайные точки для входа и выхода
    random.shuffle(perimeter_passages)
    entrance = perimeter_passages[0]
    exit = perimeter_passages[-1]
    
    # Отмечаем вход и выход
    maze[entrance[1]][entrance[0]] = 3  # Вход
    maze[exit[1]][exit[0]] = 4  # Выход
    
    # Расширяем проходы (делаем лабиринт шире)
    wide_maze = _widen_maze(maze, width, height)
    
    # Добавляем декоративные элементы
    decorated_maze = _decorate_maze(wide_maze, width, height)
    
    return decorated_maze

def _widen_maze(maze, width, height):
    """
    Расширяет проходы в лабиринте, делая их шире
    :param maze: Исходный лабиринт
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :return: Лабиринт с расширенными проходами
    """
    # Создаем копию лабиринта
    wide_maze = [row[:] for row in maze]
    
    # Проходим по всем клеткам лабиринта
    for y in range(1, height-1):
        for x in range(1, width-1):
            # Если текущая клетка - проход
            if maze[y][x] == 2:
                # Расширяем проход в случайных направлениях
                directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Верх, право, низ, лево
                random.shuffle(directions)
                
                # Выбираем случайное количество направлений для расширения (1 или 2)
                num_directions = random.randint(1, 2)
                
                for i in range(min(num_directions, len(directions))):
                    dx, dy = directions[i]
                    nx, ny = x + dx, y + dy
                    
                    # Проверяем, что не выходим за границы и не затрагиваем вход/выход
                    if (0 < nx < width-1 and 0 < ny < height-1 and
                        maze[ny][nx] == 1 and  # Это стена
                        not any(maze[ny+dy][nx+dx] in [3, 4] for dx, dy in directions)):  # Не затрагиваем вход/выход
                        # Превращаем стену в проход
                        wide_maze[ny][nx] = 2
    
    return wide_maze

def _decorate_maze(maze, width, height):
    """
    Добавляет декоративные элементы в лабиринт
    :param maze: Исходный лабиринт
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :return: Украшенный лабиринт
    """
    # Создаем копию лабиринта
    decorated_maze = [row[:] for row in maze]
    
    # Сглаживаем углы стен для более естественного вида
    for y in range(1, height-1):
        for x in range(1, width-1):
            # Если текущая клетка - стена
            if maze[y][x] == 1:
                # Проверяем соседние клетки
                neighbors = [
                    maze[y-1][x], maze[y+1][x],  # Верх, низ
                    maze[y][x-1], maze[y][x+1],  # Лево, право
                    maze[y-1][x-1], maze[y-1][x+1],  # Верхний левый, верхний правый
                    maze[y+1][x-1], maze[y+1][x+1]   # Нижний левый, нижний правый
                ]
                
                # Если вокруг много проходов, с небольшой вероятностью превращаем стену в проход
                if neighbors.count(2) >= 5 and random.random() < 0.3:
                    decorated_maze[y][x] = 2
    
    return decorated_maze

def _generate_level_map(width, height):
    """
    Генерирует карту уровня (устаревший метод)
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