from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.models.plan_input import PlanInput
from app.models.plan_output import PlanOutput
from app.agents import GoalAgent, POIAgent, SchedulerAgent, RestaurantAgent, HotelAgent, SummaryAgent

router = APIRouter()

class PlanRequest(BaseModel):
    user_query: str
    diet: Optional[str] = "none"
    price_range: Optional[str] = "medium"
    regenerate: Optional[bool] = False
    edit_part: Optional[str] = None

class PlanResponse(BaseModel):
    itinerary: str
    details: dict

@router.post("/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    try:
        # Step 1: Goal Understanding
        goal_agent = GoalAgent()
        goal = goal_agent.extract(request.user_query)
        
        # Step 2: Get Points of Interest
        poi_agent = POIAgent(goal['location'], goal['themes'])
        pois = poi_agent.get_pois()
        
        # Step 3: Schedule activities
        scheduler = SchedulerAgent()
        weather = ["clear", "rain", "clear"][:goal["days"]]
        schedule = scheduler.schedule(pois, goal["days"], weather)
        
        # Step 4: Find restaurants
        restaurant_agent = RestaurantAgent()
        restaurants = restaurant_agent.find_nearby(pois, request.diet)
        
        # Step 5: Find hotel
        hotel_agent = HotelAgent()
        hotel = hotel_agent.find_hotel(goal["location"], request.price_range)
        
        # Step 6: Generate summary
        summary_agent = SummaryAgent()
        summary = summary_agent.summarize(schedule, hotel, restaurants)
        
        return {
            "itinerary": summary,
            "details": {
                "goal": goal,
                "schedule": schedule,
                "restaurants": restaurants,
                "hotel": hotel
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
