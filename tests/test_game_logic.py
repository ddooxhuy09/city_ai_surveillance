"""
Tests for game logic functionality.
"""
import unittest
from unittest.mock import MagicMock
from src.game.game_state import GameState

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        # Mock Prolog interface
        self.mock_prolog = MagicMock()
        
        # Mock city map
        self.city_map = {
            "city_center": (100, 100),
            "industrial_zone": (300, 100),
            "residential_area": (100, 300),
            "connections": [
                ("city_center", "industrial_zone"),
                ("city_center", "residential_area")
            ],
            "exit_points": ["industrial_zone"]
        }
        
        # Create game state
        self.game_state = GameState(self.mock_prolog, self.city_map)
        
        # Initialize with AI position
        self.game_state.update_ai_position("city_center")
    
    def test_place_camera(self):
        """Test placing a camera."""
        # Place a camera
        self.game_state.place_camera("industrial_zone", 3)
        
        # Check if camera was added
        self.assertEqual(len(self.game_state.cameras), 1)
        self.assertEqual(self.game_state.cameras[0]["location"], "industrial_zone")
        self.assertEqual(self.game_state.cameras[0]["range"], 3)
        
        # Check if Prolog was updated
        self.mock_prolog.assertz.assert_called_with("camera(1, industrial_zone, 3)")
    
    def test_check_camera(self):
        """Test checking a camera."""
        # Add a camera
        self.game_state.cameras.append({
            "id": 1,
            "location": "industrial_zone",
            "range": 3,
            "time_placed": 0
        })
        
        # Mock camera detection query
        self.mock_prolog.query.return_value = iter([{"X": True}])  # Camera detects AI
        
        # Check camera
        result = self.game_state.check_camera(1)
        
        # Verify result
        self.assertTrue(result["detects_ai"])
        
        # Verify Prolog query
        self.mock_prolog.query.assert_called_with("camera_coverage(1, city_center)")
    
    def test_create_false_alert(self):
        """Test creating a false alert."""
        # Create a false alert
        self.game_state.create_false_alert("residential_area")
        
        # Check if decoy was added
        self.assertEqual(len(self.game_state.decoy_signals), 1)
        self.assertEqual(self.game_state.decoy_signals[0]["location"], "residential_area")
        
        # Check if Prolog was updated
        self.mock_prolog.assertz.assert_called_with(f"decoy_signal(residential_area, {self.game_state.decoy_signals[0]['strength']})")
    
    def test_game_over_conditions(self):
        """Test game over conditions."""
        # Game should not be over initially
        self.assertFalse(self.game_state.is_game_over())
        
        # Set game over
        self.game_state.set_game_over("ai_win")
        
        # Game should be over now
        self.assertTrue(self.game_state.is_game_over())
        self.assertEqual(self.game_state.get_game_result(), "ai_win")
