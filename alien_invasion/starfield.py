import pygame
import random


class Starfield:
    # Русский комментарий: Класс для создания и управления эффектом звездного неба с параллаксом.
    def __init__(self, screen, screen_width, screen_height, num_stars_per_layer=150):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.num_stars_per_layer = num_stars_per_layer

        # Русский комментарий: Определение слоев. Каждый слой: (speed, color, size_range)
        self.layers_config = [
            {'speed': 0.05, 'color': (100, 100, 100), 'size_range': (
                # Дальний слой (медленный, тусклый, мелкий)
                1, 1), 'num_stars': self.num_stars_per_layer // 2},
            {'speed': 0.10, 'color': (180, 180, 180), 'size_range': (
                # Средний слой (быстрее, ярче, чуть крупнее)
                1, 2), 'num_stars': self.num_stars_per_layer}
        ]

        self.layers = []
        for config in self.layers_config:
            stars = []
            for _ in range(config['num_stars']):
                x = random.randrange(0, self.screen_width)
                y = random.randrange(0, self.screen_height)
                size = random.randint(
                    config['size_range'][0], config['size_range'][1])
                # Русский комментарий: Добавляем исходную y-координату для сброса при выходе за экран
                stars.append({'x': x, 'y': y, 'initial_y': y, 'size': size,
                             'speed': config['speed'], 'color': config['color']})
            self.layers.append(stars)

    def update(self):
        # Русский комментарий: Обновляет позицию каждой звезды в каждом слое.
        for layer_idx, stars_in_layer in enumerate(self.layers):
            # Correctly get speed from config
            layer_speed = self.layers_config[layer_idx]['speed']
            for star in stars_in_layer:
                star['y'] += layer_speed  # Use layer_speed here
                # Русский комментарий: Если звезда ушла за нижний край, переносим ее наверх со случайной X координатой.
                if star['y'] > self.screen_height:
                    star['y'] = 0  # Появляется сверху
                    star['x'] = random.randrange(0, self.screen_width)

    def draw(self):
        # Русский комментарий: Отрисовывает все звезды всех слоев.
        self.screen.fill((0, 0, 0))  # Черный фон космоса
        for stars_in_layer in self.layers:
            for star in stars_in_layer:
                # Звезды рисуются как маленькие прямоугольники или круги
                # pygame.draw.rect(self.screen, star['color'], (star['x'], star['y'], star['size'], star['size']))
                # Для более "звездного" вида можно использовать круги или просто пиксели, если размер 1
                if star['size'] == 1:
                    self.screen.set_at(
                        (int(star['x']), int(star['y'])), star['color'])
                else:
                    pygame.draw.circle(self.screen, star['color'], (int(
                        star['x']), int(star['y'])), star['size'])
