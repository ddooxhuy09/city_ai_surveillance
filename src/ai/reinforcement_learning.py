""" Reinforcement Learning implementation for the AI agent. """
import random
import os
import json
from collections import deque
from src.ai.ai_agent import AIAgent

class RLAgent(AIAgent):
    def __init__(self, prolog_interface):
        """Initialize the Reinforcement Learning agent."""
        super().__init__(prolog_interface)
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.2
        self.q_table = self._initialize_q_table()
        self.recent_actions = deque(maxlen=10)  # Lưu 10 hành động gần nhất
        self.recent_failures = set()  # Lưu các hành động thất bại gần đây

    def _initialize_q_table(self):
        """Initialize the Q-table for reinforcement learning."""
        q_table = {}

        try:
            # Try to load from file if exists
            if os.path.exists("data/ai_learning/q_table.json"):
                with open("data/ai_learning/q_table.json", 'r') as f:
                    q_table = json.load(f)
                return q_table
        except Exception as e:
            print(f"Lỗi khi tải Q-table: {e}")

        try:
            # Get all locations from Prolog
            locations = list(self.prolog.query("location(X)"))
            for loc in locations:
                location = loc["X"]
                for detection in ["detected", "undetected"]:
                    state = (location, detection)
                    q_table[str(state)] = self._initialize_action_values(location)
            return q_table
        except Exception as e:
            print(f"Lỗi khi khởi tạo Q-table: {e}")
            # Return a default Q-table with minimal values
            return {
                "('city_center', 'undetected')": {
                    "industrial_zone": 0.0,
                    "residential_area": 0.0,
                    "create_decoy": 0.0
                }
            }

    def _initialize_action_values(self, location):
        """Initialize action values for a specific location."""
        actions = {}
        try:
            # Get all possible paths from current location
            connections = list(self.prolog.query(f"connected({location}, X)"))
            for conn in connections:
                actions[conn["X"]] = 0.0

            # Add decoy action if possible
            can_create = list(self.prolog.query(f"can_create_decoy({location})"))
            if can_create:
                actions["create_decoy"] = 0.0
        except Exception as e:
            print(f"Lỗi khi khởi tạo giá trị hành động: {e}")

        return actions

    def choose_action(self):
        """Choose an action using epsilon-greedy policy with Prolog integration."""
        try:
            state_str = str(self.state)
            
            # 1. Kiểm tra Prolog cho các quy tắc logic cấp cao
            prolog_suggestions = list(self.prolog.query(
                f"suggest_action({self.state[0]}, {self.state[1]}, Action, Confidence)"
            ))
            
            high_confidence_actions = []
            for action in prolog_suggestions:
                if "Action" in action and "Confidence" in action:
                    if action["Confidence"] > 0.8:
                        high_confidence_actions.append(action["Action"])
            
            # Sử dụng đề xuất Prolog với xác suất cao
            if high_confidence_actions and random.random() < 0.7:
                action = random.choice(high_confidence_actions)
                self.recent_actions.append(action)
                return action
                
            # Kiểm tra nếu trạng thái chưa có trong Q-table
            if state_str not in self.q_table:
                self.q_table[state_str] = self._initialize_action_values(self.state[0])

            # Lọc bỏ các hành động thất bại gần đây (nếu còn lựa chọn khác)
            available_actions = list(self.q_table[state_str].keys())
            filtered_actions = [a for a in available_actions if a not in self.recent_failures]
            
            # Nếu không còn hành động nào sau khi lọc, sử dụng tất cả hành động
            if not filtered_actions:
                filtered_actions = available_actions

            if random.random() < self.exploration_rate:
                # Thăm dò: chọn ngẫu nhiên từ các hành động đã lọc
                action = random.choice(filtered_actions)
            else:
                # Khai thác: chọn hành động tốt nhất từ các hành động đã lọc
                action = max(filtered_actions, key=lambda a: self.q_table[state_str][a])
            
            self.recent_actions.append(action)
            return action
        except Exception as e:
            print(f"Lỗi khi chọn hành động: {e}")
            # Return a default action
            return "industrial_zone"

    def update_q_value(self, state, action, reward, next_state):
        """Update Q-value for a state-action pair."""
        try:
            state_str = str(state)
            next_state_str = str(next_state)

            if state_str not in self.q_table:
                self.q_table[state_str] = self._initialize_action_values(state[0])

            if next_state_str not in self.q_table:
                self.q_table[next_state_str] = self._initialize_action_values(next_state[0])

            if action not in self.q_table[state_str]:
                self.q_table[state_str][action] = 0.0

            current_q = self.q_table[state_str][action]
            max_next_q = max(self.q_table[next_state_str].values()) if self.q_table[next_state_str] else 0

            # Q-learning formula
            new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
            self.q_table[state_str][action] = new_q

            # Ghi nhận hành động thất bại để tránh lặp lại
            if reward < -2.0:  # Phạt nặng cho hành động bị phát hiện
                self.recent_failures.add(action)
            # Xóa khỏi danh sách thất bại nếu thành công
            elif reward > 0 and action in self.recent_failures:
                self.recent_failures.remove(action)

            # Save Q-table periodically
            if random.random() < 0.1:  # 10% chance to save
                self.save_q_table()
        except Exception as e:
            print(f"Lỗi khi cập nhật giá trị Q: {e}")

    def optimize_q_table(self):
        """Tối ưu hóa bảng Q bằng cách loại bỏ giá trị không quan trọng"""
        pruned_q_table = {}
        
        for state, actions in self.q_table.items():
            # Chỉ giữ lại hành động có giá trị cao nhất và vài hành động có tiềm năng
            max_value = max(actions.values()) if actions else 0
            significant_actions = {
                action: value for action, value in actions.items()
                if value >= max_value * 0.5 or value > 1.0
            }
            
            if significant_actions:
                pruned_q_table[state] = significant_actions
        
        # Thay thế bảng Q với phiên bản đã tối ưu
        self.q_table = pruned_q_table

    def save_q_table(self):
        """Save the Q-table to a file."""
        try:
            # Ensure directory exists
            os.makedirs("data/ai_learning", exist_ok=True)

            with open("data/ai_learning/q_table.json", 'w') as f:
                json.dump(self.q_table, f, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu Q-table: {e}")
