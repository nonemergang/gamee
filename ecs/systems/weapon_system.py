import pygame
import math
import random
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Weapon, Bullet, Sprite, Collider, Tile, Health, Player, Enemy
from ecs.utils.sprite_manager import sprite_manager

def create_bullet_texture():
    """
    Возвращает текстуру пули из менеджера спрайтов или создает дефолтную
    """
    # Сначала пытаемся получить спрайт из менеджера
    bullet_sprite = sprite_manager.get_sprite("bullet")
    
    # Если спрайт не найден, создаем дефолтную текстуру
    if bullet_sprite is None:
        print("Спрайт пули не найден, создаем дефолтную текстуру")
        # Создаем поверхность для пули
        bullet_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
        
        # Рисуем пулю (простой круг)
        pygame.draw.circle(bullet_surface, (255, 255, 0), (4, 4), 4)  # Желтая пуля
        
        return bullet_surface
    else:
        print("Спрайт пули загружен успешно")
    
    return bullet_sprite

class WeaponSystem(System):
    """
    Система для обработки оружия и пуль
    """
    
    def __init__(self, world, screen):
        super().__init__(world)
        self.screen = screen
        self.bullet_color = (255, 255, 0)  # Желтый цвет для пуль
        self.bullet_hit_effects = []  # Эффекты попадания пуль
        self.effect_lifetime = 0.3  # Время жизни эффекта в секундах
        self.bullet_texture = create_bullet_texture()  # Загружаем текстуру пули
        print(f"Инициализация WeaponSystem: текстура пули {'загружена' if self.bullet_texture else 'не загружена'}")
    
    def update(self, dt):
        """
        Обновляет состояние оружия и пуль
        :param dt: Время, прошедшее с последнего обновления
        """
        # Обновляем оружие
        self._update_weapons(dt)
        
        # Обновляем пули
        self._update_bullets(dt)
        
        # Обновляем эффекты попадания пуль
        self._update_bullet_hit_effects(dt)
    
    def _update_weapons(self, dt):
        """
        Обновляет состояние оружия
        :param dt: Время, прошедшее с последнего обновления
        """
        # Получаем все сущности с компонентом оружия
        weapon_entities = self.world.get_entities_with_components(Weapon)
        
        for entity_id in weapon_entities:
            weapon = self.world.get_component(entity_id, Weapon)
            
            # Обновляем кулдаун оружия
            if weapon.cooldown > 0:
                weapon.cooldown -= dt
                if weapon.cooldown < 0:
                    weapon.cooldown = 0
            
            # Обрабатываем перезарядку
            if weapon.is_reloading:
                weapon.reload_timer += dt
                if weapon.reload_timer >= weapon.reload_time:
                    # Завершаем перезарядку
                    weapon.current_ammo = weapon.max_ammo
                    weapon.is_reloading = False
                    weapon.reload_timer = 0
    
    def _update_bullets(self, dt):
        """
        Обновляет состояние пуль
        :param dt: Время, прошедшее с последнего обновления
        """
        # Получаем все сущности с компонентами пули и позиции
        bullet_entities = self.world.get_entities_with_components(Bullet, Position, Velocity)
        
        for entity_id in bullet_entities:
            bullet = self.world.get_component(entity_id, Bullet)
            position = self.world.get_component(entity_id, Position)
            velocity = self.world.get_component(entity_id, Velocity)
            
            # Обновляем таймер жизни пули
            bullet.timer += dt
            if bullet.timer >= bullet.lifetime:
                # Удаляем пулю, если истекло время жизни
                self.world.delete_entity(entity_id)
                continue
            
            # Обновляем позицию пули
            position.x += velocity.dx * dt
            position.y += velocity.dy * dt
            
            # Проверяем столкновения пули
            self._check_bullet_collisions(entity_id, bullet, position)
    
    def _check_bullet_collisions(self, bullet_id, bullet, bullet_pos):
        """
        Проверяет столкновения пули с другими сущностями
        :param bullet_id: ID пули
        :param bullet: Компонент пули
        :param bullet_pos: Компонент позиции пули
        """
        # Проверяем столкновения с стенами
        wall_entities = self.world.get_entities_with_components(Tile, Position, Collider)
        for wall_id in wall_entities:
            tile = self.world.get_component(wall_id, Tile)
            if not tile.walkable:  # Проверяем только непроходимые тайлы (стены)
                wall_pos = self.world.get_component(wall_id, Position)
                wall_collider = self.world.get_component(wall_id, Collider)
                
                # Проверяем столкновение пули со стеной
                if self._check_collision(bullet_pos.x, bullet_pos.y, bullet.radius,
                                        wall_pos.x, wall_pos.y, wall_collider.width, wall_collider.height):
                    # Создаем эффект попадания в стену
                    self._create_bullet_hit_effect(bullet_pos.x, bullet_pos.y, (150, 150, 150))
                    
                    # Удаляем пулю
                    self.world.delete_entity(bullet_id)
                    return
        
        # Проверяем столкновения с врагами
        enemy_entities = self.world.get_entities_with_components(Enemy, Position, Collider)
        for enemy_id in enemy_entities:
            # Пропускаем, если пуля принадлежит этому врагу
            if bullet.owner == enemy_id:
                continue
                
            enemy_pos = self.world.get_component(enemy_id, Position)
            enemy_collider = self.world.get_component(enemy_id, Collider)
            
            # Проверяем столкновение пули с врагом
            if self._check_collision(bullet_pos.x, bullet_pos.y, bullet.radius,
                                    enemy_pos.x, enemy_pos.y, enemy_collider.width, enemy_collider.height):
                # Наносим урон врагу
                if self.world.has_component(enemy_id, Health):
                    # Получаем систему здоровья
                    health_system = next((system for system in self.world.systems if hasattr(system, 'damage_entity')), None)
                    if health_system:
                        # Наносим урон
                        damage_dealt = health_system.damage_entity(enemy_id, bullet.damage, bullet.owner)
                        
                        # Создаем эффект попадания
                        if damage_dealt > 0:
                            self._create_bullet_hit_effect(bullet_pos.x, bullet_pos.y, (255, 0, 0))
                
                # Удаляем пулю
                self.world.delete_entity(bullet_id)
                return
        
        # Проверяем столкновения с игроком
        player_entities = self.world.get_entities_with_components(Player, Position, Collider)
        for player_id in player_entities:
            # Пропускаем, если пуля принадлежит игроку
            if bullet.owner == player_id:
                continue
                
            player_pos = self.world.get_component(player_id, Position)
            player_collider = self.world.get_component(player_id, Collider)
            
            # Проверяем столкновение пули с игроком
            if self._check_collision(bullet_pos.x, bullet_pos.y, bullet.radius,
                                    player_pos.x, player_pos.y, player_collider.width, player_collider.height):
                # Наносим урон игроку
                if self.world.has_component(player_id, Health):
                    # Получаем систему здоровья
                    health_system = next((system for system in self.world.systems if hasattr(system, 'damage_entity')), None)
                    if health_system:
                        # Наносим урон
                        damage_dealt = health_system.damage_entity(player_id, bullet.damage, bullet.owner)
                        
                        # Создаем эффект попадания
                        if damage_dealt > 0:
                            self._create_bullet_hit_effect(bullet_pos.x, bullet_pos.y, (0, 0, 255))
                
                # Удаляем пулю
                self.world.delete_entity(bullet_id)
                return
    
    def _check_collision(self, x1, y1, radius, x2, y2, width, height):
        """
        Проверяет столкновение круга (пули) с прямоугольником (коллайдером)
        :param x1: X координата центра круга
        :param y1: Y координата центра круга
        :param radius: Радиус круга
        :param x2: X координата центра прямоугольника
        :param y2: Y координата центра прямоугольника
        :param width: Ширина прямоугольника
        :param height: Высота прямоугольника
        :return: True, если есть столкновение, иначе False
        """
        # Находим ближайшую точку прямоугольника к центру круга
        closest_x = max(x2 - width/2, min(x1, x2 + width/2))
        closest_y = max(y2 - height/2, min(y1, y2 + height/2))
        
        # Вычисляем расстояние от центра круга до ближайшей точки прямоугольника
        distance_x = x1 - closest_x
        distance_y = y1 - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y
        
        # Если расстояние меньше радиуса, есть столкновение
        return distance_squared < (radius * radius)
    
    def fire_bullet(self, entity_id, target_x, target_y):
        """
        Стреляет пулей из оружия сущности в указанном направлении
        :param entity_id: ID сущности, которая стреляет
        :param target_x: X координата цели
        :param target_y: Y координата цели
        :return: True, если выстрел произведен, иначе False
        """
        # Проверяем, есть ли у сущности оружие
        if not self.world.has_component(entity_id, Weapon):
            return False
            
        weapon = self.world.get_component(entity_id, Weapon)
        
        # Проверяем, готово ли оружие к стрельбе
        if weapon.cooldown > 0:
            return False
            
        # Проверяем, есть ли патроны
        if weapon.current_ammo <= 0:
            # Автоматически начинаем перезарядку
            if not weapon.is_reloading:
                weapon.is_reloading = True
                weapon.reload_timer = 0
            return False
            
        # Проверяем, есть ли у сущности позиция
        if not self.world.has_component(entity_id, Position):
            return False
            
        position = self.world.get_component(entity_id, Position)
        
        # Вычисляем направление выстрела
        dx = target_x - position.x
        dy = target_y - position.y
        length = math.sqrt(dx * dx + dy * dy)
        
        if length > 0:
            dx /= length
            dy /= length
        
        # Создаем небольшое отклонение для выстрела (разброс)
        spread = weapon.spread
        if spread > 0:
            angle = math.atan2(dy, dx)
            angle += random.uniform(-spread, spread)
            dx = math.cos(angle)
            dy = math.sin(angle)
        
        # Создаем пулю
        bullet_id = self.world.create_entity()
        
        # Добавляем компоненты пули
        bullet_speed = weapon.bullet_speed
        self.world.add_component(bullet_id, Bullet(
            owner=entity_id,
            damage=weapon.damage,
            radius=4,
            lifetime=2.0
        ))
        
        # Добавляем позицию (немного смещенную от стрелка в направлении выстрела)
        offset = 20  # Смещение от стрелка
        bullet_x = position.x + dx * offset
        bullet_y = position.y + dy * offset
        self.world.add_component(bullet_id, Position(bullet_x, bullet_y))
        
        # Добавляем скорость
        self.world.add_component(bullet_id, Velocity(dx * bullet_speed, dy * bullet_speed))
        
        # Проверяем наличие текстуры пули и при необходимости пересоздаем
        if self.bullet_texture is None:
            self.bullet_texture = create_bullet_texture()
        
        # Добавляем спрайт для пули
        bullet_sprite = Sprite(
            image=self.bullet_texture,
            width=8,
            height=8,
            layer=5  # Более высокий слой для пуль, чтобы они отображались поверх других объектов
        )
        self.world.add_component(bullet_id, bullet_sprite)
        
        # Обновляем состояние оружия
        weapon.cooldown = 1.0 / weapon.fire_rate
        weapon.current_ammo -= 1
        
        return True
    
    def reload(self, entity_id):
        """
        Перезаряжает оружие сущности
        :param entity_id: ID сущности
        :return: True, если перезарядка начата, иначе False
        """
        # Проверяем, есть ли у сущности оружие
        if not self.world.has_component(entity_id, Weapon):
            return False
            
        weapon = self.world.get_component(entity_id, Weapon)
        
        # Проверяем, нужна ли перезарядка
        if weapon.current_ammo >= weapon.max_ammo or weapon.is_reloading:
            return False
            
        # Начинаем перезарядку
        weapon.is_reloading = True
        weapon.reload_timer = 0
        
        return True
    
    def _create_bullet_hit_effect(self, x, y, color):
        """
        Создает эффект попадания пули
        :param x: X координата эффекта
        :param y: Y координата эффекта
        :param color: Цвет эффекта
        """
        # Добавляем эффект в список
        print(f"Создаю эффект попадания в позиции ({x}, {y}) с цветом {color}")
        num_particles = random.randint(25, 35)
        print(f"Создаю {num_particles} частиц для эффекта")
        
        self.bullet_hit_effects.append({
            'x': x,
            'y': y,
            'color': color,
            'size': 10,
            'max_size': 20,
            'lifetime': self.effect_lifetime,
            'timer': 0
        })
    
    def _update_bullet_hit_effects(self, dt):
        """
        Обновляет эффекты попадания пуль
        :param dt: Время, прошедшее с последнего обновления
        """
        # Обновляем все эффекты
        for effect in self.bullet_hit_effects[:]:
            # Увеличиваем таймер
            effect['timer'] += dt
            
            # Если время жизни истекло, удаляем эффект
            if effect['timer'] >= effect['lifetime']:
                self.bullet_hit_effects.remove(effect)
                print(f"Удален эффект попадания, осталось эффектов: {len(self.bullet_hit_effects)}")
                continue
            
            # Обновляем размер эффекта
            progress = effect['timer'] / effect['lifetime']
            effect['size'] = effect['max_size'] * (1 - progress)
    
    def render(self, camera):
        """
        Отрисовывает пули и эффекты попадания
        :param camera: Камера для преобразования координат
        """
        # Отрисовка пуль не требуется, так как они имеют компонент Sprite и отрисовываются RenderSystem
        
        # Отрисовываем эффекты попадания
        for effect in self.bullet_hit_effects:
            # Преобразуем координаты с учетом камеры
            screen_x, screen_y = camera.world_to_screen(effect["x"], effect["y"])
            
            # Рисуем эффект попадания (круг)
            pygame.draw.circle(self.screen, effect["color"], (int(screen_x), int(screen_y)), int(effect["size"]))
            
            # Для более заметного эффекта, рисуем внутренний круг
            inner_size = max(2, int(effect["size"] // 2))
            pygame.draw.circle(self.screen, (255, 255, 255), (int(screen_x), int(screen_y)), inner_size) 