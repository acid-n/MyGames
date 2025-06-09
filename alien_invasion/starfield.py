import pygame
import random

class Starfield:
    """Класс для управления процедурным звездным полем с эффектом параллакса."""

    def __init__(self, screen, screen_width, screen_height, num_stars_primary_layer=800, num_stars_secondary_layer=400):
        """Инициализирует звездное поле.

        Args:
            screen: Объект экрана Pygame для отрисовки.
            screen_width: Ширина экрана.
            screen_height: Высота экрана.
            num_stars_primary_layer: Количество звезд на основном (более медленном) слое. (Плотность ~0.083% для 1200x800)
            num_stars_secondary_layer: Количество звезд на вторичном (более быстром) слое. (Плотность ~0.042% для 1200x800)
                                     # Общая плотность ~0.125%
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.num_stars_primary_layer = num_stars_primary_layer
        self.num_stars_secondary_layer = num_stars_secondary_layer

        # Параметры звезд
        self.star_size_range = (1, 2)  # Размеры звезд (1-2 пикселя)
        self.star_alpha_range = (153, 230) # Прозрачность (0.6-0.9 в Pygame alpha -> 255 * 0.6 = 153, 255 * 0.9 = 229.5)

        # Скорости прокрутки для слоев параллакса
        self.scroll_speed_primary = 0.2  # Медленная скорость для основного слоя
        self.scroll_speed_secondary = 0.5 # Более быстрая скорость для вторичного слоя

        self.stars_primary = self._generate_stars(self.num_stars_primary_layer)
        self.stars_secondary = self._generate_stars(self.num_stars_secondary_layer)

    def _generate_stars(self, num_stars):
        """Генерирует список звезд со случайными параметрами."""
        stars = []
        for _ in range(num_stars):
            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)
            size = random.randint(self.star_size_range[0], self.star_size_range[1])
            # Alpha component will be handled by the surface's alpha
            base_r = random.randint(200, 255)
            base_g = random.randint(200, 255)
            base_b = random.randint(220, 255) # Slightly bluish white
            alpha = random.randint(self.star_alpha_range[0], self.star_alpha_range[1])

            # Store base color and alpha separately for clarity if needed, though surface alpha is key
            stars.append({
                'x': x,
                'y': y,
                'size': size,
                'base_color': (base_r, base_g, base_b), # Store base color
                'alpha': alpha, # Store alpha
                'surface': None
            })

        # Предварительно создаем поверхности для звезд для лучшей производительности
        for star in stars:
            star_surface = pygame.Surface((star['size'], star['size']), pygame.SRCALPHA)
            # Заливаем поверхность базовым цветом звезды (без альфа-канала в самом цвете fill)
            star_surface.fill(star['base_color'])
            # Устанавливаем общую прозрачность для этой поверхности звезды
            star_surface.set_alpha(star['alpha'])
            star['surface'] = star_surface
        return stars

    def update(self):
        """Обновляет позиции звезд для эффекта прокрутки."""
        self._scroll_stars(self.stars_primary, self.scroll_speed_primary)
        self._scroll_stars(self.stars_secondary, self.scroll_speed_secondary)

    def _scroll_stars(self, stars_list, speed):
        """Прокручивает указанный список звезд."""
        for star in stars_list:
            star['y'] += speed
            # Если звезда уходит за нижний край экрана, переместить ее наверх со случайной X координатой
            if star['y'] > self.screen_height:
                star['y'] = float(random.randint(-star['size'] - 5, 0)) # Появляется сверху, немного за экраном, float для плавной скорости
                star['x'] = random.randint(0, self.screen_width - star['size'])

    def draw(self):
        """Отрисовывает все звезды на экране."""
        # Сначала фон (черный)
        self.screen.fill((0, 0, 0))

        for star in self.stars_primary:
            self.screen.blit(star['surface'], (star['x'], star['y'])) # y может быть float

        for star in self.stars_secondary:
            self.screen.blit(star['surface'], (star['x'], star['y'])) # y может быть float
