import pygame
from pygame.sprite import Sprite
import sys


class Ship(Sprite):
    """Класс для управления кораблем"""

    def __init__(self, ai_game):
        # Русский комментарий: Инициализирует корабль и задает его начальную позицию.
        super().__init__()  # Для поддержки наследования от Sprite, если оно есть или будет
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Загрузка изображения корабля и получение его rect
        try:
            self.original_image = pygame.image.load(
                self.settings.ship_image_path).convert_alpha()
        except pygame.error as e:
            print(
                f"Не удалось загрузить спрайт корабля: {self.settings.ship_image_path} - {e}")
            # Загружаем простой прямоугольник как fallback
            self.original_image = pygame.Surface([64, 64])
            self.original_image.fill((0, 0, 255))  # Синий прямоугольник

        self.original_image = pygame.transform.scale(
            self.original_image, (64, 64))

        # Создаем варианты спрайта
        self.image_normal = self.original_image
        self.image_shielded = self._create_shielded_image(self.original_image)
        # Может быть таким же, как normal, если нет спецэффекта
        self.image_double_fire = self._create_double_fire_image(
            self.original_image)

        self.image = self.image_normal  # Текущее изображение корабля
        self.rect = self.image.get_rect()

        # Каждый новый корабль появляется у нижнего края экрана.
        self.rect.midbottom = self.screen_rect.midbottom

        # Сохранение вещественной координаты центра корабля
        self.x = float(self.rect.x)

        # Флаги перемещения
        self.moving_right = False
        self.moving_left = False

        # Состояния для визуальных эффектов
        self.shield_active = False
        self.shield_activation_time = 0
        self.double_fire_active = False
        self.double_fire_activation_time = 0

    def update(self):
        """Обновляет позицию корабля с учетом флагов"""
        self._check_effects_duration()

        # Обновляется атрибут х, не rect
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Обновление атрибута rect на основании self.x
        self.rect.x = self.x

        # Русский комментарий: Обновление визуального состояния корабля
        self.update_visual_state()

    def blitme(self):
        """Рисует корабль в текущей позиции, используя актуальный спрайт (self.image),
        который может меняться в зависимости от активных эффектов (щит, двойной выстрел)."""
        self.screen.blit(self.image, self.rect)
        # Старая отрисовка щита как отдельного прямоугольника удалена,
        # так как теперь щит - это вариант спрайта self.image_shielded.

    def center_ship(self):
        """Размещает корабль в центре нижней стороны"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def _create_shielded_image(self, base_image):
        # Русский комментарий: Создает вариант изображения с эффектом щита.
        shielded_img = base_image.copy()
        # Простой эффект: рисуем синий полупрозрачный круг вокруг корабля или меняем цвет контура.
        # Для примера, наложим полупрозрачный синий цвет на все изображение.
        overlay = pygame.Surface(shielded_img.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 100, 255, 90))  # Ярко-синий, ~35% прозрачности.
        shielded_img.blit(overlay, (0, 0))
        # Альтернативный вариант с контуром (закомментирован, так как выбран overlay.fill):
        # pygame.draw.rect(shielded_img, self.settings.ship_shield_outline_color, shielded_img.get_rect(), 2)
        return shielded_img

    def _create_double_fire_image(self, base_image):
        # Русский комментарий: Создает вариант изображения для режима двойного выстрела.
        # В текущей реализации визуальных отличий для режима двойного выстрела нет,
        # поэтому просто возвращается копия базового изображения.
        # При необходимости сюда можно добавить код для изменения спрайта (например, эффект пламени из орудий).
        double_fire_img = base_image.copy()
        # Пример закомментированного кода для добавления визуального эффекта (оранжевые точки на орудиях):
        # if "playerShip3_blue.png" in self.settings.ship_image_path: # Проверка на конкретный спрайт
        #     pygame.draw.circle(double_fire_img, (255, 165, 0), (15, 10), 3) # Левое "орудие"
        #     pygame.draw.circle(double_fire_img, (255, 165, 0), (double_fire_img.get_width() - 15, 10), 3) # Правое "орудие"
        return double_fire_img

    def update_visual_state(self):
        # Русский комментарий: Обновляет изображение корабля в зависимости от активных эффектов.
        if self.shield_active:
            self.image = self.image_shielded
        elif self.double_fire_active:  # Двойной выстрел менее приоритетен, чем щит визуально
            self.image = self.image_double_fire
        else:
            self.image = self.image_normal

    def activate_shield(self):
        # Русский комментарий: Активирует щит.
        self.shield_active = True
        self.shield_activation_time = pygame.time.get_ticks()
        print("Щит активирован на корабле")  # Для отладки

    def activate_double_fire(self):
        # Русский комментарий: Активирует двойной выстрел.
        self.double_fire_active = True
        self.double_fire_activation_time = pygame.time.get_ticks()
        print("Двойной выстрел активирован на корабле")  # Для отладки

    def _check_effects_duration(self):
        # Русский комментарий: Проверяет длительность активных эффектов.
        current_time = pygame.time.get_ticks()
        if self.shield_active and current_time - self.shield_activation_time > self.settings.shield_duration:
            self.shield_active = False
            print("Щит деактивирован (время вышло)")  # Для отладки

        if self.double_fire_active and current_time - self.double_fire_activation_time > self.settings.double_fire_duration:
            self.double_fire_active = False
            print("Двойной выстрел деактивирован (время вышло)")  # Для отладки
