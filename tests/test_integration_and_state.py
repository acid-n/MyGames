# -*- coding: utf-8 -*-
"""Интеграционные и state-тесты для Alien Invasion."""

import unittest
from unittest.mock import MagicMock, patch
import pygame  # Нужен для реальных объектов Scoreboard и др.
import os  # Для работы с путями, если потребуется
import sys  # Для модификации sys.path, если потребуется

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from alien_invasion.settings import Settings
from alien_invasion.ship import Ship
from alien_invasion.scoreboard import Scoreboard
from alien_invasion.game_stats import GameStats
from alien_invasion.alien_invasion import AlienInvasion
from alien_invasion.alien import Alien
from alien_invasion.bullet import Bullet # Added import
from alien_invasion.powerup import PowerUp # Added import


# --- Mock объекты для Pygame (адаптировано из test_game_logic.py) ---


class MockSurface:
    """Минимальный мок для pygame.Surface."""

    def __init__(self, width_height_tuple, is_alpha=False, fill_color=None):
        self.width = width_height_tuple[0]
        self.height = width_height_tuple[1]
        self._is_alpha = is_alpha
        self.rect = MockRect(0, 0, self.width, self.height)
        self._text_ = ""  # Для проверки текста в Scoreboard
        self._fill_color = fill_color

    def get_rect(self, **kwargs):  # Добавляем **kwargs для совместимости с center=...
        rect = MockRect(self.rect.x, self.rect.y, self.width, self.height)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect

    def convert_alpha(self):
        self._is_alpha = True
        return self

    def convert(self):
        self._is_alpha = False
        return self

    def copy(self):
        return MockSurface((self.width, self.height), self._is_alpha)

    def fill(self, color):
        self._fill_color = color  # Сохраняем цвет заливки

    def blit(self, source, dest, special_flags=0):
        pass

    def get_size(self):
        return (self.width, self.height)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_flags(self):
        # Return a basic flag, or pygame.SRCALPHA if it's supposed to be an alpha surface
        # For simplicity, if _is_alpha is true, assume SRCALPHA, otherwise 0.
        # Note: Real pygame.SRCALPHA is a constant. If pygame is fully mocked, this might need to be a raw int.
        try:
            return pygame.SRCALPHA if self._is_alpha else 0
        except AttributeError: # pygame might not be fully available or SRCALPHA not on it
            return 0x00000001 if self._is_alpha else 0 # A common value for SRCALPHA like flags

    def set_alpha(self, alpha_value):
        pass


class MockRect:
    """Минимальный мок для pygame.Rect."""

    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    @property
    def left(self): return self.x
    @left.setter
    def left(self, value): self.x = int(value)

    @property
    def top(self): return self.y
    @top.setter
    def top(self, value): self.y = int(value)

    @property
    def right(self): return self.x + self.width
    @right.setter
    def right(self, value): self.x = int(value) - self.width

    @property
    def bottom(self): return self.y + self.height
    @bottom.setter
    def bottom(self, value): self.y = int(value) - self.height

    @property
    def centerx(self): return self.x + self.width // 2
    @centerx.setter
    def centerx(self, value): self.x = int(value) - self.width // 2

    @property
    def centery(self): return self.y + self.height // 2
    @centery.setter
    def centery(self, value): self.y = int(value) - self.height // 2

    @property
    def center(self): return (self.centerx, self.centery)
    @center.setter
    def center(self, value):
        self.centerx = int(value[0])
        self.centery = int(value[1])

    @property
    def topleft(self): return (self.x, self.y)
    @topleft.setter
    def topleft(self, value):
        self.x = int(value[0])
        self.y = int(value[1])

    @property
    def midtop(self): return (self.centerx, self.top)
    @midtop.setter
    def midtop(self, value):
        self.centerx = int(value[0])
        self.top = int(value[1])

    @property
    def midbottom(self): return (self.centerx, self.bottom)
    @midbottom.setter
    def midbottom(self, value):
        self.centerx = int(value[0])
        self.bottom = int(value[1])

    @property
    def size(self): return (self.width, self.height)
    @size.setter
    def size(self, value):
        self.width = int(value[0])
        self.height = int(value[1])

    def copy(self):
        return MockRect(self.x, self.y, self.width, self.height)

    def inflate(self, dx, dy):
        inflated_rect = self.copy()
        inflated_rect.x -= dx // 2
        inflated_rect.y -= dy // 2
        inflated_rect.width += dx
        inflated_rect.height += dy
        return inflated_rect

    def colliderect(self, other_rect):
        # Check for non-overlap conditions
        if self.right <= other_rect.left or \
           self.left >= other_rect.right or \
           self.bottom <= other_rect.top or \
           self.top >= other_rect.bottom:
            return False # No collision
        return True # Collision

    def union_ip(self, other_rect): # other_rect_param was used before, changed to other_rect
        new_x = min(self.x, other_rect.x)
        new_y = min(self.y, other_rect.y)
        new_right = max(self.right, other_rect.right)
        new_bottom = max(self.bottom, other_rect.bottom)
        self.x = new_x
        self.y = new_y
        self.width = new_right - new_x
        self.height = new_bottom - new_y

    def contains(self, other_rect):
        """Возвращает True, если other_rect полностью содержится в этом rect."""
        return (self.left <= other_rect.left and
                self.right >= other_rect.right and
                self.top <= other_rect.top and
                self.bottom >= other_rect.bottom)

    def union(self, other_rect):
        """Возвращает новый MockRect, являющийся объединением этого и другого rect."""
        new_x = min(self.x, other_rect.x)
        new_y = min(self.y, other_rect.y)
        new_right = max(self.right, other_rect.right)
        new_bottom = max(self.bottom, other_rect.bottom)
        new_width = new_right - new_x
        new_height = new_bottom - new_y
        return MockRect(new_x, new_y, new_width, new_height)


class MockPygameImage:
    """Мок для pygame.image."""

    _expected_path_to_surface = {}  # Словарь для настройки моков Surface по путям

    def load(self, path):
        abs_norm_path = os.path.abspath(os.path.normpath(path)) # Абсолютный нормализованный путь
        if abs_norm_path in self._expected_path_to_surface:
            # print(f"MockPygameImage: Loading known path: {path} (abs_norm: {abs_norm_path})")
            return self._expected_path_to_surface[abs_norm_path]
        # print(f"MockPygameImage: Path {path} (abs_norm: {abs_norm_path}) not in expected_path_to_surface. Raising pygame.error.")
        raise pygame.error(f"MockPygameImage: Surface (asset) not found for path: {path} (abs_norm: {abs_norm_path})")

    def get_extended(self):
        return True

    @classmethod
    def set_expected_surface(cls, path, surface):
        cls._expected_path_to_surface[os.path.abspath(os.path.normpath(path))] = surface # Абсолютный нормализованный путь

    @classmethod
    def clear_expected_surfaces(cls):
        cls._expected_path_to_surface = {}


class MockPygameTransform:
    """Мок для pygame.transform."""

    def scale(self, surface, size_tuple):
        return MockSurface(size_tuple, getattr(surface, "_is_alpha", False))

    def flip(self, surface, xbool, ybool):  # Добавлено для Alien
        return surface.copy()  # Просто возвращаем копию


class MockPygameFont:
    """Мок для объекта шрифта pygame.font.Font или SysFont."""

    def __init__(self, name, size, bold=False, italic=False):
        self.name = name
        self.size = size

    def render(self, text, antialias, color, background=None):
        surface = MockSurface((len(text) * 10, 20))  # Примерные размеры
        surface._text_ = text  # Сохраняем текст для проверки
        return surface


class MockPygameDisplay:
    """Мок для pygame.display."""

    _current_screen = None

    def set_mode(self, resolution, flags=0, depth=0, display=0, vsync=0):
        MockPygameDisplay._current_screen = MockSurface(resolution)
        return MockPygameDisplay._current_screen

    def get_surface(self):  # Иногда используется для получения текущего экрана
        return MockPygameDisplay._current_screen

    def set_caption(self, title):
        pass

    def flip(self):
        pass

    def get_init(self):  # Для проверки, инициализирован ли display
        return True  # Предполагаем, что всегда инициализирован, если используется мок

    def init(self):  # Для вызова pygame.display.init()
        pass

    def quit(self):  # Для вызова pygame.display.quit()
        pass


class MockGameStats(GameStats):  # Наследуемся от реального для сохранения логики
    """Мок для GameStats с моком сохранения рекорда."""

    def __init__(self, ai_game):
        super().__init__(ai_game)
        # Ensure high_score is initialized, as the overridden _load_high_score does nothing.
        # The super().__init__ calls the real _load_high_score, which might fail if
        # highscore_filepath is not ideally set for a test environment, or if it's mocked.
        # Explicitly setting it here makes the mock more robust.
        self.high_score = 0
        self._save_high_score_called = False

    def _save_high_score(self):
        self._save_high_score_called = True  # Просто отмечаем, что метод был вызван
        # Не производим реальное сохранение в файл

    def _load_high_score(self):
        # Не производим реальную загрузку, self.high_score будет установлен в __init__
        # Это предотвращает чтение файла в тестах, использующих этот мок.
        pass


class MockAlienInvasion:
    """Упрощенный мок AlienInvasion для интеграционных тестов."""

    def __init__(self, settings_instance, screen_surface=None):
        self.settings = settings_instance
        if screen_surface:
            self.screen = screen_surface
        else:
            # Создаем мок экрана с размерами из настроек
            self.screen = MockSurface(
                (self.settings.screen_width, self.settings.screen_height)
            )

        # Для AlienFleetCreation нам понадобятся реальные stats и aliens group
        # Для ScoreboardIntegration stats будет реальным, но с моком сохранения
        # self.stats = GameStats(self) # Будет заменен в setUp теста, если нужен MockGameStats
        self.aliens = pygame.sprite.Group()  # Нужен для _create_fleet
        self.ship = None  # Может быть установлен позже, если тест требует


