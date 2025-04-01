"""
Advanced Adaptive AI that learns from player behavior and adapts strategies.
"""
from src.ai.reinforcement_learning import RLAgent
import random
import json
import os

class AdaptiveAI(RLAgent):
    def __init__(self, prolog_interface):
        """Initialize the Adaptive AI agent."""
        super().__init__(prolog_interface)
        self.camera_detection_history = {}
        self.successful_routes = []
        self.pattern_memory = {}
        self.game_time = 0
        
    def learn_from_detection(self, camera_id, location):
        """Learn from being detected by a camera."""
        try:
            if camera_id not in self.camera_detection_history:
                self.camera_detection_history[camera_id] = []
            
            self.camera_detection_history[camera_id].append({
                "location": location,
                "time": self.game_time,
                "ai_state": self.state
            })
            
            # Update Prolog with new information
            self.prolog.query(f"learn_camera_pattern({camera_id})")
        except Exception as e:
            print(f"Lỗi khi học từ phát hiện camera: {e}")
        
    def analyze_player_patterns(self, player_actions):
        """Analyze player behavior patterns."""
        try:
            for action in player_actions:
                action_type = action["type"]
                if action_type not in self.pattern_memory:
                    self.pattern_memory[action_type] = []
                
                self.pattern_memory[action_type].append({
                    "details": action["details"],
                    "time": action["time"],
                    "ai_position": action["ai_position"]
                })
            
            # Find patterns in player actions
            if "place_camera" in self.pattern_memory and len(self.pattern_memory["place_camera"]) > 3:
                recent_cameras = self.pattern_memory["place_camera"][-3:]
                self.predict_next_camera_placement(recent_cameras)
        except Exception as e:
            print(f"Lỗi khi phân tích mẫu hành vi người chơi: {e}")
    
    def predict_next_camera_placement(self, recent_cameras):
        """Predict the next camera placement by the player."""
        try:
            # Analyze recent camera positions
            locations = [cam["details"]["location"] for cam in recent_cameras]
            
            # Check for path pattern
            path_query = f"connected({locations[0]}, {locations[1]}), connected({locations[1]}, {locations[2]})"
            is_path = list(self.prolog.query(path_query))
            
            if is_path:
                # Predict next camera based on trend
                next_loc_query = f"connected({locations[2]}, NextLoc), NextLoc \\= {locations[1]}"
                possible_next = list(self.prolog.query(next_loc_query))
                
                if possible_next:
                    # Avoid potentially new camera locations
                    for loc in possible_next:
                        next_loc = loc["NextLoc"]
                        state_str = str(self.state)
                        if state_str in self.q_table and next_loc in self.q_table[state_str]:
                            self.q_table[state_str][next_loc] -= 5.0
        except Exception as e:
            print(f"Lỗi khi dự đoán vị trí camera tiếp theo: {e}")
    
    def generate_deception_strategy(self):
        """Generate a deception strategy based on learning."""
        try:
            # Simple implementation for mock version
            if self.prolog.use_mock:
                available_locations = ["city_center", "industrial_zone", "residential_area", 
                                      "shopping_mall", "park", "train_station"]
                current_loc = self.state[0]
                decoy_locations = [loc for loc in available_locations if loc != current_loc]
                if decoy_locations:
                    return {
                        "action": "create_decoy",
                        "location": random.choice(decoy_locations),
                        "timing": {"type": "immediate"}
                    }
                return None
            
            # For real Prolog
            best_decoy_query = """
            findall(Loc-Eff, (
                location(Loc), 
                can_create_decoy(Loc), 
                evaluate_decoy_effectiveness(Loc, Eff)
            ), Decoys),
            sort(2, @>=, Decoys, [BestLoc-_|_])
            """
            result = list(self.prolog.query(best_decoy_query))
            
            if result and "BestLoc" in result[0]:
                best_location = result[0]["BestLoc"]
                return {
                    "action": "create_decoy",
                    "location": best_location,
                    "timing": self.determine_optimal_timing()
                }
            return None
        except Exception as e:
            print(f"Lỗi khi tạo chiến lược đánh lừa: {e}")
            return None
    
    def determine_optimal_timing(self):
        """Determine optimal timing for deception."""
        try:
            # Analyze player camera checking patterns
            if "check_camera" in self.pattern_memory and len(self.pattern_memory["check_camera"]) > 5:
                time_diffs = []
                checks = self.pattern_memory["check_camera"][-5:]
                
                for i in range(1, len(checks)):
                    time_diffs.append(checks[i]["time"] - checks[i-1]["time"])
                
                avg_time = sum(time_diffs) / len(time_diffs)
                return {
                    "type": "after_check",
                    "delay": avg_time * 0.3
                }
            
            return {
                "type": "immediate"
            }
        except Exception as e:
            print(f"Lỗi khi xác định thời điểm tối ưu: {e}")
            return {"type": "immediate"}
    
    def save_learning_data(self, filename):
        """Save all learning data to a file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Convert state tuples to strings for JSON
            camera_history = {}
            for cam_id, detections in self.camera_detection_history.items():
                camera_history[str(cam_id)] = []
                for detection in detections:
                    detection_copy = detection.copy()
                    detection_copy["ai_state"] = str(detection_copy["ai_state"])
                    camera_history[str(cam_id)].append(detection_copy)
            
            learning_data = {
                "q_table": self.q_table,
                "camera_detection_history": camera_history,
                "pattern_memory": self.pattern_memory,
                "successful_routes": self.successful_routes
            }
            
            with open(filename, 'w') as f:
                json.dump(learning_data, f, indent=4, default=str)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu học tập: {e}")
