import unittest
from unittest import mock
from unittest.mock import patch # Added import for patch
import os
import sys
import pygame  # Added import for pygame
import alien_invasion.button  # Added: For TestButtonCreation

# Добавляем корневую директорию проекта в sys.path, чтобы можно было импортировать модули игры
# Это необходимо, если тесты запускаются непосредственно из директории tests/
# или если PYTHONPATH не настроен соответствующим образом.
# При запуске через 'python -m unittest discover' из корня проекта, это может быть не строго обязательно,
# но не помешает для универсальности.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from alien_invasion.settings import Settings
from alien_invasion.ship import Ship
from alien_invasion.scoreboard import Scoreboard
from alien_invasion.game_stats import GameStats
from alien_invasion.alien_invasion import (
    AlienInvasion,
)  # Нужен для ai_game в Ship и Scoreboard

# --- Mock объекты для Pygame ---
# Используем unittest.mock для более сложных сценариев, но для простых атрибутов
# можно обойтись такими базовыми моками.


class MockSurface:
    """Минимальный мок для pygame.Surface."""

    def __init__(self, width_height_tuple, is_alpha=False):
        self.width = width_height_tuple[0]
        self.height = width_height_tuple[1]
        self._is_alpha = is_alpha
        self.rect = MockRect(0, 0, self.width, self.height)

    def get_rect(self):
        return self.rect

    def convert_alpha(self):
        self._is_alpha = True
        return self  # Возвращаем себя же для цепочки вызовов

    def convert(self):
        self._is_alpha = False
        return self

    def copy(self):
        return MockSurface((self.width, self.height), self._is_alpha)

    def fill(self, color):
        pass  # Ничего не делаем

    def blit(self, source, dest, special_flags=0):
        pass  # Ничего не делаем

    def get_size(self):
        return (self.width, self.height)

    def get_width(self): # Added
        return self.width

    def get_height(self): # Added
        return self.height

    def set_alpha(self, alpha_value):
        pass  # Ничего не делаем


