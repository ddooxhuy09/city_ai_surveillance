"""
Reinforcement Learning implementation for the AI agent.
"""
import random
import os
import json
from src.ai.ai_agent import AIAgent

class RLAgent(AIAgent):
    def __init__(self, prolog_interface):
        """Initialize the Reinforcement Learning agent."""
        super().__init__(prolog_interface)
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.2
        self.q_table = self._initialize_q_table()
        
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
        """Choose an action using epsilon-greedy policy."""
        try:
            state_str = str(self.state)
            if state_str not in self.q_table:
                # Initialize state if not exists
                self.q_table[state_str] = self._initialize_action_values(self.state[0])
            
            if random.random() < self.exploration_rate:
                # Exploration: choose randomly
                return random.choice(list(self.q_table[state_str].keys()))
            else:
                # Exploitation: choose best action
                return max(self.q_table[state_str], key=self.q_table[state_str].get)
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
            
            # Save Q-table periodically
            if random.random() < 0.1:  # 10% chance to save
                self.save_q_table()
        except Exception as e:
            print(f"Lỗi khi cập nhật giá trị Q: {e}")
    
    def save_q_table(self):
        """Save the Q-table to a file."""
        try:
            # Ensure directory exists
            os.makedirs("data/ai_learning", exist_ok=True)
            
            with open("data/ai_learning/q_table.json", 'w') as f:
                json.dump(self.q_table, f, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu Q-table: {e}")
