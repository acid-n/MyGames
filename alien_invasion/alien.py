import pygame
from pygame.sprite import Sprite
import sys

class Alien(Sprite):
    """Класс, представляющий одного пришельца"""

    def __init__(self, ai_game):
        """Инициализирует пришельца и задает его начальную позицию"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Загрузка изображения пришельца и назначение атрибута rect
        try:
            self.image = pygame.image.load(self.settings.alien_image_path)
        except pygame.error as e:
            print(f"Error: Could not load alien image at {self.settings.alien_image_path}. Pygame error: {e}")
            sys.exit()
        self.rect = self.image.get_rect()

        # Каждый новый пришелец инициализируется со смещением от верхнего левого края, равным его размерам
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Сохранение точной горизонтальной позиции пришельца
        self.x = float(self.rect.x)

    def check_edges(self):
        """Возвращает True, если пришелец находится у края экрана"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Перемещает пришельца вправо или влево в зависимости от fleet_direction""" # Updated comment
        # Используем alien_speed_current для определения скорости пришельца
        self.x += (self.settings.alien_speed_current * self.settings.fleet_direction)
        self.rect.x = self.x