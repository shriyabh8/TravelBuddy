from time import thread_time_ns
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from app.utils.api_wrappers import fetch_places, OSM_TAGS
import logging

logger = logging.getLogger(__name__)

@dataclass
class POI:
    name: str
    description: str
    location: Tuple[float, float]
    type: str
    tags: List[Tuple[str, str]]
    osm_id: int
    osm_type: str
    relevance_score: float = 0.0
    theme_score: float = 0.0
    tag_score: float = 0.0
    matched_theme: str = ""
    price: Optional[float] = None  # Price in local currency
    luxury_level: Optional[str] = None  # 'basic', 'standard', 'luxury', 'premium'
    rating: Optional[float] = None  # 1-5 rating
    amenities: Optional[List[str]] = None  # List of amenities
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    duration: Optional[int] = None
    travel_time: Optional[int] = None
    time_to_next: Optional[int] = None
    distance_from_last: Optional[float] = None
    distance_to_next: Optional[float] = None
    distance_from_hotel: Optional[float] = None
    gap_until_next: Optional[int] = None

class POIAgent:
    def __init__(self, location: str, osm_tags: List[List[str]], budget: Optional[Dict[str, float]] = None):
        self.location = location
        self.osm_tags = osm_tags
        self.budget = budget
        self.themes = set()
        self.tag_to_theme = {
            # Entertainment
            "amenity=theatre": "entertainment",
            "amenity=cinema": "entertainment",
            "amenity=nightclub": "entertainment",
            "leisure=amusement_park": "entertainment",
            
            # Architecture
            "building=cathedral": "architecture",
            "building=church": "architecture",
            "building=mosque": "architecture",
            "building=temple": "architecture",
            "building=historical": "architecture",
            "historic=monument": "architecture",
            
            # Culture
            "amenity=museum": "culture",
            "amenity=library": "culture",
            "amenity=art_gallery": "culture",
            
            # Shopping
            "shop=mall": "shopping",
            "shop=retail": "shopping",
            
            # Food
            "amenity=restaurant": "food",
            "amenity=cafe": "food",
            "amenity=bar": "food",
            
            # Nature
            "leisure=park": "nature",
            "natural=wood": "nature",
            "natural=water": "nature",
            
            # Sports
            "leisure=sports_centre": "sports",
            "amenity=sports_centre": "sports",
            "leisure=stadium": "sports",
            
            # Adventure
            "tourism=attraction": "adventure",
            "leisure=park": "adventure",
            "natural=peak": "adventure"
        }

    def _normalize_theme_weights(self, themes: Union[List[str], Dict[str, float]]) -> Dict[str, float]:
        if isinstance(themes, list):
            n = len(themes)
            return {theme.lower(): 1.0 / n for theme in themes}
        total = sum(themes.values())
        return {theme.lower(): weight / total for theme, weight in themes.items()}

    def _get_theme_from_tags(self, tags: List[Tuple[str, str]]) -> str:
        """Get the most relevant theme from a list of tags."""
        themes = set()
        for tag in tags:
            key_value = f"{tag[0]}={tag[1]}"
            if key_value in self.tag_to_theme:
                themes.add(self.tag_to_theme[key_value])
            
            # Handle special cases
            if tag[0] == "amenity" and tag[1] in ["restaurant", "cafe", "bar"]:
                themes.add("food")
            elif tag[0] == "building" and tag[1] in ["church", "mosque", "temple"]:
                themes.add("architecture")
            elif tag[0] == "shop" and tag[1] in ["mall", "retail"]:
                themes.add("shopping")
            elif tag[0] == "leisure" and tag[1] in ["park", "sports_centre", "stadium"]:
                themes.add("nature")
                themes.add("sports")
            elif tag[0] == "natural" and tag[1] in ["wood", "water"]:
                themes.add("nature")
            elif tag[0] == "tourism" and tag[1] == "attraction":
                themes.add("adventure")
        
        return sorted(themes)[0] if themes else "unknown"

    def _score_poi(self, poi: Dict[str, Any]) -> Tuple[float, str]:
        description = poi.get('description', '').lower()
        tags = poi.get('tags', [])
        
        # Calculate base score based on tags
        base_score = 0.0
        
        # Check for exact tag matches
        for tag_key, tag_value in tags:
            key_value = f"{tag_key}={tag_value}"
            if any(f"{t[0]}={t[1]}" == key_value for t in self.osm_tags):
                base_score += 0.5
            
            # Check for partial matches in description
            if tag_value.lower() in description:
                base_score += 0.3
            
            # Check for theme matches
            if key_value in self.tag_to_theme:
                theme = self.tag_to_theme[key_value]
                if theme in self.themes:
                    base_score += 0.2
        
        # Normalize score
        base_score = min(1.0, base_score)
        
        # Get theme from tags
        theme = self._get_theme_from_tags(tags)
        
        return base_score, theme

    def _filter_by_budget(self, poi: Dict[str, Any]) -> bool:
        if not self.budget:
            return True
        for k, v in poi.get('tags', []):
            if k in ['price', 'cost']:
                try:
                    return float(v) <= self.budget['max']
                except ValueError:
                    continue
        return True

    def get_pois(self, max_results: int = 10) -> List[POI]:
        """
        Get POIs based on user preferences.
        
        Args:
            max_results: Maximum number of POIs to return
            
        Returns:
            List of POI objects
        """
        try:
            # Fetch raw POIs from API
            raw_pois = fetch_places(self.location, kinds=self.osm_tags)
            
            if not raw_pois:
                return []
            
            # Convert raw POIs to our POI objects
            pois = []
            for raw_poi in raw_pois:
                # Get tags from raw POI
                tags = [(k, v) for k, v in raw_poi.get('tags', [])]
                
                # Calculate score based on tag matches
                score = 0.0
                for user_tag in self.osm_tags:
                    user_key_value = f"{user_tag[0]}={user_tag[1]}"
                    for poi_tag in tags:
                        poi_key_value = f"{poi_tag[0]}={poi_tag[1]}"
                        if user_key_value == poi_key_value:
                            score += 1.0
                        elif user_tag[0] == poi_tag[0]:  # Partial match on key
                            score += 0.5
                
                # Get rating and price information
                rating = None
                price = None
                for k, v in raw_poi.get('tags', []):
                    if k == 'rating':
                        try:
                            rating = float(v)
                        except ValueError:
                            pass
                    elif k == 'price':
                        try:
                            price = float(v)
                        except ValueError:
                            pass
                
                # Create POI object
                poi = POI(
                    name=raw_poi.get('name', 'Unknown'),
                    description=raw_poi.get('description', ''),
                    location=(raw_poi.get('lat', 0.0), raw_poi.get('lon', 0.0)),
                    type=tags[0][0] if tags else 'unknown',  # Use first tag's key as type
                    tags=tags,
                    osm_id=raw_poi.get('id', 0),
                    osm_type=raw_poi.get('type', ''),
                    relevance_score=score,
                    theme_score=score,
                    tag_score=score,
                    matched_theme=tags[0][0] if tags else '',  # Use first tag's key as theme
                    rating=rating,
                    price=price
                )
                
                # Filter by budget if specified
                if self.budget and price and price > self.budget['max']:
                    continue
                
                pois.append(poi)
            
            # Sort by relevance score (higher is better)
            pois = sorted(pois, key=lambda p: p.relevance_score, reverse=True)
            # If we have fewer than max_results, return all
            return pois[:max_results]
            
        except Exception as e:
            logger.error(f"Error fetching POIs: {str(e)}")
            return []

