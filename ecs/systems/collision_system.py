import pygame
from ecs.systems.system import System
from ecs.components.components import Position, Collider, Velocity, Bullet, Enemy, Player, Health

class CollisionSystem(System):
    """Система для обработки столкновений между сущностями"""
    
    def update(self, dt):
        """
        Обновляет состояние столкновений
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с коллайдерами
        collider_entities = self.world.get_entities_with_components(Position, Collider)
        
        # Получаем все пули
        bullet_entities = self.world.get_entities_with_components(Bullet, Position, Collider)
        
        # Проверяем столкновения пуль с врагами
        for bullet_id in bullet_entities:
            bullet = self.world.get_component(bullet_id, Bullet)
            bullet_pos = self.world.get_component(bullet_id, Position)
            bullet_collider = self.world.get_component(bullet_id, Collider)
            
            # Проверяем, что все компоненты существуют
            if not bullet or not bullet_pos or not bullet_collider:
                continue
            
            # Пропускаем столкновения с владельцем пули
            owner_id = bullet.owner_id
            
            # Проверяем столкновения с врагами
            enemy_entities = self.world.get_entities_with_components(Enemy, Position, Collider, Health)
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
                    
                    # Удаляем пулю
                    self.world.delete_entity(bullet_id)
                    break
        
        # Проверяем столкновения между всеми сущностями с коллайдерами
        for i in range(len(collider_entities)):
            entity1_id = collider_entities[i]
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