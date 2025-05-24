from typing import Dict, Any
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
            "themes",
            "budget",
            "accommodation",
            "dietary",
            "activities",
            "constraints"
        ]
        
        # Define system prompt
        self.system_prompt = """
        You are a travel preferences parser. The user will provide their preferences for a trip.
        Extract ONLY the following information from their input:
        1. Themes (e.g., food, culture, adventure)
        2. Budget preferences
        3. Accommodation preferences
        4. Dietary restrictions
        5. Specific activities
        6. Special constraints
        
        Return the information in JSON format with these fields. Just provide the JSON object:
        {
            "themes": [list of themes],
            "budget": {"min": float, "max": float},
            "accommodation": "preference",
            "dietary": "restrictions",
            "activities": [list of activities],
            "constraints": [list of constraints]
        }
        """

    def extract(self, user_input: str) -> dict[str, Any]:
        # Add explicit instruction for JSON format
        prompt = [
            {"role": "user", "parts": [self.system_prompt, user_input]}
        ]
        
        response = self.gemini.generate_content(prompt).text
        response = response[response.index('{'):response.rindex('}')+1]
        preferences = json.loads(response)
        return self._normalize_preferences(preferences)
    
        

    def _normalize_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate the extracted preferences.
        """
        normalized = {}
        
        # Normalize themes and activities
        for field in ['themes', 'activities', 'constraints']:
            value = preferences.get(field, [])
            normalized[field] = [value] if not isinstance(value, list) else value
            
        # Normalize budget
        value = preferences.get('budget', {'min': 0, 'max': float('inf')})
        normalized['budget'] = {'min': float(value), 'max': float(value)} if not isinstance(value, dict) else value
            
        # Normalize string fields
        for field in ['accommodation', 'dietary']:
            value = preferences.get(field, '')
            normalized[field] = value.lower() if isinstance(value, str) else ''
            
        return normalized

    def _handle_error(self, user_input: str) -> Dict[str, Any]:
        """
        Handle errors by attempting to extract basic information using a fallback method.
        """
        # Try a simpler prompt if structured parsing fails
        simple_prompt = """
        Extract only travel preferences from this input:
        {user_input}
        Return ONLY the JSON object with these fields ready for me to use json.loads on the output:
        {
            "themes": ["food", "culture"],
            "budget": {"min": 1000, "max": 2000},
            "accommodation": "luxury",
            "dietary": "vegetarian",
            "activities": ["museums", "shopping"],
            "constraints": ["no early mornings"]
        }
        """
        print(simple_prompt)
        
        # Generate content with simpler prompt
        response = self.gemini.generate_content(simple_prompt.format(user_input=user_input))
        
        # Get all text parts from the response
        text_response = ''
        for part in response.text:
            if isinstance(part, str):
                text_response += part
        
        # Try direct JSON parsing
        preferences = json.loads(text_response)
        return self._normalize_preferences(preferences)

    def _generate_default_preferences(self, user_input: str) -> Dict[str, Any]:
        """
        Generate default preferences when all else fails.
        """
        # Try to extract basic information using simple keyword matching
        themes = self._extract_themes(user_input)
        dietary = self._extract_dietary(user_input)
        
        return {
            "themes": themes or ["general"],
            "budget": {"min": 1000, "max": 5000},
            "accommodation": "standard",
            "dietary": dietary or "none",
            "activities": ["sightseeing"],
            "constraints": []
        }

    def _extract_themes(self, text: str) -> list[str]:
        """
        Extract themes from text using simple keyword matching.
        """
        theme_keywords = {
            "food": ["food", "cuisine", "eat", "dine"],
            "culture": ["culture", "art", "museum", "history"],
            "adventure": ["adventure", "outdoor", "hike", "explore"],
            "luxury": ["luxury", "high-end", "premium", "fancy"]
        }
        
        themes = []
        for theme, keywords in theme_keywords.items():
            if any(keyword.lower() in text.lower() for keyword in keywords):
                themes.append(theme)
        
        return themes

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
    print(goal_agent.extract("I want to go to Paris for 5 days and I want to eat French food."))
