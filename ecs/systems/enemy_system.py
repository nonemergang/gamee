import math
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Enemy, Player

class EnemySystem(System):
    """Система для управления поведением врагов"""
    
    def update(self, dt):
        """
        Обновляет поведение врагов
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем всех врагов
        enemy_entities = self.world.get_entities_with_components(Enemy, Position, Velocity)
        
        # Получаем игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        
        if not player_entities:
            return
        
        # Берем первого игрока
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Обновляем каждого врага
        for enemy_id in enemy_entities:
            enemy = self.world.get_component(enemy_id, Enemy)
            enemy_pos = self.world.get_component(enemy_id, Position)
            enemy_vel = self.world.get_component(enemy_id, Velocity)
            
            # Вычисляем расстояние до игрока
            dx = player_pos.x - enemy_pos.x
            dy = player_pos.y - enemy_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Если враг видит игрока, преследуем его
            if distance <= enemy.detection_radius:
                # Нормализуем направление
                if distance > 0:
                    dx = dx / distance
                    dy = dy / distance
                
                # Устанавливаем скорость врага
                enemy_vel.dx = dx * enemy.speed
                enemy_vel.dy = dy * enemy.speed
            else:
                # Если игрок вне зоны видимости, останавливаемся
                enemy_vel.dx = 0
                enemy_vel.dy = 0
            
            # Обновляем таймер атаки
            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= dt 