import json
import logging

logger = logging.getLogger(__name__)


class GameStats:
    """Отслеживание статистики для игры Alien Invasion"""

    def __init__(self, ai_game):
        """Инициализирует статистику"""
        self.settings = ai_game.settings
        self.reset_stats()  # Инициализирует ships_left, score, level

        # Игра запускается в неактивном состоянии
        self.game_active = False

        # Рекорд загружается из файла или устанавливается в 0.
        self.high_score = 0 # Initialize before attempting to load
        self._load_high_score()

    def _load_high_score(self):
        """Загружает рекордный счет из файла, если он существует."""
        try:
            with open(self.settings.highscore_filepath, "r") as f:
                self.high_score = json.load(f)
        except FileNotFoundError:
            logger.info(
                "High score file not found (%s). Starting with high score 0.",
                self.settings.highscore_filepath,
            )
            self.high_score = 0  # Файл не найден, начинаем с рекорда 0
        except json.JSONDecodeError:
            logger.warning(
                "Could not decode JSON from %s. Starting with high score 0.",
                self.settings.highscore_filepath,
            )
            self.high_score = 0
        except Exception as e:
            logger.error(
                "Could not load high score from %s due to an unexpected error: %s. Starting with high score 0.",
                self.settings.highscore_filepath,
                e,
                exc_info=True,
            )
            self.high_score = 0

    def _save_high_score(self):
        """Сохраняет текущий рекордный счет в файл."""
        try:
            with open(self.settings.highscore_filepath, "w") as f:
                json.dump(self.high_score, f)
        except Exception as e:
            logger.error(
                "Could not save high score to %s. Error: %s",
                self.settings.highscore_filepath,
                e,
                exc_info=True,
            )

    def reset_stats(self):
        """Инициализирует статистику, изменяющуюся в ходе игры"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        # Важно: self.high_score здесь НЕ сбрасывается, так как он должен сохраняться между сессиями.
        # Он загружается при инициализации GameStats и обновляется только если текущий счет его превышает.
