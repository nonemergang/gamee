class World:
    """Мир ECS (Entity-Component-System)"""
    
    def __init__(self):
        """Инициализирует мир"""
        self.entities = {}  # Словарь сущностей
        self.components = {}  # Словарь компонентов
        self.systems = []  # Список систем
        self.next_entity_id = 0  # Следующий ID сущности
    
    def create_entity(self):
        """
        Создает новую сущность
        :return: ID созданной сущности
        """
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        self.entities[entity_id] = set()  # Множество компонентов сущности
        return entity_id
    
    def delete_entity(self, entity_id):
        """
        Удаляет сущность и все её компоненты
        :param entity_id: ID сущности
        """
        if entity_id in self.entities:
            # Удаляем все компоненты сущности
            for component_type in list(self.components.keys()):
                if entity_id in self.components[component_type]:
                    del self.components[component_type][entity_id]
            
            # Удаляем сущность
            del self.entities[entity_id]
    
    def clear_entities(self):
        """
        Удаляет все сущности и их компоненты
        """
        # Удаляем все компоненты
        self.components = {}
        
        # Удаляем все сущности
        self.entities = {}
        
        # Сбрасываем счетчик ID
        self.next_entity_id = 0
    
    def add_component(self, entity_id, component):
        """
        Добавляет компонент к сущности
        :param entity_id: ID сущности
        :param component: Экземпляр компонента
        """
        # Проверяем, что сущность существует
        if entity_id not in self.entities:
            return
        
        # Получаем тип компонента
        component_type = type(component)
        
        # Если такого типа компонентов еще нет, создаем словарь для него
        if component_type not in self.components:
            self.components[component_type] = {}
        
        # Добавляем компонент к сущности
        self.components[component_type][entity_id] = component
        
        # Добавляем тип компонента в множество компонентов сущности
        self.entities[entity_id].add(component_type)
    
    def remove_component(self, entity_id, component_type):
        """
        Удаляет компонент у сущности
        :param entity_id: ID сущности
        :param component_type: Тип компонента
        """
        # Проверяем, что сущность и компонент существуют
        if entity_id not in self.entities:
            return
        
        if component_type not in self.components:
            return
        
        if entity_id not in self.components[component_type]:
            return
        
        # Удаляем компонент
        del self.components[component_type][entity_id]
        
        # Удаляем тип компонента из множества компонентов сущности
        self.entities[entity_id].discard(component_type)
    
    def has_component(self, entity_id, component_type):
        """
        Проверяет, есть ли у сущности компонент указанного типа
        :param entity_id: ID сущности
        :param component_type: Тип компонента
        :return: True, если у сущности есть компонент указанного типа, иначе False
        """
        # Проверяем, что сущность существует
        if entity_id not in self.entities:
            return False
        
        # Проверяем, есть ли у сущности компонент указанного типа
        return component_type in self.entities[entity_id]
    
    def get_component(self, entity_id, component_type):
        """
        Возвращает компонент указанного типа у сущности
        :param entity_id: ID сущности
        :param component_type: Тип компонента
        :return: Экземпляр компонента или None, если компонент не найден
        """
        # Проверяем, что сущность и компонент существуют
        if not self.has_component(entity_id, component_type):
            return None
        
        # Возвращаем компонент
        return self.components[component_type][entity_id]
    
    def get_entities_with_components(self, *component_types):
        """
        Возвращает список ID сущностей, у которых есть все указанные компоненты
        :param component_types: Типы компонентов
        :return: Список ID сущностей
        """
        if not component_types:
            return list(self.entities.keys())
        
        # Если указан только один тип компонента, возвращаем все сущности с этим компонентом
        if len(component_types) == 1:
            component_type = component_types[0]
            if component_type in self.components:
                return list(self.components[component_type].keys())
            return []
        
        # Иначе находим сущности, у которых есть все указанные компоненты
        entities = []
        for entity_id, entity_components in self.entities.items():
            if all(component_type in entity_components for component_type in component_types):
                entities.append(entity_id)
        
        return entities
    
    def add_system(self, system):
        """
        Добавляет систему в мир
        :param system: Экземпляр системы
        """
        self.systems.append(system)
    
    def remove_system(self, system):
        """
        Удаляет систему из мира
        :param system: Экземпляр системы
        """
        if system in self.systems:
            self.systems.remove(system)
    
    def update(self, dt):
        """
        Обновляет все системы
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        for system in self.systems:
            system.update(dt)
    
    def render(self):
        """Запускает рендеринг всех систем"""
        for system in self.systems:
            if hasattr(system, 'render'):
                system.render() 