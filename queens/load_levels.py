"""
Level loader for the Queens puzzle.

Reads and validates puzzle definitions from a JSON file.
"""

import json
import os
from typing import List, Tuple
from queens.board import Level

def load_levels(filepath: str = "levels.json") -> List[Tuple[str, Level]]:
    """
    Reads levels from a JSON file and instantiates them.
    
    Since Level.__init__ automatically calls self._validate(), 
    all levels are strictly validated for dimensions, IDs, and 
    region connectedness the moment they are loaded.
    """
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Returning empty level list.")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    loaded_levels = []
    
    for i, level_data in enumerate(data.get("levels", [])):
        name = level_data.get("name", f"Level {i + 1}")
        size = level_data.get("size")
        regions = level_data.get("regions")
        
        try:
            level_obj = Level(size, regions)
            loaded_levels.append((name, level_obj))
        except ValueError as e:
            print(f"Failed to validate '{name}': {e}")
            raise  # Fail fast at startup if a level is invalid
            
    return loaded_levels