"""
Strategic decision making for the AI agent.
"""

class AIStrategy:
    def __init__(self, prolog_interface):
        """Initialize the strategy module with Prolog interface."""
        self.prolog = prolog_interface
        
    def evaluate_escape_routes(self):
        """Evaluate possible escape routes and return the best one."""
        query = """
        ai_state(position, CurrentPos),
        findall(Exit, exit_point(Exit), ExitPoints),
        find_best_escape_route([], ExitPoints, BestRoute)
        """
        result = list(self.prolog.query(query))
        if result and "BestRoute" in result[0]:
            return result[0]["BestRoute"]
        return None
    
    def evaluate_decoy_locations(self):
        """Evaluate possible locations for creating decoys."""
        query = """
        findall(Loc-Score, (
            location(Loc), 
            ai_state(position, CurrentPos),
            Loc \= CurrentPos,
            camera_coverage(Camera, Loc),
            evaluate_decoy_effectiveness(Loc, Score)
        ), ScoredLocations),
        sort(2, @>=, ScoredLocations, RankedLocations)
        """
        result = list(self.prolog.query(query))
        if result and "RankedLocations" in result[0]:
            return result[0]["RankedLocations"]
        return []
    
    def calculate_risk_for_path(self, path):
        """Calculate the risk level for a given path."""
        if not path:
            return float('inf')
            
        risk_sum = 0
        for location in path:
            query = f"risk_level({location}, Risk)"
            result = list(self.prolog.query(query))
            if result:
                risk = result[0]["Risk"]
                # Convert risk level to numeric value
                if risk == "high":
                    risk_sum += 3
                elif risk == "medium":
                    risk_sum += 2
                elif risk == "low":
                    risk_sum += 1
        
        return risk_sum
