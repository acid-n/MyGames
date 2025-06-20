import pygame.font
import os  # Added import
import pygame  # Added import
import logging
from pygame.sprite import Group
from alien_invasion.ship import Ship

# Constants for Scoreboard layout and appearance
_UI_ICON_SIZE = (32, 32)  # Standard size for UI icons like hearts, stars
_SCORE_FRAME_PADDING = 15 # Padding inside the score frame to the text
_LIVES_ICON_TEXT_SPACING = 5 # Space between lives heart icon and 'xN' text

logger = logging.getLogger(__name__)


class Scoreboard():
    """Класс для вывода игровой информации"""

    def __init__(self, ai_game):
        """Инициализирует атрибуты подстчета очков"""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Настройки шрифта для вывода счета
        self.text_color = self.settings.scoreboard_text_color
        self.font = pygame.font.SysFont(
            self.settings.scoreboard_font_name, self.settings.scoreboard_font_size)

        # Загрузка UI иконок
        self.heart_icon = None
        self.star_icon = None  # Пока не используется активно
        self.flag_icon = None  # Пока не используется активно

        # icon_size = (32, 32) # Replaced by _UI_ICON_SIZE

        try:
            # Русский комментарий: Иконка для жизней (сердце) из настроек
            heart_icon_path = self.settings.ui_heart_icon_path
            if os.path.exists(heart_icon_path):
                self.heart_icon = pygame.image.load(
                    heart_icon_path).convert_alpha()
                self.heart_icon = pygame.transform.scale(
                    self.heart_icon, _UI_ICON_SIZE)
            else:
                logger.warning("UI asset not found: %s. Feature may be disabled or use fallback.", heart_icon_path)

        except pygame.error as e:
            logger.warning("Error loading UI icons for Scoreboard: %s. Feature may be disabled or use fallback.", e, exc_info=True)

        # Русский комментарий: Загрузка и однократное масштабирование фона рамки для счета
        self.original_score_frame_bg = None
        self.scaled_score_frame_bg = None
        self.score_frame_rect = None
        self.frame_loaded_successfully = False
        try:
            frame_bg_path = self.settings.ui_score_frame_bg_path
            if os.path.exists(frame_bg_path):
                self.original_score_frame_bg = pygame.image.load(
                    frame_bg_path).convert_alpha()
                self.frame_loaded_successfully = True
                logger.info("UI asset loaded: Score frame background '%s'.", frame_bg_path)
            else:
                logger.warning("UI asset not found: Score frame background '%s'. Frame will be inactive.", frame_bg_path)
                # self.frame_loaded_successfully остается False
        except pygame.error as e:
            logger.warning("Error loading score frame background: %s. Frame will be inactive.", e, exc_info=True)
            # self.frame_loaded_successfully остается False

        # Подготовка изображений счетов. Эти методы создадут score_rect, high_score_rect и т.д.
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

        # Русский комментарий: Теперь, когда текстовые rects доступны, масштабируем фон рамки, если он был загружен
        if self.frame_loaded_successfully and self.original_score_frame_bg:
            # Русский комментарий: Отступы внутри рамки до текста.
            # frame_padding = 15  # px # Replaced by _SCORE_FRAME_PADDING

            # Русский комментарий: Определяем область, которую должна покрыть рамка.
            # Начнем с self.score_rect.
            if hasattr(self, 'score_rect'):
                combined_rect_for_frame = self.score_rect.copy()

                # Русский комментарий: Объединяем с self.high_score_rect, если он существует и должен быть внутри той же рамки.
                # Это предполагает, что high_score находится рядом или над score.
                # Если high_score рисуется в другом месте (например, строго по центру экрана),
                # то его не нужно включать в combined_rect_for_frame для рамки счета.
                # В текущей логике prep_high_score размещает его по центру вверху, а score справа вверху.
                # Для общей рамки их нужно будет перепозиционировать или использовать отдельные рамки.
                # Пока сделаем рамку только для score_rect и level_rect, так как они близко.
                if hasattr(self, 'level_rect'):
                    combined_rect_for_frame.union_ip(self.level_rect)
                # if hasattr(self, 'high_score_rect'):
                # combined_rect_for_frame.union_ip(self.high_score_rect) # Раскомментировать, если нужно включить и рекорд

                target_frame_width = combined_rect_for_frame.width + 2 * _SCORE_FRAME_PADDING
                target_frame_height = combined_rect_for_frame.height + 2 * _SCORE_FRAME_PADDING

                self.scaled_score_frame_bg = pygame.transform.scale(
                    self.original_score_frame_bg, (target_frame_width, target_frame_height))
                self.score_frame_rect = self.scaled_score_frame_bg.get_rect()
                # Русский комментарий: Центрируем рамку относительно объединенного текстового блока.
                self.score_frame_rect.center = combined_rect_for_frame.center
            else:
                # Русский комментарий: score_rect еще не готов, это неожиданно. Отключаем рамку.
                self.frame_loaded_successfully = False
                logger.warning("Scoreboard frame disabled because score_rect was not available after prep_score().")

    def prep_score(self):
        """Преобразует текущий счет в графическое изображение"""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)

        # Русский комментарий: Фон текста делаем прозрачным, если рамка будет использоваться, иначе используем цвет фона игры.
        text_bg_color = None if self.frame_loaded_successfully else self.settings.bg_color
        padding_x = self.settings.score_padding_right
        padding_y = self.settings.score_padding_top

        temp_score_image = self.font.render(
            score_str, True, self.text_color, text_bg_color)
        if text_bg_color is None:
            self.score_image = temp_score_image.convert_alpha()
        else:
            self.score_image = temp_score_image.convert()

        # Вывод счета в правой верхней части экрана
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - padding_x
        self.score_rect.top = padding_y

    def prep_high_score(self):
        """Преобразует рекордный счет в графическое изображение"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = f"{self.settings.text_high_score_label}{high_score:,}"

        # Русский комментарий: Фон текста рекорда делаем прозрачным, если рамка будет общая (пока не используется для рекорда).
        # Если рамка отдельная для рекорда или ее нет, используем цвет фона игры.
        # В текущей реализации рамка делается только для score и level, так что рекорд имеет свой фон.
        # Оставляем фон для рекорда, т.к. рамка его не покрывает
        text_bg_color_high = self.settings.bg_color

        temp_high_score_image = self.font.render(
            high_score_str, True, self.text_color, text_bg_color_high)
        self.high_score_image = temp_high_score_image.convert()

        # Рекорд выравнивается по центру верхней стороны
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        # Используем общий отступ сверху
        self.high_score_rect.top = self.settings.score_padding_top

    def prep_level(self):
        """Преобразует уровень в графическое изображение"""
        level_str = str(self.stats.level)
        temp_level_image = self.font.render(
            level_str, True, self.text_color, self.settings.bg_color)
        self.level_image = temp_level_image.convert()

        # Уровень выводится под текущим счетом
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + self.settings.level_score_spacing

    def prep_ships(self):
        # Русский комментарий: Готовит отображение количества жизней с использованием иконки сердца.
        if self.heart_icon:
            # Список для хранения того, что нужно отрисовать (иконка + текст)
            self.ships_items_for_draw = []

            # Иконка сердца
            heart_rect = self.heart_icon.get_rect()
            heart_rect.left = self.settings.lives_display_padding_left
            heart_rect.top = self.settings.lives_display_padding_top
            self.ships_items_for_draw.append(
                {'image': self.heart_icon, 'rect': heart_rect})

            # Текстовое представление количества жизней (например, "x3")
            ships_str = f"x{self.stats.ships_left}"
            # Используем тот же шрифт и цвет, что и для счета
            # bg_color может быть None для прозрачности, но здесь всегда self.settings.bg_color
            temp_ships_text_img = self.font.render(ships_str, True,
                                                   self.text_color, self.settings.bg_color)
            ships_text_img = temp_ships_text_img.convert()
            ships_text_rect = ships_text_img.get_rect()
            # Позиционируем текст справа от иконки сердца
            ships_text_rect.left = heart_rect.right + _LIVES_ICON_TEXT_SPACING
            ships_text_rect.centery = heart_rect.centery
            self.ships_items_for_draw.append(
                {'image': ships_text_img, 'rect': ships_text_rect})

        else:
            # Русский комментарий: Если иконка сердца не загружена, используем старую логику с кораблями
            # Этот блок нужен, если self.heart_icon None, но self.ships должен быть атрибутом класса
            if not hasattr(self, 'ships'):  # Инициализируем ships только если его нет
                self.ships = Group()
            else:
                self.ships.empty()  # Очищаем, если уже существует

            for ship_number in range(self.stats.ships_left):
                # Убедитесь, что класс Ship импортирован
                ship = Ship(self.ai_game)
                ship.rect.x = self.settings.lives_display_padding_left + \
                    ship_number * ship.rect.width
                ship.rect.y = self.settings.lives_display_padding_top
                self.ships.add(ship)
            self.ships_items_for_draw = None  # Явный признак, что используем старую систему

    def check_high_score(self):
        """Проверяет появился ли новый рекорд"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()
            self.stats._save_high_score()  # Сохраняем новый рекорд

    def show_score(self):
        """Выводит текущий счет, рекорд и число оставшихся кораблей"""
        # Русский комментарий: Отрисовка предварительно смасштабированной рамки счета, если она успешно загружена и подготовлена
        if self.frame_loaded_successfully and self.scaled_score_frame_bg and self.score_frame_rect:
            self.screen.blit(self.scaled_score_frame_bg, self.score_frame_rect)
        # Русский комментарий: Текстовые элементы счета, рекорда и уровня рисуются поверх рамки (или без нее)
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        # Русский комментарий: Отображение жизней (иконки или корабли)
        if hasattr(self, 'ships_items_for_draw') and self.ships_items_for_draw is not None and self.heart_icon:
            for item in self.ships_items_for_draw:
                self.screen.blit(item['image'], item['rect'])
        # Используем старую систему с кораблями, если иконки нет или ships_items_for_draw is None
        elif hasattr(self, 'ships'):
            self.ships.draw(self.screen)
