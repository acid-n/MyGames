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

        # _create_fleet() будет вызываться в _start_new_game(), а не при инициализации
        # self._create_fleet() # Убрано отсюда

        self.powerups = pygame.sprite.Group()
        self.last_double_fire_spawn_time = 0 # Время последнего появления бонуса "Двойной выстрел"

    def run_game(self):
        """Запуск основного цикла игры"""
        while True:
            self._check_events()

            if self.game_state == self.STATE_PLAYING:
                self.ship.update()
                self._update_bullets()

                # Динамическое изменение скорости пришельцев (DDA) на основе очков
                progress_ratio = self.stats.score / self.settings.target_score_for_max_speed
                progress_ratio_clamped = min(1.0, progress_ratio) # Ограничиваем progress_ratio значением 1.0

                # Используем Lerp для вычисления текущей скорости
                # Формула: clamped_speed = min_speed + progress_ratio_clamped * (max_speed - min_speed)
                clamped_speed = lerp(self.settings.min_alien_speed,
                                     self.settings.alien_speed_max,
                                     progress_ratio_clamped)

                # Дополнительно убедимся, что скорость находится в пределах min/max (хотя Lerp с clamped_ratio должен это гарантировать)
                self.settings.alien_speed_current = min(max(clamped_speed, self.settings.min_alien_speed), self.settings.alien_speed_max)

                # Старая логика увеличения скорости удалена:
                # if self.settings.alien_speed_current < self.settings.alien_speed_max:
                #     self.settings.alien_speed_current += self.settings.alien_speed_increase_rate
                #     self.settings.alien_speed_current = min(self.settings.alien_speed_current, self.settings.alien_speed_max)

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
                if event.key == pygame.K_p: # Pause toggle
                    if self.game_state == self.STATE_PLAYING:
                        self.game_state = self.STATE_PAUSED
                    elif self.game_state == self.STATE_PAUSED:
                        self.game_state = self.STATE_PLAYING
                else: # Handle other keydown events only if not 'P' or if 'P' didn't handle it
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
                # Add other MOUSEBUTTONDOWN checks for other states if needed (e.g. pause screen buttons)

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
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.stats.game_active = True
        self.game_state = self.STATE_PLAYING # Установка активного состояния игры
        self.last_double_fire_spawn_time = 0 # Сброс таймера кулдауна для "Двойного выстрела"
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
            for aliens_collided_list in collisions.values(): # aliens_collided_list is a list of Alien objects
                for alien_hit in aliens_collided_list:
                    self.stats.score += self.settings.alien_points # Очки за пришельца

                    # Логика появления бонусов (теперь независимая для каждого типа)

                    # Логика появления бонуса "Щит"
                    if random.random() < self.settings.shield_spawn_chance:
                        shield_powerup = PowerUp(self, 'shield', alien_hit.rect.center)
                        self.powerups.add(shield_powerup)

                    # Логика появления бонуса "Двойной выстрел" с кулдауном
                    current_time = pygame.time.get_ticks()
                    if (current_time - self.last_double_fire_spawn_time) > self.settings.double_fire_min_cooldown:
                        if random.random() < self.settings.double_fire_spawn_chance:
                            df_powerup = PowerUp(self, 'double_fire', alien_hit.rect.center)
                            self.powerups.add(df_powerup)
                            self.last_double_fire_spawn_time = current_time # Обновляем время последнего появления

                    # Нет break, поэтому если пуля попадает в нескольких пришельцев, каждый имеет шанс выбросить бонус
                    # и каждый дает очки.
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
        """Создание флота вторжения"""
        # Создание пришельца и вычисление количества пришельцев в ряду
        # Интервал между соседними пришельцами равен ширине пришельца
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (self.settings.fleet_screen_margin_x_factor * alien_width)
        number_aliens_x = int(available_space_x / (self.settings.alien_horizontal_spacing_factor * alien_width))

        """Определяет количество рядов, помещающихся на экране"""
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (self.settings.fleet_top_margin_factor * alien_height) - ship_height)
        number_rows = int(available_space_y / (self.settings.alien_vertical_spacing_factor * alien_height))

        # Создание флота вторжения
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Создание пришельца и размещение его в ряду"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + self.settings.alien_horizontal_spacing_factor * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + self.settings.alien_vertical_spacing_factor * alien.rect.height * row_number
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
            screen_rect = self.screen.get_rect() # Получаем screen_rect здесь, если он еще не атрибут класса
            pause_rect = pause_image.get_rect(center=screen_rect.center)
            self.screen.blit(pause_image, pause_rect)
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