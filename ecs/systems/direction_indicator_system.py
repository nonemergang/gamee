import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Player, Tile, DirectionIndicator, Portal

class DirectionIndicatorSystem(System):
    """
    Система для отображения указателя направления к выходу (порталу)
    """
    
    def __init__(self, world, screen, camera_system):
        super().__init__(world)
        self.screen = screen
        self.camera_system = camera_system
        self.portal_positions = []  # Позиции всех порталов на уровне
        self.indicator_color = (255, 0, 255)  # Яркий розовый цвет для лучшей видимости
        self.font = pygame.font.SysFont(None, 24)  # Увеличенный шрифт для лучшей видимости
        self.pulse_timer = 0  # Таймер для пульсации
        self.debug = False  # Полностью отключаем отладочный вывод
        
    def update(self, dt):
        """
        Обновляет указатель направления
        :param dt: Время, прошедшее с последнего обновления
        """
        # Обновляем таймер пульсации
        self.pulse_timer += dt
        if self.pulse_timer > 1.0:
            self.pulse_timer = 0
            
        # Находим все порталы в мире
        portal_entities = self.world.get_entities_with_components(Portal, Position)
        
        # Обновляем позиции порталов
        self.portal_positions = []
        for portal_id in portal_entities:
            portal_pos = self.world.get_component(portal_id, Position)
            self.portal_positions.append((portal_pos.x, portal_pos.y))
        
    def render(self, camera=None):
        """
        Отрисовывает указатель направления к порталу
        :param camera: Камера для преобразования координат (не используется, так как у нас есть self.camera_system)
        """
        # Если нет порталов, нечего отображать
        if not self.portal_positions:
            return
            
        # Находим игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if not player_entities:
            return
            
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Для каждого портала рисуем указатель направления
        for portal_x, portal_y in self.portal_positions:
            # Вычисляем направление к порталу
            dx = portal_x - player_pos.x
            dy = portal_y - player_pos.y
            
            # Вычисляем расстояние до портала
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Вычисляем угол направления к порталу (нужен для рисования стрелки)
            angle = math.degrees(math.atan2(dy, dx))
            
            # Получаем экранные координаты игрока
            player_screen_x, player_screen_y = self.camera_system.world_to_screen(player_pos.x, player_pos.y)
            
            # Рисуем указатель (стрелку)
            indicator_radius = 40  # Радиус от игрока, на котором рисуется указатель
            
            # Пульсация для привлечения внимания
            pulse_factor = 1.0 + 0.2 * math.sin(self.pulse_timer * 10)
            indicator_radius *= pulse_factor
            
            # Координаты конца стрелки
            arrow_end_x = player_screen_x + indicator_radius * math.cos(math.radians(angle))
            arrow_end_y = player_screen_y + indicator_radius * math.sin(math.radians(angle))
            
            # Рисуем линию стрелки
            pygame.draw.line(self.screen, self.indicator_color, 
                            (player_screen_x, player_screen_y), 
                            (arrow_end_x, arrow_end_y), 
                            3)
            
            # Рисуем наконечник стрелки
            arrow_size = 10
            arrow_angle1 = math.radians(angle + 150)
            arrow_angle2 = math.radians(angle - 150)
            
            arrow_point1_x = arrow_end_x + arrow_size * math.cos(arrow_angle1)
            arrow_point1_y = arrow_end_y + arrow_size * math.sin(arrow_angle1)
            
            arrow_point2_x = arrow_end_x + arrow_size * math.cos(arrow_angle2)
            arrow_point2_y = arrow_end_y + arrow_size * math.sin(arrow_angle2)
            
            pygame.draw.polygon(self.screen, self.indicator_color, 
                               [(arrow_end_x, arrow_end_y), 
                                (arrow_point1_x, arrow_point1_y), 
                                (arrow_point2_x, arrow_point2_y)])
            
            # Рисуем расстояние до портала
            distance_text = self.font.render(f"{int(distance)}", True, self.indicator_color)
            self.screen.blit(distance_text, (arrow_end_x + 5, arrow_end_y + 5)) 