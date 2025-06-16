import pygame
from ecs.systems.system import System
from ecs.components.components import Health, Player, Enemy

class HealthSystem(System):
    """Система для обработки здоровья сущностей"""
    
    def update(self, dt):
        """
        Обновляет состояние здоровья сущностей
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с компонентом здоровья
        health_entities = self.world.get_entities_with_components(Health)
        
        for entity_id in health_entities:
            health = self.world.get_component(entity_id, Health)
            
            # Проверяем, жива ли сущность
            if health.current <= 0:
                # Если это игрок, не удаляем его сразу, чтобы можно было показать экран смерти
                if self.world.has_component(entity_id, Player):
                    continue
                
                # Если это враг, удаляем его
                if self.world.has_component(entity_id, Enemy):
                    self.world.delete_entity(entity_id)
                    continue
            
            # Обрабатываем регенерацию здоровья, если она включена
            if health.regeneration_rate > 0 and health.current < health.maximum:
                # Увеличиваем таймер регенерации
                health.regeneration_timer += dt
                
                # Если прошло достаточно времени, восстанавливаем здоровье
                if health.regeneration_timer >= health.regeneration_interval:
                    health.current += health.regeneration_rate
                    health.regeneration_timer = 0
                    
                    # Убеждаемся, что здоровье не превышает максимум
                    if health.current > health.maximum:
                        health.current = health.maximum
    
    def apply_damage(self, entity_id, damage):
        """
        Применяет урон к сущности
        :param entity_id: ID сущности
        :param damage: Количество урона
        :return: True, если сущность умерла, иначе False
        """
        if not self.world.has_component(entity_id, Health):
            return False
        
        health = self.world.get_component(entity_id, Health)
        
        # Применяем урон
        health.current -= damage
        
        # Проверяем, умерла ли сущность
        if health.current <= 0:
            health.current = 0
            return True
        
        return False
    
    def heal(self, entity_id, amount):
        """
        Восстанавливает здоровье сущности
        :param entity_id: ID сущности
        :param amount: Количество восстанавливаемого здоровья
        """
        if not self.world.has_component(entity_id, Health):
            return
        
        health = self.world.get_component(entity_id, Health)
        
        # Восстанавливаем здоровье
        health.current += amount
        
        # Убеждаемся, что здоровье не превышает максимум
        if health.current > health.maximum:
            health.current = health.maximum 