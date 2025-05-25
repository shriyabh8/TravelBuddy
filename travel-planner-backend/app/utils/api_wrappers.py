from typing import List, Dict, Any, Optional
import overpy
import json
from geopy.geocoders import Nominatim

# OSM Tags mapping for different categories
OSM_TAGS = {
    "outdoors": [
        ("leisure", "park"),
        ("natural", "wood"),
        ("natural", "nature_reserve"),
        ("leisure", "garden")
    ],
    "adventure": [
        ("sport", "climbing"),
        ("route", "hiking"),
        ("tourism", "attraction"),
        ("leisure", "swimming_pool")
    ],
    "art": [
        ("tourism", "museum"),
        ("amenity", "gallery"),
        ("building", "church"),
        ("historic", "monument")
    ],
    "history": [
        ("historic", "monument"),
        ("historic", "castle"),
        ("historic", "ruins"),
        ("tourism", "museum")
    ],
    "food": [
        ("amenity", "restaurant"),
        ("amenity", "cafe"),
        ("amenity", "pub"),
        ("cuisine", "local")
    ],
    "architecture": [
        ("building", "church"),
        ("building", "cathedral"),
        ("building", "castle"),
        ("building", "palace")
    ],
    "nature": [
        ("natural", "wood"),
        ("natural", "water"),
        ("natural", "peak"),
        ("natural", "beach")
    ],
    "culture": [
        ("amenity", "library"),
        ("amenity", "theatre"),
        ("amenity", "cinema"),
        ("amenity", "museum")
    ],
    "entertainment": [
        ("amenity", "theatre"),
        ("amenity", "cinema"),
        ("amenity", "nightclub"),
        ("amenity", "casino")
    ]
}

def get_location_coordinates(location: str) -> Optional[Dict[str, float]]:
    """Get latitude and longitude for a given location name using geopy."""
    geolocator = Nominatim(user_agent="travel_buddy")
    location_data = geolocator.geocode(location)
    if location_data:
        return {
            "lat": location_data.latitude,
            "lon": location_data.longitude
        }
    return None

def build_overpass_query(lat: float, lon: float, radius: int, kinds: Optional[List[str]] = None) -> str:
    """Build an Overpass API query based on location and preferences."""
    if not kinds:
        # Default to popular tags if no kinds specified
        kinds = ["outdoors", "art", "history", "food"]
        
    query_parts = []
    for kind in kinds:
        if kind in OSM_TAGS:
            for tag_key, tag_value in OSM_TAGS[kind]:
                query_parts.append(f"node[\"{tag_key}\"=\"{tag_value}\"](around:{radius},{lat},{lon});")
                query_parts.append(f"way[\"{tag_key}\"=\"{tag_value}\"](around:{radius},{lat},{lon});")
                query_parts.append(f"relation[\"{tag_key}\"=\"{tag_value}\"](around:{radius},{lat},{lon});")
    
    query = """
[out:json][timeout:25];
(
    %s
);
out body center;
""" % ("\n    ".join(query_parts))
    return query

def fetch_osm_places(lat: float, lon: float, radius: int = 5000, kinds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch places from OpenStreetMap using Overpass API."""
    api = overpy.Overpass()
    query = build_overpass_query(lat, lon, radius, kinds)
    try:
        result = api.query(query)
        
        places = []
        for node in result.nodes:
            place = {
                "name": node.tags.get("name", "Unknown"),
                "description": node.tags.get("description", ""),
                "type": node.tags.get("amenity", node.tags.get("tourism", node.tags.get("leisure", ""))),
                "location": [node.lat, node.lon],
                "tags": list(node.tags.items()),
                "osm_id": node.id,
                "osm_type": "node"
            }
            places.append(place)
        
        # For ways, use the center point provided by Overpass
        for way in result.ways:
            if way.center_lat is not None and way.center_lon is not None:
                place = {
                    "name": way.tags.get("name", "Unknown"),
                    "description": way.tags.get("description", ""),
                    "type": way.tags.get("amenity", way.tags.get("tourism", way.tags.get("leisure", ""))),
                    "location": [way.center_lat, way.center_lon],
                    "tags": list(way.tags.items()),
                    "osm_id": way.id,
                    "osm_type": "way"
                }
                places.append(place)
        
        return places
        
    except Exception as e:
        print(f"Error fetching places: {str(e)}")
        return []

def fetch_places(location: str, kinds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch points of interest for a given location using OpenStreetMap."""
    coords = get_location_coordinates(location)
    if not coords:
        raise ValueError(f"Could not find coordinates for location: {location}")
        
    places = fetch_osm_places(
        lat=coords["lat"],
        lon=coords["lon"],
    )
    
    return places


if __name__ == "__main__":
    # Test with Paris and multiple categories
    print("Fetching places for Paris...")
    places = fetch_places("San Ramon", kinds=["outdoors"])
    print(f"\nFound {len(places)} places\n")
    
    # Display first 5 places with formatted output
    for place in places[:20]:
        print(f"Name: {place['name']}")
        print(f"Type: {place['type']}")
        print(f"Location: {place['location']}")
        if place['description']:
            print(f"Description: {place['description']}")
        print("Tags:")
        for key, value in place['tags']:
            print(f"  {key}={value}")
        print("-" * 50)