# --- Вспомогательные функции для Pygame моков ---
_original_pygame_font_init = None
_original_pygame_font_SysFont = None
_original_pygame_display_init = None
_original_pygame_display_quit = None
_original_pygame_display_set_mode = None
_original_pygame_image_load = None
_original_pygame_transform_scale = None
_original_pygame_transform_flip = None
_original_pygame_mixer_init = None
_original_pygame_mixer_Sound = None
_original_pygame_mixer_music_load = None
_original_pygame_mixer_music_play = None
_original_pygame_mixer_music_set_volume = None


def setup_pygame_mocks(target_test_case):
    """Настраивает моки для Pygame модулей."""
    global _original_pygame_font_init, _original_pygame_font_SysFont
    global _original_pygame_display_init, _original_pygame_display_quit
    global _original_pygame_display_set_mode, _original_pygame_image_load
    global _original_pygame_transform_scale, _original_pygame_transform_flip

    # Сохраняем оригинальные функции, если они еще не сохранены
    if _original_pygame_font_init is None:
        _original_pygame_font_init = pygame.font.init
    if _original_pygame_font_SysFont is None:
        _original_pygame_font_SysFont = pygame.font.SysFont
    if _original_pygame_display_init is None:
        _original_pygame_display_init = pygame.display.init
    if _original_pygame_display_quit is None:
        _original_pygame_display_quit = pygame.display.quit
    if _original_pygame_display_set_mode is None:
        _original_pygame_display_set_mode = pygame.display.set_mode
    if _original_pygame_image_load is None:
        _original_pygame_image_load = pygame.image.load
    if _original_pygame_transform_scale is None:
        _original_pygame_transform_scale = pygame.transform.scale
    if _original_pygame_transform_flip is None:
        _original_pygame_transform_flip = pygame.transform.flip
    global _original_pygame_mixer_init, _original_pygame_mixer_Sound
    global _original_pygame_mixer_music_load, _original_pygame_mixer_music_play, _original_pygame_mixer_music_set_volume

    if _original_pygame_mixer_init is None and hasattr(pygame, "mixer"):
        _original_pygame_mixer_init = pygame.mixer.init
    if _original_pygame_mixer_Sound is None and hasattr(pygame, "mixer"):
        _original_pygame_mixer_Sound = pygame.mixer.Sound
    if _original_pygame_mixer_music_load is None and hasattr(pygame, "mixer"):
        _original_pygame_mixer_music_load = pygame.mixer.music.load
    if _original_pygame_mixer_music_play is None and hasattr(pygame, "mixer"):
        _original_pygame_mixer_music_play = pygame.mixer.music.play
    if _original_pygame_mixer_music_set_volume is None and hasattr(pygame, "mixer"):
        _original_pygame_mixer_music_set_volume = pygame.mixer.music.set_volume

    # Применяем моки
    pygame.font.init = MagicMock()
    pygame.font.SysFont = MagicMock(return_value=MockPygameFont("arial", 12))

    # Мокаем display более тщательно, чтобы Scoreboard мог использовать реальный display
    # но другие тесты могли его мокать полностью.
    # В данном случае, для Scoreboard нужен font.init(), но display можно мокать.
    # Для AlienFleetCreation display тоже можно мокать.
    # Используем MockPygameDisplay для согласованности
    target_test_case.mock_display = MockPygameDisplay()
    pygame.display.init = MagicMock(side_effect=target_test_case.mock_display.init)
    pygame.display.quit = MagicMock(side_effect=target_test_case.mock_display.quit)
    pygame.display.set_mode = MagicMock(
        side_effect=target_test_case.mock_display.set_mode
    )
    pygame.display.get_surface = MagicMock(
        side_effect=target_test_case.mock_display.get_surface
    )
    pygame.display.get_init = MagicMock(
        side_effect=target_test_case.mock_display.get_init
    )
    pygame.display.flip = MagicMock(side_effect=target_test_case.mock_display.flip)

    target_test_case.mock_image_loader = MockPygameImage()
    pygame.image.load = MagicMock(side_effect=target_test_case.mock_image_loader.load)

    target_test_case.mock_transform = MockPygameTransform()
    pygame.transform.scale = MagicMock(
        side_effect=target_test_case.mock_transform.scale
    )
    pygame.transform.flip = MagicMock(side_effect=target_test_case.mock_transform.flip)

    if hasattr(pygame, "mixer"):
        pygame.mixer.init = MagicMock(name="pygame.mixer.init")
        pygame.mixer.Sound = MagicMock(name="pygame.mixer.Sound", return_value=MagicMock(play=MagicMock()))
        pygame.mixer.music = MagicMock()
        pygame.mixer.music.load = MagicMock(name="pygame.mixer.music.load")
        pygame.mixer.music.play = MagicMock(name="pygame.mixer.music.play")
        pygame.mixer.music.set_volume = MagicMock(name="pygame.mixer.music.set_volume")


def teardown_pygame_mocks():
    """Восстанавливает оригинальные Pygame модули."""
    if _original_pygame_font_init is not None:
        pygame.font.init = _original_pygame_font_init
    if _original_pygame_font_SysFont is not None:
        pygame.font.SysFont = _original_pygame_font_SysFont
    if _original_pygame_display_init is not None:
        pygame.display.init = _original_pygame_display_init
    if _original_pygame_display_quit is not None:
        pygame.display.quit = _original_pygame_display_quit
    if _original_pygame_display_set_mode is not None:
        pygame.display.set_mode = _original_pygame_display_set_mode
    if _original_pygame_image_load is not None:
        pygame.image.load = _original_pygame_image_load
    if _original_pygame_transform_scale is not None:
        pygame.transform.scale = _original_pygame_transform_scale
    if _original_pygame_transform_flip is not None:
        pygame.transform.flip = _original_pygame_transform_flip

    global _original_pygame_mixer_init, _original_pygame_mixer_Sound
    global _original_pygame_mixer_music_load, _original_pygame_mixer_music_play, _original_pygame_mixer_music_set_volume
    if hasattr(pygame, "mixer"):
        if _original_pygame_mixer_init is not None:
            pygame.mixer.init = _original_pygame_mixer_init
        if _original_pygame_mixer_Sound is not None:
            pygame.mixer.Sound = _original_pygame_mixer_Sound
        if _original_pygame_mixer_music_load is not None:
            pygame.mixer.music.load = _original_pygame_mixer_music_load
        if _original_pygame_mixer_music_play is not None:
            pygame.mixer.music.play = _original_pygame_mixer_music_play
        if _original_pygame_mixer_music_set_volume is not None:
            pygame.mixer.music.set_volume = _original_pygame_mixer_music_set_volume


    MockPygameImage.clear_expected_surfaces()


