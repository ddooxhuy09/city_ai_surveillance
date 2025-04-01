"""
Helper class to build Prolog queries programmatically.
"""

class PrologQueryBuilder:
    def __init__(self):
        """Initialize the query builder."""
        self.query_parts = []
        
    def add_condition(self, condition):
        """Add a condition to the query."""
        self.query_parts.append(condition)
        return self
    
    def add_variable(self, var_name, value=None):
        """Add a variable to the query."""
        if value is None:
            return self.add_condition(var_name)
        else:
            return self.add_condition(f"{var_name} = {value}")
    
    def add_predicate(self, predicate, *args):
        """Add a predicate to the query."""
        args_str = ", ".join(args)
        return self.add_condition(f"{predicate}({args_str})")
    
    def add_not(self, condition):
        """Add a negated condition to the query."""
        return self.add_condition(f"not({condition})")
    
    def add_findall(self, template, goal, bag):
        """Add a findall statement to the query."""
        return self.add_condition(f"findall({template}, ({goal}), {bag})")
    
    def add_sort(self, list_to_sort, predicate, sorted_list):
        """Add a sort statement to the query."""
        return self.add_condition(f"sort({list_to_sort}, {predicate}, {sorted_list})")
    
    def build(self):
        """Build the complete query string."""
        return ", ".join(self.query_parts)
