import random

def generate_prim_maze(width, height, corridor_width=1):
    """
    Генерирует лабиринт с использованием алгоритма Прима
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :param corridor_width: Ширина коридоров (в тайлах)
    :return: Двумерный массив с типами тайлов
    """
    print(f"Генерация лабиринта по алгоритму Прима: {width}x{height}")
    
    # Убедимся, что размеры достаточно большие
    if width < 15:
        width = 15
    if height < 15:
        height = 15
    
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
    
    # Пропускаем расширение коридоров, оставляем базовый лабиринт
    # Добавляем комнаты в лабиринт
    maze = add_rooms(maze, width, height, num_rooms=3, min_size=3, max_size=5)
    
    # Создаем вход и выход в лабиринте
    maze = add_entrance_exit(maze, width, height)
    
    print("Лабиринт успешно сгенерирован")
    return maze

def widen_corridors(maze, width, height, corridor_width):
    """
    Расширяет коридоры в лабиринте до указанной ширины, но сохраняет больше стен
    """
    print(f"Расширение коридоров до ширины {corridor_width}")
    
    # Создаем копию лабиринта
    wide_maze = [row[:] for row in maze]
    
    # Ограничиваем ширину коридора
    corridor_width = min(corridor_width, 2)
    
    # Сначала отмечаем все проходы
    passages = []
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 2:
                passages.append((x, y))
    
    # Расширяем только по горизонтали и вертикали, не по диагонали
    # Это создаст более структурированный лабиринт
    for x, y in passages:
        # Расширяем проход только по основным направлениям
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            # Проверяем, что не выходим за границы
            if 0 <= nx < width and 0 <= ny < height:
                # Расширяем только если это стена (не затрагиваем существующие проходы)
                if maze[ny][nx] == 1:
                    # Расширяем с вероятностью 70%, чтобы сохранить некоторые стены
                    if random.random() < 0.7:
                        wide_maze[ny][nx] = 2
    
    # Убедимся, что внешние стены остаются стенами
    for x in range(width):
        wide_maze[0][x] = 1
        wide_maze[height-1][x] = 1
    for y in range(height):
        wide_maze[y][0] = 1
        wide_maze[y][width-1] = 1
    
    # Восстанавливаем вход и выход
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 3:  # Вход
                wide_maze[y][x] = 3
            elif maze[y][x] == 4:  # Выход
                wide_maze[y][x] = 4
    
    # Подсчитываем количество проходов до и после расширения
    passages_before = sum(row.count(2) for row in maze)
    passages_after = sum(row.count(2) for row in wide_maze)
    walls_after = sum(row.count(1) for row in wide_maze)
    print(f"Проходов до расширения: {passages_before}, после: {passages_after}")
    print(f"Стен после расширения: {walls_after}")
    
    return wide_maze

