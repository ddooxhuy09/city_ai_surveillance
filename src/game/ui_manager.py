"""
Manages the user interface elements and rendering.
"""
import pygame
import os

class UIManager:
    def __init__(self, screen, city_map, game_state):
        """Initialize UI manager with screen, city map and game state."""
        self.screen = screen
        self.city_map = city_map
        self.game_state = game_state
        
        # Load UI assets
        self.load_assets()
        
        # UI state
        self.selected_camera = None
        self.camera_placement_mode = False
        self.hover_location = None
        self.show_help = False
    
    def load_assets(self):
        """Load UI assets like fonts and images."""
        # Fonts
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # Create simple placeholder images
        self.img_city = self._create_circle_surface(20, (200, 200, 200))
        self.img_camera = self._create_circle_surface(15, (0, 255, 0))
        self.img_ai = self._create_circle_surface(18, (255, 0, 0))
        self.img_exit = self._create_circle_surface(25, (255, 255, 0))
        
        # UI panels
        self.control_panel_rect = pygame.Rect(
            self.screen.get_width() - 250, 0, 
            250, self.screen.get_height()
        )
    
    def _create_circle_surface(self, size, color):
        """Create a circular surface with the given size and color."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)
        return surface
    
    def handle_event(self, event):
        """Handle UI events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicking in control panel
                if self.control_panel_rect.collidepoint(event.pos):
                    self.handle_control_panel_click(event.pos)
                else:
                    # Check if in camera placement mode
                    if self.camera_placement_mode:
                        self.place_camera_at_mouse(event.pos)
                    else:
                        # Check if clicked on camera
                        self.check_camera_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover location
            self.hover_location = self.get_location_at_mouse(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.show_help = not self.show_help
    
    def update(self, dt):
        """Update UI elements."""
        # Any animations or UI state updates can go here
        pass
    
    def render(self):
        """Render all UI elements."""
        # Draw city map
        self.render_city_map()
        
        # Draw control panel
        self.render_control_panel()
        
        # Draw game info
        self.render_game_info()
        
        # Draw help if needed
        if self.show_help:
            self.render_help()
    
    def render_city_map(self):
        """Render the city map with all elements."""
        # Draw connections first (roads)
        if "connections" in self.city_map:
            for loc1, loc2 in self.city_map["connections"]:
                if loc1 in self.city_map and loc2 in self.city_map and loc1 != "connections" and loc2 != "connections" and loc1 != "exit_points" and loc2 != "exit_points":
                    try:
                        pygame.draw.line(
                            self.screen, 
                            (100, 100, 100), 
                            self.city_map[loc1], 
                            self.city_map[loc2], 
                            3
                        )
                    except Exception as e:
                        print(f"Lỗi khi vẽ đường: {e}, {loc1}, {loc2}")
        
        # Draw locations
        for location, value in self.city_map.items():
            if location in ["connections", "exit_points"]:
                continue
                
            try:
                x, y = value
                
                # Check if it's an exit point
                if "exit_points" in self.city_map and location in self.city_map["exit_points"]:
                    self.screen.blit(self.img_exit, (x - 12, y - 12))
                else:
                    self.screen.blit(self.img_city, (x - 10, y - 10))
                
                # Draw location name
                text = self.font_small.render(location, True, (255, 255, 255))
                self.screen.blit(text, (x - text.get_width() // 2, y + 15))
            except Exception as e:
                print(f"Lỗi khi vẽ địa điểm {location}: {e}")
        
        # Draw cameras
        for camera in self.game_state.cameras:
            loc = camera["location"]
            if loc in self.city_map and loc not in ["connections", "exit_points"]:
                try:
                    x, y = self.city_map[loc]
                    self.screen.blit(self.img_camera, (x - 7, y - 7))
                    
                    # Draw camera range
                    pygame.draw.circle(
                        self.screen,
                        (0, 255, 0, 50),  # Semi-transparent green
                        (x, y),
                        camera["range"] * 50,  # Scale factor for visualization
                        1  # Circle outline
                    )
                except Exception as e:
                    print(f"Lỗi khi vẽ camera tại {loc}: {e}")
        
        # Draw AI if detected
        if self.game_state.ai_position and self.is_ai_visible():
            if self.game_state.ai_position in self.city_map and self.game_state.ai_position not in ["connections", "exit_points"]:
                try:
                    x, y = self.city_map[self.game_state.ai_position]
                    self.screen.blit(self.img_ai, (x - 9, y - 9))
                except Exception as e:
                    print(f"Lỗi khi vẽ AI: {e}")
        
        # Draw decoy signals
        for decoy in self.game_state.decoy_signals:
            if decoy["location"] in self.city_map and decoy["location"] not in ["connections", "exit_points"]:
                try:
                    x, y = self.city_map[decoy["location"]]
                    # Draw pulsating circle
                    radius = 30 + int(10 * (pygame.time.get_ticks() % 1000) / 1000.0)
                    pygame.draw.circle(
                        self.screen,
                        (255, 165, 0, 150),  # Semi-transparent orange
                        (x, y),
                        radius,
                        2
                    )
                except Exception as e:
                    print(f"Lỗi khi vẽ tín hiệu giả: {e}")
    
    def render_control_panel(self):
        """Render the control panel."""
        # Draw panel background
        pygame.draw.rect(self.screen, (50, 50, 50), self.control_panel_rect)
        
        # Draw panel title
        title = self.font_medium.render("Control Panel", True, (255, 255, 255))
        self.screen.blit(
            title, 
            (self.control_panel_rect.x + (self.control_panel_rect.width - title.get_width()) // 2, 
             self.control_panel_rect.y + 20)
        )
        
        # Draw camera placement button
        camera_button_rect = pygame.Rect(
            self.control_panel_rect.x + 20,
            self.control_panel_rect.y + 70,
            self.control_panel_rect.width - 40,
            40
        )
        pygame.draw.rect(
            self.screen, 
            (0, 150, 0) if self.camera_placement_mode else (0, 100, 0), 
            camera_button_rect
        )
        camera_text = self.font_small.render(
            "Place Camera", True, (255, 255, 255)
        )
        self.screen.blit(
            camera_text,
            (camera_button_rect.x + (camera_button_rect.width - camera_text.get_width()) // 2,
             camera_button_rect.y + (camera_button_rect.height - camera_text.get_height()) // 2)
        )
        
        # Draw score information
        score_y = self.control_panel_rect.y + 150
        player_score_text = self.font_small.render(
            f"Player Score: {self.game_state.player_score}", True, (255, 255, 255)
        )
        self.screen.blit(player_score_text, (self.control_panel_rect.x + 20, score_y))
        
        ai_score_text = self.font_small.render(
            f"AI Score: {self.game_state.ai_score}", True, (255, 255, 255)
        )
        self.screen.blit(ai_score_text, (self.control_panel_rect.x + 20, score_y + 30))
        
        # Draw time
        time_text = self.font_small.render(
            f"Time: {int(self.game_state.game_time)}s", True, (255, 255, 255)
        )
        self.screen.blit(time_text, (self.control_panel_rect.x + 20, score_y + 60))
        
        # Draw help hint
        help_text = self.font_small.render(
            "Press H for Help", True, (200, 200, 200)
        )
        self.screen.blit(
            help_text, 
            (self.control_panel_rect.x + 20, self.screen.get_height() - 40)
        )
    
    def render_game_info(self):
        """Render game information."""
        # Draw hover location info
        if self.hover_location and self.hover_location not in ["connections", "exit_points"]:
            info_text = self.font_small.render(
                f"Location: {self.hover_location}", True, (255, 255, 255)
            )
            self.screen.blit(info_text, (10, 10))
            
            # If it's an exit point, indicate this
            if "exit_points" in self.city_map and self.hover_location in self.city_map["exit_points"]:
                exit_text = self.font_small.render(
                    "EXIT POINT", True, (255, 255, 0)
                )
                self.screen.blit(exit_text, (10, 40))
    
    def render_help(self):
        """Render help screen."""
        # Create semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw help text
        help_title = self.font_large.render("Help", True, (255, 255, 255))
        self.screen.blit(
            help_title, 
            ((self.screen.get_width() - help_title.get_width()) // 2, 50)
        )
        
        help_texts = [
            "- Click 'Place Camera' then click on a location to place a camera",
            "- Cameras detect AI movement within their range",
            "- AI will try to escape the city through exit points",
            "- AI can create false signals to distract you",
            "- You win by catching the AI before it escapes",
            "- AI wins if it reaches an exit point undetected",
            "",
            "Press H to close this help screen"
        ]
        
        y = 150
        for text in help_texts:
            rendered = self.font_medium.render(text, True, (255, 255, 255))
            self.screen.blit(
                rendered,
                ((self.screen.get_width() - rendered.get_width()) // 2, y)
            )
            y += 40
    
    def show_game_over(self, result):
        """Show game over screen."""
        # Create overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.font_large.render("Game Over", True, (255, 255, 255))
        self.screen.blit(
            game_over_text,
            ((self.screen.get_width() - game_over_text.get_width()) // 2, 150)
        )
        
        # Draw result
        if result == "player_win":
            result_text = "You caught the AI! Victory!"
            color = (0, 255, 0)  # Green for victory
        else:
            result_text = "The AI escaped! You lose!"
            color = (255, 0, 0)  # Red for defeat
            
        result_rendered = self.font_large.render(result_text, True, color)
        self.screen.blit(
            result_rendered,
            ((self.screen.get_width() - result_rendered.get_width()) // 2, 250)
        )
        
        # Draw scores
        score_text = self.font_medium.render(
            f"Player Score: {self.game_state.player_score}   AI Score: {self.game_state.ai_score}",
            True, (255, 255, 255)
        )
        self.screen.blit(
            score_text,
            ((self.screen.get_width() - score_text.get_width()) // 2, 350)
        )
        
        # Draw continue text
        continue_text = self.font_medium.render(
            "Press any key to play again", True, (200, 200, 200)
        )
        self.screen.blit(
            continue_text,
            ((self.screen.get_width() - continue_text.get_width()) // 2, 450)
        )
        
        pygame.display.flip()
    
    def handle_control_panel_click(self, pos):
        """Handle clicks on the control panel."""
        # Camera placement button
        camera_button_rect = pygame.Rect(
            self.control_panel_rect.x + 20,
            self.control_panel_rect.y + 70,
            self.control_panel_rect.width - 40,
            40
        )
        
        if camera_button_rect.collidepoint(pos):
            self.camera_placement_mode = not self.camera_placement_mode
    
    def place_camera_at_mouse(self, pos):
        """Place a camera at the mouse position."""
        location = self.get_location_at_mouse(pos)
        if location and location not in ["connections", "exit_points"]:
            self.game_state.place_camera(location)
            self.camera_placement_mode = False
    
    def check_camera_click(self, pos):
        """Check if a camera was clicked."""
        for camera in self.game_state.cameras:
            loc = camera["location"]
            if loc in self.city_map and loc not in ["connections", "exit_points"]:
                try:
                    x, y = self.city_map[loc]
                    # Simple circle collision
                    dist = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
                    if dist < 15:  # Camera click radius
                        self.selected_camera = camera["id"]
                        camera_info = self.game_state.check_camera(camera["id"])
                        # Show detection status in console (could add UI feedback later)
                        if camera_info:
                            detection_status = "Detects AI!" if camera_info["detects_ai"] else "No AI detected"
                            decoy_count = len(camera_info["decoys_detected"])
                            decoy_status = f"Detected {decoy_count} decoy(s)" if decoy_count else "No decoys detected"
                            print(f"Camera {camera['id']} at {loc}: {detection_status}, {decoy_status}")
                        break
                except Exception as e:
                    print(f"Lỗi khi kiểm tra camera click: {e}")
    
    def get_location_at_mouse(self, pos):
        """Get the location at the mouse position."""
        for location, value in self.city_map.items():
            # Skip special keys
            if location in ["connections", "exit_points"]:
                continue
                
            try:
                # Now safely unpack the coordinate tuple
                x, y = value
                
                # Simple circle collision
                dist = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
                if dist < 20:  # Location click radius
                    return location
            except Exception as e:
                print(f"Lỗi khi kiểm tra vị trí chuột: {e}")
        
        return None
    
    def is_ai_visible(self):
        """Check if AI should be visible to the player."""
        # AI is always visible in mock mode for demonstration
        try:
            if self.game_state.prolog.use_mock:
                for camera in self.game_state.cameras:
                    camera_loc = camera["location"]
                    ai_loc = self.game_state.ai_position
                    
                    if camera_loc in self.city_map and ai_loc in self.city_map:
                        if camera_loc not in ["connections", "exit_points"] and ai_loc not in ["connections", "exit_points"]:
                            cam_x, cam_y = self.city_map[camera_loc]
                            ai_x, ai_y = self.city_map[ai_loc]
                            
                            # Calculate distance
                            distance = ((cam_x - ai_x) ** 2 + (cam_y - ai_y) ** 2) ** 0.5
                            
                            # Check if within range
                            if distance < camera["range"] * 100:
                                return True
                return False
            
            # For real Prolog mode
            for camera in self.game_state.cameras:
                try:
                    detection_query = f"camera_coverage({camera['id']}, {self.game_state.ai_position})"
                    if list(self.game_state.prolog.query(detection_query)):
                        return True
                except Exception as e:
                    print(f"Lỗi khi kiểm tra phát hiện AI: {e}")
            
            return False
        except Exception as e:
            print(f"Lỗi khi kiểm tra AI visible: {e}")
            return False
