from typing import Dict, Any, List
import json
import logging
import google.generativeai as genai
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class GoalAgent:
    """
    Goal Understanding Agent that extracts structured travel preferences from user input.
    
    Uses Google Gemini API to parse user preferences while place and date are handled by selection menus.
    """
    
    def __init__(self):
        """
        Initialize the GoalAgent with Gemini API.
        """
        # Load environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.gemini = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
        
        # Define response schemas
        self.response_schemas = [
            "osm_tags",
            "budget",
            "accommodation",
            "dietary",
            "activities",
            "constraints"
        ]
        
        # Define system prompt
        self.system_prompt = """
You are an OpenStreetMap (OSM) tag extractor and travel preferences parser.

Given a user's natural language description of what they want to do or see,
return a list of relevant (key, value) tag pairs from OpenStreetMap's tag system.

Only return key-value pairs that exist in OpenStreetMap, like:
- ("shop", "mall")
- ("building", "cathedral")
- ("tourism", "attraction")

Also extract any budget, accommodation, dietary, activity, and constraint preferences.

Return the information in JSON format with these fields:
{{
    "osm_tags": [["key", "value"], ["key", "value"]],
    "budget": {{"min": float, "max": float}},
    "accommodation": "preference",
    "dietary": "restrictions",
    "activities": [list of activities],
    "constraints": [list of constraints]
}}

Example input: "I want to explore the malls in Hyderabad. I also want to see architectural buildings."
Example output:
{{
    "osm_tags": [
        ["shop", "mall"],
        ["building", "retail"],
        ["building", "cathedral"],
        ["building", "palace"],
        ["tourism", "attraction"]
    ],
    "budget": {{"min": null, "max": null}},
    "accommodation": null,
    "dietary": null,
    "activities": ["Explore malls in Hyderabad", "See architectural buildings"],
    "constraints": []
}}

Now process this user input:
{user_input}
"""

            


    def extract(self, user_input: str) -> Dict[str, Any]:
        """
        Extract user preferences from natural language input.
        
        Args:
            user_input: User's natural language description of preferences
            
        Returns:
            Dictionary containing extracted preferences
        """
        try:
            # Format the prompt with user input
            prompt = self.system_prompt.format(user_input=user_input)
            
            # Get response from Gemini
            response = self.gemini.generate_content(prompt)
            
            # Get text content from response
            if hasattr(response, 'text') and isinstance(response.text, str):
                text = response.text.strip()
                
                # Find and extract JSON object
                # Look for the first { and last }
                start_idx = text.find('{')
                end_idx = text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    # Extract JSON string
                    json_str = text[start_idx:end_idx]
                    
                    # Parse JSON
                    try:
                        data = json.loads(json_str)
                        
                        # Validate response schema
                        for field in self.response_schemas:
                            if field not in data:
                                raise ValueError(f"Missing required field: {field}")
                        
                        # Extract themes from OSM tags
                        data['themes'] = self._extract_themes_from_tags(data['osm_tags'])
                        
                        # Return the data
                        return data
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON response: {json_str}")
                        raise ValueError("Failed to parse JSON response")
                else:
                    raise ValueError("No JSON object found in response")
            
            raise ValueError("Invalid response format from Gemini")
            
        except Exception as e:
            logger.error(f"Error extracting preferences: {str(e)}")
            raise

    def _extract_themes_from_tags(self, osm_tags: List[List[str]]) -> List[str]:
        """
        Extract themes from OSM tags.
        
        Args:
            osm_tags: List of [key, value] pairs representing OSM tags
            
        Returns:
            List of theme strings
        """
        themes = set()
        
        # Define theme mappings
        theme_mappings = {
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
        
        # Extract themes from tags
        for tag in osm_tags:
            key_value = f"{tag[0]}={tag[1]}"
            if key_value in theme_mappings:
                themes.add(theme_mappings[key_value])
            
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
        
        return list(themes)
    
        


        # Define themes based on OSM_TAGS structure
        theme_keywords = {
            "outdoors": ["park", "wood", "nature", "garden"],
            "adventure": ["climbing", "hiking", "attraction", "swimming"],
            "art": ["museum", "gallery", "church", "monument"],
            "history": ["monument", "castle", "ruins", "museum"],
            "food": ["restaurant", "cafe", "pub", "cuisine"],
            "architecture": ["church", "cathedral", "castle", "palace"],
            "nature": ["wood", "water", "peak", "beach"],
            "culture": ["library", "theatre", "cinema", "museum"],
            "entertainment": ["theatre", "cinema", "nightclub", "casino"]
        }
        
        # Split text into words and process each one
        words = text.lower().split()
        themes = set()  # Use set to avoid duplicates
        
        for word in words:
            # First check if word matches any OSM-related keywords
            matched_theme = None
            for theme, keywords in theme_keywords.items():
                if any(kw in word for kw in keywords):
                    themes.add(theme)
                    matched_theme = theme
                    break
            
            # If no keyword match, try to map to OSM tags
            if not matched_theme:
                # Try to map common words to OSM tags
                if "museum" in word:
                    themes.add("art")
                    themes.add("history")
                    themes.add("culture")
                elif "park" in word:
                    themes.add("outdoors")
                    themes.add("nature")
                elif "church" in word:
                    themes.add("art")
                    themes.add("architecture")
                elif "food" in word or "eat" in word:
                    themes.add("food")
                elif "explore" in word or "tour" in word:
                    # Use Gemini to determine appropriate themes for sightseeing activities
                    prompt = f"""
                    This is a travel preference parser. For the word '{word}',
                    determine which of these themes are most appropriate:
                    {', '.join(theme_keywords.keys())}
                    
                    Explain why each theme fits and provide a confidence score (1-5) for each theme.
                    Format your response as JSON:
                    {{
                        "themes": [
                            {{"theme": "theme_name", "reason": "why it fits", "score": 3}},
                            {{"theme": "theme_name", "reason": "why it fits", "score": 3}}
                        ]
                    }}
                    """
                    response = self.gemini.generate_content(prompt)
                    try:
                        # Extract JSON from response
                        start_idx = response.text.find('{')
                        end_idx = response.text.rfind('}') + 1
                        json_str = response.text[start_idx:end_idx]
                        suggestions = json.loads(json_str)
                        
                        # Add themes with score >= 3
                        for suggestion in suggestions['themes']:
                            if suggestion['score'] >= 3:
                                themes.add(suggestion['theme'])
                    except:
                        # If JSON parsing fails, use default mapping
                        themes.add("culture")  # Most sightseeing is cultural
                        themes.add("nature")   # Many tours involve nature
            
            # If still no match, ask Gemini
            if not matched_theme:
                prompt = f"""
                This is a travel preference parser. For the word '{word}',
                determine which of these themes are most appropriate:
                {', '.join(theme_keywords.keys())}
                
                Explain why each theme fits and provide a confidence score (1-5) for each theme.
                Format your response as JSON:
                {{
                    "themes": [
                        {{"theme": "theme_name", "reason": "why it fits", "score": 3}},
                        {{"theme": "theme_name", "reason": "why it fits", "score": 3}}
                    ]
                }}
                """
                response = self.gemini.generate_content(prompt)
                try:
                    # Extract JSON from response
                    start_idx = response.text.find('{')
                    end_idx = response.text.rfind('}') + 1
                    json_str = response.text[start_idx:end_idx]
                    suggestions = json.loads(json_str)
                    
                    # Add themes with score >= 3
                    for suggestion in suggestions['themes']:
                        if suggestion['score'] >= 3:
                            themes.add(suggestion['theme'])
                except:
                    # If JSON parsing fails, use a default
                    themes.add("culture")  # Most travel activities are cultural
        
        # Convert set to list and ensure we have at least one theme
        themes_list = list(themes)
        if not themes_list:
            themes_list = ["culture"]  # Fallback to culture if no themes found
        
        return themes_list

    def _extract_dietary(self, text: str) -> str:
        """
        Extract dietary preferences from text using simple keyword matching.
        """
        dietary_keywords = {
            "vegetarian": ["vegetarian", "veggie", "no meat"],
            "vegan": ["vegan", "plant-based", "no animal products"],
            "gluten-free": ["gluten-free", "no gluten"],
            "keto": ["keto", "ketogenic", "low carb"]
        }
        
        for pref, keywords in dietary_keywords.items():
            if any(keyword.lower() in text.lower() for keyword in keywords):
                return pref
        
        return "none"

if __name__ == "__main__":
    goal_agent = GoalAgent()
    print(goal_agent.extract("I want to explore to Vancouver, Stanley park, Indian food."))
