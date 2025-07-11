import pygame
from pygame.sprite import Sprite
import sys
import random
import os
import logging

logger = logging.getLogger(__name__)

# Constants for alien fallback visuals and tinting
# _FALLBACK_ALIEN_SIZE = (40, 40) # Заменено на использование alien_display_width/height из settings
_FALLBACK_ALIEN_COLOR = (0, 255, 0)  # Green
_MIN_CHANNEL_CHOICE = 0  # For R, G, B selection
_MAX_CHANNEL_CHOICE = 2
_MIN_TINT_INTENSITY = 100
_MAX_TINT_INTENSITY = 200
_MIN_TINT_ALPHA = 50
_MAX_TINT_ALPHA = 100


def _apply_tint(surface, tint_color):
    # Русский комментарий: Применяет оттенок к поверхности (surface).
    # tint_color это кортеж (R, G, B, Alpha), например (255, 0, 0, 100) для красного оттенка.
    # Создаем копию изображения, чтобы не изменять оригинал (если он еще где-то используется)
    # Однако, если tint применяется один раз при создании, можно менять self.image напрямую.
    # Для безопасности, создадим копию.

    # Убедимся, что поверхность поддерживает альфа-канал для корректного наложения
    # и не является исходным загруженным изображением, если оно будет переиспользоваться.
    # В нашем случае, self.image уже является уникальным для каждого пришельца.

    # Создаем поверхность для наложения того же размера, что и изображение пришельца
    tint_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    tint_surface.fill(tint_color)  # Заливаем выбранным цветом и прозрачностью

    # Накладываем оттенок на изображение пришельца используя режим смешивания BLEND_RGBA_MULT
    # или просто blit, если tint_surface уже с альфа-каналом.
    # BLEND_RGBA_MULT обычно хорошо подходит для эффекта "tint".
    # Если хотим просто наложить цвет, то обычный blit поверх.

    # Вариант 1: Простое наложение с альфа-прозрачностью (дает эффект "цветного стекла")
    surface.blit(tint_surface, (0, 0))
    return surface  # Возвращаем измененную поверхность

    # Вариант 2: Использование специальных флагов смешивания (может дать лучший эффект tint)
    # surface.blit(tint_surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT) # Альтернативный вариант смешивания
    # return surface
    # Примечание: pygame.BLEND_RGBA_MULT может давать разные результаты в зависимости от версии Pygame и настроек.
    # Простое наложение .blit() с альфа-каналом (выбранный вариант) является более предсказуемым.


