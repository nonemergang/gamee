import pygame
from ecs.systems.system import System
from ecs.components.components import Position, Player

class CameraSystem(System):
    """Система для управления камерой в игре"""
    
    def __init__(self, world, screen_width, screen_height):
        """
        Инициализирует систему камеры
        :param world: Мир ECS
        :param screen_width: Ширина экрана
        :param screen_height: Высота экрана
        """
        super().__init__(world)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target_id = None
        self.offset_x = 0
        self.offset_y = 0
        self.smoothness = 0.1  # Параметр сглаживания движения камеры (0-1)
        self.zoom = 4.0  # Масштаб камеры (1.0 = без масштабирования, > 1.0 = приближение)
        self.target_zoom = 4.0  # Целевой масштаб для плавного изменения
        self.zoom_smoothness = 0.05  # Параметр сглаживания изменения масштаба
    
    def follow(self, entity_id):
        """
        Устанавливает цель для следования камеры
        :param entity_id: ID сущности для следования
        """
        self.target_id = entity_id
    
    def set_zoom(self, zoom):
        """
        Устанавливает масштаб камеры
        :param zoom: Новый масштаб (1.0 = без масштабирования, > 1.0 = приближение)
        """
        if zoom < 0.5:
            zoom = 0.5  # Минимальный масштаб
        elif zoom > 8.0:
            zoom = 8.0  # Максимальный масштаб
        self.target_zoom = zoom
    
    def update(self, dt):
        """
        Обновляет положение камеры
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        if self.target_id is None:
            # Если нет цели, ищем игрока
            player_entities = self.world.get_entities_with_components(Player, Position)
            if player_entities:
                self.target_id = player_entities[0]
        
        # Плавно изменяем масштаб
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_smoothness
        
        if self.target_id is not None and self.world.has_component(self.target_id, Position):
            position = self.world.get_component(self.target_id, Position)
            
            # Вычисляем целевое положение камеры (центрирование на игроке)
            # Учитываем масштаб: при увеличении масштаба видимая область уменьшается
            target_offset_x = position.x - self.screen_width / (2 * self.zoom)
            target_offset_y = position.y - self.screen_height / (2 * self.zoom)
            
            # Плавно перемещаем камеру к целевому положению
            self.offset_x += (target_offset_x - self.offset_x) * self.smoothness
            self.offset_y += (target_offset_y - self.offset_y) * self.smoothness
    
    def get_camera_offset(self):
        """
        Возвращает текущее смещение камеры
        :return: Кортеж (offset_x, offset_y)
        """
        return (self.offset_x, self.offset_y)
    
    def get_zoom(self):
        """
        Возвращает текущий масштаб камеры
        :return: Масштаб камеры
        """
        return self.zoom
    
    def world_to_screen(self, x, y):
        """
        Преобразует мировые координаты в экранные с учетом масштаба
        :param x: Мировая координата X
        :param y: Мировая координата Y
        :return: Кортеж экранных координат (screen_x, screen_y)
        """
        # Быстрая проверка, находится ли объект в видимой области
        # Добавляем запас в 100 пикселей с каждой стороны
        margin = 100
        visible_left = self.offset_x - margin
        visible_right = self.offset_x + self.screen_width / self.zoom + margin
        visible_top = self.offset_y - margin
        visible_bottom = self.offset_y + self.screen_height / self.zoom + margin
        
        # Если объект находится далеко за пределами экрана, возвращаем координаты за пределами экрана
        if x < visible_left or x > visible_right or y < visible_top or y > visible_bottom:
            return (-1000, -1000)  # Координаты за пределами экрана
        
        screen_x = (x - self.offset_x) * self.zoom
        screen_y = (y - self.offset_y) * self.zoom
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """
        Преобразует экранные координаты в мировые с учетом масштаба
        :param screen_x: Экранная координата X
        :param screen_y: Экранная координата Y
        :return: Кортеж мировых координат (world_x, world_y)
        """
        world_x = screen_x / self.zoom + self.offset_x
        world_y = screen_y / self.zoom + self.offset_y
        return (world_x, world_y) 