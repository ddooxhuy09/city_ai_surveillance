import pygame
import random
import numpy as np
import math
import time

class GameMap:
    """Class representing the game map with barriers and streets."""

    def __init__(self, config):
        """Initialize the game map with configuration."""
        self.config = config
        self.size = config.get("map_size", 30)  # Increased default map size to 30x30
        self.cell_size = config["cell_size"]
        self.grid = np.zeros((self.size, self.size), dtype=int)  # 0: street, 1: barrier
        self.cameras = []
        self.start_pos = None
        self.end_positions = []  # Exit positions at the edges
        
        # Lưu trữ vị trí của các địa điểm cho Prolog
        self.location_positions = {}
        
        self.generate_map()

    def generate_map(self):
        """Generate a maze-like map with multiple potential paths."""
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
        self._generate_maze()

        # Ensure there's at least one valid path
        if not self.has_valid_path():
            self._create_multiple_paths()
            
        # Cập nhật thông tin vị trí cho Prolog
        self._map_locations_for_prolog()

    def _map_locations_for_prolog(self):
        """Map positions to location names for Prolog."""
        # Đối với thành phố, ánh xạ vị trí quan trọng vào tên địa điểm
        important_positions = [
            (1, 1),  # Start position (city_center)
            (self.size-2, self.size-2),  # End position (exit point - highway_entrance)
        ]
        
        # Tìm thêm một số điểm quan trọng khác trên bản đồ
        pathways = []
        for x in range(1, self.size-1):
            for y in range(1, self.size-1):
                if self.grid[x][y] == 0:  # Là đường đi
                    open_neighbors = 0
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx][ny] == 0:
                            open_neighbors += 1
                    
                    # Nếu là giao lộ (có ít nhất 3 láng giềng là đường)
                    if open_neighbors >= 3:
                        pathways.append((x, y))
        
        # Chọn ngẫu nhiên một số điểm làm các địa điểm quan trọng
        if len(pathways) >= 6:
            important_positions.extend(random.sample(pathways, 6))
        else:
            important_positions.extend(pathways)
        
        # Ánh xạ vào tên địa điểm
        location_names = [
            "city_center", 
            "highway_entrance",
            "industrial_zone", 
            "residential_area",
            "shopping_mall",
            "park",
            "train_station",
            "port"
        ]
        
        for i, pos in enumerate(important_positions[:len(location_names)]):
            self.location_positions[location_names[i]] = pos

    def get_position_for_location(self, location_name):
        """Trả về vị trí (x, y) cho một tên địa điểm."""
        return self.location_positions.get(location_name, (1, 1))  # Mặc định về city_center

    def _generate_maze(self):
        """Generate a maze using recursive division algorithm."""
        # Start with an empty grid (already created in init)
        # Recursively divide the space
        self._divide_maze(1, 1, self.size-2, self.size-2)

        # Add some random openings to create multiple paths
        self._add_random_openings()

    def _divide_maze(self, x1, y1, x2, y2):
        """Recursively divide the maze to create a perfect maze structure."""
        width = x2 - x1
        height = y2 - y1
        
        # Base case: if region is too small, don't divide further
        if width < 3 or height < 3:
            return
        
        # Choose a random point to divide the maze horizontally
        x = random.randint(x1 + 1, x2 - 1)
        # Choose a random point to divide the maze vertically
        y = random.randint(y1 + 1, y2 - 1)
        
        # Create walls
        for i in range(x1, x2 + 1):
            if self.grid[i][y] == 0:  # Only create wall if it's currently a path
                self.grid[i][y] = 1
        
        for j in range(y1, y2 + 1):
            if self.grid[x][j] == 0:  # Only create wall if it's currently a path
                self.grid[x][j] = 1
        
        # Create random openings in each wall
        # Don't create an opening at the intersection of the two walls
        openings = []
        
        # Opening in the horizontal wall
        horizontal_opening = random.randint(y1, y - 1)
        self.grid[x][horizontal_opening] = 0
        openings.append((x, horizontal_opening))
        
        horizontal_opening = random.randint(y + 1, y2)
        self.grid[x][horizontal_opening] = 0
        openings.append((x, horizontal_opening))
        
        # Opening in the vertical wall
        vertical_opening = random.randint(x1, x - 1)
        self.grid[vertical_opening][y] = 0
        openings.append((vertical_opening, y))
        
        vertical_opening = random.randint(x + 1, x2)
        self.grid[vertical_opening][y] = 0
        openings.append((vertical_opening, y))
        
        # Recursively divide the resulting quadrants
        self._divide_maze(x1, y1, x - 1, y - 1)  # Top-left
        self._divide_maze(x + 1, y1, x2, y - 1)  # Top-right
        self._divide_maze(x1, y + 1, x - 1, y2)  # Bottom-left
        self._divide_maze(x + 1, y + 1, x2, y2)  # Bottom-right

    def _add_random_openings(self):
        """Add random openings to create multiple paths through the maze."""
        num_openings = int((self.size * self.size) * 0.05)  # 5% of cells will be openings
        for _ in range(num_openings):
            x = random.randint(1, self.size - 2)
            y = random.randint(1, self.size - 2)
            
            # Don't create openings at start or end
            if (x, y) != self.start_pos and (x, y) not in self.end_positions:
                self.grid[x][y] = 0  # Create opening (path)

    def _create_multiple_paths(self):
        """Create multiple distinct paths from start to exit."""
        # Always ensure the exit is clear
        exit_pos = (self.size-2, self.size-2)
        self.grid[exit_pos[0]][exit_pos[1]] = 0
        self.end_positions = [exit_pos]
        
        sx, sy = self.start_pos
        ex, ey = exit_pos
        
        # Create main path
        self._create_path(sx, sy, ex, ey)
        
        # Create 2-3 alternative paths
        for _ in range(random.randint(2, 3)):
            # Pick intermediate points
            ix = random.randint(5, self.size - 5)
            iy = random.randint(5, self.size - 5)
            
            # Create path segments
            self._create_path(sx, sy, ix, iy)
            self._create_path(ix, iy, ex, ey)

    def _create_path(self, x1, y1, x2, y2):
        """Create a winding path between two points."""
        # Make a copy of coordinates to work with
        x, y = x1, y1
        
        # Continue until we reach the target
        while (x, y) != (x2, y2):
            # Choose direction with bias towards target
            if random.random() < 0.7:  # 70% chance to move towards target
                if x < x2:
                    x += 1
                elif x > x2:
                    x -= 1
                elif y < y2:
                    y += 1
                elif y > y2:
                    y -= 1
            else:  # 30% chance to move randomly
                direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                new_x = x + direction[0]
                new_y = y + direction[1]
                
                # Ensure we stay within bounds
                if 0 < new_x < self.size-1 and 0 < new_y < self.size-1:
                    x, y = new_x, new_y
            
            # Clear this cell
            self.grid[x][y] = 0

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
                elif self.grid[x][y] == 1:  # Barrier - draw as wall
                    pygame.draw.rect(screen, (50, 50, 150), rect)  # Blue-gray walls
                else:  # Street
                    pygame.draw.rect(screen, colors["street"], rect)

                # Draw grid lines
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
        self.vision_range = 3  # How far the camera can see
        self.vision_angle = 90  # Field of view in degrees
        self.direction = 0  # 0: right, 90: down, 180: left, 270: up
        
        # Camera timing properties for scan/rest cycle
        self.active = True  # Whether the camera is currently scanning
        self.scan_time = config.get("camera_scan_time", 3.0)  # Seconds to scan
        self.rest_time = config.get("camera_rest_time", 1.0)  # Seconds to rest
        self.timer = 0.0  # Current timer
        self.last_update = time.time()  # Last update time

    def update(self):
        """Update camera state based on elapsed time."""
        current_time = time.time()
        elapsed = current_time - self.last_update
        self.last_update = current_time
        
        # Update timer
        self.timer += elapsed
        
        # Check if we need to switch states
        if self.active and self.timer >= self.scan_time:
            self.active = False
            self.timer = 0.0
        elif not self.active and self.timer >= self.rest_time:
            self.active = True
            self.timer = 0.0

    def rotate(self, clockwise=True):
        """Rotate the camera direction."""
        if clockwise:
            self.direction = (self.direction + 90) % 360
        else:
            self.direction = (self.direction - 90) % 360

    def can_see(self, x, y, game_map):
        """Check if the camera can see the position (x, y)."""
        # Camera cannot see if it's in rest mode
        if not self.active:
            return False
            
        # Calculate distance to the target
        dx = y - self.y  # Swapped because grid is row/col but rendering is x/y
        dy = x - self.x

        # Check if within circular range
        distance = (dx**2 + dy**2)**0.5
        if distance > self.vision_range:
            return False

        # Check line of sight (no barriers in between)
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
        """Render the camera and its vision cone."""
        colors = self.config["colors"]

        # Draw camera
        center_x = (self.y + 0.5) * self.cell_size
        center_y = (self.x + 0.5) * self.cell_size
        radius = self.cell_size // 3
        
        # Draw camera with different color based on active state
        if self.active:
            camera_color = colors.get("camera", (255, 0, 0))  # Red when active
        else:
            camera_color = (100, 100, 100)  # Gray when resting
            
        pygame.draw.circle(screen, camera_color, (center_x, center_y), radius)

        # Draw direction indicator
        angle_rad = np.radians(self.direction)
        end_x = center_x + radius * np.cos(angle_rad)
        end_y = center_y + radius * np.sin(angle_rad)
        pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (end_x, end_y), 2)

        # Only draw vision if camera is active
        if self.active:
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
                colors.get("camera_vision", (255, 200, 200, 100)),
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
