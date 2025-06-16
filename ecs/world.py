class World:
    def __init__(self):
        self.entities = {}
        self.components = {}
        self.systems = []
        self.next_entity_id = 0
        
    def create_entity(self):
        """Создает новую сущность и возвращает её ID"""
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        self.entities[entity_id] = set()
        return entity_id
    
    def delete_entity(self, entity_id):
        """Удаляет сущность и все её компоненты"""
        if entity_id in self.entities:
            # Удаляем компоненты сущности
            for component_type in list(self.entities[entity_id]):
                if component_type in self.components and entity_id in self.components[component_type]:
                    del self.components[component_type][entity_id]
            
            # Удаляем сущность
            del self.entities[entity_id]
    
    def add_component(self, entity_id, component):
        """Добавляет компонент к сущности"""
        component_type = type(component)
        
        # Добавляем тип компонента к сущности
        if entity_id in self.entities:
            self.entities[entity_id].add(component_type)
        
        # Добавляем компонент в хранилище компонентов
        if component_type not in self.components:
            self.components[component_type] = {}
        
        self.components[component_type][entity_id] = component
    
    def remove_component(self, entity_id, component_type):
        """Удаляет компонент с сущности"""
        if entity_id in self.entities and component_type in self.entities[entity_id]:
            self.entities[entity_id].remove(component_type)
            
        if component_type in self.components and entity_id in self.components[component_type]:
            del self.components[component_type][entity_id]
    
    def has_component(self, entity_id, component_type):
        """Проверяет, имеет ли сущность компонент указанного типа"""
        return entity_id in self.entities and component_type in self.entities[entity_id]
    
    def get_component(self, entity_id, component_type):
        """Возвращает компонент указанного типа для сущности"""
        if component_type in self.components and entity_id in self.components[component_type]:
            return self.components[component_type][entity_id]
        return None
    
    def get_entities_with_components(self, *component_types):
        """Возвращает список сущностей, имеющих все указанные компоненты"""
        if not component_types:
            return list(self.entities.keys())
        
        # Начинаем с первого компонента
        if component_types[0] not in self.components:
            return []
        
        # Получаем сущности с первым компонентом
        entity_ids = set(self.components[component_types[0]].keys())
        
        # Фильтруем по остальным компонентам
        for component_type in component_types[1:]:
            if component_type not in self.components:
                return []
            entity_ids &= set(self.components[component_type].keys())
        
        return list(entity_ids)
    
    def add_system(self, system):
        """Добавляет систему в мир"""
        system.world = self
        self.systems.append(system)
    
    def update(self, dt):
        """Обновляет все системы"""
        for system in self.systems:
            if hasattr(system, 'update'):
                system.update(dt)
    
    def render(self):
        """Запускает рендеринг всех систем"""
        for system in self.systems:
            if hasattr(system, 'render'):
                system.render() 