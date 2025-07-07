import pygame
from pygame.sprite import Sprite


class PowerUp(Sprite):
    """Класс для представления бонуса (power-up) в игре."""


import os  # Для проверки существования файла
import logging  # Для логирования ошибок загрузки

logger = logging.getLogger(__name__)


class PowerUp(Sprite):
    """Класс для представления бонуса (power-up) в игре."""

    def __init__(self, ai_game, powerup_type, center_pos):
        """Инициализирует объект бонуса."""
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.powerup_type = powerup_type  # e.g., 'shield'

        image_path = None
        fallback_color = (
            128,
            128,
            128,
        )  # Серый цвет по умолчанию для неизвестных типов

        # Определение пути к изображению и скорости в зависимости от типа бонуса
        if self.powerup_type == "shield":
            image_path = self.settings.powerup_shield_image_path
            self.speed = self.settings.current_shield_powerup_speed
            fallback_color = self.settings.shield_powerup_color
        elif self.powerup_type == "double_fire":
            image_path = self.settings.powerup_double_fire_image_path
            self.speed = self.settings.current_double_fire_powerup_speed
            fallback_color = self.settings.double_fire_powerup_color
        # Добавить elif для других типов бонусов, если они появятся
        # elif self.powerup_type == 'star':
        #     image_path = self.settings.powerup_star_image_path
        #     self.speed = self.settings.current_star_powerup_speed # Предполагая, что такая настройка будет
        #     fallback_color = (255, 255, 0) # Желтый для звезды
        else:
            logger.warning(
                f"Неизвестный тип бонуса '{self.powerup_type}'. Будет использован fallback."
            )
            self.speed = 0.5  # Медленная скорость по умолчанию для неизвестных типов

        # Загрузка изображения или создание fallback поверхности
        target_size = (
            self.settings.powerup_display_width,
            self.settings.powerup_display_height,
        )

        if image_path and os.path.exists(image_path):
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, target_size)
            except pygame.error as e:
                logger.warning(
                    f"Не удалось загрузить изображение бонуса '{image_path}': {e}. Используется fallback."
                )
                self.image = pygame.Surface(target_size)
                self.image.fill(fallback_color)
        else:
            if image_path:  # Путь был указан, но файл не найден
                logger.warning(
                    f"Файл изображения бонуса не найден: '{image_path}'. Используется fallback."
                )
            # Если image_path не был определен (неизвестный тип бонуса) или файл не существует
            self.image = pygame.Surface(target_size)
            self.image.fill(fallback_color)

        self.rect = self.image.get_rect()

        # Начальная позиция бонуса (например, центр уничтоженного пришельца)
        self.rect.center = center_pos

        # Сохранение точной вертикальной позиции
        self.y = float(self.rect.y)

    def update(self):
        """Перемещает бонус вниз по экрану."""
        self.y += self.speed
        self.rect.y = self.y

        # Удаление бонуса, если он вышел за нижний край экрана
        if self.rect.top > self.screen_rect.bottom:
            self.kill()  # Удаляет спрайт из всех групп, в которых он состоит

    # Метод draw(self, screen) не нужен, если self.image и self.rect
    # корректно установлены, так как pygame.sprite.Group.draw() сможет его отрисовать.
