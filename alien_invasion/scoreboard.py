import pygame.font
import os  # Added import
import pygame  # Added import
import logging
from pygame.sprite import Group
from alien_invasion.ship import Ship

# Constants for Scoreboard layout and appearance
_UI_ICON_SIZE = (32, 32)  # Standard size for UI icons like hearts, stars
_SCORE_FRAME_PADDING = 15  # Padding inside the score frame to the text
# _LIVES_ICON_TEXT_SPACING = 5 # Space between lives heart icon and 'xN' text - Удалено, так как текст xN не используется
_LIVES_ICON_SPACING = 5  # Пространство между иконками жизней

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
        self.prep_ships() # Должен быть вызван до _prep_score_frame, если рамка должна учитывать и жизни

        # Русский комментарий: Подготовка рамки для счета и уровня.
        # Этот метод вызывается после prep_score и prep_level, чтобы их rect были доступны.
        self._prep_score_frame()


    def _prep_score_frame(self):
        """Подготавливает фон (рамку) для отображения счета и уровня."""
        if not (self.frame_loaded_successfully and self.original_score_frame_bg):
            return # Рамка не загружена или не должна использоваться

        # Убедимся, что score_rect и level_rect существуют
        if not hasattr(self, 'score_rect') or not hasattr(self, 'level_rect'):
            logger.warning("Scoreboard frame disabled because score_rect or level_rect was not available.")
            self.frame_loaded_successfully = False # Отключаем рамку, если нет элементов для обрамления
            return

        # Определяем область, которую должна покрыть рамка, на основе score_rect и level_rect.
        # score_rect находится вверху, level_rect под ним.
        # Их right атрибуты должны быть одинаковы для корректного выравнивания.
        combined_rect_for_frame = self.score_rect.union(self.level_rect)

        # Рассчитываем целевые размеры рамки с учетом отступов
        target_frame_width = combined_rect_for_frame.width + 2 * _SCORE_FRAME_PADDING
        target_frame_height = combined_rect_for_frame.height + 2 * _SCORE_FRAME_PADDING

        try:
            self.scaled_score_frame_bg = pygame.transform.scale(
                self.original_score_frame_bg, (target_frame_width, target_frame_height))
            self.score_frame_rect = self.scaled_score_frame_bg.get_rect()
            # Центрируем рамку относительно объединенного текстового блока.
            self.score_frame_rect.center = combined_rect_for_frame.center
        except pygame.error as e:
            logger.warning(f"Error scaling score frame background: {e}. Frame will be inactive.")
            self.frame_loaded_successfully = False


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
        # Русский комментарий: Готовит отображение количества жизней с использованием иконок сердца.
        self.life_icons_to_draw = [] # Список для хранения изображений и rect-ов иконок жизней
        self.ships_group_fallback = Group() # Для старой логики, если иконки не загружены

        if self.heart_icon:
            # Отображаем N иконок сердец
            start_x = self.settings.lives_display_padding_left
            start_y = self.settings.lives_display_padding_top

            for i in range(self.stats.ships_left):
                icon_rect = self.heart_icon.get_rect()
                icon_rect.left = start_x + i * (icon_rect.width + _LIVES_ICON_SPACING)
                icon_rect.top = start_y
                self.life_icons_to_draw.append({'image': self.heart_icon, 'rect': icon_rect})
        else:
            # Русский комментарий: Если иконка сердца не загружена, используем старую логику с кораблями
            # Очищаем группу перед добавлением новых кораблей
            self.ships_group_fallback.empty()
            for ship_number in range(self.stats.ships_left):
                ship = Ship(self.ai_game) # Класс Ship должен быть импортирован
                # Масштабируем корабли для UI, если они слишком большие
                # Предполагаем, что иконка сердца имеет размер _UI_ICON_SIZE,
                # поэтому корабли тоже должны быть примерно такого размера.
                # Это можно сделать, передав специальный флаг в Ship или отмасштабировав здесь.
                # Пока оставим оригинальный размер корабля из Ship, но это может потребовать доработки.
                # ship.image = pygame.transform.scale(ship.image, _UI_ICON_SIZE) # Пример масштабирования
                # ship.rect = ship.image.get_rect()

                ship.rect.x = self.settings.lives_display_padding_left + ship_number * (ship.rect.width + _LIVES_ICON_SPACING)
                ship.rect.y = self.settings.lives_display_padding_top
                self.ships_group_fallback.add(ship)

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

        # Русский комментарий: Отображение жизней
        if self.heart_icon and self.life_icons_to_draw:
            for item in self.life_icons_to_draw:
                self.screen.blit(item['image'], item['rect'])
        elif not self.heart_icon and hasattr(self, 'ships_group_fallback'): # Используем старую систему с кораблями, если иконки нет
            self.ships_group_fallback.draw(self.screen)
