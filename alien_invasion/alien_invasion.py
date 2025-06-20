import sys
from time import sleep

import pygame
import pygame.mixer  # Добавлен импорт для звука
# Добавлен импорт для работы с путями (например, для SDL_AUDIODRIVER)
import os

from alien_invasion.settings import Settings
from alien_invasion.game_stats import GameStats
from alien_invasion.scoreboard import Scoreboard
from alien_invasion.button import Button
from alien_invasion.ship import Ship
from alien_invasion.bullet import Bullet
from alien_invasion.alien import Alien
from alien_invasion.powerup import PowerUp
from alien_invasion.starfield import Starfield  # Импорт класса Starfield
from alien_invasion.space_object import SpaceObject  # Added import
import random
# Импортируем math для floor, ceil, или других функций, если понадобятся.
import math
import logging

# Constants for AlienInvasion layout, timing, and game rules
logger = logging.getLogger(__name__) # Logger for this module

_MENU_BUTTON_SPACING_Y = 20
_PAUSE_MENU_BUTTON_SPACING_Y = 10
_EXPLOSION_SOUND_INDEX_START = 1
_EXPLOSION_SOUND_INDEX_END = 3 # Last index is 3, so range will be (1, 4)
_PAUSE_ICON_SIZE = (32, 32)
_MILLISECONDS_PER_SECOND = 1000
_SPACE_OBJECT_BASE_INTERVAL_S = 40
_SPACE_OBJECT_INTERVAL_VARIANCE_S = 8
_DOUBLE_BULLET_X_OFFSET = 10
_ALIEN_FLEET_BOTTOM_BUFFER_FACTOR = 2.0 # Multiplier for alien_height
_POWERUP_BASE_DROP_RATE = 0.07
_SHIELD_POWERUP_MIN_LEVEL = 2
_DOUBLE_FIRE_POWERUP_MIN_LEVEL = 3
_PAUSE_TEXT_SPACING_ABOVE_BUTTON = 20
_PAUSE_ELEMENT_TOP_MARGIN = 20
_PAUSE_ICON_TEXT_SPACING = 10


