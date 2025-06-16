import pygame
from ecs.systems.system import System
from ecs.components.components import Position, Sprite, Player, Enemy, Health, Weapon
from ecs.systems.camera_system import CameraSystem

class RenderSystem(System):
    """Система для отрисовки всех сущностей"""
    
    def __init__(self, world, screen):
        super().__init__(world)
        self.screen = screen
        self.camera_system = None
        
        # Шрифт для отображения текста
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
    
    def render(self):
        """Отрисовывает все сущности с компонентами Sprite"""
        # Находим систему камеры
        if self.camera_system is None:
            self.camera_system = next((system for system in self.world.systems if isinstance(system, CameraSystem)), None)
        
        # Получаем смещение камеры
        camera_offset = (0, 0)
        if self.camera_system:
            camera_offset = self.camera_system.get_camera_offset()
        
        # Получаем все сущности со спрайтами и сортируем их по слоям
        sprite_entities = self.world.get_entities_with_components(Position, Sprite)
        sprite_entities_with_layers = [(entity_id, self.world.get_component(entity_id, Sprite).layer) for entity_id in sprite_entities]
        sprite_entities_sorted = [entity_id for entity_id, _ in sorted(sprite_entities_with_layers, key=lambda x: x[1])]
        
        # Отрисовываем каждую сущность
        for entity_id in sprite_entities_sorted:
            position = self.world.get_component(entity_id, Position)
            sprite = self.world.get_component(entity_id, Sprite)
            
            # Вычисляем экранные координаты с учетом смещения камеры
            screen_x = int(position.x + camera_offset[0])
            screen_y = int(position.y + camera_offset[1])
            
            # Если у сущности есть изображение, отрисовываем его
            if sprite.image:
                # Применяем поворот и отражение, если нужно
                image = sprite.image
                if sprite.flip_x or sprite.flip_y:
                    image = pygame.transform.flip(image, sprite.flip_x, sprite.flip_y)
                if sprite.angle != 0:
                    image = pygame.transform.rotate(image, sprite.angle)
                
                # Отрисовываем изображение
                rect = image.get_rect(center=(screen_x, screen_y))
                self.screen.blit(image, rect)
            else:
                # Если изображения нет, отрисовываем прямоугольник или круг
                pygame.draw.rect(self.screen, sprite.color, (screen_x - sprite.width // 2, screen_y - sprite.height // 2, sprite.width, sprite.height))
        
        # Отрисовываем интерфейс
        self._render_ui()
    
    def _render_ui(self):
        """Отрисовывает пользовательский интерфейс"""
        # Получаем игрока
        player_entities = self.world.get_entities_with_components(Player, Health)
        if not player_entities:
            return
        
        player_id = player_entities[0]
        player_health = self.world.get_component(player_id, Health)
        
        # Отрисовываем полосу здоровья
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = 20
        
        # Фон полосы здоровья
        pygame.draw.rect(self.screen, (50, 50, 50), (health_x, health_y, health_width, health_height))
        
        # Заполнение полосы здоровья
        health_fill_width = int(health_width * (player_health.value / player_health.max_value))
        pygame.draw.rect(self.screen, (255, 0, 0), (health_x, health_y, health_fill_width, health_height))
        
        # Рамка полосы здоровья
        pygame.draw.rect(self.screen, (200, 200, 200), (health_x, health_y, health_width, health_height), 2)
        
        # Текст здоровья
        health_text = f"HP: {player_health.value}/{player_health.max_value}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (health_x + 10, health_y + (health_height - health_surface.get_height()) // 2))
        
        # Отрисовываем информацию об оружии, если есть
        if self.world.has_component(player_id, Weapon):
            weapon = self.world.get_component(player_id, Weapon)
            
            # Отрисовываем количество патронов
            ammo_text = f"Ammo: {weapon.ammo}/{weapon.max_ammo}"
            ammo_surface = self.font.render(ammo_text, True, (255, 255, 255))
            self.screen.blit(ammo_surface, (health_x, health_y + health_height + 10))
            
            # Отрисовываем тип оружия
            weapon_text = f"Weapon: {weapon.type}"
            weapon_surface = self.font.render(weapon_text, True, (255, 255, 255))
            self.screen.blit(weapon_surface, (health_x, health_y + health_height + 40))
            
            # Если идет перезарядка, отображаем индикатор
            if weapon.is_reloading:
                reload_text = "Reloading..."
                reload_surface = self.font.render(reload_text, True, (255, 255, 0))
                self.screen.blit(reload_surface, (health_x + 150, health_y + health_height + 10)) 