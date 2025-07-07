# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock
import pygame
import os

# Добавляем путь к корневому каталогу проекта, чтобы можно было импортировать alien_invasion
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alien_invasion.settings import Settings
from alien_invasion.ship import Ship
from alien_invasion.alien import Alien
from alien_invasion.powerup import PowerUp
from alien_invasion.alien_invasion import (
    AlienInvasion,
    _EXPLOSION_SOUND_INDEX_START,
    _EXPLOSION_SOUND_INDEX_END,
)  # Для инициализации ai_game и констант звуков


class TestAssetScaling(unittest.TestCase):
    """Тесты для проверки корректности масштабирования визуальных ассетов."""

    @classmethod
    def setUpClass(cls):
        """Инициализация Pygame и базовых компонентов для всех тестов."""
        # Попытка инициализировать Pygame с "dummy" видео и аудио драйверами
        # чтобы избежать открытия окна и использования реальной звуковой карты во время тестов.
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()

        # Создаем мок для ai_game, который требуется для инициализации игровых объектов
        cls.ai_game_mock = MagicMock(spec=AlienInvasion)
        cls.ai_game_mock.settings = Settings()
        # Убедимся, что screen существует, даже если это dummy screen
        cls.ai_game_mock.screen = pygame.display.set_mode(
            (
                cls.ai_game_mock.settings.screen_width,
                cls.ai_game_mock.settings.screen_height,
            )
        )
        # Для тестов альфа-канала, нам нужны реальные пути к изображениям, если они существуют
        # или мокать pygame.image.load так, чтобы оно возвращало Surface с альфа-флагом.
        # Проще использовать реальные пути, если они доступны, и обрабатывать их отсутствие.

    # --- Тесты на масштабирование ---
    @patch("pygame.image.load")
    def test_ship_scaling(self, mock_load_image):
        """Тестирует масштабирование корабля."""
        # Мокаем pygame.image.load для возврата Surface с известными исходными размерами
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.get_rect.return_value = pygame.Rect(
            0, 0, 100, 100
        )  # Исходный размер 100x100
        mock_surface.get_size.return_value = (100, 100)  # Для _create_shielded_image
        mock_surface.convert_alpha.return_value = mock_surface
        mock_surface.copy.return_value = (
            mock_surface  # Для _create_shielded_image и др.
        )

        # Создаем мок для конечного (масштабированного) изображения
        scaled_surface_mock = MagicMock(spec=pygame.Surface)
        scaled_surface_mock.get_rect.return_value = pygame.Rect(
            0,
            0,
            self.ai_game_mock.settings.ship_display_width,
            self.ai_game_mock.settings.ship_display_height,
        )
        scaled_surface_mock.get_size.return_value = (  # get_size для scaled surface
            self.ai_game_mock.settings.ship_display_width,
            self.ai_game_mock.settings.ship_display_height,
        )
        scaled_surface_mock.convert_alpha.return_value = scaled_surface_mock
        scaled_surface_mock.copy.return_value = (
            scaled_surface_mock  # Если копия берется от масштабированного
        )
        scaled_surface_mock.blit.return_value = (
            None  # Мок для blit в _create_shielded_image
        )

        # Мокаем scale так, чтобы он возвращал наш scaled_surface_mock
        mock_transform_scale = MagicMock(return_value=scaled_surface_mock)

        # Применяем мок к pygame.transform.scale
        with patch("pygame.transform.scale", mock_transform_scale):
            mock_load_image.return_value = mock_surface

            ship = Ship(self.ai_game_mock)

            # Проверяем, что pygame.transform.scale был вызван с правильными размерами для исходного изображения
            mock_transform_scale.assert_any_call(
                mock_surface,  # Исходный mock_surface
                (
                    self.ai_game_mock.settings.ship_display_width,
                    self.ai_game_mock.settings.ship_display_height,
                ),
            )
            # Фактический размер rect корабля должен соответствовать настройкам
            self.assertEqual(
                ship.rect.width, self.ai_game_mock.settings.ship_display_width
            )
            self.assertEqual(
                ship.rect.height, self.ai_game_mock.settings.ship_display_height
            )

    @patch("pygame.image.load")
    def test_alien_scaling(self, mock_load_image):
        """Тестирует масштабирование пришельца."""
        mock_surface = MagicMock(spec=pygame.Surface)
        initial_width, initial_height = 120, 120
        mock_surface.get_rect.return_value = pygame.Rect(
            0, 0, initial_width, initial_height
        )
        mock_surface.convert_alpha.return_value = mock_surface
        mock_surface.get_width.return_value = (
            initial_width  # Для условия в _apply_tint до масштабирования
        )
        mock_surface.get_height.return_value = (
            initial_height  # Для условия в _apply_tint до масштабирования
        )
        mock_surface.get_size.return_value = (
            initial_width,
            initial_height,
        )  # Для _apply_tint
        mock_surface.blit.return_value = None  # Мок для blit в _apply_tint

        scaled_width = self.ai_game_mock.settings.alien_display_width
        scaled_height = self.ai_game_mock.settings.alien_display_height

        scaled_surface_mock = MagicMock(spec=pygame.Surface)
        scaled_surface_mock.get_rect.return_value = pygame.Rect(
            0, 0, scaled_width, scaled_height
        )
        scaled_surface_mock.get_size.return_value = (scaled_width, scaled_height)
        scaled_surface_mock.get_width.return_value = scaled_width
        scaled_surface_mock.get_height.return_value = scaled_height
        scaled_surface_mock.convert_alpha.return_value = scaled_surface_mock
        scaled_surface_mock.blit.return_value = None

        mock_transform_scale = MagicMock(return_value=scaled_surface_mock)

        with patch("pygame.transform.scale", mock_transform_scale):
            mock_load_image.return_value = mock_surface

            alien = Alien(self.ai_game_mock)

            mock_transform_scale.assert_any_call(
                mock_surface, (scaled_width, scaled_height)
            )
            self.assertEqual(alien.rect.width, scaled_width)
            self.assertEqual(alien.rect.height, scaled_height)

    @patch("pygame.image.load")
    def test_powerup_scaling(self, mock_load_image):
        """Тестирует масштабирование бонуса."""
        mock_surface = MagicMock(spec=pygame.Surface)
        initial_width, initial_height = 80, 80
        mock_surface.get_rect.return_value = pygame.Rect(
            0, 0, initial_width, initial_height
        )
        mock_surface.convert_alpha.return_value = mock_surface
        # get_size не используется напрямую в PowerUp при успешной загрузке, но лучше добавить для полноты
        mock_surface.get_size.return_value = (initial_width, initial_height)

        scaled_width = self.ai_game_mock.settings.powerup_display_width
        scaled_height = self.ai_game_mock.settings.powerup_display_height

        scaled_surface_mock = MagicMock(spec=pygame.Surface)
        scaled_surface_mock.get_rect.return_value = pygame.Rect(
            0, 0, scaled_width, scaled_height
        )
        scaled_surface_mock.convert_alpha.return_value = scaled_surface_mock
        # get_size для scaled_surface_mock не обязателен, если он не передается дальше
        # но для консистентности:
        scaled_surface_mock.get_size.return_value = (scaled_width, scaled_height)

        mock_transform_scale = MagicMock(return_value=scaled_surface_mock)

        with patch("pygame.transform.scale", mock_transform_scale):
            mock_load_image.return_value = mock_surface

            # Тестируем для типа 'shield', пути к изображениям и fallback цвета определены
            powerup = PowerUp(self.ai_game_mock, "shield", (100, 100))

            mock_transform_scale.assert_any_call(
                mock_surface, (scaled_width, scaled_height)
            )
            self.assertEqual(powerup.rect.width, scaled_width)
            self.assertEqual(powerup.rect.height, scaled_height)

    @patch("pygame.image.load")
    def test_powerup_fallback_scaling(self, mock_load_image):
        """Тестирует масштабирование бонуса при fallback (ошибка загрузки изображения)."""
        # Мокаем pygame.image.load так, чтобы он вызывал ошибку
        mock_load_image.side_effect = pygame.error("Test error loading image")

        # Нужен мок для pygame.Surface, так как он будет создан внутри PowerUp
        mock_fallback_surface = MagicMock(spec=pygame.Surface)
        mock_fallback_surface.get_rect.return_value = pygame.Rect(
            0,
            0,
            self.ai_game_mock.settings.powerup_display_width,
            self.ai_game_mock.settings.powerup_display_height,
        )

        # Мокаем pygame.Surface() для возврата нашего мока
        with patch(
            "pygame.Surface", return_value=mock_fallback_surface
        ) as mock_surface_constructor:
            powerup = PowerUp(self.ai_game_mock, "shield", (100, 100))

            # Проверяем, что pygame.Surface был вызван с правильными размерами для fallback
            mock_surface_constructor.assert_called_with(
                (
                    self.ai_game_mock.settings.powerup_display_width,
                    self.ai_game_mock.settings.powerup_display_height,
                )
            )
            # Масштабирование pygame.transform.scale не должно вызываться для fallback surface,
            # так как она уже создается нужного размера.

            self.assertEqual(
                powerup.rect.width, self.ai_game_mock.settings.powerup_display_width
            )
            self.assertEqual(
                powerup.rect.height, self.ai_game_mock.settings.powerup_display_height
            )

    # --- Тесты на альфа-канал ---

    def test_ship_image_alpha_channel(self):
        """Тест: Изображение корабля загружается с альфа-каналом."""
        if not os.path.exists(self.ai_game_mock.settings.ship_image_path):
            self.skipTest(
                f"Ассет корабля не найден: {self.ai_game_mock.settings.ship_image_path}"
            )

        # Создаем реальный объект Ship, чтобы проверить загрузку изображения
        ship = Ship(self.ai_game_mock)
        self.assertIsNotNone(ship.image, "Изображение корабля не должно быть None.")
        # convert_alpha() должен установить флаг SRCALPHA
        self.assertTrue(
            ship.image.get_flags() & pygame.SRCALPHA,
            "Изображение корабля должно иметь флаг SRCALPHA после convert_alpha().",
        )

    def test_alien_image_alpha_channel(self):
        """Тест: Изображение пришельца загружается с альфа-каналом."""
        if not self.ai_game_mock.settings.alien_sprite_paths:
            self.skipTest("Список путей к спрайтам пришельцев пуст.")

        alien_image_path = self.ai_game_mock.settings.alien_sprite_paths[0]
        if not os.path.exists(alien_image_path):
            self.skipTest(f"Ассет пришельца не найден: {alien_image_path}")

        alien = Alien(self.ai_game_mock, specific_image_path=alien_image_path)
        self.assertIsNotNone(alien.image, "Изображение пришельца не должно быть None.")
        self.assertTrue(
            alien.image.get_flags() & pygame.SRCALPHA,
            "Изображение пришельца должно иметь флаг SRCALPHA после convert_alpha().",
        )

    def test_powerup_image_alpha_channel(self):
        """Тест: Изображение бонуса загружается с альфа-каналом."""
        # Тестируем для типа 'shield'
        powerup_image_path = self.ai_game_mock.settings.powerup_shield_image_path
        if not os.path.exists(powerup_image_path):
            self.skipTest(f"Ассет бонуса 'shield' не найден: {powerup_image_path}")

        powerup = PowerUp(self.ai_game_mock, "shield", (100, 100))
        self.assertIsNotNone(powerup.image, "Изображение бонуса не должно быть None.")

        # Если изображение было загружено (не fallback), оно должно иметь альфа-канал
        # Fallback Surface создается без SRCALPHA по умолчанию, если не указать pygame.SRCALPHA при создании.
        # В коде PowerUp fallback создается как `pygame.Surface(target_size)`, что не добавляет SRCALPHA.
        # Это ожидаемое поведение для fallback. Тест проверяет именно загруженное изображение.
        # Мы можем проверить, что это не fallback, сравнив с цветом fallback, но это сложнее.
        # Проще проверить флаг, если мы уверены, что файл существует и загрузился.
        # (Данный тест предполагает, что файл существует и был успешно загружен, иначе skipTest).
        self.assertTrue(
            powerup.image.get_flags() & pygame.SRCALPHA,
            "Загруженное изображение бонуса должно иметь флаг SRCALPHA.",
        )

    @classmethod
    def tearDownClass(cls):
        """Завершение работы Pygame после всех тестов."""
        pygame.quit()


