from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Collider, Tile

class MovementSystem(System):
    """Система для обработки движения сущностей"""
    
    def update(self, dt):
        """
        Обновляет позиции всех сущностей с компонентами Position и Velocity
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с компонентами Position и Velocity
        entities = self.world.get_entities_with_components(Position, Velocity)
        
        # Получаем все сущности с коллайдерами (стены)
        collision_entities = self.world.get_entities_with_components(Position, Collider)
        
        # Получаем все тайлы для проверки границ лабиринта
        tile_entities = self.world.get_entities_with_components(Position, Tile)
        
        # Находим границы лабиринта
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for entity_id in tile_entities:
            pos = self.world.get_component(entity_id, Position)
            min_x = min(min_x, pos.x - 16)  # 16 - половина размера тайла
            min_y = min(min_y, pos.y - 16)
            max_x = max(max_x, pos.x + 16)
            max_y = max(max_y, pos.y + 16)
        
        for entity_id in entities:
            position = self.world.get_component(entity_id, Position)
            velocity = self.world.get_component(entity_id, Velocity)
            
            # Сохраняем текущую позицию для возможного отката
            old_x, old_y = position.x, position.y
            
            # Обновляем позицию на основе скорости и времени
            new_x = position.x + velocity.dx * dt
            new_y = position.y + velocity.dy * dt
            
            # Проверяем коллизии, если у сущности есть коллайдер
            if self.world.has_component(entity_id, Collider):
                collider = self.world.get_component(entity_id, Collider)
                
                # Проверяем коллизии по X и Y отдельно для более точного определения
                # Сначала перемещаем по X
                position.x = new_x
                if self._check_collisions(entity_id, collision_entities):
                    position.x = old_x  # Возвращаем старую позицию по X
                
                # Затем перемещаем по Y
                position.y = new_y
                if self._check_collisions(entity_id, collision_entities):
                    position.y = old_y  # Возвращаем старую позицию по Y
                
                # Проверяем границы лабиринта
                half_width = collider.width / 2
                half_height = collider.height / 2
                
                # Ограничиваем движение границами лабиринта
                position.x = max(min_x + half_width, min(position.x, max_x - half_width))
                position.y = max(min_y + half_height, min(position.y, max_y - half_height))
            else:
                # Если нет коллайдера, просто обновляем позицию
                position.x = new_x
                position.y = new_y
    
    def _check_collisions(self, entity_id, collision_entities):
        """
        Проверяет столкновения между сущностью и другими сущностями с коллайдерами
        :param entity_id: ID проверяемой сущности
        :param collision_entities: Список сущностей с коллайдерами
        :return: True, если есть столкновение, иначе False
        """
        # Получаем компоненты текущей сущности
        position = self.world.get_component(entity_id, Position)
        collider = self.world.get_component(entity_id, Collider)
        
        # Получаем границы текущей сущности
        entity_left = position.x - collider.width / 2
        entity_right = position.x + collider.width / 2
        entity_top = position.y - collider.height / 2
        entity_bottom = position.y + collider.height / 2
        
        for other_id in collision_entities:
            # Пропускаем саму сущность
            if other_id == entity_id:
                continue
            
            # Получаем компоненты другой сущности
            other_position = self.world.get_component(other_id, Position)
            other_collider = self.world.get_component(other_id, Collider)
            
            # Если коллайдер другой сущности - триггер, пропускаем
            if other_collider.is_trigger:
                continue
            
            # Получаем границы другой сущности
            other_left = other_position.x - other_collider.width / 2
            other_right = other_position.x + other_collider.width / 2
            other_top = other_position.y - other_collider.height / 2
            other_bottom = other_position.y + other_collider.height / 2
            
            # Проверяем пересечение (AABB коллизия)
            if (entity_left < other_right and entity_right > other_left and
                entity_top < other_bottom and entity_bottom > other_top):
                return True
        
        return False 