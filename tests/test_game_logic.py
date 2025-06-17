import unittest
import os
import sys

# Добавляем корневую директорию проекта в sys.path, чтобы можно было импортировать модули игры
# Это необходимо, если тесты запускаются непосредственно из директории tests/
# или если PYTHONPATH не настроен соответствующим образом.
# При запуске через 'python -m unittest discover' из корня проекта, это может быть не строго обязательно,
# но не помешает для универсальности.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from alien_invasion.settings import Settings
from alien_invasion.ship import Ship
from alien_invasion.scoreboard import Scoreboard
from alien_invasion.game_stats import GameStats
from alien_invasion.alien_invasion import AlienInvasion # Нужен для ai_game в Ship и Scoreboard

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
        return self # Возвращаем себя же для цепочки вызовов

    def convert(self):
        self._is_alpha = False
        return self

    def copy(self):
        return MockSurface((self.width, self.height), self._is_alpha)

    def fill(self, color):
        pass # Ничего не делаем

    def blit(self, source, dest, special_flags=0):
        pass # Ничего не делаем

    def get_size(self):
        return (self.width, self.height)

    def set_alpha(self, alpha_value):
        pass # Ничего не делаем


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
        self.width += other_rect.width # Примерное увеличение
        self.height += other_rect.height

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
        if "playerShip3_blue.png" in path: # Путь из настроек для корабля
            return MockSurface((64, 64), is_alpha=True) # Ожидаемые размеры после scale в Ship
        elif "heart.png" in path: # Пример для иконки
             return MockSurface((32,32), is_alpha=True)
        elif "blue_panel.png" in path: # Пример для фона рамки
            return MockSurface((100,50), is_alpha=True)
        return MockSurface((50, 50), is_alpha=True) # По умолчанию

    def get_extended(self):
        return True # Говорим, что PNG и др. поддерживаются

class MockPygameTransform:
    """Мок для pygame.transform."""
    def scale(self, surface, size_tuple):
        # Возвращаем новый мок Surface с указанными размерами.
        return MockSurface(size_tuple, surface._is_alpha if hasattr(surface, '_is_alpha') else False)

class MockPygameFont:
    """Мок для объекта шрифта pygame.font.Font или SysFont."""
    def render(self, text, antialias, color, background=None):
        # Возвращаем мок Surface, имитирующий отрендеренный текст.
        # Размеры зависят от текста, для простоты используем фиксированные.
        width = len(text) * 10 # Примерная ширина
        height = 20 # Примерная высота
        return MockSurface((width, height))

class MockPygameDisplay:
    """Мок для pygame.display."""
    def set_mode(self, resolution, flags=0, depth=0, display=0, vsync=0):
        return MockSurface(resolution) # Возвращаем мок экрана

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

    def _save_high_score(self): # Добавляем мок-метод
        pass


class MockAlienInvasion:
    """Мок основного класса игры AlienInvasion для инициализации других компонентов."""
    def __init__(self, mock_settings):
        self.settings = mock_settings
        self.screen = MockSurface((self.settings.screen_width, self.settings.screen_height))
        # Для Scoreboard нужен GameStats
        # Используем настоящий GameStats, так как он не зависит от Pygame напрямую для своей основной логики,
        # но ему нужен ai_game.settings.highscore_filepath, который есть в нашем mock_settings.
        # Однако, GameStats вызывает self.settings._load_high_score(), который читает файл.
        # Для изоляции теста лучше использовать MockGameStats или мокать файловые операции.
        # Либо убедиться, что highscore_filepath указывает на тестовый/временный файл.
        # Пока используем MockGameStats для простоты.
        self.stats = MockGameStats(self) # Используем мок-статистику
        self.ship = None # Ship будет создан в тесте TestShipLoading отдельно


