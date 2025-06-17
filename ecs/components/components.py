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
        self.image = image  # Изображение
        self.width = width  # Ширина
        self.height = height  # Высота
        self.color = color  # Цвет (если нет изображения)
        self.layer = layer  # Слой отрисовки (0 - задний фон, 1 - средний, 2 - передний)
        self.angle = 0  # Угол поворота в градусах
        self.flip_x = False  # Отразить по горизонтали
        self.flip_y = False  # Отразить по вертикали
        self.color_overlay = None  # Цвет для наложения на изображение (None - без наложения)
        self.opacity = 255  # Прозрачность (0-255)

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
        self.is_boss = False  # Flag to identify if this enemy is a boss
        self.shoot_cooldown = 0  # Cooldown for ranged attacks (shooting)

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
        self.spread = 0.1  # Разброс пуль в радианах (0 - без разброса)

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

class Portal:
    """Компонент для порталов, телепортирующих игрока на другие уровни"""
    def __init__(self, destination="next_level", active=True):
        self.destination = destination  # Название уровня назначения
        self.active = active  # Активен ли портал
        self.animation_timer = 0  # Таймер для анимации

class DirectionIndicator:
    """Компонент для указателя направления к определенной цели"""
    def __init__(self, target_type="exit"):
        self.target_type = target_type  # Тип цели ("exit", "entrance" и т.д.)
        self.is_visible = True  # Виден ли указатель
        self.distance = 0  # Расстояние до цели
        self.angle = 0  # Угол направления к цели

class Minimap:
    """Компонент для отображения мини-карты"""
    def __init__(self, surface=None):
        self.surface = surface  # Поверхность с отрисованной мини-картой
        self.position = (20, 20)  # Позиция мини-карты на экране (верхний левый угол)
        self.visible = True  # Видимость мини-карты

class GameProgress:
    """Компонент для отслеживания прогресса игрока в рогалике"""
    def __init__(self):
        self.level = 1  # Текущий уровень глубины
        self.enemies_killed = 0  # Количество убитых врагов
        self.total_score = 0  # Общий счет
        self.time_played = 0  # Время игры в секундах
        self.levels_completed = 0  # Количество пройденных уровней
        
        # Параметры для масштабирования сложности
        self.enemy_health_multiplier = 1.0  # Множитель здоровья врагов
        self.enemy_damage_multiplier = 1.0  # Множитель урона врагов
        self.enemy_count_multiplier = 1.0  # Множитель количества врагов
        
        # Бонусы игрока
        self.player_damage_bonus = 0  # Дополнительный урон игрока
        self.player_speed_bonus = 0  # Дополнительная скорость игрока
        self.player_health_bonus = 0  # Дополнительное здоровье игрока
        
    def increase_level(self):
        """Увеличивает уровень и обновляет множители сложности"""
        self.level += 1
        self.levels_completed += 1
        
        # Увеличиваем множители сложности с каждым уровнем
        self.enemy_health_multiplier += 0.1
        self.enemy_damage_multiplier += 0.05
        self.enemy_count_multiplier += 0.2
        
        # Ограничиваем максимальные множители
        self.enemy_health_multiplier = min(self.enemy_health_multiplier, 3.0)
        self.enemy_damage_multiplier = min(self.enemy_damage_multiplier, 2.0)
        self.enemy_count_multiplier = min(self.enemy_count_multiplier, 5.0)
        
    def add_score(self, points):
        """Добавляет очки к общему счету"""
        self.total_score += points
        
    def enemy_killed(self):
        """Увеличивает счетчик убитых врагов"""
        self.enemies_killed += 1
        self.add_score(10)  # За каждого врага даем 10 очков