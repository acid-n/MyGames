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

        # Размеры и свойства бонуса в зависимости от типа
        if self.powerup_type == 'shield':
            self.width = self.settings.shield_powerup_width
            self.height = self.settings.shield_powerup_height
            self.color = self.settings.shield_powerup_color
            self.speed = self.settings.shield_powerup_speed
        elif self.powerup_type == 'double_fire': # Новый тип бонуса "Двойной выстрел"
            self.width = self.settings.double_fire_powerup_width
            self.height = self.settings.double_fire_powerup_height
            self.color = self.settings.double_fire_powerup_color
            self.speed = self.settings.double_fire_powerup_speed
        else:
            # Тип бонуса неизвестен, используем значения по умолчанию или вызываем ошибку
            print(f"Предупреждение: Неизвестный тип бонуса '{self.powerup_type}'. Используются стандартные визуальные свойства.")
            self.width = 10 # Значение по умолчанию
            self.height = 10 # Значение по умолчанию
            self.color = (128, 128, 128) # Серый цвет по умолчанию
            self.speed = 0.5 # Медленная скорость по умолчанию

        # Создание поверхности и rect для бонуса
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
