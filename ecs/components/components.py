class Component:
    """Базовый класс для всех компонентов"""
    pass

class Position:
    """Компонент позиции"""
    def __init__(self, x=0, y=0):
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
    def __init__(self):
        self.speed = 200  # Скорость движения
        self.health = 100
        self.max_health = 100

class Enemy:
    """Компонент для врагов"""
    def __init__(self, type="basic", speed=100, health=30, damage=10):
        self.type = type
        self.speed = speed
        self.health = health
        self.max_health = health
        self.damage = damage
        self.detection_radius = 400  # Радиус обнаружения игрока
        self.attack_cooldown = 0

class Collider:
    """Компонент для коллизий"""
    def __init__(self, width=32, height=32, is_trigger=False):
        self.width = width
        self.height = height
        self.is_trigger = is_trigger  # Если True, то не блокирует движение

class Weapon:
    """Компонент для оружия"""
    def __init__(self, type="pistol", damage=10, fire_rate=0.5, bullet_speed=500, ammo=12, max_ammo=12):
        self.type = type
        self.damage = damage
        self.fire_rate = fire_rate  # Выстрелов в секунду
        self.bullet_speed = bullet_speed
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.cooldown = 0
        self.is_reloading = False
        self.reload_time = 1.0  # Время перезарядки в секундах
        self.reload_timer = 0

class Bullet:
    """Компонент для пуль"""
    def __init__(self, owner_id, damage=10, lifetime=2.0):
        self.owner_id = owner_id
        self.damage = damage
        self.lifetime = lifetime  # Время жизни пули в секундах
        self.timer = 0

class Health:
    """Компонент здоровья"""
    def __init__(self, value=100, max_value=100):
        self.value = value
        self.max_value = max_value
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
    def __init__(self, type="floor", walkable=True):
        self.type = type
        self.walkable = walkable 