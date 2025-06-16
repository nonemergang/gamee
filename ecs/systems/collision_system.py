from ecs.systems.system import System
from ecs.components.components import Position, Collider, Bullet, Enemy, Player, Health

class CollisionSystem(System):
    """Система для обработки столкновений между сущностями"""
    
    def update(self, dt):
        """
        Проверяет и обрабатывает столкновения между сущностями
        :param dt: Время, прошедшее с последнего обновления (в секундах)
        """
        # Получаем все сущности с коллайдерами
        collider_entities = self.world.get_entities_with_components(Position, Collider)
        
        # Проверяем столкновения пуль с врагами
        bullet_entities = self.world.get_entities_with_components(Bullet, Position, Collider)
        enemy_entities = self.world.get_entities_with_components(Enemy, Position, Collider, Health)
        
        for bullet_id in bullet_entities:
            bullet = self.world.get_component(bullet_id, Bullet)
            bullet_pos = self.world.get_component(bullet_id, Position)
            bullet_collider = self.world.get_component(bullet_id, Collider)
            
            for enemy_id in enemy_entities:
                # Пропускаем, если пуля принадлежит врагу
                if bullet.owner_id == enemy_id:
                    continue
                
                enemy_pos = self.world.get_component(enemy_id, Position)
                enemy_collider = self.world.get_component(enemy_id, Collider)
                enemy_health = self.world.get_component(enemy_id, Health)
                
                # Проверяем столкновение
                if self._check_collision(bullet_pos, bullet_collider, enemy_pos, enemy_collider):
                    # Наносим урон врагу
                    enemy_health.value -= bullet.damage
                    
                    # Удаляем пулю
                    self.world.delete_entity(bullet_id)
                    
                    # Если у врага закончилось здоровье, удаляем его
                    if enemy_health.value <= 0:
                        self.world.delete_entity(enemy_id)
                    
                    # Прерываем цикл, так как пуля уже удалена
                    break
        
        # Проверяем столкновения игрока с врагами
        player_entities = self.world.get_entities_with_components(Player, Position, Collider, Health)
        
        for player_id in player_entities:
            player_pos = self.world.get_component(player_id, Position)
            player_collider = self.world.get_component(player_id, Collider)
            player_health = self.world.get_component(player_id, Health)
            
            # Пропускаем, если игрок неуязвим
            if player_health.invulnerable:
                player_health.invulnerable_timer -= dt
                if player_health.invulnerable_timer <= 0:
                    player_health.invulnerable = False
                continue
            
            for enemy_id in enemy_entities:
                enemy = self.world.get_component(enemy_id, Enemy)
                enemy_pos = self.world.get_component(enemy_id, Position)
                enemy_collider = self.world.get_component(enemy_id, Collider)
                
                # Проверяем столкновение
                if self._check_collision(player_pos, player_collider, enemy_pos, enemy_collider):
                    # Наносим урон игроку
                    player_health.value -= enemy.damage
                    
                    # Делаем игрока временно неуязвимым
                    player_health.invulnerable = True
                    player_health.invulnerable_timer = 0.5  # 0.5 секунды неуязвимости
                    
                    # Если у игрока закончилось здоровье, обрабатываем это
                    if player_health.value <= 0:
                        # Здесь можно добавить логику окончания игры
                        pass
                    
                    # Сбрасываем таймер атаки врага
                    enemy.attack_cooldown = 1.0  # 1 секунда между атаками
                    
                    break
    
    def _check_collision(self, pos1, collider1, pos2, collider2):
        """
        Проверяет столкновение между двумя сущностями
        :param pos1: Компонент Position первой сущности
        :param collider1: Компонент Collider первой сущности
        :param pos2: Компонент Position второй сущности
        :param collider2: Компонент Collider второй сущности
        :return: True, если есть столкновение, иначе False
        """
        # Вычисляем границы первой сущности
        left1 = pos1.x - collider1.width / 2
        right1 = pos1.x + collider1.width / 2
        top1 = pos1.y - collider1.height / 2
        bottom1 = pos1.y + collider1.height / 2
        
        # Вычисляем границы второй сущности
        left2 = pos2.x - collider2.width / 2
        right2 = pos2.x + collider2.width / 2
        top2 = pos2.y - collider2.height / 2
        bottom2 = pos2.y + collider2.height / 2
        
        # Проверяем пересечение
        return (left1 < right2 and right1 > left2 and
                top1 < bottom2 and bottom1 > top2) 