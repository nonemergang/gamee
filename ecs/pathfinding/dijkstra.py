import heapq

class DijkstraPathfinder:
    """
    Реализация алгоритма Дейкстры для поиска кратчайшего пути
    """
    
    def __init__(self, level_map, width, height):
        """
        Инициализирует поиск пути
        :param level_map: Карта уровня (двумерный массив)
        :param width: Ширина карты
        :param height: Высота карты
        """
        self.level_map = level_map
        self.width = width
        self.height = height
        
    def find_path(self, start_x, start_y, target_x, target_y, max_distance=100):
        """
        Находит кратчайший путь от начальной точки до целевой
        :param start_x: Начальная позиция X
        :param start_y: Начальная позиция Y
        :param target_x: Целевая позиция X
        :param target_y: Целевая позиция Y
        :param max_distance: Максимальное расстояние поиска
        :return: Список точек пути [(x1, y1), (x2, y2), ...] или пустой список, если путь не найден
        """
        # Проверяем, что начальная и целевая точки находятся в пределах карты
        if not self._is_valid_position(start_x, start_y) or not self._is_valid_position(target_x, target_y):
            return []
        
        # Проверяем, что начальная и целевая точки проходимы
        if not self._is_walkable(start_x, start_y) or not self._is_walkable(target_x, target_y):
            return []
        
        # Округляем координаты до целых чисел (для работы с тайлами)
        start_x, start_y = int(start_x // 32), int(start_y // 32)
        target_x, target_y = int(target_x // 32), int(target_y // 32)
        
        # Словарь для хранения расстояний от начальной точки до всех остальных
        distances = {}
        
        # Словарь для хранения предыдущих точек для восстановления пути
        previous = {}
        
        # Приоритетная очередь для обхода точек
        # (расстояние, (x, y))
        queue = [(0, (start_x, start_y))]
        
        # Инициализируем расстояния
        for x in range(self.width):
            for y in range(self.height):
                distances[(x, y)] = float('inf')
        
        # Расстояние до начальной точки равно 0
        distances[(start_x, start_y)] = 0
        
        # Пока очередь не пуста
        while queue:
            # Извлекаем точку с наименьшим расстоянием
            current_distance, current_pos = heapq.heappop(queue)
            
            # Если достигли целевой точки или превысили максимальное расстояние
            if current_pos == (target_x, target_y) or current_distance > max_distance:
                break
            
            # Если уже нашли более короткий путь к этой точке
            if current_distance > distances[current_pos]:
                continue
            
            # Получаем соседние точки
            neighbors = self._get_neighbors(current_pos[0], current_pos[1])
            
            # Обрабатываем каждого соседа
            for neighbor in neighbors:
                # Вычисляем новое расстояние
                distance = current_distance + 1  # Вес каждого шага равен 1
                
                # Если нашли более короткий путь
                if distance < distances[neighbor]:
                    # Обновляем расстояние
                    distances[neighbor] = distance
                    # Запоминаем предыдущую точку
                    previous[neighbor] = current_pos
                    # Добавляем в очередь
                    heapq.heappush(queue, (distance, neighbor))
        
        # Восстанавливаем путь
        path = []
        current = (target_x, target_y)
        
        # Если путь не найден
        if current not in previous and current != (start_x, start_y):
            return []
        
        # Восстанавливаем путь в обратном порядке
        while current != (start_x, start_y):
            # Преобразуем координаты тайлов обратно в мировые координаты (центр тайла)
            world_x = current[0] * 32 + 16
            world_y = current[1] * 32 + 16
            path.append((world_x, world_y))
            current = previous.get(current)
            if current is None:  # Если путь прервался
                break
        
        # Возвращаем путь в правильном порядке (от начала к концу)
        path.reverse()
        return path
    
    def _is_valid_position(self, x, y):
        """
        Проверяет, находится ли позиция в пределах карты
        :param x: Позиция X
        :param y: Позиция Y
        :return: True, если позиция в пределах карты, иначе False
        """
        tile_x, tile_y = int(x // 32), int(y // 32)
        return 0 <= tile_x < self.width and 0 <= tile_y < self.height
    
    def _is_walkable(self, x, y):
        """
        Проверяет, является ли позиция проходимой
        :param x: Позиция X
        :param y: Позиция Y
        :return: True, если позиция проходима, иначе False
        """
        tile_x, tile_y = int(x // 32), int(y // 32)
        # Проверяем, что тайл существует и является проходимым (код 2, 3 или 4)
        return self.level_map[tile_y][tile_x] in [2, 3, 4]
    
    def _get_neighbors(self, x, y):
        """
        Получает список соседних проходимых точек
        :param x: Позиция X
        :param y: Позиция Y
        :return: Список соседних точек [(x1, y1), (x2, y2), ...]
        """
        neighbors = []
        
        # Проверяем соседей по четырем направлениям (верх, право, низ, лево)
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            # Проверяем, что сосед находится в пределах карты
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Проверяем, что сосед проходим
                if self.level_map[ny][nx] in [2, 3, 4]:  # Проходимые тайлы
                    neighbors.append((nx, ny))
        
        return neighbors 