class Alien(Sprite):
    """Класс, представляющий одного пришельца"""

    def __init__(self, ai_game, specific_image_path=None):
        # Русский комментарий: Инициализирует пришельца и задает его начальную позицию.
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Загрузка изображения пришельца
        if specific_image_path and os.path.exists(specific_image_path):
            self.image_path = specific_image_path
        elif (
            self.settings.alien_sprite_paths
        ):  # Если есть список путей и specific_image_path не задан
            self.image_path = random.choice(self.settings.alien_sprite_paths)
        else:
            # Этот блок теперь должен быть недостижим, если self.settings.alien_sprite_paths
            # всегда содержит хотя бы один путь (например, fallback 'alien_ship_01.png'),
            # как это обеспечивается в обновленном settings.py.
            # Если он все же достигается, это указывает на проблему в settings.py.
            logger.critical(
                "No alien sprites available in settings.alien_sprite_paths, even fallback is missing!"
            )
            # В качестве крайнего случая, чтобы игра не упала, устанавливаем image_path в None
            # и полагаемся на try-except блок ниже, который создаст цветную поверхность.
            self.image_path = None

        try:
            if self.image_path:  # Только если image_path не None
                self.image = pygame.image.load(self.image_path).convert_alpha()
            else:  # Если image_path is None (из-за критической ошибки выше)
                raise pygame.error("No image path provided for alien sprite.")
        except pygame.error as e:
            logger.warning(
                "Failed to load alien sprite: %s - %s. Using fallback.",
                self.image_path,
                e,
            )
            # Используем размеры из настроек для fallback
            fallback_size = (
                self.settings.alien_display_width,
                self.settings.alien_display_height,
            )
            self.image = pygame.Surface(fallback_size)
            self.image.fill(_FALLBACK_ALIEN_COLOR)

        # Масштабирование спрайта пришельца
        self.image = pygame.transform.scale(
            self.image,
            (self.settings.alien_display_width, self.settings.alien_display_height),
        )

        # Русский комментарий: Применяем случайный оттенок, если изображение загружено успешно
        # Проверка, что это не fallback Surface(1,1) или что-то подобное
        if (
            hasattr(self, "image")
            and self.image.get_width() > 1
            and self.image.get_height() > 1
        ):
            # Выбираем случайный цвет для оттенка (R, G, B) и альфа-канал для интенсивности
            # Фракций пока нет, поэтому оттенок полностью случайный для каждого пришельца
            # 0 или 1, чтобы один из каналов был доминирующим или отсутствовал
            r = random.randint(0, 1)  # 0 or 1 for off/on
            g = random.randint(0, 1)  # 0 or 1 for off/on
            b = random.randint(0, 1)  # 0 or 1 for off/on
            # Чтобы цвет был не слишком темным, убедимся, что хотя бы один канал не нулевой (если r,g,b все 0)
            if r == 0 and g == 0 and b == 0:  # All channels are zero
                choice = random.randint(_MIN_CHANNEL_CHOICE, _MAX_CHANNEL_CHOICE)
                if choice == _MIN_CHANNEL_CHOICE:  # 0
                    r = 1
                elif choice == _MIN_CHANNEL_CHOICE + 1:  # 1
                    g = 1
                else:
                    b = 1  # choice will be _MAX_CHANNEL_CHOICE (2)

            # Интенсивность основного цвета
            tint_r = r * random.randint(_MIN_TINT_INTENSITY, _MAX_TINT_INTENSITY)
            tint_g = g * random.randint(_MIN_TINT_INTENSITY, _MAX_TINT_INTENSITY)
            tint_b = b * random.randint(_MIN_TINT_INTENSITY, _MAX_TINT_INTENSITY)
            # Прозрачность оттенка (50-100 из 255)
            tint_alpha = random.randint(_MIN_TINT_ALPHA, _MAX_TINT_ALPHA)

            chosen_tint_color = (tint_r, tint_g, tint_b, tint_alpha)
            logger.debug(
                "Применяем оттенок %s к %s",
                chosen_tint_color,
                self.image_path if self.image_path else "N/A",
            )
            self.image = _apply_tint(self.image, chosen_tint_color)

        # Масштабирование спрайта пришельца было перенесено выше, перед применением оттенка,
        # чтобы оттенок применялся к уже масштабированному изображению.

        # Ensure self.rect is a real pygame.Rect for compatibility with pygame collision functions
        # even if self.image might be a MockSurface in tests (which returns a MockRect from get_rect())
        temp_rect = self.image.get_rect()
        self.rect = pygame.Rect(temp_rect.left, temp_rect.top, temp_rect.width, temp_rect.height)

        # Каждый новый пришелец появляется в левом верхнем углу экрана,
        # со смещением от краев, равным его размерам (ширине для x, высоте для y).
        # Это значит, что между левым краем экрана и левым краем пришельца будет self.rect.width пикселей.
        # Аналогично для верхнего края.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Сохранение точной горизонтальной позиции пришельца
        self.x = float(self.rect.x)

        # Русский комментарий: Атрибут для хранения типа бонуса, который может выпасть из этого пришельца
        # None, 'shield', 'double_fire', etc.
        self.assigned_powerup_type = None

    def check_edges(self):
        """Возвращает True, если пришелец находится у края экрана"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Перемещает пришельца вправо или влево в зависимости от fleet_direction"""  # Обновленный комментарий
        # Используем alien_speed_current для определения скорости пришельца
        self.x += self.settings.alien_speed_current * self.settings.fleet_direction
        self.rect.x = int(self.x) # Вернул int()
