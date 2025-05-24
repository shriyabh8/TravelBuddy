from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class POI(BaseModel):
    name: str
    location: str
    category: str
    description: str
    rating: Optional[float] = None
    opening_hours: Optional[List[str]] = None

class Restaurant(BaseModel):
    name: str
    cuisine: str
    price_range: str
    rating: Optional[float] = None
    dietary_options: List[str]
    location: str

class Hotel(BaseModel):
    name: str
    location: str
    rating: float
    price_range: str
    amenities: List[str]

class DailySchedule(BaseModel):
    morning: List[POI]
    afternoon: List[POI]
    evening: List[POI]
    dinner: Optional[Restaurant] = None

class PlanOutput(BaseModel):
    summary: str
    schedule: List[DailySchedule]
    hotel: Hotel
    restaurants: List[Restaurant]
    
    class Config:
        schema_extra = {
            "example": {
                "summary": "4-day luxury trip to Paris with cultural experiences...",
                "schedule": [
                    {
                        "morning": [
                            {"name": "Louvre Museum", "category": "museum"}
                        ],
                        "afternoon": [
                            {"name": "Eiffel Tower", "category": "landmark"}
                        ],
                        "evening": [
                            {"name": "Champs-Élysées", "category": "shopping"}
                        ],
                        "dinner": {
                            "name": "Le Jules Verne",
                            "cuisine": "French"
                        }
                    }
                ],
                "hotel": {
                    "name": "Shangri-La Hotel",
                    "rating": 5.0
                },
                "restaurants": [
                    {
                        "name": "Le Meurice",
                        "cuisine": "French",
                        "rating": 4.8
                    }
                ]
            }
        }