class AlienInvasion:
    """Класс для управления ресурсами и поведением игры"""

    # Состояния игры
    STATE_MENU = 'menu'
    STATE_PLAYING = 'playing'
    STATE_PAUSED = 'paused'
    STATE_GAME_OVER = 'game_over'

    def __init__(self):
        """Инициализирует игру и создает игровые ресурсы."""  # Форматирование PEP8
        pygame.init()

        # Проверка поддержки расширенных изображений (PNG)
        if not pygame.image.get_extended():
            logger.critical("Pygame собран без поддержки расширенных изображений (например, для загрузки PNG). Проверьте установку Pygame.")
            sys.exit(
                "Pygame не поддерживает PNG. Убедитесь, что SDL_image установлен с поддержкой PNG.")

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Создание экземпляра звездного поля
        self.starfield = Starfield(
            self.screen, self.settings.screen_width, self.settings.screen_height)

        # Создание экземпляра для хранения игровой статистики
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.game_state = self.STATE_MENU  # Начальное состояние игры - Меню

        # Корабль создается, но будет использоваться/рисоваться только в STATE_PLAYING
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        # Кнопки меню
        self.new_game_button = Button(self, self.settings.text_new_game_button)
        self.exit_button = Button(self, self.settings.text_exit_button)

        # Позиционирование кнопок меню
        # Расположение кнопки "Новая игра" по центру экрана
        self.new_game_button.rect.center = self.screen.get_rect().center

        # Расположение кнопки "Выход" по центру горизонтали, под кнопкой "Новая игра" с отступом
        self.exit_button.rect.centerx = self.screen.get_rect().centerx
        self.exit_button.rect.top = self.new_game_button.rect.bottom + _MENU_BUTTON_SPACING_Y

        # Кнопки меню паузы
        self.resume_button = Button(self, self.settings.text_resume_button)
        self.restart_button_paused = Button(
            self, self.settings.text_restart_button)
        self.main_menu_button = Button(
            self, self.settings.text_main_menu_button)

        # Расположение кнопки "Продолжить" (например, по центру)
        self.resume_button.rect.centerx = self.screen.get_rect().centerx
        self.resume_button.rect.centery = self.screen.get_rect().centery - \
            self.resume_button.rect.height

        # Расположение кнопки "Заново" (в меню паузы) под кнопкой "Продолжить"
        self.restart_button_paused.rect.centerx = self.screen.get_rect().centerx
        self.restart_button_paused.rect.top = self.resume_button.rect.bottom + _PAUSE_MENU_BUTTON_SPACING_Y

        # Расположение кнопки "Главное меню" под кнопкой "Заново" (в меню паузы)
        self.main_menu_button.rect.centerx = self.screen.get_rect().centerx
        self.main_menu_button.rect.top = self.restart_button_paused.rect.bottom + _PAUSE_MENU_BUTTON_SPACING_Y

        # _create_fleet() будет вызываться в _start_new_game(), а не при инициализации игры.
        # self._create_fleet() # Удалено отсюда, чтобы флот не создавался до начала новой игры.

        self.powerups = pygame.sprite.Group()
        # self.last_double_fire_spawn_time = 0 # Удалено: Заменено системой "мешка с шариками" для бонусов.
        # self.last_shield_spawn_time = 0 # Удалено: Заменено системой "мешка с шариками" для бонусов.
        # Время начала текущего уровня (в тиках pygame.time.get_ticks()).
        self.level_start_time = 0

        # Счетчики волны (могут быть полезны для отладки или специфических механик).
        self.aliens_in_wave = 0  # Общее количество пришельцев в текущей волне.
        # Количество уничтоженных пришельцев в текущей волне.
        self.aliens_destroyed_current_wave = 0
        # self.guaranteed_powerup_spawned_this_wave = False # Удалено: Заменено системой "мешка с шариками".

        # --- Начало новой последовательности инициализации аудио ---
        self.sound_system_initialized = False
        try:
            pygame.mixer.init()  # Параметры по умолчанию
            self.sound_system_initialized = True
            logger.info("Микшер Pygame успешно инициализирован с настройками по умолчанию.")
        except pygame.error as e_mixer_default:
            logger.warning("Инициализация pygame.mixer.init() по умолчанию не удалась: %s", e_mixer_default)
            logger.info("Попытка инициализации микшера с SDL_AUDIODRIVER=dummy ...")
            # Установка переменной окружения для "пустого" аудиодрайвера
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            try:
                pygame.mixer.init()
                # Система инициализирована, но это "пустой" драйвер
                self.sound_system_initialized = True
                logger.info("Микшер Pygame успешно инициализирован с SDL_AUDIODRIVER=dummy. В игре не будет звука.")
                self.settings.audio_enabled = False  # Обновляем флаг в настройках
            except pygame.error as e_mixer_dummy:
                logger.error("pygame.mixer.init() с SDL_AUDIODRIVER=dummy также не удалась: %s", e_mixer_dummy)
                logger.error("Звуковая система не может быть инициализирована. Игра будет запущена без звука.")
                self.settings.audio_enabled = False  # Обновляем флаг в настройках

        if not self.sound_system_initialized or not self.settings.audio_enabled:
            logger.warning("АУДИОСИСТЕМА ОТКЛЮЧЕНА. В ИГРЕ НЕ БУДЕТ ЗВУКОВЫХ ЭФФЕКТОВ И МУЗЫКИ.")
        # --- Конец новой последовательности инициализации аудио ---

        # Загрузка звуковых эффектов (только если аудиосистема включена)
        self.sound_laser = None
        self.sound_powerup = None
        self.sound_shield_recharge = None
        self.sounds_explosion = []

        if self.sound_system_initialized and self.settings.audio_enabled:
            try:
                # Русский комментарий: Путь к файлу звука лазера из настроек
                sfx_laser_path = self.settings.sound_laser_path
                if os.path.exists(sfx_laser_path):
                    self.sound_laser = pygame.mixer.Sound(sfx_laser_path)
                else:
                    logger.warning("Загрузка ассета не удалась: Звуковой файл не найден: %s", sfx_laser_path)

                # Путь к файлу звука подбора бонуса из настроек
                sfx_powerup_path = self.settings.sound_powerup_path
                if os.path.exists(sfx_powerup_path):
                    self.sound_powerup = pygame.mixer.Sound(sfx_powerup_path)
                else:
                    logger.warning("Загрузка ассета не удалась: Звуковой файл не найден: %s", sfx_powerup_path)

                # Путь к файлу звука перезарядки щита из настроек
                sfx_shield_path = self.settings.sound_shield_recharge_path
                if os.path.exists(sfx_shield_path):
                    self.sound_shield_recharge = pygame.mixer.Sound(
                        sfx_shield_path)
                else:
                    logger.warning("Загрузка ассета не удалась: Звуковой файл не найден: %s", sfx_shield_path)

                # Загрузка нескольких звуков взрыва с использованием паттерна из настроек
                # Предполагаем имена explosion01.ogg, explosion02.ogg, explosion03.ogg
                for i in range(_EXPLOSION_SOUND_INDEX_START, _EXPLOSION_SOUND_INDEX_END + 1):
                    # Формируем путь к звуку взрыва, используя паттерн из настроек
                    sound_path = self.settings.sound_explosion_pattern.format(
                        i)
                    if os.path.exists(sound_path):
                        self.sounds_explosion.append(
                            pygame.mixer.Sound(sound_path))
                    else:
                        logger.warning("Загрузка ассета не удалась: Звуковой файл не найден: %s", sound_path)
                if not self.sounds_explosion:
                    logger.warning("Загрузка ассета не удалась: Звуки взрыва не загружены (файлы не найдены или паттерн некорректен).")

            except pygame.error as e:
                logger.warning("Загрузка ассета не удалась: Ошибка инициализации/загрузки звуковых эффектов: %s", e, exc_info=True)

            # Загрузка и воспроизведение фоновой музыки
            # TODO: Раскомментировать и протестировать загрузку музыки, если music_volume будет добавлено в Settings.
            # try:
            #     music_path = self.settings.music_background_path # Используем путь из настроек
            #     if os.path.exists(music_path):
            #         pygame.mixer.music.load(music_path)
            #         # pygame.mixer.music.set_volume(self.settings.music_volume) # Громкость музыки (0.0 до 1.0)
            #         pygame.mixer.music.play(-1)  # -1 для бесконечного цикла
            #     else:
            #         logger.warning("Загрузка ассета не удалась: Файл фоновой музыки не найден: %s", music_path)
            # except pygame.error as e:
            #     logger.warning("Загрузка ассета не удалась: Ошибка загрузки или воспроизведения фоновой музыки %s: %s", music_path, e, exc_info=True)
        else:
            logger.info("Загрузка звуков пропущена, так как аудиосистема отключена.")

        # Загрузка UI иконок (например, для кнопки паузы)
        self.pause_icon = None
        # icon_size_ui = (32, 32) # Replaced by _PAUSE_ICON_SIZE

        try:
            # Русский комментарий: Путь к иконке паузы из настроек.
            pause_icon_path = self.settings.ui_pause_icon_path  # Используем путь из настроек
            if os.path.exists(pause_icon_path):
                self.pause_icon = pygame.image.load(
                    pause_icon_path).convert_alpha()
                self.pause_icon = pygame.transform.scale(
                    self.pause_icon, _PAUSE_ICON_SIZE)
            else:
                # Русский комментарий: Предупреждение о ненайденной иконке UI.
                logger.warning("Загрузка ассета не удалась: Иконка UI не найдена: %s", pause_icon_path)
            # Иконка gear.png (для кнопки настроек/меню) пока не используется напрямую, загрузка пропущена.
        except pygame.error as e:
            # Русский комментарий: Предупреждение об ошибке загрузки UI иконок.
            logger.warning("Загрузка ассета не удалась: Ошибка загрузки UI иконок для AlienInvasion: %s", e, exc_info=True)

        # Группа для процедурных космических объектов (планеты, галактики)
        self.space_objects = pygame.sprite.Group()
        self.last_space_object_spawn_time = pygame.time.get_ticks()
        # Интервал появления космических объектов
        self.space_object_spawn_interval_min = (_SPACE_OBJECT_BASE_INTERVAL_S - _SPACE_OBJECT_INTERVAL_VARIANCE_S) * _MILLISECONDS_PER_SECOND
        self.space_object_spawn_interval_max = (_SPACE_OBJECT_BASE_INTERVAL_S + _SPACE_OBJECT_INTERVAL_VARIANCE_S) * _MILLISECONDS_PER_SECOND
        self.current_spawn_interval = random.randint(
            self.space_object_spawn_interval_min, self.space_object_spawn_interval_max)

        # --- Кэширование Surface для текста "Пауза" ---
        # Создаем Surface для текста "Пауза" один раз при инициализации для оптимизации.
        # Используем шрифт и цвет из Scoreboard для консистентности, или можно определить отдельные настройки.
        # Важно: self.sb (Scoreboard) должен быть уже инициализирован к этому моменту.
        if hasattr(self, 'sb') and hasattr(self.sb, 'font'): # Убедимся, что sb и font существуют
            pause_font = self.sb.font
            pause_text_color = self.settings.scoreboard_text_color # или специальный цвет для паузы

            # Рендерим текст "Пауза"
            self.paused_text_surface = pause_font.render(
                self.settings.text_pause_message,
                True,
                pause_text_color,
                None # Фон прозрачный
            )
            # Применяем convert_alpha() для лучшей производительности при блиттинге, если текст с альфа-каналом или для консистентности
            self.paused_text_surface = self.paused_text_surface.convert_alpha()

            # Rect для этого Surface можно рассчитать здесь, если позиция всегда одинакова относительно чего-либо,
            # или оставить расчет в _update_screen, если позиция динамически зависит от других элементов (кнопок).
            # self.paused_text_rect = self.paused_text_surface.get_rect()
            # Пока расчет оставим в _update_screen, так как позиция зависит от кнопок.
        else:
            # Если sb или font не найдены (например, при тестировании без полного Scoreboard),
            # устанавливаем плейсхолдер или логируем ошибку.
            self.paused_text_surface = None
            logger.error("Не удалось создать кэшированный Surface для текста 'Пауза': Scoreboard или шрифт не инициализирован.")
        # --- Конец кэширования ---


    def run_game(self):
        """Запуск основного цикла игры."""  # Форматирование PEP8

        # frame_counter = 0
        # max_frames_for_profiling = 200 # Логика перенесена в main_profiled

        while True:
            # if IS_PROFILING_RUN_FLAG: # Логика перенесена в main_profiled
            #     if frame_counter >= max_frames_for_profiling:
            #         sys.exit("Profiling frame limit reached")
            #     frame_counter += 1

            # Если PROFILE_MODE глобальная или передана, можно использовать ее здесь
            # Для простоты, предположим, что если main_profiled вызывается, то мы в режиме профилирования.
            # Однако, PROFILE_MODE установлена в __main__, так что run_game не знает о ней напрямую.
            # Лучше передать это как параметр или установить атрибут в self.settings или self.
            # В данном случае, т.к. main_profiled вызывает run_game, можно положиться на то,
            # что run_profiler_and_save_stats завершит процесс.
            # Но для надежности, добавим проверку на PROFILE_MODE, если бы она была доступна здесь.
            # Поскольку PROFILE_MODE не доступна здесь напрямую, а timeout уже был,
            # попробуем более простой вариант - просто запустить и надеяться, что QUIT обработается.
            # Предыдущий таймаут был на уровне выполнения команды.
            # Попробуем еще раз, но если снова таймаут, то нужно будет передать PROFILE_MODE внутрь класса.

            # --- Начало изменения для принудительного выхода при профилировании ---
            # Этот код будет активен только если PROFILE_MODE в __main__ была True
            # и мы запустили run_profiler_and_save_stats -> main_profiled -> ai.run_game()
            # Чтобы этот код работал, нужно, чтобы AlienInvasion знал о PROFILE_MODE.
            # Проще всего это сделать, если run_profiler_and_save_stats установит
            # какой-то флаг в settings или передаст аргумент.
            # Пока что, для простоты, я оставлю этот код здесь, но он не будет работать без
            # передачи флага PROFILE_MODE в AlienInvasion.
            # Вместо этого, я буду полагаться на то, что _check_events() обработает sys.exit()
            # корректно, если Pygame сможет инициализировать display.

            # --- Коррекция: Добавим frame_counter, если PROFILE_MODE была установлена в __main__ ---
            # Старая логика с is_profiling_run удалена отсюда, так как заменена глобальным флагом и sys.exit() выше.
            self._check_events()

            # Обновление состояния звездного поля (прокрутка)
            # Выполняется всегда, чтобы звезды двигались даже в меню или на паузе.
            self.starfield.update()

            if self.game_state == self.STATE_PLAYING:
                self.ship.update()
                self._update_bullets()

                # Логика динамической сложности (DDA) внутри уровня: постепенное увеличение скорости пришельцев.
                # Эта скорость (alien_speed_current) сбрасывается для каждого нового уровня в initialize_dynamic_settings.
                if hasattr(self.settings, 'alien_speed_increase_rate') and hasattr(self.settings, 'alien_speed_max_level'):
                    if self.settings.alien_speed_current < self.settings.alien_speed_max_level:
                        self.settings.alien_speed_current += self.settings.alien_speed_increase_rate
                        # Ограничение текущей скорости максимальной скоростью для данного уровня (из alien_speed_max_level).
                        self.settings.alien_speed_current = min(
                            self.settings.alien_speed_current, self.settings.alien_speed_max_level)

                self._update_aliens()
                self.powerups.update()
                self._check_ship_powerup_collisions()
                self._try_spawn_space_object()
                self.space_objects.update()
            elif self.game_state == self.STATE_MENU:
                # Placeholder for menu update logic (e.g., self._update_menu())
                pass
            elif self.game_state == self.STATE_PAUSED:
                # Placeholder for pause screen update logic (e.g., self._update_pause_screen())
                pass

            self._update_screen()

    def _check_events(self):
        """Обрабатывает нажатия клавиш и события мыши"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Если игра в процессе или на паузе, ESC теперь всегда ведет в главное меню
                    if self.game_state == self.STATE_PLAYING or self.game_state == self.STATE_PAUSED:
                        self.game_state = self.STATE_MENU
                        # Показываем мышь в меню
                        pygame.mouse.set_visible(True)
                    # Если в главном меню или на экране конца игры, ESC по-прежнему закрывает игру
                    elif self.game_state == self.STATE_MENU or self.game_state == self.STATE_GAME_OVER:
                        sys.exit()
                elif event.key == pygame.K_p:  # Simple Pause toggle (no menu)
                    if self.game_state == self.STATE_PLAYING:
                        self.game_state = self.STATE_PAUSED
                        # No mouse visibility change for 'P' to keep it simple
                    elif self.game_state == self.STATE_PAUSED:
                        self.game_state = self.STATE_PLAYING
                        # Видимость мыши не меняется при паузе через 'P' для простоты.
                else:
                    # События клавиатуры, связанные с геймплеем
                    self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.game_state == self.STATE_MENU or self.game_state == self.STATE_GAME_OVER:
                    clicked_new_game = self.new_game_button.is_clicked(
                        mouse_pos)
                    clicked_exit = self.exit_button.is_clicked(mouse_pos)

                    if clicked_new_game:
                        self._start_new_game()
                    elif clicked_exit:
                        sys.exit()
                elif self.game_state == self.STATE_PAUSED:
                    clicked_resume = self.resume_button.is_clicked(mouse_pos)
                    clicked_restart_paused = self.restart_button_paused.is_clicked(
                        mouse_pos)
                    clicked_main_menu = self.main_menu_button.is_clicked(
                        mouse_pos)

                    if clicked_resume:
                        self.game_state = self.STATE_PLAYING
                        pygame.mouse.set_visible(False)
                    elif clicked_restart_paused:
                        self._start_new_game()  # Этот метод уже устанавливает PLAYING и скрывает мышь
                    elif clicked_main_menu:
                        self.game_state = self.STATE_MENU
                        # Убедимся, что мышь видна в меню
                        pygame.mouse.set_visible(True)

            # Отдельная обработка событий для K_p была интегрирована выше.
            # Специфичные для меню события KEYDOWN (например, навигация по меню клавишами)
            # могут быть добавлены здесь или в _check_keydown_events.
            # if self.game_state == self.STATE_MENU:
            #     pass # Пример: self._check_menu_keydown_events(event)

    # def _check_play_button(self, mouse_pos): # Метод удален, т.к. кнопки теперь специфичны для состояний.
    #     """Запускает новую игру при нажатии кнопки Play."""
    #     button_clicked = self.play_button.is_clicked(mouse_pos) # play_button больше не является общей.
    #     if button_clicked and (self.game_state == self.STATE_MENU or self.game_state == self.STATE_GAME_OVER):
    #         self._start_new_game()

    def _start_new_game(self):
        """Начинает новую игру."""
        # Сброс игровой статистики
        self.stats.reset_stats()  # Сначала сбрасываем статистику, чтобы self.stats.level стал 1
        self.settings.initialize_dynamic_settings(
            self.stats.level)  # Загрузка настроек для уровня 1
        # Флаг активности игры (может быть избыточен при наличии game_state)
        self.stats.game_active = True
        self.game_state = self.STATE_PLAYING  # Установка активного состояния игры
        # self.last_double_fire_spawn_time = 0 # Удалено (система бонусов изменена)
        # self.last_shield_spawn_time = 0 # Удалено (система бонусов изменена)
        self.level_start_time = pygame.time.get_ticks()  # Установка времени начала уровня

        # Сброс счетчиков волны
        self.aliens_in_wave = 0
        self.aliens_destroyed_current_wave = 0
        # self.guaranteed_powerup_spawned_this_wave = False # Удалено (система бонусов изменена)

        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        # Сброс элементов раунда
        self._reset_round_elements()
        # Указатель мыши скрывается
        pygame.mouse.set_visible(False)

    def _reset_round_elements(self):
        """Сбрасывает элементы, которые меняются каждый раунд/жизнь."""
        # Очистка списков пришельцев и снарядов
        self.aliens.empty()
        self.bullets.empty()
        self.powerups.empty()  # Очищаем бонусы при новой игре/раунде
        # Создание нового флота и размещение корабля в центре
        self._create_fleet()
        self.ship.center_ship()

    def _check_keydown_events(self, event):
        """Реагирует на нажатие клавиш"""
        if event.key == pygame.K_RIGHT and self.stats.game_active:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT and self.stats.game_active:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE and self.stats.game_active:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Реагирует на отпускание клавиш"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Создание нового снаряда (или двух) и включение его в группу bullets"""
        if self.ship.double_fire_active:
            # Режим "Двойной выстрел" активен
            # Убедимся, что есть место для двух снарядов
            if len(self.bullets) <= self.settings.bullets_allowed - 2:
                bullet1 = Bullet(self)
                bullet2 = Bullet(self)

                # Смещаем снаряды относительно центра корабля
                # Начальная позиция обоих снарядов - верхушка центра корабля.
                # Затем смещаем rect.x для каждого. self.y в классе Bullet уже установлен корректно.
                bullet1.rect.x -= _DOUBLE_BULLET_X_OFFSET
                bullet2.rect.x += _DOUBLE_BULLET_X_OFFSET

                self.bullets.add(bullet1)
                self.bullets.add(bullet2)
                # Звук выстрела для двойного огня (можно сделать его уникальным)
                if self.sound_system_initialized and self.settings.audio_enabled and self.sound_laser:
                    self.sound_laser.play()  # TODO: Возможно, другой звук для двойного выстрела?
        else:
            # Обычный режим огня
            if len(self.bullets) < self.settings.bullets_allowed:
                new_bullet = Bullet(self)
                self.bullets.add(new_bullet)
                # Воспроизведение звука выстрела
                if self.sound_system_initialized and self.settings.audio_enabled and self.sound_laser:
                    self.sound_laser.play()

    def _update_bullets(self):
        """Обновляет позиции снарядов и удаляет старые пули."""  # Форматирование PEP8
        # Обновление позиций снарядов
        self.bullets.update()

        # Уничтожение снарядов, вышедших за пределы экрана
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Обработка коллизий снарядов с пришельцами"""

        # Проверка попаданий в пришельцев
        # При обнаружении попадания удалить снаряд и пришельца.
        # True, True означает, что и пуля, и пришелец будут удалены.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            # collisions - это словарь, где ключ - пуля, значение - список столкнувшихся с ней пришельцев.
            for aliens_collided_list in collisions.values():
                # alien_hit - конкретный пришелец из списка столкнувшихся.
                for alien_hit in aliens_collided_list:
                    # Начисление очков за пришельца.
                    self.stats.score += self.settings.alien_points
                    # Увеличиваем счетчик уничтоженных в текущей волне.
                    self.aliens_destroyed_current_wave += 1
                    # Воспроизведение случайного звука взрыва.
                    # Убедимся, что список звуков не пуст.
                    if self.sound_system_initialized and self.settings.audio_enabled and self.sounds_explosion:
                        random.choice(self.sounds_explosion).play()

                    # Новая логика выпадения бонусов.
                    # Проверяем, был ли этому пришельцу назначен бонус при создании флота.
                    if alien_hit.assigned_powerup_type:
                        powerup_type = alien_hit.assigned_powerup_type
                        # Создаем бонус в центре уничтоженного пришельца.
                        new_powerup = PowerUp(
                            self, powerup_type, alien_hit.rect.center)
                        self.powerups.add(new_powerup)
                        # Старая логика появления бонусов (гарантированного и вероятностного),
                        # основанная на времени, кулдаунах и шансах, была удалена.
                        # Теперь бонусы выпадают только если они были предварительно назначены пришельцу.

            self.sb.prep_score()  # Обновление отображения счета.
            self.sb.check_high_score()  # Проверка и обновление рекорда.

        if not self.aliens:
            # Уничтожение существующих снарядов и создание нового флота
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Увеличение уровня.
            self.stats.level += 1
            self.sb.prep_level()
            # Загрузка настроек для нового уровня.
            self.settings.load_level_settings(self.stats.level)
            # Сброс времени начала нового уровня.
            self.level_start_time = pygame.time.get_ticks()

    def _update_aliens(self):
        """
        Проверяет, достиг ли флот края экрана,
        с последующим обновлением позиций всех пришельцев во флоте
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизий пришелец - корабль
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверить, добрались ли пришельцы до нижнего края экрана
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Проверяет, добрались ли пришельцы до нижнего края экрана"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Происходит то же, что при столкновении с кораблем
                self._ship_hit()
                break

    def _ship_hit(self):
        """Обрабатывает столкновение корабля с пришельцами"""
        if self.ship.shield_active:
            # Если щит активен, не обрабатываем попадание
            # Можно добавить логику уничтожения пришельца, столкнувшегося со щитом, если нужно
            # Например, найти столкнувшегося пришельца и вызвать alien.kill()
            # Это потребует передачи информации о столкнувшемся пришельце в _ship_hit
            # или повторной проверки столкновения здесь.
            # Пока что щит просто делает корабль неуязвимым.
            return

        if self.stats.ships_left > 0:
            # Уменьшение ships_left и обновление панели счета
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Сброс элементов раунда (очистка пришельцев, пуль, бонусов; создание нового флота; центрирование корабля).
            self._reset_round_elements()
            # Пауза для возможности игроку сориентироваться.
            sleep(self.settings.ship_hit_pause_duration)
        else:
            # Синхронизация флага активности игры (хотя game_state важнее).
            self.stats.game_active = False
            # Установка состояния "Игра окончена".
            self.game_state = self.STATE_GAME_OVER
            # Показ курсора мыши для взаимодействия с меню.
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Создание флота вторжения и сброс счетчиков для гарантированного бонуса."""
        # Создание пришельца и вычисление количества пришельцев в ряду
        # Интервал между соседними пришельцами равен ширине пришельца
        alien = Alien(self)  # Dummy alien for dimensions
        alien_width, alien_height = alien.rect.size

        # Расчет количества пришельцев в ряду (по горизонтали)
        # Учитываем отступы по краям экрана и между пришельцами.
        available_space_x = self.settings.screen_width - \
            (self.settings.fleet_screen_margin_x_factor * alien_width)
        # self.settings.alien_horizontal_spacing_factor определяет, сколько "ширин пришельца" занимает один пришелец + его отступ.
        number_aliens_x_float = available_space_x / \
            (self.settings.alien_horizontal_spacing_factor * alien_width)
        # Применяем фактор текущего уровня для плотности пришельцев в ряду.
        # current_aliens_per_row_factor (из Settings) влияет на количество пришельцев.
        # Базовое количество без фактора плотности.
        base_number_aliens_x = int(number_aliens_x_float)
        number_aliens_x = int(base_number_aliens_x *
                              self.settings.current_aliens_per_row_factor)
        # Как минимум один пришелец в ряду.
        number_aliens_x = max(1, number_aliens_x)

        # Расчет количества рядов пришельцев (по вертикали) с учетом новых правил.
        ship_height = self.ship.rect.height
        # Рассчитываем доступное вертикальное пространство для пришельцев,
        # оставляя буфер от корабля.
        available_height_for_aliens = (self.settings.screen_height -
                                       # Отступ сверху.
                                       (self.settings.fleet_top_margin_factor * alien_height) -
                                       ship_height -  # Высота корабля.
                                       # Буфер от корабля.
                                       (_ALIEN_FLEET_BOTTOM_BUFFER_FACTOR * alien_height))

        # Максимально возможное количество рядов, если бы они занимали все доступное пространство.
        # self.settings.alien_vertical_spacing_factor определяет, сколько "высот пришельца" занимает один ряд + его отступ.
        if (self.settings.alien_vertical_spacing_factor * alien_height) > 0:
            max_possible_rows = int(
                available_height_for_aliens / (self.settings.alien_vertical_spacing_factor * alien_height))
        else:
            # Избегаем деления на ноль, если вертикальный отступ некорректен.
            max_possible_rows = 0
        # Убедимся, что не отрицательное.
        max_possible_rows = max(0, max_possible_rows)

        # Рассчитываем базовое количество рядов на основе фактора (который ограничен для уровней 6+).
        # current_alien_rows_factor (из Settings) определяет, какую долю от max_possible_rows занимать.
        base_number_rows = int(max_possible_rows *
                               self.settings.current_alien_rows_factor)

        # Добавляем дополнительные ряды, определенные в settings для высоких уровней.
        final_number_rows = base_number_rows + self.settings.additional_alien_rows

        # Ограничиваем итоговое количество рядов максимально возможным на экране
        # и гарантируем хотя бы один ряд, если это возможно.
        final_number_rows = min(final_number_rows, max_possible_rows)
        final_number_rows = max(
            1, final_number_rows) if max_possible_rows > 0 else 0

        # Создание флота вторжения.
        # Используем final_number_rows вместо старого number_rows.
        for row_number in range(final_number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number,
                                   alien_width, alien_height)

        # Инициализация/сброс счетчиков волны.
        self.aliens_in_wave = len(self.aliens)
        self.aliens_destroyed_current_wave = 0
        # self.guaranteed_powerup_spawned_this_wave = False # Удалено (система бонусов изменена).

        # Логика предварительного назначения бонусов (система "мешка с шариками").
        # Эта система определяет, из каких пришельцев выпадут бонусы.
        enemy_count = len(self.aliens)
        # Базовая доля пришельцев, из которых выпадут бонусы.
        # drop_rate = 0.07 # Replaced by _POWERUP_BASE_DROP_RATE
        # Количество бонусов, которое должно выпасть на уровне.
        # Округляем до ближайшего большего целого, чтобы даже при малом количестве врагов был шанс на бонус.
        drops_per_level = math.ceil(enemy_count * _POWERUP_BASE_DROP_RATE)

        # Определяем, какие типы бонусов доступны на текущем уровне.
        available_powerup_types = []
        if self.stats.level >= _SHIELD_POWERUP_MIN_LEVEL:
            available_powerup_types.append('shield')
        if self.stats.level >= _DOUBLE_FIRE_POWERUP_MIN_LEVEL:
            available_powerup_types.append('double_fire')
        # Сюда можно добавить другие типы бонусов и условия их появления.

        if drops_per_level > 0 and available_powerup_types and enemy_count > 0:
            # Убедимся, что не пытаемся назначить больше бонусов, чем есть пришельцев.
            drops_to_assign = min(drops_per_level, enemy_count)

            # Выбираем случайных пришельцев, из которых выпадут бонусы.
            # random.sample гарантирует, что каждый выбранный пришелец уникален.
            # Преобразуем self.aliens в список, так как random.sample требует последовательность.
            try:
                # Убедимся, что drops_to_assign не отрицательное и является int
                aliens_for_powerups = random.sample(
                    list(self.aliens), int(max(0, drops_to_assign)))
            except ValueError:
                # Это может произойти, если int(max(0, drops_to_assign)) > len(list(self.aliens)),
                # но min() выше должен это предотвращать. На всякий случай.
                # В случае ошибки, бонусов не будет назначено.
                aliens_for_powerups = []

            # Назначаем каждому выбранному пришельцу случайный тип бонуса из доступных.
            for alien_obj in aliens_for_powerups:
                if available_powerup_types:  # Дополнительная проверка на случай, если список пуст.
                    chosen_powerup_type = random.choice(
                        available_powerup_types)
                    alien_obj.assigned_powerup_type = chosen_powerup_type
                    logger.debug("Assigned %s to alien at %s", chosen_powerup_type, alien_obj.rect.topleft)

    def _create_alien(self, alien_number, row_number, alien_width, alien_height, specific_image_path=None):
        """Создание пришельца и размещение его в ряду."""  # Добавлены alien_width, alien_height, specific_image_path в параметры.
        alien = Alien(
            # Передача specific_image_path конструктору Alien.
            self, specific_image_path=specific_image_path)
        # alien_width, alien_height теперь используются из аргументов, а не из alien.rect.size,
        # чтобы избежать зависимости от конкретного спрайта пришельца по умолчанию при расчете позиций.
        alien.x = alien_width + self.settings.alien_horizontal_spacing_factor * \
            alien_width * alien_number
        alien.rect.x = alien.x
        # Исправленный расчет позиции Y с использованием переданной alien_height.
        alien.rect.y = alien_height + \
            self.settings.alien_vertical_spacing_factor * alien_height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана."""  # Форматирование PEP8
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Опускает весь флот и меняет направление флота"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Обновляет изображения на экране и отображает новый экран"""
        # self.screen.fill(self.settings.bg_color) # Заменено на фон из Starfield.draw()
        # self.screen.fill(self.settings.bg_color) # Заменено на фон из Starfield.draw().
        # Отрисовка звездного поля (должна быть первой, чтобы быть на заднем плане).
        self.starfield.draw()
        # Отрисовка процедурных космических объектов (планеты, галактики).
        self.space_objects.draw(self.screen)

        # Отрисовка игровых объектов, если игра не в меню (пауза или игра).
        if self.game_state != self.STATE_MENU:
            self.ship.blitme()
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.aliens.draw(self.screen)
            self.powerups.draw(self.screen)  # Отрисовка бонусов.

        # Вывод информации о счете (всегда видим, кроме, возможно, чистого меню без игры).
        if self.game_state != self.STATE_MENU or self.stats.game_active:  # Показываем счет, если игра была начата
            self.sb.show_score()

        # Отображение элементов UI в зависимости от состояния игры.
        if self.game_state == self.STATE_GAME_OVER or self.game_state == self.STATE_MENU:
            # В состоянии "Игра окончена" или "Меню" отображаем кнопки "Новая игра" и "Выход".
            self.new_game_button.draw_button()
            self.exit_button.draw_button()
        elif self.game_state == self.STATE_PAUSED:
            # В состоянии "Пауза" отображаем сообщение "Пауза" и кнопки меню паузы.

            # Используем кэшированный Surface для текста "Пауза"
            if self.paused_text_surface:
                pause_image_to_blit = self.paused_text_surface
                screen_rect = self.screen.get_rect()

                # Рассчитываем позицию текста "Пауза" (зависит от кнопок, поэтому здесь)
                # Этот rect (current_pause_rect) используется только для позиционирования при блиттинге.
                pause_rect_y_offset = self.resume_button.rect.top - pause_image_to_blit.get_height() - _PAUSE_TEXT_SPACING_ABOVE_BUTTON
                current_pause_rect = pause_image_to_blit.get_rect(
                    centerx=screen_rect.centerx, top=pause_rect_y_offset
                )

                # Проверка, чтобы текст не уехал слишком высоко.
                if current_pause_rect.top < _PAUSE_ELEMENT_TOP_MARGIN:
                    current_pause_rect.top = _PAUSE_ELEMENT_TOP_MARGIN

                # Отрисовка иконки паузы, если она есть (логика иконки остается прежней).
                if self.pause_icon:
                    pause_icon_rect = self.pause_icon.get_rect(
                        centerx=screen_rect.centerx)
                    pause_icon_rect.bottom = current_pause_rect.top - _PAUSE_ICON_TEXT_SPACING
                    if pause_icon_rect.top < _PAUSE_ELEMENT_TOP_MARGIN:
                        pause_icon_rect.top = _PAUSE_ELEMENT_TOP_MARGIN
                    self.screen.blit(self.pause_icon, pause_icon_rect)

                # Отрисовка кэшированного текста "Пауза".
                self.screen.blit(pause_image_to_blit, current_pause_rect)
            else:
                # Fallback или логирование, если self.paused_text_surface не был создан.
                logger.error("Кэшированный Surface для текста 'Пауза' (self.paused_text_surface) отсутствует.")

            # Отрисовка кнопок меню паузы.
            self.resume_button.draw_button()
            self.restart_button_paused.draw_button()
            self.main_menu_button.draw_button()
            # Игровые элементы (корабль, пришельцы, пули, счет) уже отрисованы до этого блока,
            # поэтому они останутся видимыми на экране "Пауза", но "замороженными".

        pygame.display.flip()  # Отображение последнего отрисованного экрана.

    def _check_ship_powerup_collisions(self):
        """Проверяет столкновения корабля с бонусами."""
        # Аргумент True удаляет спрайт бонуса из группы при столкновении.
        collected_powerups = pygame.sprite.spritecollide(
            self.ship, self.powerups, True)
        for powerup in collected_powerups:
            if powerup.powerup_type == 'shield':
                self.ship.activate_shield()
                # Воспроизведение звука активации щита.
                if self.sound_system_initialized and self.settings.audio_enabled and self.sound_shield_recharge:
                    self.sound_shield_recharge.play()
            # Обработка сбора бонуса "Двойной выстрел".
            elif powerup.powerup_type == 'double_fire':
                self.ship.activate_double_fire()
                # Воспроизведение звука подбора бонуса.
                if self.sound_system_initialized and self.settings.audio_enabled and self.sound_powerup:
                    self.sound_powerup.play()
            # Добавить elif для других типов бонусов, если они появятся позже.

    def _try_spawn_space_object(self):
        # Пытается создать новый процедурный космический объект (планету/галактику), если пришло время.
        current_time = pygame.time.get_ticks()
        if current_time - self.last_space_object_spawn_time > self.current_spawn_interval:
            # Если есть доступные спрайты планет/галактик.
            if self.settings.planet_sprite_paths:
                image_path = random.choice(self.settings.planet_sprite_paths)

                new_object = SpaceObject(
                    screen_width=self.settings.screen_width,
                    screen_height=self.settings.screen_height,
                    image_path=image_path,
                    # target_size_ratio_range, speed, fade_duration_ms - используются значения по умолчанию из SpaceObject.
                )
                self.space_objects.add(new_object)
                logger.debug("Spawned SpaceObject: %s", image_path)

                self.last_space_object_spawn_time = current_time
                # Установка нового случайного интервала для следующего объекта.
                self.current_spawn_interval = random.randint(
                    self.space_object_spawn_interval_min, self.space_object_spawn_interval_max)
            # else:
                # logger.debug("Нет доступных спрайтов для космических объектов.") # Для отладки


