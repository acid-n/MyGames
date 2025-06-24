# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock
import pygame
import os

# Добавляем путь к корневому каталогу проекта, чтобы можно было импортировать alien_invasion
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alien_invasion.settings import Settings
from alien_invasion.ship import Ship
from alien_invasion.alien import Alien
from alien_invasion.powerup import PowerUp
from alien_invasion.alien_invasion import AlienInvasion # Для инициализации ai_game


class TestAssetScaling(unittest.TestCase):
    """Тесты для проверки корректности масштабирования визуальных ассетов."""

    @classmethod
    def setUpClass(cls):
        """Инициализация Pygame и базовых компонентов для всех тестов."""
        # Попытка инициализировать Pygame с "dummy" видео и аудио драйверами
        # чтобы избежать открытия окна и использования реальной звуковой карты во время тестов.
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        pygame.init()

        # Создаем мок для ai_game, который требуется для инициализации игровых объектов
        cls.ai_game_mock = MagicMock(spec=AlienInvasion)
        cls.ai_game_mock.settings = Settings()
        # Убедимся, что screen существует, даже если это dummy screen
        cls.ai_game_mock.screen = pygame.display.set_mode((
            cls.ai_game_mock.settings.screen_width,
            cls.ai_game_mock.settings.screen_height
        ))


    @patch('pygame.image.load')
    def test_ship_scaling(self, mock_load_image):
        """Тестирует масштабирование корабля."""
        # Мокаем pygame.image.load для возврата Surface с известными исходными размерами
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, 100, 100) # Исходный размер 100x100
        mock_surface.get_size.return_value = (100, 100) # Для _create_shielded_image
        mock_surface.convert_alpha.return_value = mock_surface
        mock_surface.copy.return_value = mock_surface # Для _create_shielded_image и др.

        # Создаем мок для конечного (масштабированного) изображения
        scaled_surface_mock = MagicMock(spec=pygame.Surface)
        scaled_surface_mock.get_rect.return_value = pygame.Rect(
            0, 0,
            self.ai_game_mock.settings.ship_display_width,
            self.ai_game_mock.settings.ship_display_height
        )
        scaled_surface_mock.get_size.return_value = ( # get_size для scaled surface
            self.ai_game_mock.settings.ship_display_width,
            self.ai_game_mock.settings.ship_display_height
        )
        scaled_surface_mock.convert_alpha.return_value = scaled_surface_mock
        scaled_surface_mock.copy.return_value = scaled_surface_mock # Если копия берется от масштабированного
        scaled_surface_mock.blit.return_value = None # Мок для blit в _create_shielded_image

        # Мокаем scale так, чтобы он возвращал наш scaled_surface_mock
        mock_transform_scale = MagicMock(return_value=scaled_surface_mock)

        # Применяем мок к pygame.transform.scale
        with patch('pygame.transform.scale', mock_transform_scale):
            mock_load_image.return_value = mock_surface

            ship = Ship(self.ai_game_mock)

            # Проверяем, что pygame.transform.scale был вызван с правильными размерами для исходного изображения
            mock_transform_scale.assert_any_call(
                mock_surface, # Исходный mock_surface
                (self.ai_game_mock.settings.ship_display_width, self.ai_game_mock.settings.ship_display_height)
            )
            # Фактический размер rect корабля должен соответствовать настройкам
            self.assertEqual(ship.rect.width, self.ai_game_mock.settings.ship_display_width)
            self.assertEqual(ship.rect.height, self.ai_game_mock.settings.ship_display_height)

    @patch('pygame.image.load')
    def test_alien_scaling(self, mock_load_image):
        """Тестирует масштабирование пришельца."""
        mock_surface = MagicMock(spec=pygame.Surface)
        initial_width, initial_height = 120, 120
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, initial_width, initial_height)
        mock_surface.convert_alpha.return_value = mock_surface
        mock_surface.get_width.return_value = initial_width # Для условия в _apply_tint до масштабирования
        mock_surface.get_height.return_value = initial_height # Для условия в _apply_tint до масштабирования
        mock_surface.get_size.return_value = (initial_width, initial_height) # Для _apply_tint
        mock_surface.blit.return_value = None # Мок для blit в _apply_tint

        scaled_width = self.ai_game_mock.settings.alien_display_width
        scaled_height = self.ai_game_mock.settings.alien_display_height

        scaled_surface_mock = MagicMock(spec=pygame.Surface)
        scaled_surface_mock.get_rect.return_value = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_surface_mock.get_size.return_value = (scaled_width, scaled_height)
        scaled_surface_mock.get_width.return_value = scaled_width
        scaled_surface_mock.get_height.return_value = scaled_height
        scaled_surface_mock.convert_alpha.return_value = scaled_surface_mock
        scaled_surface_mock.blit.return_value = None

        mock_transform_scale = MagicMock(return_value=scaled_surface_mock)

        with patch('pygame.transform.scale', mock_transform_scale):
            mock_load_image.return_value = mock_surface

            alien = Alien(self.ai_game_mock)

            mock_transform_scale.assert_any_call(
                mock_surface,
                (scaled_width, scaled_height)
            )
            self.assertEqual(alien.rect.width, scaled_width)
            self.assertEqual(alien.rect.height, scaled_height)

    @patch('pygame.image.load')
    def test_powerup_scaling(self, mock_load_image):
        """Тестирует масштабирование бонуса."""
        mock_surface = MagicMock(spec=pygame.Surface)
        initial_width, initial_height = 80, 80
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, initial_width, initial_height)
        mock_surface.convert_alpha.return_value = mock_surface
        # get_size не используется напрямую в PowerUp при успешной загрузке, но лучше добавить для полноты
        mock_surface.get_size.return_value = (initial_width, initial_height)


        scaled_width = self.ai_game_mock.settings.powerup_display_width
        scaled_height = self.ai_game_mock.settings.powerup_display_height

        scaled_surface_mock = MagicMock(spec=pygame.Surface)
        scaled_surface_mock.get_rect.return_value = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_surface_mock.convert_alpha.return_value = scaled_surface_mock
        # get_size для scaled_surface_mock не обязателен, если он не передается дальше
        # но для консистентности:
        scaled_surface_mock.get_size.return_value = (scaled_width, scaled_height)


        mock_transform_scale = MagicMock(return_value=scaled_surface_mock)

        with patch('pygame.transform.scale', mock_transform_scale):
            mock_load_image.return_value = mock_surface

            # Тестируем для типа 'shield', пути к изображениям и fallback цвета определены
            powerup = PowerUp(self.ai_game_mock, 'shield', (100, 100))

            mock_transform_scale.assert_any_call(
                mock_surface,
                (scaled_width, scaled_height)
            )
            self.assertEqual(powerup.rect.width, scaled_width)
            self.assertEqual(powerup.rect.height, scaled_height)

    @patch('pygame.image.load')
    def test_powerup_fallback_scaling(self, mock_load_image):
        """Тестирует масштабирование бонуса при fallback (ошибка загрузки изображения)."""
        # Мокаем pygame.image.load так, чтобы он вызывал ошибку
        mock_load_image.side_effect = pygame.error("Test error loading image")

        # Нужен мок для pygame.Surface, так как он будет создан внутри PowerUp
        mock_fallback_surface = MagicMock(spec=pygame.Surface)
        mock_fallback_surface.get_rect.return_value = pygame.Rect(
            0, 0,
            self.ai_game_mock.settings.powerup_display_width,
            self.ai_game_mock.settings.powerup_display_height
        )

        # Мокаем pygame.Surface() для возврата нашего мока
        with patch('pygame.Surface', return_value=mock_fallback_surface) as mock_surface_constructor:
            powerup = PowerUp(self.ai_game_mock, 'shield', (100, 100))

            # Проверяем, что pygame.Surface был вызван с правильными размерами для fallback
            mock_surface_constructor.assert_called_with(
                (self.ai_game_mock.settings.powerup_display_width, self.ai_game_mock.settings.powerup_display_height)
            )
            # Масштабирование pygame.transform.scale не должно вызываться для fallback surface,
            # так как она уже создается нужного размера.

            self.assertEqual(powerup.rect.width, self.ai_game_mock.settings.powerup_display_width)
            self.assertEqual(powerup.rect.height, self.ai_game_mock.settings.powerup_display_height)


    @classmethod
    def tearDownClass(cls):
        """Завершение работы Pygame после всех тестов."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
