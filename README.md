# Alien Invasion

## Project Overview

Alien Invasion is a classic arcade-style space shooter game. The player controls a spaceship at the bottom of the screen, tasked with defending Earth from waves of descending aliens. The core objective is to shoot down as many aliens as possible, achieve a high score, and survive for as many levels as you can.

Key features include:
*   **Dynamic Alien Fleets:** Aliens move across and down the screen in formations.
*   **Player Ship Controls:** Smooth left/right movement and bullet firing.
*   **Progressive Difficulty:** Game difficulty increases with each level, with aliens becoming faster and potentially more numerous.
*   **Scoring System:** Points are awarded for destroying aliens, with a persistent high score saved locally.
*   **Power-ups:** Collectible items like shields and double-fire to aid the player.
*   **Multiple Lives:** The player starts with a set number of ships (lives).
*   **Visual Effects:** Includes a scrolling starfield background, animated sprites, and visual feedback for game events.
*   **Sound Effects:** Audio feedback for actions like shooting, explosions, and power-up collection.
*   **Game States:** Clear menu, gameplay, paused, and game over states.

## Setup Instructions

Follow these steps to set up and run Alien Invasion on your local machine.

**Prerequisites:**
*   Python 3.x installed on your system.
*   Pip (Python package installer), which usually comes with Python.

**1. Clone the Repository:**
   Open your terminal or command prompt and clone the repository using Git:
   ```bash
   git clone <repository_url>
   cd <repository_directory_name>
   ```
   (Replace `<repository_url>` with the actual URL of the Git repository and `<repository_directory_name>` with the name of the directory created by cloning.)

**2. Install Dependencies:**
   The game relies on Pygame and other potential libraries. These are listed in `requirements.txt`. Install them using pip:
   ```bash
   pip install -r requirements.txt
   ```

**3. Run the Game:**
   Once the dependencies are installed, you can run the game from the project's root directory:
   ```bash
   python alien_invasion/alien_invasion.py
   ```
   Or, if you are already in the `alien_invasion` directory:
   ```bash
   python alien_invasion.py
   ```

## How to Play

**Objective:**
Your main goal is to destroy incoming waves of aliens before they reach the bottom of the screen or collide with your ship. Survive as long as possible and aim for the highest score.

**Controls:**
*   **Move Left:** Press the `LEFT ARROW` key.
*   **Move Right:** Press the `RIGHT ARROW` key.
*   **Fire Bullet:** Press the `SPACEBAR`.
*   **Pause/Resume:** Press the `P` key to toggle pause during gameplay.
*   **Navigate Menus/Exit:**
    *   Use the `MOUSE` to click buttons in the main menu, pause menu, or game over screen.
    *   Press `ESC` during gameplay or in the pause menu to return to the main menu.
    *   Press `ESC` in the main menu or game over screen to quit the game.
    *   Press `Q` at any time to quit the game immediately.

**Gameplay Loop:**
1.  **Start:** Begin from the main menu by clicking "New Game".
2.  **Waves of Aliens:** Aliens will appear at the top of the screen and move horizontally. When they reach the edge of the screen, they drop down and reverse direction.
3.  **Shooting:** Control your ship to shoot bullets at the aliens. Each destroyed alien earns you points.
4.  **Player Lives:** You start with a set number of lives (ships). If an alien collides with your ship (and your shield is not active), or if an alien reaches the bottom of the screen, you lose a life. The game ends when you run out of lives.
5.  **Levels:** Successfully destroying an entire fleet of aliens advances you to the next level. Each new level typically increases the difficulty, such as faster aliens or different fleet configurations.
6.  **Scoring:** Your score increases with each alien destroyed. The game keeps track of your current score and a high score, which is saved between game sessions.

**Power-ups:**
Occasionally, destroyed aliens will drop power-ups. Move your ship over them to collect:
*   **Shield:** Provides temporary invulnerability from alien collisions. Your ship will have a visual shield effect.
*   **Double Fire:** Allows your ship to shoot two bullets simultaneously for a limited time.

## Code Structure

The game is organized into several Python files, each managing a specific aspect of the game:

