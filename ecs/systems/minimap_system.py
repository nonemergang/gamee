import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Minimap, Position, Player

class MinimapSystem(System):
    """
    Система для отображения мини-карты, показывающей расположение портала
    """
    def __init__(self, world, screen):
        super().__init__(world)
        self.screen = screen
        self.player_position = None
        self.pulse_timer = 0
        
    def update(self, dt):
        """
        Обновляет мини-карту
        :param dt: Время, прошедшее с последнего обновления
        """
        # Обновляем таймер пульсации
        self.pulse_timer += dt
        
        # Получаем позицию игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if player_entities:
            player_id = player_entities[0]
            self.player_position = self.world.get_component(player_id, Position)
    
    def render(self, camera=None):
        """
        Отрисовывает мини-карту
        :param camera: Камера для преобразования координат (не используется для мини-карты)
        """
        minimap_entities = self.world.get_entities_with_components(Minimap)
        if not minimap_entities:
            return
            
        minimap_id = minimap_entities[0]
        minimap = self.world.get_component(minimap_id, Minimap)
        
        if not minimap.visible or not minimap.surface:
            return
            
        # Получаем размеры мини-карты
        minimap_width = minimap.surface.get_width()
        minimap_height = minimap.surface.get_height()
        
        # Создаем копию поверхности мини-карты для добавления текущей позиции игрока
        display_surface = minimap.surface.copy()
        
        # Если есть позиция игрока, отображаем её на мини-карте
        if self.player_position:
            # Получаем размеры уровня из карты
            level_width = 30 * 32  # Ширина уровня в пикселях (30 тайлов по 32 пикселя)
            level_height = 30 * 32  # Высота уровня в пикселях
            
            # Масштабирование координат игрока для мини-карты
            player_x = int(self.player_position.x / level_width * minimap_width)
            player_y = int(self.player_position.y / level_height * minimap_height)
            
            # Создаем эффект пульсации для маркера игрока
            pulse_value = abs(math.sin(self.pulse_timer * 5)) * 0.5 + 0.5  # От 0.5 до 1.0
            pulse_radius = int(5 * pulse_value + 3)
            
            # Рисуем маркер игрока (пульсирующий белый круг)
            pygame.draw.circle(display_surface, (255, 255, 255), (player_x, player_y), pulse_radius)
            
        # Добавляем рамку вокруг мини-карты
        pygame.draw.rect(display_surface, (255, 255, 255), (0, 0, minimap_width, minimap_height), 2)
        
        # Отображаем мини-карту в углу экрана
        self.screen.blit(display_surface, minimap.position)
        
        # Добавляем заголовок мини-карты
        font = pygame.font.SysFont(None, 20)
        title_surface = font.render("КАРТА", True, (255, 255, 255))
        self.screen.blit(title_surface, (minimap.position[0] + minimap_width // 2 - title_surface.get_width() // 2, 
                                        minimap.position[1] - 25))
    
    # Оставляем метод draw для обратной совместимости
    def draw(self):
        """
        Устаревший метод отрисовки мини-карты, используйте render вместо него
        """
        self.render() 