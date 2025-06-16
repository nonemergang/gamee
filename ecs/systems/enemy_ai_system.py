import math
import pygame
import random
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Enemy, Player, Health, Weapon, PathDebug
from ecs.pathfinding.dijkstra import DijkstraPathfinder

class EnemyAISystem(System):
    """Система для управления искусственным интеллектом врагов"""
    
    def __init__(self, world):
        super().__init__(world)
        self.pathfinder = None
        self.level_map = None
        self.map_width = 0
        self.map_height = 0
        self.path_update_timer = 0
        self.path_update_interval = 0.5  # Обновляем путь каждые 0.5 секунды
        self.enemy_paths = {}  # Словарь для хранения путей врагов
        self.debug_mode = False  # Отключаем режим отладки для отображения путей
    
    def set_level_map(self, level_map, width, height):
        """
        Устанавливает карту уровня для поиска пути
        :param level_map: Карта уровня
        :param width: Ширина карты
        :param height: Высота карты
        """
        self.level_map = level_map
        self.map_width = width
        self.map_height = height
        self.pathfinder = DijkstraPathfinder(level_map, width, height)
    
    def update(self, dt):
        """
        Обновляет поведение врагов
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Если карта не установлена, ничего не делаем
        if not self.pathfinder:
            return
        
        # Обновляем таймер для пересчета путей
        self.path_update_timer += dt
        should_update_paths = self.path_update_timer >= self.path_update_interval
        
        # Получаем всех врагов
        enemy_entities = self.world.get_entities_with_components(Enemy, Position, Velocity)
        
        # Получаем игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        
        if not player_entities:
            return  # Если игрока нет, ничего не делаем
        
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Если нужно обновить пути
        if should_update_paths:
            self.path_update_timer = 0
            # Очищаем старые пути
            self.enemy_paths.clear()
        
        # Обновляем поведение каждого врага
        for enemy_id in enemy_entities:
            enemy = self.world.get_component(enemy_id, Enemy)
            enemy_pos = self.world.get_component(enemy_id, Position)
            enemy_vel = self.world.get_component(enemy_id, Velocity)
            
            # Вычисляем расстояние до игрока (по прямой)
            dx = player_pos.x - enemy_pos.x
            dy = player_pos.y - enemy_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Обновляем состояние врага
            if distance < enemy.detection_radius:
                # Если игрок в зоне обнаружения, используем поиск пути
                
                # Если нужно обновить путь или у этого врага еще нет пути
                if should_update_paths or enemy_id not in self.enemy_paths:
                    # Находим путь к игроку
                    path = self._find_path(enemy_pos.x, enemy_pos.y, player_pos.x, player_pos.y)
                    self.enemy_paths[enemy_id] = path
                    
                    # Обновляем или добавляем компонент PathDebug для отображения пути
                    if self.debug_mode:
                        if self.world.has_component(enemy_id, PathDebug):
                            path_debug = self.world.get_component(enemy_id, PathDebug)
                            path_debug.path = path
                        else:
                            self.world.add_component(enemy_id, PathDebug(path))
                
                # Если у врага есть путь
                if enemy_id in self.enemy_paths and self.enemy_paths[enemy_id]:
                    path = self.enemy_paths[enemy_id]
                    
                    # Берем следующую точку пути
                    next_point = path[0]
                    
                    # Вычисляем направление к следующей точке
                    dx = next_point[0] - enemy_pos.x
                    dy = next_point[1] - enemy_pos.y
                    point_distance = math.sqrt(dx * dx + dy * dy)
                    
                    # Если достигли точки, удаляем её из пути
                    if point_distance < 5:
                        if len(path) > 1:
                            self.enemy_paths[enemy_id] = path[1:]
                            # Обновляем компонент PathDebug
                            if self.debug_mode and self.world.has_component(enemy_id, PathDebug):
                                path_debug = self.world.get_component(enemy_id, PathDebug)
                                path_debug.path = path[1:]
                        else:
                            self.enemy_paths[enemy_id] = []
                            # Очищаем путь в компоненте PathDebug
                            if self.debug_mode and self.world.has_component(enemy_id, PathDebug):
                                path_debug = self.world.get_component(enemy_id, PathDebug)
                                path_debug.path = []
                    
                    # Нормализуем вектор направления
                    if point_distance > 0:
                        dx /= point_distance
                        dy /= point_distance
                    
                    # Устанавливаем скорость врага
                    enemy_vel.dx = dx * enemy.speed
                    enemy_vel.dy = dy * enemy.speed
                else:
                    # Если пути нет, двигаемся напрямую к игроку
                    if distance > 0:
                        dx = (player_pos.x - enemy_pos.x) / distance
                        dy = (player_pos.y - enemy_pos.y) / distance
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
                # Для простоты просто останавливаемся
                enemy_vel.dx = 0
                enemy_vel.dy = 0
                
                # Очищаем путь
                if enemy_id in self.enemy_paths:
                    self.enemy_paths[enemy_id] = []
                
                # Очищаем компонент PathDebug
                if self.debug_mode and self.world.has_component(enemy_id, PathDebug):
                    path_debug = self.world.get_component(enemy_id, PathDebug)
                    path_debug.path = []
    
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
        Находит путь от начальной точки к целевой используя алгоритм Дейкстры
        :param start_x: Начальная координата X
        :param start_y: Начальная координата Y
        :param target_x: Целевая координата X
        :param target_y: Целевая координата Y
        :return: Список точек пути
        """
        if self.pathfinder:
            return self.pathfinder.find_path(start_x, start_y, target_x, target_y)
        return [(target_x, target_y)]  # Если pathfinder не инициализирован, возвращаем прямой путь 