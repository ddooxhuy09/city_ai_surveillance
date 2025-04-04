"""AI training module for offline learning."""
import random
import os
import json
import time
from src.ai.adaptive_ai import AdaptiveAI
from src.prolog_interface.prolog_connector import PrologConnector
from src.game.map import GameMap

class AITrainer:
    def __init__(self, config):
        """Initialize the AI trainer with configuration."""
        self.config = config
        self.prolog = PrologConnector(use_mock=config.get("use_mock_prolog", True))
        self.prolog.load_knowledge_base()
        
    def generate_random_map(self, size=None, variation=10):
        """Generate a random map for training."""
        if size is None:
            size = self.config.get("map_size", 30)
            
        # Tạo cấu hình tạm thời
        temp_config = self.config.copy()
        temp_config["map_size"] = size
        
        # Tạo bản đồ mới
        game_map = GameMap(temp_config)
        return game_map
        
    def generate_random_camera_placement(self, game_map, num_cameras=None):
        """Generate random camera placement for training."""
        if num_cameras is None:
            # Số lượng camera tỷ lệ với kích thước bản đồ
            num_cameras = game_map.size // 5
            
        cameras = []
        wall_positions = []
        
        # Tìm tất cả vị trí tường
        for x in range(game_map.size):
            for y in range(game_map.size):
                if game_map.grid[x][y] == 1:  # Là tường
                    wall_positions.append((x, y))
                    
        # Chọn ngẫu nhiên vị trí cho camera
        if wall_positions:
            sample_size = min(num_cameras, len(wall_positions))
            camera_positions = random.sample(wall_positions, sample_size)
            
            # Đặt camera
            for pos in camera_positions:
                game_map.add_camera(pos)
                cameras.append(pos)
                
        return cameras
                
    def run_simulation(self, ai_agent, game_map, max_steps=100):
        """Run a simulation with the AI on the given map."""
        # Tạo một phiên bản AI cho mô phỏng
        ai = ai_agent
        ai.pos = game_map.start_pos
        ai.path = []
        ai.path_index = 0
        ai.move_progress = 0
        ai.captured = False
        ai.escaped = False
        
        # Thực hiện mô phỏng
        steps = 0
        while steps < max_steps and not ai.captured and not ai.escaped:
            # Instead of trying to call find_path_bfs() on the AI object,
            # we should use the AITrainer's own method
            if not ai.path:
                ai.path = self.find_path_bfs(ai, game_map)
                ai.path_index = 0
                
                # Nếu không tìm thấy đường đi, kết thúc mô phỏng
                if not ai.path:
                    break
            
            # Di chuyển dọc theo đường đi
            if ai.path_index < len(ai.path):
                new_pos = ai.path[ai.path_index]
                
                # Kiểm tra nếu bị camera phát hiện
                for camera in game_map.cameras:
                    if camera.active and camera.can_see(new_pos[0], new_pos[1], game_map):
                        ai.captured = True
                        # Cập nhật Q-table với phần thưởng tiêu cực
                        state = (f"pos_{ai.pos[0]}_{ai.pos[1]}", "undetected")
                        action = f"move_to_{new_pos[0]}_{new_pos[1]}"
                        next_state = (f"pos_{new_pos[0]}_{new_pos[1]}", "detected")
                        ai.update_q_value(state, action, -10.0, next_state)
                        break
                
                # Nếu không bị phát hiện, tiếp tục di chuyển
                if not ai.captured:
                    # Cập nhật Q-table với phần thưởng nhỏ cho di chuyển thành công
                    state = (f"pos_{ai.pos[0]}_{ai.pos[1]}", "undetected")
                    action = f"move_to_{new_pos[0]}_{new_pos[1]}"
                    next_state = (f"pos_{new_pos[0]}_{new_pos[1]}", "undetected")
                    ai.update_q_value(state, action, 0.1, next_state)
                    
                    # Cập nhật vị trí
                    ai.pos = new_pos
                    ai.path_index += 1
                
                # Kiểm tra nếu đã đến exit
                if ai.pos in game_map.end_positions:
                    ai.escaped = True
                    
                    # Thưởng lớn cho việc thoát thành công
                    for i in range(max(0, len(ai.path) - 5), len(ai.path)):
                        if i < len(ai.path) - 1:
                            pos1 = ai.path[i]
                            pos2 = ai.path[i+1]
                            state = (f"pos_{pos1[0]}_{pos1[1]}", "undetected")
                            action = f"move_to_{pos2[0]}_{pos2[1]}"
                            next_state = (f"pos_{pos2[0]}_{pos2[1]}", "undetected")
                            # Thưởng cao hơn cho các bước cuối cùng
                            reward = 5.0 + (i - (len(ai.path) - 5)) * 2.0
                            ai.update_q_value(state, action, reward, next_state)
            
            steps += 1
        
        # Trả về kết quả
        result = {
            "escaped": ai.escaped,
            "captured": ai.captured,
            "steps": steps,
            "path_length": len(ai.path) if ai.path else 0
        }
        
        return result
        
    def find_path_bfs(self, ai, game_map):
        """Find a path using BFS algorithm."""
        start = game_map.start_pos
        goals = game_map.end_positions
        
        # Standard BFS implementation
        queue = [(start, [])]
        visited = {start}
        
        while queue:
            (x, y), path = queue.pop(0)
            
            # Check if we reached any goal
            if (x, y) in goals:
                return path + [(x, y)]
            
            # Check all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < game_map.size and 0 <= ny < game_map.size and 
                    game_map.grid[nx][ny] == 0 and (nx, ny) not in visited):
                    queue.append(((nx, ny), path + [(x, y)]))
                    visited.add((nx, ny))
        
        # No path found
        return []
        
    def train_ai_offline(self, num_episodes=1000, maps_variation=10):
        """Train AI through multiple episodes with varying maps."""
        print("Khởi tạo AI Agent cho huấn luyện...")
        ai_agent = AdaptiveAI(self.prolog)
        
        # Đặt các giá trị khởi tạo
        ai_agent.exploration_rate = 0.5  # Tăng tỷ lệ thăm dò trong training
        
        print(f"Bắt đầu huấn luyện với {num_episodes} tập...")
        success_count = 0
        capture_count = 0
        
        for episode in range(num_episodes):
            start_time = time.time()
            
            # Tạo bản đồ mới định kỳ
            if episode % 100 == 0:
                print(f"Tập {episode}/{num_episodes}: Tạo bản đồ mới...")
                game_map = self.generate_random_map(variation=maps_variation)
                
            # Đặt camera ngẫu nhiên
            if episode % 10 == 0:
                cameras = self.generate_random_camera_placement(game_map)
                
            # Chạy mô phỏng
            result = self.run_simulation(ai_agent, game_map)
            
            # Cập nhật thống kê
            if result["escaped"]:
                success_count += 1
                print(f"Tập {episode}: AI thoát thành công sau {result['steps']} bước!")
            elif result["captured"]:
                capture_count += 1
                
            # Điều chỉnh tỷ lệ thăm dò theo thời gian
            ai_agent.exploration_rate = max(0.1, 0.5 - (episode / num_episodes) * 0.4)
            
            # Lưu dữ liệu định kỳ
            if episode % 50 == 0 or episode == num_episodes - 1:
                ai_agent.save_learning_data(f"data/ai_learning/training_episode_{episode}.json")
                print(f"Đã lưu dữ liệu huấn luyện tại tập {episode}")
                print(f"Tỷ lệ thành công hiện tại: {success_count/(episode+1)*100:.2f}%")
                print(f"Tỷ lệ bị bắt: {capture_count/(episode+1)*100:.2f}%")
            
            # Thông tin huấn luyện
            if episode % 10 == 0:
                elapsed = time.time() - start_time
                print(f"Tập {episode}: hoàn thành trong {elapsed:.2f}s")
        
        # Tối ưu hóa Q-table cuối cùng
        ai_agent.optimize_q_table()
        
        # Lưu mô hình cuối cùng
        ai_agent.save_learning_data("data/ai_learning/pretrained_model.json")
        print("Huấn luyện hoàn tất!")
        print(f"Tỷ lệ thành công: {success_count/num_episodes*100:.2f}%")
        print(f"Tỷ lệ bị bắt: {capture_count/num_episodes*100:.2f}%")
