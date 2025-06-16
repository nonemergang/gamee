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
    
    # Расширяем проходы для создания более широких коридоров
    if corridor_width > 1:
        maze = widen_corridors(maze, width, height, corridor_width)
    
    # Создаем вход и выход в лабиринте
    maze = add_entrance_exit(maze, width, height)
    
    print("Лабиринт успешно сгенерирован")
    return maze

def widen_corridors(maze, width, height, corridor_width):
    """
    Расширяет коридоры в лабиринте до указанной ширины, но сохраняет некоторые стены
    """
    print(f"Расширение коридоров до ширины {corridor_width}")
    
    # Создаем копию лабиринта
    wide_maze = [row[:] for row in maze]
    
    # Ограничиваем ширину коридора, чтобы сохранить стены
    corridor_width = min(corridor_width, 2)
    
    # Сначала отмечаем все проходы
    passages = []
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 2:
                passages.append((x, y))
    
    # Теперь расширяем только отмеченные проходы
    for x, y in passages:
        # Расширяем проход в обе стороны, но только на 1 клетку
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = x + dx, y + dy
                # Проверяем, что не выходим за границы
                if 0 <= nx < width and 0 <= ny < height:
                    # Не расширяем по диагонали (сохраняем больше стен)
                    if dx == 0 or dy == 0:
                        wide_maze[ny][nx] = 2
    
    # Подсчитываем количество проходов до и после расширения
    passages_before = sum(row.count(2) for row in maze)
    passages_after = sum(row.count(2) for row in wide_maze)
    walls_after = sum(row.count(1) for row in wide_maze)
    print(f"Проходов до расширения: {passages_before}, после: {passages_after}")
    print(f"Стен после расширения: {walls_after}")
    
    return wide_maze

def add_entrance_exit(maze, width, height):
    """
    Добавляет вход и выход в лабиринт
    """
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
    
    return maze 