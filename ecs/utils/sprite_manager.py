import os
import pygame

class SpriteManager:
    """
    Менеджер спрайтов для загрузки и управления изображениями
    """
    
    def __init__(self):
        """
        Инициализирует менеджер спрайтов
        """
        self.sprites = {}
        self.default_sprites = {}
        
    def load_sprites(self, sprites_dir="assets/sprites"):
        """
        Загружает все спрайты из указанной директории
        :param sprites_dir: Путь к директории со спрайтами
        """
        print(f"Загрузка спрайтов из {sprites_dir}...")
        
        # Проверяем, существует ли директория
        if not os.path.exists(sprites_dir):
            print(f"Директория {sprites_dir} не существует")
            return
        
        # Загружаем все файлы из директории
        for filename in os.listdir(sprites_dir):
            # Проверяем, что это изображение
            if filename.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                # Получаем имя спрайта (без расширения)
                sprite_name = os.path.splitext(filename)[0]
                
                # Загружаем изображение
                try:
                    sprite_path = os.path.join(sprites_dir, filename)
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    self.sprites[sprite_name] = sprite
                    print(f"Загружен спрайт: {sprite_name}")
                except pygame.error as e:
                    print(f"Ошибка загрузки спрайта {filename}: {e}")
        
        print(f"Загружено спрайтов: {len(self.sprites)}")
        
        # Создаем дефолтные спрайты для случаев, когда нет нужных изображений
        self._create_default_sprites()
    
    def _create_default_sprites(self):
        """
        Создает дефолтные спрайты для случаев, когда нет нужных изображений
        """
        # Дефолтный спрайт игрока
        player_size = 24
        player_sprite = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
        pygame.draw.circle(player_sprite, (50, 100, 200), (player_size//2, player_size//2), player_size//2)
        # Глаза и рот
        eye_size = player_size // 6
        eye_offset = player_size // 4
        pygame.draw.circle(player_sprite, (255, 255, 255), (player_size//2 - eye_offset, player_size//2 - eye_offset), eye_size)
        pygame.draw.circle(player_sprite, (0, 0, 0), (player_size//2 - eye_offset, player_size//2 - eye_offset), eye_size // 2)
        pygame.draw.circle(player_sprite, (255, 255, 255), (player_size//2 + eye_offset, player_size//2 - eye_offset), eye_size)
        pygame.draw.circle(player_sprite, (0, 0, 0), (player_size//2 + eye_offset, player_size//2 - eye_offset), eye_size // 2)
        pygame.draw.arc(player_sprite, (0, 0, 0), (player_size//4, player_size//2, player_size//2, player_size//2), 0, 3.14, 2)
        self.default_sprites["player"] = player_sprite
        
        # Дефолтный спрайт врага
        enemy_size = 32
        enemy_sprite = pygame.Surface((enemy_size, enemy_size), pygame.SRCALPHA)
        pygame.draw.circle(enemy_sprite, (200, 50, 50), (enemy_size//2, enemy_size//2), enemy_size//2)
        # Глаза и рот
        eye_size = enemy_size // 6
        eye_offset = enemy_size // 4
        pygame.draw.circle(enemy_sprite, (255, 255, 255), (enemy_size//2 - eye_offset, enemy_size//2 - eye_offset), eye_size)
        pygame.draw.circle(enemy_sprite, (0, 0, 0), (enemy_size//2 - eye_offset, enemy_size//2 - eye_offset), eye_size // 2)
        pygame.draw.circle(enemy_sprite, (255, 255, 255), (enemy_size//2 + eye_offset, enemy_size//2 - eye_offset), eye_size)
        pygame.draw.circle(enemy_sprite, (0, 0, 0), (enemy_size//2 + eye_offset, enemy_size//2 - eye_offset), eye_size // 2)
        pygame.draw.arc(enemy_sprite, (0, 0, 0), (enemy_size//4, enemy_size//2, enemy_size//2, enemy_size//2), 0, 3.14, 2)
        self.default_sprites["enemy"] = enemy_sprite
        
        # Дефолтный спрайт пули
        bullet_size = 8
        bullet_sprite = pygame.Surface((bullet_size*2, bullet_size*2), pygame.SRCALPHA)
        # Основная пуля (желтая)
        pygame.draw.circle(bullet_sprite, (255, 255, 0), (bullet_size, bullet_size), bullet_size//2)
        # Внутренняя часть (более яркая)
        pygame.draw.circle(bullet_sprite, (255, 255, 200), (bullet_size, bullet_size), bullet_size//4)
        self.default_sprites["bullet"] = bullet_sprite
        
        # Дефолтные спрайты тайлов
        tile_size = 32
        
        # Стена
        wall_sprite = pygame.Surface((tile_size, tile_size))
        wall_sprite.fill((60, 60, 70))
        # Добавляем эффект кирпичей
        for i in range(0, tile_size, 8):
            for j in range(0, tile_size, 4):
                offset = 4 if i % 16 == 0 else 0
                pygame.draw.rect(wall_sprite, (80, 80, 90), (offset + j, i, 3, 3))
        # Добавляем тени
        pygame.draw.line(wall_sprite, (40, 40, 50), (0, 0), (0, tile_size-1), 2)
        pygame.draw.line(wall_sprite, (40, 40, 50), (0, 0), (tile_size-1, 0), 2)
        pygame.draw.line(wall_sprite, (90, 90, 100), (tile_size-1, 0), (tile_size-1, tile_size-1), 2)
        pygame.draw.line(wall_sprite, (90, 90, 100), (0, tile_size-1), (tile_size-1, tile_size-1), 2)
        self.default_sprites["wall"] = wall_sprite
        
        # Пол
        floor_sprite = pygame.Surface((tile_size, tile_size))
        floor_sprite.fill((180, 180, 190))
        # Добавляем эффект плитки
        for i in range(0, tile_size, 8):
            for j in range(0, tile_size, 8):
                pygame.draw.rect(floor_sprite, (170, 170, 180), (j, i, 7, 7))
        self.default_sprites["floor"] = floor_sprite
        
        # Вход
        entrance_sprite = pygame.Surface((tile_size, tile_size))
        entrance_sprite.fill((100, 200, 100))
        # Добавляем узор
        pygame.draw.circle(entrance_sprite, (50, 150, 50), (tile_size//2, tile_size//2), tile_size//3)
        pygame.draw.circle(entrance_sprite, (150, 250, 150), (tile_size//2, tile_size//2), tile_size//6)
        self.default_sprites["entrance"] = entrance_sprite
        
        # Выход
        exit_sprite = pygame.Surface((tile_size, tile_size))
        exit_sprite.fill((200, 100, 100))
        # Добавляем узор
        pygame.draw.circle(exit_sprite, (150, 50, 50), (tile_size//2, tile_size//2), tile_size//3)
        pygame.draw.circle(exit_sprite, (250, 150, 150), (tile_size//2, tile_size//2), tile_size//6)
        self.default_sprites["exit"] = exit_sprite
    
    def get_sprite(self, name):
        """
        Возвращает спрайт по имени
        :param name: Имя спрайта
        :return: Спрайт или None, если спрайт не найден
        """
        # Сначала ищем в загруженных спрайтах
        if name in self.sprites:
            return self.sprites[name]
        
        # Если не нашли, ищем в дефолтных спрайтах
        if name in self.default_sprites:
            return self.default_sprites[name]
        
        # Если и там не нашли, возвращаем None
        print(f"Спрайт {name} не найден")
        return None

# Создаем глобальный экземпляр менеджера спрайтов
sprite_manager = SpriteManager() 