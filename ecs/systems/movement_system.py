from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Collider

class MovementSystem(System):
    """Система для обработки движения сущностей"""
    
    def update(self, dt):
        """
        Обновляет позиции всех сущностей с компонентами Position и Velocity
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с компонентами Position и Velocity
        entities = self.world.get_entities_with_components(Position, Velocity)
        
        for entity_id in entities:
            position = self.world.get_component(entity_id, Position)
            velocity = self.world.get_component(entity_id, Velocity)
            
            # Обновляем позицию на основе скорости и времени
            new_x = position.x + velocity.dx * dt
            new_y = position.y + velocity.dy * dt
            
            # Проверяем коллизии, если у сущности есть коллайдер
            if self.world.has_component(entity_id, Collider):
                collider = self.world.get_component(entity_id, Collider)
                
                # Если коллайдер не является триггером, проверяем столкновения
                if not collider.is_trigger:
                    # Проверяем столкновения с другими коллайдерами
                    collision_entities = self.world.get_entities_with_components(Position, Collider)
                    
                    # Проверяем столкновения по X
                    position.x = new_x
                    if self._check_collisions(entity_id, collision_entities):
                        position.x = position.x  # Возвращаем старую позицию
                    
                    # Проверяем столкновения по Y
                    position.y = new_y
                    if self._check_collisions(entity_id, collision_entities):
                        position.y = position.y  # Возвращаем старую позицию
                else:
                    # Если коллайдер - триггер, просто обновляем позицию
                    position.x = new_x
                    position.y = new_y
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
            
            # Проверяем пересечение
            if (entity_left < other_right and entity_right > other_left and
                entity_top < other_bottom and entity_bottom > other_top):
                return True
        
        return False 