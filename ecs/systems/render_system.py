import pygame
from ecs.systems.system import System
from ecs.components.components import Position, Sprite, Health, Weapon

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
    
    def update(self, dt):
        """
        Отрисовывает все сущности с компонентами Position и Sprite
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Очищаем экран
        self.screen.fill((0, 0, 0))
        
        # Получаем смещение камеры
        camera_offset = self.camera_system.get_camera_offset()
        
        # Собираем все сущности с компонентами Position и Sprite
        renderable_entities = self.world.get_entities_with_components(Position, Sprite)
        
        # Сортируем сущности по слою отрисовки
        sorted_entities = []
        for entity_id in renderable_entities:
            sprite = self.world.get_component(entity_id, Sprite)
            sorted_entities.append((entity_id, sprite.layer))
        
        sorted_entities.sort(key=lambda x: x[1])
        
        # Отрисовываем сущности
        for entity_id, _ in sorted_entities:
            position = self.world.get_component(entity_id, Position)
            sprite = self.world.get_component(entity_id, Sprite)
            
            # Преобразуем мировые координаты в экранные
            screen_x = position.x - camera_offset[0]
            screen_y = position.y - camera_offset[1]
            
            # Проверяем, находится ли объект в пределах экрана
            if (screen_x + sprite.width / 2 < 0 or screen_x - sprite.width / 2 > self.screen.get_width() or
                screen_y + sprite.height / 2 < 0 or screen_y - sprite.height / 2 > self.screen.get_height()):
                continue  # Пропускаем отрисовку объектов за пределами экрана
            
            # Создаем прямоугольник для отрисовки
            rect = pygame.Rect(
                screen_x - sprite.width / 2,
                screen_y - sprite.height / 2,
                sprite.width,
                sprite.height
            )
            
            # Если у спрайта есть изображение, отрисовываем его
            if sprite.image:
                # Создаем копию изображения для поворота
                rotated_image = pygame.transform.rotate(sprite.image, sprite.angle)
                
                # Получаем новый прямоугольник после поворота
                rotated_rect = rotated_image.get_rect(center=rect.center)
                
                # Отрисовываем изображение
                self.screen.blit(rotated_image, rotated_rect)
            else:
                # Иначе отрисовываем цветной прямоугольник
                pygame.draw.rect(self.screen, sprite.color, rect)
            
            # Если у сущности есть компонент здоровья, отрисовываем полоску здоровья
            if self.world.has_component(entity_id, Health):
                health = self.world.get_component(entity_id, Health)
                self._render_health_bar(screen_x, screen_y, sprite.width, health)
        
        # Отрисовываем интерфейс
        self._render_ui()
    
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
        """Отрисовывает пользовательский интерфейс"""
        # Находим игрока
        player_entities = self.world.get_entities_with_components(Position, Health, Weapon)
        
        if not player_entities:
            return
        
        player_id = player_entities[0]
        health = self.world.get_component(player_id, Health)
        weapon = self.world.get_component(player_id, Weapon)
        
        # Отрисовываем здоровье игрока
        health_text = f"Здоровье: {health.current}/{health.maximum}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (10, 10))
        
        # Отрисовываем боеприпасы
        ammo_text = f"Патроны: {weapon.ammo}/{weapon.max_ammo}"
        ammo_surface = self.font.render(ammo_text, True, (255, 255, 255))
        self.screen.blit(ammo_surface, (10, 40))
        
        # Если идет перезарядка, отображаем индикатор
        if weapon.is_reloading:
            reload_progress = weapon.reload_timer / weapon.reload_time
            reload_text = f"Перезарядка: {int(reload_progress * 100)}%"
            reload_surface = self.font.render(reload_text, True, (255, 200, 0))
            self.screen.blit(reload_surface, (10, 70))
    
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