*   `alien_invasion/alien_invasion.py`: The main game file that initializes the game, runs the primary game loop, and manages game states.
*   `alien_invasion/settings.py`: Contains the `Settings` class, which stores and manages all game settings like screen dimensions, speeds, colors, and difficulty parameters.
*   `alien_invasion/ship.py`: Defines the `Ship` class, responsible for the player's spaceship, its movement, and appearance.
*   `alien_invasion/alien.py`: Defines the `Alien` class, responsible for individual alien behavior, appearance, and movement within the fleet.
*   `alien_invasion/bullet.py`: Defines the `Bullet` class, managing the properties and behavior of bullets fired by the player's ship.
*   `alien_invasion/game_stats.py`: Manages game statistics like current score, high score, level, and remaining player lives.
*   `alien_invasion/scoreboard.py`: Handles the display of scoring information, level, and remaining lives on the screen.
*   `alien_invasion/button.py`: Provides a `Button` class for creating clickable buttons used in menus and game over screens.
*   `alien_invasion/powerup.py`: Defines the `PowerUp` class, managing the behavior and appearance of collectible power-ups.
*   `alien_invasion/starfield.py`: Creates and manages a scrolling starfield effect for the game's background.
*   `alien_invasion/space_object.py`: Manages decorative space objects (like planets and galaxies) that appear in the background.

## Asset Management

Game assets such as images and sounds are organized within the `assets/` directory. This directory is further structured to separate different types of assets:

*   **`assets/audio/sfx/`**: Contains sound effects for game events like laser shots, explosions, and power-up collections.
*   **`assets/audio/music/`**: Intended for background music tracks (though current implementation might have this commented out or pending).
*   **`assets/gfx/`**: Contains graphics and images, further subdivided into:
    *   `assets/gfx/ships/player/`: Sprites for the player's ship.
    *   `assets/gfx/ships/aliens/`: Sprites for various alien ships.
    *   `assets/gfx/powerups/`: (Assumed location, e.g., if power-ups had dedicated sprites beyond simple colored rectangles). Currently, power-ups are drawn shapes, but image assets would go here.
    *   `assets/gfx/ui/icons/`: Icons used for UI elements like hearts for lives or pause symbols.
    *   `assets/gfx/ui/frames/`: Images used for UI frames, like the panel behind the score.
    *   `assets/gfx/planets/`: Sprites for decorative background planets and galaxies.

The game includes fallback mechanisms for some assets. For instance, if specific ship or alien sprites fail to load, the game may default to simpler geometric shapes or placeholder images to ensure it can still run.

A script named `download_assets.sh` (if present in the repository) would typically be used to download and place larger asset files from an external source if they are not directly included in the Git repository to save space.

## Contributing

Contributions to Alien Invasion are welcome! Here are a few ways you can help:

*   **Reporting Bugs:** If you find a bug, please open an issue on the GitHub Issues page for this project. Describe the bug in detail, including steps to reproduce it.
*   **Suggesting Features:** Have an idea for a new feature or an improvement to an existing one? Feel free to open an issue to discuss it.
*   **Code Contributions:** If you'd like to contribute code, please fork the repository and submit a pull request with your changes. Ensure your code follows the existing style and includes comments where necessary.

We aim to create a welcoming environment for contributors.

## Troubleshooting/FAQ

Here are some common issues and how to resolve them:

*   **Q: The game doesn't start and I see an error like `ModuleNotFoundError: No module named 'pygame'`.**
    *   **A:** This means Pygame is not installed. You can install it by running:
        ```bash
        pip install pygame
        ```
        Alternatively, ensure you have installed all dependencies from the `requirements.txt` file:
        ```bash
        pip install -r requirements.txt
        ```

*   **Q: The game runs slowly or lags.**
    *   **A:**
        *   Ensure your computer meets the basic requirements for running Pygame games.
        *   Close other resource-intensive applications running in the background.
        *   If applicable to your system, ensure your graphics drivers are up to date.

*   **Q: There is no sound in the game.**
    *   **A:**
        *   Check your computer's system volume and ensure it's not muted or too low.
        *   Verify that your speakers or headphones are properly connected and working.
        *   The game has an audio initialization sequence. If it fails to initialize the primary audio driver, it may attempt a dummy driver, resulting in no sound. Check the console output when the game starts for messages related to "pygame.mixer" or "audio system".
        *   The game also has an `audio_enabled` setting in `settings.py`; ensure this is `True` if you expect sound.

*   **Q: I'm getting errors about missing asset files.**
    *   **A:**
        *   Ensure you have correctly cloned or downloaded the entire project, including the `assets/` directory.
        *   If the project includes a `download_assets.sh` script or similar instructions for obtaining assets, make sure you have run it.
        *   The game attempts to use fallback assets if primary ones are missing, but critical assets might still cause issues if not found.
