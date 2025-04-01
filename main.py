#!/usr/bin/env python3
# Main entry point for the game
import pygame
import sys
import os
import argparse
from src.game.game_engine import GameEngine
from src.utils.config import load_config

# Kiểm tra và tạo thư mục prolog nếu chưa tồn tại
print(f"Thư mục làm việc hiện tại: {os.getcwd()}")
prolog_dir = os.path.join(os.getcwd(), "prolog")
print(f"Kiểm tra thư mục prolog tồn tại: {os.path.exists(prolog_dir)}")
if not os.path.exists(prolog_dir):
    os.makedirs(prolog_dir)
    print("Đã tạo thư mục prolog")

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
    parser = argparse.ArgumentParser(description='City AI Surveillance Game')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--map-size', type=int, default=20, help='Size of the map grid (NxN)')
    parser.add_argument('--use-mock-prolog', action='store_true', help='Use mock Prolog interface')
    return parser.parse_args()

def main():
    """Main entry point for the City AI Surveillance game."""
    args = parse_arguments()
    config = load_config()
    
    # Update config with command line arguments
    config["debug_mode"] = args.debug
    config["map_size"] = args.map_size or 30  # Default to larger 30x30 map
    config["use_mock_prolog"] = args.use_mock_prolog if hasattr(args, 'use_mock_prolog') else True
    
    # Game settings
    config["cell_size"] = 25  # Slightly smaller cells to fit the larger map on screen
    config["colors"] = {
        "background": (255, 255, 255),  # White for background
        "barrier": (0, 100, 255),       # Blue for barriers/blocks
        "street": (150, 150, 150),      # Gray for streets
        "camera": (255, 0, 0),          # Red for cameras
        "ai": (0, 200, 0),              # Green for AI character (fallback)
        "camera_vision": (255, 200, 200, 100)  # Transparent red for camera vision
    }
    
    try:
        pygame.init()
        game = GameEngine(config)
        game.run()
    except Exception as e:
        print(f"Lỗi khi chạy game: {e}")
        import traceback
        traceback.print_exc()
        input("Nhấn Enter để thoát...")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