if __name__ == '__main__':
    # Настройка базовой конфигурации логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Application started.") # Пример информационного сообщения

    # Создание экземпляра и запуск игры.
    ai = AlienInvasion()
    ai.run_game()
    logging.info("Application finished.")

# --- Код для профилирования ---
import cProfile
import pstats
import io # Для сохранения вывода pstats в строку/файл

def main_profiled(): # Обертка для профилирования
    # Настройка базовой конфигурации логирования (если еще не настроено глобально)
    # logging.basicConfig(
    #     level=logging.INFO, # Устанавливаем INFO, чтобы видеть стартовые сообщения игры
    #     format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S'
    # )
    # logging.info("Application started for profiling.")

    ai = AlienInvasion()
    # Вместо ai.run_game() с его бесконечным циклом,
    # профилируем только создание объекта AlienInvasion.
    logger.info("Профилирование: только создание объекта AlienInvasion.")
    try:
        ai = AlienInvasion() # Создание объекта
        logger.info("Профилирование: объект AlienInvasion создан успешно.")
    except Exception as e:
        logger.error(f"Профилирование: Ошибка при создании AlienInvasion: {e}", exc_info=True)
    # Симуляция игрового цикла полностью убрана для этого теста.
    logger.info("Профилирование: main_profiled завершил попытку создания объекта.")


