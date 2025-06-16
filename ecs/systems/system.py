class System:
    """Базовый класс для всех систем в ECS архитектуре"""
    def __init__(self, world=None):
        self.world = world
        
    def update(self, dt):
        """
        Обновляет систему
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        pass
    
    def render(self):
        """Отрисовывает компоненты, если необходимо"""
        pass 