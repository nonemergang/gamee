import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Player, Portal, Tile, GameProgress
from ecs.factories.level_factory import create_level
from ecs.factories.enemy_factory import create_enemy

class PortalSystem(System):
    """
    Система для обработки порталов, телепортирующих игрока между уровнями
    """
    
    def __init__(self, world):
        super().__init__(world)
        self.current_level = 1  # Текущий номер уровня
        self.level_entities = {}  # Сущности по уровням
        self.activation_radius = 32  # Радиус активации портала (уменьшен для более точной активации)
        self.teleporting = False  # Флаг телепортации
        self.teleport_timer = 0  # Таймер для анимации телепортации
        self.teleport_cooldown = 0  # Кулдаун между телепортациями
        self.teleport_destination = None  # Назначение текущей телепортации
        self.teleport_player_id = None  # ID игрока, который телепортируется
        self.debug = True  # Флаг для отладочного вывода
        
        # Инициализируем компонент прогресса игры
        self.game_progress = GameProgress()
        
        # Отладочный вывод при инициализации только если включен режим отладки
        if self.debug:
            print("Система порталов инициализирована")
    
    def update(self, dt):
        """
        Обновляет состояние порталов
        :param dt: Время, прошедшее с последнего обновления
        """
        # Обновляем время игры
        if hasattr(self, 'game_progress'):
            self.game_progress.time_played += dt
            
        # Обновляем кулдаун телепортации
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt
            
        # Если происходит телепортация, обрабатываем её
        if self.teleporting:
            self.teleport_timer += dt
            if self.teleport_timer >= 1.0:  # Завершаем телепортацию через секунду
                # Выполняем телепортацию
                self.complete_teleport()
                
                # Сбрасываем флаги телепортации
                self.teleporting = False
                self.teleport_timer = 0
                self.teleport_destination = None
                self.teleport_player_id = None
                
                # Устанавливаем кулдаун телепортации
                self.teleport_cooldown = 2.0  # 2 секунды кулдауна
            return
        
        # Если активен кулдаун, пропускаем проверку порталов
        if self.teleport_cooldown > 0:
            return
            
        # Находим игрока
        player_entities = self.world.get_entities_with_components(Player, Position)
        if not player_entities:
            if self.debug:
                print("PortalSystem: Игрок не найден!")
            return
        
        player_id = player_entities[0]
        player_pos = self.world.get_component(player_id, Position)
        
        # Находим все порталы
        portal_entities = self.world.get_entities_with_components(Portal, Position)
        
        # Отладочный вывод количества найденных порталов только если включен режим отладки
        if self.debug:
            if len(portal_entities) == 0:
                print("PortalSystem: Порталы не найдены в мире!")
            else:
                print(f"PortalSystem: Найдено порталов: {len(portal_entities)}")
        
        # Находим все тайлы выхода (exit)
        exit_tiles = []
        tile_entities = self.world.get_entities_with_components(Tile, Position)
        for entity_id in tile_entities:
            tile = self.world.get_component(entity_id, Tile)
            if tile.name == "exit":
                exit_pos = self.world.get_component(entity_id, Position)
                exit_tiles.append((entity_id, exit_pos))
                
        # Если нашли тайлы выхода, проверяем находится ли игрок на них
        for exit_id, exit_pos in exit_tiles:
            # Рассчитываем расстояние от игрока до выхода
            dx = exit_pos.x - player_pos.x
            dy = exit_pos.y - player_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Отладочный вывод расстояния до выхода
            if self.debug:
                print(f"Расстояние до выхода: {distance:.1f}, радиус активации: {self.activation_radius}")
            
            # Если игрок внутри радиуса активации выхода
            if distance <= self.activation_radius:
                # Отладочный вывод при активации выхода
                print(f"Активация выхода на следующий уровень!")
                
                # Начинаем телепортацию на следующий уровень
                self.start_teleport(player_id, "next_level")
                return
            
        # Проверяем, находится ли игрок рядом с порталом
        for portal_id in portal_entities:
            portal = self.world.get_component(portal_id, Portal)
            
            # Пропускаем неактивные порталы
            if not portal.active:
                continue
                
            portal_pos = self.world.get_component(portal_id, Position)
            
            # Рассчитываем расстояние от игрока до портала
            dx = portal_pos.x - player_pos.x
            dy = portal_pos.y - player_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Отладочный вывод расстояния до портала только если включен режим отладки
            if self.debug:
                print(f"Расстояние до портала: {distance:.1f}, радиус активации: {self.activation_radius}")
            
            # Если игрок внутри радиуса активации портала
            if distance <= self.activation_radius:
                # Отладочный вывод при активации портала
                print(f"Активация портала! Назначение: {portal.destination}")
                
                # Начинаем телепортацию
                self.start_teleport(player_id, "next_level")  # Всегда телепортируем на следующий уровень
                break
    
    def start_teleport(self, player_id, destination):
        """
        Начинает процесс телепортации игрока
        :param player_id: ID игрока
        :param destination: Название уровня назначения
        """
        # Отладочный вывод начала телепортации
        print(f"Начинаем телепортацию игрока {player_id} в {destination}")
        
        # Сохраняем информацию о телепортации
        self.teleporting = True
        self.teleport_timer = 0
        self.teleport_destination = destination
        self.teleport_player_id = player_id
        
    def complete_teleport(self):
        """
        Завершает процесс телепортации игрока
        """
        if not self.teleport_player_id or not self.teleport_destination:
            print("Ошибка: нет информации о телепортации")
            return
            
        player_id = self.teleport_player_id
        
        # Проверяем существование игрока
        if not self.world.entity_exists(player_id):
            print(f"Ошибка: игрок с ID {player_id} не существует")
            return
            
        # Увеличиваем уровень в прогрессе
        if hasattr(self, 'game_progress'):
            self.game_progress.increase_level()
            self.current_level = self.game_progress.level
            print(f"Переход на уровень {self.current_level}")
        
        # Удаляем все сущности текущего уровня
        self.clear_current_level()
        
        # Создаем новый уровень с увеличенным размером
        base_size = 30
        level_width = base_size + (self.current_level * 3)  # Увеличиваем размер с каждым уровнем
        level_height = base_size + (self.current_level * 3)
        
        print(f"Создание нового уровня размером {level_width}x{level_height}")
        
        # Создаем новый уровень
        level_entities = create_level(world=self.world, width=level_width, height=level_height)
        
        # Находим вход в новый уровень для размещения игрока
        entrance_pos = self.find_entrance_position(level_entities)
        
        # Если нашли вход, телепортируем игрока туда
        if entrance_pos:
            player_pos = self.world.get_component(player_id, Position)
            player_pos.x = entrance_pos.x
            player_pos.y = entrance_pos.y
            print(f"Игрок {player_id} телепортирован на новый уровень ({entrance_pos.x}, {entrance_pos.y})")
        
        # Создаем врагов на новом уровне
        self.spawn_enemies_on_level(level_entities, player_id)
        
        # Обновляем текущий уровень
        self.level_entities[self.current_level] = level_entities
        
        print(f"Создан новый уровень {self.current_level} с {len(level_entities)} сущностями")
    
    def clear_current_level(self):
        """
        Удаляет все сущности текущего уровня
        """
        # Находим игрока, чтобы не удалить его
        player_entities = self.world.get_entities_with_components(Player)
        player_id = player_entities[0] if player_entities else None
        
        # Удаляем все сущности, кроме игрока
        for entity_id in list(self.world.entities.keys()):
            if entity_id != player_id:
                self.world.delete_entity(entity_id)
    
    def find_entrance_position(self, level_entities):
        """
        Находит позицию входа на уровень
        :param level_entities: Список ID сущностей уровня
        :return: Компонент Position входа или None
        """
        # Ищем тайл входа
        for entity_id in level_entities:
            if self.world.has_component(entity_id, Tile):
                tile = self.world.get_component(entity_id, Tile)
                if tile.name == "entrance" and self.world.has_component(entity_id, Position):
                    return self.world.get_component(entity_id, Position)
        
        # Если не нашли вход, ищем любой проходимый тайл
        for entity_id in level_entities:
            if self.world.has_component(entity_id, Tile):
                tile = self.world.get_component(entity_id, Tile)
                if tile.walkable and self.world.has_component(entity_id, Position):
                    return self.world.get_component(entity_id, Position)
        
        return None
    
    def spawn_enemies_on_level(self, level_entities, player_id):
        """
        Создает врагов на уровне
        :param level_entities: Список ID сущностей уровня
        :param player_id: ID игрока
        """
        # Рассчитываем количество врагов в зависимости от уровня
        base_enemy_count = 3
        if hasattr(self, 'game_progress'):
            enemy_count = int(base_enemy_count + (self.current_level * 1.5))  # Больше врагов с каждым уровнем
        else:
            enemy_count = base_enemy_count + self.current_level
        
        # Собираем все проходимые тайлы
        floor_tiles = []
        for entity_id in level_entities:
            if self.world.has_component(entity_id, Tile):
                tile = self.world.get_component(entity_id, Tile)
                if tile.walkable and tile.name == "floor":
                    pos = self.world.get_component(entity_id, Position)
                    floor_tiles.append((pos.x, pos.y))
        
        # Если нашли проходимые тайлы, создаем врагов
        if floor_tiles:
            player_pos = self.world.get_component(player_id, Position)
            
            for _ in range(enemy_count):
                # Выбираем случайную позицию
                import random
                x, y = random.choice(floor_tiles)
                
                # Проверяем, что позиция достаточно далеко от игрока
                distance = ((x - player_pos.x) ** 2 + (y - player_pos.y) ** 2) ** 0.5
                
                # Если позиция слишком близко к игроку, пробуем другую
                attempts = 0
                while distance < 200 and attempts < 10:
                    x, y = random.choice(floor_tiles)
                    distance = ((x - player_pos.x) ** 2 + (y - player_pos.y) ** 2) ** 0.5
                    attempts += 1
                
                # Создаем врага с увеличенными характеристиками в зависимости от уровня
                if hasattr(self, 'game_progress'):
                    health_mult = 1.0 + (self.current_level * 0.1)  # Увеличиваем здоровье на 10% с каждым уровнем
                    damage_mult = 1.0 + (self.current_level * 0.1)  # Увеличиваем урон на 10% с каждым уровнем
                    create_enemy(self.world, x, y, health_multiplier=health_mult, damage_multiplier=damage_mult)
                else:
                    create_enemy(self.world, x, y)
            
            print(f"Создано {enemy_count} врагов на уровне {self.current_level}")
    
    def add_level_entities(self, level_name, entities):
        """
        Добавляет сущности для определенного уровня
        :param level_name: Название уровня
        :param entities: Список ID сущностей
        """
        self.level_entities[level_name] = entities
        
    def get_game_progress(self):
        """
        Возвращает компонент прогресса игры
        :return: Компонент GameProgress
        """
        return self.game_progress 