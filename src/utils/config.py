"""
Configuration loading and management.
"""
import json
import os

def load_config(config_file="data/game_config/config.json"):
    """Load game configuration from a JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Try to load from file if exists
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
    except Exception as e:
        print(f"Lỗi khi tải cấu hình: {e}")
    
    # Create default config
    default_config = {
        "screen_width": 1024,
        "screen_height": 768,
        "ai_turn_interval": 5000,  # ms
        "camera_range_default": 3,
        "decoy_duration": 30,  # seconds
        "enable_sound": True,
        "difficulty": "medium",
        "use_mock_prolog": True  # Set to True to use mock Prolog
    }
    
    # Save default config
    try:
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình mặc định: {e}")
    
    return default_config

def save_config(config, config_file="data/game_config/config.json"):
    """Save game configuration to a JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình: {e}")
        return False
