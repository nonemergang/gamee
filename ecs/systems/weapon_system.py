import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Bullet, Sprite, Collider

def create_bullet_texture():
    """Создает текстуру пули"""
    size = 8
    texture = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Основная пуля (желтая)
    pygame.draw.circle(texture, (255, 255, 0), (size//2, size//2), size//2)
    
    # Внутренняя часть (более яркая)
    pygame.draw.circle(texture, (255, 255, 200), (size//2, size//2), size//4)
    
    # Эффект свечения
    glow = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    for i in range(5):
        alpha = 100 - i * 20
        radius = size//2 + i
        pygame.draw.circle(glow, (255, 255, 0, alpha), (size, size), radius)
    
    # Объединяем основную пулю и свечение
    final_texture = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    final_texture.blit(glow, (0, 0))
    final_texture.blit(texture, (size - size//2, size - size//2))
    
    return final_texture

class WeaponSystem(System):
    """Система для обработки оружия и пуль"""
    
    def __init__(self, world):
        super().__init__(world)
        self.bullet_texture = create_bullet_texture()
    
    def update(self, dt):
        """
        Обновляет состояние пуль
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с пулями
        bullet_entities = self.world.get_entities_with_components(Bullet, Position)
        
        for bullet_id in bullet_entities:
            bullet = self.world.get_component(bullet_id, Bullet)
            
            # Обновляем время жизни пули
            bullet.timer += dt
            
            # Если время жизни пули истекло, удаляем её
            if bullet.timer >= bullet.lifetime:
                self.world.delete_entity(bullet_id)
    
    def create_bullet(self, owner_id, x, y, dx, dy, damage, speed):
        """
        Создает пулю
        :param owner_id: ID владельца пули
        :param x: Начальная позиция X
        :param y: Начальная позиция Y
        :param dx: Направление X
        :param dy: Направление Y
        :param damage: Урон пули
        :param speed: Скорость пули
        :return: ID созданной пули
        """
        # Создаем сущность пули
        bullet_id = self.world.create_entity()
        
        # Добавляем компоненты
        self.world.add_component(bullet_id, Bullet(owner_id, damage))
        self.world.add_component(bullet_id, Position(x, y))
        self.world.add_component(bullet_id, Velocity(dx * speed, dy * speed))
        
        # Вычисляем угол поворота для спрайта
        angle = math.degrees(math.atan2(dy, dx))
        
        # Добавляем спрайт для отрисовки с текстурой
        sprite = Sprite(image=self.bullet_texture, width=16, height=16, layer=5)
        sprite.angle = angle  # Поворачиваем пулю в направлении движения
        self.world.add_component(bullet_id, sprite)
        
        # Добавляем коллайдер для обнаружения столкновений
        self.world.add_component(bullet_id, Collider(width=8, height=8, is_trigger=True))
        
        return bullet_id 