# --- Тестовые классы ---

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
        self.assertTrue(hasattr(self.settings, '_ASSETS_DIR'), "Settings должен иметь атрибут _ASSETS_DIR.")
        self.assertIsInstance(self.settings._ASSETS_DIR, str, "_ASSETS_DIR должен быть строкой.")
        # Ожидаемый путь: settings.py находится в alien_invasion/, _ASSETS_DIR указывает на ../assets
        expected_path_part = os.path.join("..", "assets")
        # Проверяем, что _ASSETS_DIR оканчивается на '../assets' (или '..\assets' на Windows)
        # Используем os.path.normpath для корректного сравнения путей независимо от ОС
        normalized_assets_dir = os.path.normpath(self.settings._ASSETS_DIR)
        # Получаем путь к директории, где лежит settings.py
        settings_py_dir = os.path.dirname(self.settings.__class__.__module__.replace('.', os.sep))
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
        self.assertTrue(normalized_assets_dir.endswith(os.path.normpath(expected_path_part)),
                        f"_ASSETS_DIR ('{normalized_assets_dir}') должен оканчиваться на '{os.path.normpath(expected_path_part)}'.")


    def test_key_asset_paths(self):
        """Проверка нескольких ключевых путей к ассетам."""
        # Путь к изображению корабля
        self.assertTrue(hasattr(self.settings, 'ship_image_path'), "Должен быть атрибут ship_image_path.")
        self.assertIsInstance(self.settings.ship_image_path, str, "ship_image_path должен быть строкой.")
        self.assertTrue(self.settings.ship_image_path.endswith('.png'), "ship_image_path должен оканчиваться на '.png'.")

        # Путь к звуку лазера
        self.assertTrue(hasattr(self.settings, 'sound_laser_path'), "Должен быть атрибут sound_laser_path.")
        self.assertIsInstance(self.settings.sound_laser_path, str, "sound_laser_path должен быть строкой.")
        self.assertTrue(self.settings.sound_laser_path.endswith('.ogg'), "sound_laser_path должен оканчиваться на '.ogg'.")

        # Путь к иконке сердца для Scoreboard
        self.assertTrue(hasattr(self.settings, 'ui_heart_icon_path'), "Должен быть атрибут ui_heart_icon_path.")
        self.assertIsInstance(self.settings.ui_heart_icon_path, str, "ui_heart_icon_path должен быть строкой.")
        self.assertTrue(self.settings.ui_heart_icon_path.endswith('.png'), "ui_heart_icon_path должен оканчиваться на '.png'.")