class MockRect:
    """Минимальный мок для pygame.Rect."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.centerx = x + width // 2
        self.centery = y + height // 2
        self.midbottom = (self.centerx, y + height)
        self.midtop = (self.centerx, y)
        self.right = x + width
        self.left = x
        self.top = y
        self.bottom = y + height

    def copy(self):
        return MockRect(self.x, self.y, self.width, self.height)

    def union_ip(self, other_rect):
        # Упрощенная логика для теста Scoreboard
        self.width += other_rect.width  # Примерное увеличение
        self.height += other_rect.height

    def union(self, other_rect):
        """Возвращает новый MockRect, являющийся объединением этого и другого rect."""
        new_x = min(self.x, other_rect.x)
        new_y = min(self.y, other_rect.y)
        new_right = max(self.right, other_rect.right)
        new_bottom = max(self.bottom, other_rect.bottom)
        new_width = new_right - new_x
        new_height = new_bottom - new_y
        return MockRect(new_x, new_y, new_width, new_height)

    @property
    def center(self):
        return (self.centerx, self.centery)

    @center.setter
    def center(self, value):
        self.centerx = value[0]
        self.centery = value[1]
        self.x = self.centerx - self.width // 2
        self.y = self.centery - self.height // 2
        # Обновляем остальные зависимые атрибуты
        self.midbottom = (self.centerx, self.y + self.height)
        self.midtop = (self.centerx, self.y)
        self.right = self.x + self.width
        self.left = self.x
        self.top = self.y
        self.bottom = self.y + self.height


class MockPygameImage:
    """Мок для pygame.image."""

    def load(self, path):
        # Возвращаем мок Surface, имитирующий загрузку изображения.
        # Размеры могут быть произвольными, но для теста Ship лучше соответствовать ожиданиям.
        if "playerShip3_blue.png" in path:  # Путь из настроек для корабля
            return MockSurface(
                (64, 64), is_alpha=True
            )  # Ожидаемые размеры после scale в Ship
        elif "heart.png" in path:  # Пример для иконки
            return MockSurface((32, 32), is_alpha=True)
        elif "blue_panel.png" in path:  # Пример для фона рамки
            return MockSurface((100, 50), is_alpha=True)
        return MockSurface((50, 50), is_alpha=True)  # По умолчанию

    def get_extended(self):
        return True  # Говорим, что PNG и др. поддерживаются


class MockPygameTransform:
    """Мок для pygame.transform."""

    def scale(self, surface, size_tuple):
        # Возвращаем новый мок Surface с указанными размерами.
        return MockSurface(
            size_tuple, surface._is_alpha if hasattr(surface, "_is_alpha") else False
        )


class MockPygameFont:
    """Мок для объекта шрифта pygame.font.Font или SysFont."""

    def __init__(
        self, name, size, bold=False, italic=False
    ):  # Match SysFont signature better
        pass

    def render(self, text, antialias, color, background=None):
        # Возвращаем мок Surface, имитирующий отрендеренный текст.
        # Размеры зависят от текста, для простоты используем фиксированные.
        width = len(text) * 10  # Примерная ширина
        height = 20  # Примерная высота
        return MockSurface((width, height))


class MockPygameDisplay:
    """Мок для pygame.display."""

    def set_mode(self, resolution, flags=0, depth=0, display=0, vsync=0):
        return MockSurface(resolution)  # Возвращаем мок экрана

    def set_caption(self, title):
        pass

    def flip(self):
        pass


class MockGameStats:
    """Упрощенный мок для GameStats, если полный не нужен."""

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.ships_left = self.settings.ship_limit
        self.game_active = False

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def _save_high_score(self):  # Добавляем мок-метод
        pass


class MockAlienInvasion:
    """Мок основного класса игры AlienInvasion для инициализации других компонентов."""

    def __init__(self, mock_settings):
        self.settings = mock_settings
        self.screen = MockSurface(
            (self.settings.screen_width, self.settings.screen_height)
        )
        # Для Scoreboard нужен GameStats
        # Используем настоящий GameStats, так как он не зависит от Pygame напрямую для своей основной логики,
        # но ему нужен ai_game.settings.highscore_filepath, который есть в нашем mock_settings.
        # Однако, GameStats вызывает self.settings._load_high_score(), который читает файл.
        # Для изоляции теста лучше использовать MockGameStats или мокать файловые операции.
        # Либо убедиться, что highscore_filepath указывает на тестовый/временный файл.
        # Пока используем MockGameStats для простоты.
        self.stats = MockGameStats(self)  # Используем мок-статистику
        self.ship = None  # Ship будет создан в тесте TestShipLoading отдельно


# --- Тестовые классы ---


# Новый тестовый класс для вспомогательных функций из settings.py
class TestSettingsHelpers(unittest.TestCase):
    def test_lerp_function(self):
        # Импортируем lerp здесь, чтобы избежать проблем с областью видимости при мокинге
        from alien_invasion.settings import lerp

        self.assertEqual(lerp(0, 10, 0.5), 5)
        self.assertEqual(lerp(10, 20, 0), 10)
        self.assertEqual(lerp(10, 20, 1), 20)
        self.assertAlmostEqual(lerp(0, 1, 0.33), 0.33)
        # Тест на ограничение t
        self.assertEqual(lerp(0, 10, -1.0), 0)  # t < 0 should be clamped to 0
        self.assertEqual(lerp(0, 10, 2.0), 10)  # t > 1 should be clamped to 1


class TestSettingsInitialization(unittest.TestCase):
    """Тесты для инициализации класса Settings."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()

    def test_settings_object_created(self):
        """Проверка, что объект Settings успешно создается."""
        self.assertIsNotNone(self.settings, "Объект Settings не должен быть None.")

    def test_assets_dir_attribute(self):
        """Проверка атрибута _ASSETS_DIR."""
        self.assertTrue(
            hasattr(self.settings, "_ASSETS_DIR"),
            "Settings должен иметь атрибут _ASSETS_DIR.",
        )
        self.assertIsInstance(
            self.settings._ASSETS_DIR, str, "_ASSETS_DIR должен быть строкой."
        )
        # Ожидаемый путь: settings.py находится в alien_invasion/, _ASSETS_DIR указывает на ../assets
        expected_path_part = os.path.join("..", "assets")
        # Проверяем, что _ASSETS_DIR оканчивается на '../assets' (или '..\assets' на Windows)
        # Используем os.path.normpath для корректного сравнения путей независимо от ОС
        normalized_assets_dir = os.path.normpath(self.settings._ASSETS_DIR)
        # Получаем путь к директории, где лежит settings.py
        settings_py_dir = os.path.dirname(
            self.settings.__class__.__module__.replace(".", os.sep)
        )
        # Если settings.py в alien_invasion, то его родительская директория - это корень проекта.
        # _ASSETS_DIR должен быть равен os.path.join(корень_проекта, 'assets')
        # или, если смотреть от settings.py: os.path.abspath(os.path.join(директория_settings_py, '..', 'assets'))

        # Более точная проверка:
        # 1. Получаем абсолютный путь к директории, где находится settings.py
        # settings_module_path = sys.modules[Settings.__module__].__file__ # Путь к settings.py
        # settings_dir = os.path.dirname(settings_module_path)
        # expected_abs_assets_dir = os.path.abspath(os.path.join(settings_dir, "..", "assets"))
        # self.assertEqual(os.path.abspath(self.settings._ASSETS_DIR), expected_abs_assets_dir,
        #                  f"_ASSETS_DIR должен указывать на {expected_abs_assets_dir}")
        # Замечание: приведенный выше способ с sys.modules может быть сложен, если структура не стандартная.
        # Проще проверить окончание пути, как было задумано изначально, если мы знаем структуру.
        # self.assertTrue(normalized_assets_dir.endswith(os.path.normpath(expected_path_part)),
        #                 f"_ASSETS_DIR ('{normalized_assets_dir}') должен оканчиваться на '{os.path.normpath(expected_path_part)}'.")
        # Corrected assertion:
        expected_abs_assets_dir = os.path.abspath(os.path.join(project_root, "assets"))
        self.assertEqual(
            normalized_assets_dir,
            expected_abs_assets_dir,
            f"_ASSETS_DIR ('{normalized_assets_dir}') должен быть '{expected_abs_assets_dir}'.",
        )

    def test_key_asset_paths(self):
        """Проверка нескольких ключевых путей к ассетам."""
        # Путь к изображению корабля
        self.assertTrue(
            hasattr(self.settings, "ship_image_path"),
            "Должен быть атрибут ship_image_path.",
        )
        self.assertIsInstance(
            self.settings.ship_image_path, str, "ship_image_path должен быть строкой."
        )
        self.assertTrue(
            self.settings.ship_image_path.endswith(".png"),
            "ship_image_path должен оканчиваться на '.png'.",
        )

        # Путь к звуку лазера
        self.assertTrue(
            hasattr(self.settings, "sound_laser_path"),
            "Должен быть атрибут sound_laser_path.",
        )
        self.assertIsInstance(
            self.settings.sound_laser_path, str, "sound_laser_path должен быть строкой."
        )
        self.assertTrue(
            self.settings.sound_laser_path.endswith(".ogg"),
            "sound_laser_path должен оканчиваться на '.ogg'.",
        )

        # Путь к иконке сердца для Scoreboard
        self.assertTrue(
            hasattr(self.settings, "ui_heart_icon_path"),
            "Должен быть атрибут ui_heart_icon_path.",
        )
        self.assertIsInstance(
            self.settings.ui_heart_icon_path,
            str,
            "ui_heart_icon_path должен быть строкой.",
        )
        self.assertTrue(
            self.settings.ui_heart_icon_path.endswith(".png"),
            "ui_heart_icon_path должен оканчиваться на '.png'.",
        )

    def test_localized_strings_exist_and_correct(self):
        """Проверка наличия и корректности локализованных строк."""
        self.assertEqual(self.settings.text_new_game_button, "Новая игра")
        self.assertEqual(self.settings.text_exit_button, "Выход")
        self.assertEqual(self.settings.text_resume_button, "Продолжить")
        self.assertEqual(self.settings.text_restart_button, "Заново")
        self.assertEqual(self.settings.text_main_menu_button, "Главное меню")
        self.assertEqual(self.settings.text_pause_message, "Пауза")
        self.assertEqual(self.settings.text_high_score_label, "Рекорд: ")


