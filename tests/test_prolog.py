"""
Tests for Prolog interface functionality.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
from src.prolog_interface.prolog_connector import PrologConnector

class TestPrologInterface(unittest.TestCase):
    @patch('pyswip.Prolog')
    def setUp(self, mock_prolog_class):
        # Setup mock Prolog class
        self.mock_prolog = mock_prolog_class.return_value
        
        # Create PrologConnector with mock
        self.prolog_connector = PrologConnector()
    
    @patch('os.path.join')
    def test_load_knowledge_base(self, mock_join):
        """Test loading knowledge base."""
        # Setup path mocking
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Mock consult method
        self.prolog_connector.consult = MagicMock()
        
        # Call method
        self.prolog_connector.load_knowledge_base()
        
        # Verify consults
        self.prolog_connector.consult.assert_any_call("prolog/kb_city.pl")
        self.prolog_connector.consult.assert_any_call("prolog/kb_surveillance.pl")
        self.prolog_connector.consult.assert_any_call("prolog/kb_ai_behavior.pl")
        self.prolog_connector.consult.assert_any_call("prolog/kb_rules.pl")
        
        # Verify assertz calls
        self.mock_prolog.assertz.assert_any_call("ai_state(position, city_center)")
        self.mock_prolog.assertz.assert_any_call("ai_state(detected, undetected)")
        self.mock_prolog.assertz.assert_any_call("ai_state(known_cameras, [])")
        self.mock_prolog.assertz.assert_any_call("ai_state(escape_plan, [])")
    
    def test_query(self):
        """Test Prolog query."""
        # Setup mock query response
        mock_response = [{"X": "value"}]
        self.mock_prolog.query.return_value = mock_response
        
        # Call query
        result = self.prolog_connector.query("test_query(X)")
        
        # Verify query was called with correct params
        self.mock_prolog.query.assert_called_with("test_query(X)")
        
        # Verify result
        self.assertEqual(result, mock_response)
    
    def test_assertz_and_retract(self):
        """Test assertz and retract."""
        # Call assertz
        self.prolog_connector.assertz("test_fact(value)")
        
        # Verify assertz
        self.mock_prolog.assertz.assert_called_with("test_fact(value)")
        
        # Call retract
        self.prolog_connector.retract("test_fact(value)")
        
        # Verify retract
        self.mock_prolog.retract.assert_called_with("test_fact(value)")
