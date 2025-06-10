#!/bin/bash

echo "Начало загрузки ассетов..."

# Функция для скачивания файла
download_file() {
    url="$1"
    output_path="$2"
    mkdir -p "$(dirname "$output_path")" # Создаем директорию, если ее нет
    echo "Загрузка $url в $output_path"
    if curl -L -o "$output_path" "$url"; then
        echo "Успешно загружено: $output_path"
    else
        echo "Ошибка при загрузке $url. Код ошибки: $?"
    fi
}

# SFX
download_file "https://pixabay.com/sound-effects/laser-game-gamer-games-125770/" "assets/audio/sfx/laser/laser01.wav_download_page.html"
echo "Примечание: Для laser01.wav скачана HTML страница. Пожалуйста, перейдите по ссылке https://pixabay.com/sound-effects/laser-game-gamer-games-125770/ и скачайте WAV файл вручную в assets/audio/sfx/laser/laser01.wav"

download_file "https://pixabay.com/sound-effects/80s-style-power-up-74233/" "assets/audio/sfx/powerup/powerup01.wav_download_page.html"
echo "Примечание: Для powerup01.wav скачана HTML страница. Пожалуйста, перейдите по ссылке https://pixabay.com/sound-effects/80s-style-power-up-74233/ и скачайте WAV файл вручную в assets/audio/sfx/powerup/powerup01.wav"

download_file "https://pixabay.com/sound-effects/shield-recharging-110126/" "assets/audio/sfx/shield/shield_recharge.wav_download_page.html"
echo "Примечание: Для shield_recharge.wav скачана HTML страница. Пожалуйста, перейдите по ссылке https://pixabay.com/sound-effects/shield-recharging-110126/ и скачайте WAV файл вручную в assets/audio/sfx/shield/shield_recharge.wav"

echo "Взрывы: Пожалуйста, скачайте 'Impact Sounds' от Kenney с https://kenney.nl/assets/impact-sounds и выберите 3-4 WAV файла в assets/audio/sfx/explosion/"
# Пример: download_file "URL_TO_KENNEY_IMPACT_SOUNDS_ZIP" "temp_impact_sounds.zip"
# unzip temp_impact_sounds.zip -d assets/audio/sfx/explosion/ # Пользователю нужно будет выбрать нужные файлы

# Music
download_file "https://opengameart.org/sites/default/files/Soundfighter%20-%20Outer%20Space%20Loop.ogg" "assets/audio/music/outer_space_loop.ogg"

# UI Icons & Frames
echo "UI Иконки: Пожалуйста, скачайте 'Game Icons' от Kenney с https://kenney.nl/assets/game-icons и распакуйте PNG файлы в assets/gfx/ui/icons/"
# Пример: download_file "URL_TO_KENNEY_GAME_ICONS_ZIP" "temp_game_icons.zip"
# unzip temp_game_icons.zip -d assets/gfx/ui/icons/ # Пользователю нужно будет выбрать нужные файлы

echo "UI Рамки: Пожалуйста, скачайте 'UI Pack – Sci-Fi' от Kenney с https://kenney.nl/assets/ui-pack-sci-fi и распакуйте PNG файлы в assets/gfx/ui/frames/"
# Пример: download_file "URL_TO_KENNEY_UI_PACK_ZIP" "temp_ui_pack.zip"
# unzip temp_ui_pack.zip -d assets/gfx/ui/frames/ # Пользователю нужно будет выбрать нужные файлы

# Player Ship
echo "Корабль игрока: Пожалуйста, скачайте 'Space Shooter Redux' от Kenney с https://kenney.nl/assets/space-shooter-redux, найдите playerShip3_blue.png и поместите в assets/gfx/ships/player/"
# Пример: download_file "URL_TO_KENNEY_SPACE_SHOOTER_REDUX_ZIP" "temp_space_shooter_redux.zip"
# unzip temp_space_shooter_redux.zip
# cp "путь/к/playerShip3_blue.png" "assets/gfx/ships/player/playerShip3_blue.png"

# Enemy Ships
echo "Корабли пришельцев: Пожалуйста, скачайте '200+ CC0 Spaceship Sprites' с https://opengameart.org/content/200-cc0-spaceship-sprites и выберите 12 PNG файлов в assets/gfx/ships/aliens/"
# Пример: download_file "URL_TO_200_SPACESHIPS_ZIP" "temp_200_spaceships.zip"
# unzip temp_200_spaceships.zip -d assets/gfx/ships/aliens/ # Пользователю нужно будет выбрать нужные файлы

# Planets / Galaxies
echo "Планеты/Галактики: Пожалуйста, скачайте 'Space Kit' от Kenney с https://kenney.nl/assets/space-kit и распакуйте PNG файлы планет/галактик в assets/gfx/planets/"
# Пример: download_file "URL_TO_KENNEY_SPACE_KIT_ZIP" "temp_space_kit.zip"
# unzip temp_space_kit.zip -d assets/gfx/planets/ # Пользователю нужно будет выбрать нужные файлы

echo "Загрузка ассетов завершена. Пожалуйста, проверьте все пути и при необходимости скачайте/распакуйте файлы вручную, как указано выше."
echo "Не забудьте сделать скрипт исполняемым: chmod +x download_assets.sh"
echo "И добавить скачанные ассеты в Git LFS, если они еще не отслеживаются: git add assets/"
