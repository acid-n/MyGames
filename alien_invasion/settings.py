import os
import math # Импортируем модуль math для математических операций

def lerp(start, end, t):
    """Линейная интерполяция."""
    # Ограничиваем t между 0 и 1
    t = max(0.0, min(1.0, t))
    return start + t * (end - start)

_SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
# Русский комментарий: Базовая директория для всех ассетов игры.
_ASSETS_DIR = os.path.join(_SETTINGS_DIR, "..", "assets")
_IMAGES_DIR = os.path.join(_SETTINGS_DIR, 'images') # TODO: Этот путь выглядит устаревшим, проверить использование и возможно удалить в пользу _ASSETS_DIR/gfx

class Settings():
    """Класс для хранения всех настроек игры Alien Invasion"""

    def __init__(self):
        """Инициализирует статические настройки игры"""
        # Фактор максимального увеличения скорости пришельцев сверх линейной прогрессии
        # Используется для уровней 6 и выше
        self.max_speed_factor = 2.0 # Максимальный множитель скорости

        # Audio settings
        self.audio_enabled = True # Global flag for enabling/disabling audio

        # Параметры экрана
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Настройки корабля
        self.ship_speed = 1.5
        self.ship_limit = 3

        # Параметры снаряда
        self.bullet_speed = 1.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 0, 0) # Ярко-красный
        self.bullets_allowed = 100      # Больше разрешенных снарядов

        # Настройки пришельцев
        # self.alien_speed = 1.0 # Заменено на alien_speed_current, min_alien_speed, max_alien_speed
        self.min_alien_speed = 0.5  # Минимальная скорость пришельцев (начальная)
        self.alien_speed_current = self.min_alien_speed # Текущая скорость пришельцев, изменяется динамически
        self.alien_speed_max = 3.0      # Максимальная скорость пришельцев
        self.target_score_for_max_speed = 50000 # Целевой счет для достижения максимальной скорости пришельцев
        self.fleet_drop_speed = 10

        # Темп ускорения игры
        self.speedup_scale = 1.15 # Уменьшен для более плавной прогрессии
        # Темп роста стоимости пришельцев
        self.score_scale = 1.5

        # Game behavior settings
        self.ship_hit_pause_duration = 0.5

        # Fleet layout settings
        self.fleet_screen_margin_x_factor = 2.0
        self.alien_horizontal_spacing_factor = 2.0
        self.fleet_top_margin_factor = 3.0
        self.alien_vertical_spacing_factor = 2.0

        # Resource paths
        self.ship_image_path = os.path.join(_SETTINGS_DIR, '..', 'assets', 'gfx', 'ships', 'player', 'playerShip3_blue.png') # Путь относительно settings.py
        # self.alien_image_path - теперь список alien_sprite_paths
        # self.alien_image_path = os.path.join(_IMAGES_DIR, 'alien.bmp')

        # High score storage
        self.highscore_filepath = os.path.join(_SETTINGS_DIR, "highscore.json")

        # Scoreboard settings
        self.scoreboard_text_color = (30, 30, 30)
        self.scoreboard_font_size = 48
        self.scoreboard_font_name = None
        self.score_padding_right = 20
        self.score_padding_top = 20
        self.level_score_spacing = 10
        self.lives_display_padding_left = 10
        self.lives_display_padding_top = 10

        # Button settings
        self.play_button_text = "Play" # Note: This might be unused now menu buttons have specific texts
        # self.button_width = 200 # Removed for dynamic sizing
        # self.button_height = 50 # Removed for dynamic sizing
        self.button_padding_x = 40  # Total horizontal padding (20px on each side)
        self.button_padding_y = 20  # Total vertical padding (10px on each side)
        self.button_color_default = (0, 255, 0)
        self.button_text_color_default = (255, 255, 255)
        self.button_font_size = 48
        self.button_font_name = None

        # Menu settings
        # Настройки меню
        self.menu_new_game_button_text = "Новая игра"
        self.menu_exit_button_text = "Выход"

        # Настройки бонусов
        # self.powerup_general_spawn_chance = 0.1 # Удалено: Теперь рассчитывается для каждого уровня

        # Бонус "Щит"
        self.shield_duration = 5000  # миллисекунды (5 секунд)
        # self.shield_spawn_chance = 0.1 # Удалено: Теперь рассчитывается для каждого уровня
        # Визуальные свойства бонуса "Щит"
        self.shield_powerup_color = (0, 0, 255)  # Синий
        self.shield_powerup_width = 15
        self.shield_powerup_height = 15
        # self.shield_powerup_speed = 0.4 # Удалено: Скорость теперь динамическая
        # Визуальный эффект щита корабля
        self.ship_shield_outline_color = (0, 191, 255)  # Ярко-голубой (Deep sky blue)

        # Бонус "Двойной выстрел"
        self.double_fire_duration = 10000  # мс (10 секунд)
        # self.double_fire_spawn_chance = 0.05 # Удалено: Теперь рассчитывается для каждого уровня
        # self.double_fire_min_cooldown = 15000 # Удалено: Теперь рассчитывается для каждого уровня
        # Визуальные свойства бонуса "Двойной выстрел"
        self.double_fire_powerup_color = (255, 165, 0)  # Оранжевый
        self.double_fire_powerup_width = 15
        self.double_fire_powerup_height = 15
        # self.double_fire_powerup_speed = 0.4 # Удалено: Скорость теперь динамическая

        # Настройки уровней теперь полностью динамические.
        # Список self.level_settings удален, так как параметры уровней рассчитываются функциями.
        self.current_level_number = 1 # Уровень по умолчанию - 1

        # Дополнительные ряды пришельцев для высоких уровней
        self.additional_alien_rows = 0 # Инициализация значения по умолчанию

        # Русский комментарий: Пути к звуковым эффектам
        self.sound_laser_path = os.path.join(self._ASSETS_DIR, "audio", "sfx", "laser", "laser01.ogg")
        self.sound_powerup_path = os.path.join(self._ASSETS_DIR, "audio", "sfx", "powerup", "powerup01.ogg")
        self.sound_shield_recharge_path = os.path.join(self._ASSETS_DIR, "audio", "sfx", "shield", "shield_recharge.ogg")
        # Русский комментарий: Паттерн для звуков взрыва, используйте .format(i) для подстановки номера
        self.sound_explosion_pattern = os.path.join(self._ASSETS_DIR, "audio", "sfx", "explosion", "explosion0{}.ogg")

        # Русский комментарий: Пути к UI ассетам
        self.ui_heart_icon_path = os.path.join(self._ASSETS_DIR, "gfx", "ui", "icons", "heart.png")
        self.ui_score_frame_bg_path = os.path.join(self._ASSETS_DIR, "gfx", "ui", "frames", "blue_panel.png")

        # Русский комментарий: Ссылка на директорию ассетов для удобства доступа из других модулей (например, alien_invasion.py для иконки паузы)
        # Это не новый путь к ресурсу, а удобная ссылка на уже определенную _ASSETS_DIR.
        # Используем self._ASSETS_DIR, чтобы избежать конфликта имен с глобальной _ASSETS_DIR, если такой будет.
        # Имя self._ASSETS_DIR выбрано для указания, что это "внутренний" путь настроек.
        self._ASSETS_DIR = _ASSETS_DIR # Присваиваем глобально определенный путь переменной экземпляра

        self.initialize_dynamic_settings(self.current_level_number)

    # --- Calculation functions for dynamic settings ---
    # --- Функции расчета для динамических настроек ---
    def calculate_alien_speed(self, level_number):
        # Расчет скорости пришельцев в зависимости от номера уровня.
        # Для уровней 1-5 используется линейная прогрессия.
        # Для уровней 6 и выше скорость увеличивается на основе множителя,
        # который растет каждые 5 уровней, с учетом self.max_speed_factor.
        # Скорость также ограничена глобальным максимумом self.alien_speed_max.

        if level_number < 6:
            # Старая логика для уровней 1-5
            # Скорость пришельцев: базовая + прирост за уровень, с ограничением сверху
            base_speed = 0.3  # Начальная скорость на уровне 1
            speed_step_per_level = base_speed * 0.03 # Прирост 3% от базовой скорости за каждый уровень после первого
            # Рассчитанная скорость для текущего уровня
            current_speed = base_speed + (level_number - 1) * speed_step_per_level
            max_speed_cap_old_logic = 1.5 # Максимальная скорость пришельцев по старой логике
            # Возвращаем минимальное значение между рассчитанной скоростью и старым капом (1.5),
            # но также не превышая глобальный максимум self.alien_speed_max
            return min(current_speed, max_speed_cap_old_logic, self.alien_speed_max)
        else:
            # Новая логика для уровней 6 и выше
            # Рассчитываем скорость для уровня 5 по старой формуле как базовую
            level_5_base_speed = 0.3  # Базовая скорость на уровне 1
            level_5_speed_step = level_5_base_speed * 0.03
            level_5_speed = level_5_base_speed + (5 - 1) * level_5_speed_step # Скорость на уровне 5: 0.3 + 4 * 0.009 = 0.336

            # Рассчитываем множитель скорости, который увеличивается каждые 5 уровней
            # math.floor((level_number - 1) / 5) определяет, сколько раз по 5 уровней пройдено
            # Например, для уровней 6-10 это будет 1, для 11-15 это будет 2, и т.д.
            # Множитель увеличивается на 0.05 за каждый такой шаг (например, 1.05, 1.10, ...)
            speed_multiplier = min(1 + 0.05 * math.floor((level_number - 1) / 5), self.max_speed_factor)

            # Рассчитываем новую скорость путем умножения скорости 5-го уровня на множитель
            calculated_speed = level_5_speed * speed_multiplier

            # Итоговая скорость ограничивается глобальным максимальным значением self.alien_speed_max (3.0)
            # Русский комментарий: Итоговая скорость пришельцев.
            return min(calculated_speed, self.alien_speed_max)

    def calculate_fleet_drop_speed(self, level_number):
        # Расчет скорости снижения флота в зависимости от номера уровня.
        # Логика аналогична calculate_alien_speed: линейная прогрессия для уровней 1-5,
        # и множитель для уровней 6 и выше, ограниченный self.max_speed_factor.
        # Скорость также ограничена глобальным максимумом max_drop_speed_cap.

        max_drop_speed_cap = 20.0 # Максимальная скорость снижения флота (глобальный кап)

        if level_number < 6:
            # Старая логика для уровней 1-5
            # Скорость снижения флота: базовая + прирост за уровень, с ограничением сверху
            base_drop_speed = 8.0  # Начальная скорость снижения на уровне 1
            drop_speed_step_per_level = base_drop_speed * 0.025 # Прирост 2.5% от базовой скорости за каждый уровень
            # Рассчитанная скорость для текущего уровня
            current_drop_speed = base_drop_speed + (level_number - 1) * drop_speed_step_per_level
            # Возвращаем минимальное значение между рассчитанной скоростью и глобальным капом
            return min(current_drop_speed, max_drop_speed_cap)
        else:
            # Новая логика для уровней 6 и выше
            # Рассчитываем скорость снижения для уровня 5 по старой формуле как базовую
            level_5_base_drop_speed = 8.0
            level_5_drop_step = level_5_base_drop_speed * 0.025
            level_5_drop_speed = level_5_base_drop_speed + (5 - 1) * level_5_drop_step # Скорость на уровне 5: 8.0 + 4 * 0.2 = 8.8

            # Рассчитываем множитель скорости, аналогично скорости пришельцев
            speed_multiplier = min(1 + 0.05 * math.floor((level_number - 1) / 5), self.max_speed_factor)

            # Рассчитываем новую скорость снижения
            calculated_drop_speed = level_5_drop_speed * speed_multiplier

            # Итоговая скорость снижения ограничивается глобальным максимальным значением max_drop_speed_cap (20.0)
            # Русский комментарий: Итоговая скорость снижения флота.
            return min(calculated_drop_speed, max_drop_speed_cap)

    def calculate_aliens_per_row_factor(self, level_number):
        # Фактор для количества пришельцев в ряду: базовый + прирост, с ограничением
        # Этот фактор влияет на плотность пришельцев по горизонтали.
        # Больший фактор = больше пришельцев в ряду (меньше горизонтальный промежуток).
        base_aliens_per_row_factor = 0.7  # Начальный фактор на уровне 1
        # Увеличиваем на 0.01 за уровень, что эквивалентно уменьшению отступов
        factor_step_per_level = 0.01

        # Рассчитанный фактор для текущего уровня
        current_factor = base_aliens_per_row_factor + (level_number - 1) * factor_step_per_level

        # Максимальный фактор, чтобы избежать слишком плотного размещения или отрицательных отступов
        max_factor_cap = 1.1
        return min(current_factor, max_factor_cap)

    def calculate_alien_rows_factor(self, level_number):
        # Фактор для количества рядов пришельцев: базовый + прирост, с ограничением.
        # Этот фактор влияет на то, какую часть экрана по вертикали занимают пришельцы.
        # Больший фактор = больше рядов пришельцев (до определенного предела).
        # Для уровней 6 и выше, этот фактор рассчитывается как для уровня 5,
        # а фактическое добавление рядов будет управляться self.additional_alien_rows.

        # Русский комментарий: Определяем эффективный уровень для расчета базового фактора.
        # Для уровней 6 и выше, используем настройки 5-го уровня как основу.
        effective_level_for_factor = min(level_number, 5)

        base_alien_rows_factor = 0.5  # Начальный фактор на уровне 1
        # Увеличиваем на 0.0075 за уровень, чтобы ряды добавлялись плавно
        factor_step_per_level = 0.0075

        # Рассчитанный фактор для текущего (или эффективного) уровня
        current_factor = base_alien_rows_factor + (effective_level_for_factor - 1) * factor_step_per_level

        # Максимальный фактор, чтобы пришельцы не занимали весь экран и оставалось место для маневра
        max_factor_cap = 0.9
        # Русский комментарий: Итоговый фактор для расчета базового количества рядов.
        return min(current_factor, max_factor_cap)

    def calculate_alien_points(self, level_number):
        # Расчет очков за пришельца: базовое количество + прирост за уровень, с ограничением
        base_points = 50  # Базовое количество очков на уровне 1
        points_increment = 5  # Прирост очков за каждый следующий уровень
        max_points = 250  # Максимальное количество очков за пришельца

        # Рассчитанные очки для текущего уровня
        calculated_points = base_points + (level_number - 1) * points_increment
        return min(calculated_points, max_points)

    # --- Calculation functions for power-up settings ---
    # --- Функции расчета для настроек бонусов ---
    def calculate_shield_spawn_chance(self, level_number):
        # Расчет шанса появления бонуса "Щит"
        if level_number == 1:
            return 0.0  # Шанс 0 на уровне 1
        elif level_number >= 2:
            return 0.15 # Шанс 15% на уровнях 2 и выше
        else: # Для level_number < 1 (например, 0 или отрицательные)
            return 0.0

    def calculate_double_fire_spawn_chance(self, level_number):
        # Расчет шанса появления бонуса "Двойной выстрел"
        if level_number <= 2: # Уровни 1-2
            return 0.0  # Шанс 0 на уровнях 1 и 2
        elif level_number >= 3: # Уровни 3 и выше
            return 0.12 # Шанс 12% на уровнях 3 и выше
        else: # Для level_number < 1 (например, 0 или отрицательные), хотя это покрывается level_number <= 2
            return 0.0

    def calculate_double_fire_min_cooldown(self, level_number):
        # Расчет минимального времени перезарядки для бонуса "Двойной выстрел"
        if level_number < 1: # Базовая проверка для предотвращения ошибок с level_number = 0 или отрицательным
            level_number = 1
        # Уровень 1: 60000мс (60с), Уровень 30: 10000мс (10с).
        # Минимальная перезарядка теперь 15000мс (15с).
        # Время перезарядки уменьшается с ростом уровня.
        # (level_number - 1) нормализует начало диапазона уровней к 0.
        # (29.0) это диапазон изменения (30 - 1).
        val = lerp(60000.0, 10000.0, (level_number - 1) / 29.0)
        return max(val, 15000.0) # Перезарядка не может быть меньше 15000 мс

    def calculate_shield_min_cooldown(self, level_number):
        # Расчет минимального времени перезарядки для бонуса "Щит"
        if level_number < 1: # Базовая проверка
            level_number = 1
        # Параметры lerp аналогичны "Двойному выстрелу" для консистентности.
        # Уровень 1: 60000мс (60с), Уровень 30: 10000мс (10с).
        # Минимальная перезарядка 15000мс (15с).
        # Время перезарядки уменьшается с ростом уровня.
        val = lerp(60000.0, 10000.0, (level_number - 1) / 29.0)
        return max(val, 15000.0) # Перезарядка не может быть меньше 15000 мс

    def calculate_powerup_general_min_level_time(self, level_number):
        # Расчет минимального времени на уровне для появления любого бонуса
        if level_number < 1: # Базовая проверка
            level_number = 1
        # Уровень 1: 10000мс (10с), Уровень 10: 3000мс (3с), Мин. время: 2000мс (2с)
        # Минимальное время, которое должно пройти на уровне перед тем, как может появиться бонус.
        # Это время уменьшается с ростом уровня, делая появление бонусов более частым.
        # (level_number - 1) нормализует начало диапазона уровней к 0.
        # (9.0) это диапазон изменения (10 - 1).
        val = lerp(10000.0, 3000.0, (level_number - 1) / 9.0)
        return max(val, 2000.0) # Не меньше минимального установленного времени

    def get_current_level_settings(self, level_number):
        """Возвращает словарь настроек для указанного уровня, вычисляя их динамически."""
        settings = {} # Инициализация пустого словаря для настроек

        # Рассчитываем основные параметры сложности на основе номера уровня
        settings['min_alien_speed'] = self.calculate_alien_speed(level_number) # Скорость пришельцев
        settings['fleet_drop_speed'] = self.calculate_fleet_drop_speed(level_number) # Скорость снижения флота
        settings['aliens_per_row_factor'] = self.calculate_aliens_per_row_factor(level_number) # Фактор пришельцев в ряду
        settings['alien_rows_factor'] = self.calculate_alien_rows_factor(level_number) # Фактор рядов пришельцев
        settings['alien_points'] = self.calculate_alien_points(level_number) # Очки за пришельца

        # alien_speed_increase_rate и alien_speed_max_level - эти параметры больше не используются
        # в контексте прогрессии между уровнями, так как скорость теперь полностью определяется
        # уровнем через calculate_alien_speed. Они могут быть нужны для DDA внутри одного уровня,
        # но это выходит за рамки текущей задачи. Оставим их пока для обратной совместимости
        # или будущих доработок, но установим в значения, не влияющие на текущую логику.
        settings['alien_speed_increase_rate'] = 0.0 # Прирост скорости внутри уровня (для DDA, пока не используется)
        settings['alien_speed_max_level'] = settings['min_alien_speed'] # Макс. скорость на уровне (для DDA, привязана к базовой)

        # Динамически рассчитываемые настройки бонусов
        settings['shield_spawn_chance'] = self.calculate_shield_spawn_chance(level_number) # Шанс появления щита
        settings['shield_min_cooldown'] = self.calculate_shield_min_cooldown(level_number) # Перезарядка щита
        settings['double_fire_spawn_chance'] = self.calculate_double_fire_spawn_chance(level_number) # Шанс двойного выстрела
        settings['double_fire_min_cooldown'] = self.calculate_double_fire_min_cooldown(level_number) # Перезарядка двойного выстрела
        settings['powerup_general_min_level_time'] = self.calculate_powerup_general_min_level_time(level_number) # Мин. время для бонуса

        return settings # Возвращаем словарь с рассчитанными настройками

    def initialize_dynamic_settings(self, level_number):
        """Инициализирует настройки, изменяющиеся в ходе игры, на основе текущего уровня."""
        self.current_level_number = level_number # Сохраняем номер текущего уровня
        # Получаем конфигурацию для текущего уровня с помощью динамических расчетов
        level_config = self.get_current_level_settings(level_number)

        # Сброс общих настроек скорости корабля и снарядов.
        # Эти параметры могут быть сделаны зависимыми от уровня, если потребуется в будущем,
        # но пока они остаются фиксированными или изменяются через другие механизмы (например, `increase_speed`).
        self.ship_speed = 1.5
        self.bullet_speed = 1.5

        # Настройки пришельцев из данных уровня, полученных из level_config
        self.min_alien_speed = level_config['min_alien_speed'] # Минимальная/начальная скорость пришельцев для уровня
        self.alien_speed_current = self.min_alien_speed # Текущая скорость пришельцев (может меняться в течении уровня DDA)
        self.alien_speed_increase_rate = level_config['alien_speed_increase_rate'] # Коэффициент увеличения скорости (для DDA)
        self.alien_speed_max_level = level_config['alien_speed_max_level'] # Максимальная скорость на данном уровне (для DDA)

        self.fleet_drop_speed = level_config['fleet_drop_speed'] # Скорость снижения флота для уровня
        self.alien_points = level_config['alien_points'] # Очки за пришельца для уровня

        # Факторы для расчета количества пришельцев, применяемые в create_fleet()
        self.current_aliens_per_row_factor = level_config['aliens_per_row_factor']
        self.current_alien_rows_factor = level_config['alien_rows_factor']

        # Русский комментарий: Установка количества дополнительных рядов пришельцев.
        # Для уровней 1-5 дополнительных рядов нет.
        # Начиная с уровня 6, каждые 5 уровней добавляется один дополнительный ряд.
        if level_number >= 6:
            # math.floor((level_number - 1) / 5) определяет количество полных "пятерок" уровней сверх первого.
            # Например, для уровней 6-10 это 1, для 11-15 это 2, и т.д.
            self.additional_alien_rows = math.floor((level_number - 1) / 5)
        else:
            self.additional_alien_rows = 0
        # print(f"Level {level_number}: Additional alien rows set to {self.additional_alien_rows}") # Для отладки

        # Настройки бонусов, загруженные для текущего уровня
        self.current_shield_spawn_chance = level_config['shield_spawn_chance']
        self.current_shield_min_cooldown = level_config['shield_min_cooldown']
        self.current_double_fire_spawn_chance = level_config['double_fire_spawn_chance']
        self.current_double_fire_min_cooldown = level_config['double_fire_min_cooldown']
        self.current_powerup_general_min_level_time = level_config['powerup_general_min_level_time']

        # Расчет скорости падения бонусов
        base_fall_speed_ratio = 0.50 # Базовая скорость падения бонуса (50% от минимальной скорости пришельцев на данном уровне)
        base_powerup_speed = self.min_alien_speed * base_fall_speed_ratio

        powerup_speed_multiplier = 1.0 # Множитель скорости падения для уровней 6+
        if level_number >= 6:
            # Множитель увеличивается на 0.05 за каждые 5 уровней (аналогично скорости пришельцев)
            powerup_speed_multiplier = 1 + 0.05 * math.floor((level_number - 1) / 5)
            # Ограничение множителя скорости падения (аналогично пришельцам, используем тот же self.max_speed_factor)
            powerup_speed_multiplier = min(powerup_speed_multiplier, self.max_speed_factor)

        # Итоговая скорость падения бонуса
        final_powerup_speed = base_powerup_speed * powerup_speed_multiplier

        # Ограничение: скорость падения не должна превышать минимальную скорость пришельцев на уровне
        max_powerup_speed_cap = self.min_alien_speed
        final_powerup_speed = min(final_powerup_speed, max_powerup_speed_cap)

        # Устанавливаем рассчитанную скорость для всех типов бонусов
        self.current_shield_powerup_speed = final_powerup_speed
        self.current_double_fire_powerup_speed = final_powerup_speed

        # fleet_direction = 1 обозначает движение вправо, а -1 влево.
        # Направление сбрасывается на каждом уровне или при инициализации.
        self.fleet_direction = 1

        # Русский комментарий: Пути к спрайтам пришельцев
        self.alien_sprite_paths = []
        base_alien_gfx_path = os.path.join(_SETTINGS_DIR, '..', 'assets', 'gfx', 'ships', 'aliens')
        for i in range(1, 25): # Загружаем все 24 спрайта alien_ship_01.png ... alien_ship_24.png
            path = os.path.join(base_alien_gfx_path, f"alien_ship_{i:02d}.png") # Например, alien_ship_01.png
            if os.path.exists(path):
                self.alien_sprite_paths.append(path)
            else:
                print(f"WARNING: Asset not found: Alien sprite not found - {path}")

        if not self.alien_sprite_paths:
            print("CRITICAL ERROR: No alien sprites loaded. Using fallback 'alien.bmp'.")
            # Fallback на старый спрайт, если новые не найдены
            # _IMAGES_DIR is defined globally, so we can use it directly.
            self.alien_sprite_paths.append(os.path.join(_IMAGES_DIR, 'alien.bmp'))

        self.current_alien_image_path = None # Будет устанавливаться в Alien.__init__

        # Русский комментарий: Пути к спрайтам планет и галактик
        self.planet_sprite_paths = []
        base_planet_gfx_path = os.path.join(_SETTINGS_DIR, '..', 'assets', 'gfx', 'planets')
        # Предположим, что файлы называются planet01.png, planet02.png, galaxy01.png и т.д.
        # Пользователю нужно будет обеспечить наличие этих файлов.
        # Пример нескольких файлов:
        planet_files = ["planet01.png", "planet02.png", "planet03.png", "galaxy01.png", "galaxy02.png"]
        for p_file in planet_files:
            path = os.path.join(base_planet_gfx_path, p_file)
            if os.path.exists(path):
                self.planet_sprite_paths.append(path)
            else:
                print(f"WARNING: Asset not found: Planet/Galaxy sprite not found - {path}")

        if not self.planet_sprite_paths:
            print("INFO: No planet/galaxy sprites loaded.")
            # Можно добавить дефолтный, если это критично, но для фоновых объектов это может быть не обязательно.

    def load_level_settings(self, new_level_number):
        """Загружает настройки для нового уровня, используя динамические расчеты."""
        # print(f"Loading settings for level {new_level_number}") # Старый лог на английском
        print(f"Загрузка настроек для уровня {new_level_number}") # Лог на русском
        self.initialize_dynamic_settings(new_level_number)

    def increase_speed(self):
        """Увеличивает настройки скорости корабля и снарядов.
           Скорость пришельцев и очки теперь управляются через load_level_settings (динамически)."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        # self.min_alien_speed и self.alien_points больше не масштабируются здесь

        # Логирование изменения скорости
        print(f"--- Ship/Bullet Speed Increased (Global Scale) ---")
        print(f"New ship speed: {self.ship_speed:.2f}")
        print(f"New bullet speed: {self.bullet_speed:.2f}")
        # print(f"New min alien speed for next level: {self.min_alien_speed:.2f}") # Это больше не актуально здесь
        # print(f"New alien points: {self.alien_points}") # Это также не актуально здесь
        print(f"-----------------------")