if __name__ == "__main__":
    # Example OSM tags for parks and restaurants
    osm_tags = [
        ["leisure", "park"],
        ["amenity", "restaurant"],
        ["cuisine", "indian"]
    ]
    
    poi_agent = POIAgent(
        location="Vancouver",
        osm_tags=osm_tags,
        budget={"min": None, "max": None}
    )
    pois = poi_agent.get_pois(max_results=20)
    print(f"\nFound {len(pois)} recommended POIs\n")
    for poi in pois:
        print(f"Name: {poi.name}")
        print(f"Theme: {poi.matched_theme}")
        print(f"Tags: {poi.tags}")
        print("-" * 40)
        print(f"Type: {poi.type}")
        print(f"Location: {poi.location}")
        if poi.description:
            print(f"Description: {poi.description}")
        print(f"Theme Score: {poi.theme_score:.2f}")
        print(f"Matched Theme: {poi.matched_theme}")
        print(f"Relevance Score: {poi.relevance_score:.2f}")
        print(f"Tag Score: {poi.tag_score:.2f}")
        
        # Print additional information
        if poi.price is not None:
            print(f"Price: {poi.price}")
        if poi.luxury_level:
            print(f"Luxury Level: {poi.luxury_level}")
        if poi.rating is not None:
            print(f"Rating: {poi.rating:.1f}")
        if poi.amenities:
            print("Amenities:")
            for amenity in poi.amenities:
                print(f"  {amenity}")
        
        print("Tags:")
        for key, value in poi.tags:
            print(f"  {key}={value}")
        print("-" * 50)
