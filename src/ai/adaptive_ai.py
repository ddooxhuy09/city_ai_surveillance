""" Advanced Adaptive AI that learns from player behavior and adapts strategies. """ 
from src.ai.reinforcement_learning import RLAgent
import random
import json
import os
from collections import defaultdict

class AdaptiveAI(RLAgent):
    def __init__(self, prolog_interface):
        """Initialize the Adaptive AI agent."""
        super().__init__(prolog_interface)
        self.camera_detection_history = {}
        self.successful_routes = []
        self.pattern_memory = {}
        self.game_time = 0
        self.deception_rate = 0.3  # Tỷ lệ tạo mồi nhử
        self.load_learning_data()

    def load_learning_data(self):
        """Load all learning data from file."""
        try:
            learning_file = "data/ai_learning/adaptive_model.json"
            if os.path.exists(learning_file):
                with open(learning_file, 'r') as f:
                    data = json.load(f)
                    
                    # Chỉ tải các dữ liệu bổ sung nếu có
                    if "camera_detection_history" in data:
                        self.camera_detection_history = data["camera_detection_history"]
                    if "pattern_memory" in data:
                        self.pattern_memory = data["pattern_memory"]
                    if "successful_routes" in data:
                        self.successful_routes = data["successful_routes"]
                    if "deception_rate" in data:
                        self.deception_rate = data["deception_rate"]
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu học tập thích ứng: {e}")

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
            
            # Giảm điểm cho đường đi này
            state_str = str(self.state)
            if state_str in self.q_table:
                for action in self.q_table[state_str]:
                    if action_leads_to(action, location):
                        self.q_table[state_str][action] -= 5.0
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
            # Chỉ tạo mồi nhử với xác suất được cấu hình
            if random.random() > self.deception_rate:
                return None
                
            # Simple implementation for mock version
            if self.prolog.use_mock:
                available_locations = ["city_center", "industrial_zone", "residential_area", "shopping_mall", "park", "train_station"]
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

    def identify_surveillance_blind_spots(self, game_map):
        """Phát hiện điểm mù trong hệ thống giám sát"""
        blind_spots = []
        camera_coverage = set()
        
        # Thu thập vùng phủ sóng của tất cả camera
        for camera in game_map.cameras:
            for x in range(game_map.size):
                for y in range(game_map.size):
                    if game_map.grid[x][y] == 0 and camera.can_see(x, y, game_map):
                        camera_coverage.add((x, y))
        
        # Tìm điểm mù (các ô đường đi không bị phát hiện)
        for x in range(game_map.size):
            for y in range(game_map.size):
                if game_map.grid[x][y] == 0 and (x, y) not in camera_coverage:
                    blind_spots.append((x, y))
        
        # Tăng giá trị Q cho các đường đi qua điểm mù
        for spot in blind_spots:
            for state in self.q_table:
                for action in self.q_table[state]:
                    # Tăng giá trị cho hành động dẫn đến điểm mù
                    if self._action_leads_to_spot(action, spot, game_map):
                        self.q_table[state][action] += 2.0
                        
        return blind_spots

    def _action_leads_to_spot(self, action, spot, game_map):
        """Kiểm tra xem hành động có dẫn đến điểm mù không"""
        # Giả lập đơn giản - trong thực tế cần phức tạp hơn
        if isinstance(action, str) and not action.startswith("create_decoy"):
            location_x, location_y = game_map.get_position_for_location(action)
            spot_x, spot_y = spot
            
            # Nếu gần với điểm mù
            distance = abs(location_x - spot_x) + abs(location_y - spot_y)
            return distance <= 2
            
        return False

    def adapt_to_player_strategy(self, player_id):
        """Điều chỉnh chiến lược dựa trên lịch sử chơi của người chơi cụ thể"""
        player_history_file = f"data/player_profiles/{player_id}_history.json"
        
        if os.path.exists(player_history_file):
            try:
                with open(player_history_file, 'r') as f:
                    player_data = json.load(f)
                    
                # Phân tích xu hướng đặt camera của người chơi
                if "camera_placement_patterns" in player_data:
                    self.counter_camera_patterns(player_data["camera_placement_patterns"])
                    
                # Điều chỉnh tỷ lệ tạo mồi nhử dựa trên phong cách chơi
                if "detection_rate" in player_data:
                    if player_data["detection_rate"] > 0.7:  # Người chơi giỏi phát hiện
                        self.deception_rate = 0.8  # Tăng tỷ lệ tạo mồi nhử
                    else:
                        self.deception_rate = 0.3  # Giảm tỷ lệ tạo mồi nhử
            except Exception as e:
                print(f"Lỗi khi thích nghi với chiến lược người chơi: {e}")
                
        # Điều chỉnh tham số thăm dò/khai thác
        games_played = self.get_games_played(player_id)
        self.exploration_rate = max(0.05, 0.3 - (games_played * 0.01))

    def counter_camera_patterns(self, patterns):
        """Phát triển chiến lược đối phó với mẫu đặt camera"""
        try:
            # Ví dụ đơn giản: Tăng điểm cho hành động né tránh camera thường gặp
            common_camera_locations = patterns.get("common_locations", [])
            
            for location in common_camera_locations:
                # Tăng điểm cho hành động tránh các vị trí camera phổ biến
                for state in self.q_table:
                    for action in self.q_table[state]:
                        if action != location and action != "create_decoy":
                            # Tăng giá trị cho hành động tránh vị trí camera phổ biến
                            self.q_table[state][action] += 1.0
        except Exception as e:
            print(f"Lỗi khi đối phó với mẫu camera: {e}")

    def get_games_played(self, player_id):
        """Lấy số lượng trò chơi đã chơi với người chơi cụ thể"""
        try:
            player_history_file = f"data/player_profiles/{player_id}_history.json"
            
            if os.path.exists(player_history_file):
                with open(player_history_file, 'r') as f:
                    player_data = json.load(f)
                    return player_data.get("games_played", 0)
            return 0
        except Exception as e:
            print(f"Lỗi khi lấy số trò chơi đã chơi: {e}")
            return 0

    def save_learning_data(self, filename=None):
        """Save all learning data to a file."""
        if filename is None:
            filename = "data/ai_learning/adaptive_model.json"
            
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
                "successful_routes": self.successful_routes,
                "deception_rate": self.deception_rate
            }

            with open(filename, 'w') as f:
                json.dump(learning_data, f, indent=4, default=str)
                
            # Tối ưu hóa định kỳ
            if random.random() < 0.2:  # 20% cơ hội tối ưu hóa
                self.optimize_q_table()
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu học tập: {e}")
