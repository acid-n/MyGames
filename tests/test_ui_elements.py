# -*- coding: utf-8 -*-
"""
Тесты для элементов пользовательского интерфейса, таких как Scoreboard.
"""
import unittest
import pygame
import os
from unittest.mock import MagicMock, patch

# Добавляем путь к корневой директории проекта, чтобы можно было импортировать модули игры
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alien_invasion.settings import Settings
from alien_invasion.game_stats import GameStats
from alien_invasion.scoreboard import Scoreboard, _UI_ICON_SIZE, _SCORE_FRAME_PADDING, _LIVES_ICON_SPACING
from alien_invasion.ship import Ship # Нужен для fallback в Scoreboard

# Отключаем звук для тестов, если он инициализируется где-то глобально
os.environ['SDL_AUDIODRIVER'] = 'dummy'

class TestScoreboardUI(unittest.TestCase):
    """Тесты для класса Scoreboard и его UI компонентов."""

    @classmethod
    def setUpClass(cls):
        """Инициализация Pygame и основных объектов для всех тестов класса."""
        pygame.init()
        # Нужен экран для инициализации шрифтов и некоторых других вещей в Pygame
        cls.screen_surface = pygame.display.set_mode((1200, 800))

        cls.settings = Settings()
        # Убедимся, что пути к ассетам корректны для тестового окружения
        # (предполагаем, что тесты запускаются из корневой папки проекта или CI настроен правильно)
        # Если пути относительные, как в проекте, они должны работать.

        # Модифицируем пути к тестовым ассетам, если это необходимо,
        # или убедимся, что основные ассеты доступны.
        # Для сердца и рамки, если они не найдены, Scoreboard должен обрабатывать это корректно.
        # cls.settings.ui_heart_icon_path = "path/to/test_heart.png"
        # cls.settings.ui_score_frame_bg_path = "path/to/test_frame.png"

    def setUp(self):
        """Настройка для каждого теста: создание экземпляров игры, статистики и scoreboard."""
        self.ai_game_mock = MagicMock()
        self.ai_game_mock.screen = self.screen_surface
        self.ai_game_mock.settings = self.settings
        self.stats = GameStats(self.ai_game_mock) # GameStats требует ai_game для settings

        # Mock для корабля, так как Scoreboard может его создавать в fallback для жизней
        # ai_game_mock.ship используется в Bullet, но не напрямую в Scoreboard.
        # Однако, Ship(ai_game) вызывается в Scoreboard.prep_ships (fallback).
        # Поэтому ai_game_mock должен иметь атрибут ship, который является экземпляром Ship или его моком.
        # Чтобы избежать полной инициализации Ship, можно его тоже мокнуть, если он не нужен для теста.
        # Но для простоты, если Ship не делает ничего сложного в __init__ без реальной игры, можно создать.
        # self.ai_game_mock.ship = Ship(self.ai_game_mock) # Это может вызвать проблемы, если Ship сложный
        # Лучше так:
        # self.ai_game_mock.ship = MagicMock(spec=Ship)
        # self.ai_game_mock.ship.rect = pygame.Rect(0,0,50,50) # Пример
        # Но Scoreboard сам создает Ship, так что ai_game_mock должен быть достаточным.

        self.scoreboard = Scoreboard(self.ai_game_mock)


    def test_heart_icon_loaded_and_scaled(self):
        """Тест: Иконка сердца загружена и отмасштабирована."""
        if not os.path.exists(self.settings.ui_heart_icon_path):
            self.assertIsNone(self.scoreboard.heart_icon, "Иконка сердца должна быть None, если файл не найден.")
            self.skipTest(f"Ассет иконки сердца не найден: {self.settings.ui_heart_icon_path}")

        self.assertIsNotNone(self.scoreboard.heart_icon, "Иконка сердца не должна быть None, если файл существует.")
        self.assertIsInstance(self.scoreboard.heart_icon, pygame.Surface, "Иконка сердца должна быть pygame.Surface.")
        self.assertEqual(self.scoreboard.heart_icon.get_size(), _UI_ICON_SIZE, f"Размер иконки сердца должен быть {_UI_ICON_SIZE}.")
        # Проверка альфа-канала (SRCALPHA флаг должен быть установлен после convert_alpha())
        self.assertTrue(self.scoreboard.heart_icon.get_flags() & pygame.SRCALPHA, "Иконка сердца должна иметь альфа-канал (SRCALPHA флаг).")

    def test_lives_display_multiple_icons(self):
        """Тест: Отображение жизней несколькими иконками."""
        self.stats.ships_left = 3
        self.scoreboard.prep_ships() # Переподготовка отображения жизней

        if not self.scoreboard.heart_icon:
             self.skipTest("Иконка сердца не загружена, тест отображения жизней иконками пропускается.")

        self.assertTrue(hasattr(self.scoreboard, 'life_icons_to_draw'), "Scoreboard должен иметь атрибут 'life_icons_to_draw'.")
        self.assertEqual(len(self.scoreboard.life_icons_to_draw), self.stats.ships_left, "Количество иконок жизней должно соответствовать ships_left.")

        if self.stats.ships_left > 0:
            first_icon_rect = self.scoreboard.life_icons_to_draw[0]['rect']
            expected_x = self.settings.lives_display_padding_left
            expected_y = self.settings.lives_display_padding_top
            self.assertEqual(first_icon_rect.left, expected_x, f"Первая иконка жизни должна быть в x={expected_x}.")
            self.assertEqual(first_icon_rect.top, expected_y, f"Первая иконка жизни должна быть в y={expected_y}.")

            if self.stats.ships_left > 1:
                icon1_rect = self.scoreboard.life_icons_to_draw[0]['rect']
                icon2_rect = self.scoreboard.life_icons_to_draw[1]['rect']
                # Проверяем, что вторая иконка смещена вправо относительно первой
                expected_spacing = icon1_rect.width + _LIVES_ICON_SPACING # Используем импортированную константу
                self.assertEqual(icon2_rect.left, icon1_rect.left + expected_spacing,
                                 f"Вторая иконка жизни должна быть смещена на {expected_spacing} пикселей вправо от первой.")
                self.assertEqual(icon1_rect.top, icon2_rect.top, "Иконки жизней должны быть на одном уровне по вертикали.")

    def test_score_frame_preparation(self):
        """Тест: Подготовка рамки для счета и уровня."""
        # Вызываем методы подготовки текста, чтобы rect-ы были созданы
        self.scoreboard.prep_score()
        self.scoreboard.prep_level()
        # Вызываем метод подготовки рамки (теперь он отдельный)
        self.scoreboard._prep_score_frame()

        if not os.path.exists(self.settings.ui_score_frame_bg_path):
            self.assertFalse(self.scoreboard.frame_loaded_successfully, "frame_loaded_successfully должно быть False, если файл рамки не найден.")
            self.skipTest(f"Ассет рамки счета не найден: {self.settings.ui_score_frame_bg_path}")

        self.assertTrue(self.scoreboard.frame_loaded_successfully, "frame_loaded_successfully должно быть True, если рамка загружена.")
        self.assertIsNotNone(self.scoreboard.scaled_score_frame_bg, "Масштабированный фон рамки не должен быть None.")
        self.assertIsNotNone(self.scoreboard.score_frame_rect, "Rect для рамки счета не должен быть None.")

        expected_width = self.scoreboard.score_rect.union(self.scoreboard.level_rect).width + 2 * _SCORE_FRAME_PADDING
        expected_height = self.scoreboard.score_rect.union(self.scoreboard.level_rect).height + 2 * _SCORE_FRAME_PADDING

        self.assertEqual(self.scoreboard.score_frame_rect.width, expected_width, "Ширина рамки счета рассчитана неверно.")
        self.assertEqual(self.scoreboard.score_frame_rect.height, expected_height, "Высота рамки счета рассчитана неверно.")

        combined_text_rect = self.scoreboard.score_rect.union(self.scoreboard.level_rect)
        self.assertEqual(self.scoreboard.score_frame_rect.center, combined_text_rect.center, "Рамка счета должна быть центрирована относительно текстовых блоков.")

    def test_prep_ships_fallback_when_no_heart_icon(self):
        """Тест: prep_ships использует fallback (группу кораблей), если иконка сердца не загружена."""
        # "Повреждаем" путь к иконке, чтобы она не загрузилась
        original_heart_path = self.settings.ui_heart_icon_path
        self.settings.ui_heart_icon_path = "non_existent_path.png"

        # Создаем новый экземпляр Scoreboard, чтобы он попытался загрузить "несуществующую" иконку
        scoreboard_no_icon = Scoreboard(self.ai_game_mock)
        self.settings.ui_heart_icon_path = original_heart_path # Восстанавливаем путь

        self.assertIsNone(scoreboard_no_icon.heart_icon, "Иконка сердца должна быть None, если путь неверный.")

        self.stats.ships_left = 2
        scoreboard_no_icon.prep_ships() # Должен использовать fallback

        self.assertTrue(hasattr(scoreboard_no_icon, 'ships_group_fallback'), "Scoreboard должен иметь атрибут 'ships_group_fallback'.")
        self.assertEqual(len(scoreboard_no_icon.ships_group_fallback), self.stats.ships_left, "Количество кораблей в fallback-группе должно соответствовать ships_left.")
        self.assertIsInstance(scoreboard_no_icon.ships_group_fallback.sprites()[0], Ship, "Элементы в fallback-группе должны быть экземплярами Ship.")

    def test_score_frame_no_overflow_with_large_score(self):
        """Тест: Рамка счета корректно обрамляет текст даже при большом значении счета."""
        if not self.scoreboard.frame_loaded_successfully:
            self.skipTest(f"Ассет рамки счета не найден или не загружен ({self.settings.ui_score_frame_bg_path}), тест переполнения рамки пропускается.")

        self.stats.score = 9999999 # Большой счет
        self.stats.level = 88 # Двузначный уровень для проверки combined_rect
        self.scoreboard.prep_score() # Это вызовет _prep_score_frame внутри
        self.scoreboard.prep_level() # Это также вызовет _prep_score_frame

        score_rect = self.scoreboard.score_rect
        level_rect = self.scoreboard.level_rect
        frame_rect = self.scoreboard.score_frame_rect

        # Проверяем, что рамка существует
        self.assertIsNotNone(frame_rect, "Рамка счета (score_frame_rect) не должна быть None.")

        # 1. Проверяем, что текст счета полностью внутри рамки с учетом верхнего и правого отступов
        # Правый край текста должен быть левее или равен правому краю рамки минус отступ
        self.assertLessEqual(score_rect.right, frame_rect.right - _SCORE_FRAME_PADDING,
                             "Правый край текста счета выходит за рамку или отсутствует правый отступ.")
        # Левый край текста должен быть правее или равен левому краю рамки плюс отступ
        self.assertGreaterEqual(score_rect.left, frame_rect.left + _SCORE_FRAME_PADDING,
                                "Левый край текста счета выходит за рамку или отсутствует левый отступ.")
        # Верхний край текста счета должен быть ниже или равен верхнему краю рамки плюс отступ
        self.assertGreaterEqual(score_rect.top, frame_rect.top + _SCORE_FRAME_PADDING,
                               "Верхний край текста счета выходит за рамку или отсутствует верхний отступ.")

        # 2. Проверяем, что текст уровня полностью внутри рамки с учетом нижнего и правого отступов
        self.assertLessEqual(level_rect.right, frame_rect.right - _SCORE_FRAME_PADDING,
                             "Правый край текста уровня выходит за рамку или отсутствует правый отступ.")
        self.assertGreaterEqual(level_rect.left, frame_rect.left + _SCORE_FRAME_PADDING,
                                "Левый край текста уровня выходит за рамку или отсутствует левый отступ.")
        # Нижний край текста уровня должен быть выше или равен нижнему краю рамки минус отступ
        self.assertLessEqual(level_rect.bottom, frame_rect.bottom - _SCORE_FRAME_PADDING,
                             "Нижний край текста уровня выходит за рамку или отсутствует нижний отступ.")

        # 3. Дополнительная проверка: объединенный rect текста также должен быть внутри
        combined_text_rect = score_rect.union(level_rect)
        self.assertTrue(frame_rect.contains(combined_text_rect),
                        "Объединенный Rect текста счета и уровня должен полностью содержаться в рамке.")

        # 4. Проверка центрирования (как в test_score_frame_preparation)
        self.assertEqual(frame_rect.center, combined_text_rect.center,
                         "Рамка счета должна быть центрирована относительно объединенного текстового блока.")


    @classmethod
    def tearDownClass(cls):
        """Завершение работы Pygame после всех тестов."""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
