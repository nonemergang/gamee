import pygame
from ecs.systems.system import System
from ecs.components.components import Health, Player, Enemy, Position

class HealthSystem(System):
    """
    Система для обработки здоровья сущностей
    """
    
    def __init__(self, world, screen):
        super().__init__(world)
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.damage_color = (255, 0, 0)  # Красный цвет для индикации урона
        self.heal_color = (0, 255, 0)    # Зеленый цвет для индикации лечения
        self.damage_indicators = []  # Список индикаторов урона/лечения
        self.indicator_lifetime = 1.0  # Время жизни индикатора в секундах
        
        # Получаем систему порталов для доступа к GameProgress
        self.portal_system = None
    
    def update(self, dt):
        """
        Обновляет состояние здоровья всех сущностей
        :param dt: Время, прошедшее с последнего обновления
        """
        # Получаем систему порталов, если еще не получили
        if not self.portal_system:
            for system in self.world.systems:
                if hasattr(system, 'get_game_progress'):
                    self.portal_system = system
                    break
        
        # Обновляем индикаторы урона/лечения
        self.update_damage_indicators(dt)
        
        # Получаем все сущности с компонентом здоровья
        entities = self.world.get_entities_with_components(Health)
        
        for entity_id in entities:
            health = self.world.get_component(entity_id, Health)
            
            # Обрабатываем неуязвимость
            if health.invulnerable:
                health.invulnerable_timer -= dt
                if health.invulnerable_timer <= 0:
                    health.invulnerable = False
            
            # Обрабатываем регенерацию здоровья
            if health.regeneration_rate > 0:
                health.regeneration_timer += dt
                if health.regeneration_timer >= health.regeneration_interval:
                    health.regeneration_timer = 0
                    self.heal_entity(entity_id, health.regeneration_rate)
            
            # Проверяем, не умерла ли сущность
            if health.current <= 0:
                # Проверяем, является ли сущность игроком
                if self.world.has_component(entity_id, Player):
                    # Игрок умер, обрабатываем смерть игрока
                    self.handle_player_death(entity_id)
                else:
                    # Обрабатываем смерть не-игрока (например, врага)
                    self.handle_entity_death(entity_id)
    
    def damage_entity(self, entity_id, damage, attacker_id=None):
        """
        Наносит урон сущности
        :param entity_id: ID сущности
        :param damage: Количество урона
        :param attacker_id: ID атакующей сущности (если есть)
        :return: Фактически нанесенный урон (0, если сущность неуязвима)
        """
        if not self.world.entity_exists(entity_id):
            return 0
            
        health = self.world.get_component(entity_id, Health)
        if not health:
            return 0
            
        # Проверяем неуязвимость
        if health.invulnerable:
            return 0
            
        # Наносим урон
        old_health = health.current
        health.current = max(0, health.current - damage)
        actual_damage = old_health - health.current
        
        # Если урон нанесен, создаем индикатор урона
        if actual_damage > 0 and self.world.has_component(entity_id, Position):
            position = self.world.get_component(entity_id, Position)
            self.add_damage_indicator(position.x, position.y, actual_damage, is_healing=False)
            
            # Делаем сущность временно неуязвимой
            health.invulnerable = True
            health.invulnerable_timer = 0.5  # Полсекунды неуязвимости
        
        return actual_damage
    
    def heal_entity(self, entity_id, amount):
        """
        Лечит сущность
        :param entity_id: ID сущности
        :param amount: Количество лечения
        :return: Фактически восстановленное здоровье
        """
        if not self.world.entity_exists(entity_id):
            return 0
            
        health = self.world.get_component(entity_id, Health)
        if not health:
            return 0
            
        # Восстанавливаем здоровье
        old_health = health.current
        health.current = min(health.maximum, health.current + amount)
        actual_healing = health.current - old_health
        
        # Если здоровье восстановлено, создаем индикатор лечения
        if actual_healing > 0 and self.world.has_component(entity_id, Position):
            position = self.world.get_component(entity_id, Position)
            self.add_damage_indicator(position.x, position.y, actual_healing, is_healing=True)
        
        return actual_healing
    
    def handle_player_death(self, player_id):
        """
        Обрабатывает смерть игрока
        :param player_id: ID игрока
        """
        print("Игрок умер!")
        
        # Сбрасываем здоровье игрока до максимума
        health = self.world.get_component(player_id, Health)
        health.current = health.maximum
        
        # Сбрасываем прогресс игры, если есть система порталов
        if self.portal_system and hasattr(self.portal_system, 'game_progress'):
            # Сохраняем счет и количество убитых врагов
            score = self.portal_system.game_progress.total_score
            enemies_killed = self.portal_system.game_progress.enemies_killed
            
            # Создаем новый прогресс
            self.portal_system.game_progress = self.portal_system.game_progress.__class__()
            
            # Восстанавливаем счет и количество убитых врагов
            self.portal_system.game_progress.total_score = score
            self.portal_system.game_progress.enemies_killed = enemies_killed
            
            # Сбрасываем уровень
            self.portal_system.current_level = 1
            
            print(f"Игра сброшена! Общий счет: {score}, Убито врагов: {enemies_killed}")
            
            # Перезагружаем уровень
            if hasattr(self.portal_system, 'clear_current_level'):
                self.portal_system.clear_current_level()
                
                # Создаем новый уровень
                from ecs.factories.level_factory import create_level
                level_entities = create_level(self.world, 30, 30)
                
                # Находим вход для размещения игрока
                entrance_pos = self.portal_system.find_entrance_position(level_entities)
                if entrance_pos:
                    player_pos = self.world.get_component(player_id, Position)
                    player_pos.x = entrance_pos.x
                    player_pos.y = entrance_pos.y
                
                # Создаем врагов
                self.portal_system.spawn_enemies_on_level(level_entities, player_id)
    
    def handle_entity_death(self, entity_id):
        """
        Обрабатывает смерть сущности (не игрока)
        :param entity_id: ID сущности
        """
        # Проверяем, является ли сущность врагом
        if self.world.has_component(entity_id, Enemy):
            # Увеличиваем счетчик убитых врагов в GameProgress
            if self.portal_system and hasattr(self.portal_system, 'game_progress'):
                self.portal_system.game_progress.enemy_killed()
                
                # Выводим информацию о прогрессе
                progress = self.portal_system.game_progress
                print(f"Враг убит! Счет: {progress.total_score}, Убито врагов: {progress.enemies_killed}")
        
        # Удаляем сущность из мира
        self.world.delete_entity(entity_id)
    
    def add_damage_indicator(self, x, y, amount, is_healing=False):
        """
        Добавляет индикатор урона/лечения
        :param x: Позиция X
        :param y: Позиция Y
        :param amount: Количество урона/лечения
        :param is_healing: True, если это лечение, False, если урон
        """
        # Создаем случайное смещение для индикатора
        import random
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 0)
        
        # Определяем цвет индикатора
        color = self.heal_color if is_healing else self.damage_color
        
        # Создаем текст индикатора
        text = f"+{amount}" if is_healing else f"-{amount}"
        
        # Добавляем индикатор в список
        self.damage_indicators.append({
            'x': x + offset_x,
            'y': y + offset_y,
            'text': text,
            'color': color,
            'lifetime': self.indicator_lifetime,
            'velocity_y': -30  # Скорость движения индикатора вверх
        })
    
    def update_damage_indicators(self, dt):
        """
        Обновляет индикаторы урона/лечения
        :param dt: Время, прошедшее с последнего обновления
        """
        # Обновляем все индикаторы
        for indicator in self.damage_indicators[:]:
            # Уменьшаем время жизни
            indicator['lifetime'] -= dt
            
            # Перемещаем индикатор вверх
            indicator['y'] += indicator['velocity_y'] * dt
            
            # Если время жизни истекло, удаляем индикатор
            if indicator['lifetime'] <= 0:
                self.damage_indicators.remove(indicator)
    
    def render(self, camera):
        """
        Отрисовывает индикаторы урона/лечения и полоски здоровья
        :param camera: Камера для преобразования координат
        """
        # Отрисовываем индикаторы урона/лечения
        for indicator in self.damage_indicators:
            # Преобразуем координаты с учетом камеры
            screen_x, screen_y = camera.world_to_screen(indicator['x'], indicator['y'])
            
            # Настраиваем прозрачность в зависимости от оставшегося времени жизни
            alpha = int(255 * (indicator['lifetime'] / self.indicator_lifetime))
            color = (indicator['color'][0], indicator['color'][1], indicator['color'][2], alpha)
            
            # Отрисовываем текст
            text_surface = self.font.render(indicator['text'], True, color)
            self.screen.blit(text_surface, (screen_x, screen_y))
        
        # Отрисовываем полоски здоровья для сущностей
        entities = self.world.get_entities_with_components(Health, Position)
        
        for entity_id in entities:
            health = self.world.get_component(entity_id, Health)
            position = self.world.get_component(entity_id, Position)
            
            # Преобразуем координаты с учетом камеры
            screen_x, screen_y = camera.world_to_screen(position.x, position.y)
            
            # Определяем размер полоски здоровья
            bar_width = 30
            bar_height = 5
            
            # Определяем цвет полоски здоровья
            health_ratio = health.current / health.maximum
            if health_ratio > 0.7:
                color = (0, 255, 0)  # Зеленый
            elif health_ratio > 0.3:
                color = (255, 255, 0)  # Желтый
            else:
                color = (255, 0, 0)  # Красный
            
            # Отрисовываем фон полоски здоровья
            pygame.draw.rect(self.screen, (0, 0, 0), 
                            (screen_x - bar_width/2, screen_y - 20, bar_width, bar_height))
            
            # Отрисовываем полоску здоровья
            current_width = bar_width * health_ratio
            pygame.draw.rect(self.screen, color, 
                            (screen_x - bar_width/2, screen_y - 20, current_width, bar_height))
        
        # Отрисовываем полоску здоровья игрока в углу экрана
        player_entities = self.world.get_entities_with_components(Player, Health)
        if player_entities:
            player_id = player_entities[0]
            health = self.world.get_component(player_id, Health)
            
            # Определяем размер полоски здоровья игрока
            bar_width = 200
            bar_height = 20
            bar_x = 20
            bar_y = self.screen.get_height() - 40
            
            # Определяем цвет полоски здоровья
            health_ratio = health.current / health.maximum
            if health_ratio > 0.7:
                color = (0, 255, 0)  # Зеленый
            elif health_ratio > 0.3:
                color = (255, 255, 0)  # Желтый
            else:
                color = (255, 0, 0)  # Красный
            
            # Отрисовываем фон полоски здоровья
            pygame.draw.rect(self.screen, (50, 50, 50), 
                            (bar_x, bar_y, bar_width, bar_height))
            
            # Отрисовываем полоску здоровья
            current_width = bar_width * health_ratio
            pygame.draw.rect(self.screen, color, 
                            (bar_x, bar_y, current_width, bar_height))
            
            # Отрисовываем текст с количеством здоровья
            health_text = f"HP: {health.current}/{health.maximum}"
            text_surface = self.font.render(health_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (bar_x + 10, bar_y + 2))
            
            # Отрисовываем информацию о прогрессе, если доступна
            if self.portal_system and hasattr(self.portal_system, 'game_progress'):
                progress = self.portal_system.game_progress
                
                # Отрисовываем текст с информацией о прогрессе
                level_text = f"Уровень: {progress.level}"
                score_text = f"Счет: {progress.total_score}"
                kills_text = f"Убито: {progress.enemies_killed}"
                
                level_surface = self.font.render(level_text, True, (255, 255, 255))
                score_surface = self.font.render(score_text, True, (255, 255, 255))
                kills_surface = self.font.render(kills_text, True, (255, 255, 255))
                
                self.screen.blit(level_surface, (bar_x + bar_width + 20, bar_y))
                self.screen.blit(score_surface, (bar_x + bar_width + 20, bar_y + 20))
                self.screen.blit(kills_surface, (bar_x + bar_width + 120, bar_y + 20)) 