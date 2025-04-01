"""
Manages the state of the game including player score, AI position, and game status.
"""
import time
import random

class GameState:
    def __init__(self, prolog, city_map):
        """Initialize game state with Prolog interface and city map."""
        self.prolog = prolog
        self.city_map = city_map
        self.player_score = 0
        self.ai_score = 0
        self.game_time = 0
        self.player_actions = []
        self.cameras = []
        self.sensors = []
        self.decoy_signals = []
        self.ai_position = "city_center"  # Default starting position
        self.game_over = False
        self.game_result = None
        
    def update(self, dt):
        """Update game state based on time delta."""
        self.game_time += dt / 1000.0  # Convert ms to seconds
        
        # Update decoy signals (they expire after some time)
        current_time = time.time()
        self.decoy_signals = [decoy for decoy in self.decoy_signals 
                             if current_time - decoy["time_created"] < decoy["duration"]]
    
    def place_camera(self, location, range_val=3):
        """Place a camera at the specified location."""
        camera_id = len(self.cameras) + 1
        camera = {
            "id": camera_id,
            "location": location,
            "range": range_val,
            "time_placed": self.game_time
        }
        self.cameras.append(camera)
        
        # Update Prolog with camera information
        try:
            self.prolog.assertz(f"camera({camera_id}, {location}, {range_val})")
        except Exception as e:
            print(f"Lỗi khi cập nhật Prolog: {e}")
        
        # Record player action
        self.player_actions.append({
            "type": "place_camera",
            "details": {
                "id": camera_id,
                "location": location,
                "range": range_val
            },
            "time": self.game_time,
            "ai_position": self.ai_position
        })
    
    def check_camera(self, camera_id):
        """Check a camera for AI detection."""
        # Record player action
        self.player_actions.append({
            "type": "check_camera",
            "details": {
                "camera_id": camera_id
            },
            "time": self.game_time,
            "ai_position": self.ai_position
        })
        
        # Find camera in the list
        camera_data = next((cam for cam in self.cameras if cam["id"] == camera_id), None)
        if not camera_data:
            return None
        
        # Check if camera detects AI
        detects_ai = False
        try:
            if self.prolog.use_mock:
                # For mock Prolog, use simple distance check
                camera_loc = camera_data["location"]
                cam_x, cam_y = self.city_map[camera_loc]
                ai_x, ai_y = self.city_map[self.ai_position]
                
                # Calculate distance
                distance = ((cam_x - ai_x) ** 2 + (cam_y - ai_y) ** 2) ** 0.5
                
                # Check if within range (convert range to pixels)
                detects_ai = distance < camera_data["range"] * 100
            else:
                # For real Prolog
                detection_query = f"camera_coverage({camera_id}, {self.ai_position})"
                detected = list(self.prolog.query(detection_query))
                detects_ai = len(detected) > 0
        except Exception as e:
            print(f"Lỗi khi kiểm tra camera: {e}")
        
        # Check for decoy signals
        decoys_detected = []
        for decoy in self.decoy_signals:
            try:
                if self.prolog.use_mock:
                    # For mock Prolog, use simple distance check
                    camera_loc = camera_data["location"]
                    cam_x, cam_y = self.city_map[camera_loc]
                    decoy_x, decoy_y = self.city_map[decoy["location"]]
                    
                    # Calculate distance
                    distance = ((cam_x - decoy_x) ** 2 + (cam_y - decoy_y) ** 2) ** 0.5
                    
                    # Check if within range
                    if distance < camera_data["range"] * 100:
                        decoys_detected.append(decoy)
                else:
                    # For real Prolog
                    decoy_query = f"camera_coverage({camera_id}, {decoy['location']})"
                    if list(self.prolog.query(decoy_query)):
                        decoys_detected.append(decoy)
            except Exception as e:
                print(f"Lỗi khi kiểm tra tín hiệu giả: {e}")
        
        return {
            "detects_ai": detects_ai,
            "decoys_detected": decoys_detected
        }
    
    def create_false_alert(self, location):
        """Create a false alert at the specified location."""
        decoy = {
            "id": len(self.decoy_signals) + 1,
            "location": location,
            "strength": 70 + random.random() * 30,  # Random strength between 70-100
            "time_created": time.time(),
            "duration": 30.0  # Seconds
        }
        self.decoy_signals.append(decoy)
        
        # Update Prolog
        try:
            self.prolog.assertz(f"decoy_signal({location}, {decoy['strength']})")
        except Exception as e:
            print(f"Lỗi khi tạo tín hiệu giả trong Prolog: {e}")
    
    def update_ai_position(self, position):
        """Update the AI's position in the game state."""
        self.ai_position = position
    
    def is_game_over(self):
        """Check if the game is over."""
        return self.game_over
    
    def set_game_over(self, result):
        """Set the game as over with a result."""
        self.game_over = True
        self.game_result = result
    
    def get_game_result(self):
        """Get the result of the game."""
        return self.game_result
