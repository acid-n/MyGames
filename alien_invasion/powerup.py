import pygame
from pygame.sprite import Sprite

class PowerUp(Sprite):
    """Класс для представления бонуса (power-up) в игре."""

    def __init__(self, ai_game, powerup_type, center_pos):
        """Инициализирует объект бонуса."""
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.powerup_type = powerup_type # e.g., 'shield'

        # Размеры и свойства бонуса (пока только для 'shield')
        if self.powerup_type == 'shield':
            self.width = self.settings.shield_powerup_width
            self.height = self.settings.shield_powerup_height
            self.color = self.settings.shield_powerup_color
            self.speed = self.settings.shield_powerup_speed
        # else:
            # Можно добавить другие типы бонусов здесь
            # self.width = 0 # или значения по умолчанию
            # self.height = 0
            # self.color = (0,0,0)
            # self.speed = 0

        # Создание поверхности и rect для бонуса
        # Убедимся, что width и height инициализированы, даже если тип неизвестен (хотя бы в 0)
        if not hasattr(self, 'width'): # Если тип не 'shield' и нет других else if
            self.width = 0
            self.height = 0
            self.color = (0,0,0) # Черный по умолчанию, если не задан
            self.speed = 0 # Не будет двигаться, если не задана скорость

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
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
            self.kill() # Удаляет спрайт из всех групп, в которых он состоит

    # Метод draw(self, screen) не нужен, если self.image и self.rect
    # корректно установлены, так как pygame.sprite.Group.draw() сможет его отрисовать.