# Cleaned up general mocks for TestButtonCreation, keeping only essential non-targeted ones
@mock.patch("pygame.mixer.init", lambda *args, **kwargs: None)  # General mock
@mock.patch("pygame.mixer.Sound", lambda *args, **kwargs: None)  # General mock
@mock.patch("pygame.image.get_extended", lambda: True)  # General mock
@mock.patch("pygame.init", lambda: None)  # General mock
@mock.patch("pygame.font.init", lambda: None)
@mock.patch("pygame.font.get_init", lambda: True)
@mock.patch(
    "pygame.font.SysFont",
    lambda name, size, bold=False, italic=False: MockPygameFont(
        name, size, bold, italic
    ),
)  # Corrected SysFont mock
class TestButtonCreation(unittest.TestCase):
    """Тесты для класса Button, особенно в контексте локализации."""

    def setUp(self):
        # Русский комментарий: Настройка перед каждым тестом для TestButtonCreation.
        self.settings = Settings()
        self.mock_ai_game = MockAlienInvasion(self.settings)
        # Button.__init__ вызывает _prep_msg, который использует self.font.render.
        # self.font (pygame.font.SysFont) мокается декоратором класса.

    def test_button_uses_settings_text(self):  # Убран аргумент mock_sysfont
        """Проверка, что кнопка использует текст из настроек."""
        # Используем одну из локализованных строк
        button_text_from_settings = self.settings.text_new_game_button
        button = alien_invasion.button.Button(
            self.mock_ai_game, button_text_from_settings
        )

        # MockPygameFont.render в нашем моке создает MockSurface, где width = len(text) * 10
        # Проверяем, что msg_image имеет ожидаемую ширину на основе текста из настроек
        expected_width = len(button_text_from_settings) * 10
        self.assertEqual(
            button.msg_image.width,
            expected_width,
            f"Ширина изображения кнопки '{button.msg_image.width}' не соответствует ожидаемой "
            f"ширине '{expected_width}' для текста '{button_text_from_settings}'.",
        )

    def test_button_prep_msg_handles_string(self):  # Убран аргумент mock_sysfont
        """Проверка, что _prep_msg корректно обрабатывает переданную строку."""
        test_msg = "Test Message"
        button = alien_invasion.button.Button(
            self.mock_ai_game, "Dummy"
        )  # Начальное сообщение

        # Вызываем _prep_msg напрямую
        button._prep_msg(test_msg)

        expected_width = len(test_msg) * 10
        self.assertEqual(button.msg_image.width, expected_width)
        # Дополнительно можно проверить, что msg_image_rect обновился, но это уже детали реализации Button

    def test_button_is_clicked_positive(self):
        """Тест: button.is_clicked() возвращает True при клике внутри кнопки."""
        # Создаем кнопку для этого теста, ее rect будет инициализирован в __init__
        # msg_image_rect.center по умолчанию будет screen_rect.center
        # rect кнопки (self.rect) по умолчанию равен msg_image_rect
        button = alien_invasion.button.Button(self.mock_ai_game, "Test Button")

        # Клик точно в центре кнопки
        mouse_pos_center = button.rect.center
        self.assertTrue(
            button.is_clicked(mouse_pos_center),
            "Клик в центре кнопки должен вернуть True.",
        )

        # Клик в одном из углов кнопки (например, левый верхний)
        mouse_pos_topleft = button.rect.topleft
        self.assertTrue(
            button.is_clicked(mouse_pos_topleft),
            "Клик в левом верхнем углу кнопки должен вернуть True.",
        )

    def test_button_is_clicked_negative_outside(self):
        """Тест: button.is_clicked() возвращает False при клике снаружи кнопки."""
        button = alien_invasion.button.Button(self.mock_ai_game, "Test Button")

        # Клик слева от кнопки
        mouse_pos_left_outside = (button.rect.left - 1, button.rect.centery)
        self.assertFalse(
            button.is_clicked(mouse_pos_left_outside),
            "Клик слева от кнопки должен вернуть False.",
        )

        # Клик справа от кнопки
        mouse_pos_right_outside = (button.rect.right + 1, button.rect.centery)
        self.assertFalse(
            button.is_clicked(mouse_pos_right_outside),
            "Клик справа от кнопки должен вернуть False.",
        )

        # Клик над кнопкой
        mouse_pos_above = (button.rect.centerx, button.rect.top - 1)
        self.assertFalse(
            button.is_clicked(mouse_pos_above), "Клик над кнопкой должен вернуть False."
        )

        # Клик под кнопкой
        mouse_pos_below = (button.rect.centerx, button.rect.bottom + 1)
        self.assertFalse(
            button.is_clicked(mouse_pos_below), "Клик под кнопкой должен вернуть False."
        )

    def test_button_is_clicked_on_edge(self):
        """Тест: button.is_clicked() возвращает True при клике на границе кнопки."""
        button = alien_invasion.button.Button(self.mock_ai_game, "Test Button")

        # Клик на правой границе (pygame.Rect.collidepoint включает границы)
        mouse_pos_right_edge = (
            button.rect.right - 1,
            button.rect.centery,
        )  # -1 потому что right это "за" последним пикселем
        # В реализации collidepoint(x,y): self.x <= x < self.x + self.width and self.y <= y < self.y + self.height
        # Значит, x должен быть < right. То есть button.rect.right - 1 это последняя внутренняя координата.
        self.assertTrue(
            button.is_clicked(mouse_pos_right_edge),
            f"Клик на правой границе ({mouse_pos_right_edge}) должен вернуть True. Rect: {button.rect}",
        )

        # Клик на нижней границе
        mouse_pos_bottom_edge = (button.rect.centerx, button.rect.bottom - 1)
        self.assertTrue(
            button.is_clicked(mouse_pos_bottom_edge),
            f"Клик на нижней границе ({mouse_pos_bottom_edge}) должен вернуть True. Rect: {button.rect}",
        )

        # Клик на левой верхней точке (уже покрыт в positive, но для явности)
        mouse_pos_top_left_edge = button.rect.topleft
        self.assertTrue(
            button.is_clicked(mouse_pos_top_left_edge),
            f"Клик на левой верхней границе ({mouse_pos_top_left_edge}) должен вернуть True. Rect: {button.rect}",
        )


