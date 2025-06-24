import pygame
import random
import math # Добавлено для math.copysign

# Русский комментарий: Диапазон коэффициентов для размера планет (относительно меньшей стороны экрана)
# Позволяет планетам быть значительно крупнее и частично за экраном.
_TARGET_SIZE_RATIO_RANGE = (0.15, 0.6) # Пример: от 15% до 60% меньшей стороны экрана
# Русский комментарий: Диапазон скоростей для медленного дрейфа (пикселей в кадр)
_DRIFT_SPEED_RANGE = (0.05, 0.20)


class SpaceObject(pygame.sprite.Sprite):
    # Русский комментарий: Класс для представления процедурно появляющихся планет или галактик.
    def __init__(self, screen_width, screen_height, image_path, fade_duration_ms=3000):
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fade_duration_ms = fade_duration_ms

        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(
                f"WARNING: Failed to load space object image: {image_path} - {e}. Using fallback.")
            # Создаем простой fallback-объект (например, серый круг)
            # Используем _TARGET_SIZE_RATIO_RANGE для определения размера fallback
            min_screen_dim = min(screen_width, screen_height)
            fallback_diameter = int(
                min_screen_dim * (_TARGET_SIZE_RATIO_RANGE[0] + _TARGET_SIZE_RATIO_RANGE[1]) / 2)
            self.original_image = pygame.Surface(
                (fallback_diameter, fallback_diameter), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (100, 100, 100, 150), (
                fallback_diameter // 2, fallback_diameter // 2), fallback_diameter // 2)

        # Масштабирование изображения
        # Размер теперь относительно меньшей стороны экрана для лучшей адаптивности
        min_screen_dimension = min(self.screen_width, self.screen_height)
        target_ratio = random.uniform(
            _TARGET_SIZE_RATIO_RANGE[0], _TARGET_SIZE_RATIO_RANGE[1])

        original_aspect_ratio = self.original_image.get_width() / self.original_image.get_height()

        # Масштабируем по одной из сторон, сохраняя пропорции
        if self.original_image.get_width() >= self.original_image.get_height():
            self.base_width = int(min_screen_dimension * target_ratio)
            self.base_height = int(self.base_width / original_aspect_ratio) if original_aspect_ratio > 0 else self.base_width
        else:
            self.base_height = int(min_screen_dimension * target_ratio)
            self.base_width = int(self.base_height * original_aspect_ratio) if original_aspect_ratio > 0 else self.base_height


        self.scaled_image = pygame.transform.scale(
            self.original_image, (self.base_width, self.base_height))
        self.image = self.scaled_image.copy()  # image будет изменяться во время fade
        self.rect = self.image.get_rect()

        # Начальная позиция и направление движения
        self._set_initial_position_and_velocity()

        # Вещественные координаты для плавного движения
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Состояния для fade-in/out
        self.alpha = 0  # Начальная прозрачность (полностью прозрачен)
        self.image.set_alpha(self.alpha)
        self.state = 'fade_in'  # 'fade_in', 'visible', 'fade_out'
        self.creation_time = pygame.time.get_ticks()  # Для fade-in/out
        self.visible_start_time = 0 # Для отслеживания времени в состоянии 'visible' (пока не используется для логики fade_out)


    def _set_initial_position_and_velocity(self):
        """Устанавливает начальную позицию за пределами экрана и случайную диагональную скорость."""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        speed_magnitude = random.uniform(_DRIFT_SPEED_RANGE[0], _DRIFT_SPEED_RANGE[1])

        # Задаем начальные координаты так, чтобы объект был полностью за экраном
        if side == 'top':
            self.rect.centerx = random.randint(0, self.screen_width)
            self.rect.bottom = -self.rect.height // 2 # Половина высоты над экраном
            self.dx = random.uniform(-speed_magnitude, speed_magnitude) # Может двигаться влево или вправо
            self.dy = speed_magnitude # Движется вниз
        elif side == 'bottom':
            self.rect.centerx = random.randint(0, self.screen_width)
            self.rect.top = self.screen_height + self.rect.height // 2
            self.dx = random.uniform(-speed_magnitude, speed_magnitude)
            self.dy = -speed_magnitude # Движется вверх
        elif side == 'left':
            self.rect.right = -self.rect.width // 2
            self.rect.centery = random.randint(0, self.screen_height)
            self.dx = speed_magnitude # Движется вправо
            self.dy = random.uniform(-speed_magnitude, speed_magnitude) # Может двигаться вверх или вниз
        elif side == 'right':
            self.rect.left = self.screen_width + self.rect.width // 2
            self.rect.centery = random.randint(0, self.screen_height)
            self.dx = -speed_magnitude # Движется влево
            self.dy = random.uniform(-speed_magnitude, speed_magnitude)

        # Убедимся, что объект не стоит на месте (хотя с uniform это маловероятно для обоих dx и dy)
        if self.dx == 0 and self.dy == 0:
            self.dx = speed_magnitude if random.choice([True, False]) else -speed_magnitude
            self.dy = speed_magnitude if random.choice([True, False]) else -speed_magnitude
            if self.dx == 0 and self.dy == 0: # Если все еще нули (крайне маловероятно)
                 self.dy = speed_magnitude # Просто двигаем вниз


    def _update_fade_state(self):
        """Обновляет состояние прозрачности (fade-in/out)."""
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.creation_time

        if self.state == 'fade_in':
            if time_elapsed < self.fade_duration_ms:
                self.alpha = int(255 * (time_elapsed / self.fade_duration_ms))
            else:
                self.alpha = 255
                self.state = 'visible'
                # self.visible_start_time = current_time # Можно использовать, если нужна логика нахождения в 'visible'
        elif self.state == 'fade_out':
            # Важно: self.creation_time сбрасывается при вызове start_fade_out()
            if time_elapsed < self.fade_duration_ms:
                self.alpha = int(255 * (1 - (time_elapsed / self.fade_duration_ms)))
            else:
                self.alpha = 0
                # Окончательное удаление произойдет в update, когда объект полностью выйдет за экран

        self.alpha = min(max(0, self.alpha), 255)
        self.image.set_alpha(self.alpha)


    def update(self):
        # Обновление состояния прозрачности
        self._update_fade_state()

        # Движение
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Проверка, не пора ли начать исчезновение (если объект еще не исчезает)
        # Это условие можно усложнить, например, начинать fade_out, когда большая часть объекта покинула экран.
        # Пока оставим простое условие: если объект видим и начинает выходить за любую из границ.
        if self.state == 'visible':
            # Проверяем, если какая-либо часть объекта все еще на экране
            on_screen_horizontally = self.rect.right > 0 and self.rect.left < self.screen_width
            on_screen_vertically = self.rect.bottom > 0 and self.rect.top < self.screen_height

            # Если объект уже не виден на экране (полностью вышел за любую из границ), начинаем fade_out
            # Это условие должно быть более точным, чтобы fade-out начинался, когда он *начинает* выходить.
            # Вместо этого, будем инициировать fade_out, когда объект прошел "достаточно" далеко.
            # Для простоты, если центр объекта вышел за расширенные границы экрана (например, экран + половина размера объекта),
            # то начинаем fade_out. Но это усложнит, проще положиться на условие ниже.

            # Условие для начала fade_out: если объект почти полностью покинул экран.
            # Это условие более надежно, чем проверка на 3/4 экрана, так как движение диагональное.
            # Если правый край левее 0 ИЛИ левый край правее ширины ИЛИ нижний край выше 0 ИЛИ верхний край ниже высоты
            if not self.screen_rect.colliderect(self.rect.inflate(self.rect.width // 2, self.rect.height // 2)):
                 if self.state == 'visible': # Дополнительная проверка, чтобы не вызывать многократно
                    self.start_fade_out()


        # Окончательное удаление, если объект полностью ушел за экран и уже не виден (alpha == 0)
        # Объект считается "ушедшим", если его rect не пересекается с rect экрана, увеличенным на размеры объекта
        # Это гарантирует, что даже большие, частично видимые объекты будут удалены, когда они полностью скроются.
        # Создаем "мертвую зону" вокруг экрана.
        # Увеличиваем область проверки на половину ширины/высоты объекта с каждой стороны,
        # чтобы убедиться, что он полностью скрылся.
        outer_bounds = self.screen_rect.inflate(self.rect.width, self.rect.height)
        if not outer_bounds.colliderect(self.rect) and self.alpha == 0:
            self.kill()


    def start_fade_out(self):
        # Русский комментарий: Инициирует процесс исчезновения объекта.
        if self.state == 'visible':  # Начинаем fade-out только если объект был полностью видим
            self.state = 'fade_out'
            self.creation_time = pygame.time.get_ticks()  # Сбрасываем таймер для fade-out
            # print(f"SpaceObject starting fade_out at ({self.rect.x}, {self.rect.y})") # Для отладки
