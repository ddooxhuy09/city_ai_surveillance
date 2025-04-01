"""
Generates the city map with random elements.
"""
import random

class CityGenerator:
    def __init__(self, prolog, config):
        """Initialize city generator with Prolog interface and config."""
        self.prolog = prolog
        self.config = config
        self.screen_width = config.get("screen_width", 1024)
        self.screen_height = config.get("screen_height", 768)
        
    def generate_city(self):
        """Generate a random city layout."""
        try:
            if self.prolog.use_mock:
                return self._generate_mock_city()
            else:
                return self._generate_prolog_city()
        except Exception as e:
            print(f"Lỗi khi tạo thành phố: {e}")
            return self._generate_mock_city()
    
    def _generate_mock_city(self):
        """Generate a city without using Prolog."""
        # Define locations
        locations = [
            "city_center", "industrial_zone", "residential_area", 
            "shopping_mall", "park", "highway_entrance", 
            "port", "train_station"
        ]
        
        # Define connections
        connections = [
            ("city_center", "industrial_zone"),
            ("city_center", "residential_area"),
            ("industrial_zone", "highway_entrance"),
            ("residential_area", "shopping_mall"),
            ("shopping_mall", "park"),
            ("park", "highway_entrance"),
            ("highway_entrance", "port"),
            ("city_center", "train_station"),
            ("train_station", "port")
        ]
        
        # Define exit points
        exit_points = ["highway_entrance", "port", "train_station"]
        
        # Create city map
        city_map = {}
        
        # Define margins
        margin = 100
        
        # Place locations
        for loc in locations:
            while True:
                x = random.randint(margin, self.screen_width - 250 - margin)  # Account for control panel
                y = random.randint(margin, self.screen_height - margin)
                
                # Check distance from other locations
                too_close = False
                for existing_loc, (ex, ey) in city_map.items():
                    if existing_loc in ["connections", "exit_points"]:
                        continue
                    distance = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                    if distance < 150:  # Minimum distance between locations
                        too_close = True
                        break
                
                if not too_close:
                    city_map[loc] = (x, y)
                    break
        
        # Add connections
        city_map["connections"] = connections
        
        # Add exit points
        city_map["exit_points"] = exit_points
        
        return city_map
    
    def _generate_prolog_city(self):
        """Generate a city based on Prolog knowledge base."""
        # Get all locations from Prolog
        locations_query = list(self.prolog.query("location(X)"))
        locations = [loc["X"] for loc in locations_query]
        
        # Create city map with random positions
        city_map = {}
        
        # Define margins
        margin = 100
        
        # Place locations
        for loc in locations:
            while True:
                x = random.randint(margin, self.screen_width - 250 - margin)  # Account for control panel
                y = random.randint(margin, self.screen_height - margin)
                
                # Check distance from other locations
                too_close = False
                for existing_loc, (ex, ey) in city_map.items():
                    if existing_loc in ["connections", "exit_points"]:
                        continue
                    distance = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                    if distance < 150:  # Minimum distance between locations
                        too_close = True
                        break
                
                if not too_close:
                    city_map[loc] = (x, y)
                    break
        
        # Get connections from Prolog
        connections = []
        for loc1 in locations:
            query = f"connected({loc1}, X)"
            conn_results = list(self.prolog.query(query))
            for result in conn_results:
                loc2 = result["X"]
                if (loc1, loc2) not in connections and (loc2, loc1) not in connections:
                    connections.append((loc1, loc2))
        
        # Add connections to city map
        city_map["connections"] = connections
        
        # Add exit points
        exit_points = list(self.prolog.query("exit_point(X)"))
        city_map["exit_points"] = [exit["X"] for exit in exit_points]
        
        return city_map
