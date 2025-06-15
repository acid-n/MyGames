import os
import zipfile
import shutil
import subprocess
from PIL import Image
import xml.etree.ElementTree as ET

# --- Конфигурация ---
# Базовая директория для ассетов относительно скрипта
ASSETS_BASE_DIR = "assets"
# Временная директория для ручных загрузок и распаковки
TEMP_DIR = "temp_assets_download"

# Список директорий, которые нужно создать
DIRECTORIES = [
    os.path.join(ASSETS_BASE_DIR, "gfx", "planets"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ui", "frames"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ui", "misc"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "backgrounds"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "player"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "aliens"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "laser"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "powerup"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "shield"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "explosion"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "powerups"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "explosions"),
]

# Словари для ассетов: source_temp_file - имя файла в TEMP_DIR
ASSETS = {
    "kenney_planets_pack": {
        "manual_download_url": "Ссылка, откуда ты скачал этот пак с планетами",
        "source_temp_file": "kenney_planets.zip",
        "destination_path": os.path.join(TEMP_DIR, "kenney_planets_unzipped"),
        "extract_path": "Planets", # Путь внутри распакованного архива к файлам планет
        "files_to_copy_mapping": [
            ("planet00.png", "planet01.png"),
            ("planet01.png", "planet02.png"),
            ("planet02.png", "planet03.png")
        ]
    },
    "space_shooter_redux": {
        "manual_download_url": "https://opengameart.org/content/space-shooter-redux",
        "source_temp_file": "SpaceShooterRedux.zip",
        "destination_path": os.path.join(TEMP_DIR, "space-shooter-redux-unzipped"),
    },
    "cc0_spaceship_sprites": {
        "manual_download_url": "https://opengameart.org/content/200-cc0-spaceship-sprites",
        "source_temp_file": "200Starships.zip",
        "destination_path": os.path.join(TEMP_DIR, "200-cc0-spaceship-sprites-unzipped"),
        "files_to_copy": []
    },
}

# --- Вспомогательные функции ---

def create_directories():
    """Создает все необходимые директории для ассетов."""
    print("Создание необходимых директорий...")
    for path in DIRECTORIES:
        os.makedirs(path, exist_ok=True)
        print(f"  Директория создана: {path}")

