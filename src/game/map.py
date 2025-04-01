import pygame
import random
import numpy as np
import math

class GameMap:
    """Class representing the game map with barriers and streets."""
    
    def __init__(self, config):
        self.config = config
        self.size = config.get("map_size", 30)  # Increased default map size to 30x30
        self.cell_size = config["cell_size"]
        self.grid = np.zeros((self.size, self.size), dtype=int)  # 0: street, 1: barrier
        self.cameras = []
        self.start_pos = None
        self.end_positions = []  # Exit positions at the edges
        self.house_svg = self._create_house_svg()  # Create house SVG rendering
        self.generate_map()
    
    def _create_house_svg(self):
        """Create a simple house icon as a pygame surface."""
        width, height = self.cell_size, self.cell_size
        
        # Create a surface for the house
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # House colors
        house_color = (70, 70, 200)
        roof_color = (200, 70, 70)
        
        # Draw house body (rectangle)
        house_rect = pygame.Rect(width * 0.2, height * 0.4, width * 0.6, height * 0.5)
        pygame.draw.rect(surface, house_color, house_rect)
        
        # Draw roof (triangle)
        roof_points = [
            (width * 0.1, height * 0.4),  # Left bottom
            (width * 0.5, height * 0.1),  # Top middle
            (width * 0.9, height * 0.4)   # Right bottom
        ]
        pygame.draw.polygon(surface, roof_color, roof_points)
        
        # Draw door
        door_rect = pygame.Rect(width * 0.4, height * 0.6, width * 0.2, height * 0.3)
        pygame.draw.rect(surface, (150, 80, 20), door_rect)
        
        # Draw window
        window_rect = pygame.Rect(width * 0.25, height * 0.45, width * 0.15, height * 0.15)
        pygame.draw.rect(surface, (200, 200, 255), window_rect)
        
        window_rect2 = pygame.Rect(width * 0.6, height * 0.45, width * 0.15, height * 0.15)
        pygame.draw.rect(surface, (200, 200, 255), window_rect2)
        
        return surface
    
    def generate_map(self):
        """Generate a complex maze-like map with multiple potential paths."""
        # Create border barriers
        for i in range(self.size):
            for j in range(self.size):
                # Create border
                if (i == 0 or i == self.size-1 or j == 0 or j == self.size-1):
                    self.grid[i][j] = 1  # Barrier
        
        # Set start position at top-left (1,1)
        self.grid[1][1] = 0  # Ensure it's a street
        self.start_pos = (1, 1)
        
        # Set exit position at bottom-right (size-2, size-2)
        self.grid[self.size-2][self.size-2] = 0  # Ensure it's a street
        self.end_positions = [(self.size-2, self.size-2)]
        
        # Create a complex maze pattern
        self._generate_complex_maze()
        
        # Ensure there's at least one valid path
        if not self.has_valid_path():
            self._create_complex_path()
    
    def _generate_complex_maze(self):
        """Generate a complex maze with multiple possible paths."""
        # Add some barriers (20% of the map) as a base to leave more open space
        barrier_count = int(0.2 * (self.size-2) * (self.size-2))
        cells = [(i, j) for i in range(2, self.size-2) for j in range(2, self.size-2)]
        random.shuffle(cells)
        
        for i, j in cells[:barrier_count]:
            self.grid[i][j] = 1
        
        # Create maze patterns with gaps for multiple paths
        
        # 1. Create horizontal walls with gaps
        for i in range(4, self.size-4, 4):
            # Skip with 30% probability to ensure more open areas
            if random.random() < 0.3:
                continue
                
            # Horizontal wall with multiple gaps
            for j in range(1, self.size-1):
                # Create a gap pattern (40% chance of gap)
                if j % 3 != 0 and random.random() > 0.4:
                    self.grid[i][j] = 1
        
        # 2. Create vertical walls with gaps
        for j in range(4, self.size-4, 4):
            # Skip with 30% probability
            if random.random() < 0.3:
                continue
                
            # Vertical wall with multiple gaps
            for i in range(1, self.size-1):
                # Create a gap pattern (40% chance of gap)
                if i % 3 != 0 and random.random() > 0.4:
                    self.grid[i][j] = 1
        
        # 3. Create some random "neighborhoods" (clusters of houses)
        for _ in range(4):
            center_x = random.randint(5, self.size-6)
            center_y = random.randint(5, self.size-6)
            radius = random.randint(2, 4)
            
            # Place houses in a rough circular pattern with gaps
            for i in range(center_x - radius, center_x + radius + 1):
                for j in range(center_y - radius, center_y + radius + 1):
                    if 0 < i < self.size-1 and 0 < j < self.size-1:
                        # Create a circular-ish pattern with random gaps
                        distance = math.sqrt((i - center_x)**2 + (j - center_y)**2)
                        if distance <= radius and random.random() > 0.4:
                            self.grid[i][j] = 1
        
        # 4. Ensure direct vicinity of start and end is accessible
        for dx, dy in [(0, 1), (1, 0), (1, 1)]:
            self.grid[1 + dx][1 + dy] = 0  # Clear around start
            self.grid[self.size-2 - dx][self.size-2 - dy] = 0  # Clear around end
    
    def _create_complex_path(self):
        """Create a complex path from start to exit when no valid path exists."""
        if not self.start_pos or not self.end_positions:
            return
        
        # Always ensure the exit is at the bottom-right corner
        exit_pos = (self.size-2, self.size-2)
        self.grid[exit_pos[0]][exit_pos[1]] = 0
        self.end_positions = [exit_pos]
        
        sx, sy = self.start_pos
        ex, ey = exit_pos
        
        # Create a zigzag path instead of a straight line
        # First go halfway down
        mid_x = (sx + ex) // 2
        for x in range(sx, mid_x + 1):
            self.grid[x][sy] = 0
        
        # Then go halfway right
        mid_y = (sy + ey) // 2
        for y in range(sy, mid_y + 1):
            self.grid[mid_x][y] = 0
        
        # Then continue to bottom
        for x in range(mid_x, ex + 1):
            self.grid[x][mid_y] = 0
        
        # Finally go to the right to reach the exit
        for y in range(mid_y, ey + 1):
            self.grid[ex][y] = 0
        
        # Add a few random detours to create alternative paths
        for _ in range(3):
            x = random.randint(2, self.size-3)
            y = random.randint(2, self.size-3)
            length = random.randint(3, 6)
            
            # Horizontal or vertical detour
            if random.choice([True, False]):
                # Horizontal
                for j in range(max(1, y-length), min(self.size-1, y+length)):
                    self.grid[x][j] = 0
            else:
                # Vertical
                for i in range(max(1, x-length), min(self.size-1, x+length)):
                    self.grid[i][y] = 0
    
    def has_valid_path(self):
        """Check if there's a valid path from start to any exit using BFS."""
        if not self.start_pos or not self.end_positions:
            return False
        
        visited = set()
        queue = [self.start_pos]
        visited.add(self.start_pos)
        
        while queue:
            x, y = queue.pop(0)
            
            if (x, y) in self.end_positions:
                return True
            
            # Check all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.size and 0 <= ny < self.size and 
                    self.grid[nx][ny] == 0 and (nx, ny) not in visited):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
        
        return False
    
    def add_camera(self, pos):
        """Add a camera at the specified position if it's a barrier."""
        x, y = pos
        if 0 <= x < self.size and 0 <= y < self.size and self.grid[x][y] == 1:
            camera = Camera(x, y, self.config)
            self.cameras.append(camera)
            return True
        return False
    
    def render(self, screen):
        """Render the map on the screen."""
        colors = self.config["colors"]
        
        # Draw the grid
        for x in range(self.size):
            for y in range(self.size):
                rect = pygame.Rect(
                    y * self.cell_size, 
                    x * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                
                # Check if it's a border
                if (x == 0 or x == self.size-1 or y == 0 or y == self.size-1):
                    # Draw border as black
                    pygame.draw.rect(screen, (0, 0, 0), rect)
                elif self.grid[x][y] == 1:  # Barrier - draw house icon
                    screen.blit(self.house_svg, (y * self.cell_size, x * self.cell_size))
                else:  # Street
                    pygame.draw.rect(screen, colors["street"], rect)
                
                # Draw grid lines (lighter to be less distracting)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)
        
        # Draw start position
        if self.start_pos:
            x, y = self.start_pos
            start_rect = pygame.Rect(
                y * self.cell_size, 
                x * self.cell_size, 
                self.cell_size, 
                self.cell_size
            )
            pygame.draw.rect(screen, (0, 255, 0), start_rect)  # Green for start
        
        # Draw exit positions
        for x, y in self.end_positions:
            end_rect = pygame.Rect(
                y * self.cell_size, 
                x * self.cell_size, 
                self.cell_size, 
                self.cell_size
            )
            pygame.draw.rect(screen, (255, 165, 0), end_rect)  # Orange for exit
        
        # Draw cameras and their vision
        for camera in self.cameras:
            camera.render(screen, self)


class Camera:
    """Class representing a surveillance camera with a field of view."""
    
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.config = config
        self.cell_size = config["cell_size"]
        self.vision_range = 3  # Reduced from 5 to 3 - How far the camera can see
        self.vision_angle = 90  # Field of view in degrees
        self.direction = 0  # 0: right, 90: down, 180: left, 270: up
        
    def rotate(self, clockwise=True):
        """Rotate the camera direction."""
        if clockwise:
            self.direction = (self.direction + 90) % 360
        else:
            self.direction = (self.direction - 90) % 360
    
    def can_see(self, x, y, game_map):
        """Check if the camera can see the position (x, y) within a circular area."""
        # Calculate distance to the target
        dx = y - self.y  # Swapped because grid is row/col but rendering is x/y
        dy = x - self.x
        
        # Check if within circular range
        distance = (dx**2 + dy**2)**0.5
        if distance > self.vision_range:
            return False
        
        # Check line of sight (no barriers in between)
        # Simple Bresenham line algorithm to check for barriers
        points = self._get_line(self.x, self.y, x, y)
        for px, py in points[1:-1]:  # Skip start and end points
            if 0 <= px < game_map.size and 0 <= py < game_map.size:
                if game_map.grid[px][py] == 1:  # Barrier blocks vision
                    return False
        
        return True
    
    def _get_line(self, x0, y0, x1, y1):
        """Get a list of points in a line from (x0, y0) to (x1, y1)."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        return points
    
    def render(self, screen, game_map):
        """Render the camera and its vision cone as a circle."""
        colors = self.config["colors"]
        
        # Draw camera
        center_x = (self.y + 0.5) * self.cell_size
        center_y = (self.x + 0.5) * self.cell_size
        radius = self.cell_size // 3
        pygame.draw.circle(screen, colors["camera"], (center_x, center_y), radius)
        
        # Draw direction indicator
        angle_rad = np.radians(self.direction)
        end_x = center_x + radius * np.cos(angle_rad)
        end_y = center_y + radius * np.sin(angle_rad)
        pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (end_x, end_y), 2)
        
        # Draw vision cone as a circle
        vision_surface = pygame.Surface(
            (game_map.size * self.cell_size, game_map.size * self.cell_size), 
            pygame.SRCALPHA
        )
        
        # Calculate vision radius in pixels
        vision_radius = self.vision_range * self.cell_size
        
        # Draw a semi-transparent circle for the camera's vision
        pygame.draw.circle(
            vision_surface, 
            colors["camera_vision"], 
            (center_x, center_y), 
            vision_radius
        )
        
        # Apply vision surface to the main screen
        screen.blit(vision_surface, (0, 0))
        
        # Draw the perimeter of the vision range
        pygame.draw.circle(
            screen, 
            (255, 0, 0, 128),  # Semi-transparent red
            (center_x, center_y), 
            vision_radius, 
            1  # Line width
        )
