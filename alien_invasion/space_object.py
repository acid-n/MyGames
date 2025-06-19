import pygame
import random


class SpaceObject(pygame.sprite.Sprite):
    # Русский комментарий: Класс для представления процедурно появляющихся планет или галактик.
    def __init__(self, screen_width, screen_height, image_path, target_size_ratio_range=(0.08, 0.12), speed=0.01, fade_duration_ms=2000):
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = speed  # Скорость должна быть достаточно медленной для фоновых объектов
        self.fade_duration_ms = fade_duration_ms

        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(
                f"WARNING: Failed to load space object image: {image_path} - {e}. Using fallback.")
            # Создаем простой fallback-объект (например, серый круг)
            fallback_diameter = int(
                screen_width * (target_size_ratio_range[0] + target_size_ratio_range[1]) / 2)
            self.original_image = pygame.Surface(
                (fallback_diameter, fallback_diameter), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (100, 100, 100, 150), (
                fallback_diameter // 2, fallback_diameter // 2), fallback_diameter // 2)

        # Масштабирование изображения
        target_ratio = random.uniform(
            target_size_ratio_range[0], target_size_ratio_range[1])
        self.base_width = int(self.screen_width * target_ratio)
        original_aspect_ratio = self.original_image.get_width() / \
            self.original_image.get_height()
        self.base_height = int(
            self.base_width / original_aspect_ratio) if original_aspect_ratio > 0 else self.base_width

        self.scaled_image = pygame.transform.scale(
            self.original_image, (self.base_width, self.base_height))
        self.image = self.scaled_image.copy()  # image будет изменяться во время fade
        self.rect = self.image.get_rect()

        # Начальная позиция (например, появляется сверху, за экраном, движется вниз)
        self.rect.centerx = random.randint(
            self.rect.width // 2, self.screen_width - self.rect.width // 2)
        self.rect.bottom = 0  # Начинает сверху, за экраном

        self.y = float(self.rect.y)  # Для плавного движения

        # Состояния для fade-in/out
        self.alpha = 0  # Начальная прозрачность (полностью прозрачен)
        self.image.set_alpha(self.alpha)
        self.state = 'fade_in'  # 'fade_in', 'visible', 'fade_out'
        self.creation_time = pygame.time.get_ticks()  # Для fade-in
        self.visible_start_time = 0  # Для отслеживания времени в состоянии 'visible'

    def _update_fade_out(self):  # Вызывается из update, если state == 'fade_out'
        current_time = pygame.time.get_ticks()
        # creation_time сбрасывается при входе в fade_out
        time_elapsed_fade_out = current_time - self.creation_time

        if time_elapsed_fade_out < self.fade_duration_ms:
            self.alpha = int(
                255 * (1 - (time_elapsed_fade_out / self.fade_duration_ms)))
        else:
            self.alpha = 0
            self.kill()  # Удаляем спрайт из всех групп pygame

        # Убедимся, что альфа в пределах 0-255
        self.alpha = min(max(0, self.alpha), 255)
        self.image.set_alpha(self.alpha)

    def update(self):  # Полный метод update
        current_time = pygame.time.get_ticks()

        # Движение
        self.y += self.speed
        self.rect.y = int(self.y)

        if self.state == 'fade_in':
            time_elapsed_fade_in = current_time - self.creation_time
            if time_elapsed_fade_in < self.fade_duration_ms:
                self.alpha = int(
                    255 * (time_elapsed_fade_in / self.fade_duration_ms))
            else:
                self.alpha = 255
                self.state = 'visible'
                self.visible_start_time = current_time  # Запоминаем время входа в 'visible'
            self.alpha = min(max(0, self.alpha), 255)
            self.image.set_alpha(self.alpha)

        elif self.state == 'visible':
            # Условие для начала fade_out: объект прошел 3/4 экрана
            if self.rect.top > self.screen_height * 0.75:
                self.start_fade_out()

        elif self.state == 'fade_out':
            self._update_fade_out()

        # Окончательное удаление, если объект ушел за экран и уже не виден (alpha == 0)
        if self.rect.top > self.screen_height and self.alpha == 0:
            self.kill()

    def start_fade_out(self):
        # Русский комментарий: Инициирует процесс исчезновения объекта.
        if self.state == 'visible':  # Начинаем fade-out только если объект был полностью видим
            self.state = 'fade_out'
            self.creation_time = pygame.time.get_ticks()  # Сбрасываем таймер для fade-out
            # print(f"SpaceObject starting fade_out at y={self.rect.top}") # Для отладки