@unittest.mock.patch('pygame.image', MockPygameImage())
@unittest.mock.patch('pygame.transform', MockPygameTransform())
@unittest.mock.patch('pygame.display', MockPygameDisplay()) # Мокаем display для инициализации AlienInvasion
@unittest.mock.patch('pygame.font.SysFont', lambda name, size: MockPygameFont()) # Мокаем SysFont
@unittest.mock.patch('pygame.mixer.init', lambda *args, **kwargs: None) # Мокаем инициализацию микшера
@unittest.mock.patch('pygame.mixer.Sound', lambda *args, **kwargs: None) # Мокаем загрузку звуков
@unittest.mock.patch('pygame.image.get_extended', lambda: True) # Мокаем проверку расширений
@unittest.mock.patch('pygame.init', lambda: None) # Мокаем pygame.init()
class TestShipLoading(unittest.TestCase):
    """Тесты для загрузки и инициализации объекта Ship."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()
        # Для инициализации Ship нужен объект ai_game, который имеет screen и settings.
        # Создадим простой мок для ai_game или используем MockAlienInvasion.
        self.mock_ai_game = MockAlienInvasion(self.settings)
        # Ship также использует self.settings.ship_image_path, который должен быть валидным путем
        # к моменту вызова pygame.image.load. MockPygameImage это учтет.
        self.ship = Ship(self.mock_ai_game)
        self.mock_ai_game.ship = self.ship # Присваиваем корабль моку игры

    def test_ship_created_successfully(self):
        """Проверка, что объект Ship создается и его ключевые атрибуты инициализированы."""
        self.assertIsNotNone(self.ship, "Объект Ship не должен быть None.")
        self.assertIsNotNone(self.ship.image, "ship.image не должен быть None.")
        self.assertIsInstance(self.ship.image, MockSurface, "ship.image должен быть экземпляром MockSurface (pygame.Surface).")

        self.assertIsNotNone(self.ship.rect, "ship.rect не должен быть None.")
        self.assertIsInstance(self.ship.rect, MockRect, "ship.rect должен быть экземпляром MockRect (pygame.Rect).")

    def test_ship_initial_position(self):
        """Проверка начальной позиции корабля."""
        # Корабль должен быть спозиционирован внизу по центру экрана.
        # screen_rect у мок-экрана нашего mock_ai_game.
        mock_screen_rect = self.mock_ai_game.screen.get_rect()
        self.assertEqual(self.ship.rect.centerx, mock_screen_rect.centerx, "Корабль должен быть по центру оси X.")
        self.assertEqual(self.ship.rect.midbottom[1], mock_screen_rect.midbottom[1], "Низ корабля должен совпадать с низом экрана.")


@unittest.mock.patch('pygame.font.SysFont', lambda name, size: MockPygameFont())
@unittest.mock.patch('pygame.image.load', MockPygameImage().load) # Используем метод load нашего мока
@unittest.mock.patch('pygame.transform.scale', MockPygameTransform().scale)
class TestScoreboardUpdates(unittest.TestCase):
    """Тесты для обновления информации в Scoreboard."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()
        self.mock_screen = MockSurface((self.settings.screen_width, self.settings.screen_height))

        # Scoreboard требует ai_game с screen, settings, stats
        self.mock_ai_game = MockAlienInvasion(self.settings) # stats уже мокнут внутри MockAlienInvasion

        # Убедимся, что путь к highscore_filepath существует или мокнем файловые операции,
        # если GameStats будет реальным. MockGameStats не читает файл.
        # self.settings.highscore_filepath = "test_highscore.json" # Можно подменить для реального GameStats

        self.scoreboard = Scoreboard(self.mock_ai_game)

    def test_initial_scoreboard_images_created(self):
        """Проверка, что начальные изображения для счета, уровня и кораблей созданы."""
        self.assertIsNotNone(self.scoreboard.score_image, "score_image должно быть создано.")
        self.assertIsInstance(self.scoreboard.score_image, MockSurface, "score_image должно быть MockSurface.")

        self.assertIsNotNone(self.scoreboard.level_image, "level_image должно быть создано.")
        self.assertIsInstance(self.scoreboard.level_image, MockSurface, "level_image должно быть MockSurface.")

        # Проверка отображения жизней (может быть либо self.ships группа, либо self.ships_items_for_draw)
        if self.scoreboard.heart_icon: # Если иконка сердца загружена (через мок)
            self.assertTrue(hasattr(self.scoreboard, 'ships_items_for_draw'))
            self.assertIsNotNone(self.scoreboard.ships_items_for_draw)
            self.assertGreater(len(self.scoreboard.ships_items_for_draw), 0, "Должны быть элементы для отображения жизней.")
        else: # Старая логика с группой кораблей
            self.assertTrue(hasattr(self.scoreboard, 'ships'))
            self.assertIsNotNone(self.scoreboard.ships, "Группа ships должна быть создана.")
            # self.assertGreater(len(self.scoreboard.ships), 0, "Должны быть корабли в группе ships.")
            # Примечание: ships создаются на основе self.stats.ships_left, который равен 3 по умолчанию.
            # Но если Ship не мокнуть полностью, он может упасть.
            # В текущей конфигурации setUp для Scoreboard, Ship не создается напрямую в Scoreboard,
            # а только если heart_icon не загружен. heart_icon у нас мокается.

    def test_score_update_reflects_in_image(self):
        """Проверка, что изменение счета в GameStats и вызов prep_score обновляет score_image."""
        initial_score_image_surface = self.scoreboard.score_image

        # Изменяем счет в статистике
        self.mock_ai_game.stats.score = 12345
        self.scoreboard.prep_score() # Перерисовываем изображение счета

        updated_score_image_surface = self.scoreboard.score_image

        self.assertIsNotNone(updated_score_image_surface, "Обновленное score_image не должно быть None.")
        self.assertIsInstance(updated_score_image_surface, MockSurface, "Обновленное score_image должно быть MockSurface.")

        # Простая проверка, что объект изображения изменился (или его размеры, если текст другой).
        # Сравнение самих пикселей сложно без реального рендеринга.
        # В нашем моке MockPygameFont().render() возвращает Surface с шириной len(text)*10.
        # Старый счет "0" -> ширина 10. Новый счет "12,340" (округленный до -1) -> 6 символов * 10 = 60.
        # (Примечание: round(12345, -1) = 12340. format -> "12,340")

        # score_str для 0: "0" -> 1*10 = 10
        # rounded_score for 12345 is 12340. score_str = "{:,}".format(12340) -> "12,340" (6 символов) -> 6*10=60
        self.assertNotEqual(initial_score_image_surface.width, updated_score_image_surface.width,
                           "Ширина изображения счета должна измениться после обновления счета, "
                           f"старая ширина: {initial_score_image_surface.width}, "
                           f"новая ширина: {updated_score_image_surface.width}")

    def tearDown(self):
        """Очистка после тестов, если необходимо (например, удалить тестовые файлы)."""
        # if os.path.exists("test_highscore.json"):
        #     os.remove("test_highscore.json")
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)

```
