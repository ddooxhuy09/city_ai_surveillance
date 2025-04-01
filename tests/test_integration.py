"""
Integration tests to verify components work together correctly.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import pygame
from src.game.game_engine import GameEngine
from src.game.game_state import GameState
from src.ai.adaptive_ai import AdaptiveAI
from src.prolog_interface.prolog_connector import PrologConnector

@patch('pygame.init')
@patch('pygame.display.set_mode')
class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Mock config
        self.config = {
            "screen_width": 800,
            "screen_height": 600,
            "ai_turn_interval": 1000
        }
        
        # Skip actual rendering in tests
        pygame.display.flip = MagicMock()
    
    @patch('src.prolog_interface.prolog_connector.PrologConnector')
    @patch('src.game.city_generator.CityGenerator')
    @patch('src.game.game_state.GameState')
    @patch('src.game.ui_manager.UIManager')
    @patch('src.ai.adaptive_ai.AdaptiveAI')
    def test_game_engine_initialization(self, mock_ai, mock_ui, mock_state, 
                                        mock_city, mock_prolog, *args):
        """Test game engine initialization."""
        # Setup mocks
        mock_prolog_instance = mock_prolog.return_value
        mock_city_instance = mock_city.return_value
        mock_city_instance.generate_city.return_value = {"city_center": (100, 100)}
        
        # Create game engine
        game_engine = GameEngine(self.config)
        
        # Verify components initialized
        self.assertIsNotNone(game_engine.prolog)
        self.assertIsNotNone(game_engine.city_generator)
        self.assertIsNotNone(game_engine.city_map)
        self.assertIsNotNone(game_engine.game_state)
        self.assertIsNotNone(game_engine.ui_manager)
        self.assertIsNotNone(game_engine.ai)
    
    @patch('src.prolog_interface.prolog_connector.PrologConnector')
    def test_ai_interaction_with_game_state(self, mock_prolog, *args):
        """Test AI interaction with game state."""
        # Setup mock prolog
        mock_prolog_instance = mock_prolog.return_value
        mock_prolog_instance.query.return_value = iter([{"Pos": "city_center", "Status": "undetected"}])
        
        # Create components
        city_map = {
            "city_center": (100, 100),
            "industrial_zone": (300, 100),
            "connections": [("city_center", "industrial_zone")],
            "exit_points": ["industrial_zone"]
        }
        
        game_state = GameState(mock_prolog_instance, city_map)
        ai = AdaptiveAI(mock_prolog_instance)
        
        # Initialize AI position in game state
        game_state.update_ai_position("city_center")
        
        # Mock AI's move
        ai.move_to = MagicMock()
        ai.move_to.side_effect = lambda loc: game_state.update_ai_position(loc)
        
        # Test AI movement affecting game state
        ai.move_to("industrial_zone")
        
        # Verify game state was updated
        self.assertEqual(game_state.ai_position, "industrial_zone")
