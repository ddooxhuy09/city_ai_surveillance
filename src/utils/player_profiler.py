"""Module for tracking and analyzing player behavior."""
import os
import json
import time
from collections import defaultdict

class PlayerProfiler:
    def __init__(self, player_id="default_player"):
        """Initialize player profiler with a player ID."""
        self.player_id = player_id
        self.profile_path = f"data/player_profiles/{player_id}_history.json"
        self.detection_success = 0  # AI bị phát hiện
        self.detection_failure = 0  # AI thoát thành công
        self.games_played = 0
        self.camera_placement_patterns = defaultdict(int)
        self.common_mistakes = defaultdict(int)
        self.game_sessions = []
        
        self.load_profile()
        
    def load_profile(self):
        """Load player profile from file if it exists."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            
            if os.path.exists(self.profile_path):
                with open(self.profile_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load basic stats
                    self.detection_success = data.get("detection_success", 0)
                    self.detection_failure = data.get("detection_failure", 0)
                    self.games_played = data.get("games_played", 0)
                    
                    # Load patterns
                    if "camera_placement_patterns" in data:
                        self.camera_placement_patterns = defaultdict(int)
                        for key, value in data["camera_placement_patterns"].items():
                            self.camera_placement_patterns[key] = value
                            
                    # Load common mistakes
                    if "common_mistakes" in data:
                        self.common_mistakes = defaultdict(int)
                        for key, value in data["common_mistakes"].items():
                            self.common_mistakes[key] = value
                            
                    # Load game sessions if present
                    if "game_sessions" in data:
                        self.game_sessions = data["game_sessions"]
                        
        except Exception as e:
            print(f"Lỗi khi tải hồ sơ người chơi: {e}")
            # Initialize empty profile
            self.detection_success = 0
            self.detection_failure = 0
            self.games_played = 0
            self.camera_placement_patterns = defaultdict(int)
            self.common_mistakes = defaultdict(int)
            self.game_sessions = []
    
    def add_detection_success(self):
        """Add a detection success (AI was caught)."""
        self.detection_success += 1
        self.games_played += 1
        
    def add_detection_failure(self):
        """Add a detection failure (AI escaped)."""
        self.detection_failure += 1
        self.games_played += 1
        
    def record_camera_placement(self, position):
        """Record camera placement pattern."""
        pos_key = f"{position[0]}_{position[1]}"
        self.camera_placement_patterns[pos_key] += 1
        
    def record_mistake(self, mistake_type):
        """Record a common mistake made by the player."""
        self.common_mistakes[mistake_type] += 1
        
    def add_game_session(self, actions):
        """Add a game session with all actions."""
        if actions:
            self.game_sessions.append({
                "timestamp": time.time(),
                "actions": actions
            })
            
            # Analyze session to extract patterns
            self._analyze_session(actions)
            
    def _analyze_session(self, actions):
        """Analyze a game session to extract patterns."""
        # Track camera placements
        camera_positions = []
        
        for action in actions:
            if action["type"] == "place_camera" and "position" in action:
                pos = action["position"]
                pos_key = f"{pos[0]}_{pos[1]}"
                self.camera_placement_patterns[pos_key] += 1
                camera_positions.append(pos)
                
            # Identify common mistakes
            if action["type"] == "ai_escaped":
                # If AI escaped with few cameras placed
                if len(camera_positions) < 3:
                    self.record_mistake("too_few_cameras")
                    
                # Check for cameras that are too close together
                if self._has_clustered_cameras(camera_positions):
                    self.record_mistake("clustered_cameras")
                    
    def _has_clustered_cameras(self, positions, threshold=3):
        """Check if cameras are clustered too close together."""
        if len(positions) < 2:
            return False
            
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions[i+1:], i+1):
                # Manhattan distance
                distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                if distance < threshold:
                    return True
                    
        return False
        
    def get_detection_rate(self):
        """Get the success rate of detecting the AI."""
        total_games = self.detection_success + self.detection_failure
        if total_games == 0:
            return 0
        return self.detection_success / total_games
        
    def get_top_camera_positions(self, count=5):
        """Get the top N most frequent camera positions."""
        sorted_positions = sorted(
            self.camera_placement_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return dict(sorted_positions[:count])
        
    def get_common_mistakes(self, count=3):
        """Get the most common mistakes made by the player."""
        sorted_mistakes = sorted(
            self.common_mistakes.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return dict(sorted_mistakes[:count])
        
    def save_profile(self):
        """Save player profile to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            
            profile_data = {
                "player_id": self.player_id,
                "detection_success": self.detection_success,
                "detection_failure": self.detection_failure,
                "games_played": self.games_played,
                "detection_rate": self.get_detection_rate(),
                "camera_placement_patterns": dict(self.camera_placement_patterns),
                "common_mistakes": dict(self.common_mistakes),
                "common_locations": list(self.get_top_camera_positions(10).keys()),
                "last_update": time.time()
            }
            
            # Only save the last 10 game sessions to keep file size reasonable
            if self.game_sessions:
                profile_data["game_sessions"] = self.game_sessions[-10:]
                
            with open(self.profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
                
        except Exception as e:
            print(f"Lỗi khi lưu hồ sơ người chơi: {e}")
