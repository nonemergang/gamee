import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Player, Velocity, Tile

class LightingSystem(System):
    """Система для создания эффекта освещения с использованием упрощенного Raycasting"""
    
    def __init__(self, world, screen, camera_system=None):
        """
        Инициализирует систему освещения на основе упрощенного Raycasting
        :param world: Мир ECS
        :param screen: Поверхность Pygame для отрисовки
        :param camera_system: Система камеры для преобразования координат
        """
        super().__init__(world)
        self.screen = screen
        self.camera_system = camera_system
        
        # Параметры освещения (упрощенные)
        self.max_ray_length = 250      # Уменьшенная максимальная длина луча
        self.ray_count = 60            # Сильно уменьшено количество лучей для оптимизации
        self.fov = 120                 # Угол обзора в градусах
        self.darkness_alpha = 180      # Затемнение (0-255)
        
        # Параметры мерцания
        self.flicker_intensity = 0.05  # Уменьшена интенсивность мерцания
        self.flicker_speed = 2.0       # Уменьшена скорость мерцания
        self.flicker_timer = 0.0       # Таймер для мерцания
        self.current_flicker = 1.0     # Текущий множитель мерцания
        
        # Сохраняем последнюю позицию и направление игрока
        self.last_player_pos = (0, 0)
        self.last_player_direction = 0
        
        # Создаем поверхность для затемнения
        self.darkness_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        
        # Кэшируем стены для оптимизации
        self.wall_cache = []
        self.wall_cache_dirty = True
        
        # Предварительно вычисляем углы для лучей
        self.ray_angles = []
        self.update_ray_angles()
        
        # Параметры света вокруг игрока
        self.player_light_radius = 180  # Радиус света вокруг игрока
        self.use_only_player_light = True  # Флаг для использования только света вокруг игрока
        
        # Оптимизация: предварительно создаем маску свечения
        self.glow_surface = None
        self.create_glow_surface()
        
        # Оптимизация: ограничиваем частоту обновления
        self.update_interval = 0.05  # Обновление каждые 50 мс
        self.update_timer = 0.0
        
        # Оптимизация: кэшируем последний полигон света
        self.last_light_polygon = []
        self.last_player_screen_pos = (0, 0)
        
    def create_glow_surface(self):
        """Предварительно создает поверхность свечения для оптимизации"""
        glow_radius = self.player_light_radius
        self.glow_surface = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
        
        # Создаем градиентное свечение с высокой интенсивностью
        for r in range(int(glow_radius), 0, -4):  # Шаг -4 для оптимизации
            # Вычисляем прозрачность в зависимости от радиуса (чем дальше, тем прозрачнее)
            alpha = int(240 * (1 - r / glow_radius))
            pygame.draw.circle(self.glow_surface, (0, 0, 0, alpha), (int(glow_radius), int(glow_radius)), r, 1)
    
    def update_ray_angles(self):
        """Обновляет углы для лучей на основе угла обзора"""
        self.ray_angles = []
        half_fov = self.fov / 2
        angle_step = self.fov / (self.ray_count - 1) if self.ray_count > 1 else 0
        
        for i in range(self.ray_count):
            angle = -half_fov + (i * angle_step)
            self.ray_angles.append(math.radians(angle))
    
    def update(self, dt):
        """
        Обновляет эффект освещения
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Если нет camera_system, пропускаем обновление
        if not self.camera_system:
            return
        
        # Обновляем таймер
        self.update_timer += dt
        if self.update_timer < self.update_interval:
            return  # Пропускаем обновление, если не прошло достаточно времени
        
        self.update_timer = 0.0  # Сбрасываем таймер
            
        # Находим игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if not player_entities:
            return
        
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Определяем направление игрока
        player_direction = self.last_player_direction  # По умолчанию используем последнее известное направление
        if self.world.has_component(player_id, Velocity):
            velocity = self.world.get_component(player_id, Velocity)
            if velocity.x != 0 or velocity.y != 0:
                # Вычисляем угол на основе вектора скорости
                player_direction = math.atan2(-velocity.y, velocity.x)  # Отрицательный Y для соответствия координатам экрана
        
        # Обновляем эффект мерцания
        self._update_flicker(dt)
        
        # Сохраняем позицию и направление игрока
        self.last_player_pos = (player_pos.x, player_pos.y)
        self.last_player_direction = player_direction
        
        # Обновляем кэш стен если необходимо
        if self.wall_cache_dirty:
            self.update_wall_cache()
            self.wall_cache_dirty = False
    
    def update_wall_cache(self):
        """Обновляет кэш стен для оптимизации расчетов"""
        self.wall_cache = []
        
        # Получаем все тайлы-стены
        tile_entities = self.world.get_entities_with_components(Tile, Position)
        
        # Оптимизация: ограничиваем количество стен для проверки
        max_walls = 200  # Максимальное количество стен для проверки
        wall_count = 0
        
        for entity_id in tile_entities:
            tile = self.world.get_component(entity_id, Tile)
            if not tile.walkable:  # Стена
                pos = self.world.get_component(entity_id, Position)
                
                # Оптимизация: проверяем только стены в радиусе видимости
                player_x, player_y = self.last_player_pos
                dx = pos.x - player_x
                dy = pos.y - player_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Если стена слишком далеко, пропускаем ее
                if distance > self.max_ray_length * 1.5:
                    continue
                
                # Сохраняем координаты углов тайла (для проверки пересечений)
                tile_size = 32  # Размер тайла
                half_size = tile_size / 2
                
                # Координаты углов тайла
                x1, y1 = pos.x - half_size, pos.y - half_size  # Верхний левый
                x2, y2 = pos.x + half_size, pos.y - half_size  # Верхний правый
                x3, y3 = pos.x + half_size, pos.y + half_size  # Нижний правый
                x4, y4 = pos.x - half_size, pos.y + half_size  # Нижний левый
                
                # Добавляем стороны тайла (для проверки пересечений)
                self.wall_cache.append(((x1, y1), (x2, y2)))  # Верхняя сторона
                self.wall_cache.append(((x2, y2), (x3, y3)))  # Правая сторона
                self.wall_cache.append(((x3, y3), (x4, y4)))  # Нижняя сторона
                self.wall_cache.append(((x4, y4), (x1, y1)))  # Левая сторона
                
                wall_count += 4
                if wall_count >= max_walls:
                    break
    
    def render(self, camera=None):
        """
        Отрисовывает эффект освещения
        :param camera: Камера для преобразования координат
        """
        # Применяем эффект Raycasting
        self._apply_raycasting()
    
    def _update_flicker(self, dt):
        """
        Обновляет эффект мерцания фонарика
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        self.flicker_timer += dt * self.flicker_speed
        # Используем синус для плавного мерцания
        flicker_offset = math.sin(self.flicker_timer) * self.flicker_intensity
        self.current_flicker = 1.0 + flicker_offset
    
    def _ray_cast(self, start_x, start_y, angle, max_distance):
        """
        Выполняет упрощенный Raycasting из заданной точки в заданном направлении
        :param start_x: Начальная X координата
        :param start_y: Начальная Y координата
        :param angle: Угол луча в радианах
        :param max_distance: Максимальная длина луча
        :return: Точка пересечения с ближайшей стеной или конечная точка луча
        """
        # Вычисляем конечную точку луча
        end_x = start_x + math.cos(angle) * max_distance
        end_y = start_y - math.sin(angle) * max_distance  # Отрицательный Y для соответствия координатам экрана
        
        closest_intersection = None
        closest_distance = float('inf')
        
        # Проверяем пересечения со всеми стенами
        for wall in self.wall_cache:
            # Проверяем пересечение луча со стеной
            intersection = self._line_intersection(
                start_x, start_y, end_x, end_y,
                wall[0][0], wall[0][1], wall[1][0], wall[1][1]
            )
            
            if intersection:
                # Вычисляем расстояние до пересечения
                dx = intersection[0] - start_x
                dy = intersection[1] - start_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Если это ближайшее пересечение, сохраняем его
                if distance < closest_distance:
                    closest_distance = distance
                    closest_intersection = intersection
        
        # Если нет пересечений, возвращаем конечную точку луча
        return closest_intersection if closest_intersection else (end_x, end_y)
    
    def _line_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """
        Проверяет пересечение двух отрезков (оптимизированная версия)
        :return: Координаты точки пересечения или None, если пересечения нет
        """
        # Вычисляем определитель
        den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        
        # Если определитель равен 0, линии параллельны
        if abs(den) < 0.0001:  # Небольшой порог для численной стабильности
            return None
            
        # Вычисляем параметры t и u
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        
        # Если параметры в диапазоне [0, 1], есть пересечение
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            # Вычисляем координаты точки пересечения
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return x, y
            
        return None
    
    def _apply_raycasting(self):
        """
        Применяет эффект освещения с использованием упрощенного Raycasting
        """
        # Получаем позицию игрока
        player_x, player_y = self.last_player_pos
        
        # Преобразуем позицию игрока в экранные координаты
        player_screen_x, player_screen_y = self.camera_system.world_to_screen(player_x, player_y)
        
        # Создаем новую поверхность для затемнения
        self.darkness_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        self.darkness_surface.fill((0, 0, 0, self.darkness_alpha))
        
        # Создаем поверхность для света (полностью прозрачная)
        light_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        
        # Если включен режим "только свет вокруг игрока", не рисуем конус света
        if not self.use_only_player_light:
            # Оптимизация: если игрок не двигался, используем кэшированный полигон
            if (abs(player_screen_x - self.last_player_screen_pos[0]) < 1 and 
                abs(player_screen_y - self.last_player_screen_pos[1]) < 1 and 
                len(self.last_light_polygon) > 0):
                # Используем кэшированный полигон
                light_polygon = self.last_light_polygon
            else:
                # Учитываем мерцание в длине лучей
                max_ray_length = self.max_ray_length * self.current_flicker
                
                # Получаем точки для полигона света
                light_polygon = []
                
                # Направление взгляда игрока
                direction = self.last_player_direction
                
                # Выполняем Raycasting для каждого угла в поле зрения
                for ray_angle in self.ray_angles:
                    # Вычисляем абсолютный угол луча
                    absolute_angle = direction + ray_angle
                    
                    # Выполняем Raycasting
                    end_x, end_y = self._ray_cast(player_x, player_y, absolute_angle, max_ray_length)
                    
                    # Преобразуем мировые координаты в экранные
                    screen_x, screen_y = self.camera_system.world_to_screen(end_x, end_y)
                    
                    # Добавляем точку в полигон
                    light_polygon.append((screen_x, screen_y))
                
                # Кэшируем полигон и позицию игрока
                self.last_light_polygon = light_polygon
                self.last_player_screen_pos = (player_screen_x, player_screen_y)
            
            # Создаем градиентное освещение с затуханием по краям
            if len(light_polygon) > 2:
                # Формируем полный список точек полигона
                complete_polygon = [(player_screen_x, player_screen_y)] + light_polygon
                
                # Рисуем основной полигон света
                pygame.draw.polygon(light_surface, (0, 0, 0, 0), complete_polygon)
        
        # Накладываем свет на затемнение с использованием вычитания альфа-канала
        self.darkness_surface.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
        # Используем предварительно созданную поверхность свечения
        if self.glow_surface:
            # Накладываем свечение на затемнение
            glow_radius = self.player_light_radius
            self.darkness_surface.blit(self.glow_surface, 
                                    (int(player_screen_x - glow_radius), int(player_screen_y - glow_radius)), 
                                    special_flags=pygame.BLEND_RGBA_SUB)
        
        # Накладываем затемнение на экран
        self.screen.blit(self.darkness_surface, (0, 0))
    
    def set_player_light_only(self, value):
        """
        Устанавливает режим освещения только вокруг игрока
        :param value: True - только свет вокруг игрока, False - обычный режим с конусом света
        """
        self.use_only_player_light = value
    
    def increase_player_light_radius(self, amount=10):
        """
        Увеличивает радиус света вокруг игрока
        :param amount: Величина увеличения
        """
        self.player_light_radius += amount
        self.create_glow_surface()  # Пересоздаем поверхность свечения
        
    def decrease_player_light_radius(self, amount=10):
        """
        Уменьшает радиус света вокруг игрока
        :param amount: Величина уменьшения
        """
        self.player_light_radius = max(50, self.player_light_radius - amount)
        self.create_glow_surface()  # Пересоздаем поверхность свечения 