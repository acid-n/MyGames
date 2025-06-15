import os
import zipfile
import shutil
import subprocess

# --- Конфигурация ---
# Базовая директория для ассетов относительно скрипта
ASSETS_BASE_DIR = "assets"
# Временная директория для ручных загрузок
TEMP_DIR = "temp_assets_download"

# Список директорий, которые нужно создать
DIRECTORIES = [
    os.path.join(ASSETS_BASE_DIR, "gfx", "planets"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ui", "frames"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "player"),
    os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "aliens"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "laser"), # Эти папки все равно создадим
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "powerup"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "shield"),
    os.path.join(ASSETS_BASE_DIR, "audio", "sfx", "explosion"), # Эта папка тоже создастся, но пока будет пустой
    os.path.join(ASSETS_BASE_DIR, "audio", "music"),
]

# Словари для ассетов: source_temp_file - имя файла в TEMP_DIR (как у тебя на скриншоте)
# Архив kenney_impact-sounds.zip полностью удален из этого списка.
ASSETS = {
    "kenney_space_kit": {
        "manual_download_url": "https://kenney.nl/assets/space-kit",
        "source_temp_file": "kenney_space-kit.zip", # Изменено под твой файл
        "destination_path": os.path.join(TEMP_DIR, "space-kit"),
        "files_to_copy": [
            ("planets/planetPurple_round.png", os.path.join(ASSETS_BASE_DIR, "gfx", "planets", "planet01.png")),
            ("planets/planetBlue_round.png", os.path.join(ASSETS_BASE_DIR, "gfx", "planets", "planet02.png")),
            ("planets/planetRed_round.png", os.path.join(ASSETS_BASE_DIR, "gfx", "planets", "planet03.png")),
            ("planets/galaxy.png", os.path.join(ASSETS_BASE_DIR, "gfx", "planets", "galaxy01.png")),
            ("planets/galaxy.png", os.path.join(ASSETS_BASE_DIR, "gfx", "planets", "galaxy02.png")), # Копия
        ]
    },
    "kenney_ui_pack_sci_fi": { # Оставил имя ключа старым, чтобы не менять логику ниже
        "manual_download_url": "https://kenney.nl/assets/ui-pack-sci-fi",
        "source_temp_file": "kenney_ui-pack-space-expansion.zip", # Изменено под твой файл
        "destination_path": os.path.join(TEMP_DIR, "ui-pack-sci-fi"),
        "files_to_copy": [
            ("PNG/blue_panel.png", os.path.join(ASSETS_BASE_DIR, "gfx", "ui", "frames", "blue_panel.png")),
        ]
    },
    "space_shooter_redux": {
        "manual_download_url": "https://opengameart.org/content/space-shooter-redux",
        "source_temp_file": "SpaceShooterRedux.zip", # Изменено под твой файл
        "destination_path": os.path.join(TEMP_DIR, "space-shooter-redux"),
        "files_to_copy": [
            ("PNG/playerShip3_blue.png", os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "player", "playerShip3_blue.png")),
        ]
    },
    "cc0_spaceship_sprites": {
        "manual_download_url": "https://opengameart.org/content/200-cc0-spaceship-sprites",
        "source_temp_file": "200Starships.zip", # Изменено под твой файл
        "destination_path": os.path.join(TEMP_DIR, "200-cc0-spaceship-sprites"),
        "files_to_copy": [] # Будет обработано отдельно из-за нумерации
    },
    #kenney_impact_sounds полностью удален из этого списка
    "outer_space_loop_music": {
        "manual_download_url": "https://opengameart.org/content/outer-space-loop",
        "source_temp_file": "outer_space.mp3", # Изменено под твой файл (теперь .mp3)
        "destination_path": os.path.join(ASSETS_BASE_DIR, "audio", "music", "outer_space_loop.ogg"), # Назначение оставляем OGG
        "is_direct_copy": True
    }
}

# --- Вспомогательные функции (без изменений) ---

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
        print(f"Ошибка: Исходный файл не найден: {source}. Убедитесь, что он существует в распакованном архиве или в {TEMP_DIR}.")
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

# --- Основная логика скрипта ---

