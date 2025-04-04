""" Base AI Agent class that handles state management and basic AI functionality. """
from abc import ABC, abstractmethod
import random
import pickle
import os

class AIAgent(ABC):
    def __init__(self, prolog_interface):
        """Initialize the AI agent with a Prolog interface."""
        self.prolog = prolog_interface
        self.state = self._get_current_state()

    def _get_current_state(self):
        """Get the current state from Prolog."""
        try:
            query = "ai_state(position, Pos), ai_state(detected, Status)"
            result = list(self.prolog.query(query))
            return (result[0]["Pos"], result[0]["Status"]) if result else ("city_center", "undetected")
        except Exception as e:
            print(f"Lỗi khi lấy trạng thái hiện tại: {e}")
            return ("city_center", "undetected")

    @abstractmethod
    def choose_action(self):
        """Choose an action based on the current state."""
        pass

    def move_to(self, location):
        """Move the AI to a new location."""
        try:
            # Remove old position
            list(self.prolog.query("retract(ai_state(position, _))"))

            # Update new position
            self.prolog.assertz(f"ai_state(position, {location})")

            # Check if AI is detected
            is_detected = self.check_if_detected(location)

            # Update detection state
            list(self.prolog.query("retract(ai_state(detected, _))"))
            if is_detected:
                self.prolog.assertz("ai_state(detected, detected)")
            else:
                self.prolog.assertz("ai_state(detected, undetected)")

            # Update current state
            self.state = self._get_current_state()
        except Exception as e:
            print(f"Lỗi khi di chuyển AI: {e}")

    def check_if_detected(self, location):
        """Check if the AI is detected at the given location."""
        try:
            detected = list(self.prolog.query(f"camera_coverage(_, {location})"))
            return len(detected) > 0
        except Exception as e:
            print(f"Lỗi khi kiểm tra phát hiện: {e}")
            return False

    def save_state(self, filename):
        """Save the AI state to a file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'wb') as f:
                pickle.dump(self.state, f)
        except Exception as e:
            print(f"Lỗi khi lưu trạng thái: {e}")

    def load_state(self, filename):
        """Load the AI state from a file."""
        try:
            with open(filename, 'rb') as f:
                self.state = pickle.load(f)
        except FileNotFoundError:
            print(f"File trạng thái {filename} không tìm thấy.")
        except Exception as e:
            print(f"Lỗi khi tải trạng thái: {e}")
