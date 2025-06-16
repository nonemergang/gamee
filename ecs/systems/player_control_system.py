import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Player, Weapon
from ecs.systems.camera_system import CameraSystem

class PlayerControlSystem(System):
    """Система для обработки пользовательского ввода и управления игроком"""
    
    def update(self, dt):
        """
        Обрабатывает пользовательский ввод и обновляет компоненты игрока
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности игрока
        player_entities = self.world.get_entities_with_components(Player, Position, Velocity)
        
        if not player_entities:
            return
        
        # Обрабатываем только первого игрока (в случае многопользовательской игры)
        player_id = player_entities[0]
        player = self.world.get_component(player_id, Player)
        position = self.world.get_component(player_id, Position)
        velocity = self.world.get_component(player_id, Velocity)
        
        # Обработка клавиатурного ввода для движения
        keys = pygame.key.get_pressed()
        
        # Сбрасываем скорость
        velocity.dx = 0
        velocity.dy = 0
        
        # Определяем направление движения
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity.dy = -player.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.dy = player.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity.dx = -player.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.dx = player.speed
        
        # Нормализуем диагональное движение
        if velocity.dx != 0 and velocity.dy != 0:
            length = math.sqrt(velocity.dx ** 2 + velocity.dy ** 2)
            velocity.dx = velocity.dx / length * player.speed
            velocity.dy = velocity.dy / length * player.speed
        
        # Обработка стрельбы
        if self.world.has_component(player_id, Weapon):
            weapon = self.world.get_component(player_id, Weapon)
            
            # Обновляем таймер перезарядки
            if weapon.is_reloading:
                weapon.reload_timer += dt
                if weapon.reload_timer >= weapon.reload_time:
                    weapon.ammo = weapon.max_ammo
                    weapon.is_reloading = False
                    weapon.reload_timer = 0
            
            # Обновляем таймер стрельбы
            if weapon.cooldown > 0:
                weapon.cooldown -= dt
            
            # Получаем смещение камеры
            camera_offset = self._get_camera_offset()
            
            # Обработка нажатия кнопки мыши для стрельбы
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] and weapon.cooldown <= 0 and not weapon.is_reloading and weapon.ammo > 0:
                # Получаем позицию мыши в экранных координатах
                mouse_pos = pygame.mouse.get_pos()
                
                # Преобразуем экранные координаты в мировые с учетом смещения камеры
                # Для правильного расчета направления стрельбы
                world_mouse_x = mouse_pos[0] + camera_offset[0]
                world_mouse_y = mouse_pos[1] + camera_offset[1]
                
                # Вычисляем направление стрельбы
                dx = world_mouse_x - position.x
                dy = world_mouse_y - position.y
                
                # Нормализуем направление
                length = math.sqrt(dx ** 2 + dy ** 2)
                if length > 0:
                    dx = dx / length
                    dy = dy / length
                
                # Создаем событие стрельбы (будет обработано в WeaponSystem)
                self._create_shoot_event(player_id, position.x, position.y, dx, dy)
                
                # Обновляем состояние оружия
                weapon.ammo -= 1
                weapon.cooldown = 1.0 / weapon.fire_rate
            
            # Обработка перезарядки (клавиша R)
            if keys[pygame.K_r] and not weapon.is_reloading and weapon.ammo < weapon.max_ammo:
                weapon.is_reloading = True
                weapon.reload_timer = 0
    
    def _create_shoot_event(self, player_id, x, y, dx, dy):
        """
        Создает событие стрельбы
        :param player_id: ID игрока
        :param x: Позиция X
        :param y: Позиция Y
        :param dx: Направление X
        :param dy: Направление Y
        """
        # Здесь мы могли бы использовать систему событий
        # Но для простоты просто вызовем метод создания пули из WeaponSystem
        weapon_system = next((system for system in self.world.systems if isinstance(system, WeaponSystem)), None)
        if weapon_system:
            weapon = self.world.get_component(player_id, Weapon)
            weapon_system.create_bullet(player_id, x, y, dx, dy, weapon.damage, weapon.bullet_speed)
    
    def _get_camera_offset(self):
        """
        Получает смещение камеры для преобразования координат
        :return: Кортеж (offset_x, offset_y)
        """
        camera_system = next((system for system in self.world.systems if isinstance(system, CameraSystem)), None)
        if camera_system:
            return camera_system.get_camera_offset()
        return (0, 0)

# Импортируем WeaponSystem для создания пуль
from ecs.systems.weapon_system import WeaponSystem 