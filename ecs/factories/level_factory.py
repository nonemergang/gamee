import random
import pygame
from ecs.components.components import Position, Sprite, Collider, Tile

# Загружаем текстуры или создаем их
def get_textures():
    textures = {}
    
    # Создаем текстуры программно, если нет готовых изображений
    # Стена
    wall_texture = pygame.Surface((32, 32))
    wall_texture.fill((60, 60, 70))
    # Добавляем эффект кирпичей
    for i in range(0, 32, 8):
        for j in range(0, 32, 4):
            offset = 4 if i % 16 == 0 else 0
            pygame.draw.rect(wall_texture, (80, 80, 90), (offset + j, i, 3, 3))
    # Добавляем тени
    pygame.draw.line(wall_texture, (40, 40, 50), (0, 0), (0, 31), 2)
    pygame.draw.line(wall_texture, (40, 40, 50), (0, 0), (31, 0), 2)
    pygame.draw.line(wall_texture, (90, 90, 100), (31, 0), (31, 31), 2)
    pygame.draw.line(wall_texture, (90, 90, 100), (0, 31), (31, 31), 2)
    textures["wall"] = wall_texture
    
    # Пол
    floor_texture = pygame.Surface((32, 32))
    floor_texture.fill((180, 180, 190))
    # Добавляем эффект плитки
    for i in range(0, 32, 8):
        for j in range(0, 32, 8):
            pygame.draw.rect(floor_texture, (170, 170, 180), (j, i, 7, 7))
    textures["floor"] = floor_texture
    
    # Вход
    entrance_texture = pygame.Surface((32, 32))
    entrance_texture.fill((100, 200, 100))
    # Добавляем узор
    pygame.draw.circle(entrance_texture, (50, 150, 50), (16, 16), 10)
    pygame.draw.circle(entrance_texture, (150, 250, 150), (16, 16), 5)
    textures["entrance"] = entrance_texture
    
    # Выход
    exit_texture = pygame.Surface((32, 32))
    exit_texture.fill((200, 100, 100))
    # Добавляем узор
    pygame.draw.circle(exit_texture, (150, 50, 50), (16, 16), 10)
    pygame.draw.circle(exit_texture, (250, 150, 150), (16, 16), 5)
    textures["exit"] = exit_texture
    
    # Декоративные элементы
    # Трещина на полу
    crack_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.line(crack_texture, (100, 100, 110), (10, 10), (22, 22), 2)
    pygame.draw.line(crack_texture, (100, 100, 110), (22, 22), (28, 18), 2)
    textures["crack"] = crack_texture
    
    # Мох на стене
    moss_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
    for i in range(10):
        x = random.randint(0, 31)
        y = random.randint(0, 31)
        size = random.randint(2, 5)
        pygame.draw.circle(moss_texture, (0, 150, 0, 100), (x, y), size)
    textures["moss"] = moss_texture
    
    return textures

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
    
    # Загружаем текстуры
    textures = get_textures()
    
    # Генерируем карту лабиринта
    level_map = _generate_perfect_maze(width, height)
    
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
                texture = textures["wall"]
                # Добавляем мох к некоторым стенам для разнообразия
                if random.random() < 0.1:
                    texture = texture.copy()
                    texture.blit(textures["moss"], (0, 0))
                walkable = False
                layer = 1
                tile_name = "wall"
            elif tile_type == 2:  # Пол
                texture = textures["floor"]
                # Добавляем трещины к некоторым плиткам пола для разнообразия
                if random.random() < 0.05:
                    texture = texture.copy()
                    texture.blit(textures["crack"], (0, 0))
                walkable = True
                layer = 0
                tile_name = "floor"
            elif tile_type == 3:  # Вход в лабиринт
                texture = textures["entrance"]
                walkable = True
                layer = 0
                tile_name = "entrance"
            elif tile_type == 4:  # Выход из лабиринта
                texture = textures["exit"]
                walkable = True
                layer = 0
                tile_name = "exit"
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
    
    return level_entities

def _generate_perfect_maze(width, height):
    """
    Генерирует идеальный лабиринт с использованием алгоритма Recursive Backtracking
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
    
    # Добавляем комнаты и расширяем некоторые коридоры
    maze = _add_rooms_and_widen_corridors(maze, width, height)
    
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
    
    # Если какой-то из списков пуст, используем общий список
    if not entrance_candidates:
        entrance_candidates = perimeter_passages
    if not exit_candidates:
        exit_candidates = perimeter_passages
    
    # Выбираем случайные точки
    entrance = random.choice(entrance_candidates)
    exit_pos = random.choice(exit_candidates)
    
    # Отмечаем вход и выход
    maze[entrance[1]][entrance[0]] = 3  # Вход
    maze[exit_pos[1]][exit_pos[0]] = 4  # Выход
    
    return maze

def _add_rooms_and_widen_corridors(maze, width, height):
    """
    Добавляет комнаты и расширяет коридоры в лабиринте
    :param maze: Исходный лабиринт
    :param width: Ширина лабиринта
    :param height: Высота лабиринта
    :return: Модифицированный лабиринт
    """
    # Создаем копию лабиринта
    modified_maze = [row[:] for row in maze]
    
    # Добавляем комнаты
    num_rooms = random.randint(3, 6)  # Случайное количество комнат
    for _ in range(num_rooms):
        # Случайный размер комнаты
        room_width = random.randint(3, 7)
        room_height = random.randint(3, 7)
        
        # Случайная позиция комнаты (не слишком близко к краям)
        room_x = random.randint(2, width - room_width - 2)
        room_y = random.randint(2, height - room_height - 2)
        
        # Создаем комнату
        for y in range(room_y, room_y + room_height):
            for x in range(room_x, room_x + room_width):
                if 0 <= x < width and 0 <= y < height:
                    modified_maze[y][x] = 2  # Проход
    
    # Расширяем коридоры
    for y in range(1, height-1):
        for x in range(1, width-1):
            # Если текущая клетка - проход
            if maze[y][x] == 2:
                # Расширяем коридор в случайных направлениях
                directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Верх, право, низ, лево
                
                # С некоторой вероятностью расширяем коридор
                if random.random() < 0.3:
                    # Выбираем случайное направление
                    dx, dy = random.choice(directions)
                    nx, ny = x + dx, y + dy
                    
                    # Проверяем, что не выходим за границы
                    if 0 < nx < width-1 and 0 < ny < height-1:
                        # Превращаем стену в проход
                        modified_maze[ny][nx] = 2
    
    # Соединяем комнаты с основным лабиринтом
    # Для этого проходим по всем стенам и с некоторой вероятностью превращаем их в проходы,
    # если рядом есть как минимум два прохода
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