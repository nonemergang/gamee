import math
import pygame
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Enemy, Player, Health, Weapon

class EnemyAISystem(System):
    """Система для управления искусственным интеллектом врагов"""
    
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
            return  # Если игрока нет, ничего не делаем
        
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Обновляем поведение каждого врага
        for enemy_id in enemy_entities:
            enemy = self.world.get_component(enemy_id, Enemy)
            enemy_pos = self.world.get_component(enemy_id, Position)
            enemy_vel = self.world.get_component(enemy_id, Velocity)
            
            # Вычисляем направление к игроку
            dx = player_pos.x - enemy_pos.x
            dy = player_pos.y - enemy_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Обновляем состояние врага
            if distance < enemy.detection_radius:
                # Если игрок в зоне обнаружения, преследуем его
                if distance > 0:
                    # Нормализуем вектор направления
                    dx /= distance
                    dy /= distance
                    
                    # Устанавливаем скорость врага
                    enemy_vel.dx = dx * enemy.speed
                    enemy_vel.dy = dy * enemy.speed
                
                # Если враг достаточно близко к игроку, атакуем
                if distance < enemy.attack_radius and enemy.attack_cooldown <= 0:
                    self._attack_player(enemy_id, player_id)
                    enemy.attack_cooldown = enemy.attack_rate
                
                # Обновляем таймер атаки
                if enemy.attack_cooldown > 0:
                    enemy.attack_cooldown -= dt
            else:
                # Если игрок вне зоны обнаружения, патрулируем или стоим на месте
                enemy_vel.dx = 0
                enemy_vel.dy = 0
    
    def _attack_player(self, enemy_id, player_id):
        """
        Атакует игрока
        :param enemy_id: ID врага
        :param player_id: ID игрока
        """
        # Проверяем, есть ли у игрока компонент здоровья
        if not self.world.has_component(player_id, Health):
            return
        
        # Получаем компоненты
        enemy = self.world.get_component(enemy_id, Enemy)
        player_health = self.world.get_component(player_id, Health)
        
        # Наносим урон игроку
        player_health.current -= enemy.damage
        
        # Если здоровье игрока опустилось до 0 или ниже, игрок умирает
        if player_health.current <= 0:
            self.world.delete_entity(player_id)
    
    def _find_path(self, start_x, start_y, target_x, target_y):
        """
        Находит путь от начальной точки к целевой
        :param start_x: Начальная координата X
        :param start_y: Начальная координата Y
        :param target_x: Целевая координата X
        :param target_y: Целевая координата Y
        :return: Список точек пути
        """
        # Для простоты используем прямую линию
        # В более сложной реализации здесь можно использовать A* или другой алгоритм поиска пути
        return [(target_x, target_y)] 