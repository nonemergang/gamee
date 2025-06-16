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
        self.ammo = max_ammo
        self.cooldown = 0
        self.is_reloading = False
        self.reload_time = 2.0
        self.reload_timer = 0

class Bullet:
    """Компонент для пуль"""
    def __init__(self, owner_id, damage=10, lifetime=2.0):
        self.owner_id = owner_id
        self.damage = damage
        self.lifetime = lifetime
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