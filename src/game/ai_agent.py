import pygame
import numpy as np
from collections import deque
from src.utils.gif_loader import AnimatedSprite
import os

class AIAgent:
    """AI agent that uses BFS to find paths and avoid camera detection."""
    
    def __init__(self, game_map, config):
        self.game_map = game_map
        self.config = config
        self.cell_size = config["cell_size"]
        self.pos = game_map.start_pos if game_map.start_pos else (1, 1)
        self.path = []
        self.path_index = 0
        self.is_moving = False
        self.speed = 5  # Cells per second
        self.move_progress = 0
        self.captured = False
        self.escaped = False
        
        # Load animated sprite for the agent
        gif_url = "https://piskel-imgstore-b.appspot.com/img/55430b28-0ea0-11f0-b38e-bfefe72123d5.gif"
        # Reduce size to 10 times (instead of 50 times)
        sprite_size = (10 * (self.cell_size - 4), 3 * (self.cell_size - 4))
        self.sprite = self._load_agent_sprite(gif_url, sprite_size)
        
        # For debugging
        print(f"Loaded sprite frames: {len(self.sprite.frames) if self.sprite else 0}")
        print(f"AI agent sprite size: {sprite_size}")
    
    def _load_agent_sprite(self, url, size):
        """Load the agent sprite from URL or local cache"""
        try:
            # Create a local cache directory if it doesn't exist
            cache_dir = os.path.join(os.getcwd(), "assets", "sprites")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Local cache file path
            cache_file = os.path.join(cache_dir, "agent_sprite.gif")
            print(f"Loading sprite from: {cache_file if os.path.exists(cache_file) else url}")
            
            # Try to load from cache first, if not available download from URL
            if os.path.exists(cache_file):
                sprite = AnimatedSprite.from_file(cache_file, size)
            else:
                sprite = AnimatedSprite.from_url(url, size, save_path=cache_file)
                print(f"Downloaded sprite to: {cache_file}")
            
            # If sprite loading failed, create a fallback sprite
            if not sprite.frames:
                print("Sprite loading failed, creating fallback")
                # Create a single frame as fallback
                surf = pygame.Surface(size, pygame.SRCALPHA)
                surf.fill(self.config["colors"]["ai"])
                sprite = AnimatedSprite(frames=[surf], durations=[100])
            
            return sprite
        except Exception as e:
            print(f"Error loading sprite: {e}")
            # Create fallback sprite
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill(self.config["colors"]["ai"])
            return AnimatedSprite(frames=[surf], durations=[100])
    
    def start_movement(self):
        """Start the AI movement by calculating a path."""
        self.is_moving = True
        self.captured = False
        self.escaped = False
        self.path_index = 0
        self.move_progress = 0
        self.path = self.find_path_bfs()
    
    def stop_movement(self):
        """Stop the AI movement."""
        self.is_moving = False
    
    def reset(self):
        """Reset the AI to the start position."""
        self.pos = self.game_map.start_pos if self.game_map.start_pos else (1, 1)
        self.path = []
        self.path_index = 0
        self.is_moving = False
        self.move_progress = 0
        self.captured = False
        self.escaped = False
    
    def update(self, dt):
        """Update the AI position based on the path."""
        if not self.is_moving or self.captured or self.escaped:
            return
        
        # Update sprite animation
        self.sprite.update(dt)
        
        if not self.path:
            self.is_moving = False
            return
        
        # Check if captured by a camera
        for camera in self.game_map.cameras:
            if camera.can_see(self.pos[0], self.pos[1], self.game_map):
                self.captured = True
                self.is_moving = False
                return
        
        # Check if reached an exit
        if self.pos in self.game_map.end_positions:
            self.escaped = True
            self.is_moving = False
            return
        
        # Move along the path
        if self.path_index < len(self.path):
            # Calculate how much to move
            self.move_progress += self.speed * dt
            
            if self.move_progress >= 1:
                # Move to the next cell
                self.move_progress = 0
                self.pos = self.path[self.path_index]
                self.path_index += 1
    
    def find_path_bfs(self):
        """Find a path from current position to any exit using BFS."""
        if not self.game_map.end_positions:
            print("No exit positions found")
            return []
        
        # Create a grid to mark visited cells
        visited = set()
        queue = deque([(self.pos, [])])  # (position, path_so_far)
        visited.add(self.pos)
        
        while queue:
            (x, y), path = queue.popleft()
            current_path = path + [(x, y)]
            
            # Check if reached an exit
            if (x, y) in self.game_map.end_positions:
                print(f"Path found with length {len(current_path)}")
                return current_path
            
            # Check all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                new_pos = (nx, ny)
                
                if (0 <= nx < self.game_map.size and 
                    0 <= ny < self.game_map.size and 
                    self.game_map.grid[nx][ny] == 0 and 
                    new_pos not in visited):
                    
                    # Check if the new position is visible by any camera
                    visible_to_camera = False
                    for camera in self.game_map.cameras:
                        if camera.can_see(nx, ny, self.game_map):
                            visible_to_camera = True
                            break
                    
                    if not visible_to_camera:
                        queue.append((new_pos, current_path))
                        visited.add(new_pos)
        
        print("No path found")
        return []  # No path found
    
    def render(self, screen):
        """Render the AI agent on the screen."""
        colors = self.config["colors"]
        
        # Draw AI agent as an animated sprite
        x, y = self.pos
        
        # Calculate position to center the large sprite on the cell
        sprite_width = 10 * (self.cell_size - 4)  # 10x instead of 50x
        sprite_height = 10 * (self.cell_size - 4)  # 10x instead of 50x
        
        # Center the sprite at the cell position
        screen_x = y * self.cell_size - (sprite_width - self.cell_size) / 2
        screen_y = x * self.cell_size - (sprite_height - self.cell_size) / 2
        
        # Get current frame from the animated sprite
        current_frame = self.sprite.get_current_frame()
        if current_frame:
            screen.blit(current_frame, (screen_x, screen_y))
        else:
            # Fallback to colored rectangle if sprite is not available
            rect = pygame.Rect(
                y * self.cell_size + self.cell_size // 4, 
                x * self.cell_size + self.cell_size // 4, 
                self.cell_size // 2, 
                self.cell_size // 2
            )
            pygame.draw.rect(screen, colors["ai"], rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Add border for better visibility
