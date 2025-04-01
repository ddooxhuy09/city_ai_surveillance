"""
Utilities for data storage and retrieval.
"""
import json
import pickle
import os
import time

class DataStorage:
    def __init__(self, base_dir="data"):
        """Initialize data storage with base directory."""
        self.base_dir = base_dir
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            os.path.join(self.base_dir, "ai_learning"),
            os.path.join(self.base_dir, "game_config"),
            os.path.join(self.base_dir, "saved_games")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_json(self, data, filename, subdirectory=None):
        """Save data as JSON."""
        filepath = self._get_filepath(filename, subdirectory)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_json(self, filename, subdirectory=None):
        """Load data from JSON."""
        filepath = self._get_filepath(filename, subdirectory)
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"Error parsing JSON file {filepath}")
            return None
    
    def save_pickle(self, data, filename, subdirectory=None):
        """Save data using pickle."""
        filepath = self._get_filepath(filename, subdirectory)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load_pickle(self, filename, subdirectory=None):
        """Load data using pickle."""
        filepath = self._get_filepath(filename, subdirectory)
        
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
        except pickle.PickleError:
            print(f"Error unpickling file {filepath}")
            return None
    
    def save_game_state(self, game_state, ai_state):
        """Save the current game state with timestamp."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"game_save_{timestamp}.json"
        
        data = {
            "timestamp": timestamp,
            "game_state": game_state,
            "ai_state": ai_state
        }
        
        self.save_json(data, filename, "saved_games")
        return filename
    
    def list_saved_games(self):
        """List all saved games."""
        saved_games_dir = os.path.join(self.base_dir, "saved_games")
        
        try:
            files = os.listdir(saved_games_dir)
            return [f for f in files if f.startswith("game_save_") and f.endswith(".json")]
        except FileNotFoundError:
            return []
    
    def _get_filepath(self, filename, subdirectory=None):
        """Get the full filepath."""
        if subdirectory:
            directory = os.path.join(self.base_dir, subdirectory)
            os.makedirs(directory, exist_ok=True)
            return os.path.join(directory, filename)
        else:
            return os.path.join(self.base_dir, filename)
