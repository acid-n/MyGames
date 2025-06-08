import os

def lerp(start, end, t):
    """Линейная интерполяция."""
    # Ограничиваем t между 0 и 1
    t = max(0.0, min(1.0, t))
    return start + t * (end - start)

_SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
_IMAGES_DIR = os.path.join(_SETTINGS_DIR, 'images')

class Settings():
    """Класс для хранения всех настроек игры Alien Invasion"""

    def __init__(self):
        """Инициализирует статические настройки игры"""
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
        self.ship_image_path = os.path.join(_IMAGES_DIR, 'ship.bmp')
        self.alien_image_path = os.path.join(_IMAGES_DIR, 'alien.bmp')

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
        self.menu_new_game_button_text = "Новая игра"
        self.menu_exit_button_text = "Выход"

        # Настройки бонусов
        # self.powerup_general_spawn_chance = 0.1 # Removed: Now per-level

        # Бонус "Щит"
        self.shield_duration = 5000  # миллисекунды (5 секунд)
        # self.shield_spawn_chance = 0.1 # Removed: Now per-level
        # Визуальные свойства бонуса "Щит"
        self.shield_powerup_color = (0, 0, 255)  # Синий
        self.shield_powerup_width = 15
        self.shield_powerup_height = 15
        self.shield_powerup_speed = 0.4 # Скорость падения бонуса
        # Визуальный эффект щита корабля
        self.ship_shield_outline_color = (0, 191, 255)  # Ярко-голубой (Deep sky blue)

        # Бонус "Двойной выстрел"
        self.double_fire_duration = 10000  # мс (10 секунд)
        # self.double_fire_spawn_chance = 0.05 # Removed: Now per-level
        # self.double_fire_min_cooldown = 15000 # Removed: Now per-level
        # Визуальные свойства бонуса "Двойной выстрел"
        self.double_fire_powerup_color = (255, 165, 0)  # Оранжевый
        self.double_fire_powerup_width = 15
        self.double_fire_powerup_height = 15
        self.double_fire_powerup_speed = 0.4 # Скорость падения бонуса

        # Level settings
        self.level_settings = [
            { # Level 1 Settings
                'min_alien_speed': 0.3,
                'alien_speed_increase_rate': 0.0,
                'min_alien_speed': 0.3,
                'alien_speed_increase_rate': 0.0, # These could also be dynamic if desired
                'alien_speed_max_level': 0.3,   # Or derived from min_alien_speed
                'fleet_drop_speed': 8,
                'aliens_per_row_factor': 0.7,
                'alien_rows_factor': 0.5,
                'alien_points': 50,
                # Power-up keys removed as they are now dynamically calculated
            },
            { # Level 2 Settings
                'min_alien_speed': 0.5,
                'alien_speed_increase_rate': 0.00005,
                'alien_speed_max_level': 0.7,
                'fleet_drop_speed': 10,
                'aliens_per_row_factor': 0.85,
                'alien_rows_factor': 0.7,
                'alien_points': 75,
            },
            { # Level 3 Settings
                'min_alien_speed': 0.7,
                'alien_speed_increase_rate': 0.0001,
                'alien_speed_max_level': 1.2,
                'fleet_drop_speed': 12,
                'aliens_per_row_factor': 1.0,
                'alien_rows_factor': 0.9,
                'alien_points': 100,
            }
        ]
        # self.level_settings can be further trimmed or removed if all aspects are dynamic
        # and no specific per-level overrides are needed.
        self.current_level_number = 1 # Default to level 1

        self.initialize_dynamic_settings(self.current_level_number)

    # --- Calculation functions for dynamic settings ---
    def calculate_alien_speed(self, level_number):
        base_speed = 0.3
        speed_at_level_50 = 1.5
        max_speed = 2.0
        t = level_number / 50.0
        calculated_speed = lerp(base_speed, speed_at_level_50, t)
        return min(calculated_speed, max_speed)

    def calculate_fleet_drop_speed(self, level_number):
        base_drop = 8
        drop_at_level_30 = 15
        max_drop = 20
        t = level_number / 30.0
        calculated_drop = lerp(base_drop, drop_at_level_30, t)
        return min(calculated_drop, max_drop)

    def calculate_aliens_per_row_factor(self, level_number):
        base_factor = 0.7
        factor_at_level_20 = 1.0
        max_factor = 1.1
        t = level_number / 20.0
        calculated_factor = lerp(base_factor, factor_at_level_20, t)
        return min(calculated_factor, max_factor)

    def calculate_alien_rows_factor(self, level_number):
        base_factor = 0.5
        factor_at_level_25 = 0.9
        max_factor = 1.0
        t = level_number / 25.0
        calculated_factor = lerp(base_factor, factor_at_level_25, t)
        return min(calculated_factor, max_factor)

    def calculate_alien_points(self, level_number):
        base_points = 50
        points_increment = 5
        max_points = 250
        calculated_points = base_points + (level_number - 1) * points_increment
        return min(calculated_points, max_points)

    # --- Calculation functions for power-up settings ---
    def calculate_shield_spawn_chance(self, level_number):
        if level_number < 1:
            return 0.0
        # Level 1: 0.0, Level 20: 0.15, Cap: 0.20
        val = lerp(0.0, 0.15, (level_number - 1) / (20.0 - 1))
        return min(val, 0.20)

    def calculate_double_fire_spawn_chance(self, level_number):
        if level_number < 3: # No double fire before level 3
            return 0.0
        # Level 3: 0.0, Level 25: 0.10, Cap: 0.15
        val = lerp(0.0, 0.10, (level_number - 3) / (25.0 - 3))
        return min(val, 0.15)

    def calculate_double_fire_min_cooldown(self, level_number):
        if level_number < 1: # Should not happen if level_number starts at 1
            level_number = 1
        # Level 1: 60000ms, Level 30: 10000ms, Min Cooldown: 8000ms
        val = lerp(60000.0, 10000.0, (level_number - 1) / (30.0 - 1))
        return max(val, 8000.0) # Ensure it doesn't go below min_cooldown

    def calculate_powerup_general_min_level_time(self, level_number):
        if level_number < 1: # Should not happen
            level_number = 1
        # Level 1: 10000ms, Level 10: 3000ms, Min Time: 2000ms
        val = lerp(10000.0, 3000.0, (level_number - 1) / (10.0 - 1))
        return max(val, 2000.0) # Ensure it doesn't go below min_time

    def get_current_level_settings(self, level_number):
        """Возвращает словарь настроек для указанного уровня, вычисляя их динамически."""
        settings = {}

        # Рассчитываем основные параметры сложности
        settings['min_alien_speed'] = self.calculate_alien_speed(level_number)
        settings['fleet_drop_speed'] = self.calculate_fleet_drop_speed(level_number)
        settings['aliens_per_row_factor'] = self.calculate_aliens_per_row_factor(level_number)
        settings['alien_rows_factor'] = self.calculate_alien_rows_factor(level_number)
        settings['alien_points'] = self.calculate_alien_points(level_number)

        # alien_speed_increase_rate и alien_speed_max_level
        settings['alien_speed_increase_rate'] = 0.00005 # Может оставаться константой или стать динамическим
        settings['alien_speed_max_level'] = settings['min_alien_speed'] # Связано с min_alien_speed

        # Динамически рассчитываемые настройки бонусов
        settings['shield_spawn_chance'] = self.calculate_shield_spawn_chance(level_number)
        settings['double_fire_spawn_chance'] = self.calculate_double_fire_spawn_chance(level_number)
        settings['double_fire_min_cooldown'] = self.calculate_double_fire_min_cooldown(level_number)
        settings['powerup_general_min_level_time'] = self.calculate_powerup_general_min_level_time(level_number)

        return settings

    def initialize_dynamic_settings(self, level_number):
        """Инициализирует настройки, изменяющиеся в ходе игры, на основе текущего уровня."""
        self.current_level_number = level_number
        level_config = self.get_current_level_settings(level_number)

        # Сброс общих настроек скорости корабля и снарядов (могут не зависеть от уровня)
        self.ship_speed = 1.5 # Или можно сделать частью level_settings, если нужно
        self.bullet_speed = 1.5 # Или можно сделать частью level_settings

        # Настройки пришельцев из данных уровня
        self.min_alien_speed = level_config['min_alien_speed']
        self.alien_speed_current = self.min_alien_speed # Начальная скорость пришельцев для уровня
        self.alien_speed_increase_rate = level_config['alien_speed_increase_rate']
        self.alien_speed_max_level = level_config['alien_speed_max_level']

        self.fleet_drop_speed = level_config['fleet_drop_speed']
        self.alien_points = level_config['alien_points']

        # Факторы для расчета количества пришельцев
        self.current_aliens_per_row_factor = level_config['aliens_per_row_factor']
        self.current_alien_rows_factor = level_config['alien_rows_factor']

        # Настройки бонусов
        self.current_shield_spawn_chance = level_config['shield_spawn_chance']
        self.current_double_fire_spawn_chance = level_config['double_fire_spawn_chance']
        self.current_double_fire_min_cooldown = level_config['double_fire_min_cooldown']
        self.current_powerup_general_min_level_time = level_config['powerup_general_min_level_time']

        # fleet_direction = 1 обозначает движение вправо, а -1 влево
        self.fleet_direction = 1

    def load_level_settings(self, new_level_number):
        """Загружает настройки для нового уровня."""
        print(f"Loading settings for level {new_level_number}")
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