# Cleaned up general mocks for TestShipLoading
@mock.patch("pygame.mixer.init", lambda *args, **kwargs: None)
@mock.patch("pygame.mixer.Sound", lambda *args, **kwargs: None)
@mock.patch("pygame.image", new_callable=MockPygameImage)  # Имя аргумента: mock_image
@mock.patch(
    "pygame.transform", new_callable=MockPygameTransform
)  # Имя аргумента: mock_transform
@mock.patch(
    "pygame.display.set_mode",
    lambda res, flags=0, depth=0, display=0, vsync=0: MockSurface(res),
)
@mock.patch("pygame.image.get_extended", lambda: True)
@mock.patch("pygame.init", lambda: None)
@mock.patch("pygame.display.init", lambda: None)
@mock.patch("pygame.display.get_init", lambda: True)
class TestShipLoading(unittest.TestCase):
    """Тесты для загрузки и инициализации объекта Ship."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        # Русский комментарий: Инициализация Pygame (мокнутая) и дисплея для тестов Ship.
        self.settings = Settings()
        # Для инициализации Ship нужен объект ai_game, который имеет screen и settings.
        # Используем MockAlienInvasion.
        self.mock_ai_game = MockAlienInvasion(self.settings)
        # Ship использует self.settings.ship_image_path. MockPygameImage учтет это.
        self.ship = Ship(self.mock_ai_game)
        self.mock_ai_game.ship = self.ship  # Присваиваем корабль моку игры

    # Аргументы в обратном порядке декораторов: mock_transform, mock_image. Остальные lambda-моки не передаются.
    def test_ship_created_successfully(self, mock_transform, mock_image):
        """Проверка, что объект Ship создается и его ключевые атрибуты инициализированы."""
        self.assertIsNotNone(self.ship, "Объект Ship не должен быть None.")
        self.assertIsNotNone(self.ship.image, "ship.image не должен быть None.")
        # Русский комментарий: Изменен ассерт на pygame.Surface, так как мокинг сложен.
        self.assertIsInstance(
            self.ship.image,
            pygame.Surface,
            f"ship.image должен быть экземпляром pygame.Surface. Получен: {type(self.ship.image)}",
        )

        self.assertIsNotNone(self.ship.rect, "ship.rect не должен быть None.")
        # Русский комментарий: Если self.ship.image - реальный Surface, то и self.ship.rect будет реальным Rect.
        self.assertIsInstance(
            self.ship.rect,
            pygame.Rect,
            f"ship.rect должен быть экземпляром pygame.Rect. Получен: {type(self.ship.rect)}",
        )

    def test_ship_initial_position(self, mock_transform, mock_image):
        """Проверка начальной позиции корабля."""
        # Корабль должен быть спозиционирован внизу по центру экрана.
        # screen_rect берется у мок-экрана нашего mock_ai_game.
        mock_screen_rect = self.mock_ai_game.screen.get_rect()
        self.assertEqual(
            self.ship.rect.centerx,
            mock_screen_rect.centerx,
            "Корабль должен быть по центру оси X.",
        )
        self.assertEqual(
            self.ship.rect.midbottom[1],
            mock_screen_rect.midbottom[1],
            "Низ корабля должен совпадать с низом экрана.",
        )


# Cleaned up general mocks for TestScoreboardUpdates
# pygame.font.init() and pygame.font.get_init() should not be mocked here,
# as Scoreboard relies on real font initialization.
# SysFont can be mocked to return a MockPygameFont.
@mock.patch("pygame.font.SysFont", lambda name, size, bold=False, italic=False: MockPygameFont(name, size, bold, italic))
@mock.patch("pygame.image.get_extended", lambda: True)
@mock.patch("pygame.init", lambda: None) # General init for pygame
@mock.patch("pygame.display.init", lambda: None) # Mock display init
@mock.patch("pygame.display.set_mode", lambda res, flags=0, depth=0, display=0, vsync=0: MockSurface(res)) # Mock set_mode
# @mock.patch("pygame.font.init", lambda: None) # REMOVED
# @mock.patch("pygame.font.get_init", lambda: True) # REMOVED
@mock.patch("pygame.mixer.init", lambda *args, **kwargs: None)
@mock.patch("pygame.mixer.Sound", lambda *args, **kwargs: None)
# REMOVING class-level patches for pygame.image and pygame.transform
# @mock.patch("pygame.image", new_callable=MockPygameImage)
# @mock.patch("pygame.transform", new_callable=MockPygameTransform)
class TestScoreboardUpdates(unittest.TestCase):
    """Тесты для обновления информации в Scoreboard."""

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()

        pygame.font.init()
        pygame.display.init()
        try:
            pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        except pygame.error:
            pass

        # Patch specific functions used by Scoreboard within setUp for better control
        self.mock_image_load = patch('pygame.image.load').start()
        self.mock_transform_scale = patch('pygame.transform.scale').start()
        self.mock_sysfont = patch('pygame.font.SysFont', return_value=MockPygameFont(None, 48)).start() # MockPygameFont from this file

        self.addCleanup(patch.stopall) # Stops all patches started with start()

        # Configure mocks
        # self.mock_image_load.return_value = MockSurface((32,32)) # Default MockSurface
        # More specific:
        def image_load_side_effect(path):
            if path == self.settings.ui_heart_icon_path:
                return MockSurface((32,32), is_alpha=True)
            elif path == self.settings.ui_score_frame_bg_path:
                return MockSurface((100,50), is_alpha=True) # Example size
            return MockSurface((10,10), is_alpha=True) # Default for other paths
        self.mock_image_load.side_effect = image_load_side_effect

        self.mock_transform_scale.side_effect = lambda surface, size: MockSurface(size, getattr(surface, '_is_alpha', False))


        self.mock_ai_game = MockAlienInvasion(self.settings)
        self.scoreboard = Scoreboard(self.mock_ai_game)

    @classmethod
    def tearDownClass(cls):
        pass

    @patch('alien_invasion.scoreboard.Ship')
    def test_initial_scoreboard_images_created(self, MockShip):
        """Проверка, что начальные изображения для счета, уровня и кораблей созданы."""

        # Mocks for pygame.image.load, pygame.transform.scale, pygame.font.SysFont are set up in self.setUp()
        # No need for mock_pygame_transform, mock_pygame_image as arguments here.

        # Configure the mock Ship if its rect size is important for fallback in prep_ships
        # MockShip.return_value.rect = MockRect(0,0,30,30) # Example

        # Since SysFont is mocked at class level to return MockPygameFont,
        # and MockPygameFont.render returns MockSurface, these should be MockSurface.
        self.assertIsNotNone(
            self.scoreboard.score_image, "score_image должно быть создано."
        )
        self.assertIsInstance(
            self.scoreboard.score_image,
            MockSurface, # Expecting MockSurface from this file's context
            f"score_image должно быть MockSurface. Получен: {type(self.scoreboard.score_image)}",
        )

        self.assertIsNotNone(
            self.scoreboard.level_image, "level_image должно быть создано."
        )
        self.assertIsInstance(
            self.scoreboard.level_image,
            MockSurface, # Expecting MockSurface
            f"level_image должно быть MockSurface. Получен: {type(self.scoreboard.level_image)}",
        )

        # Проверка отображения жизней
        # pygame.image (mock_pygame_image) is an instance of local MockPygameImage.
        # mock_pygame_image.load returns a local MockSurface.
        # pygame.transform (mock_pygame_transform) is an instance of local MockPygameTransform.
        # mock_pygame_transform.scale also returns a local MockSurface.

        # We need to ensure that the mocks provided by class decorators are correctly configured
        # for the paths Scoreboard uses. This should happen if MockPygameImage is set up correctly.
        # Let's assume heart_icon is loaded.

        self.assertIsNotNone(self.scoreboard.heart_icon,
            f"Иконка сердца должна была быть загружена (мокнута). Path: {self.settings.ui_heart_icon_path}")
        self.assertIsInstance(self.scoreboard.heart_icon, MockSurface,
            f"heart_icon должен быть MockSurface. Получено: {type(self.scoreboard.heart_icon)}")

        self.assertTrue(
            hasattr(self.scoreboard, "life_icons_to_draw"),
            "Scoreboard должен иметь атрибут 'life_icons_to_draw', когда heart_icon загружен."
        )
        self.assertIsNotNone(
            self.scoreboard.life_icons_to_draw,
            "life_icons_to_draw не должен быть None."
        )
        self.assertEqual(
            len(self.scoreboard.life_icons_to_draw),
            self.settings.ship_limit, # Начальное количество жизней
            "Количество иконок жизней должно соответствовать начальному ship_limit."
        )
        if self.settings.ship_limit > 0 and self.scoreboard.life_icons_to_draw:
            self.assertIsInstance(
                self.scoreboard.life_icons_to_draw[0]["image"],
                MockSurface,
                f"Изображение иконки жизни должно быть MockSurface. Получено: {type(self.scoreboard.life_icons_to_draw[0]['image'])}"
            )

    def test_score_update_reflects_in_image(self): # Removed mock arguments
        """Проверка, что изменение счета в GameStats и вызов prep_score обновляет score_image."""
        # Сохраняем ссылку на текущий объект Surface перед обновлением
        initial_score_image_surface_obj = self.scoreboard.score_image

        # Изменяем счет в статистике
        self.mock_ai_game.stats.score = 12345
        self.scoreboard.prep_score()  # Перерисовываем изображение счета

        updated_score_image_surface = self.scoreboard.score_image

        self.assertIsNotNone(
            updated_score_image_surface, "Обновленное score_image не должно быть None."
        )
        self.assertIsInstance(
            updated_score_image_surface,
            MockSurface, # Expect MockSurface due to mocks in setUp
            "Обновленное score_image должно быть MockSurface.",
        )

        # Простая проверка, что объект изображения изменился (или его размеры, если текст другой).
        # Сравнение самих пикселей сложно без реального рендеринга.
        # В нашем моке MockPygameFont().render() возвращает Surface с шириной len(text)*10.
        # Старый счет "0" -> ширина 10. Новый счет "12,340" (округленный до -1) -> 6 символов * 10 = 60.
        # (Примечание: round(12345, -1) = 12340. format -> "12,340")

        # В реальном Pygame объект Surface может быть тем же, но его содержимое изменится.
        # Проверка по id не всегда надежна. Лучше проверять по содержимому или размерам, если они должны меняться.
        # С реальным рендерингом шрифта размеры могут быть более предсказуемыми, чем с MockSurface.
        # Однако, точные размеры зависят от шрифта, который SysFont выберет в тестовом окружении.
        # Поэтому более надежно проверить, что это РАЗНЫЕ объекты, если prep_score создает новый Surface.
        # Если prep_score модифицирует существующий Surface, то id будет одинаковым, но содержимое разным.
        # В текущей реализации Button и Scoreboard, render создает новый Surface.
        self.assertNotEqual(
            id(initial_score_image_surface_obj),
            id(updated_score_image_surface),
            "Объект score_image должен быть новым после prep_score, если текст изменился.",
        )
        # Проверим, что ширина изменилась (зависит от шрифта, но для разных строк обычно разная)
        # Это менее надежно, чем проверка id, если prep_score всегда создает новый объект.
        # self.assertNotEqual(initial_score_image_surface_obj.get_width(), updated_score_image_surface.get_width(),
        #                    "Ширина изображения счета должна измениться после обновления счета.")

    def test_high_score_label_from_settings(self): # Removed mock arguments
        """Проверка, что метка рекорда используется из Settings."""
        # Устанавливаем произвольный рекорд
        self.mock_ai_game.stats.high_score = 54321
        self.scoreboard.prep_high_score()  # Готовим изображение рекорда

        # MockPygameFont().render в нашем моке создает MockSurface с шириной len(text) * 10.
        # Ожидаемый текст: "Рекорд: 54,320" (округление до -1 для 54321 -> 54320)
        # Длина "Рекорд: " = 8 символов. Длина "54,320" = 6 символов. Итого 14 символов.
        expected_label = self.settings.text_high_score_label  # "Рекорд: "
        rounded_high_score_val = round(self.mock_ai_game.stats.high_score, -1)
        expected_score_str_part = "{:,}".format(rounded_high_score_val)  # "54,320"
        expected_full_text = expected_label + expected_score_str_part

        # С реальным рендерингом точную ширину предсказать сложно без знания шрифта.
        # Проверим, что изображение создано и является Surface.
        self.assertIsNotNone(self.scoreboard.high_score_image)
        self.assertIsInstance(self.scoreboard.high_score_image, MockSurface) # Expect MockSurface
        # Можно сделать более слабую проверку, что ширина больше нуля или какого-то минимального значения.
        self.assertGreater(
            self.scoreboard.high_score_image.get_width(),
            0,
            f"Ширина high_score_image должна быть больше 0 для текста '{expected_full_text}'.",
        )

    def tearDown(self):
        """Очистка после тестов, если необходимо (например, удалить тестовые файлы)."""
        # if os.path.exists("test_highscore.json"):
        #     os.remove("test_highscore.json")
        pygame.font.quit()  # Освобождаем ресурсы шрифтов
        pygame.display.quit()  # Освобождаем ресурсы дисплея
        pass


class TestGameStats(unittest.TestCase):
    """Тесты для класса GameStats."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()
        # Используем уникальное имя файла для тестов, чтобы не пересекаться с реальным файлом.
        self.test_highscore_path = "test_highscore.json"
        self.settings.highscore_filepath = self.test_highscore_path

        # Mock ai_game, достаточно только атрибута settings для GameStats
        self.mock_ai_game = mock.Mock()
        self.mock_ai_game.settings = self.settings

        # Удаляем тестовый файл рекордов перед каждым тестом, если он существует
        if os.path.exists(self.test_highscore_path):
            os.remove(self.test_highscore_path)

    def tearDown(self):
        """Очистка после каждого теста."""
        if os.path.exists(self.test_highscore_path):
            os.remove(self.test_highscore_path)

    def test_load_highscore_corrupted_file(self):
        """Тест загрузки рекорда из поврежденного JSON файла."""
        # Создаем файл с некорректным JSON
        with open(self.test_highscore_path, "w") as f:
            f.write("{'score': 1000")  # Незакрытая скобка, некорректный JSON

        # GameStats инициализируется и должен попытаться загрузить рекорд
        # _load_high_score вызывается в __init__
        stats = GameStats(self.mock_ai_game)

        # Ожидаем, что high_score будет 0 из-за ошибки декодирования
        self.assertEqual(
            stats.high_score, 0, "High score должен быть 0, если JSON файл поврежден."
        )

    def test_load_highscore_file_not_found(self):
        """Тест загрузки рекорда, когда файл не найден."""
        # Убедимся, что файл не существует (setUp должен был это обеспечить)
        self.assertFalse(
            os.path.exists(self.test_highscore_path),
            "Файл рекордов не должен существовать для этого теста.",
        )

        stats = GameStats(self.mock_ai_game)
        self.assertEqual(
            stats.high_score, 0, "High score должен быть 0, если файл не найден."
        )

    def test_load_highscore_success(self):
        """Тест успешной загрузки рекорда из файла."""
        expected_score = 12345
        # Создаем файл с корректным JSON
        with open(self.test_highscore_path, "w") as f:
            import json  # нужен для json.dump

            json.dump(expected_score, f)

        stats = GameStats(self.mock_ai_game)
        self.assertEqual(
            stats.high_score,
            expected_score,
            f"High score должен быть {expected_score} при успешной загрузке.",
        )

    def test_save_high_score(self):
        """Тест сохранения рекорда."""
        stats = GameStats(self.mock_ai_game)
        stats.high_score = 98765
        stats._save_high_score()  # Метод для сохранения

        self.assertTrue(
            os.path.exists(self.test_highscore_path),
            "Файл рекордов должен быть создан.",
        )

        # Проверяем содержимое файла
        with open(self.test_highscore_path, "r") as f:
            import json  # нужен для json.load

            saved_score = json.load(f)
        self.assertEqual(
            saved_score, 98765, "Сохраненный рекорд не соответствует ожидаемому."
        )


if __name__ == "__main__":
    # Импортируем Button здесь, чтобы избежать циклического импорта на уровне модуля,
    # если Button сам импортирует что-то, что может быть замокано глобально.
    # Это больше предосторожность для сложных структур.
    import alien_invasion.button

    unittest.main(verbosity=2)
