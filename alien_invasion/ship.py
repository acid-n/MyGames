import pygame
from pygame.sprite import Sprite
import sys

class Ship(Sprite):
    """Класс для управления кораблем"""

    def __init__(self, ai_game):
        """Инициализирует корабль и задает его начальную позицию"""
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Загружает изображение корабля и получает прямоугольник
        try:
            self.image = pygame.image.load(self.settings.ship_image_path)
        except pygame.error as e:
            print(f"Error: Could not load ship image at {self.settings.ship_image_path}. Pygame error: {e}")
            sys.exit()
        self.rect = self.image.get_rect()

        # Каждый новый корабль появляется у нижнего края экрана
        self.rect.midbottom = self.screen_rect.midbottom

        # Сохранение вещественной координаты центра корабля
        self.x = float(self.rect.x)

        # Флаг перемещения
        self.moving_right = False
        self.moving_left = False

        # Атрибуты щита
        self.shield_active = False
        self.shield_end_time = 0

        # Атрибуты двойного огня (Double Fire)
        self.double_fire_active = False # Флаг активности двойного огня
        self.double_fire_end_time = 0   # Время окончания действия двойного огня

    def activate_shield(self):
        """Активирует щит на корабле на определенное время."""
        self.shield_active = True
        self.shield_end_time = pygame.time.get_ticks() + self.settings.shield_duration
        # Возможно, добавить звуковой эффект или визуальное подтверждение активации здесь

    def update(self):
        """Обновляет позицию корабля с учетом флагов"""

        # Обновляется атрибут х, не rect
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Обновление атрибута rect на основании self.x
        self.rect.x = self.x

        # Проверка и деактивация щита по времени
        if self.shield_active and pygame.time.get_ticks() > self.shield_end_time:
            self.shield_active = False
            # Возможно, добавить звуковой эффект или визуальное подтверждение деактивации

        # Проверка и деактивация двойного огня по времени
        if self.double_fire_active and pygame.time.get_ticks() > self.double_fire_end_time:
            self.double_fire_active = False
            # Возможно, добавить звуковой эффект или визуальное подтверждение деактивации двойного огня

    def activate_double_fire(self):
        """Активирует режим двойного огня (Double Fire) на определенное время."""
        self.double_fire_active = True
        self.double_fire_end_time = pygame.time.get_ticks() + self.settings.double_fire_duration
        # Возможно, добавить звуковой эффект или визуальное подтверждение активации

    def blitme(self):
        """Рисует корабль в текущей позиции"""
        self.screen.blit(self.image, self.rect)

        # Отрисовка щита, если он активен
        if self.shield_active:
            # Создаем прямоугольник немного больше корабля для эффекта обводки
            shield_rect = self.rect.inflate(10, 10) # Увеличить на 5 пикс. с каждой стороны
            pygame.draw.rect(self.screen, self.settings.ship_shield_outline_color, shield_rect, 2) # Толщина линии 2 пикс.

    def center_ship(self):
        """Размещает корабль в центре нижней стороны"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)