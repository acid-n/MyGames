import os

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
                'alien_speed_max_level': 0.3,
                'fleet_drop_speed': 8,
                'aliens_per_row_factor': 0.7,
                'alien_rows_factor': 0.5,
                'alien_points': 50,
                'shield_spawn_chance': 0.0,
                'double_fire_spawn_chance': 0.0,
                'double_fire_min_cooldown': 999999, # Effectively infinite
                'powerup_general_min_level_time': 999999, # Effectively infinite
            },
            { # Level 2 Settings
                'min_alien_speed': 0.5,
                'alien_speed_increase_rate': 0.00005,
                'alien_speed_max_level': 0.7,
                'fleet_drop_speed': 10,
                'aliens_per_row_factor': 0.85,
                'alien_rows_factor': 0.7,
                'alien_points': 75,
                'shield_spawn_chance': 0.1,
                'double_fire_spawn_chance': 0.0,
                'double_fire_min_cooldown': 999999, # Effectively infinite for DF
                'powerup_general_min_level_time': 5000, # 5 seconds
            },
            { # Level 3 Settings
                'min_alien_speed': 0.7,
                'alien_speed_increase_rate': 0.0001,
                'alien_speed_max_level': 1.2,
                'fleet_drop_speed': 12,
                'aliens_per_row_factor': 1.0,
                'alien_rows_factor': 0.9,
                'alien_points': 100,
                'shield_spawn_chance': 0.07,
                'double_fire_spawn_chance': 0.05,
                'double_fire_min_cooldown': 15000, # 15 seconds
                'powerup_general_min_level_time': 3000, # 3 seconds
            }
        ]
        self.current_level_number = 1 # Default to level 1

        self.initialize_dynamic_settings(self.current_level_number)

    def get_current_level_settings(self, level_number):
        """Возвращает словарь настроек для указанного уровня."""
        # Уровень нумеруется с 1, а список с 0
        level_index = level_number - 1
        if level_index < 0:
            level_index = 0 # Безопасность, если вдруг передан некорректный уровень
        if level_index >= len(self.level_settings):
            # Если запрошенный уровень превышает количество определенных,
            # используем настройки последнего определенного уровня (или можно ввести множители)
            return self.level_settings[-1]
        return self.level_settings[level_index]

    def initialize_dynamic_settings(self, level_number):
        """Инициализирует настройки, изменяющиеся в ходе игры, на основе текущего уровня."""
        self.current_level_number = level_number
        level_config = self.get_current_level_settings(level_number)

        # Сброс общих настроек скорости корабля и снарядов (могут не зависеть от уровня)
        self.ship_speed = 1.5 # Или можно сделать частью level_settings, если нужно
        self.bullet_speed = 1.5 # Или можно сделать частью level_settings

        # Настройки пришельцев из данных уровня
        self.min_alien_speed = level_config.get('min_alien_speed', 0.5)
        self.alien_speed_current = self.min_alien_speed # Начальная скорость пришельцев для уровня
        # Ensure alien_speed_increase_rate and alien_speed_max_level are loaded
        self.alien_speed_increase_rate = level_config.get('alien_speed_increase_rate', 0.0)
        self.alien_speed_max_level = level_config.get('alien_speed_max_level', self.alien_speed_current)

        self.fleet_drop_speed = level_config.get('fleet_drop_speed', 10)
        self.alien_points = level_config.get('alien_points', 50)

        # Факторы для расчета количества пришельцев, делаем их доступными как атрибуты
        self.current_aliens_per_row_factor = level_config.get('aliens_per_row_factor', 1.0)
        self.current_alien_rows_factor = level_config.get('alien_rows_factor', 1.0)

        # Power-up settings from level_config
        self.current_shield_spawn_chance = level_config.get('shield_spawn_chance', 0.0)
        self.current_double_fire_spawn_chance = level_config.get('double_fire_spawn_chance', 0.0)
        self.current_double_fire_min_cooldown = level_config.get('double_fire_min_cooldown', 999999)
        self.current_powerup_general_min_level_time = level_config.get('powerup_general_min_level_time', 999999)


        # fleet_direction = 1 обозначает движение вправо, а -1 влево
        self.fleet_direction = 1

        # Глобальный alien_speed_max все еще может быть полезен для DDA, если DDA выходит за рамки одного уровня
        # self.alien_speed_max = 3.0 # Этот атрибут теперь менее важен, т.к. есть alien_speed_max_level

    def load_level_settings(self, new_level_number):
        """Загружает настройки для нового уровня."""
        print(f"Loading settings for level {new_level_number}")
        self.initialize_dynamic_settings(new_level_number)

    def increase_speed(self):
        """Увеличивает настройки скорости корабля и снарядов.
           Скорость пришельцев и очки теперь управляются через load_level_settings."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        # self.min_alien_speed *= self.speedup_scale # Удалено, управляется настройками уровня
        # self.alien_points = int(self.alien_points * self.score_scale) # Удалено, управляется настройками уровня

        # Логирование изменения скорости
        print(f"--- Ship/Bullet Speed Increased (Global Scale) ---")
        print(f"New ship speed: {self.ship_speed:.2f}")
        print(f"New bullet speed: {self.bullet_speed:.2f}")
        # print(f"New min alien speed for next level: {self.min_alien_speed:.2f}") # Это больше не актуально здесь
        # print(f"New alien points: {self.alien_points}") # Это также не актуально здесь
        print(f"-----------------------")