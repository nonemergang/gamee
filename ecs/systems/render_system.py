import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Sprite, Health, Weapon, PathDebug, Player

class RenderSystem(System):
    """Система для отрисовки игровых объектов"""
    
    def __init__(self, world, screen, camera_system):
        """
        Инициализирует систему отрисовки
        :param world: Мир ECS
        :param screen: Поверхность Pygame для отрисовки
        :param camera_system: Система камеры для преобразования координат
        """
        super().__init__(world)
        self.screen = screen
        self.camera_system = camera_system
        
        # Создаем шрифт для отображения текста
        self.font = pygame.font.SysFont(None, 24)
        
        # Загружаем или создаем текстуры для интерфейса
        self.ui_textures = self._create_ui_textures()
        
        # Флаг для отображения отладочной информации
        self.debug = False
        
        # Создаем поверхность для затемнения
        self.darkness_surface = None
        self.light_radius = 300  # Радиус света вокруг игрока
        
        # Предварительно создаем градиентные маски для разных масштабов
        self.light_masks = {}
        self.current_zoom = 0
        self.update_darkness_surface()
    
    def update_darkness_surface(self):
        """Обновляет поверхность затемнения"""
        # Создаем поверхность размером с экран
        self.darkness_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        
        # Заполняем поверхность полупрозрачным черным цветом
        self.darkness_surface.fill((0, 0, 0, 180))  # RGBA: черный с 70% непрозрачности
    
    def _create_light_mask(self, radius):
        """
        Создает градиентную маску света
        :param radius: Радиус света
        :return: Поверхность с градиентной маской
        """
        # Создаем маску для света
        light_mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        # Шаг для оптимизации (рисуем не каждый пиксель)
        step = max(1, int(radius / 100))
        
        # Создаем градиентный круг
        for r in range(int(radius), 0, -step):
            # Вычисляем прозрачность в зависимости от расстояния от центра
            alpha = int(180 * (r / radius))  # От 0 до 180
            alpha = min(180, alpha)  # Ограничиваем максимальную непрозрачность
            
            # Рисуем круг с нужной прозрачностью
            pygame.draw.circle(light_mask, (0, 0, 0, alpha), (radius, radius), r)
        
        return light_mask
    
    def update(self, dt):
        """
        Отрисовывает все объекты
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Проверяем, изменился ли масштаб камеры
        current_zoom = self.camera_system.get_zoom()
        if abs(current_zoom - self.current_zoom) > 0.1:
            # Если масштаб значительно изменился, очищаем кэш масок
            self.light_masks = {}
            self.current_zoom = current_zoom
        
        # Очищаем экран
        self.screen.fill((0, 0, 0))
        
        # Получаем все сущности со спрайтами и позициями
        sprite_entities = self.world.get_entities_with_components(Sprite, Position)
        
        # Сортируем сущности по слою спрайта (чтобы отрисовывать в правильном порядке)
        sprite_entities.sort(key=lambda entity_id: self.world.get_component(entity_id, Sprite).layer)
        
        # Отрисовываем каждую сущность
        for entity_id in sprite_entities:
            sprite = self.world.get_component(entity_id, Sprite)
            position = self.world.get_component(entity_id, Position)
            
            # Преобразуем мировые координаты в экранные с учетом камеры
            screen_x, screen_y = self.camera_system.world_to_screen(position.x, position.y)
            
            # Создаем прямоугольник для отрисовки
            rect = pygame.Rect(
                screen_x - sprite.width / 2 * self.camera_system.get_zoom(),
                screen_y - sprite.height / 2 * self.camera_system.get_zoom(),
                sprite.width * self.camera_system.get_zoom(),
                sprite.height * self.camera_system.get_zoom()
            )
            
            # Проверяем, находится ли объект в пределах экрана
            screen_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
            if not screen_rect.colliderect(rect):
                continue  # Пропускаем объекты вне экрана
            
            # Если у спрайта есть изображение, отрисовываем его
            if sprite.image:
                # Если у спрайта есть угол поворота, поворачиваем изображение
                if sprite.angle != 0:
                    # Масштабируем изображение до нужного размера с учетом масштаба камеры
                    scaled_image = pygame.transform.scale(sprite.image, (
                        int(sprite.width * self.camera_system.get_zoom()),
                        int(sprite.height * self.camera_system.get_zoom())
                    ))
                    # Поворачиваем изображение
                    rotated_image = pygame.transform.rotate(scaled_image, -sprite.angle)  # Отрицательный угол для правильного поворота
                    # Получаем прямоугольник повернутого изображения
                    rotated_rect = rotated_image.get_rect(center=rect.center)
                    # Отрисовываем повернутое изображение
                    self.screen.blit(rotated_image, rotated_rect)
                else:
                    # Отрисовываем изображение без поворота
                    scaled_image = pygame.transform.scale(sprite.image, (
                        int(sprite.width * self.camera_system.get_zoom()),
                        int(sprite.height * self.camera_system.get_zoom())
                    ))
                    self.screen.blit(scaled_image, rect)
            else:
                # Если у спрайта нет изображения, отрисовываем прямоугольник с цветом
                pygame.draw.rect(self.screen, sprite.color, rect)
        
        # Отрисовываем частицы эффектов попадания
        self._render_hit_particles()
        
        # Отрисовываем пути (для отладки)
        if self.debug:
            self._render_paths()
        
        # Применяем эффект затемнения с градиентным кругом
        self._render_darkness_effect()
        
        # Отрисовываем пользовательский интерфейс
        self._render_ui()
    
    def _render_darkness_effect(self):
        """Отрисовывает эффект затемнения с градиентным кругом вокруг игрока"""
        # Получаем игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if not player_entities:
            return
            
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Преобразуем позицию игрока в экранные координаты
        screen_x, screen_y = self.camera_system.world_to_screen(player_pos.x, player_pos.y)
        
        # Создаем копию поверхности затемнения
        darkness_copy = self.darkness_surface.copy()
        
        # Радиус света зависит от масштаба камеры
        light_radius = int(self.light_radius * self.camera_system.get_zoom())
        
        # Используем кэшированную маску или создаем новую
        light_mask_key = light_radius
        if light_mask_key not in self.light_masks:
            self.light_masks[light_mask_key] = self._create_light_mask(light_radius)
        
        light_mask = self.light_masks[light_mask_key]
        
        # Вырезаем круг из поверхности затемнения
        darkness_copy.blit(light_mask, (screen_x - light_radius, screen_y - light_radius), special_flags=pygame.BLEND_RGBA_SUB)
        
        # Отображаем затемнение на экране
        self.screen.blit(darkness_copy, (0, 0))
    
    def _render_paths(self):
        """Отрисовывает пути для отладки"""
        # Получаем все сущности с путями
        path_entities = self.world.get_entities_with_components(PathDebug, Position)
        
        for entity_id in path_entities:
            path_debug = self.world.get_component(entity_id, PathDebug)
            position = self.world.get_component(entity_id, Position)
            
            # Если путь не пустой и видимый
            if path_debug.path and path_debug.visible:
                # Отрисовываем линии между точками пути
                prev_point = (position.x, position.y)
                for point in path_debug.path:
                    # Преобразуем мировые координаты в экранные
                    screen_prev_x, screen_prev_y = self.camera_system.world_to_screen(prev_point[0], prev_point[1])
                    screen_x, screen_y = self.camera_system.world_to_screen(point[0], point[1])
                    
                    # Отрисовываем линию
                    pygame.draw.line(self.screen, (0, 255, 0), (screen_prev_x, screen_prev_y), (screen_x, screen_y), 2)
                    
                    # Отрисовываем точку
                    pygame.draw.circle(self.screen, (255, 0, 0), (screen_x, screen_y), 3)
                    
                    prev_point = point
    
    def _render_health_bar(self, x, y, width, health):
        """
        Отрисовывает полоску здоровья
        :param x: Позиция X
        :param y: Позиция Y
        :param width: Ширина объекта
        :param health: Компонент здоровья
        """
        # Параметры полоски здоровья
        bar_width = width
        bar_height = 5
        bar_y_offset = 10  # Смещение полоски здоровья вверх от объекта
        
        # Вычисляем процент здоровья
        health_percent = health.current / health.maximum
        
        # Создаем прямоугольники для фона и заполнения
        bg_rect = pygame.Rect(x - bar_width / 2, y - bar_height / 2 - bar_y_offset, bar_width, bar_height)
        fill_rect = pygame.Rect(x - bar_width / 2, y - bar_height / 2 - bar_y_offset, bar_width * health_percent, bar_height)
        
        # Определяем цвет в зависимости от процента здоровья
        if health_percent > 0.7:
            color = (0, 255, 0)  # Зеленый
        elif health_percent > 0.3:
            color = (255, 255, 0)  # Желтый
        else:
            color = (255, 0, 0)  # Красный
        
        # Отрисовываем полоску здоровья
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)  # Фон
        pygame.draw.rect(self.screen, color, fill_rect)  # Заполнение
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 1)  # Граница
    
    def _render_ui(self):
        """Отрисовка пользовательского интерфейса"""
        # Получаем игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if not player_entities:
            return
            
        player_id = player_entities[0]
        
        # Получаем компоненты здоровья и оружия
        if not self.world.has_component(player_id, Health) or not self.world.has_component(player_id, "Weapon"):
            return
            
        health = self.world.get_component(player_id, Health)
        weapon = self.world.get_component(player_id, "Weapon")
        
        # Отрисовка здоровья
        health_text = f"Здоровье: {health.current}/{health.maximum}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (10, 10))
        
        # Отрисовка полоски здоровья
        health_percent = health.current / health.maximum
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 40
        
        # Фон полоски здоровья
        pygame.draw.rect(self.screen, (100, 100, 100), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Полоска здоровья
        health_width = int(health_bar_width * health_percent)
        health_color = (0, 255, 0)  # Зеленый
        if health_percent < 0.3:
            health_color = (255, 0, 0)  # Красный
        elif health_percent < 0.7:
            health_color = (255, 255, 0)  # Желтый
            
        pygame.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, health_width, health_bar_height))
        
        # Отрисовка боеприпасов
        ammo_text = f"Патроны: {weapon.current_ammo}/{weapon.max_ammo}"
        ammo_surface = self.font.render(ammo_text, True, (255, 255, 255))
        self.screen.blit(ammo_surface, (10, 70))
    
    def _create_ui_textures(self):
        """
        Создает текстуры для интерфейса
        :return: Словарь с текстурами
        """
        textures = {}
        
        # Создаем текстуру для иконки здоровья
        health_icon = pygame.Surface((24, 24))
        health_icon.fill((255, 0, 0))
        pygame.draw.rect(health_icon, (200, 0, 0), (2, 2, 20, 20))
        pygame.draw.rect(health_icon, (255, 255, 255), (10, 5, 4, 14))
        pygame.draw.rect(health_icon, (255, 255, 255), (5, 10, 14, 4))
        textures["health"] = health_icon
        
        # Создаем текстуру для иконки патронов
        ammo_icon = pygame.Surface((24, 24))
        ammo_icon.fill((100, 100, 100))
        pygame.draw.rect(ammo_icon, (200, 200, 0), (2, 2, 20, 20))
        pygame.draw.rect(ammo_icon, (255, 255, 255), (8, 5, 8, 15))
        pygame.draw.rect(ammo_icon, (255, 255, 255), (6, 18, 12, 3))
        textures["ammo"] = ammo_icon
        
        return textures
    
    def _render_hit_particles(self):
        """Отрисовывает частицы эффектов попадания"""
        # Получаем систему столкновений
        from ecs.systems.collision_system import CollisionSystem
        collision_system = next((system for system in self.world.systems if isinstance(system, CollisionSystem)), None)
        
        if not collision_system or not hasattr(collision_system, 'hit_effects'):
            return
        
        # Отрисовываем частицы для каждого эффекта
        for effect in collision_system.hit_effects:
            for particle in effect['particles']:
                try:
                    # Преобразуем мировые координаты частицы в экранные
                    screen_x, screen_y = self.camera_system.world_to_screen(particle['x'], particle['y'])
                    
                    # Вычисляем размер частицы с учетом масштаба камеры
                    size = particle['size'] * self.camera_system.get_zoom()
                    
                    # Вычисляем прозрачность частицы в зависимости от оставшегося времени жизни
                    fade = 1 - (particle['timer'] / particle['lifetime'])
                    
                    # Получаем цвет частицы и применяем затухание
                    color = particle['color']
                    r = max(0, min(255, int(color[0] * fade)))
                    g = max(0, min(255, int(color[1] * fade)))
                    b = max(0, min(255, int(color[2] * fade)))
                    
                    # Отрисовываем частицу как круг
                    pygame.draw.circle(self.screen, (r, g, b), (int(screen_x), int(screen_y)), max(1, int(size)))
                except Exception as e:
                    # Если возникла ошибка при отрисовке частицы, пропускаем её
                    print(f"Ошибка при отрисовке частицы: {e}") 

    def render(self, camera=None):
        """
        Отрисовывает все объекты на экране
        :param camera: Камера для преобразования координат (не используется, так как у нас есть self.camera_system)
        """
        # Очищаем экран
        self.screen.fill((0, 0, 0))
        
        # Получаем все сущности со спрайтами и позициями
        sprite_entities = self.world.get_entities_with_components(Sprite, Position)
        
        # Сортируем сущности по слою спрайта (чтобы отрисовывать в правильном порядке)
        sprite_entities.sort(key=lambda entity_id: self.world.get_component(entity_id, Sprite).layer)
        
        # Отрисовываем каждую сущность
        for entity_id in sprite_entities:
            sprite = self.world.get_component(entity_id, Sprite)
            position = self.world.get_component(entity_id, Position)
            
            # Преобразуем мировые координаты в экранные с учетом камеры
            screen_x, screen_y = self.camera_system.world_to_screen(position.x, position.y)
            
            # Создаем прямоугольник для отрисовки
            rect = pygame.Rect(
                screen_x - sprite.width / 2 * self.camera_system.get_zoom(),
                screen_y - sprite.height / 2 * self.camera_system.get_zoom(),
                sprite.width * self.camera_system.get_zoom(),
                sprite.height * self.camera_system.get_zoom()
            )
            
            # Проверяем, находится ли объект в пределах экрана
            screen_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
            if not screen_rect.colliderect(rect):
                continue  # Пропускаем объекты вне экрана
            
            # Если у спрайта есть изображение, отрисовываем его
            if sprite.image:
                # Если у спрайта есть угол поворота, поворачиваем изображение
                if sprite.angle != 0:
                    # Масштабируем изображение до нужного размера с учетом масштаба камеры
                    scaled_image = pygame.transform.scale(sprite.image, (
                        int(sprite.width * self.camera_system.get_zoom()),
                        int(sprite.height * self.camera_system.get_zoom())
                    ))
                    # Поворачиваем изображение
                    rotated_image = pygame.transform.rotate(scaled_image, -sprite.angle)  # Отрицательный угол для правильного поворота
                    # Получаем прямоугольник повернутого изображения
                    rotated_rect = rotated_image.get_rect(center=rect.center)
                    # Отрисовываем повернутое изображение
                    self.screen.blit(rotated_image, rotated_rect)
                else:
                    # Отрисовываем изображение без поворота
                    scaled_image = pygame.transform.scale(sprite.image, (
                        int(sprite.width * self.camera_system.get_zoom()),
                        int(sprite.height * self.camera_system.get_zoom())
                    ))
                    self.screen.blit(scaled_image, rect)
            else:
                # Если у спрайта нет изображения, отрисовываем прямоугольник с цветом
                pygame.draw.rect(self.screen, sprite.color, rect)
        
        # Отрисовываем частицы эффектов попадания
        self._render_hit_particles()
        
        # Отрисовываем пути (для отладки)
        if self.debug:
            self._render_paths()
        
        # Применяем эффект затемнения с градиентным кругом
        self._render_darkness_effect()
        
        # Отрисовываем пользовательский интерфейс
        self._render_ui() 