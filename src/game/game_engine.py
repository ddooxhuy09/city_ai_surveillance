"""
Main game engine that manages game loop and integration of components.
"""
import pygame
import sys
import time
import os
from src.game.map import GameMap
from src.game.ai_agent import AIAgent

class Button:
    """Simple button class for UI elements."""
    
    def __init__(self, rect, text, color, hover_color, action):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.hovered = False
        
    def render(self, screen, font):
        """Render the button on the screen."""
        # Draw button background
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # Border
        
        # Draw text
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events for the button."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.action()
                return True
        return False


class GameEngine:
    """Main game engine class that manages the game state and rendering."""
    
    def __init__(self, config):
        self.config = config
        self.screen_width = config.get("screen_width", 800)
        self.screen_height = config.get("screen_height", 600)
        self.cell_size = config.get("cell_size", 30)
        self.map_size = config.get("map_size", 20)
        
        # Adjust screen size based on map size
        self.screen_width = max(self.screen_width, self.map_size * self.cell_size + 200)
        self.screen_height = max(self.screen_height, self.map_size * self.cell_size + 100)
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("City AI Surveillance")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        # Game state
        self.game_map = GameMap(config)
        self.ai_agent = AIAgent(self.game_map, config)
        self.create_ui()
        
        self.state = "placing_cameras"  # States: placing_cameras, simulation
        self.simulation_result = None  # None, "captured", or "escaped"
    
    def create_ui(self):
        """Create UI elements like buttons."""
        button_width = 120
        button_height = 40
        margin = 20
        
        # Create buttons
        self.buttons = []
        
        # Start button
        start_rect = pygame.Rect(
            self.map_size * self.cell_size + margin,
            margin,
            button_width,
            button_height
        )
        start_button = Button(
            start_rect,
            "Start",
            (100, 200, 100),  # Green
            (150, 250, 150),  # Light green on hover
            self.start_simulation
        )
        self.buttons.append(start_button)
        
        # Reset button
        reset_rect = pygame.Rect(
            self.map_size * self.cell_size + margin,
            margin * 2 + button_height,
            button_width,
            button_height
        )
        reset_button = Button(
            reset_rect,
            "Reset",
            (200, 100, 100),  # Red
            (250, 150, 150),  # Light red on hover
            self.reset_game
        )
        self.buttons.append(reset_button)
        
        # New Map button
        new_map_rect = pygame.Rect(
            self.map_size * self.cell_size + margin,
            margin * 3 + button_height * 2,
            button_width,
            button_height
        )
        new_map_button = Button(
            new_map_rect,
            "New Map",
            (100, 100, 200),  # Blue
            (150, 150, 250),  # Light blue on hover
            self.generate_new_map
        )
        self.buttons.append(new_map_button)
        
        # Rotate Camera button (only visible when a camera is selected)
        rotate_rect = pygame.Rect(
            self.map_size * self.cell_size + margin,
            margin * 4 + button_height * 3,
            button_width,
            button_height
        )
        rotate_button = Button(
            rotate_rect,
            "Rotate Camera",
            (200, 200, 100),  # Yellow
            (250, 250, 150),  # Light yellow on hover
            self.rotate_selected_camera
        )
        self.buttons.append(rotate_button)
        
        # Game state variables
        self.selected_camera = None
    
    def start_simulation(self):
        """Start the AI simulation."""
        if self.state == "placing_cameras":
            self.state = "simulation"
            self.ai_agent.start_movement()
            self.simulation_result = None
    
    def reset_game(self):
        """Reset the game state."""
        self.ai_agent.reset()
        self.state = "placing_cameras"
        self.simulation_result = None
    
    def generate_new_map(self):
        """Generate a new map and reset the game."""
        self.game_map = GameMap(self.config)
        self.ai_agent = AIAgent(self.game_map, self.config)
        self.reset_game()
    
    def rotate_selected_camera(self):
        """Rotate the selected camera."""
        if self.selected_camera is not None and self.state == "placing_cameras":
            camera = self.game_map.cameras[self.selected_camera]
            camera.rotate()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle button events
            for button in self.buttons:
                if button.handle_event(event):
                    break
            
            # Handle mouse clicks on the map
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                
                # Check if click is within map bounds
                if mouse_x < self.map_size * self.cell_size and mouse_y < self.map_size * self.cell_size:
                    grid_x = mouse_y // self.cell_size
                    grid_y = mouse_x // self.cell_size
                    
                    if self.state == "placing_cameras":
                        # Place camera on barrier
                        if self.game_map.grid[grid_x][grid_y] == 1:
                            # Check if there's already a camera here
                            camera_index = None
                            for i, cam in enumerate(self.game_map.cameras):
                                if cam.x == grid_x and cam.y == grid_y:
                                    camera_index = i
                                    break
                            
                            if camera_index is not None:
                                # Select camera for rotation
                                self.selected_camera = camera_index
                            else:
                                # Place new camera
                                self.game_map.add_camera((grid_x, grid_y))
                                self.selected_camera = len(self.game_map.cameras) - 1
    
    def update(self):
        """Update game state."""
        dt = self.clock.get_time() / 1000.0  # Delta time in seconds
        
        if self.state == "simulation":
            # Add debug info
            if self.config.get("debug_mode", False):
                print(f"AI position: {self.ai_agent.pos}, Path length: {len(self.ai_agent.path)}")
                print(f"Path index: {self.ai_agent.path_index}, Is moving: {self.ai_agent.is_moving}")
            
            self.ai_agent.update(dt)
            
            # Check simulation results
            if self.ai_agent.captured:
                self.simulation_result = "captured"
                self.state = "placing_cameras"
                print("AI was captured!")
            elif self.ai_agent.escaped:
                self.simulation_result = "escaped"
                self.state = "placing_cameras"
                print("AI escaped!")
    
    def render(self):
        """Render the game state."""
        # Fill background with white
        self.screen.fill(self.config["colors"]["background"])
        
        # Render map
        self.game_map.render(self.screen)
        
        # Render AI agent
        self.ai_agent.render(self.screen)
        
        # Render UI
        for button in self.buttons:
            button.render(self.screen, self.font)
        
        # Render status text
        status_text = f"State: {self.state.capitalize()}"
        status_surf = self.font.render(status_text, True, (0, 0, 0))
        self.screen.blit(status_surf, (self.map_size * self.cell_size + 20, 120))
        
        if self.selected_camera is not None and self.state == "placing_cameras":
            camera_text = f"Selected Camera: {self.selected_camera + 1}"
            camera_surf = self.font.render(camera_text, True, (0, 0, 0))
            self.screen.blit(camera_surf, (self.map_size * self.cell_size + 20, 150))
        
        if self.simulation_result:
            result_text = f"AI was {'captured' if self.simulation_result == 'captured' else 'escaped'}!"
            result_color = (255, 0, 0) if self.simulation_result == "captured" else (0, 128, 0)
            result_surf = self.font.render(result_text, True, result_color)
            self.screen.blit(result_surf, (self.map_size * self.cell_size + 20, 180))
        
        # Draw instructions
        instructions = [
            "Instructions:",
            "1. Click on barriers to place cameras",
            "2. Select a camera and click 'Rotate Camera'",
            "3. Press 'Start' to run the simulation",
            "4. AI will try to escape using BFS",
            "5. Press 'Reset' to try again",
            "6. Press 'New Map' for a new layout"
        ]
        
        for i, line in enumerate(instructions):
            instr_surf = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(instr_surf, (self.map_size * self.cell_size + 20, 220 + i * 25))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
