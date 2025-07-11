# Дорожная карта улучшений игры "Alien Invasion"

Этот документ описывает планируемые фазы и задачи по улучшению игры "Alien Invasion".

## Фаза 1: Техническая основа и базовый UI/UX
- [x] Внедрение системы состояний игры (Game State Machine: Главное меню, Игра, Пауза, Конец игры).
- [x] Базовое Главное меню (пункты: "Новая игра", "Выход").
- [x] Функция Паузы (возможность поставить игру на паузу и возобновить).
- [x] Сохранение рекорда (high score) между игровыми сессиями (например, в текстовый или JSON файл).
- [x] Управление: Нажатие клавиши ESC во время игрового процесса или в меню паузы теперь всегда возвращает игрока в главное меню. Выход из игры по ESC возможен из главного меню или экрана "Конец игры".

## Фаза 2: Улучшения игрового процесса (первый набор)
- [x] Один-два типа бонусов (Power-ups) для корабля игрока (например, "Двойной выстрел", "Щит"). Включая механику их появления и подбора.
    - *Дополнено и переработано: Реализованы бонусы "Щит" и "Двойной выстрел" с обновленной логикой их распределения и характеристик:*
        -   ***Доступность по уровням:*** *Уровень 1: бонусы отсутствуют. Уровень 2+: доступен "Щит". Уровень 3+: доступны "Щит" и "Двойной выстрел".*
        -   ***Распределение бонусов ("Мешок с шариками"):*** *Количество выпадающих бонусов за уровень рассчитывается как `ceil(количество_пришельцев * dropRate)` (рекомендуемый `dropRate` ≈ 7%). Эти бонусы предварительно случайным образом назначаются пришельцам перед началом уровня. Это гарантирует расчетное количество бонусов за волну.*
        -   ***Скорость падения бонусов:*** *Базовая скорость падения составляет 50% от начальной скорости пришельцев на данном уровне. Начиная с 6-го уровня, эта скорость увеличивается на +5% каждые 5 уровней (аналогично множителю сложности пришельцев), но не превышает текущую базовую скорость пришельцев на уровне.*
- [x] Визуализация лазеров игрока.
    - *Завершено: Цвет снарядов игрока изменен на ярко-красный для лучшей видимости.*
- [x] Поведение движения врагов.
    - *Дополнено и переработано: Система прогрессии сложности, основанная на номере текущего уровня, была уточнена:*
        -   ***Базовая сложность (Уровни 1-5):*** *Сохранены текущие настройки сложности для уровней 1-5 как базовая линия.*
        -   ***Повышение сложности (Уровни 6+):*** *Начиная с 6-го уровня, общая сложность увеличивается на +5% каждые 5 уровней (6-10, 11-15 и т.д.). Это достигается с помощью множителя скорости (`speedMultiplier = clamp(1 + 0.05 * floor((level−1)/5), 1, maxSpeedFactor)`), который применяется к скорости пришельцев и скорости снижения флота.*
        -   ***Дополнительные ряды пришельцев (Уровни 6+):*** *Для увеличения давления без экстремального ускорения скорости, добавляются дополнительные ряды пришельцев: +1 ряд на 6-м уровне, +1 на 11-м, и так далее (`floor((level-1)/5)` дополнительных рядов), с учетом высоты экрана.*
        -   ***Факторы плотности и скорости:*** *Существующие факторы, влияющие на количество пришельцев в ряду и базовое количество рядов (до добавления бонусных рядов), а также скорость снижения флота и базовая скорость пришельцев, теперь используют свои значения для 5-го уровня как основу для уровней 6 и выше, к которой затем применяются новые модификаторы (`speedMultiplier`, дополнительные ряды).*
        -   ***Ограничения (Caps):*** *Для всех параметров сложности сохранены или введены максимальные значения для предотвращения чрезмерного усложнения и сохранения играбельности.*
        -   ***Стоимость пришельцев:*** *Количество очков за уничтожение пришельца по-прежнему увеличивается с уровнем.*
- [ ] Один новый тип врага с поведением, отличным от базового (например, более прочный или стреляющий).

## Фаза 3: Визуальные и звуковые улучшения (базовые)
- [x] **Процедурный фон "звездное небо"**: Статический фон заменен на динамический процедурный фон черного звездного неба. Фон состоит из двух слоев параллакса для создания эффекта глубины, со звездами размером 1-2 пикселя и плотностью пикселей 0.1 – 0.2%. Звезды имеют различную прозрачность (alpha 0.6-0.9) и медленно прокручиваются.
- [ ] Базовые звуковые эффекты (добавление/улучшение звуков для выстрелов корабля и врагов (если появятся стреляющие враги), взрывов, получения бонуса, столкновения).
- [ ] Простые анимации (например, анимация взрыва для корабля и пришельцев).

## Последующие фазы (для дальнейшего планирования и детализации)
- [ ] Расширенная система бонусов (больше типов, возможно, с уровнями улучшений).
- [ ] Больше типов врагов, включая врагов-боссов в конце определенных этапов/волн.
- [ ] Продвинутая графика и анимации (более детализированные спрайты, анимации движения, параллакс-скроллинг для фона).
- [ ] Фоновая музыка (разная для меню и игрового процесса, возможно, меняющаяся в зависимости от интенсивности игры).
- [ ] Улучшенное звуковое оформление (более качественные и разнообразные звуки).
- [ ] Гибкая система конфигурации уровней/волн (например, через файлы данных JSON или YAML, описывающие типы врагов, их количество, порядок появления, бонусы на уровне).
- [ ] Расширенная таблица лидеров (например, топ-10 игроков с вводом имени).
- [ ] Дополнительные визуальные эффекты (например, следы от пуль, эффекты частиц).
- [ ] Возможно, другие типы оружия для игрока.
- [ ] ... (другие идеи, которые могут появиться в ходе разработки).

## Фаза 4: Корректировка ассетов и репозитория
- [x] **Обеспечение минимально валидными ассетами-заглушками и удаление Git LFS:** Все ассеты хранятся в репозитории. Для отсутствующих графических и звуковых файлов используются автоматически генерируемые минимальные заглушки (1x1 PNG, копии OGG для WAV) для предотвращения ошибок загрузки и обеспечения запуска игры. Зависимость от Git LFS полностью устранена.
    - Графические ассеты-заглушки: валидные прозрачные PNG 1x1 пиксель.
    - Звуковые ассеты-заглушки (WAV): копии существующего валидного OGG-файла (для предотвращения ошибок чтения).
    - Git LFS удален из конфигурации проекта (` .gitattributes`).
    - Код игры обновлен для корректной работы с отсутствующими ассетами (вывод предупреждений, использование fallback-графики) и улучшенной инициализации аудиосистемы (включая fallback на dummy-драйвер).
    - Добавлен скрипт `tools/check_assets.py` для базовой проверки загрузки ассетов.
    - *Примечание: Рекомендуется заменять заглушки на полные версии ассетов. Ссылки и инструкции находятся в `download_assets.sh`.*
