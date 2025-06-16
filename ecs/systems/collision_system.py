import pygame
import random
import math
from ecs.systems.system import System
from ecs.components.components import Position, Collider, Velocity, Bullet, Enemy, Player, Health, Tile, Sprite

class CollisionSystem(System):
    """Система для обработки столкновений между сущностями"""
    
    def __init__(self, world):
        super().__init__(world)
        self.hit_effects = []  # Список эффектов попадания
    
    def update(self, dt):
        """
        Обновляет состояние столкновений
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Обновляем эффекты попадания
        self._update_hit_effects(dt)
        
        # Получаем все сущности с коллайдерами
        collider_entities = self.world.get_entities_with_components(Position, Collider)
        
        # Получаем все пули
        bullet_entities = self.world.get_entities_with_components(Bullet, Position, Velocity)
        
        # Проверяем столкновения пуль с врагами и стенами
        for bullet_id in bullet_entities:
            # Если пуля уже удалена, пропускаем
            if not self.world.entity_exists(bullet_id):
                continue
                
            bullet = self.world.get_component(bullet_id, Bullet)
            bullet_pos = self.world.get_component(bullet_id, Position)
            bullet_vel = self.world.get_component(bullet_id, Velocity)
            
            # Если у пули есть коллайдер, используем его
            bullet_collider = None
            if self.world.has_component(bullet_id, Collider):
                bullet_collider = self.world.get_component(bullet_id, Collider)
            else:
                # Если у пули нет коллайдера, создаем временный с размером из компонента Bullet
                bullet_collider = Collider(width=bullet.radius * 2, height=bullet.radius * 2)
            
            # Проверяем, что все компоненты существуют
            if not bullet or not bullet_pos:
                continue
            
            # Пропускаем столкновения с владельцем пули
            owner_id = bullet.owner
            
            # Проверяем столкновения с врагами
            enemy_entities = self.world.get_entities_with_components(Enemy, Position, Collider, Health)
            bullet_hit = False
            
            for enemy_id in enemy_entities:
                # Пропускаем, если враг - владелец пули (хотя такого не должно быть)
                if enemy_id == owner_id:
                    continue
                
                enemy_pos = self.world.get_component(enemy_id, Position)
                enemy_collider = self.world.get_component(enemy_id, Collider)
                
                # Проверяем, что все компоненты существуют
                if not enemy_pos or not enemy_collider:
                    continue
                
                # Проверяем столкновение
                if self._check_collision(bullet_pos, bullet_collider, enemy_pos, enemy_collider):
                    # Наносим урон врагу
                    enemy_health = self.world.get_component(enemy_id, Health)
                    if enemy_health:
                        enemy_health.current -= bullet.damage
                        
                        # Если здоровье врага опустилось до 0 или ниже, удаляем его
                        if enemy_health.current <= 0:
                            self.world.delete_entity(enemy_id)
                    
                    # Создаем эффект попадания
                    self._create_hit_effect(bullet_pos.x, bullet_pos.y, (255, 0, 0))
                    
                    # Удаляем пулю
                    self.world.delete_entity(bullet_id)
                    bullet_hit = True
                    break
            
            # Если пуля уже попала во врага, переходим к следующей
            if bullet_hit:
                continue
            
            # Проверяем столкновения со стенами (тайлами, которые не проходимы)
            wall_entities = self.world.get_entities_with_components(Tile, Position, Collider)
            
            # Предварительная проверка - находится ли пуля в пределах карты
            # Если пуля вышла за пределы карты, удаляем её
            if bullet_pos.x < 0 or bullet_pos.x > 1000 or bullet_pos.y < 0 or bullet_pos.y > 1000:
                self.world.delete_entity(bullet_id)
                continue
                
            for wall_id in wall_entities:
                wall_tile = self.world.get_component(wall_id, Tile)
                
                # Пропускаем проходимые тайлы
                if wall_tile.walkable:
                    continue
                
                wall_pos = self.world.get_component(wall_id, Position)
                wall_collider = self.world.get_component(wall_id, Collider)
                
                # Сначала проверяем примерное расстояние для оптимизации
                dx = bullet_pos.x - wall_pos.x
                dy = bullet_pos.y - wall_pos.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Если расстояние меньше суммы радиусов, проверяем точное столкновение
                if distance < (bullet.radius + wall_collider.width / 2 + 10):  # Увеличиваем запас для надежности
                    if self._check_collision(bullet_pos, bullet_collider, wall_pos, wall_collider):
                        # Создаем эффект попадания
                        self._create_hit_effect(bullet_pos.x, bullet_pos.y, (150, 150, 0))
                        
                        # Удаляем пулю при столкновении со стеной
                        self.world.delete_entity(bullet_id)
                        break
        
        # Проверяем столкновения между всеми сущностями с коллайдерами
        for i in range(len(collider_entities)):
            entity1_id = collider_entities[i]
            
            # Пропускаем удаленные сущности
            if not self.world.entity_exists(entity1_id):
                continue
                
            entity1_pos = self.world.get_component(entity1_id, Position)
            entity1_collider = self.world.get_component(entity1_id, Collider)
            
            # Проверяем, что все компоненты существуют
            if not entity1_pos or not entity1_collider:
                continue
            
            # Если у сущности есть скорость, проверяем столкновения с другими сущностями
            if self.world.has_component(entity1_id, Velocity):
                entity1_vel = self.world.get_component(entity1_id, Velocity)
                
                # Проверяем, что компонент скорости существует
                if not entity1_vel:
                    continue
                
                for j in range(i + 1, len(collider_entities)):
                    entity2_id = collider_entities[j]
                    
                    # Пропускаем удаленные сущности
                    if not self.world.entity_exists(entity2_id):
                        continue
                        
                    entity2_pos = self.world.get_component(entity2_id, Position)
                    entity2_collider = self.world.get_component(entity2_id, Collider)
                    
                    # Проверяем, что все компоненты существуют
                    if not entity2_pos or not entity2_collider:
                        continue
                    
                    # Пропускаем триггеры (они не препятствуют движению)
                    if entity2_collider.is_trigger:
                        continue
                    
                    # Проверяем столкновение
                    if self._check_collision(entity1_pos, entity1_collider, entity2_pos, entity2_collider):
                        # Обрабатываем столкновение
                        self._handle_collision(entity1_id, entity1_pos, entity1_vel, entity1_collider,
                                              entity2_id, entity2_pos, entity2_collider)
    
    def _create_hit_effect(self, x, y, color):
        """
        Создает эффект попадания в указанной позиции
        :param x: Координата X
        :param y: Координата Y
        :param color: Цвет эффекта (r, g, b)
        """
        # Убедимся, что цвет имеет только RGB компоненты
        if len(color) > 3:
            color = color[:3]  # Берем только RGB компоненты
        
        print(f"Создаю эффект попадания в позиции ({x}, {y}) с цветом {color}")
        
        # Добавляем эффект в список с временем жизни
        self.hit_effects.append({
            'id': None,  # Не создаем сущность для эффекта
            'lifetime': 0.5,  # Время жизни эффекта в секундах
            'timer': 0,
            'particles': []
        })
        
        # Создаем частицы для эффекта
        num_particles = random.randint(25, 35)  # Увеличиваем количество частиц
        print(f"Создаю {num_particles} частиц для эффекта")
        
        for _ in range(num_particles):
            angle = random.uniform(0, 360)
            speed = random.uniform(80, 250)  # Увеличиваем скорость частиц
            size = random.uniform(1.5, 4)  # Уменьшенный размер частиц
            lifetime = random.uniform(0.3, 0.6)  # Время жизни частиц
            
            dx = math.cos(math.radians(angle)) * speed
            dy = math.sin(math.radians(angle)) * speed
            
            self.hit_effects[-1]['particles'].append({
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'size': size,
                'lifetime': lifetime,
                'timer': 0,
                'color': color
            })
    
    def _update_hit_effects(self, dt):
        """
        Обновляет эффекты попадания
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Обновляем таймеры эффектов
        for effect in self.hit_effects[:]:
            effect['timer'] += dt
            
            # Обновляем частицы
            for particle in effect['particles']:
                particle['timer'] += dt
                particle['x'] += particle['dx'] * dt
                particle['y'] += particle['dy'] * dt
                
                # Уменьшаем скорость частиц (трение)
                particle['dx'] *= 0.95
                particle['dy'] *= 0.95
            
            # Если время жизни эффекта истекло, удаляем его
            if effect['timer'] >= effect['lifetime']:
                # Удаляем сущность, если она существует
                if effect['id'] is not None and self.world.entity_exists(effect['id']):
                    self.world.delete_entity(effect['id'])
                self.hit_effects.remove(effect)
                print(f"Удален эффект попадания, осталось эффектов: {len(self.hit_effects)}")
        
        # Выводим количество активных эффектов каждые 60 кадров
        if hasattr(self, 'debug_counter'):
            self.debug_counter += 1
            if self.debug_counter >= 60:
                self.debug_counter = 0
                if self.hit_effects:
                    print(f"Активных эффектов: {len(self.hit_effects)}")
        else:
            self.debug_counter = 0
    
    def _check_collision(self, pos1, collider1, pos2, collider2):
        """
        Проверяет столкновение между двумя сущностями
        :param pos1: Компонент Position первой сущности
        :param collider1: Компонент Collider первой сущности
        :param pos2: Компонент Position второй сущности
        :param collider2: Компонент Collider второй сущности
        :return: True, если есть столкновение, иначе False
        """
        # Проверяем, что все компоненты существуют
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
    
    def _handle_collision(self, entity1_id, pos1, vel1, collider1, entity2_id, pos2, collider2):
        """
        Обрабатывает столкновение между двумя сущностями
        :param entity1_id: ID первой сущности
        :param pos1: Компонент Position первой сущности
        :param vel1: Компонент Velocity первой сущности
        :param collider1: Компонент Collider первой сущности
        :param entity2_id: ID второй сущности
        :param pos2: Компонент Position второй сущности
        :param collider2: Компонент Collider второй сущности
        """
        # Проверяем, что все компоненты существуют
        if not pos1 or not vel1 or not collider1 or not pos2 or not collider2:
            return
        
        # Определяем направление столкновения
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        
        # Вычисляем минимальное расстояние для разрешения столкновения
        min_dist_x = (collider1.width + collider2.width) / 2
        min_dist_y = (collider1.height + collider2.height) / 2
        
        # Определяем направление отталкивания
        push_x = 0
        push_y = 0
        
        # Определяем, с какой стороны произошло столкновение
        if abs(dx) < min_dist_x and abs(dy) < min_dist_y:
            # Вычисляем величину перекрытия по каждой оси
            overlap_x = min_dist_x - abs(dx)
            overlap_y = min_dist_y - abs(dy)
            
            # Выбираем ось с меньшим перекрытием для разрешения столкновения
            if overlap_x < overlap_y:
                # Столкновение по оси X
                push_x = overlap_x * (1 if dx < 0 else -1)
                vel1.dx = 0  # Останавливаем движение по оси X
            else:
                # Столкновение по оси Y
                push_y = overlap_y * (1 if dy < 0 else -1)
                vel1.dy = 0  # Останавливаем движение по оси Y
        
        # Применяем отталкивание
        pos1.x += push_x
        pos1.y += push_y 