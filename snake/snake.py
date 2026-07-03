# snake-game — Классика с расширенной кастомизацией
# Copyright (C) 2026 Angel-Sora
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pygame
import random
import sys
import json
import os
from pygame.locals import *

# Инициализация
pygame.init()

# Константы
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Цвета по умолчанию
DEFAULT_COLORS = {
    'snake_head': (0, 200, 0),
    'snake_body': (0, 255, 0),
    'food': (255, 50, 50),
    'background': (20, 20, 30),
    'grid': (50, 50, 60),
    'text': (255, 255, 255)
}

# Настройки
SETTINGS_FILE = 'settings.json'
HAT_COLORS = [
    (255, 200, 50),   # Жёлтая
    (200, 50, 50),    # Красная
    (50, 100, 200),   # Синяя
    (200, 100, 50),   # Коричневая
    (150, 50, 150),   # Фиолетовая
    (255, 100, 100),  # Розовая
    (50, 200, 100),   # Зелёная
    (255, 150, 50),   # Оранжевая
    (200, 200, 200),  # Серая
    (255, 255, 255),  # Белая
]

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'colors': DEFAULT_COLORS.copy(), 'hat': 0, 'pattern': 0}
    return {'colors': DEFAULT_COLORS.copy(), 'hat': 0, 'pattern': 0}

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f)

# Загрузка настроек
settings = load_settings()
COLORS = settings.get('colors', DEFAULT_COLORS.copy())
SELECTED_HAT = settings.get('hat', 0)
SELECTED_PATTERN = settings.get('pattern', 0)

# Настройка окна
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("🐍 Змейка - Стильная")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 60)
title_font = pygame.font.Font(None, 72)

# Паттерны для тела змейки
PATTERNS = [
    [],  # Нет узора
    [0, 2, 4, 6, 8],  # Полоски через одну
    [0, 1, 2, 3, 4],  # Градиент
    [0, 3, 6, 9],  # Крупные полосы
    [0, 1, 3, 4, 6, 7, 9],  # Пиксельный
]

