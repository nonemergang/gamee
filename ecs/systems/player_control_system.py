import pygame
import math
from ecs.systems.system import System
from ecs.components.components import Position, Velocity, Player, Weapon, Sprite
from ecs.systems.camera_system import CameraSystem
from ecs.systems.weapon_system import WeaponSystem

class PlayerControlSystem(System):
    """Система для обработки пользовательского ввода и управления игроком"""
    
    def __init__(self, world):
        super().__init__(world)
        self.weapon_system = None
        self.debug_mode = False  # Отключаем режим отладки
    
    def set_weapon_system(self, weapon_system):
        """
        Устанавливает ссылку на систему оружия
        :param weapon_system: Система оружия
        """
        self.weapon_system = weapon_system
        print(f"WeaponSystem установлена: {weapon_system}")
    
    def update(self, dt):
        """
        Обновляет систему управления игроком
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с компонентами Player, Position и Velocity
        player_entities = self.world.get_entities_with_components(Player, Position, Velocity)
        
        if not player_entities:
            return  # Нет игроков для обработки
            
        # Обрабатываем каждого игрока
        for player_id in player_entities:
            player = self.world.get_component(player_id, Player)
            position = self.world.get_component(player_id, Position)
            velocity = self.world.get_component(player_id, Velocity)
            
            # Проверяем наличие спрайта для поворота
            has_sprite = self.world.has_component(player_id, Sprite)
            
            # Проверяем наличие компонента Weapon (используем класс Weapon, а не строку)
            has_weapon = self.world.has_component(player_id, Weapon)
            if self.debug_mode and not has_weapon:
                print(f"У игрока нет компонента Weapon!")
            
            # Получаем состояние клавиш
            keys = pygame.key.get_pressed()
            
            # Сбрасываем скорость
            velocity.dx = 0
            velocity.dy = 0
            
            # Обработка движения
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                velocity.dy = -player.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                velocity.dy = player.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                velocity.dx = -player.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                velocity.dx = player.speed
            
            # Нормализуем скорость по диагонали
            if velocity.dx != 0 and velocity.dy != 0:
                velocity.dx *= 0.7071  # 1/sqrt(2)
                velocity.dy *= 0.7071
            
            # Получаем позицию курсора мыши
            mouse_x, mouse_y = pygame.mouse.get_pos()
            camera_system = next((system for system in self.world.systems if isinstance(system, CameraSystem)), None)
            
            if camera_system:
                # Преобразуем координаты мыши в мировые координаты
                world_mouse_x, world_mouse_y = camera_system.screen_to_world(mouse_x, mouse_y)
                
                # Поворачиваем спрайт игрока в сторону курсора
                if has_sprite:
                    sprite = self.world.get_component(player_id, Sprite)
                    
                    # Вычисляем угол между игроком и курсором
                    dx = world_mouse_x - position.x
                    dy = world_mouse_y - position.y
                    angle = math.degrees(math.atan2(dy, dx))
                    
                    # Корректируем угол для правильного отображения спрайта
                    # В Pygame 0 градусов - это направление вправо, а 90 градусов - вниз
                    # Мы хотим, чтобы спрайт смотрел вверх при 0 градусов
                    sprite.angle = angle + 90
            
                # Обработка стрельбы
                mouse_buttons = pygame.mouse.get_pressed()
                if mouse_buttons[0]:  # Левая кнопка мыши
                    if self.debug_mode:
                        print(f"Клик мыши: экран({mouse_x}, {mouse_y}), мир({world_mouse_x:.1f}, {world_mouse_y:.1f})")
                        print(f"Игрок: ({position.x:.1f}, {position.y:.1f})")
                    
                    # Проверяем наличие weapon_system
                    if not self.weapon_system:
                        print("weapon_system не установлена! Поиск WeaponSystem среди систем...")
                        self.weapon_system = next((system for system in self.world.systems if isinstance(system, WeaponSystem)), None)
                        if self.weapon_system:
                            print(f"WeaponSystem найдена: {self.weapon_system}")
                        else:
                            print("WeaponSystem не найдена среди систем мира!")
                    
                    # Стреляем в направлении мыши
                    if has_weapon and self.weapon_system:
                        # Передаем целевые координаты для выстрела
                        self.weapon_system.fire_bullet(player_id, world_mouse_x, world_mouse_y)
                    elif self.debug_mode:
                        if not has_weapon:
                            print("Не могу стрелять: у игрока нет оружия")
                        if not self.weapon_system:
                            print("Не могу стрелять: нет системы оружия")
            
            # Обработка перезарядки (клавиша R)
            if keys[pygame.K_r] and self.weapon_system and has_weapon:
                self.weapon_system.reload(player_id)
    
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