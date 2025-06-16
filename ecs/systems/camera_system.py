from ecs.systems.system import System
from ecs.components.components import Position, Player, Camera

class CameraSystem(System):
    """Система для управления камерой, следующей за игроком"""
    
    def __init__(self, world, screen_width, screen_height):
        super().__init__(world)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.camera_entity = None
    
    def update(self, dt):
        """
        Обновляет положение камеры
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Если камера еще не создана, создаем её
        if self.camera_entity is None:
            self.camera_entity = self._create_camera()
        
        # Получаем компонент камеры
        camera = self.world.get_component(self.camera_entity, Camera)
        camera_pos = self.world.get_component(self.camera_entity, Position)
        
        # Если у камеры есть цель, следуем за ней
        if camera.target_id is not None and self.world.has_component(camera.target_id, Position):
            target_pos = self.world.get_component(camera.target_id, Position)
            
            # Плавно перемещаем камеру к цели
            lerp_factor = 5.0 * dt  # Коэффициент интерполяции
            camera_pos.x += (target_pos.x - camera_pos.x) * lerp_factor
            camera_pos.y += (target_pos.y - camera_pos.y) * lerp_factor
        
        # Если у камеры нет цели, ищем игрока
        else:
            player_entities = self.world.get_entities_with_components(Player, Position)
            if player_entities:
                camera.target_id = player_entities[0]
    
    def get_camera_offset(self):
        """
        Возвращает смещение камеры для отрисовки
        :return: Кортеж (offset_x, offset_y)
        """
        if self.camera_entity is None:
            return (0, 0)
        
        camera_pos = self.world.get_component(self.camera_entity, Position)
        
        # Смещение - это разница между центром экрана и позицией камеры
        offset_x = self.screen_width / 2 - camera_pos.x
        offset_y = self.screen_height / 2 - camera_pos.y
        
        return (offset_x, offset_y)
    
    def _create_camera(self):
        """
        Создает сущность камеры
        :return: ID сущности камеры
        """
        camera_entity = self.world.create_entity()
        self.world.add_component(camera_entity, Camera())
        self.world.add_component(camera_entity, Position(0, 0))
        return camera_entity 