class TestGameStatsAndScoreboardIntegration(unittest.TestCase):
    """Тесты для интеграции GameStats и Scoreboard."""

    @classmethod
    def setUpClass(cls):
        """Настройка класса: инициализация Pygame модулей, нужных для Scoreboard."""
        pygame.font.init()
        pygame.display.init() # Initialize display
        try:
            pygame.display.set_mode((1,1)) # Set a minimal display mode for convert/convert_alpha
        except pygame.error:
            pass # Headless environment

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов класса."""
        pygame.font.quit()
        pygame.display.quit() # Quit display

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()

        # Настраиваем моки для pygame.image и pygame.transform, т.к. Scoreboard их использует
        # для загрузки и масштабирования иконки сердца.
        # pygame.display также мокается, чтобы избежать создания реального окна.
        # pygame.font уже инициализирован реально в setUpClass.

        # Модифицируем setup_pygame_mocks, чтобы он не мокал pygame.font
        global _original_pygame_font_init, _original_pygame_font_SysFont
        self._actual_font_init = pygame.font.init
        self._actual_font_SysFont = pygame.font.SysFont

        # Отключаем моки для font перед вызовом setup_pygame_mocks
        pygame.font.init = MagicMock(
            side_effect=lambda: None
        )  # Делаем временный no-op мок
        pygame.font.SysFont = MagicMock(
            return_value=MockPygameFont("arial", 12)
        )  # Временный мок

        setup_pygame_mocks(self)  # Применяем остальные моки (display, image, transform)

        # Восстанавливаем реальные функции для font, если они были заменены моками setup_pygame_mocks
        # Это важно, т.к. setup_pygame_mocks глобально меняет pygame.font.init и SysFont
        pygame.font.init = self._actual_font_init
        pygame.font.SysFont = self._actual_font_SysFont

        # Убедимся, что pygame.font действительно инициализирован для Scoreboard
        if not pygame.font.get_init():
            pygame.font.init()

        # Создаем мок ai_game. Ему нужен screen и settings.
        # Screen будет мокнут через MockPygameDisplay.set_mode()
        # который вызывается внутри AlienInvasion.__init__ или должен быть установлен явно.
        # Scoreboard использует ai_game.screen.get_rect()
        self.mock_screen_surface = MockSurface(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )  # Это вызовет наш мок

        self.ai_game = MockAlienInvasion(
            self.settings, screen_surface=pygame.display.get_surface()
        )

        # Используем MockGameStats, который наследуется от GameStats, но мокает _save_high_score и _load_high_score
        self.stats = MockGameStats(self.ai_game)
        self.ai_game.stats = self.stats  # Привязываем stats к моку ai_game

        # Настраиваем мок для загрузки изображения сердца
        # Scoreboard использует self.settings.ui_heart_icon_path
        heart_image_surface = MockSurface((30, 30), is_alpha=True)  # Примерные размеры
        MockPygameImage.set_expected_surface(
            self.settings.ui_heart_icon_path, heart_image_surface
        )

        # Создаем реальный Scoreboard
        self.sb = Scoreboard(self.ai_game)

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()
        # Убедимся, что реальные функции font восстановлены, если вдруг tearDown не отработал корректно
        if hasattr(self, "_actual_font_init"):
            pygame.font.init = self._actual_font_init
        if hasattr(self, "_actual_font_SysFont"):
            pygame.font.SysFont = self._actual_font_SysFont

    def test_score_update_reflects_in_scoreboard(self):
        """Тест: обновление счета отражается в Scoreboard."""
        initial_score_image_id = id(self.sb.score_image)
        initial_score_image_width = self.sb.score_image.get_width()

        self.stats.score = 12345
        self.sb.prep_score()

        self.assertIsNotNone(
            self.sb.score_image, "sb.score_image не должен быть None после prep_score."
        )
        # Поскольку используется реальный рендеринг шрифтов, новый Surface должен быть создан.
        # Проверяем, что ID объекта изменился или его ширина (если текст изменился).
        # Более надежно, если prep_score всегда создает новый Surface.

        # Форматированный ожидаемый текст (для возможной отладки или сравнения ширины)
        # locale.setlocale(locale.LC_ALL, '') # Учитываем локаль для форматирования
        # expected_text = "{:,}".format(round(12345, -1)) # "12,340"
        # print(f"Initial width: {initial_score_image_width}, New width: {self.sb.score_image.get_width()}, Expected text for new: '{expected_text}'")

        # Проверяем, что либо ID изменился, либо ширина (если ID остался тот же, но содержимое другое)
        # В текущей реализации Scoreboard.prep_score он всегда создает новый Surface через font.render.
        self.assertNotEqual(
            initial_score_image_id,
            id(self.sb.score_image),
            "ID объекта sb.score_image должен измениться после обновления счета, "
            "так как создается новый Surface.",
        )
        # Дополнительно можно проверить, что ширина изменилась, но это зависит от шрифта и текста.
        # Для "0" и "12,340" ширина точно должна отличаться.
        self.assertNotEqual(
            initial_score_image_width,
            self.sb.score_image.get_width(),
            "Ширина sb.score_image должна измениться для другого счета.",
        )

    def test_level_update_reflects_in_scoreboard(self):
        """Тест: обновление уровня отражается в Scoreboard."""
        initial_level_image_id = id(self.sb.level_image)
        initial_level_image_width = self.sb.level_image.get_width()

        self.stats.level = 5
        self.sb.prep_level()

        self.assertIsNotNone(
            self.sb.level_image, "sb.level_image не должен быть None после prep_level."
        )

        # Проверяем, что ID объекта изменился или его ширина (если текст изменился)
        self.assertNotEqual(
            initial_level_image_id,
            id(self.sb.level_image),
            "ID объекта sb.level_image должен измениться после обновления уровня.",
        )
        # Уровни "1" и "5" должны иметь разную ширину, если шрифт не моноширинный для цифр
        # или если prep_level всегда создает новый объект Surface.
        # self.assertNotEqual( # This can be flaky if mock font renders "1" and "5" with same width
        #     initial_level_image_width,
        #     self.sb.level_image.get_width(),
        #     "Ширина sb.level_image должна измениться для другого уровня.",
        # )
        # More robust check is that the ID changed, as prep_level creates a new surface.
        self.assertNotEqual(
            initial_level_image_id, id(self.sb.level_image),
            "ID объекта sb.level_image должен измениться после prep_level, если текст изменился."
        )


    def test_high_score_update_and_display(self):
        """Тест: обновление рекорда и его отображение."""
        initial_high_score_image_id = id(self.sb.high_score_image)
        initial_high_score_image_width = self.sb.high_score_image.get_width()
        initial_high_score = self.stats.high_score  # Обычно 0

        self.stats.score = 5000  # Новый счет, который должен стать рекордом
        self.sb.check_high_score()  # Этот метод должен обновить stats.high_score и sb.prep_high_score()

        self.assertEqual(
            self.stats.high_score,
            self.stats.score,
            "Рекорд в GameStats должен обновиться значением текущего счета.",
        )
        self.assertTrue(
            self.stats._save_high_score_called,
            "Метод _save_high_score в MockGameStats должен быть вызван.",
        )

        self.assertIsNotNone(
            self.sb.high_score_image,
            "sb.high_score_image не должен быть None после обновления рекорда.",
        )

        # Проверяем, что ID объекта изменился или его ширина
        self.assertNotEqual(
            initial_high_score_image_id,
            id(self.sb.high_score_image),
            "ID объекта sb.high_score_image должен измениться после обновления рекорда.",
        )
        # Текст рекорда изменится с "Рекорд: 0" на "Рекорд: 5,000" (или подобное), ширина должна измениться.
        self.assertNotEqual(
            initial_high_score_image_width,
            self.sb.high_score_image.get_width(),
            "Ширина sb.high_score_image должна измениться для нового рекорда.",
        )

    def test_ships_left_update_reflects_in_scoreboard(self):
        """Тест: обновление количества кораблей отражается в Scoreboard."""
        # Scoreboard uses life_icons_to_draw if heart_icon is available,
        # or ships_group_fallback (a Group) otherwise.
        # In this test's setUp, heart_icon is mocked and should be available.
        self.assertIsNotNone(self.sb.heart_icon, "Heart icon should be mocked and available.")
        self.assertTrue(hasattr(self.sb, "life_icons_to_draw"), "Scoreboard should have life_icons_to_draw.")

        initial_ships_drawn_count = len(self.sb.life_icons_to_draw)
        self.assertEqual(
            initial_ships_drawn_count,
            self.settings.ship_limit,
            f"Изначально должно отображаться {self.settings.ship_limit} кораблей.",
        )

        self.stats.ships_left -= 1
        self.sb.prep_ships()

        new_ships_drawn_count = len(self.sb.life_icons_to_draw)
        self.assertEqual(
            new_ships_drawn_count,
            self.stats.ships_left,
            "Количество отображаемых кораблей должно соответствовать stats.ships_left.",
        )

        self.assertNotEqual(
            initial_ships_drawn_count,
            new_ships_drawn_count,
            "Количество отображаемых кораблей должно было измениться.",
        )

        # Проверяем, что элементы в life_icons_to_draw являются ожидаемыми (содержат Surface)
        if new_ships_drawn_count > 0:
            # MockPygameImage.load настроен в setUp для ui_heart_icon_path возвращать MockSurface
            # pygame.transform.scale (мокнутый) также возвращает MockSurface
            self.assertIsInstance(
                self.sb.life_icons_to_draw[0]["image"],
                MockSurface, # This MockSurface is from test_integration_and_state.py
                "Изображение корабля (сердца) должно быть MockSurface из-за моков.",
            )

        # Уменьшим до 0 кораблей
        self.stats.ships_left = 0
        self.sb.prep_ships()
        self.assertEqual(
            len(self.sb.life_icons_to_draw),
            0,
            "При 0 кораблях список life_icons_to_draw должен быть пуст.",
        )


class TestAlienFleetCreation(unittest.TestCase):
    """Тесты для создания флота пришельцев."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()
        setup_pygame_mocks(
            self
        )  # Используем общие моки, включая display, image, transform, font

        # Настраиваем мок для загрузки изображения пришельца
        # Alien класс загружает изображение из self.settings.alien_sprite_paths
        # Alien.__init__ также использует pygame.transform.flip, который уже мокнут в setup_pygame_mocks
        # Используем alien_display_width и alien_display_height для размеров мока
        alien_image_surface = MockSurface(
            (self.settings.alien_display_width, self.settings.alien_display_height), is_alpha=True
        )
        # Alien.py выбирает случайный путь из alien_sprite_paths. Для теста мокнем первый.
        if self.settings.alien_sprite_paths:
            MockPygameImage.set_expected_surface(
                self.settings.alien_sprite_paths[0], alien_image_surface
            )
        else: # Fallback если список пуст (хотя Settings должен предоставлять fallback)
            MockPygameImage.set_expected_surface(
                "dummy_alien_path.png", alien_image_surface # Alien сам имеет fallback на Surface если путь не найден
            )


        # Создаем экземпляр AlienInvasion. Он будет использовать мокнутый display, image, etc.
        # AlienInvasion.__init__ создает экран, настройки, статистику.
        # Для _create_fleet важны ai_game.screen, ai_game.settings, ai_game.stats, ai_game.aliens
        # ai_game.ship используется для получения высоты корабля.

        # Используем настоящий AlienInvasion, так как нам нужна его логика _create_fleet
        # Моки Pygame должны перехватить все вызовы к Pygame.
        # AlienInvasion создаст реальный GameStats, что нормально для этого теста.
        # AlienInvasion создаст реальный Ship, которому нужны моки image и transform.

        # Мок для изображения корабля, так как Ship создается внутри AlienInvasion
        ship_image_surface = MockSurface(
            (self.settings.ship_display_width, self.settings.ship_display_height), # Используем display_width/height
            is_alpha=True,
        )
        MockPygameImage.set_expected_surface(
            self.settings.ship_image_path, ship_image_surface
        )

        self.ai_game = AlienInvasion(
            #settings_overrides={"logging_level": "CRITICAL"} # AlienInvasion не принимает этот параметр
        )  # Используем реальный класс

        # ai_game.ship уже создан внутри AlienInvasion.__init__
        # self.ship = self.ai_game.ship
        # Убедимся, что у корабля есть корректный rect.height для расчетов во флоте
        # Это должно быть обработано моками image.load и transform.scale в Ship.__init__

        # ai_game.aliens (pygame.sprite.Group) уже создан.
        # Alien класс при создании будет использовать мокнутый pygame.image.load

        # Для вызова _create_fleet() напрямую, убедимся что игра не в состоянии game_over
        self.ai_game.stats.game_active = True
        self.ai_game.stats.ships_left = self.ai_game.settings.ship_limit

        # _create_fleet также может зависеть от текущего уровня для powerups
        self.ai_game.stats.level = 1  # Устанавливаем начальный уровень

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()

    def test_fleet_creation_calculates_correct_alien_count(self):
        """Тест: создание флота рассчитывает правильное количество пришельцев."""
        # Убедимся, что настройки соответствуют началу игры (уровень 1)
        # Это должно быть установлено в self.ai_game = AlienInvasion() -> settings.initialize_dynamic_settings(1)
        # и если stats.level = 1, как в setUp.

        # Вызываем метод создания флота
        self.ai_game._create_fleet()

        # Логика расчета ожидаемого количества пришельцев (скопирована и адаптирована из AlienInvasion._create_fleet)
        settings = self.ai_game.settings  # Используем настройки из ai_game
        alien_width = (
            settings.alien_display_width
        )  # Размеры из настроек display_width/height
        alien_height = settings.alien_display_height

        # Расчет количества пришельцев в ряду (по горизонтали)
        available_space_x = settings.screen_width - (
            settings.fleet_screen_margin_x_factor * alien_width
        )
        number_aliens_x_float = available_space_x / (
            settings.alien_horizontal_spacing_factor * alien_width
        )
        base_number_aliens_x = int(number_aliens_x_float)
        number_aliens_x = int(
            base_number_aliens_x * settings.current_aliens_per_row_factor
        )
        number_aliens_x = max(1, number_aliens_x)

        # Расчет количества рядов пришельцев (по вертикали)
        ship_height = self.ai_game.ship.rect.height
        _ALIEN_FLEET_BOTTOM_BUFFER_FACTOR = 2.0  # Значение из alien_invasion.py
        available_height_for_aliens = (
            settings.screen_height
            - (settings.fleet_top_margin_factor * alien_height)
            - ship_height
            - (_ALIEN_FLEET_BOTTOM_BUFFER_FACTOR * alien_height)
        )

        max_possible_rows = 0
        if (settings.alien_vertical_spacing_factor * alien_height) > 0:
            max_possible_rows = int(
                available_height_for_aliens
                / (settings.alien_vertical_spacing_factor * alien_height)
            )
        max_possible_rows = max(0, max_possible_rows)

        base_number_rows = int(max_possible_rows * settings.current_alien_rows_factor)
        final_number_rows = base_number_rows + settings.additional_alien_rows
        final_number_rows = min(final_number_rows, max_possible_rows)
        final_number_rows = max(1, final_number_rows) if max_possible_rows > 0 else 0

        expected_num_aliens = number_aliens_x * final_number_rows

        self.assertEqual(
            len(self.ai_game.aliens),
            expected_num_aliens,
            "Количество созданных пришельцев не соответствует расчетному.",
        )

    def test_powerup_assignment_in_fleet(self):
        """Тест: назначение бонусов во флоте."""
        # --- Тест для Уровня 1 (бонусы не должны назначаться) ---
        self.ai_game.stats.level = 1
        # Убедимся, что initialize_dynamic_settings вызвался для уровня 1, если это влияет на бонусы
        # В AlienInvasion._create_fleet() доступные бонусы определяются на основе self.stats.level
        # settings.initialize_dynamic_settings() не влияет напрямую на типы бонусов.

        self.ai_game._create_fleet()  # Создаем флот для уровня 1

        assigned_powerups_lvl1 = 0
        for alien in self.ai_game.aliens:
            if alien.assigned_powerup_type:
                assigned_powerups_lvl1 += 1

        self.assertEqual(
            assigned_powerups_lvl1, 0, "На уровне 1 не должно быть назначено бонусов."
        )

        # --- Тест для Уровня 3 (бонусы щита и двойного огня доступны) ---
        self.ai_game.stats.level = 3  # Устанавливаем уровень, где бонусы доступны
        # Очищаем старый флот перед созданием нового
        self.ai_game.aliens.empty()
        self.ai_game._create_fleet()

        enemy_count_lvl3 = len(self.ai_game.aliens)
        if enemy_count_lvl3 == 0:  # Если флот пуст, дальнейшие проверки не имеют смысла
            self.skipTest(
                "Флот не был создан для уровня 3, пропускаем тест назначения бонусов."
            )
            return

        _POWERUP_BASE_DROP_RATE = 0.07  # из alien_invasion.py
        _SHIELD_POWERUP_MIN_LEVEL = 2  # из alien_invasion.py
        _DOUBLE_FIRE_POWERUP_MIN_LEVEL = 3  # из alien_invasion.py

        # Ожидаемое количество бонусов
        import math  # нужен для math.ceil

        expected_drops_per_level = math.ceil(enemy_count_lvl3 * _POWERUP_BASE_DROP_RATE)

        available_powerup_types_lvl3 = []
        if self.ai_game.stats.level >= _SHIELD_POWERUP_MIN_LEVEL:
            available_powerup_types_lvl3.append("shield")
        if self.ai_game.stats.level >= _DOUBLE_FIRE_POWERUP_MIN_LEVEL:
            available_powerup_types_lvl3.append("double_fire")

        expected_drops_to_assign = 0
        if available_powerup_types_lvl3:  # Только если есть доступные типы бонусов
            expected_drops_to_assign = min(expected_drops_per_level, enemy_count_lvl3)

        assigned_powerups_lvl3 = 0
        assigned_types_found_lvl3 = set()
        for alien in self.ai_game.aliens:
            if alien.assigned_powerup_type:
                assigned_powerups_lvl3 += 1
                assigned_types_found_lvl3.add(alien.assigned_powerup_type)

        # random.sample выбирает ТОЧНОЕ количество, если k <= популяция
        self.assertEqual(
            assigned_powerups_lvl3,
            expected_drops_to_assign,
            f"Количество назначенных бонусов на уровне 3 ({assigned_powerups_lvl3}) "
            f"не соответствует ожидаемому ({expected_drops_to_assign}). "
            f"Всего пришельцев: {enemy_count_lvl3}, Базовая ставка: {_POWERUP_BASE_DROP_RATE}",
        )

        if expected_drops_to_assign > 0:
            self.assertTrue(
                assigned_types_found_lvl3.issubset(set(available_powerup_types_lvl3)),
                f"Обнаружены недопустимые типы бонусов: {assigned_types_found_lvl3}. "
                f"Допустимые на уровне 3: {available_powerup_types_lvl3}",
            )
            self.assertGreater(
                len(assigned_types_found_lvl3),
                0,
                "На уровне 3 должны быть назначены какие-либо бонусы, если expected_drops_to_assign > 0.",
            )