class TestSoundAssets(unittest.TestCase):
    """Тесты для проверки корректной загрузки звуковых ассетов."""

    @classmethod
    def setUpClass(cls):
        """Инициализация Pygame.mixer и Settings."""
        os.environ["SDL_AUDIODRIVER"] = "dummy"  # Убедимся, что аудиодрайвер dummy
        pygame.mixer.pre_init(44100, -16, 2, 512)  # Параметры для dummy
        pygame.init()  # Pygame.init() также инициализирует mixer, если он не был инициализирован

        # Проверим, инициализирован ли микшер, если нет - инициализируем явно
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error as e:
                # Если и тут не удалось, возможно, тесты звука не смогут пройти
                print(f"Не удалось инициализировать pygame.mixer в setUpClass: {e}")
                # Можно установить флаг, чтобы пропускать тесты, или позволить им упасть
                cls.mixer_initialized = False
            else:
                cls.mixer_initialized = True
        else:
            cls.mixer_initialized = True

        cls.settings = Settings()

    def setUp(self):
        """Пропускаем тест, если микшер не инициализирован."""
        if not self.mixer_initialized:
            self.skipTest("Pygame mixer не был успешно инициализирован.")

    def _check_sound_loaded(self, sound_path, sound_attribute_name=""):
        """Вспомогательный метод для проверки загрузки одного звукового файла."""
        if not os.path.exists(sound_path):
            self.skipTest(f"Звуковой файл не найден: {sound_path}")

        sound = None
        try:
            sound = pygame.mixer.Sound(sound_path)
        except pygame.error as e:
            self.fail(f"Ошибка загрузки звука '{sound_path}': {e}")

        self.assertIsNotNone(
            sound, f"Звук '{sound_path}' не должен быть None после загрузки."
        )
        self.assertIsInstance(
            sound,
            pygame.mixer.Sound,
            f"Объект для '{sound_path}' должен быть pygame.mixer.Sound.",
        )
        # Можно добавить проверку длительности, если она известна и важна
        # self.assertGreater(sound.get_length(), 0, f"Длительность звука '{sound_path}' должна быть больше 0.")

    def test_load_laser_sound(self):
        """Тест: Загрузка звука лазера."""
        self._check_sound_loaded(self.settings.sound_laser_path, "Laser Sound")

    def test_load_explosion_sounds(self):
        """Тест: Загрузка звуков взрыва (согласно измененной логике)."""
        sound_paths_to_test = []
        for i in range(_EXPLOSION_SOUND_INDEX_START, _EXPLOSION_SOUND_INDEX_END + 1):
            path = self.settings.sound_explosion_pattern.format(i)
            sound_paths_to_test.append(path)

        if not sound_paths_to_test:
            self.skipTest(
                "Нет путей для звуков взрыва для тестирования (возможно, из-за _EXPLOSION_SOUND_INDEX)."
            )

        for path in sound_paths_to_test:
            self._check_sound_loaded(path, f"Explosion Sound {path}")

    def test_load_powerup_sound(self):
        """Тест: Загрузка звука подбора бонуса."""
        self._check_sound_loaded(self.settings.sound_powerup_path, "Powerup Sound")

    def test_load_shield_recharge_sound(self):
        """Тест: Загрузка звука перезарядки щита."""
        self._check_sound_loaded(
            self.settings.sound_shield_recharge_path, "Shield Recharge Sound"
        )

    # Тест для фоновой музыки может быть добавлен аналогично, если используется pygame.mixer.music
    # def test_load_background_music(self):
    #     """Тест: Загрузка фоновой музыки."""
    #     music_path = self.settings.music_background_path
    #     if not os.path.exists(music_path):
    #         self.skipTest(f"Файл фоновой музыки не найден: {music_path}")
    #     try:
    #         pygame.mixer.music.load(music_path)
    #         # pygame.mixer.music.unload() # Освобождаем, если нужно
    #     except pygame.error as e:
    #         self.fail(f"Ошибка загрузки фоновой музыки '{music_path}': {e}")

    @classmethod
    def tearDownClass(cls):
        """Завершение работы Pygame.mixer и Pygame после всех тестов."""
        if pygame.mixer.get_init():  # Проверяем, был ли микшер инициализирован
            pygame.mixer.quit()
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
