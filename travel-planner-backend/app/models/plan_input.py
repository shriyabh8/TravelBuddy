from pydantic import BaseModel, Field
from typing import Optional, List

class Location(BaseModel):
    city: str
    country: Optional[str] = None

class Theme(BaseModel):
    name: str
    weight: float = 1.0

class Budget(BaseModel):
    min: float = 0.0
    max: float = float('inf')
    currency: str = "USD"

class Preferences(BaseModel):
    themes: List[Theme]
    budget: Budget
    accommodation: Optional[str] = None
    dietary: Optional[str] = None
    activities: Optional[List[str]] = None
    constraints: Optional[List[str]] = None

class PlanInput(BaseModel):
    user_query: str
    preferences: Optional[Preferences] = None
    regenerate: Optional[bool] = False
    edit_part: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_query": "I want a 4-day trip to Paris with a mix of luxury and culture",
                "preferences": {
                    "themes": [
                        {"name": "luxury", "weight": 0.7},
                        {"name": "culture", "weight": 0.8}
                    ],
                    "budget": {
                        "min": 1000,
                        "max": 2000,
                        "currency": "USD"
                    },
                    "accommodation": "luxury",
                    "dietary": "vegetarian"
                }
            }
        }
