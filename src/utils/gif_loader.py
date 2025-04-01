import pygame
import requests
import io
from PIL import Image, ImageSequence
import os

def download_gif(url, save_path=None):
    """Download a GIF from a URL and optionally save it"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            gif_data = response.content
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(gif_data)
            return gif_data
        else:
            print(f"Failed to download GIF: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading GIF: {e}")
        return None

def load_gif_frames(gif_data=None, gif_path=None):
    """Load frames from a GIF file or data"""
    frames = []
    durations = []
    
    try:
        if gif_data:
            gif = Image.open(io.BytesIO(gif_data))
        elif gif_path and os.path.exists(gif_path):
            gif = Image.open(gif_path)
        else:
            print("No valid GIF data or path provided")
            return [], []
        
        # Extract frames
        for frame in ImageSequence.Iterator(gif):
            # Convert to RGBA if needed
            frame_rgba = frame.convert("RGBA")
            frame_data = frame_rgba.tobytes()
            frame_size = frame_rgba.size
            pygame_frame = pygame.image.fromstring(frame_data, frame_size, "RGBA")
            frames.append(pygame_frame)
            
            # Get frame duration (in milliseconds)
            duration = frame.info.get('duration', 100)  # Default to 100ms
            durations.append(duration)
            
        return frames, durations
    
    except Exception as e:
        print(f"Error loading GIF frames: {e}")
        return [], []

class AnimatedSprite:
    """Class to handle animated sprites from GIF files"""
    
    def __init__(self, frames, durations, default_size=None):
        self.frames = frames
        self.durations = durations
        self.current_frame = 0
        self.frame_time = 0
        
        # Resize frames if default_size is provided
        if default_size and self.frames:
            self.resize(default_size)
    
    def resize(self, size):
        """Resize all frames to the specified size"""
        if not self.frames:
            return
            
        self.frames = [pygame.transform.scale(frame, size) for frame in self.frames]
    
    def update(self, dt):
        """Update animation based on elapsed time (in seconds)"""
        if not self.frames or not self.durations:
            return
            
        # Convert dt to milliseconds
        dt_ms = dt * 1000
        
        # Update frame time
        self.frame_time += dt_ms
        
        # Check if we need to advance to the next frame
        if self.frame_time >= self.durations[self.current_frame]:
            self.frame_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        """Get the current frame of the animation"""
        if not self.frames:
            return None
            
        return self.frames[self.current_frame]
    
    @classmethod
    def from_url(cls, url, default_size=None, save_path=None):
        """Create an AnimatedSprite from a URL"""
        gif_data = download_gif(url, save_path)
        if gif_data:
            frames, durations = load_gif_frames(gif_data=gif_data)
            return cls(frames, durations, default_size)
        return cls([], [])
    
    @classmethod
    def from_file(cls, file_path, default_size=None):
        """Create an AnimatedSprite from a file"""
        if os.path.exists(file_path):
            frames, durations = load_gif_frames(gif_path=file_path)
            return cls(frames, durations, default_size)
        return cls([], [])
