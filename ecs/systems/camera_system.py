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
    
    def follow(self, entity_id):
        """
        Устанавливает цель для следования камеры
        :param entity_id: ID сущности для следования
        """
        self.target_id = entity_id
    
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
        
        if self.target_id is not None and self.world.has_component(self.target_id, Position):
            position = self.world.get_component(self.target_id, Position)
            
            # Вычисляем целевое положение камеры (центрирование на игроке)
            target_offset_x = position.x - self.screen_width / 2
            target_offset_y = position.y - self.screen_height / 2
            
            # Плавно перемещаем камеру к целевому положению
            self.offset_x += (target_offset_x - self.offset_x) * self.smoothness
            self.offset_y += (target_offset_y - self.offset_y) * self.smoothness
    
    def get_camera_offset(self):
        """
        Возвращает текущее смещение камеры
        :return: Кортеж (offset_x, offset_y)
        """
        return (self.offset_x, self.offset_y)
    
    def world_to_screen(self, x, y):
        """
        Преобразует мировые координаты в экранные
        :param x: Мировая координата X
        :param y: Мировая координата Y
        :return: Кортеж экранных координат (screen_x, screen_y)
        """
        screen_x = x - self.offset_x
        screen_y = y - self.offset_y
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """
        Преобразует экранные координаты в мировые
        :param screen_x: Экранная координата X
        :param screen_y: Экранная координата Y
        :return: Кортеж мировых координат (world_x, world_y)
        """
        world_x = screen_x + self.offset_x
        world_y = screen_y + self.offset_y
        return (world_x, world_y) 