def run_profiler_and_save_stats():
    profiler = cProfile.Profile()

    # Используем profiler.call() для более чистого перехвата исключений типа SystemExit
    try:
        profiler.call(main_profiled)
    except SystemExit as e:
        logger.warning(f"Профилирование перехвачено SystemExit: {e}. Статистика будет сохранена.")
    finally:
        profiler.disable() # Убедимся, что профилировщик выключен

    # Сохранение результатов профилирования
    s = io.StringIO()
    # Сортировка по совокупному времени, затем по общему времени, затем по количеству вызовов
    # ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative', 'tottime', 'calls')
    # Для начала достаточно сортировки по cumulative и tottime
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative', 'tottime')
    ps.print_stats(30) # Показать топ 30 функций

    # Запись в файл
    with open("profiling_results.txt", "w") as f:
        f.write(s.getvalue())

    # Опционально: сохранить бинарный файл для SnakeViz
    # profiler.dump_stats('profile_results.prof')

    # Вывод в консоль для информации
    # print("\nРезультаты профилирования сохранены в profiling_results.txt")
    # print("Топ по совокупному времени ('cumulative'):")
    # pstats.Stats(profiler).sort_stats('cumulative').print_stats(20)
    # print("\nТоп по общему времени выполнения функции ('tottime'):")
    # pstats.Stats(profiler).sort_stats('tottime').print_stats(20)


if __name__ == '__main__':
    # --- Управление запуском: обычный или профилирование ---
    PROFILE_MODE = False # Измените на True для запуска с профилированием

    if PROFILE_MODE:
        print("Запуск игры в режиме профилирования...")
        # Настройка логирования для профилирования (можно сделать менее подробным)
        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        run_profiler_and_save_stats()
        print("Профилирование завершено. Результаты в profiling_results.txt")
    else:
        # Обычный запуск игры
        # Настройка базовой конфигурации логирования (если еще не настроено)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.info("Application started.")
        ai = AlienInvasion()
        ai.run_game()
        logging.info("Application finished.")
# --- Конец кода для профилирования ---
