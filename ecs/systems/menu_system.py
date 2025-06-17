import pygame

class MenuSystem:
    """Система для отображения меню игры (начальное меню и экран окончания игры)"""
    
    def __init__(self, screen, font=None):
        """
        Инициализирует систему меню
        :param screen: Поверхность Pygame для отрисовки
        :param font: Шрифт для текста меню
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Создаем шрифты разных размеров
        if font is None:
            self.title_font = pygame.font.SysFont(None, 72)
            self.button_font = pygame.font.SysFont(None, 48)
            self.score_font = pygame.font.SysFont(None, 36)
        else:
            self.title_font = font
            self.button_font = font
            self.score_font = font
        
        # Цвета
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.button_color = (50, 50, 50)
        self.button_hover_color = (80, 80, 80)
        self.button_text_color = (255, 255, 255)
        
        # Состояние меню
        self.show_start_menu = True
        self.show_game_over = False
        
        # Кнопки
        self.buttons = []
        
        # Создаем кнопки для начального меню
        self.start_menu_buttons = [
            {
                'text': 'Начать',
                'rect': pygame.Rect(self.width // 2 - 100, self.height // 2, 200, 50),
                'action': 'start_game'
            },
            {
                'text': 'Выход',
                'rect': pygame.Rect(self.width // 2 - 100, self.height // 2 + 70, 200, 50),
                'action': 'exit_game'
            }
        ]
        
        # Создаем кнопки для экрана окончания игры
        self.game_over_buttons = [
            {
                'text': 'Заново',
                'rect': pygame.Rect(self.width // 2 - 100, self.height // 2 + 50, 200, 50),
                'action': 'restart_game'
            },
            {
                'text': 'Выход',
                'rect': pygame.Rect(self.width // 2 - 100, self.height // 2 + 120, 200, 50),
                'action': 'exit_game'
            }
        ]
        
        # Текущий счет для отображения на экране окончания игры
        self.score = 0
        self.level = 1
        self.enemies_killed = 0
    
    def update(self, events):
        """
        Обрабатывает события и обновляет состояние меню
        :param events: Список событий Pygame
        :return: Действие, которое нужно выполнить ('start_game', 'exit_game', 'restart_game', None)
        """
        if not (self.show_start_menu or self.show_game_over):
            return None
        
        # Определяем, какие кнопки отображать
        if self.show_start_menu:
            self.buttons = self.start_menu_buttons
        elif self.show_game_over:
            self.buttons = self.game_over_buttons
        
        # Получаем позицию мыши
        mouse_pos = pygame.mouse.get_pos()
        
        # Обрабатываем события
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
                for button in self.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        return button['action']
        
        return None
    
    def render(self):
        """
        Отрисовывает меню
        """
        if not (self.show_start_menu or self.show_game_over):
            return
        
        print(f"Отрисовка меню: show_start_menu={self.show_start_menu}, show_game_over={self.show_game_over}")
        
        # Очищаем экран
        self.screen.fill(self.bg_color)
        
        # Отрисовываем заголовок
        if self.show_start_menu:
            title_text = "Рогалик в лабиринте"
            title_surface = self.title_font.render(title_text, True, self.text_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(title_surface, title_rect)
            print("Отрисован заголовок стартового меню")
        elif self.show_game_over:
            title_text = "Игра окончена"
            title_surface = self.title_font.render(title_text, True, self.text_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
            self.screen.blit(title_surface, title_rect)
            print("Отрисован заголовок экрана окончания игры")
            
            # Отображаем счет
            score_text = f"Счет: {self.score}"
            score_surface = self.score_font.render(score_text, True, self.text_color)
            score_rect = score_surface.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(score_surface, score_rect)
            
            # Отображаем уровень
            level_text = f"Уровень: {self.level}"
            level_surface = self.score_font.render(level_text, True, self.text_color)
            level_rect = level_surface.get_rect(center=(self.width // 2, self.height // 3 + 30))
            self.screen.blit(level_surface, level_rect)
            
            # Отображаем количество убитых врагов
            kills_text = f"Убито врагов: {self.enemies_killed}"
            kills_surface = self.score_font.render(kills_text, True, self.text_color)
            kills_rect = kills_surface.get_rect(center=(self.width // 2, self.height // 3 + 60))
            self.screen.blit(kills_surface, kills_rect)
            print(f"Отрисована статистика: счет={self.score}, уровень={self.level}, убито={self.enemies_killed}")
        
        # Отрисовываем кнопки
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Проверяем, наведена ли мышь на кнопку
            if button['rect'].collidepoint(mouse_pos):
                button_color = self.button_hover_color
            else:
                button_color = self.button_color
            
            # Отрисовываем кнопку
            pygame.draw.rect(self.screen, button_color, button['rect'], border_radius=10)
            pygame.draw.rect(self.screen, self.text_color, button['rect'], 2, border_radius=10)
            
            # Отрисовываем текст кнопки
            button_text = self.button_font.render(button['text'], True, self.button_text_color)
            button_text_rect = button_text.get_rect(center=button['rect'].center)
            self.screen.blit(button_text, button_text_rect)
        
        print(f"Отрисовано кнопок: {len(self.buttons)}")
    
    def show_start(self):
        """Показывает начальное меню"""
        self.show_start_menu = True
        self.show_game_over = False
    
    def show_game_over_screen(self, score, level, enemies_killed):
        """
        Показывает экран окончания игры
        :param score: Счет игрока
        :param level: Достигнутый уровень
        :param enemies_killed: Количество убитых врагов
        """
        print(f"Показываем экран окончания игры: счет={score}, уровень={level}, убито врагов={enemies_killed}")
        self.show_start_menu = False
        self.show_game_over = True
        self.score = score
        self.level = level
        self.enemies_killed = enemies_killed
        print(f"Состояние меню: show_start_menu={self.show_start_menu}, show_game_over={self.show_game_over}")
    
    def hide(self):
        """Скрывает все меню"""
        self.show_start_menu = False
        self.show_game_over = False
        print("Все меню скрыты") 