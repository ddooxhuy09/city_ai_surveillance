#!/usr/bin/env python3
# Main entry point for the game
import pygame
import sys
import os
import argparse
from src.game.game_engine import GameEngine
from src.utils.config import load_config
from src.ai.ai_trainer import AITrainer

# Create necessary directories
def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        "prolog",
        "data/ai_learning",
        "data/game_config",
        "data/saved_games",
        "data/player_profiles",
        "assets/sprites"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory checked/created: {directory}")

# Check and create necessary directories
ensure_directories()

# Make sure PIL/Pillow and requests are installed
try:
    import PIL
    import requests
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "requests"])
    print("Dependencies installed successfully.")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Maze Runner AI Surveillance Game')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--map-size', type=int, default=20, help='Size of the map grid (NxN)')
    parser.add_argument('--use-mock-prolog', action='store_true', help='Use mock Prolog interface')
    parser.add_argument('--show-path', action='store_true', help='Show AI path visualization')
    parser.add_argument('--train', action='store_true', help='Run AI training session')
    parser.add_argument('--episodes', type=int, default=100, help='Number of training episodes')
    return parser.parse_args()

def main():
    """Main entry point for the Maze Runner AI Surveillance game."""
    args = parse_arguments()
    config = load_config()

    # Update config with command line arguments
    config["debug_mode"] = args.debug
    config["map_size"] = args.map_size or 30  # Default to larger 30x30 map
    config["use_mock_prolog"] = args.use_mock_prolog if hasattr(args, 'use_mock_prolog') else True
    config["show_path"] = args.show_path if hasattr(args, 'show_path') else True

    # Game settings
    config["cell_size"] = 25  # Slightly smaller cells to fit the larger map on screen
    config["colors"] = {
        "background": (255, 255, 255),  # White for background
        "barrier": (50, 50, 150),       # Blue-gray for barriers/walls
        "street": (150, 150, 150),      # Gray for streets
        "camera": (255, 0, 0),          # Red for cameras
        "ai": (0, 200, 0),              # Green for AI character (fallback)
        "camera_vision": (255, 200, 200, 100)  # Transparent red for camera vision
    }

    # Run AI training if requested
    if args.train:
        print(f"Starting AI training session with {args.episodes} episodes...")
        trainer = AITrainer(config)
        trainer.train_ai_offline(num_episodes=args.episodes)
        print("Training completed!")
        return

    # Run the game
    try:
        pygame.init()
        game = GameEngine(config)
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
