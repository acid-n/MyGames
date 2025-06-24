# -*- coding: utf-8 -*-
"""
Тесты для фоновых космических объектов (SpaceObject).
"""
import unittest
import pygame
import os
import random
from unittest.mock import MagicMock, patch

# Добавляем путь к корневой директории проекта
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alien_invasion.settings import Settings
from alien_invasion.space_object import SpaceObject, _TARGET_SIZE_RATIO_RANGE, _DRIFT_SPEED_RANGE
from alien_invasion.alien_invasion import AlienInvasion # Для теста спавна

# Отключаем звук
os.environ['SDL_AUDIODRIVER'] = 'dummy'

class TestSpaceObject(unittest.TestCase):
    """Тесты для класса SpaceObject."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen_surface = pygame.display.set_mode((1200, 800)) # Нужен для screen_rect в SpaceObject
        cls.settings = Settings()
        # Убедимся, что есть хотя бы один путь к планете для тестов
        if not cls.settings.planet_sprite_paths:
            # Создадим временный placeholder-файл, если список пуст, чтобы тест мог пройти
            # Это не лучший подход, лучше иметь тестовые ассеты.
            # Но для простоты, если список пуст, тест инициализации может упасть.
            # Предположим, что settings всегда содержит валидные пути или fallback.
            # Если нет, то это проблема конфигурации проекта.
            # В данном случае, если cls.settings.planet_sprite_paths пуст, тест test_creation_random_image пропустится.
            # А для SpaceObject нужен конкретный image_path.
            # Создадим временный PNG файл для тестов, если его нет
            cls.test_planet_image_path = "temp_test_planet.png"
            if not os.path.exists(cls.test_planet_image_path):
                try:
                    surface = pygame.Surface((10,10), pygame.SRCALPHA)
                    surface.fill((10,20,30,100))
                    pygame.image.save(surface, cls.test_planet_image_path)
                    cls.created_temp_image = True
                except pygame.error: # Может быть, если нет прав на запись или pygame не может сохранить
                    cls.test_planet_image_path = None # Не удалось создать
                    cls.created_temp_image = False
            else:
                cls.created_temp_image = False # Файл уже существовал
        else:
            cls.test_planet_image_path = cls.settings.planet_sprite_paths[0]
            cls.created_temp_image = False


    def setUp(self):
        self.screen_width = 1200
        self.screen_height = 800
        if not self.test_planet_image_path:
             self.skipTest("Не удалось получить/создать тестовое изображение планеты.")

        self.space_object = SpaceObject(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            image_path=self.test_planet_image_path
        )

    def test_initialization_size_and_alpha(self):
        """Тест: Корректная инициализация размера и альфа-канала."""
        self.assertIsNotNone(self.space_object.image, "Изображение объекта не должно быть None.")
        self.assertTrue(self.space_object.image.get_flags() & pygame.SRCALPHA, "Изображение объекта должно иметь альфа-канал.")

        min_screen_dim = min(self.screen_width, self.screen_height)
        # Проверяем, что размер объекта находится в ожидаемых пределах
        # (учитывая, что base_width или base_height масштабируется по target_ratio)
        obj_width = self.space_object.rect.width
        obj_height = self.space_object.rect.height

        # Ожидаемая минимальная и максимальная ширина/высота на основе _TARGET_SIZE_RATIO_RANGE
        # Это приблизительная проверка, так как пропорции сохраняются.
        min_possible_dim = min_screen_dim * _TARGET_SIZE_RATIO_RANGE[0]
        max_possible_dim = min_screen_dim * _TARGET_SIZE_RATIO_RANGE[1]

        self.assertTrue(min_possible_dim <= max(obj_width, obj_height) <= max_possible_dim * 1.5, # *1.5 на случай искажения пропорций
                        f"Размер объекта ({obj_width}x{obj_height}) выходит за пределы ожидаемого диапазона, основанного на {min_possible_dim}-{max_possible_dim}.")
        self.assertEqual(self.space_object.alpha, 0, "Начальная альфа должна быть 0 (fade_in).")
        self.assertEqual(self.space_object.state, 'fade_in', "Начальное состояние должно быть 'fade_in'.")

    def test_initial_position_and_velocity(self):
        """Тест: Начальная позиция за экраном и корректная скорость."""
        rect = self.space_object.rect
        # Проверяем, что объект изначально находится за пределами одной из сторон
        is_off_top = rect.bottom < 0
        is_off_bottom = rect.top > self.screen_height
        is_off_left = rect.right < 0
        is_off_right = rect.left > self.screen_width
        self.assertTrue(is_off_top or is_off_bottom or is_off_left or is_off_right, "Объект должен начинаться за пределами экрана.")

        # Проверяем скорость
        self.assertTrue(_DRIFT_SPEED_RANGE[0] <= abs(self.space_object.dx) <= _DRIFT_SPEED_RANGE[1] or \
                        _DRIFT_SPEED_RANGE[0] <= abs(self.space_object.dy) <= _DRIFT_SPEED_RANGE[1],
                        "Компоненты скорости dx или dy должны быть в пределах _DRIFT_SPEED_RANGE.")
        self.assertNotEqual(self.space_object.dx == 0 and self.space_object.dy == 0, True, "Скорость не должна быть нулевой по обоим компонентам.")

    def test_movement(self):
        """Тест: Движение объекта."""
        initial_x, initial_y = self.space_object.rect.topleft
        self.space_object.update()
        self.assertNotEqual(self.space_object.rect.topleft, (initial_x, initial_y), "Объект должен изменить позицию после update.")
        # Более точная проверка:
        expected_x = initial_x + self.space_object.dx
        expected_y = initial_y + self.space_object.dy
        self.assertAlmostEqual(self.space_object.rect.x, expected_x, delta=1.0, msg="Позиция X обновлена некорректно.")
        self.assertAlmostEqual(self.space_object.rect.y, expected_y, delta=1.0, msg="Позиция Y обновлена некорректно.")


    def test_fade_in_out_and_kill(self):
        """Тест: Логика fade-in, fade-out и самоуничтожения объекта."""
        # Fade-in
        self.space_object.creation_time = pygame.time.get_ticks() - self.space_object.fade_duration_ms // 2 # Половина времени прошла
        self.space_object.update()
        self.assertTrue(0 < self.space_object.alpha < 255, "Альфа должна быть между 0 и 255 во время fade-in.")

        self.space_object.creation_time = pygame.time.get_ticks() - self.space_object.fade_duration_ms -1 # Время вышло
        self.space_object.update()
        self.assertEqual(self.space_object.alpha, 255, "Альфа должна быть 255 после fade-in.")
        self.assertEqual(self.space_object.state, 'visible', "Состояние должно быть 'visible' после fade-in.")

        # Start fade-out
        self.space_object.start_fade_out()
        self.assertEqual(self.space_object.state, 'fade_out', "Состояние должно быть 'fade_out'.")

        # Fade-out
        self.space_object.creation_time = pygame.time.get_ticks() - self.space_object.fade_duration_ms // 2 # Половина времени прошла
        self.space_object.update()
        self.assertTrue(0 < self.space_object.alpha < 255, "Альфа должна быть между 0 и 255 во время fade-out.")

        # Kill (после fade-out и выхода за экран)
        self.space_object.creation_time = pygame.time.get_ticks() - self.space_object.fade_duration_ms - 1 # Время fade вышло
        self.space_object.alpha = 0 # Устанавливаем альфа в 0, как будто fade_out завершился
        # Перемещаем объект далеко за экран
        self.space_object.rect.x = -self.space_object.rect.width - 1000
        self.space_object.rect.y = -self.space_object.rect.height - 1000

        # Мокаем группу, чтобы проверить вызов kill
        mock_group = MagicMock(spec=pygame.sprite.Group)
        self.space_object.add(mock_group) # Добавляем в мок-группу

        self.space_object.update() # Должен вызвать kill()

        # Проверяем, что объект был удален из группы (косвенная проверка kill())
        # Это не самая надежная проверка kill, так как kill удаляет из всех групп.
        # Лучше было бы мокнуть self.kill и проверить, что он был вызван.
        # Но для этого нужно @patch.object(SpaceObject, 'kill') для каждого экземпляра, что сложнее.
        # Вместо этого проверим, что объект исчез из группы, в которую мы его добавили.
        # Однако, update может вызвать kill несколько раз, если условия сохраняются.
        # Более простой тест: если alpha == 0 и объект за экраном, он должен быть убит.
        # Мы не можем напрямую проверить, был ли kill() вызван без мока самого метода kill.
        # Поэтому этот тест в текущем виде не идеален для проверки kill.
        # Для простоты оставим как есть, но это слабое место.
        # Предположим, что если alpha=0 и объект за экраном, то kill() внутри update отработает.
        # Проверим, что объект не в группе после update, если бы он был добавлен в реальную группу.
        # Но так как мы не можем легко проверить это без изменения кода SpaceObject или сложных моков,
        # этот аспект (вызов kill) остается не полностью протестированным здесь.
        # Мы можем проверить, что если alpha = 0 и объект за экраном, то он должен быть удален.
        # В данном случае, после update() с alpha=0 и за экраном, self.space_object.alive() должно вернуть False.
        self.assertFalse(self.space_object.alive(), "Объект должен быть 'убит' (не alive), если он за экраном и alpha=0 после update.")


    @classmethod
    def tearDownClass(cls):
        if cls.created_temp_image and cls.test_planet_image_path and os.path.exists(cls.test_planet_image_path):
            try:
                os.remove(cls.test_planet_image_path)
            except OSError:
                pass # Не страшно, если не удалось удалить временный файл
        pygame.quit()

class TestSpaceObjectSpawning(unittest.TestCase):
    """Тесты для логики спавна SpaceObject в AlienInvasion."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        # cls.screen_surface = pygame.display.set_mode((1200, 800))

    def setUp(self):
        # Для AlienInvasion нужна полная инициализация, так как он создает много объектов.
        # Используем patch для мока зависимостей, которые могут мешать (например, звук)
        # или требуют много времени на инициализацию.
        # В данном случае, Settings и другие компоненты нужны.
        # Для простоты, если тесты AlienInvasion медленные, их можно вынести или оптимизировать.
        # Пока создадим полный экземпляр AlienInvasion.
        with patch('pygame.mixer.init') as mock_mixer_init, \
             patch('pygame.mixer.Sound') as mock_sound, \
             patch('pygame.mixer.music.load') as mock_music_load, \
             patch('pygame.mixer.music.play') as mock_music_play:
            # Чтобы избежать проблем с путем к highscore.json в GameStats при тестах
            with patch('alien_invasion.game_stats.GameStats._load_high_score', return_value=0), \
                 patch('alien_invasion.game_stats.GameStats._save_high_score'):
                self.ai_game = AlienInvasion()

        # Убедимся, что есть пути к планетам
        if not self.ai_game.settings.planet_sprite_paths:
            self.ai_game.settings.planet_sprite_paths.append(TestSpaceObject.test_planet_image_path) # Используем тот же временный путь
            if not TestSpaceObject.test_planet_image_path: # Если даже временного нет
                 self.skipTest("Нет доступных спрайтов планет для теста спавна.")


    def test_spawn_limit(self):
        """Тест: Не спавнится больше объектов, чем self.settings.max_space_objects."""
        self.ai_game.settings.max_space_objects = 2
        self.ai_game.space_objects.empty() # Очищаем группу перед тестом

        # Форсируем несколько попыток спавна
        for _ in range(self.ai_game.settings.max_space_objects + 2):
            # Устанавливаем время так, чтобы спавн точно произошел
            self.ai_game.last_space_object_spawn_time = pygame.time.get_ticks() - self.ai_game.current_spawn_interval - 1
            self.ai_game._try_spawn_space_object()

        self.assertLessEqual(len(self.ai_game.space_objects), self.ai_game.settings.max_space_objects,
                             "Количество космических объектов не должно превышать max_space_objects.")

    def test_spawn_uses_random_image_and_correct_params(self):
        """Тест: Спавн использует случайное изображение и корректные параметры."""
        if not self.ai_game.settings.planet_sprite_paths:
            self.skipTest("Список путей к спрайтам планет пуст.")

        self.ai_game.space_objects.empty()
        self.ai_game.last_space_object_spawn_time = pygame.time.get_ticks() - self.ai_game.current_spawn_interval - 1

        with patch('random.choice') as mock_random_choice:
            # Настраиваем mock_random_choice, чтобы он возвращал известный путь
            # Это нужно, если self.settings.planet_sprite_paths не пуст
            if self.ai_game.settings.planet_sprite_paths:
                 mock_random_choice.return_value = self.ai_game.settings.planet_sprite_paths[0]
            else: # Если список пуст, random.choice не будет вызван, или вызовет ошибку
                  # Этот случай должен быть обработан в _try_spawn_space_object или покрыт skipTest выше
                  pass

            self.ai_game._try_spawn_space_object()

            if self.ai_game.settings.planet_sprite_paths: # Только если есть пути, должен быть вызван random.choice
                mock_random_choice.assert_called_with(self.ai_game.settings.planet_sprite_paths)

        self.assertEqual(len(self.ai_game.space_objects), 1, "Должен быть создан один космический объект.")
        spawned_obj = self.ai_game.space_objects.sprites()[0]
        self.assertIsInstance(spawned_obj, SpaceObject, "Созданный объект должен быть экземпляром SpaceObject.")
        self.assertEqual(spawned_obj.fade_duration_ms, self.ai_game.settings.space_object_fade_duration_ms,
                         "Fade duration для объекта установлен не из настроек.")

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
