"""
Tests for AI functionality.
"""
import unittest
from unittest.mock import MagicMock, patch
from src.ai.adaptive_ai import AdaptiveAI

class TestAI(unittest.TestCase):
    def setUp(self):
        # Mock Prolog interface
        self.mock_prolog = MagicMock()
        
        # Setup mock query responses
        self.mock_prolog.query.return_value = iter([{"Pos": "city_center", "Status": "undetected"}])
        
        # Create AI instance with mock
        self.ai = AdaptiveAI(self.mock_prolog)
    
    def test_ai_initialization(self):
        """Test AI initialization."""
        self.assertEqual(self.ai.state[0], "city_center")
        self.assertEqual(self.ai.state[1], "undetected")
    
    def test_choose_action(self):
        """Test AI action choice."""
        # Mock q_table for testing
        self.ai.q_table = {
            ("city_center", "undetected"): {
                "industrial_zone": 10.0,
                "residential_area": 5.0,
                "create_decoy": 2.0
            }
        }
        
        # Force exploitation
        self.ai.exploration_rate = 0
        
        # AI should choose industrial_zone (highest Q-value)
        action = self.ai.choose_action()
        self.assertEqual(action, "industrial_zone")
    
    def test_move_to(self):
        """Test AI movement."""
        # Setup mock for detection check
        self.mock_prolog.query.side_effect = [
            iter([]),  # retract position
            iter([]),  # assertz new position
            iter([{"X": "camera1"}]),  # AI is detected by camera
            iter([]),  # retract detection status
            iter([]),  # assertz detected
            iter([{"Pos": "industrial_zone", "Status": "detected"}])  # get current state
        ]
        
        # Move AI
        self.ai.move_to("industrial_zone")
        
        # Check new state
        self.assertEqual(self.ai.state[0], "industrial_zone")
        self.assertEqual(self.ai.state[1], "detected")
        
        # Verify Prolog interactions
        self.mock_prolog.assertz.assert_any_call("ai_state(position, industrial_zone)")
        self.mock_prolog.assertz.assert_any_call("ai_state(detected, detected)")
    
    def test_update_q_value(self):
        """Test Q-value updates."""
        # Setup Q-table with initial values
        self.ai.q_table = {
            ("city_center", "undetected"): {"industrial_zone": 5.0},
            ("industrial_zone", "detected"): {"shopping_mall": 2.0}
        }
        
        # Update Q-value with positive reward
        self.ai.update_q_value(
            ("city_center", "undetected"), 
            "industrial_zone", 
            10.0, 
            ("industrial_zone", "detected")
        )
        
        # Check updated Q-value
        new_q = self.ai.q_table[("city_center", "undetected")]["industrial_zone"]
        self.assertGreater(new_q, 5.0)
