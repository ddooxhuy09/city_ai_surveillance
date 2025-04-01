#!/usr/bin/env python3
# Main entry point for the game
import pygame
import sys
import os
from src.game.game_engine import GameEngine
from src.utils.config import load_config

# Kiểm tra và tạo thư mục prolog nếu chưa tồn tại
print(f"Thư mục làm việc hiện tại: {os.getcwd()}")
prolog_dir = os.path.join(os.getcwd(), "prolog")
print(f"Kiểm tra thư mục prolog tồn tại: {os.path.exists(prolog_dir)}")
if not os.path.exists(prolog_dir):
    os.makedirs(prolog_dir)
    print("Đã tạo thư mục prolog")

def main():
    """Main entry point for the City AI Surveillance game."""
    config = load_config()
    
    # Đặt giá trị này thành False nếu muốn sử dụng Prolog thực, True nếu gặp lỗi
    config["use_mock_prolog"] = True
    
    try:
        game = GameEngine(config)
        game.run()
    except Exception as e:
        print(f"Lỗi khi chạy game: {e}")
        import traceback
        traceback.print_exc()
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
