from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import random

load_dotenv()

class APIError(Exception):
    """Exception raised for API-related errors."""
    pass

def fetch_places(location: str) -> List[Dict[str, Any]]:
    """
    Fetch trending points of interest (POIs) for a given location.
    
    Args:
        location: The destination city/country name
        
    Returns:
        List of POI dictionaries with the following structure:
        - name: str
        - description: str
        - type: str (category of POI)
        - location: list[float] (latitude, longitude)
        - rating: float (optional)
        - price: float (optional)
        - tags: list[str] (optional)
    
    Raises:
        APIError: If there's an error fetching POIs
    """
    try:
        # Mock data with some variety
        pois = [
            {
                "name": f"{location} Fish Market",
                "description": "Famous seafood market with fresh catches",
                "type": "food",
                "location": [random.uniform(35, 36), random.uniform(139, 140)],
                "rating": random.uniform(4.0, 5.0),
                "price": random.uniform(10, 50),
                "tags": ["food", "market", "local"]
            },
            {
                "name": f"{location} Historical Museum",
                "description": "Comprehensive museum showcasing local history",
                "type": "culture",
                "location": [random.uniform(35, 36), random.uniform(139, 140)],
                "rating": random.uniform(4.0, 5.0),
                "price": random.uniform(10, 20),
                "tags": ["culture", "museum", "history"]
            },
            {
                "name": f"{location} Central Park",
                "description": "Large urban park with walking trails and gardens",
                "type": "nature",
                "location": [random.uniform(35, 36), random.uniform(139, 140)],
                "rating": random.uniform(4.0, 5.0),
                "price": 0.0,
                "tags": ["nature", "outdoor", "free"]
            },
            {
                "name": f"{location} Art Gallery",
                "description": "Modern art gallery featuring local artists",
                "type": "art",
                "location": [random.uniform(35, 36), random.uniform(139, 140)],
                "rating": random.uniform(4.0, 5.0),
                "price": random.uniform(10, 30),
                "tags": ["art", "culture", "gallery"]
            },
            {
                "name": f"{location} Main Street",
                "description": "Popular shopping district with local boutiques",
                "type": "shopping",
                "location": [random.uniform(35, 36), random.uniform(139, 140)],
                "rating": random.uniform(4.0, 5.0),
                "price": random.uniform(20, 100),
                "tags": ["shopping", "local", "boutique"]
            }
        ]
        
        # Add some randomness to make it more realistic
        return random.sample(pois, len(pois))
        
    except Exception as e:
        raise APIError(f"Failed to fetch places: {str(e)}")
