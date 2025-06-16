import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Bullet, Sprite, Collider, Tile
from ecs.utils.sprite_manager import sprite_manager

def create_bullet_texture():
    """
    Возвращает текстуру пули из менеджера спрайтов или создает дефолтную
    """
    return sprite_manager.get_sprite("bullet")

class WeaponSystem(System):
    """Система для обработки оружия и пуль"""
    
    def __init__(self, world):
        super().__init__(world)
        self.bullet_cooldown = {}  # Словарь для отслеживания перезарядки оружия
        self.reload_status = {}    # Словарь для отслеживания статуса перезарядки
    
    def update(self, dt):
        """
        Обновляет состояние пуль
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Обновляем таймеры перезарядки
        for entity_id, cooldown in list(self.bullet_cooldown.items()):
            self.bullet_cooldown[entity_id] = max(0, cooldown - dt)
        
        # Обновляем статусы перезарядки
        for entity_id in list(self.reload_status.keys()):
            if not self.world.has_component(entity_id, "Weapon"):
                del self.reload_status[entity_id]
                continue
                
            weapon = self.world.get_component(entity_id, "Weapon")
            reload_time = self.reload_status[entity_id]
            
            if reload_time > 0:
                self.reload_status[entity_id] = max(0, reload_time - dt)
                if self.reload_status[entity_id] == 0:
                    weapon.current_ammo = weapon.max_ammo
                    print(f"Перезарядка завершена, патронов: {weapon.current_ammo}")
        
        # Получаем все сущности с пулями
        bullet_entities = self.world.get_entities_with_components(Bullet, Position)
        
        for bullet_id in bullet_entities:
            bullet = self.world.get_component(bullet_id, Bullet)
            
            # Проверяем время жизни пули
            bullet.timer += dt
            if bullet.timer >= bullet.lifetime:
                self.world.delete_entity(bullet_id)
                continue
    
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
        self.world.add_component(bullet_id, Bullet(owner=owner_id, damage=damage, radius=4, lifetime=2.0))
        self.world.add_component(bullet_id, Position(x, y))
        self.world.add_component(bullet_id, Velocity(dx * speed, dy * speed))
        
        # Вычисляем угол поворота для спрайта
        angle = math.degrees(math.atan2(dy, dx))
        
        # Получаем текстуру пули
        bullet_texture = create_bullet_texture()
        
        # Добавляем спрайт для отрисовки с текстурой
        sprite = Sprite(image=bullet_texture, width=12, height=12, layer=5)
        sprite.angle = angle  # Поворачиваем пулю в направлении движения
        self.world.add_component(bullet_id, sprite)
        
        # Добавляем коллайдер для обнаружения столкновений
        self.world.add_component(bullet_id, Collider(width=8, height=8, is_trigger=True))
        
        print(f"Создана пуля ID:{bullet_id} в позиции ({x:.1f}, {y:.1f}) со скоростью ({dx * speed:.1f}, {dy * speed:.1f})")
        
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
    
    def fire_bullet(self, entity_id, target_x, target_y):
        # Проверяем, есть ли у сущности оружие
        if not self.world.has_component(entity_id, "Weapon"):
            print(f"Сущность {entity_id} не имеет компонента Weapon")
            return
        
        weapon = self.world.get_component(entity_id, "Weapon")
        print(f"Найден компонент Weapon у сущности {entity_id}: damage={weapon.damage}, fire_rate={weapon.fire_rate}")
        
        # Проверяем перезарядку
        if entity_id in self.bullet_cooldown and self.bullet_cooldown[entity_id] > 0:
            print(f"Перезарядка: осталось {self.bullet_cooldown[entity_id]:.2f} сек")
            return
            
        # Проверяем, идет ли перезарядка
        if entity_id in self.reload_status and self.reload_status[entity_id] > 0:
            print(f"Идет перезарядка: осталось {self.reload_status[entity_id]:.2f} сек")
            return
        
        # Проверяем боезапас
        if weapon.current_ammo <= 0 and weapon.max_ammo > 0:
            # Автоматическая перезарядка при пустом магазине
            print("Магазин пуст, начинаем перезарядку")
            self.reload(entity_id)
            return
        
        # Уменьшаем боезапас
        if weapon.max_ammo > 0:
            weapon.current_ammo -= 1
        
        # Устанавливаем перезарядку
        self.bullet_cooldown[entity_id] = 1.0 / weapon.fire_rate
        
        # Получаем позицию стрелка
        position = self.world.get_component(entity_id, Position)
        
        # Вычисляем направление
        dx = target_x - position.x
        dy = target_y - position.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Создаем пулю с помощью метода create_bullet
        self.create_bullet(entity_id, position.x, position.y, dx, dy, weapon.damage, weapon.bullet_speed)
        
        # Добавляем отладочную информацию
        print(f"Выстрел! Патронов осталось: {weapon.current_ammo}")
    
    def reload(self, entity_id):
        """
        Перезаряжает оружие сущности
        :param entity_id: ID сущности
        """
        if not self.world.has_component(entity_id, "Weapon"):
            return
            
        weapon = self.world.get_component(entity_id, "Weapon")
        
        # Проверяем, нужна ли перезарядка
        if weapon.current_ammo == weapon.max_ammo:
            return
            
        # Проверяем, идет ли уже перезарядка
        if entity_id in self.reload_status and self.reload_status[entity_id] > 0:
            return
            
        # Начинаем перезарядку
        reload_time = 2.0  # Время перезарядки в секундах
        self.reload_status[entity_id] = reload_time
        print(f"Перезарядка начата, осталось {reload_time:.1f} сек") 