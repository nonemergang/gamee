import pygame
import os

def main():
    # Убедимся, что директория существует
    os.makedirs('assets/sprites', exist_ok=True)

    # Инициализируем pygame
    pygame.init()

    # Создаем спрайт игрока
    player_size = 24
    player = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
    # Тело (синее)
    pygame.draw.circle(player, (0, 100, 255), (player_size//2, player_size//2), player_size//2)
    # Глаза (белые с черными зрачками)
    eye_size = player_size // 6
    pygame.draw.circle(player, (255, 255, 255), (player_size//3, player_size//3), eye_size)
    pygame.draw.circle(player, (0, 0, 0), (player_size//3, player_size//3), eye_size//2)
    pygame.draw.circle(player, (255, 255, 255), (player_size*2//3, player_size//3), eye_size)
    pygame.draw.circle(player, (0, 0, 0), (player_size*2//3, player_size//3), eye_size//2)
    # Рот
    pygame.draw.arc(player, (0, 0, 0), (player_size//4, player_size//2, player_size//2, player_size//2), 0, 3.14, 2)
    pygame.image.save(player, 'assets/sprites/player.png')
    print("Создан спрайт игрока")

    # Создаем спрайт врага
    enemy_size = 32
    enemy = pygame.Surface((enemy_size, enemy_size), pygame.SRCALPHA)
    # Тело (красное)
    pygame.draw.circle(enemy, (255, 50, 50), (enemy_size//2, enemy_size//2), enemy_size//2)
    # Глаза (белые с черными зрачками)
    eye_size = enemy_size // 6
    pygame.draw.circle(enemy, (255, 255, 255), (enemy_size//3, enemy_size//3), eye_size)
    pygame.draw.circle(enemy, (0, 0, 0), (enemy_size//3, enemy_size//3), eye_size//2)
    pygame.draw.circle(enemy, (255, 255, 255), (enemy_size*2//3, enemy_size//3), eye_size)
    pygame.draw.circle(enemy, (0, 0, 0), (enemy_size*2//3, enemy_size//3), eye_size//2)
    # Рот (злой)
    pygame.draw.arc(enemy, (0, 0, 0), (enemy_size//4, enemy_size//2, enemy_size//2, enemy_size//2), 3.14, 6.28, 2)
    pygame.image.save(enemy, 'assets/sprites/enemy.png')
    print("Создан спрайт врага")

    # Создаем спрайт пули
    bullet_size = 16
    bullet = pygame.Surface((bullet_size, bullet_size), pygame.SRCALPHA)
    # Желтый круг
    pygame.draw.circle(bullet, (255, 255, 0), (bullet_size//2, bullet_size//2), bullet_size//3)
    # Свечение
    for i in range(3):
        alpha = 150 - i * 50
        pygame.draw.circle(bullet, (255, 255, 0, alpha), (bullet_size//2, bullet_size//2), bullet_size//3 + i)
    pygame.image.save(bullet, 'assets/sprites/bullet.png')
    print("Создан спрайт пули")

    # Создаем спрайты для тайлов
    tile_size = 32

    # Стена
    wall = pygame.Surface((tile_size, tile_size))
    wall.fill((80, 80, 100))
    # Текстура кирпичей
    for y in range(0, tile_size, 8):
        for x in range(0, tile_size, 16):
            offset = 8 if y % 16 == 0 else 0
            pygame.draw.rect(wall, (100, 100, 120), (x + offset, y, 7, 7))
    pygame.image.save(wall, 'assets/sprites/wall.png')
    print("Создан спрайт стены")

    # Пол
    floor = pygame.Surface((tile_size, tile_size))
    floor.fill((200, 200, 220))
    # Текстура плитки
    for y in range(0, tile_size, 16):
        for x in range(0, tile_size, 16):
            pygame.draw.rect(floor, (180, 180, 200), (x, y, 15, 15))
    pygame.image.save(floor, 'assets/sprites/floor.png')
    print("Создан спрайт пола")

    # Вход
    entrance = pygame.Surface((tile_size, tile_size))
    entrance.fill((100, 200, 100))
    # Узор входа
    pygame.draw.circle(entrance, (50, 150, 50), (tile_size//2, tile_size//2), tile_size//3)
    pygame.draw.circle(entrance, (150, 250, 150), (tile_size//2, tile_size//2), tile_size//6)
    pygame.image.save(entrance, 'assets/sprites/entrance.png')
    print("Создан спрайт входа")

    # Выход
    exit_tile = pygame.Surface((tile_size, tile_size))
    exit_tile.fill((200, 100, 100))
    # Узор выхода
    pygame.draw.circle(exit_tile, (150, 50, 50), (tile_size//2, tile_size//2), tile_size//3)
    pygame.draw.circle(exit_tile, (250, 150, 150), (tile_size//2, tile_size//2), tile_size//6)
    pygame.image.save(exit_tile, 'assets/sprites/exit.png')
    print("Создан спрайт выхода")

    # Декоративные элементы
    # Трещина на полу
    crack = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    pygame.draw.line(crack, (100, 100, 110), (10, 10), (22, 22), 2)
    pygame.draw.line(crack, (100, 100, 110), (22, 22), (28, 18), 2)
    pygame.image.save(crack, 'assets/sprites/crack.png')
    print("Создан спрайт трещины")

    # Мох на стене
    moss = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    for i in range(10):
        x = pygame.time.get_ticks() % tile_size
        y = (pygame.time.get_ticks() * 2) % tile_size
        size = (pygame.time.get_ticks() % 4) + 2
        pygame.draw.circle(moss, (0, 150, 0, 100), (x, y), size)
    pygame.image.save(moss, 'assets/sprites/moss.png')
    print("Создан спрайт мха")

    print('Спрайты успешно созданы в папке assets/sprites')

if __name__ == "__main__":
    main() 