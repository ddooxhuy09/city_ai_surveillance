"""
Logging utility for game events and debugging.
"""
import logging
import os
import time

class GameLogger:
    def __init__(self, log_level=logging.INFO, log_dir="logs"):
        """Initialize the game logger."""
        self.log_dir = log_dir
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("CityAI")
        self.logger.setLevel(log_level)
        
        # Remove existing handlers if any
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create file handler
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"city_ai_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set formatter for handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("Logger initialized")
    
    def log_game_event(self, event_type, details):
        """Log a game event."""
        self.logger.info(f"GAME EVENT - {event_type}: {details}")
    
    def log_ai_action(self, action, details):
        """Log an AI action."""
        self.logger.info(f"AI ACTION - {action}: {details}")
    
    def log_player_action(self, action, details):
        """Log a player action."""
        self.logger.info(f"PLAYER ACTION - {action}: {details}")
    
    def log_error(self, error_message, exception=None):
        """Log an error."""
        if exception:
            self.logger.error(f"{error_message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(error_message)
    
    def log_prolog_query(self, query, result):
        """Log a Prolog query and its result."""
        self.logger.debug(f"PROLOG QUERY: {query}")
        self.logger.debug(f"PROLOG RESULT: {result}")