if __name__ == "__main__":
    unittest.main()


class TestShipAndBulletInteraction(unittest.TestCase):
    """Тесты для взаимодействия Корабля и Пуль."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()
        # Модифицируем setup_pygame_mocks, чтобы он также мокал mixer
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        self._actual_mixer_init = getattr(pygame, "mixer", MagicMock()).init
        self._actual_mixer_Sound = getattr(pygame, "mixer", MagicMock()).Sound

        # Временно заменяем mixer на MagicMock перед вызовом setup_pygame_mocks
        # чтобы избежать ошибок, если mixer не был корректно инициализирован ранее
        original_mixer_module = pygame.mixer if hasattr(pygame, "mixer") else None
        pygame.mixer = MagicMock()
        pygame.mixer.init = MagicMock()
        pygame.mixer.Sound = MagicMock()

        setup_pygame_mocks(self)  # Мокаем display, image, transform, font

        # Восстанавливаем или устанавливаем моки для mixer после setup_pygame_mocks
        # Это гарантирует, что mixer.init и mixer.Sound будут мокнуты, даже если setup_pygame_mocks их не трогает
        pygame.mixer = MagicMock()  # Пересоздаем, чтобы быть уверенным в чистоте мока
        pygame.mixer.init = MagicMock(name="pygame.mixer.init")
        pygame.mixer.Sound = MagicMock(
            name="pygame.mixer.Sound", return_value=MagicMock(play=MagicMock())
        )

        # Настраиваем моки для изображений корабля и пришельца (на случай если Bullet их использует)
        ship_image_surface = MockSurface(
            (self.settings.ship_display_width, self.settings.ship_display_height), # Используем display_width/height
            is_alpha=True,
        )
        MockPygameImage.set_expected_surface(
            self.settings.ship_image_path, ship_image_surface
        )
        # Пулям изображение не нужно, они рисуются через pygame.draw.rect

        # Используем реальный AlienInvasion
        self.ai_game = AlienInvasion()
        self.ai_game.stats.game_active = True  # Для возможности стрельбы
        self.ship = (
            self.ai_game.ship
        )  # Получаем ссылку на корабль, созданный в AlienInvasion
        self.bullets = self.ai_game.bullets  # Получаем ссылку на группу пуль

        # Дополнительно мокаем звук лазера, т.к. он используется в _fire_bullet
        self.ai_game.sound_laser = MagicMock(play=MagicMock())

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()

        # Восстанавливаем оригинальный mixer, если он был
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        if hasattr(pygame, "mixer"):  # Проверяем, существует ли модуль mixer
            pygame.mixer.init = self._actual_mixer_init
            pygame.mixer.Sound = self._actual_mixer_Sound

    def test_fire_single_bullet(self):
        """Тест: одиночный выстрел добавляет одну пулю."""
        self.ship.double_fire_active = False
        initial_bullet_count = len(self.bullets)

        self.ai_game._fire_bullet()

        self.assertEqual(
            len(self.bullets),
            initial_bullet_count + 1,
            "Должна была быть добавлена одна пуля.",
        )

        # Проверка позиции пули (последней добавленной)
        # Bullet.__init__ устанавливает rect.midtop = ai_game.ship.rect.midtop
        # ai_game.ship.rect - это MockRect, его midtop должен быть корректным
        added_bullet = list(self.bullets)[-1]  # Получаем последнюю добавленную пулю
        self.assertEqual(
            added_bullet.rect.midtop,
            self.ship.rect.midtop,
            "Пуля должна появиться вверху по центру корабля.",
        )

    def test_fire_double_bullet(self):
        """Тест: двойной выстрел добавляет две пули со смещением."""
        self.ship.double_fire_active = True
        initial_bullet_count = len(self.bullets)
        _DOUBLE_BULLET_X_OFFSET = 10  # из alien_invasion.py

        self.ai_game._fire_bullet()

        self.assertEqual(
            len(self.bullets),
            initial_bullet_count + 2,
            "Должны были быть добавлены две пули.",
        )

        # Проверка позиций пуль
        bullet1 = list(self.bullets)[-2]
        bullet2 = list(self.bullets)[-1]

        # Обе пули изначально появляются в ship.rect.midtop, затем смещаются по X
        # Bullet.__init__ (self, ai_game, x_offset=0)
        # _fire_bullet для double: bullet1.rect.x -= _DOUBLE_BULLET_X_OFFSET, bullet2.rect.x += _DOUBLE_BULLET_X_OFFSET
        # Важно: Bullet.rect.x устанавливается ПОСЛЕ Bullet.rect.midtop = ship.rect.midtop
        # Поэтому midtop у самих пуль после смещения X уже не будет равен ship.rect.midtop.
        # Проверяем centerx и top отдельно.

        expected_centerx_b1 = self.ship.rect.centerx - _DOUBLE_BULLET_X_OFFSET
        expected_centerx_b2 = self.ship.rect.centerx + _DOUBLE_BULLET_X_OFFSET

        # Сравниваем с учетом того, что Bullet() может принимать x_offset, но в _fire_bullet он не используется,
        # а rect.x изменяется напрямую.
        # Bullet.x (float) инициализируется как self.rect.x.
        # self.rect.x для bullet1/2 будет ship.rect.centerx - bullet_width/2 - offset

        # Проще проверить итоговые centerx пуль
        self.assertEqual(
            bullet1.rect.centerx,
            expected_centerx_b1,
            f"Первая пуля двойного выстрела смещена некорректно по X. Ожидалось {expected_centerx_b1}, получено {bullet1.rect.centerx}",
        )
        self.assertEqual(
            bullet2.rect.centerx,
            expected_centerx_b2,
            f"Вторая пуля двойного выстрела смещена некорректно по X. Ожидалось {expected_centerx_b2}, получено {bullet2.rect.centerx}",
        )

        self.assertEqual(
            bullet1.rect.top,
            self.ship.rect.top,
            "Верхняя координата первой пули должна совпадать с верхней координатой корабля.",
        )
        self.assertEqual(
            bullet2.rect.top,
            self.ship.rect.top,
            "Верхняя координата второй пули должна совпадать с верхней координатой корабля.",
        )

    def test_bullet_limit(self):
        """Тест: ограничение на количество одновременно существующих пуль."""
        self.ship.double_fire_active = False
        self.settings.bullets_allowed = 1  # Устанавливаем лимит в 1 пулю
        self.ai_game.settings.bullets_allowed = 1  # Обновляем в ai_game.settings

        # Очищаем существующие пули на всякий случай
        self.bullets.empty()

        self.ai_game._fire_bullet()  # Первый выстрел, должна появиться 1 пуля
        self.assertEqual(
            len(self.bullets), 1, "После первого выстрела должна быть 1 пуля."
        )

        self.ai_game._fire_bullet()  # Второй выстрел, новая пуля не должна появиться
        self.assertEqual(
            len(self.bullets),
            1,
            "Количество пуль не должно превышать settings.bullets_allowed (1).",
        )

        # Проверим с двойным выстрелом и лимитом 1 - ни одна не должна добавиться, если уже есть 1.
        self.bullets.empty()
        self.settings.bullets_allowed = 1
        self.ai_game.settings.bullets_allowed = 1
        # Сначала добавляем одну пулю обычным выстрелом
        self.ship.double_fire_active = False
        self.ai_game._fire_bullet()
        self.assertEqual(
            len(self.bullets),
            1,
            "Должна быть 1 пуля после одиночного выстрела перед тестом двойного.",
        )

        # Теперь пытаемся выстрелить двойным, но лимит 1 и уже есть 1 пуля
        self.ship.double_fire_active = True
        self.ai_game._fire_bullet()
        # В AlienInvasion._fire_bullet() есть проверка: if len(self.bullets) <= self.settings.bullets_allowed - 2:
        # Если bullets_allowed = 1, то 1 <= 1 - 2 (1 <= -1) -> False. Так что 0 пуль добавится.
        self.assertEqual(
            len(self.bullets),
            1,
            "Двойной выстрел не должен был добавить пуль, так как лимит (1) уже достигнут.",
        )

        # Проверим с двойным выстрелом и лимитом 2 - должны добавиться 2 пули, если было 0.
        self.bullets.empty()
        self.settings.bullets_allowed = 2
        self.ai_game.settings.bullets_allowed = 2
        self.ship.double_fire_active = True
        self.ai_game._fire_bullet()
        self.assertEqual(
            len(self.bullets),
            2,
            "Двойной выстрел должен был добавить 2 пули при лимите 2 и пустой группе.",
        )

        # Если лимит 2 и уже есть 1 пуля, двойной выстрел не должен добавить пуль
        self.bullets.empty()
        # Добавляем одну пулю
        self.ship.double_fire_active = False
        self.ai_game._fire_bullet()  # Теперь 1 пуля в группе
        self.assertEqual(len(self.bullets), 1, "Подготовка: одна пуля в группе.")

        self.ship.double_fire_active = True  # Включаем двойной выстрел
        self.ai_game._fire_bullet()  # Пытаемся выстрелить двойным
        # len(self.bullets) = 1. self.settings.bullets_allowed = 2.
        # Условие: 1 <= 2 - 2  (1 <= 0) -> False. Ничего не добавится.
        self.assertEqual(
            len(self.bullets),
            1,
            "Двойной выстрел не должен был добавить пуль, если лимит 2, но уже есть 1 пуля (не хватает места для двух).",
        )


class TestBulletAlienCollisionLogic(unittest.TestCase):
    """Тесты для логики столкновения Пули и Пришельца."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()

        # Настройка моков Pygame, включая mixer
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        self._actual_mixer_init = getattr(pygame, "mixer", MagicMock()).init
        self._actual_mixer_Sound = getattr(pygame, "mixer", MagicMock()).Sound
        original_mixer_module = pygame.mixer if hasattr(pygame, "mixer") else None
        pygame.mixer = MagicMock()
        pygame.mixer.init = MagicMock()
        pygame.mixer.Sound = MagicMock()

        # setup_pygame_mocks мокает display, image, transform, font.
        # Важно, что font мокается, т.к. Scoreboard инициализируется и использует font.render.
        # MockPygameFont.render вернет MockSurface, что достаточно.
        setup_pygame_mocks(self)

        pygame.mixer = MagicMock()
        pygame.mixer.init = MagicMock(name="pygame.mixer.init")
        pygame.mixer.Sound = MagicMock(
            name="pygame.mixer.Sound", return_value=MagicMock(play=MagicMock())
        )

        # Моки для изображений
        ship_image_surface = MockSurface(
            (self.settings.ship_display_width, self.settings.ship_display_height), # Используем display_width/height
            is_alpha=True,
        )
        MockPygameImage.set_expected_surface(
            self.settings.ship_image_path, ship_image_surface
        )

        self.alien_image_surface = MockSurface(
            (self.settings.alien_display_width, self.settings.alien_display_height), is_alpha=True # Используем display_width/height
        )
        # Alien.py выбирает случайный путь из alien_sprite_paths. Для теста мокнем первый.
        if self.settings.alien_sprite_paths: # Check if list is not empty
            MockPygameImage.set_expected_surface(
                self.settings.alien_sprite_paths[0], self.alien_image_surface
            )
        else: # Fallback, if alien_sprite_paths is empty
             MockPygameImage.set_expected_surface(
                "dummy_alien_path_for_collision_test.png", self.alien_image_surface # Ensure a unique path if needed
            )

        self.ai_game = AlienInvasion()
        # Patch _create_fleet on the instance after it's created
        self.patcher_create_fleet = patch.object(self.ai_game, '_create_fleet', return_value=None)
        self.mock_create_fleet = self.patcher_create_fleet.start()
        self.addCleanup(self.patcher_create_fleet.stop)

        self.ai_game.stats.game_active = True
        self.stats = self.ai_game.stats
        self.sb = self.ai_game.sb  # Scoreboard создается в AlienInvasion

        # Мокаем звуки, используемые в _check_bullet_alien_collisions
        self.ai_game.sounds_explosion = [
            MagicMock(play=MagicMock())
        ]  # Список с моком звука взрыва
        self.ai_game.sound_powerup = MagicMock(play=MagicMock())  # Мок звука бонуса

        # Очищаем группы перед каждым тестом
        self.ai_game.bullets.empty()
        self.ai_game.aliens.empty()
        self.ai_game.powerups.empty()

        # Создаем тестовые объекты Bullet и Alien
        self.bullet = Bullet(self.ai_game)
        # Alien требует ai_game в конструкторе, который в свою очередь содержит settings
        self.alien = Alien(self.ai_game)

        # Устанавливаем их так, чтобы они пересекались
        self.bullet.rect.x = 100
        self.bullet.rect.y = 100
        self.bullet.rect.width = 5  # Типичные размеры пули
        self.bullet.rect.height = 15

        self.alien.rect.x = 100
        self.alien.rect.y = 100
        self.alien.rect.width = (
            self.settings.alien_display_width
        )
        self.alien.rect.height = self.settings.alien_display_height

        self.alien.assigned_powerup_type = None  # По умолчанию для первого теста

        self.ai_game.bullets.add(self.bullet)
        self.ai_game.aliens.add(self.alien)

        # Начальные значения для проверки
        self.initial_score = self.stats.score
        self.initial_aliens_destroyed = self.ai_game.aliens_destroyed_current_wave # Attribute is on AlienInvasion instance

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        if hasattr(pygame, "mixer"):
            pygame.mixer.init = self._actual_mixer_init
            pygame.mixer.Sound = self._actual_mixer_Sound
        # self.patcher_create_fleet.stop() # Handled by addCleanup

    # No longer need this mock_create_fleet in the signature as it's an instance attribute now
    @patch(
        "alien_invasion.scoreboard.Scoreboard.prep_score"
    )  # Мокаем метод prep_score у Scoreboard
    def test_collision_removes_objects_and_updates_score(self, mock_prep_score):
        """Тест: столкновение удаляет объекты, обновляет счет и вызывает prep_score."""
        self.assertEqual(
            len(self.ai_game.bullets), 1, "В начале должна быть одна пуля."
        )
        self.assertEqual(
            len(self.ai_game.aliens), 1, "В начале должен быть один пришелец."
        )

        self.ai_game._check_bullet_alien_collisions()

        self.assertEqual(
            len(self.ai_game.bullets), 0, "Пуля должна быть удалена после столкновения."
        )
        self.assertEqual(
            len(self.ai_game.aliens),
            0,
            "Пришелец должен быть удален после столкновения.",
        )
        self.mock_create_fleet.assert_called_once() # Убедимся, что мокнутый _create_fleet был вызван

        self.assertEqual(
            self.stats.score,
            self.initial_score + self.settings.alien_points,
            "Счет должен увеличиться на стоимость пришельца.",
        )
        self.assertEqual(
            self.ai_game.aliens_destroyed_current_wave, # Check attribute on ai_game
            self.initial_aliens_destroyed + 1,
            "Счетчик уничтоженных пришельцев должен увеличиться.",
        )

        mock_prep_score.assert_called_once()
        # Проверяем, что звук взрыва был вызван
        self.ai_game.sounds_explosion[0].play.assert_called_once()

    def test_collision_with_powerup_alien_spawns_powerup(self):
        """Тест: столкновение с пришельцем с бонусом создает объект PowerUp."""
        self.alien.assigned_powerup_type = "shield"  # Назначаем бонус пришельцу

        # Устанавливаем позицию пришельца так, чтобы он столкнулся с пулей (пуля в 100,100)
        # self.alien.rect это pygame.Rect, используем его атрибуты
        self.alien.rect.topleft = (100, 100)
        expected_powerup_center = self.alien.rect.center

        self.ai_game._check_bullet_alien_collisions()

        self.assertEqual(len(self.ai_game.bullets), 0, "Пуля должна быть удалена.")
        self.assertEqual(len(self.ai_game.aliens), 0, "Пришелец должен быть удален.")
        self.mock_create_fleet.assert_called_once() # Убедимся, что мокнутый _create_fleet был вызван
        self.assertEqual(len(self.ai_game.powerups), 1, "Должен появиться один бонус.")

        spawned_powerup = list(self.ai_game.powerups)[0]
        self.assertEqual(
            spawned_powerup.powerup_type, "shield", "Тип созданного бонуса некорректен."
        )
        self.assertEqual(
            spawned_powerup.rect.center,
            expected_powerup_center,
            "Бонус должен появиться в центре уничтоженного пришельца.",
        )
        # Проверяем, что звук бонуса (при подборе) НЕ вызывался, а звук взрыва - да.
        self.ai_game.sounds_explosion[0].play.assert_called_once()
        self.ai_game.sound_powerup.play.assert_not_called()  # Звук подбора бонуса здесь не должен играть


