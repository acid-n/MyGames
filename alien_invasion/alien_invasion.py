import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from powerup import PowerUp
import random
import math # Импортируем math для floor, ceil, или других функций, если понадобятся. lerp определим сами.

# Функция линейной интерполяции (Lerp)
def lerp(start, end, t):
    """Вычисляет линейную интерполяцию между start и end для данного t."""
    return start + t * (end - start)

class AlienInvasion:
    """Класс для управления ресурсами и поведением игры"""

    # Состояния игры
    STATE_MENU = 'menu'
    STATE_PLAYING = 'playing'
    STATE_PAUSED = 'paused'
    STATE_GAME_OVER = 'game_over'

    def __init__(self):
        """Инициализирует игру и создает игровые ресурсы"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Создание экземпляра для хранения игровой статистики
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.game_state = self.STATE_MENU # Начальное состояние игры - Меню

        self.ship = Ship(self) # Корабль создается, но будет использоваться/рисоваться только в STATE_PLAYING
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        # Кнопки меню
        self.new_game_button = Button(self, self.settings.menu_new_game_button_text)
        self.exit_button = Button(self, self.settings.menu_exit_button_text)

        # Позиционирование кнопок меню
        # Position "New Game" button centered on the screen
        self.new_game_button.rect.center = self.screen.get_rect().center

        # Position "Exit" button centered horizontally, and below "New Game" button with a 20px gap
        self.exit_button.rect.centerx = self.screen.get_rect().centerx
        self.exit_button.rect.top = self.new_game_button.rect.bottom + 20

        # Pause Menu Buttons
        self.resume_button = Button(self, "Продолжить")
        self.restart_button_paused = Button(self, "Заново")
        self.main_menu_button = Button(self, "Главное меню")

        # Position Resume button (e.g., centered)
        self.resume_button.rect.centerx = self.screen.get_rect().centerx
        self.resume_button.rect.centery = self.screen.get_rect().centery - self.resume_button.rect.height

        # Position Restart button below Resume
        self.restart_button_paused.rect.centerx = self.screen.get_rect().centerx
        self.restart_button_paused.rect.top = self.resume_button.rect.bottom + 10 # 10px gap

        # Position Main Menu button below Restart
        self.main_menu_button.rect.centerx = self.screen.get_rect().centerx
        self.main_menu_button.rect.top = self.restart_button_paused.rect.bottom + 10

        # _create_fleet() будет вызываться в _start_new_game(), а не при инициализации
        # self._create_fleet() # Убрано отсюда

        self.powerups = pygame.sprite.Group()
        self.last_double_fire_spawn_time = 0 # Время последнего появления бонуса "Двойной выстрел"
        self.last_shield_spawn_time = 0 # Время последнего появления бонуса "Щит"
        self.level_start_time = 0 # Время начала текущего уровня (в тиках)

        # Счетчики для гарантированного выпадения бонуса
        self.aliens_in_wave = 0 # Общее количество пришельцев в текущей волне
        self.aliens_destroyed_current_wave = 0 # Количество уничтоженных пришельцев в текущей волне
        self.guaranteed_powerup_spawned_this_wave = False # Флаг, был ли уже гарантированный бонус в этой волне

    def run_game(self):
        """Запуск основного цикла игры"""
        while True:
            self._check_events()

            if self.game_state == self.STATE_PLAYING:
                self.ship.update()
                self._update_bullets()

                # New DDA logic based on per-level increase rate and max speed
                if hasattr(self.settings, 'alien_speed_increase_rate') and hasattr(self.settings, 'alien_speed_max_level'):
                    if self.settings.alien_speed_current < self.settings.alien_speed_max_level:
                        self.settings.alien_speed_current += self.settings.alien_speed_increase_rate
                        self.settings.alien_speed_current = min(self.settings.alien_speed_current, self.settings.alien_speed_max_level)

                self._update_aliens()
                self.powerups.update()
                self._check_ship_powerup_collisions()
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
                        pygame.mouse.set_visible(True) # Показываем мышь в меню
                    # Если в главном меню или на экране конца игры, ESC по-прежнему закрывает игру
                    elif self.game_state == self.STATE_MENU or self.game_state == self.STATE_GAME_OVER:
                        sys.exit()
                elif event.key == pygame.K_p: # Simple Pause toggle (no menu)
                    if self.game_state == self.STATE_PLAYING:
                        self.game_state = self.STATE_PAUSED
                        # No mouse visibility change for 'P' to keep it simple
                    elif self.game_state == self.STATE_PAUSED:
                        self.game_state = self.STATE_PLAYING
                        # No mouse visibility change for 'P'
                else:
                    self._check_keydown_events(event) # Gameplay related key events
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.game_state == self.STATE_MENU or self.game_state == self.STATE_GAME_OVER:
                    clicked_new_game = self.new_game_button.is_clicked(mouse_pos)
                    clicked_exit = self.exit_button.is_clicked(mouse_pos)

                    if clicked_new_game:
                        self._start_new_game()
                    elif clicked_exit:
                        sys.exit()
                elif self.game_state == self.STATE_PAUSED:
                    clicked_resume = self.resume_button.is_clicked(mouse_pos)
                    clicked_restart_paused = self.restart_button_paused.is_clicked(mouse_pos)
                    clicked_main_menu = self.main_menu_button.is_clicked(mouse_pos)

                    if clicked_resume:
                        self.game_state = self.STATE_PLAYING
                        pygame.mouse.set_visible(False)
                    elif clicked_restart_paused:
                        self._start_new_game() # This already sets state to PLAYING and hides mouse
                    elif clicked_main_menu:
                        self.game_state = self.STATE_MENU
                        pygame.mouse.set_visible(True) # Ensure mouse is visible for menu

            # Removed the separate state-specific event processing for K_p here, as it's integrated above.
            # Menu state specific KEYDOWN events (e.g. navigating menu with keys) could go here or in _check_keydown_events
            # if self.game_state == self.STATE_MENU:
            #     pass # Example: self._check_menu_keydown(event)

    # def _check_play_button(self, mouse_pos): # Метод удален
    #     """Запускает новую игру при нажатии кнопки Play"""
    #     button_clicked = self.play_button.is_clicked(mouse_pos)
    #     if button_clicked and not self.stats.game_active:
    #         self._start_new_game()

    def _start_new_game(self):
        """Начинает новую игру."""
        # Сборос игровой статистики
        self.stats.reset_stats() # Reset stats first so self.stats.level is 1
        self.settings.initialize_dynamic_settings(self.stats.level) # Load settings for level 1
        self.stats.game_active = True
        self.game_state = self.STATE_PLAYING # Установка активного состояния игры
        self.last_double_fire_spawn_time = 0 # Сброс таймера кулдауна для "Двойного выстрела"
        self.last_shield_spawn_time = 0 # Сброс таймера кулдауна для "Щита"
        self.level_start_time = pygame.time.get_ticks() # Установка времени начала уровня

        # Сброс счетчиков для гарантированного бонуса при новой игре
        self.aliens_in_wave = 0
        self.aliens_destroyed_current_wave = 0
        self.guaranteed_powerup_spawned_this_wave = False

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
        self.powerups.empty() # Очищаем бонусы при новой игре/раунде
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
            if len(self.bullets) <= self.settings.bullets_allowed - 2: # Убедимся, что есть место для двух снарядов
                bullet1 = Bullet(self)
                bullet2 = Bullet(self)

                # Смещаем снаряды относительно центра корабля
                # Начальная позиция обоих снарядов - верхушка центра корабля.
                # Затем смещаем rect.x для каждого. self.y в классе Bullet уже установлен корректно.
                bullet1.rect.x -= 10 # Сместить влево
                bullet2.rect.x += 10 # Сместить вправо

                self.bullets.add(bullet1)
                self.bullets.add(bullet2)
        else:
            # Обычный режим огня
            if len(self.bullets) < self.settings.bullets_allowed:
                new_bullet = Bullet(self)
                self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Обновляет позиции снарядов и удаляет старые пули"""
        # Update bullets positions
        self.bullets.update()

        # Уничтожение исчезнувших снарядов
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Обработка коллизий снарядов с пришельцами"""

        # Проверка попаданий в пришельцев
        # При обнаружении попадания удалить снаряд и пришельца
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens_collided_list in collisions.values(): # aliens_collided_list - список пришельцев, уничтоженных одной пулей
                for alien_hit in aliens_collided_list:
                    self.stats.score += self.settings.alien_points # Очки за пришельца
                    self.aliens_destroyed_current_wave += 1 # Увеличиваем счетчик уничтоженных в волне

                    current_game_time = pygame.time.get_ticks()

                    # --- Логика гарантированного появления бонуса ---
                    # Проверяем, если еще не было гарантированного бонуса в этой волне
                    # и уничтожено достаточно пришельцев (например, 75%)
                    if not self.guaranteed_powerup_spawned_this_wave and \
                       self.aliens_in_wave > 0 and \
                       self.aliens_destroyed_current_wave >= 0.75 * self.aliens_in_wave:

                        spawned_guaranteed = False
                        # Пытаемся сначала заспавнить "Щит"
                        if self.stats.level >= 2 and \
                           hasattr(self.settings, 'current_shield_min_cooldown') and \
                           (current_game_time - self.last_shield_spawn_time) > self.settings.current_shield_min_cooldown:
                            # Проверяем также шанс, чтобы не спавнить всегда, если доступно по уровню и КД прошел
                            # Хотя для гарантированного спавна можно и без random.random() < settings.current_shield_spawn_chance
                            # Но для консистентности и если шанс 0, то не спавнить.
                            if hasattr(self.settings, 'current_shield_spawn_chance') and self.settings.current_shield_spawn_chance > 0:
                                shield_powerup = PowerUp(self, 'shield', alien_hit.rect.center)
                                self.powerups.add(shield_powerup)
                                self.last_shield_spawn_time = current_game_time
                                self.guaranteed_powerup_spawned_this_wave = True
                                spawned_guaranteed = True

                        # Если "Щит" не заспавнен (или не мог быть заспавнен) и гарантированный бонус еще не вышел
                        if not spawned_guaranteed and \
                           self.stats.level >= 3 and \
                           hasattr(self.settings, 'current_double_fire_min_cooldown') and \
                           (current_game_time - self.last_double_fire_spawn_time) > self.settings.current_double_fire_min_cooldown:
                            if hasattr(self.settings, 'current_double_fire_spawn_chance') and self.settings.current_double_fire_spawn_chance > 0:
                                df_powerup = PowerUp(self, 'double_fire', alien_hit.rect.center)
                                self.powerups.add(df_powerup)
                                self.last_double_fire_spawn_time = current_game_time
                                self.guaranteed_powerup_spawned_this_wave = True
                                # spawned_guaranteed = True # Уже не нужно, это последний вариант

                    # --- Обычная логика появления бонусов (если гарантированный еще не выпал) ---
                    # Проверка общего минимального времени на уровне для появления бонусов
                    if hasattr(self.settings, 'current_powerup_general_min_level_time') and \
                       (current_game_time - self.level_start_time) < self.settings.current_powerup_general_min_level_time:
                        pass # Слишком рано на уровне для бонусов
                    else:
                        # Логика появления бонуса "Щит" (если не было гарантированного спавна)
                        if not self.guaranteed_powerup_spawned_this_wave and \
                           hasattr(self.settings, 'current_shield_spawn_chance') and \
                           hasattr(self.settings, 'current_shield_min_cooldown') and \
                           self.settings.current_shield_spawn_chance > 0 and \
                           self.stats.level >= 2: # Щит доступен со 2-го уровня
                            if (current_game_time - self.last_shield_spawn_time) > self.settings.current_shield_min_cooldown:
                                if random.random() < self.settings.current_shield_spawn_chance:
                                    shield_powerup = PowerUp(self, 'shield', alien_hit.rect.center)
                                    self.powerups.add(shield_powerup)
                                    self.last_shield_spawn_time = current_game_time
                                    self.guaranteed_powerup_spawned_this_wave = True # Засчитываем как выпавший бонус

                        # Логика появления бонуса "Двойной выстрел" (если не было гарантированного спавна или щита)
                        if not self.guaranteed_powerup_spawned_this_wave and \
                           hasattr(self.settings, 'current_double_fire_spawn_chance') and \
                           hasattr(self.settings, 'current_double_fire_min_cooldown') and \
                           self.settings.current_double_fire_spawn_chance > 0 and \
                           self.stats.level >= 3: # Двойной выстрел доступен с 3-го уровня
                            if (current_game_time - self.last_double_fire_spawn_time) > self.settings.current_double_fire_min_cooldown:
                                if random.random() < self.settings.current_double_fire_spawn_chance:
                                    df_powerup = PowerUp(self, 'double_fire', alien_hit.rect.center)
                                    self.powerups.add(df_powerup)
                                    self.last_double_fire_spawn_time = current_game_time
                                    self.guaranteed_powerup_spawned_this_wave = True # Засчитываем как выпавший бонус

            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Уничтожение существующих снарядов и создание нового флота
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Увеличение уровня
            self.stats.level += 1
            self.sb.prep_level()
            # Load settings for the new level
            self.settings.load_level_settings(self.stats.level)
            self.level_start_time = pygame.time.get_ticks() # Сброс времени начала уровня

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
            # Сброс элементов раунда
            self._reset_round_elements()
            # Пауза
            sleep(self.settings.ship_hit_pause_duration)
        else:
            self.stats.game_active = False # Keep game_active in sync
            self.game_state = self.STATE_GAME_OVER
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Создание флота вторжения и сброс счетчиков для гарантированного бонуса."""
        # Создание пришельца и вычисление количества пришельцев в ряду
        # Интервал между соседними пришельцами равен ширине пришельца
        alien = Alien(self) # Dummy alien for dimensions
        alien_width, alien_height = alien.rect.size

        # Calculate initial numbers based on screen space and default spacing
        initial_available_space_x = self.settings.screen_width - (self.settings.fleet_screen_margin_x_factor * alien_width)
        initial_number_aliens_x = int(initial_available_space_x / (self.settings.alien_horizontal_spacing_factor * alien_width))

        ship_height = self.ship.rect.height
        initial_available_space_y = (self.settings.screen_height - (self.settings.fleet_top_margin_factor * alien_height) - ship_height)
        initial_number_rows = int(initial_available_space_y / (self.settings.alien_vertical_spacing_factor * alien_height))

        # Apply level-specific factors
        number_aliens_x = int(initial_number_aliens_x * self.settings.current_aliens_per_row_factor)
        number_rows = int(initial_number_rows * self.settings.current_alien_rows_factor)

        # Add safeguards
        number_aliens_x = max(1, number_aliens_x)
        number_rows = max(1, number_rows)

        # Создание флота вторжения using the calculated numbers
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number, alien_width, alien_height) # Pass alien_width, alien_height

        # Инициализация/сброс счетчиков для механики гарантированного бонуса
        self.aliens_in_wave = len(self.aliens)
        self.aliens_destroyed_current_wave = 0
        self.guaranteed_powerup_spawned_this_wave = False

    def _create_alien(self, alien_number, row_number, alien_width, alien_height): # Accept alien_width, alien_height
        """Создание пришельца и размещение его в ряду"""
        alien = Alien(self)
        # alien_width, alien_height = alien.rect.size # Not needed if passed as args
        alien.x = alien_width + self.settings.alien_horizontal_spacing_factor * alien_width * alien_number
        alien.rect.x = alien.x
        # Corrected y position calculation to use alien_height consistently
        alien.rect.y = alien_height + self.settings.alien_vertical_spacing_factor * alien_height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана"""
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
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.powerups.draw(self.screen) # Отрисовка бонусов

        # Вывод информации о счете
        self.sb.show_score()

        # Отображение элементов в зависимости от состояния игры
        if self.game_state == self.STATE_GAME_OVER or self.game_state == self.STATE_MENU:
            self.new_game_button.draw_button()
            self.exit_button.draw_button()
        elif self.game_state == self.STATE_PAUSED:
            pause_text = "Пауза"
            # Используем шрифт и цвет из scoreboard для консистентности, или можно задать свои в settings
            pause_image = self.sb.font.render(pause_text, True,
                                              self.settings.scoreboard_text_color,
                                              None) # None для прозрачного фона текста
            screen_rect = self.screen.get_rect()
            # Position "Пауза" text above the buttons
            text_rect_y_offset = self.resume_button.rect.top - pause_image.get_height() - 20 # 20px above resume button
            pause_rect = pause_image.get_rect(centerx=screen_rect.centerx, top=text_rect_y_offset)

            # Ensure the text is not positioned too high if buttons are very high.
            # A simple check: if pause_rect.top is less than some margin, adjust it.
            # For now, assuming buttons are reasonably placed.
            # if pause_rect.top < 20: # Example margin
            #    pause_rect.top = 20

            self.screen.blit(pause_image, pause_rect)

            # Draw Pause Menu Buttons
            self.resume_button.draw_button()
            self.restart_button_paused.draw_button()
            self.main_menu_button.draw_button()
            # Игровые элементы (корабль, пришельцы, пули, счет) уже отрисованы до этого блока,
            # поэтому они останутся видимыми, но замороженными.

        pygame.display.flip()

    def _check_ship_powerup_collisions(self):
        """Проверяет столкновения корабля с бонусами."""
        # The True argument will remove the power-up sprite upon collision
        collected_powerups = pygame.sprite.spritecollide(self.ship, self.powerups, True)
        for powerup in collected_powerups:
            if powerup.powerup_type == 'shield':
                self.ship.activate_shield()
            elif powerup.powerup_type == 'double_fire': # Обработка сбора бонуса "Двойной выстрел"
                self.ship.activate_double_fire()
            # Добавить elif для других типов бонусов, если они появятся позже

if __name__ == '__main__':
    # Создание экземпляра и запуск игры
    ai = AlienInvasion()
    ai.run_game()