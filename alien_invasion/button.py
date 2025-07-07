import pygame.font


class Button:

    def __init__(self, ai_game, msg):
        """Инициализирует атрибуты кнопки"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings

        # Назначение цветов и шрифта для кнопки (размеры будут динамическими)
        self.button_color = self.settings.button_color_default
        self.text_color = self.settings.button_text_color_default
        self.font = pygame.font.SysFont(
            self.settings.button_font_name, self.settings.button_font_size
        )

        # Сначала готовим текстовое изображение, чтобы получить его размеры
        self._prep_msg(msg)

        # Создание прямоугольника кнопки на основе размеров текста и отступов
        self.rect = pygame.Rect(
            0,
            0,
            self.msg_image_rect.width + self.settings.button_padding_x,
            self.msg_image_rect.height + self.settings.button_padding_y,
        )

        # Позиционирование кнопки (центр) будет установлено извне (в alien_invasion.py)
        # self.rect.center = self.screen_rect.center # Убрано, позиция задается в alien_invasion.py

        # Центрирование текстового изображения внутри кнопки
        self.msg_image_rect.center = self.rect.center

    def _prep_msg(self, msg):
        """Преобразует msg в графическое изображение."""
        temp_msg_image = self.font.render(
            msg, True, self.text_color, None
        )  # None for transparent text background
        self.msg_image = temp_msg_image.convert_alpha()
        self.msg_image_rect = self.msg_image.get_rect()
        # Убираем self.msg_image_rect.center = self.rect.center отсюда,
        # так как self.rect еще не имеет финальных размеров на этом этапе.

    def draw_button(self):
        # Отображение пустой кнопки и вывод сообщения
        self.screen.fill(self.button_color, self.rect)
        # Убедимся, что текст всегда центрирован относительно текущей позиции rect кнопки
        self.msg_image_rect.center = self.rect.center
        self.screen.blit(self.msg_image, self.msg_image_rect)

    def is_clicked(self, mouse_pos):
        """Возвращает True, если кнопка была нажата (клик попал в область кнопки)."""
        return self.rect.collidepoint(mouse_pos)