def add_rooms(maze, width, height, num_rooms=3, min_size=3, max_size=5):
    """
    Добавляет комнаты в лабиринт
    :param maze: Лабиринт
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :param num_rooms: Количество комнат
    :param min_size: Минимальный размер комнаты
    :param max_size: Максимальный размер комнаты
    :return: Лабиринт с комнатами
    """
    print(f"Добавление {num_rooms} комнат размером от {min_size}x{min_size} до {max_size}x{max_size}")
    
    # Создаем копию лабиринта
    modified_maze = [row[:] for row in maze]
    
    # Делим лабиринт на секторы для более равномерного распределения комнат
    sector_width = width // 3
    sector_height = height // 3
    
    rooms_added = 0
    attempts = 0
    max_attempts = 50  # Максимальное количество попыток добавить комнаты
    
    # Пытаемся добавить комнаты
    while rooms_added < num_rooms and attempts < max_attempts:
        attempts += 1
        
        # Выбираем случайный сектор
        sector_x = random.randint(0, 2)
        sector_y = random.randint(0, 2)
        
        # Определяем границы сектора с отступами от края
        start_x = sector_x * sector_width + 2
        start_y = sector_y * sector_height + 2
        end_x = min((sector_x + 1) * sector_width - 2, width - 2)
        end_y = min((sector_y + 1) * sector_height - 2, height - 2)
        
        # Если сектор слишком маленький, пропускаем его
        if end_x - start_x < min_size + 2 or end_y - start_y < min_size + 2:
            continue
        
        # Случайный размер комнаты
        room_width = min(random.randint(min_size, max_size), end_x - start_x)
        room_height = min(random.randint(min_size, max_size), end_y - start_y)
        
        # Случайная позиция комнаты в пределах сектора
        room_x = random.randint(start_x, end_x - room_width)
        room_y = random.randint(start_y, end_y - room_height)
        
        # Проверяем, что комната не пересекается с другими комнатами
        # Для простоты просто проверяем, что в этом месте есть хотя бы одна стена
        has_wall = False
        for y in range(room_y, room_y + room_height):
            for x in range(room_x, room_x + room_width):
                if modified_maze[y][x] == 1:  # Если есть стена
                    has_wall = True
                    break
            if has_wall:
                break
        
        if not has_wall:
            continue  # Если нет стен, значит комната уже есть или это проход
        
        # Создаем комнату
        for y in range(room_y, room_y + room_height):
            for x in range(room_x, room_x + room_width):
                if 0 <= y < height and 0 <= x < width:
                    modified_maze[y][x] = 2  # Проход
        
        # Соединяем комнату с основным лабиринтом
        # Выбираем случайную сторону комнаты
        side = random.randint(0, 3)  # 0 - верх, 1 - право, 2 - низ, 3 - лево
        
        # Создаем проход от комнаты к ближайшему коридору
        if side == 0:  # Верх
            x = random.randint(room_x, room_x + room_width - 1)
            for y in range(room_y - 1, 0, -1):
                modified_maze[y][x] = 2  # Проход
                if y > 0 and modified_maze[y-1][x] == 2:
                    break  # Нашли существующий проход
        elif side == 1:  # Право
            y = random.randint(room_y, room_y + room_height - 1)
            for x in range(room_x + room_width, width - 1):
                modified_maze[y][x] = 2  # Проход
                if x < width - 1 and modified_maze[y][x+1] == 2:
                    break  # Нашли существующий проход
        elif side == 2:  # Низ
            x = random.randint(room_x, room_x + room_width - 1)
            for y in range(room_y + room_height, height - 1):
                modified_maze[y][x] = 2  # Проход
                if y < height - 1 and modified_maze[y+1][x] == 2:
                    break  # Нашли существующий проход
        else:  # Лево
            y = random.randint(room_y, room_y + room_height - 1)
            for x in range(room_x - 1, 0, -1):
                modified_maze[y][x] = 2  # Проход
                if x > 0 and modified_maze[y][x-1] == 2:
                    break  # Нашли существующий проход
        
        rooms_added += 1
        print(f"Добавлена комната {rooms_added}: позиция ({room_x}, {room_y}), размер {room_width}x{room_height}")
    
    print(f"Добавлено всего {rooms_added} комнат")
    return modified_maze

def add_entrance_exit(maze, width, height):
    """
    Добавляет вход и выход в лабиринт
    """
    print("Создание входа и выхода из лабиринта")
    
    # Принудительно создаем вход и выход в противоположных сторонах лабиринта
    # Вход - всегда в верхней левой части
    entrance_x = random.randrange(1, width // 3)
    entrance_y = 0
    
    # Выход - всегда в нижней правой части
    exit_x = random.randrange(width * 2 // 3, width - 1)
    exit_y = height - 1
    
    # Устанавливаем вход и убираем стены для прохода
    maze[entrance_y][entrance_x] = 3  # Вход
    maze[entrance_y + 1][entrance_x] = 2  # Проход после входа
    
    # Устанавливаем выход и убираем стены для прохода
    maze[exit_y][exit_x] = 4  # Выход
    maze[exit_y - 1][exit_x] = 2  # Проход перед выходом
    
    # Создаем явный путь от входа к выходу, чтобы гарантировать проходимость
    # Сначала движемся вниз до середины
    current_x = entrance_x
    current_y = entrance_y + 1
    
    mid_y = height // 2
    while current_y < mid_y:
        maze[current_y][current_x] = 2  # Проход
        current_y += 1
    
    # Затем движемся вправо до позиции над выходом
    while current_x < exit_x:
        maze[current_y][current_x] = 2  # Проход
        current_x += 1
    
    # И наконец вниз до выхода
    while current_y < exit_y:
        maze[current_y][current_x] = 2  # Проход
        current_y += 1
    
    print(f"Вход создан: {entrance_x}, {entrance_y}")
    print(f"Выход создан: {exit_x}, {exit_y}")
    
    # Дополнительная проверка
    if maze[entrance_y][entrance_x] != 3 or maze[exit_y][exit_x] != 4:
        print("ОШИБКА: Не удалось создать вход или выход!")
    else:
        print("Вход и выход успешно созданы")
    
    return maze 