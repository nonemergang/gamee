import pygame
import math
import numpy as np
from ecs.systems.system import System
from ecs.components.components import Position, Player

class LightingSystem(System):
    """Система для создания эффекта плавного освещения вокруг игрока"""
    
    def __init__(self, world, screen, camera_system):
        """
        Инициализирует систему освещения
        :param world: Мир ECS
        :param screen: Поверхность Pygame для отрисовки
        :param camera_system: Система камеры для преобразования координат
        """
        super().__init__(world)
        self.screen = screen
        self.camera_system = camera_system
        
        # Параметры освещения
        self.light_radius = 180  # Меньший радиус света
        self.darkness_alpha = 220  # Максимальная тьма
        
        # Создаем поверхность для затемнения
        self.darkness_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        
        # Создаем радиальный градиент для затемнения
        self.gradient_surface = self._create_radial_gradient(screen.get_width(), screen.get_height(), self.light_radius, self.darkness_alpha)
    
    def update(self, dt):
        """
        Обновляет эффект освещения
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Находим игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if not player_entities:
            return
        
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Получаем смещение камеры
        camera_offset = self.camera_system.get_camera_offset()
        
        # Преобразуем мировые координаты игрока в экранные
        screen_x = int(player_pos.x - camera_offset[0])
        screen_y = int(player_pos.y - camera_offset[1])
        
        # Применяем эффект освещения
        self._apply_lighting(screen_x, screen_y)
    
    def _create_radial_gradient(self, width, height, radius, max_alpha):
        """
        Создаёт радиальный градиент (поверхность) с плавным переходом альфа-канала
        """
        arr = np.zeros((height, width, 4), dtype=np.uint8)
        center_x = width // 2
        center_y = height // 2
        y_indices, x_indices = np.ogrid[:height, :width]
        dist = np.sqrt((x_indices - center_x) ** 2 + (y_indices - center_y) ** 2)
        norm = np.clip(dist / radius, 0, 1)
        alpha = norm * max_alpha  # Линейный градиент: в центре 0, к краям max_alpha
        arr[..., 3] = alpha.astype(np.uint8)
        surface = pygame.surfarray.make_surface(arr[..., :3])
        surface = surface.convert_alpha()
        pygame.surfarray.pixels_alpha(surface)[:, :] = arr[..., 3]
        return surface
    
    def _apply_lighting(self, player_x, player_y):
        """
        Применяет эффект освещения к экрану
        :param player_x: Экранная координата X игрока
        :param player_y: Экранная координата Y игрока
        """
        # Сначала полностью затемняем экран
        self.darkness_surface.fill((0, 0, 0, self.darkness_alpha))
        # Создаём градиент с центром на игроке
        grad = self._create_radial_gradient(self.screen.get_width(), self.screen.get_height(), self.light_radius, self.darkness_alpha)
        grad_rect = grad.get_rect(center=(player_x, player_y))
        # Вырезаем "дырку" света обычным blit (альфа в центре = 0)
        self.darkness_surface.blit(grad, grad_rect)
        # Накладываем затемнение на экран
        self.screen.blit(self.darkness_surface, (0, 0)) 