def main():
    print("Начало процесса добавления ассетов...")

    # Создаем временную директорию
    print(f"Создание временной директории для ручных загрузок: {TEMP_DIR}")
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Теперь не просим ничего скачивать, так как работаем с тем, что есть
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
        destination_path_for_unzip = asset_info.get("destination_path") # Это путь для распаковки архива
        destination_path_for_copy = asset_info.get("destination_path") # Это путь для прямого копирования

        if not os.path.exists(source_temp_file_path):
            print(f"  Внимание: Файл '{source_temp_file_path}' не найден. Пропускаем обработку этого ассета.")
            continue # Пропускаем обработку этого ассета, если файл не найден

        if asset_info.get("is_direct_copy", False): # Для outer_space.mp3
            # Здесь destination_path_for_copy - это assets/audio/music/outer_space_loop.ogg
            if copy_file(source_temp_file_path, destination_path_for_copy):
                print(f"  Ассет {key} успешно скопирован.")
        else: # Для архивов
            if extract_zip(source_temp_file_path, destination_path_for_unzip):
                if key == "kenney_space_kit":
                    for src, dest in asset_info["files_to_copy"]:
                        copy_file(os.path.join(destination_path_for_unzip, src), dest)
                elif key == "kenney_ui_pack_sci_fi":
                    for src, dest in asset_info["files_to_copy"]:
                        found = False
                        # Попробуем найти файл в нескольких местах, так как структура архивов Kenney может отличаться
                        for sub_dir in ["PNG", "UI", ""]: # '' для случаев без подпапки
                            full_src_path = os.path.join(destination_path_for_unzip, sub_dir, src)
                            if os.path.exists(full_src_path):
                                copy_file(full_src_path, dest)
                                found = True
                                break
                        if not found:
                            print(f"  Предупреждение: Не удалось найти {src} для {key} в ожидаемых подпапках. Проверьте структуру архива.")
                elif key == "space_shooter_redux":
                    for src, dest in asset_info["files_to_copy"]:
                        copy_file(os.path.join(destination_path_for_unzip, src), dest)
                elif key == "cc0_spaceship_sprites":
                    # Обработка 12 кораблей пришельцев
                    aliens_source_dir_candidates = [
                        os.path.join(destination_path_for_unzip, "200 CC0 spaceships (PNG)"), # Это частый путь
                        os.path.join(destination_path_for_unzip, "PNG"),
                        destination_path_for_unzip # Вдруг файлы прямо в корне архива
                    ]
                    
                    aliens_source_dir = None
                    for candidate_dir in aliens_source_dir_candidates:
                        if os.path.exists(candidate_dir):
                            aliens_source_dir = candidate_dir
                            break

                    if aliens_source_dir:
                        # Фильтруем файлы, которые выглядят как спрайты кораблей
                        alien_ships = [f for f in os.listdir(aliens_source_dir) if f.lower().endswith(".png")]
                        
                        # Дополнительная фильтрация: если есть файлы типа "alien_ship_xx.png"
                        # то сначала их, иначе просто первые 12 любых PNG
                        specific_aliens = [f for f in alien_ships if f.lower().startswith("alien_")]
                        if specific_aliens:
                            alien_ships = specific_aliens
                            
                        alien_ships.sort() # Сортируем для предсказуемого порядка
                        
                        if len(alien_ships) < 12:
                            print(f"  Предупреждение: Найдено только {len(alien_ships)} кораблей пришельцев. Ожидалось 12. Копируем все найденные.")
                        
                        for i, ship_file in enumerate(alien_ships[:12]): # Берем первые 12
                            src_path = os.path.join(aliens_source_dir, ship_file)
                            dest_path = os.path.join(ASSETS_BASE_DIR, "gfx", "ships", "aliens", f"alien_ship_{i+1:02d}.png")
                            copy_file(src_path, dest_path)
                    else:
                        print(f"  Ошибка: Не найдена подходящая директория с кораблями пришельцев в {destination_path_for_unzip}. Проверьте структуру архива.")
                # Логика для kenney_impact_sounds полностью удалена
                else:
                    print(f"  Нет специальной логики копирования для '{key}'. Проверьте скрипт, если ожидались другие действия.")

    # Временные файлы сохраняем, чтобы не скачивать каждый раз
    print(f"\nВременные файлы сохранены в '{TEMP_DIR}'. При повторном запуске они будут использованы.")


    # Шаг 3: Добавление файлов в Git и коммит
    print("\n--- Добавление ассетов в Git и коммит ---")
    
    # Добавим .gitignore для игнорирования временной папки и pycache, venv
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
        # Если .gitignore уже есть, проверим, есть ли там temp_assets_download/ и venv/
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
                
    run_git_command(f"git add {ASSETS_BASE_DIR}") # Добавляем ассеты
    run_git_command(f"git add add_assets.py") # Добавляем сам скрипт
    run_git_command(f"git add {gitignore_path}") # Добавляем .gitignore (если создан/обновлен)

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
