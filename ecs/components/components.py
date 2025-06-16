class Component:
    """Базовый класс для всех компонентов"""
    pass

class Position:
    """Компонент позиции"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Velocity:
    """Компонент скорости"""
    def __init__(self, dx=0, dy=0):
        self.dx = dx
        self.dy = dy
        
    # Свойства для совместимости с кодом, использующим x и y вместо dx и dy
    @property
    def x(self):
        return self.dx
        
    @x.setter
    def x(self, value):
        self.dx = value
        
    @property
    def y(self):
        return self.dy
        
    @y.setter
    def y(self, value):
        self.dy = value

class Sprite:
    """Компонент для отображения спрайта"""
    def __init__(self, image=None, width=32, height=32, color=(255, 255, 255), layer=0):
        self.image = image
        self.width = width
        self.height = height
        self.color = color
        self.layer = layer  # Слой отрисовки (более высокий слой отрисовывается поверх)
        self.flip_x = False
        self.flip_y = False
        self.angle = 0

class Player:
    """Маркерный компонент для игрока"""
    def __init__(self, speed=150):
        self.speed = speed
        self.health = 100
        self.max_health = 100

class Enemy:
    """Компонент для врагов"""
    def __init__(self, speed=100, damage=10, detection_radius=300, attack_radius=50, attack_rate=1.0):
        self.speed = speed
        self.damage = damage
        self.detection_radius = detection_radius
        self.attack_radius = attack_radius
        self.attack_rate = attack_rate
        self.attack_cooldown = 0

class Collider:
    """Компонент для коллизий"""
    def __init__(self, width=32, height=32, is_trigger=False):
        self.width = width
        self.height = height
        self.is_trigger = is_trigger  # Если True, то не блокирует движение

class Weapon:
    """Компонент для оружия"""
    def __init__(self, damage=10, fire_rate=5, bullet_speed=400, max_ammo=30):
        self.damage = damage
        self.fire_rate = fire_rate
        self.bullet_speed = bullet_speed
        self.max_ammo = max_ammo
        self.current_ammo = max_ammo  # Текущее количество патронов
        self.cooldown = 0
        self.is_reloading = False
        self.reload_time = 2.0
        self.reload_timer = 0

class Bullet:
    """Компонент для пуль"""
    def __init__(self, owner=None, damage=10, radius=4, lifetime=2.0):
        self.owner = owner  # ID владельца пули
        self.damage = damage
        self.radius = radius  # Радиус пули для проверки столкновений
        self.lifetime = lifetime  # Время жизни пули в секундах
        self.timer = 0

class Health:
    """Компонент здоровья"""
    def __init__(self, maximum=100, current=100, regeneration_rate=0, regeneration_interval=1.0):
        self.maximum = maximum
        self.current = current
        self.regeneration_rate = regeneration_rate
        self.regeneration_interval = regeneration_interval
        self.regeneration_timer = 0
        self.invulnerable = False
        self.invulnerable_timer = 0

class Camera:
    """Компонент камеры"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_id = None  # ID сущности, за которой следует камера

class Tile:
    """Компонент для тайлов уровня"""
    def __init__(self, name="floor", walkable=True):
        self.name = name
        self.walkable = walkable

class PathDebug:
    """Компонент для отображения пути"""
    def __init__(self, path=None):
        self.path = path or []  # Список точек пути [(x1, y1), (x2, y2), ...]
        self.visible = True  # Флаг видимости пути 