class TestShipPowerUpCollisionLogic(unittest.TestCase):
    """Тесты для логики столкновения Корабля и Бонуса."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()

        # Настройка моков Pygame, включая mixer
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        self._actual_mixer_init = getattr(pygame, "mixer", MagicMock()).init
        self._actual_mixer_Sound = getattr(pygame, "mixer", MagicMock()).Sound
        original_mixer_module = pygame.mixer if hasattr(pygame, "mixer") else None
        pygame.mixer = MagicMock()
        pygame.mixer.init = MagicMock()
        pygame.mixer.Sound = MagicMock()

        setup_pygame_mocks(self)  # Мокаем display, image, transform, font

        pygame.mixer = MagicMock()
        pygame.mixer.init = MagicMock(name="pygame.mixer.init")
        pygame.mixer.Sound = MagicMock(
            name="pygame.mixer.Sound", return_value=MagicMock(play=MagicMock())
        )

        # Моки для изображений корабля и бонусов
        ship_image_surface = MockSurface(
            (self.settings.ship_display_width, self.settings.ship_display_height), # Используем display_width/height
            is_alpha=True,
        )
        MockPygameImage.set_expected_surface(
            self.settings.ship_image_path, ship_image_surface
        )

        shield_powerup_image_surface = MockSurface(
            (20, 20), is_alpha=True
        )  # Примерный размер
        MockPygameImage.set_expected_surface(
            self.settings.powerup_shield_image_path, shield_powerup_image_surface
        )

        double_fire_powerup_image_surface = MockSurface((20, 20), is_alpha=True)
        MockPygameImage.set_expected_surface(
            self.settings.powerup_double_fire_image_path,
            double_fire_powerup_image_surface,
        )

        self.ai_game = AlienInvasion()
        self.ai_game.stats.game_active = True
        self.ship = self.ai_game.ship

        # Мокаем звуки, используемые при подборе бонусов
        self.ai_game.sound_shield_recharge = MagicMock(play=MagicMock())
        self.ai_game.sound_powerup = MagicMock(
            play=MagicMock()
        )  # Общий звук для других бонусов

        self.ai_game.powerups.empty()

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        if hasattr(pygame, "mixer"):
            pygame.mixer.init = self._actual_mixer_init
            pygame.mixer.Sound = self._actual_mixer_Sound

    def _setup_collision(self, powerup_type):
        """Вспомогательный метод для настройки столкновения корабля с бонусом."""
        self.ship.rect.x = 100
        self.ship.rect.y = 100

        # PowerUp(self, powerup_type, center_pos)
        # Изображение для PowerUp будет загружено через мок pygame.image.load
        powerup = PowerUp(self.ai_game, powerup_type, center_pos=(100, 100))
        # powerup.rect унаследует x,y от center_pos, но width/height от MockSurface
        # Убедимся, что rect корабля и бонуса пересекаются
        powerup.rect.center = self.ship.rect.center

        self.ai_game.powerups.add(powerup)
        self.assertEqual(
            len(self.ai_game.powerups),
            1,
            f"Бонус типа {powerup_type} должен быть добавлен.",
        )
        return powerup

    def test_ship_collects_shield_powerup(self):
        """Тест: корабль подбирает бонус 'щит'."""
        self._setup_collision("shield")

        # Сбрасываем состояние щита перед проверкой
        self.ship.shield_active = False
        self.ship.shield_activation_time = 0

        self.ai_game._check_ship_powerup_collisions()

        self.assertEqual(
            len(self.ai_game.powerups),
            0,
            "Бонус 'щит' должен быть удален после подбора.",
        )
        self.assertTrue(self.ship.shield_active, "Щит корабля должен активироваться.")
        self.assertNotEqual(
            self.ship.shield_activation_time,
            0,
            "Время активации щита должно быть установлено.",
        )
        self.ai_game.sound_shield_recharge.play.assert_called_once()

    @patch("pygame.time.get_ticks")
    def test_shield_powerup_duration(self, mock_get_ticks):
        """Тест: бонус 'щит' деактивируется по истечении времени."""
        self.ship.shield_active = True
        initial_activation_time = 10000  # Произвольное начальное время в мс
        self.ship.shield_activation_time = initial_activation_time

        # Устанавливаем текущее время чуть больше длительности щита
        mock_get_ticks.return_value = (
            initial_activation_time + self.settings.shield_duration + 1 # Используем shield_duration
        )

        self.ship._check_effects_duration()  # Метод Ship, который проверяет длительность эффектов

        self.assertFalse(
            self.ship.shield_active, "Щит должен деактивироваться по истечении времени."
        )

    def test_ship_collects_double_fire_powerup(self):
        """Тест: корабль подбирает бонус 'двойной огонь'."""
        self._setup_collision("double_fire")

        self.ship.double_fire_active = False
        self.ship.double_fire_activation_time = 0

        self.ai_game._check_ship_powerup_collisions()

        self.assertEqual(
            len(self.ai_game.powerups), 0, "Бонус 'двойной огонь' должен быть удален."
        )
        self.assertTrue(
            self.ship.double_fire_active, "Двойной огонь должен активироваться."
        )
        self.assertNotEqual(
            self.ship.double_fire_activation_time,
            0,
            "Время активации двойного огня должно быть установлено.",
        )
        self.ai_game.sound_powerup.play.assert_called_once()  # Общий звук для бонуса

    @patch("pygame.time.get_ticks")
    def test_double_fire_powerup_duration(self, mock_get_ticks):
        """Тест: бонус 'двойной огонь' деактивируется по истечении времени."""
        self.ship.double_fire_active = True
        initial_activation_time = 20000  # Произвольное начальное время
        self.ship.double_fire_activation_time = initial_activation_time

        mock_get_ticks.return_value = (
            initial_activation_time + self.settings.double_fire_duration + 1 # Используем double_fire_duration
        )

        self.ship._check_effects_duration()

        self.assertFalse(
            self.ship.double_fire_active,
            "Двойной огонь должен деактивироваться по истечении времени.",
        )


class TestAlienInvasionStateManagement(unittest.TestCase):
    """Тесты для управления состояниями игры AlienInvasion."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()

        # Моки для Pygame, включая mixer. `setup_pygame_mocks` уже мокает font, display, image, transform.
        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        self._actual_mixer_init = getattr(pygame, "mixer", MagicMock()).init
        self._actual_mixer_Sound = getattr(pygame, "mixer", MagicMock()).Sound
        original_mixer_module = (
            pygame.mixer if hasattr(pygame, "mixer") else None
        )  # Сохраняем ссылку на оригинальный модуль
        pygame.mixer = MagicMock()  # Заменяем модуль целиком
        pygame.mixer.init = MagicMock(name="pygame.mixer.init")
        pygame.mixer.Sound = MagicMock(
            name="pygame.mixer.Sound", return_value=MagicMock(play=MagicMock())
        )

        setup_pygame_mocks(self)  # Применяет моки для display, image, transform, font

        # Дополнительные моки, специфичные для управления состояниями
        self.mock_set_visible = patch("pygame.mouse.set_visible").start()
        self.mock_get_pos = patch("pygame.mouse.get_pos").start()
        self.mock_sys_exit = patch("sys.exit").start()

        # Моки для изображений, т.к. AlienInvasion их загружает (корабль, иконка паузы и т.д.)
        # AlienInvasion -> Ship -> self.settings.ship_image_path
        # AlienInvasion -> self.settings.ui_pause_icon_path
        # AlienInvasion -> Scoreboard -> Ship -> self.settings.ui_heart_icon_path (через sb.prep_ships -> Ship())
        # Alien (создается в _create_fleet) -> self.settings.alien_sprite_paths
        MockPygameImage.set_expected_surface( # ship_display_width/height не используются напрямую в ship.image, Ship сам масштабирует
            self.settings.ship_image_path, MockSurface((self.settings.ship_display_width, self.settings.ship_display_height)) # Используем display_width/height
        )
        MockPygameImage.set_expected_surface(
            self.settings.ui_pause_icon_path, MockSurface((32, 32))
        )
        MockPygameImage.set_expected_surface(
            self.settings.ui_heart_icon_path, MockSurface((30, 30))
        )
        # Alien.py выбирает случайный путь из alien_sprite_paths. Для теста мокнем первый.
        if self.settings.alien_sprite_paths:
            MockPygameImage.set_expected_surface(
                self.settings.alien_sprite_paths[0],
                MockSurface((self.settings.alien_display_width, self.settings.alien_display_height)), # Используем display_width/height
            )
        else: # Fallback
            MockPygameImage.set_expected_surface(
                "dummy_alien_path.png",
                MockSurface((self.settings.alien_display_width, self.settings.alien_display_height)),
            )


        # Powerup images for potential calls if game state leads to powerup creation/drawing
        MockPygameImage.set_expected_surface(
            self.settings.powerup_shield_image_path, MockSurface((20, 20))
        )
        MockPygameImage.set_expected_surface(
            self.settings.powerup_double_fire_image_path, MockSurface((20, 20))
        )

        self.ai_game = AlienInvasion(#settings_overrides={"logging_level": "CRITICAL"}
                                     )

        # Моки для звуков, которые могут быть вызваны при смене состояний или действиях
        self.ai_game.sound_laser = MagicMock(play=MagicMock())
        self.ai_game.sound_powerup = MagicMock(play=MagicMock())
        self.ai_game.sound_shield_recharge = MagicMock(play=MagicMock())
        self.ai_game.sounds_explosion = [MagicMock(play=MagicMock())]

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()
        patch.stopall()  # Останавливаем все патчи, запущенные через patch().start()

        global _original_pygame_mixer_init, _original_pygame_mixer_Sound
        if hasattr(pygame, "mixer"):
            pygame.mixer.init = self._actual_mixer_init
            pygame.mixer.Sound = self._actual_mixer_Sound

    def test_initial_state_is_menu(self):
        """Тест: начальное состояние игры - STATE_MENU."""
        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_MENU,
            "Начальное состояние игры должно быть 'menu'.",
        )

    def test_start_new_game_changes_state_to_playing_and_resets(self):
        """Тест: _start_new_game переводит игру в STATE_PLAYING и сбрасывает параметры."""
        initial_score = 1000
        initial_level = 2
        initial_ships = 1
        self.ai_game.stats.score = initial_score
        self.ai_game.stats.level = initial_level
        self.ai_game.stats.ships_left = initial_ships
        # Устанавливаем game_active в False, чтобы проверить, что _start_new_game его меняет
        self.ai_game.stats.game_active = False
        # Устанавливаем game_state в game_over, чтобы проверить, что он меняется
        self.ai_game.game_state = AlienInvasion.STATE_GAME_OVER

        self.ai_game._start_new_game()

        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_PLAYING,
            "Состояние игры должно измениться на 'playing'.",
        )
        self.assertTrue(
            self.ai_game.stats.game_active, "Флаг game_active должен стать True."
        )
        self.assertEqual(self.ai_game.stats.score, 0, "Счет должен быть сброшен.")
        self.assertEqual(
            self.ai_game.stats.level, 1, "Уровень должен быть сброшен на 1."
        )
        self.assertEqual(
            self.ai_game.stats.ships_left,
            self.settings.ship_limit,
            "Количество жизней должно быть сброшено до начального.",
        )
        self.assertTrue(
            len(self.ai_game.aliens) > 0, "Флот пришельцев должен быть создан."
        )
        self.mock_set_visible.assert_called_with(False)  # Мышь должна быть скрыта

    def test_ship_hit_last_life_changes_state_to_game_over(self):
        """Тест: потеря последнего корабля переводит игру в STATE_GAME_OVER."""
        self.ai_game.game_state = (
            AlienInvasion.STATE_PLAYING
        )  # Начинаем в состоянии игры
        self.ai_game.stats.game_active = True
        self.ai_game.stats.ships_left = 1  # Последняя жизнь

        with patch("time.sleep", return_value=None) as mock_sleep:
            self.ai_game._ship_hit()

        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_GAME_OVER,
            "Состояние игры должно измениться на 'game_over'.",
        )
        self.assertFalse(
            self.ai_game.stats.game_active, "Флаг game_active должен стать False."
        )
        self.mock_set_visible.assert_called_with(True)  # Мышь должна стать видимой

    def _create_key_event(self, key_code):
        """Вспомогательная функция для создания события нажатия клавиши."""
        return pygame.event.Event(pygame.KEYDOWN, {"key": key_code})

    def test_escape_key_in_playing_or_paused_state_goes_to_menu(self):
        """Тест: ESC в состояниях PLAYING или PAUSED переводит в меню."""
        # Тест для состояния PLAYING
        self.ai_game.game_state = AlienInvasion.STATE_PLAYING
        self.mock_set_visible.reset_mock()  # Сбрасываем мок перед проверкой

        event_esc = self._create_key_event(pygame.K_ESCAPE)
        # Передаем событие в _check_events (через мок pygame.event.get)
        with patch(
            "pygame.event.get",
            return_value=[event_esc, pygame.event.Event(pygame.QUIT)],
        ):  # QUIT для выхода из цикла _check_events
            self.ai_game._check_events()

        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_MENU,
            "ESC из PLAYING должен перевести в состояние MENU.",
        )
        self.mock_set_visible.assert_called_with(True)  # Мышь должна стать видимой

        # Тест для состояния PAUSED
        self.ai_game.game_state = AlienInvasion.STATE_PAUSED
        self.mock_set_visible.reset_mock()

        with patch(
            "pygame.event.get",
            return_value=[event_esc, pygame.event.Event(pygame.QUIT)],
        ):
            self.ai_game._check_events()

        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_MENU,
            "ESC из PAUSED должен перевести в состояние MENU.",
        )
        self.mock_set_visible.assert_called_with(True)

    def test_p_key_toggles_pause_play(self):
        """Тест: Клавиша 'P' переключает между PAUSED и PLAYING."""
        # Из PLAYING в PAUSED
        self.ai_game.game_state = AlienInvasion.STATE_PLAYING
        event_p = self._create_key_event(pygame.K_p)
        with patch(
            "pygame.event.get", return_value=[event_p, pygame.event.Event(pygame.QUIT)]
        ):
            self.ai_game._check_events()
        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_PAUSED,
            "Нажатие 'P' в PLAYING должно перевести в PAUSED.",
        )

        # Из PAUSED в PLAYING
        with patch(
            "pygame.event.get", return_value=[event_p, pygame.event.Event(pygame.QUIT)]
        ):
            self.ai_game._check_events()
        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_PLAYING,
            "Нажатие 'P' в PAUSED должно перевести в PLAYING.",
        )

    def _create_mouse_event(self, pos):
        """Вспомогательная функция для создания события клика мыши."""
        return pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}
        )  # button 1 = ЛКМ

    @patch.object(AlienInvasion, "_start_new_game")  # Мокаем метод самого объекта
    def test_menu_button_clicks(self, mock_start_new_game_method):
        """Тест: клики по кнопкам в главном меню."""
        self.ai_game.game_state = AlienInvasion.STATE_MENU
        self.mock_sys_exit.reset_mock() # Reset at the beginning of the test
        mock_start_new_game_method.reset_mock()

        # # Клик по "Новая игра"
        # self.mock_get_pos.return_value = (
        #     self.ai_game.new_game_button.rect.center
        # )  # Мокаем позицию мыши
        # event_click_new_game = self._create_mouse_event(
        #     self.ai_game.new_game_button.rect.center
        # )
        # with patch("pygame.event.get", return_value=[event_click_new_game]):
        #     self.ai_game._check_events()
        # mock_start_new_game_method.assert_called_once()
        # mock_start_new_game_method.reset_mock()

        # Клик по "Выход"
        # self.mock_sys_exit.reset_mock() # Already reset at the start
        self.mock_get_pos.return_value = self.ai_game.exit_button.rect.center
        event_click_exit = self._create_mouse_event(
            self.ai_game.exit_button.rect.center
        )
        with patch("pygame.event.get", return_value=[event_click_exit]):
            self.ai_game._check_events()
        self.mock_sys_exit.assert_called_once()

    @patch.object(AlienInvasion, "_start_new_game")
    def test_paused_menu_button_clicks(self, mock_start_new_game_method_paused):
        """Тест: клики по кнопкам в меню паузы."""
        self.ai_game.game_state = AlienInvasion.STATE_PAUSED
        self.mock_set_visible.reset_mock()  # Сбрасываем мок set_visible

        # Клик по "Продолжить"
        self.mock_get_pos.return_value = self.ai_game.resume_button.rect.center
        event_click_resume = self._create_mouse_event(
            self.ai_game.resume_button.rect.center
        )
        with patch(
            "pygame.event.get",
            return_value=[event_click_resume, pygame.event.Event(pygame.QUIT)],
        ):
            self.ai_game._check_events()
        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_PLAYING,
            "Клик 'Продолжить' должен перевести в состояние PLAYING.",
        )
        self.mock_set_visible.assert_called_with(False)  # Мышь должна скрыться

        # Клик по "Заново" (в меню паузы)
        self.ai_game.game_state = AlienInvasion.STATE_PAUSED  # Возвращаем в паузу
        self.mock_get_pos.return_value = self.ai_game.restart_button_paused.rect.center
        event_click_restart = self._create_mouse_event(
            self.ai_game.restart_button_paused.rect.center
        )
        with patch(
            "pygame.event.get",
            return_value=[event_click_restart, pygame.event.Event(pygame.QUIT)],
        ):
            self.ai_game._check_events()
        mock_start_new_game_method_paused.assert_called_once()  # _start_new_game должен быть вызван

        # Клик по "Главное меню" (в меню паузы)
        self.ai_game.game_state = AlienInvasion.STATE_PAUSED  # Возвращаем в паузу
        self.mock_set_visible.reset_mock()
        self.mock_get_pos.return_value = self.ai_game.main_menu_button.rect.center
        event_click_main_menu = self._create_mouse_event(
            self.ai_game.main_menu_button.rect.center
        )
        with patch(
            "pygame.event.get",
            return_value=[event_click_main_menu, pygame.event.Event(pygame.QUIT)],
        ):
            self.ai_game._check_events()
        self.assertEqual(
            self.ai_game.game_state,
            AlienInvasion.STATE_MENU,
            "Клик 'Главное меню' должен перевести в состояние MENU.",
        )
        self.mock_set_visible.assert_called_with(True)  # Мышь должна стать видимой


