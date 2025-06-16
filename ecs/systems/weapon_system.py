from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Bullet, Sprite, Collider

class WeaponSystem(System):
    """Система для обработки оружия и пуль"""
    
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
        
        # Добавляем спрайт для отрисовки
        self.world.add_component(bullet_id, Sprite(width=8, height=8, color=(255, 255, 0), layer=5))
        
        # Добавляем коллайдер для обнаружения столкновений
        self.world.add_component(bullet_id, Collider(width=8, height=8, is_trigger=True))
        
        return bullet_id 