def draw_pattern(cell, index, color, pattern_index):
    """Рисует узор на клетке змейки"""
    if pattern_index == 0 or pattern_index >= len(PATTERNS):
        return
    
    pattern = PATTERNS[pattern_index]
    if index % 10 in pattern or index in pattern:
        center = cell.center
        radius = cell.width // 4
        
        if pattern_index == 1:
            # Полоски
            pygame.draw.line(screen, (255, 255, 255, 80), 
                           (cell.x + 2, cell.y + 2), 
                           (cell.x + cell.width - 2, cell.y + cell.height - 2), 2)
        elif pattern_index == 2:
            # Точки
            pygame.draw.circle(screen, (255, 255, 255, 120), center, radius // 2)
        elif pattern_index == 3:
            # Крестики
            pygame.draw.line(screen, (255, 255, 255, 80),
                           (cell.x + 3, cell.y + 3),
                           (cell.x + cell.width - 3, cell.y + cell.height - 3), 1)
            pygame.draw.line(screen, (255, 255, 255, 80),
                           (cell.x + cell.width - 3, cell.y + 3),
                           (cell.x + 3, cell.y + cell.height - 3), 1)
        elif pattern_index == 4:
            # Шахматка
            if (cell.x // CELL_SIZE + cell.y // CELL_SIZE) % 2 == 0:
                pygame.draw.rect(screen, (255, 255, 255, 50), cell)

# Классы игры
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow_flag = False
        self.move_counter = 0
    
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False
        self.move_counter += 1
    
    def grow(self):
        self.grow_flag = True
    
    def check_collision(self):
        head = self.body[0]
        if (head[0] < 0 or head[0] >= GRID_WIDTH or
            head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
        if head in self.body[1:]:
            return True
        return False
    
    def change_direction(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def draw_hat(self, x, y, size):
        """Рисует шляпу на голове змейки"""
        if SELECTED_HAT == 0:
            return
        
        hat_color = HAT_COLORS[SELECTED_HAT % len(HAT_COLORS)]
        hat_x = x * size
        hat_y = y * size
        
        # Основание шляпы
        pygame.draw.rect(screen, hat_color, (hat_x, hat_y - 8, size, 8), border_radius=3)
        
        # Верхушка шляпы
        if SELECTED_HAT == 1:  # Цилиндр
            pygame.draw.rect(screen, hat_color, (hat_x + 3, hat_y - 16, size - 6, 8))
            pygame.draw.rect(screen, (255, 255, 255), (hat_x + 3, hat_y - 16, size - 6, 8), 1)
        elif SELECTED_HAT == 2:  # Треугольная
            points = [(hat_x + size//2, hat_y - 18),
                     (hat_x + 2, hat_y - 8),
                     (hat_x + size - 2, hat_y - 8)]
            pygame.draw.polygon(screen, hat_color, points)
        elif SELECTED_HAT == 3:  # Шляпа с полями
            pygame.draw.ellipse(screen, hat_color, (hat_x - 3, hat_y - 6, size + 6, 6))
            pygame.draw.rect(screen, hat_color, (hat_x + 4, hat_y - 12, size - 8, 6))
        elif SELECTED_HAT == 4:  # Корона
            for i in range(3):
                cx = hat_x + 4 + i * 6
                pygame.draw.polygon(screen, (255, 215, 0),
                                  [(cx, hat_y - 16),
                                   (cx + 2, hat_y - 10),
                                   (cx - 2, hat_y - 10)])
            pygame.draw.rect(screen, (255, 215, 0), (hat_x, hat_y - 8, size, 8))
        elif SELECTED_HAT == 5:  # Кепка
            pygame.draw.arc(screen, hat_color, (hat_x, hat_y - 10, size, 12), 0, 3.14, 2)
            pygame.draw.rect(screen, hat_color, (hat_x + size - 4, hat_y - 8, 4, 8))
        else:  # Простая шляпа
            pygame.draw.ellipse(screen, hat_color, (hat_x - 2, hat_y - 10, size + 4, 6))
            pygame.draw.rect(screen, hat_color, (hat_x + 4, hat_y - 14, size - 8, 6))
    
    def draw(self, screen):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Основной цвет
            if i == 0:
                color = COLORS['snake_head']
            else:
                color = COLORS['snake_body']
                # Затемняем хвост
                darkness = max(0.5, 1 - (i / len(self.body)) * 0.5)
                color = tuple(int(c * darkness) for c in color)
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            
            # Добавляем узор
            if i > 0:
                draw_pattern(rect, i, color, SELECTED_PATTERN)
            
            # Рисуем шляпу на голове
            if i == 0:
                self.draw_hat(x, y, CELL_SIZE)

class Food:
    def __init__(self, snake_body):
        self.position = self.random_position(snake_body)
    
    def random_position(self, snake_body):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_body:
                return (x, y)
    
    def respawn(self, snake_body):
        self.position = self.random_position(snake_body)
    
    def draw(self, screen):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, COLORS['food'], rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        
        # Рисуем звёздочку на еде
        center = rect.center
        for i in range(4):
            angle = i * 90 + pygame.time.get_ticks() // 100
            dx = int(6 * pygame.math.Vector2(1, 0).rotate(angle).x)
            dy = int(6 * pygame.math.Vector2(1, 0).rotate(angle).y)
            pygame.draw.circle(screen, (255, 255, 255, 100), 
                             (center[0] + dx, center[1] + dy), 2)

# Кнопка
class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 255), hover_color=(50, 50, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.clicked = False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_color = self.hover_color if self.is_hovered else self.color
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if self.is_hovered else pygame.SYSTEM_CURSOR_ARROW)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False

def show_game_over(screen, score):
    """Красивое меню после смерти"""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Заголовок
    title = big_font.render("ИГРА ОКОНЧЕНА", True, (255, 50, 50))
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))
    
    # Счёт
    score_text = big_font.render(f"Счёт: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 230))
    
    # Декоративные змейки
    for i in range(5):
        x = 50 + i * 130
        y = 320 + (i % 2) * 30
        for j in range(4):
            rect = pygame.Rect(x + j * 15, y + j * 10, 12, 12)
            pygame.draw.rect(screen, (0, 200, 0, 100), rect, 2)
    
    # Кнопки
    restart_button = Button(WINDOW_WIDTH // 2 - 130, 400, 120, 50, "Рестарт", (0, 200, 0), (0, 150, 0))
    menu_button = Button(WINDOW_WIDTH // 2 + 10, 400, 120, 50, "В меню", (100, 100, 255), (50, 50, 200))
    
    restart_button.draw(screen)
    menu_button.draw(screen)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if restart_button.handle_event(event):
                return 'restart'
            
            if menu_button.handle_event(event):
                return 'menu'

def show_score(screen, score):
    text = font.render(f"Счёт: {score}", True, COLORS['text'])
    screen.blit(text, (10, 10))

def draw_grid():
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, COLORS['grid'], (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, COLORS['grid'], (0, y), (WINDOW_WIDTH, y), 1)

def game_loop():
    snake = Snake()
    food = Food(snake.body)
    score = 0
    speed = 10
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
                elif event.key == pygame.K_ESCAPE:
                    return 'menu'
        
        snake.move()
        
        if snake.body[0] == food.position:
            snake.grow()
            score += 1
            food.respawn(snake.body)
            speed = 10 + score // 5
        
        if snake.check_collision():
            result = show_game_over(screen, score)
            if result == 'restart':
                snake = Snake()
                food = Food(snake.body)
                score = 0
                speed = 10
                continue
            elif result == 'menu':
                return 'menu'
        
        screen.fill(COLORS['background'])
        draw_grid()
        snake.draw(screen)
        food.draw(screen)
        show_score(screen, score)
        
        hint = small_font.render("ESC - меню", True, (100, 100, 100))
        screen.blit(hint, (WINDOW_WIDTH - 100, 10))
        
        pygame.display.flip()
        clock.tick(speed)

# Меню кастомизации
class ColorPicker:
    def __init__(self, x, y, label, color_key, color):
        self.x = x
        self.y = y
        self.label = label
        self.color_key = color_key
        self.color = list(color)
        self.sliders = []
        self.create_sliders()
    
    def create_sliders(self):
        labels = ['R', 'G', 'B']
        for i, (label, value) in enumerate(zip(labels, self.color)):
            self.sliders.append({
                'label': label,
                'value': value,
                'rect': pygame.Rect(self.x + 200, self.y + i * 22, 150, 14)
            })
    
    def draw(self, screen):
        # Название
        text = small_font.render(self.label, True, (255, 255, 255))
        screen.blit(text, (self.x, self.y + 2))
        
        # Превью цвета
        rect = pygame.Rect(self.x + 120, self.y, 60, 20)
        pygame.draw.rect(screen, self.color, rect, border_radius=3)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1, border_radius=3)
        
        # Слайдеры
        for slider in self.sliders:
            pygame.draw.rect(screen, (50, 50, 50), slider['rect'])
            pygame.draw.rect(screen, (100, 100, 100), slider['rect'], 1)
            
            fill_rect = pygame.Rect(slider['rect'].x, slider['rect'].y, 
                                   (slider['value'] / 255) * slider['rect'].width, 
                                   slider['rect'].height)
            color = (255, 0, 0) if slider['label'] == 'R' else \
                    (0, 255, 0) if slider['label'] == 'G' else \
                    (0, 0, 255)
            pygame.draw.rect(screen, color, fill_rect)
            
            val_text = small_font.render(f"{slider['label']}: {slider['value']}", True, (200, 200, 200))
            screen.blit(val_text, (slider['rect'].x + 160, slider['rect'].y - 2))
    
    def handle_event(self, event):
        for slider in self.sliders:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if slider['rect'].collidepoint(event.pos):
                    relative_x = event.pos[0] - slider['rect'].x
                    new_value = int((relative_x / slider['rect'].width) * 255)
                    new_value = max(0, min(255, new_value))
                    slider['value'] = new_value
                    if slider['label'] == 'R':
                        self.color[0] = new_value
                    elif slider['label'] == 'G':
                        self.color[1] = new_value
                    elif slider['label'] == 'B':
                        self.color[2] = new_value
                    COLORS[self.color_key] = tuple(self.color)
                    save_settings({'colors': COLORS, 'hat': SELECTED_HAT, 'pattern': SELECTED_PATTERN})
                    return True
        return False

def settings_menu():
    global SELECTED_HAT, SELECTED_PATTERN, COLORS
    
    # Вкладки
    tabs = ["Цвета", "Шляпы", "Узоры"]
    active_tab = 0  # 0 - цвета, 1 - шляпы, 2 - узоры
    
    # Создаём кнопки вкладок
    tab_buttons = []
    tab_width = 150
    tab_height = 40
    tab_y = 60
    total_width = len(tabs) * tab_width
    start_x = (WINDOW_WIDTH - total_width) // 2
    
    for i, tab_name in enumerate(tabs):
        btn = Button(
            start_x + i * tab_width,
            tab_y,
            tab_width,
            tab_height,
            tab_name,
            (60, 60, 80) if i != active_tab else (0, 150, 200),
            (80, 80, 100) if i != active_tab else (0, 200, 255)
        )
        tab_buttons.append(btn)
    
    # Создаём пикеры цветов
    colors_y_start = 130
    colors_spacing = 55
    pickers = [
        ColorPicker(100, colors_y_start + 0 * colors_spacing, "Голова", 'snake_head', COLORS['snake_head']),
        ColorPicker(100, colors_y_start + 1 * colors_spacing, "Тело", 'snake_body', COLORS['snake_body']),
        ColorPicker(100, colors_y_start + 2 * colors_spacing, "Еда", 'food', COLORS['food']),
        ColorPicker(100, colors_y_start + 3 * colors_spacing, "Фон", 'background', COLORS['background']),
        ColorPicker(100, colors_y_start + 4 * colors_spacing, "Сетка", 'grid', COLORS['grid']),
    ]
    
    # Создаём кнопки для шляп (с иконками)
    hat_names = ["Нет", "Цилиндр", "Треуг.", "Поля", "Корона", "Кепка", "Шляпа"]
    hat_buttons = []
    hat_x = 150
    hat_y = 130
    hat_spacing = 50
    
    for i in range(len(hat_names)):
        btn = Button(
            hat_x,
            hat_y + i * hat_spacing,
            400, 35,
            hat_names[i],
            (60, 60, 80) if i != SELECTED_HAT else (0, 150, 0),
            (80, 80, 100) if i != SELECTED_HAT else (0, 200, 0)
        )
        hat_buttons.append(btn)
    
    # Создаём кнопки для узоров
    pattern_names = ["Нет", "Полоски", "Точки", "Кресты", "Шахматы"]
    pattern_buttons = []
    pattern_x = 150
    pattern_y = 130
    pattern_spacing = 50
    
    for i in range(len(pattern_names)):
        btn = Button(
            pattern_x,
            pattern_y + i * pattern_spacing,
            400, 35,
            pattern_names[i],
            (60, 60, 80) if i != SELECTED_PATTERN else (0, 150, 150),
            (80, 80, 100) if i != SELECTED_PATTERN else (0, 200, 200)
        )
        pattern_buttons.append(btn)
    
    # Кнопки управления
    back_button = Button(WINDOW_WIDTH - 140, 20, 120, 40, "Назад", (100, 100, 255), (50, 50, 200))
    reset_button = Button(WINDOW_WIDTH - 140, 560, 120, 40, "Сброс", (200, 100, 50), (150, 50, 0))
    
    # Превью змейки (справа внизу)
    preview_snake = [(5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (0, 3)]
    preview_food = (8, 3)
    
    running = True
    while running:
        screen.fill((25, 25, 35))
        
        # Заголовок
        title = big_font.render("Настройки", True, (255, 255, 255))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 10))
        
        # Рисуем вкладки
        for i, btn in enumerate(tab_buttons):
            # Обновляем цвет активной вкладки
            if i == active_tab:
                btn.color = (0, 150, 200)
                btn.hover_color = (0, 200, 255)
            else:
                btn.color = (60, 60, 80)
                btn.hover_color = (80, 80, 100)
            btn.draw(screen)
        
        # Содержимое вкладок
        if active_tab == 0:  # Цвета
            # Заголовок
            label = font.render("Выберите цвет для каждого элемента:", True, (200, 200, 200))
            screen.blit(label, (100, 110))
            
            for picker in pickers:
                picker.draw(screen)
        
        elif active_tab == 1:  # Шляпы
            # Заголовок
            label = font.render("Выберите шляпу для змейки:", True, (200, 200, 200))
            screen.blit(label, (150, 105))
            
            # Подсказка
            hint = small_font.render("Кликните на шляпу чтобы выбрать", True, (150, 150, 150))
            screen.blit(hint, (150, 125))
            
            for btn in hat_buttons:
                btn.draw(screen)
        
        elif active_tab == 2:  # Узоры
            # Заголовок
            label = font.render("Выберите узор для тела змейки:", True, (200, 200, 200))
            screen.blit(label, (150, 105))
            
            # Подсказка
            hint = small_font.render("Кликните на узор чтобы выбрать", True, (150, 150, 150))
            screen.blit(hint, (150, 125))
            
            for btn in pattern_buttons:
                btn.draw(screen)
        
        # Превью змейки с текущими настройками (всегда видно)
        preview_x = 550
        preview_y = 480
        
        # Рамка превью
        preview_bg = pygame.Rect(preview_x - 5, preview_y - 5, 130, 90)
        pygame.draw.rect(screen, (40, 40, 50), preview_bg, border_radius=5)
        pygame.draw.rect(screen, (80, 80, 100), preview_bg, 2, border_radius=5)
        
        # Рисуем превью фона
        bg_rect = pygame.Rect(preview_x, preview_y, 120, 80)
        pygame.draw.rect(screen, COLORS['background'], bg_rect)
        
        # Рисуем превью змейки
        for i, (px, py) in enumerate(preview_snake):
            rect = pygame.Rect(preview_x + 10 + px * 15, preview_y + 10 + py * 15, 12, 12)
            color = COLORS['snake_head'] if i == 0 else COLORS['snake_body']
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            
            # Рисуем шляпу на превью
            if i == 0 and SELECTED_HAT > 0:
                hat_color = HAT_COLORS[SELECTED_HAT % len(HAT_COLORS)]
                pygame.draw.rect(screen, hat_color, (rect.x, rect.y - 5, rect.width, 4))
                if SELECTED_HAT == 1:  # Цилиндр
                    pygame.draw.rect(screen, hat_color, (rect.x + 2, rect.y - 10, rect.width - 4, 5))
                elif SELECTED_HAT == 2:  # Треугольная
                    points = [(rect.centerx, rect.y - 12),
                             (rect.x + 1, rect.y - 5),
                             (rect.x + rect.width - 1, rect.y - 5)]
                    pygame.draw.polygon(screen, hat_color, points)
                elif SELECTED_HAT == 3:  # С полями
                    pygame.draw.ellipse(screen, hat_color, (rect.x - 2, rect.y - 4, rect.width + 4, 4))
                elif SELECTED_HAT == 4:  # Корона
                    for j in range(3):
                        cx = rect.x + 3 + j * 4
                        pygame.draw.polygon(screen, (255, 215, 0),
                                          [(cx, rect.y - 10),
                                           (cx + 2, rect.y - 5),
                                           (cx - 2, rect.y - 5)])
        
        # Рисуем превью еды
        food_rect = pygame.Rect(preview_x + 10 + preview_food[0] * 15, 
                               preview_y + 10 + preview_food[1] * 15, 12, 12)
        pygame.draw.rect(screen, COLORS['food'], food_rect)
        pygame.draw.rect(screen, (255, 255, 255), food_rect, 1)
        
        # Подпись превью
        preview_label = small_font.render("Превью", True, (150, 150, 150))
        screen.blit(preview_label, (preview_x + 30, preview_y - 20))
        
        # Кнопки управления
        back_button.draw(screen)
        reset_button.draw(screen)
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Обработка вкладок
            for i, btn in enumerate(tab_buttons):
                if btn.handle_event(event):
                    active_tab = i
                    # Обновляем цвета вкладок
                    for j, b in enumerate(tab_buttons):
                        if j == active_tab:
                            b.color = (0, 150, 200)
                            b.hover_color = (0, 200, 255)
                        else:
                            b.color = (60, 60, 80)
                            b.hover_color = (80, 80, 100)
            
            # Обработка кнопки "Назад"
            if back_button.handle_event(event):
                save_settings({'colors': COLORS, 'hat': SELECTED_HAT, 'pattern': SELECTED_PATTERN})
                running = False
                return
            
            # Обработка кнопки "Сброс"
            if reset_button.handle_event(event):
                COLORS = DEFAULT_COLORS.copy()
                SELECTED_HAT = 0
                SELECTED_PATTERN = 0
                # Обновляем пикеры
                for picker in pickers:
                    picker.color = list(COLORS[picker.color_key])
                # Обновляем цвета кнопок шляп
                for i, btn in enumerate(hat_buttons):
                    btn.color = (60, 60, 80) if i != SELECTED_HAT else (0, 150, 0)
                    btn.hover_color = (80, 80, 100) if i != SELECTED_HAT else (0, 200, 0)
                # Обновляем цвета кнопок узоров
                for i, btn in enumerate(pattern_buttons):
                    btn.color = (60, 60, 80) if i != SELECTED_PATTERN else (0, 150, 150)
                    btn.hover_color = (80, 80, 100) if i != SELECTED_PATTERN else (0, 200, 200)
            
            # Обработка кнопок шляп (только если активна вкладка "Шляпы")
            if active_tab == 1:
                for i, btn in enumerate(hat_buttons):
                    if btn.handle_event(event):
                        SELECTED_HAT = i
                        # Обновляем цвета кнопок
                        for j, b in enumerate(hat_buttons):
                            b.color = (60, 60, 80) if j != SELECTED_HAT else (0, 150, 0)
                            b.hover_color = (80, 80, 100) if j != SELECTED_HAT else (0, 200, 0)
            
            # Обработка кнопок узоров (только если активна вкладка "Узоры")
            if active_tab == 2:
                for i, btn in enumerate(pattern_buttons):
                    if btn.handle_event(event):
                        SELECTED_PATTERN = i
                        # Обновляем цвета кнопок
                        for j, b in enumerate(pattern_buttons):
                            b.color = (60, 60, 80) if j != SELECTED_PATTERN else (0, 150, 150)
                            b.hover_color = (80, 80, 100) if j != SELECTED_PATTERN else (0, 200, 200)
            
            # Обработка пикеров цвета (только если активна вкладка "Цвета")
            if active_tab == 0:
                for picker in pickers:
                    picker.handle_event(event)
        
        pygame.display.flip()
        clock.tick(60)

def main_menu():
    play_button = Button(WINDOW_WIDTH // 2 - 100, 300, 200, 50, "Играть", (0, 200, 0), (0, 150, 0))
    settings_button = Button(WINDOW_WIDTH // 2 - 100, 370, 200, 50, "Настройки", (100, 100, 255), (50, 50, 200))
    exit_button = Button(WINDOW_WIDTH // 2 - 100, 440, 200, 50, "Выход", (200, 50, 50), (150, 0, 0))
    
    while True:
        screen.fill((30, 30, 40))
        
        # Фоновые узоры
        for i in range(5):
            x = 50 + i * 130
            y = 100 + (i % 2) * 20
            for j in range(4):
                rect = pygame.Rect(x + j * 15, y + j * 10, 12, 12)
                pygame.draw.rect(screen, (0, 80, 0, 50), rect, 1)
        
        # Заголовок
        title = title_font.render("ЗМЕЙКА", True, (0, 255, 0))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))
        
        # Подзаголовок
        subtitle = font.render("Стильная классика с кастомизацией", True, (200, 200, 200))
        screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 220))
        
        # Кнопки
        for button in [play_button, settings_button, exit_button]:
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if play_button.handle_event(event):
                result = game_loop()
                if result == 'menu':
                    continue
            
            if settings_button.handle_event(event):
                settings_menu()
            
            if exit_button.handle_event(event):
                pygame.quit()
                sys.exit()
        
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