def extract_zip(zip_path, extract_to_path):
    """Распаковывает ZIP-архив."""
    print(f"Распаковка {zip_path} в {extract_to_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_path)
        print("  Архив успешно распакован.")
        return True
    except zipfile.BadZipFile:
        print(f"Ошибка: {zip_path} не является действительным ZIP-файлом. Убедитесь, что он не поврежден.")
        return False
    except Exception as e:
        print(f"Ошибка при распаковке {zip_path}: {e}")
        return False

def copy_file(source, destination):
    """Копирует файл из источника в назначение."""
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(source, destination)
        print(f"  Скопировано: {source} -> {destination}")
        return True
    except FileNotFoundError:
        print(f"Ошибка: Исходный файл не найден: {source}. Убедитесь, что он существует.")
        return False
    except Exception as e:
        print(f"Ошибка при копировании {source} в {destination}: {e}")
        return False

def run_git_command(command):
    """Выполняет команду Git."""
    try:
        print(f"Выполнение Git команды: {command}")
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения Git команды: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def get_sprite_coordinates_from_xml(xml_path):
    """Парсит XML-файл и возвращает словарь с координатами спрайтов."""
    sprite_coords = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for subtexture in root.findall('SubTexture'):
            name = subtexture.get('name')
            x = int(subtexture.get('x'))
            y = int(subtexture.get('y'))
            width = int(subtexture.get('width'))
            height = int(subtexture.get('height'))
            sprite_coords[name] = (x, y, x + width, y + height)
        print(f"  Координаты спрайтов загружены из {xml_path}")
    except FileNotFoundError:
        print(f"  Ошибка: XML-файл '{xml_path}' не найден. Невозможно получить координаты спрайтов.")
    except Exception as e:
        print(f"  Ошибка при парсинге XML-файла '{xml_path}': {e}")
    return sprite_coords

def extract_sprite_from_sheet(sheet_image_path, sprite_name, sprite_coords, output_path):
    """Вырезает спрайт из изображения, используя координаты из словаря."""
    if sprite_name not in sprite_coords:
        print(f"  Ошибка: Координаты для спрайта '{sprite_name}' не найдены в XML. Пропускаем.")
        return False
    crop_box = sprite_coords[sprite_name]
    return extract_sprite_direct(sheet_image_path, crop_box, output_path)

def extract_sprite_direct(image_path, crop_box, output_path):
    """Вырезает спрайт из изображения и сохраняет его."""
    try:
        with Image.open(image_path) as img:
            cropped_img = img.crop(crop_box)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cropped_img.save(output_path)
            print(f"  Вырезано: {output_path}")
            return True
    except FileNotFoundError:
        print(f"  Ошибка: Исходный спрайтшит не найден: {image_path}")
        return False
    except Exception as e:
        print(f"  Ошибка при вырезке спрайта {output_path}: {e}")
        return False

# --- Основная логика скрипта ---

def main():
    print("Начало процесса добавления ассетов...")

    # Создаем временную директорию
    print(f"Создание временной директории для ручных загрузок: {TEMP_DIR}")
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    print(f"\n--- Использование файлов из '{TEMP_DIR}' ---")
    print("  Убедитесь, что в этой папке находятся следующие файлы:")
    for key, asset_info in ASSETS.items():
        print(f"  - Ожидаемый файл: {asset_info.get('source_temp_file')}")
    print("\nПродолжаем работу с имеющимися файлами. Если каких-то файлов не хватает, скрипт пропустит их.")

    # Шаг 1: Подготовка директорий
    create_directories()

    # Шаг 2: Размещение ассетов из локальных файлов
    print("\n--- Размещение ассетов из локальных файлов ---")

    for key, asset_info in ASSETS.items():
        print(f"\nОбработка: {key}")
        source_temp_file_path = os.path.join(TEMP_DIR, asset_info["source_temp_file"])
        destination_unzip_dir = asset_info.get("destination_path")
        
        if not os.path.exists(source_temp_file_path):
            print(f"  Внимание: Файл '{source_temp_file_path}' не найден. Пропускаем обработку этого ассета.")
            continue

        if asset_info.get("is_direct_copy", False):
            pass
        else:
            if extract_zip(source_temp_file_path, destination_unzip_dir):
                if key == "kenney_planets_pack": # Планеты
                    planets_source_dir = os.path.join(destination_unzip_dir, asset_info["extract_path"])
                    if os.path.exists(planets_source_dir):
                        for src_name, dest_name in asset_info["files_to_copy_mapping"]:
                            copy_file(os.path.join(planets_source_dir, src_name), os.path.join(ASSETS_BASE_DIR, "gfx", "planets", dest_name))
                        print("  Планеты успешно скопированы.")
                    else:
                        print(f"  Ошибка: Не найдена папка '{asset_info['extract_path']}' в распакованном архиве {source_temp_file_path}.")

                elif key == "space_shooter_redux": # Space Shooter Redux - основной источник!
                    redux_base_dir = destination_unzip_dir
                    # ОБНОВЛЕННЫЕ ПУТИ К sheet.png и sheet.xml
                    sheet_image_path = os.path.join(redux_base_dir, "Spritesheet", "sheet.png") # <--- Исправлено здесь
                    sheet_xml_path = os.path.join(redux_base_dir, "Spritesheet", "sheet.xml")   # <--- Исправлено здесь
                    
                    sprite_coords = {}
                    if os.path.exists(sheet_xml_path):
                        sprite_coords = get_sprite_coordinates_from_xml(sheet_xml_path)
                    else:
                        print(f"  Ошибка: XML-файл спрайтшита '{sheet_xml_path}' не найден. Невозможно вырезать спрайты.")
                        continue

                    if not os.path.exists(sheet_image_path):
                        print(f"  Ошибка: Спрайтшит 'sheet.png' не найден в распакованном архиве Space Shooter Redux. Графические ассеты не скопированы.")
                        continue

                    print(f"  Обнаружен спрайтшит: {sheet_image_path} и XML: {sheet_xml_path}. Вырезаем спрайты и копируем звуки...")

                    # 1. Копируем звуки из папки Bonus
                    bonus_sounds_dir = os.path.join(redux_base_dir, "Bonus")
                    if os.path.exists(bonus_sounds_dir):
                        copy_file(os.path.join(bonus_sounds_dir, "sfx_laser1.ogg"), os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "laser", "laser01.ogg"))
                        copy_file(os.path.join(bonus_sounds_dir, "sfx_twoTone.ogg"), os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "powerup", "powerup01.ogg"))
                        copy_file(os.path.join(bonus_sounds_dir, "sfx_shieldUp.ogg"), os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "shield", "shield_recharge.ogg"))
                        
                        copy_file(os.path.join(bonus_sounds_dir, "sfx_lose.ogg"), os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "explosion", "explosion01.ogg"))
                        print("  Звуковые эффекты (лазер, бонус, щит, один взрыв) из Space Shooter Redux скопированы.")
                    else:
                        print(f"  Внимание: Папка 'Bonus' со звуками не найдена в распакованном архиве Space Shooter Redux. Звуки не скопированы.")
                    
                    # 2. Вырезаем спрайты из sheet.png
                    if sprite_coords:
                        # Корабль игрока
                        extract_sprite_from_sheet(sheet_image_path, "playerShip3_blue.png", sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "player", "playerShip3_blue.png"))
                        
                        # Корабли пришельцев (12 штук) - возьмем разных "enemy" из Redux
                        enemy_ships_to_copy = [
                            "enemyRed1.png", "enemyBlue2.png", "enemyGreen3.png", "enemyBlack4.png",
                            "enemyBlue1.png", "enemyGreen2.png", "enemyBlack3.png", "enemyRed4.png",
                            "enemyGreen1.png", "enemyBlack2.png", "enemyRed3.png", "enemyBlue4.png"
                        ]
                        for i, alien_name in enumerate(enemy_ships_to_copy):
                            extract_sprite_from_sheet(sheet_image_path, alien_name, sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "aliens", f"alien_ship_{i+1:02d}.png"))
                        
                        # Бонусы (спрайты)
                        extract_sprite_from_sheet(sheet_image_path, "powerupBlue_bolt.png", sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "powerups", "powerup_bolt.png"))
                        extract_sprite_from_sheet(sheet_image_path, "powerupBlue_shield.png", sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "powerups", "powerup_shield.png"))
                        extract_sprite_from_sheet(sheet_image_path, "powerupBlue_star.png", sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "powerups", "powerup_star.png"))

                        # Эффекты взрыва (спрайты) - 3 кадра анимации. Используем "fire" из sheet.png.
                        explosion_sprite_names = ["fire00.png", "fire01.png", "fire02.png"]
                        for i, exp_name in enumerate(explosion_sprite_names):
                             extract_sprite_from_sheet(sheet_image_path, exp_name, sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "explosions", f"explosion{i+1:02d}.png"))

                        # UI рамка (blue_panel.png) - используем "buttonBlue.png" из sheet.png
                        extract_sprite_from_sheet(sheet_image_path, "buttonBlue.png", sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "ui", "frames", "blue_panel.png"))

                        # Фоновые элементы (звездное поле)
                        extract_sprite_from_sheet(sheet_image_path, "meteorBrown_big1.png", sprite_coords, os.path.join(ASSETS_BASE_DIR, "gfx", "backgrounds", "background01.png"))
                        print("  Внимание: Используется 'meteorBrown_big1.png' как фон. Возможно, в папке 'Backgrounds' Space Shooter Redux есть более подходящие фоны, которые можно скопировать вручную.")

                    else:
                        print("  Невозможно вырезать спрайты из sheet.png, так как координаты не загружены.")
                
                elif key == "cc0_spaceship_sprites": # Для дополнительного разнообразия пришельцев
                    aliens_source_dir_candidates = [
                        os.path.join(destination_unzip_dir, "200Starships", "Clean"),
                        os.path.join(destination_unzip_dir, "200Starships", "Raw"),
                        os.path.join(destination_unzip_dir, "200Starships", "Shaded"),
                        os.path.join(destination_unzip_dir, "200Starships"),
                        destination_unzip_dir
                    ]
                    
                    aliens_source_dir = None
                    for candidate_dir in aliens_source_dir_candidates:
                        if os.path.exists(candidate_dir):
                            if any(f.lower().endswith(".png") for f in os.listdir(candidate_dir)):
                                aliens_source_dir = candidate_dir
                                break

                    if aliens_source_dir:
                        alien_ships = [f for f in os.listdir(aliens_source_dir) if f.lower().endswith(".png")]
                        
                        if len(alien_ships) >= 12:
                            print(f"  Копируем 12 дополнительных кораблей пришельцев из '{asset_info['source_temp_file']}'.")
                            for i, ship_file in enumerate(alien_ships[:12]):
                                src_path = os.path.join(aliens_source_dir, ship_file)
                                dest_path = os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "aliens", f"alien_ship_{i+13:02d}.png")
                                copy_file(src_path, dest_path)
                        else:
                            print(f"  Внимание: В '{asset_info['source_temp_file']}' найдено только {len(alien_ships)} кораблей. Ожидалось 12 дополнительных. Копируем все найденные.")
                            for i, ship_file in enumerate(alien_ships):
                                src_path = os.path.join(aliens_source_dir, ship_file)
                                dest_path = os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "aliens", f"alien_ship_{i+13:02d}.png")
                                copy_file(src_path, dest_path)
                    else:
                        print(f"  Ошибка: Не найдена подходящая директория с PNG-кораблями пришельцев в {destination_unzip_dir}. Проверьте структуру архива.")
                else:
                    print(f"  Нет специальной логики копирования для '{key}'. Если ожидались файлы, убедитесь, что они указаны в 'files_to_copy_mapping'.")

    # Временные файлы сохраняем, чтобы не скачивать каждый раз
    print(f"\nВременные файлы сохранены в '{TEMP_DIR}'. При повторном запуске они будут использованы.")


    # Шаг 3: Добавление файлов в Git и коммит
    print("\n--- Добавление ассетов в Git и коммит ---")
    
    gitignore_path = ".gitignore"
    gitignore_content = """
# Python
__pycache__/
*.pyc

# Virtual environment
venv/

# Temporary assets download folder
temp_assets_download/
"""
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content.strip())
        print(f"Создан файл {gitignore_path} для игнорирования временных файлов.")
    else:
        with open(gitignore_path, "r+") as f:
            content = f.read()
            changed = False
            if "temp_assets_download/" not in content:
                f.write("\n# Temporary assets download folder\ntemp_assets_download/\n")
                changed = True
            if "venv/" not in content:
                f.write("\n# Virtual environment\venv/\n")
                changed = True
            if changed:
                print(f"Обновлен файл {gitignore_path} для игнорирования временных файлов и venv.")
                
    run_git_command(f"git add {ASSETS_BASE_DIR}")
    run_git_command(f"git add add_assets.py")
    run_git_command(f"git add {gitignore_path}")

    if run_git_command('git commit -m "Добавлены все необходимые игровые ассеты"'):
        print("\nКоммит успешно создан. Попытка отправить изменения на удаленный репозиторий...")
        print("Пожалуйста, убедитесь, что у вас настроены учетные данные Git для 'git push'.")
        if run_git_command("git push"):
            print("\nВсе ассеты успешно добавлены в репозиторий и отправлены!")
        else:
            print("\nНе удалось отправить изменения на удаленный репозиторий. Попробуйте 'git push' вручную.")
    else:
        print("\nНе удалось создать коммит. Возможно, нечего коммитить или есть другие ошибки. Проверьте сообщения выше.")

    print("\nПроцесс завершен.")

if __name__ == "__main__":
    main()
