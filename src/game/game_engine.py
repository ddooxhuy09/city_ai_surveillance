"""
Main game engine that manages game loop and integration of components.
"""
import pygame
import sys
import time
import os
from src.game.game_state import GameState
from src.game.city_generator import CityGenerator
from src.game.ui_manager import UIManager
from src.ai.adaptive_ai import AdaptiveAI
from src.prolog_interface.prolog_connector import PrologConnector

class GameEngine:
    def __init__(self, config):
        """Initialize the game engine with configuration."""
        self.config = config
        pygame.init()
        
        # Setup display
        self.screen_width = config.get("screen_width", 1024)
        self.screen_height = config.get("screen_height", 768)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Giám Sát Thành Phố AI")
        
        # Initialize components
        use_mock_prolog = config.get("use_mock_prolog", False)
        self.prolog = PrologConnector(use_mock_prolog)
        self.prolog.load_knowledge_base()
        
        self.city_generator = CityGenerator(self.prolog, config)
        self.city_map = self.city_generator.generate_city()
        
        self.game_state = GameState(self.prolog, self.city_map)
        self.ui_manager = UIManager(self.screen, self.city_map, self.game_state)
        
        self.ai = AdaptiveAI(self.prolog)
        
        # Game variables
        self.clock = pygame.time.Clock()
        self.running = True
        self.ai_turn_timer = 0
        self.ai_turn_interval = config.get("ai_turn_interval", 5000)  # ms
        
        # Ensure data directories exist
        os.makedirs("data/ai_learning", exist_ok=True)
        os.makedirs("data/game_config", exist_ok=True)
        os.makedirs("data/saved_games", exist_ok=True)
        
    def run(self):
        """Run the main game loop."""
        try:
            while self.running:
                dt = self.clock.tick(60)  # 60 FPS
                
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.ui_manager.handle_event(event)
                
                # Update game state
                self.update(dt)
                
                # Render
                self.render()
                
                # Check game over conditions
                if self.game_state.is_game_over():
                    self.handle_game_over()
            
            pygame.quit()
        except Exception as e:
            print(f"Lỗi trong vòng lặp game: {e}")
            import traceback
            traceback.print_exc()
            pygame.quit()
            sys.exit(1)
    
    def update(self, dt):
        """Update game state."""
        self.game_state.update(dt)
        
        # AI turn logic
        self.ai_turn_timer += dt
        if self.ai_turn_timer >= self.ai_turn_interval:
            self.ai_turn_timer = 0
            self.handle_ai_turn()
        
        # Update UI
        self.ui_manager.update(dt)
    
    def render(self):
        """Render the game to the screen."""
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Render UI elements
        self.ui_manager.render()
        
        # Flip the display
        pygame.display.flip()
    
    def handle_ai_turn(self):
        """Handle the AI's turn."""
        try:
            # Update AI game time
            self.ai.game_time += self.ai_turn_interval / 1000  # Convert ms to seconds
            
            # Analyze player actions
            self.ai.analyze_player_patterns(self.game_state.player_actions)
            
            # Choose and execute AI action
            action = self.ai.choose_action()
            
            if action == "create_decoy":
                # Create false signal
                decoy_strategy = self.ai.generate_deception_strategy()
                if decoy_strategy:
                    decoy_location = decoy_strategy["location"]
                    self.game_state.create_false_alert(decoy_location)
                    self.game_state.ai_score += 2
            else:
                # Move to new location
                old_position = self.ai.state[0]
                self.ai.move_to(action)
                
                # Check if AI is detected
                new_state = self.ai._get_current_state()
                if new_state[1] == "detected":
                    # AI is detected
                    self.game_state.player_score += 1
                    # Find camera that detected AI
                    
                    # For mock Prolog, use a simple approach
                    if self.prolog.use_mock:
                        for camera in self.game_state.cameras:
                            self.ai.learn_from_detection(camera["id"], action)
                    else:
                        # For real Prolog
                        detecting_camera_query = f"camera(ID, _, _), camera_coverage(ID, {action})"
                        detecting_cameras = list(self.prolog.query(detecting_camera_query))
                        if detecting_cameras:
                            camera_id = detecting_cameras[0]["ID"]
                            self.ai.learn_from_detection(camera_id, action)
                
                # Check if AI has reached an exit point
                if self.prolog.use_mock:
                    # For mock Prolog
                    exit_check = action in self.city_map.get("exit_points", [])
                else:
                    # For real Prolog
                    exit_check = list(self.prolog.query(f"exit_point({action})"))
                
                if exit_check:
                    if new_state[1] == "undetected":
                        # AI escaped successfully
                        self.game_state.set_game_over("ai_win")
                        self.game_state.ai_score += 10
                    else:
                        # AI caught at exit point
                        self.game_state.set_game_over("player_win")
                        self.game_state.player_score += 5
            
            # Update game state with AI's new position
            self.game_state.update_ai_position(self.ai.state[0])
        except Exception as e:
            print(f"Lỗi trong lượt của AI: {e}")
    
    def handle_game_over(self):
        """Handle game over condition."""
        try:
            result = self.game_state.get_game_result()
            
            # Save AI learning data
            self.ai.save_learning_data("data/ai_learning/learning_data.json")
            
            # Display game over screen
            self.ui_manager.show_game_over(result)
            
            # Wait for player input
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        waiting = False
            
            # Reset or exit based on player choice
            self.reset_game()
        except Exception as e:
            print(f"Lỗi khi xử lý game over: {e}")
    
    def reset_game(self):
        """Reset the game to initial state."""
        try:
            # Regenerate city
            self.city_map = self.city_generator.generate_city()
            
            # Reset game state
            self.game_state = GameState(self.prolog, self.city_map)
            
            # Reset UI
            self.ui_manager = UIManager(self.screen, self.city_map, self.game_state)
            
            # Reset AI (but maintain learning)
            self.prolog.reset_ai_state()
            self.ai = AdaptiveAI(self.prolog)
            
            # Reset timers
            self.ai_turn_timer = 0
        except Exception as e:
            print(f"Lỗi khi khởi tạo lại trò chơi: {e}")
