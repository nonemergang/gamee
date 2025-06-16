import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Bullet, Sprite, Collider, Tile

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
        
        # Получаем все стены для проверки столкновений
        wall_entities = []
        tile_entities = self.world.get_entities_with_components(Tile, Position, Collider)
        for tile_id in tile_entities:
            tile = self.world.get_component(tile_id, Tile)
            if not tile.walkable:  # Если тайл непроходимый (стена)
                wall_entities.append(tile_id)
        
        for bullet_id in bullet_entities:
            bullet = self.world.get_component(bullet_id, Bullet)
            bullet_pos = self.world.get_component(bullet_id, Position)
            bullet_collider = self.world.get_component(bullet_id, Collider)
            
            # Обновляем время жизни пули
            bullet.timer += dt
            
            # Если время жизни пули истекло, удаляем её
            if bullet.timer >= bullet.lifetime:
                self.world.delete_entity(bullet_id)
                continue
            
            # Проверяем столкновения пули со стенами
            for wall_id in wall_entities:
                wall_pos = self.world.get_component(wall_id, Position)
                wall_collider = self.world.get_component(wall_id, Collider)
                
                # Проверяем столкновение
                if self._check_collision(bullet_pos, bullet_collider, wall_pos, wall_collider):
                    self.world.delete_entity(bullet_id)
                    break
    
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
        
        # Нормализуем вектор направления
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # Смещаем начальную позицию пули от игрока в направлении выстрела
        # чтобы избежать задержки пули в персонаже
        offset = 20  # Расстояние смещения от игрока
        x += dx * offset
        y += dy * offset
        
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
    
    def _check_collision(self, pos1, collider1, pos2, collider2):
        """
        Проверяет столкновение между двумя сущностями
        :param pos1: Компонент Position первой сущности
        :param collider1: Компонент Collider первой сущности
        :param pos2: Компонент Position второй сущности
        :param collider2: Компонент Collider второй сущности
        :return: True, если есть столкновение, иначе False
        """
        # Проверяем, что все параметры существуют
        if not pos1 or not collider1 or not pos2 or not collider2:
            return False
            
        # Вычисляем границы первой сущности
        left1 = pos1.x - collider1.width / 2
        right1 = pos1.x + collider1.width / 2
        top1 = pos1.y - collider1.height / 2
        bottom1 = pos1.y + collider1.height / 2
        
        # Вычисляем границы второй сущности
        left2 = pos2.x - collider2.width / 2
        right2 = pos2.x + collider2.width / 2
        top2 = pos2.y - collider2.height / 2
        bottom2 = pos2.y + collider2.height / 2
        
        # Проверяем пересечение (AABB коллизия)
        return (left1 < right2 and right1 > left2 and
                top1 < bottom2 and bottom1 > top2) 