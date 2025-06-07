import pygame.font

class Button():

    def __init__(self, ai_game, msg):
        """Инициализирует атрибуты кнопки"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings

        # Назначение размеров и своств кнопок
        self.width, self.height = self.settings.button_width, self.settings.button_height
        self.button_color = self.settings.button_color_default
        self.text_color = self.settings.button_text_color_default
        self.font = pygame.font.SysFont(self.settings.button_font_name, self.settings.button_font_size)

        # Построение объекта rect кнопки и выравнивание по центру экрана
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # Сообщение кнопки создается только один раз
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Преобразует msg в прямоугольник и выравнивает текст по центру"""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        # Отображение пустой кнопки и вывод сообщения
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

    def is_clicked(self, mouse_pos):
        """Возвращает True, если кнопка была нажата (клик попал в область кнопки)."""
        return self.rect.collidepoint(mouse_pos)