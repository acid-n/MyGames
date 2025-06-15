import pygame.font
import os # Added import
import pygame # Added import
from pygame.sprite import Group
from ship import Ship

class Scoreboard():
    """Класс для вывода игровой информации"""

    def __init__(self, ai_game):
        """Инициализирует атрибуты подстчета очков"""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Настройки шрифта для вывода счета
        self.text_color = self.settings.scoreboard_text_color
        self.font = pygame.font.SysFont(self.settings.scoreboard_font_name, self.settings.scoreboard_font_size)

        # Загрузка UI иконок
        self.heart_icon = None
        self.star_icon = None # Пока не используется активно
        self.flag_icon = None # Пока не используется активно

        icon_size = (32, 32) # Требуемый размер иконок

        try:
            # Иконка для жизней (сердце)
            heart_icon_path = "assets/gfx/ui/icons/heart.png" # Убедитесь, что имя файла корректно
            if os.path.exists(heart_icon_path):
                self.heart_icon = pygame.image.load(heart_icon_path).convert_alpha()
                self.heart_icon = pygame.transform.scale(self.heart_icon, icon_size)
            else:
                print(f"WARNING: UI asset not found: {heart_icon_path}. Feature may be disabled or use fallback.")

        except pygame.error as e:
            print(f"WARNING: UI asset not found: Error loading UI icons for Scoreboard: {e}. Feature may be disabled or use fallback.")

        # Загрузка элементов Sci-Fi рамки для счета
        self.score_frame_elements = {}
        self.score_frame_active = False # Флаг, показывающий, удалось ли загрузить рамку
        try:
            # Русский комментарий: Загружаем углы. Предполагаем, что все углы одного размера.
            # Реальные имена файлов из Kenney UI Pack Sci-Fi могут отличаться.
            # Например, 'buttonSquare_blue_pressed.png' может быть использован как фон,
            # а элементы типа 'borderSmall_TL.png' как углы/грани.
            # Здесь мы используем плейсхолдеры из FRAME_ELEMENTS_PATHS.

            # Пример загрузки одного элемента для демонстрации
            frame_bg_path = "assets/gfx/ui/frames/blue_panel.png" # Замените на реальный файл из пака
            if os.path.exists(frame_bg_path):
                self.score_frame_elements['background'] = pygame.image.load(frame_bg_path).convert_alpha()
                # Предполагаем, что рамка будет вокруг текущего счета и рекорда.
                # Размеры рамки нужно будет адаптировать.
                self.score_frame_active = True # Помечаем, что хотя бы фон загружен
                print(f"INFO: UI asset loaded: Score frame background '{frame_bg_path}'.")
            else:
                print(f"WARNING: UI asset not found: Score frame background '{frame_bg_path}'. Frame will be inactive.")
                self.score_frame_active = False

            # Дополнительно можно загрузить углы и грани, если используется 9-patch подход
            # self.score_frame_elements['top_left'] = pygame.image.load(FRAME_ELEMENTS_PATHS['top_left']).convert_alpha()
            # ... и так далее для других элементов.
            # Пока ограничимся фоном для простоты.

        except pygame.error as e:
            print(f"WARNING: UI asset not found: Error loading score frame elements: {e}. Frame will be inactive.")
            self.score_frame_active = False

        # Подготовка изображений счетов
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self):
        """Преобразует текущий счет в графическое изображение"""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)

        # Русский комментарий: Если рамка активна, делаем фон текста прозрачным и добавляем отступы
        text_bg_color = self.settings.bg_color
        padding_x = self.settings.score_padding_right
        padding_y = self.settings.score_padding_top

        if self.score_frame_active and 'background' in self.score_frame_elements:
            text_bg_color = None # Прозрачный фон для текста
            # Предположим, что рамка дает нам некоторый внутренний отступ.
            # Эти значения нужно будет настроить в зависимости от вида рамки.
            # Например, если у рамки есть своя граница в 10px.
            # padding_x += 10
            # padding_y += 10
            # Для простоты пока оставим стандартные отступы, но фон сделаем прозрачным.

        self.score_image = self.font.render(score_str, True, self.text_color, text_bg_color)

        # Вывод счета в правой верхней части экрана
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - padding_x
        self.score_rect.top = padding_y

    def prep_high_score(self):
        """Преобразует рекордный счет в графическое изображение"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = "{:,}".format(high_score)

        text_bg_color_high = self.settings.bg_color
        if self.score_frame_active and 'background' in self.score_frame_elements:
            text_bg_color_high = None # Прозрачный фон для текста

        self.high_score_image = self.font.render(high_score_str, True, self.text_color, text_bg_color_high)

        # Рекорд выравнивается по центру верхней стороны
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.settings.score_padding_top # Используем общий отступ сверху

    def prep_level(self):
        """Преобразует уровень в графическое изображение"""
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str, True, self.text_color, self.settings.bg_color)

        # Уровень выводится под текущим счетом
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + self.settings.level_score_spacing

    def prep_ships(self):
        # Русский комментарий: Готовит отображение количества жизней с использованием иконки сердца.
        if self.heart_icon:
            self.ships_items_for_draw = [] # Список для хранения того, что нужно отрисовать (иконка + текст)

            # Иконка сердца
            heart_rect = self.heart_icon.get_rect()
            heart_rect.left = self.settings.lives_display_padding_left
            heart_rect.top = self.settings.lives_display_padding_top
            self.ships_items_for_draw.append({'image': self.heart_icon, 'rect': heart_rect})

            # Текстовое представление количества жизней (например, "x3")
            ships_str = f"x{self.stats.ships_left}"
            # Используем тот же шрифт и цвет, что и для счета
            ships_text_img = self.font.render(ships_str, True,
                                              self.text_color, self.settings.bg_color) # bg_color может быть None для прозрачности
            ships_text_rect = ships_text_img.get_rect()
            # Позиционируем текст справа от иконки сердца
            ships_text_rect.left = heart_rect.right + 5 # Небольшой отступ
            ships_text_rect.centery = heart_rect.centery
            self.ships_items_for_draw.append({'image': ships_text_img, 'rect': ships_text_rect})

        else:
            # Русский комментарий: Если иконка сердца не загружена, используем старую логику с кораблями
            # Этот блок нужен, если self.heart_icon None, но self.ships должен быть атрибутом класса
            if not hasattr(self, 'ships'): # Инициализируем ships только если его нет
                 self.ships = Group()
            else:
                 self.ships.empty() # Очищаем, если уже существует

            for ship_number in range(self.stats.ships_left):
                ship = Ship(self.ai_game) # Убедитесь, что класс Ship импортирован
                ship.rect.x = self.settings.lives_display_padding_left + ship_number * ship.rect.width
                ship.rect.y = self.settings.lives_display_padding_top
                self.ships.add(ship)
            self.ships_items_for_draw = None # Явный признак, что используем старую систему

    def check_high_score(self):
        """Проверяет появился ли новый рекорд"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()
            self.stats._save_high_score() # Сохраняем новый рекорд

    def show_score(self):
        """Выводит текущий счет, рекорд и число оставшихся кораблей"""
        # Русский комментарий: Отрисовка рамки счета, если она активна
        if self.score_frame_active and 'background' in self.score_frame_elements:
            # Рамка должна рисоваться ПОД текстом счета и рекорда.
            # Создадим Rect для рамки, который охватывает self.score_rect и self.high_score_rect
            # Это очень упрощенный подход. В идеале, размеры рамки должны быть известны заранее.

            # Определяем область, которую должна покрыть рамка
            # Возьмем верхнюю точку от рекорда (или счета, если рекорд выше)
            # и левую/правую границы от них же.
            # Для простоты, предположим, что рамка рисуется только вокруг текущего счета.
            if hasattr(self, 'score_rect'): # Ensure score_rect exists
                frame_bg_rect = self.score_frame_elements['background'].get_rect()

                # Центрируем фон рамки относительно текста счета, но делаем его больше
                # Это потребует точной настройки размеров фона рамки или использования 9-patch
                # Пример: делаем фон немного больше текста счета
                frame_padding = 10 # px

                # Tentative combined rect for score and high_score to be covered by frame
                # This part can be complex depending on desired frame behavior
                # For now, let's assume the frame primarily covers the score_rect area,
                # and high_score might be drawn over it or have its own frame.
                # The provided script focuses on score_rect for simplicity.
                combined_rect_for_frame = self.score_rect.copy()
                if hasattr(self, 'high_score_rect'):
                     combined_rect_for_frame.union_ip(self.high_score_rect)
                # Add padding around this combined area

                frame_bg_rect.width = combined_rect_for_frame.width + 2 * frame_padding
                frame_bg_rect.height = combined_rect_for_frame.height + 2 * frame_padding # Consider level display too if it's close
                frame_bg_rect.center = combined_rect_for_frame.center

                # Масштабируем изображение фона рамки под этот Rect
                scaled_frame_bg = pygame.transform.scale(self.score_frame_elements['background'], (frame_bg_rect.width, frame_bg_rect.height))
                self.screen.blit(scaled_frame_bg, frame_bg_rect)

        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        # Русский комментарий: Отображение жизней (иконки или корабли)
        if hasattr(self, 'ships_items_for_draw') and self.ships_items_for_draw is not None and self.heart_icon:
            for item in self.ships_items_for_draw:
                self.screen.blit(item['image'], item['rect'])
        elif hasattr(self, 'ships'): # Используем старую систему с кораблями, если иконки нет или ships_items_for_draw is None
            self.ships.draw(self.screen)