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
        self.bullet_color = (255, 0, 0) # Bright red
        self.bullets_allowed = 100      # More bullets allowed

        # Настройки пришельцев
        # self.alien_speed = 1.0 # Replaced by alien_speed_current, _initial, _max, _increase_rate
        self.alien_speed_initial = 0.5  # Starting speed for aliens
        self.alien_speed_current = self.alien_speed_initial # Current alien speed, increases gradually
        self.alien_speed_max = 3.0      # Maximum speed for aliens
        self.alien_speed_increase_rate = 0.0001 # How much alien speed increases per game loop in play state
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

        # Power-up Settings
        # General spawn chance for any power-up (can be refined later if needed)
        self.powerup_general_spawn_chance = 0.1 # Example: 10% chance for A power-up to spawn

        # Shield Power-up
        self.shield_duration = 5000  # milliseconds (5 seconds)
        self.shield_spawn_chance = 0.1  # Specific chance if chosen from general spawn, or independent. Current plan: independent.
        # Shield Power-up item visual properties
        self.shield_powerup_color = (0, 0, 255)  # Blue
        self.shield_powerup_width = 15
        self.shield_powerup_height = 15
        self.shield_powerup_speed = 1.0 # Speed at which the power-up item falls
        # Ship's shield visual effect
        self.ship_shield_outline_color = (0, 191, 255)  # Deep sky blue

        # Double Fire Power-up
        self.double_fire_duration = 10000  # ms (10 seconds)
        self.double_fire_spawn_chance = 0.08 # 8% chance, slightly less than shield
        # Double Fire Power-up item visual properties
        self.double_fire_powerup_color = (255, 165, 0)  # Orange
        self.double_fire_powerup_width = 15
        self.double_fire_powerup_height = 15
        self.double_fire_powerup_speed = 1.0 # Speed at which the power-up item falls

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Инициализирует настройки, изменяющиеся в ходе игры"""
        # Reset speed settings to their initial values
        self.ship_speed = 1.5
        self.bullet_speed = 1.5
        # self.alien_speed = 1.0 # Removed, now handled by alien_speed_current being reset to alien_speed_initial
        self.alien_speed_current = self.alien_speed_initial # Reset current speed to initial for the new game/level

        # fleet_direction = 1 обозначает движение вправо, а -1 влево
        self.fleet_direction = 1

        # Подсчет очков
        self.alien_points = 50

    def increase_speed(self):
        """Увеличивает настройки скорости и стоимость пришельцев"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        # self.alien_speed *= self.speedup_scale # Now increases alien_speed_initial for next level
        self.alien_speed_initial *= self.speedup_scale # Increase base speed for the next level
        # Ensure alien_speed_initial does not exceed alien_speed_max after increase.
        # Though, current logic implies alien_speed_current is the one capped by alien_speed_max during gameplay.
        # Consider if alien_speed_initial should also be capped or if speedup_scale is managed to prevent excessive initial speeds.


        self.alien_points = int(self.alien_points * self.score_scale)

        # Логирование изменения скорости
        print(f"--- Speed Increased ---")
        print(f"New ship speed: {self.ship_speed:.2f}")
        print(f"New bullet speed: {self.bullet_speed:.2f}")
        print(f"New initial alien speed for next level: {self.alien_speed_initial:.2f}") # Updated log message
        print(f"New alien points: {self.alien_points}")
        print(f"-----------------------")