class TestAlienLogic(unittest.TestCase):
    """Тесты для логики класса Alien."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        self.settings = Settings()
        setup_pygame_mocks(self)  # Мокаем display, image, transform, font

        # Мок для изображения пришельца
        self.alien_image_mock_surface = MockSurface( # Используем display_width/height
            (self.settings.alien_display_width, self.settings.alien_display_height), is_alpha=True
        )
        # Alien.py выбирает случайный путь из alien_sprite_paths. Для теста мокнем первый.
        if self.settings.alien_sprite_paths:
            MockPygameImage.set_expected_surface(
                self.settings.alien_sprite_paths[0], self.alien_image_mock_surface
            )
        else: # Fallback
             MockPygameImage.set_expected_surface(
                "dummy_alien_path.png", self.alien_image_mock_surface
            )


        # Создаем мок ai_game, достаточный для Alien
        # Alien.__init__ использует: ai_game.screen, ai_game.settings
        # Alien.check_edges использует: self.screen_rect (полученный из ai_game.screen.get_rect())
        # Alien.update использует: self.settings.alien_speed_current, self.settings.fleet_direction
        self.mock_screen = MockSurface(
            (self.settings.screen_width, self.settings.screen_height)
        )

        # Используем MockAlienInvasion, т.к. он уже предоставляет screen и settings
        # Но нам не нужна вся сложность AlienInvasion, поэтому можно было бы и простой MagicMock
        self.ai_game_mock = MockAlienInvasion(
            self.settings, screen_surface=self.mock_screen
        )

        self.alien = Alien(self.ai_game_mock)
        self.screen_rect = self.mock_screen.get_rect()  # Для удобства в тестах

    def tearDown(self):
        """Очистка после каждого теста."""
        teardown_pygame_mocks()
        MockPygameImage.clear_expected_surfaces()

    def test_alien_check_edges_true_at_edges(self):
        """Тест: alien.check_edges() возвращает True на краях экрана."""
        # Правый край
        self.alien.rect.right = self.screen_rect.right
        self.assertTrue(
            self.alien.check_edges(),
            "check_edges() должна вернуть True на правом краю.",
        )

        # Убедимся, что немного зайдя за край, тоже True
        self.alien.rect.right = self.screen_rect.right + 10
        self.assertTrue(
            self.alien.check_edges(),
            "check_edges() должна вернуть True за правым краем.",
        )

        # Левый край
        self.alien.rect.left = self.screen_rect.left  # Обычно 0
        self.assertTrue(
            self.alien.check_edges(), "check_edges() должна вернуть True на левом краю."
        )

        # Убедимся, что немного зайдя за край, тоже True
        self.alien.rect.left = self.screen_rect.left - 10
        self.assertTrue(
            self.alien.check_edges(),
            "check_edges() должна вернуть True за левым краем.",
        )

    def test_alien_check_edges_false_in_middle(self):
        """Тест: alien.check_edges() возвращает False в середине экрана."""
        self.alien.rect.centerx = self.screen_rect.centerx
        # Убедимся, что он не касается краев
        self.alien.rect.left = self.screen_rect.centerx - self.alien.rect.width / 2
        self.alien.rect.right = self.screen_rect.centerx + self.alien.rect.width / 2

        self.assertFalse(
            self.alien.check_edges(),
            f"check_edges() должна вернуть False в середине экрана. "
            f"Alien rect: {self.alien.rect}, Screen rect: {self.screen_rect}",
        )

    def test_alien_update_moves_correctly(self):
        """Тест: alien.update() корректно смещает пришельца."""
        # Движение вправо
        self.ai_game_mock.settings.fleet_direction = 1
        self.ai_game_mock.settings.alien_speed_current = 1.5  # Пример скорости

        # Устанавливаем начальные координаты alien явно
        self.alien.rect.topleft = (100, 50)
        self.alien.x = float(self.alien.rect.x) # self.alien.x будет 100.0

        # Запоминаем float координату перед обновлением
        current_float_x_before_update = self.alien.x  # Должно быть 100.0

        self.alien.update()

        expected_float_x_after_update = current_float_x_before_update + self.ai_game_mock.settings.alien_speed_current # 100.0 + 1.5 = 101.5

        self.assertAlmostEqual(
            self.alien.x,
            expected_float_x_after_update,
            places=5,
            msg=f"Float координата self.alien.x должна обновиться. Было {current_float_x_before_update}, стало {self.alien.x}, ожидалось {expected_float_x_after_update}",
        )
        self.assertEqual(
            self.alien.rect.x,
            int(expected_float_x_after_update), # Сравниваем rect.x с int от ожидаемой float координаты
            f"Целочисленная координата rect.x пришельца должна обновиться (вправо). Ожидалось int({expected_float_x_after_update})={int(expected_float_x_after_update)}, получено {self.alien.rect.x}. Float x был {self.alien.x}",
        )

        # Движение влево
        self.ai_game_mock.settings.fleet_direction = -1
        # alien.x уже равен expected_float_x_after_update (101.5)
        current_float_x_before_second_update = self.alien.x
        self.alien.update() # fleet_direction = -1, speed = 1.5. alien.x = 101.5 - 1.5 = 100.0
        expected_float_x_after_second_update = current_float_x_before_second_update - self.ai_game_mock.settings.alien_speed_current
        self.assertAlmostEqual(
            self.alien.x,
            expected_float_x_after_second_update, # Должно быть 100.0
            places=5,
            msg="Пришелец должен сместиться влево.",
        )
        self.assertEqual(
            self.alien.rect.x,
            int(expected_float_x_after_second_update), # int(100.0) = 100
            f"Целочисленная координата rect.x пришельца должна обновиться (влево). Ожидалось int({expected_float_x_after_second_update})={int(expected_float_x_after_second_update)}, получено {self.alien.rect.x}. Float x был {self.alien.x}",
        )
