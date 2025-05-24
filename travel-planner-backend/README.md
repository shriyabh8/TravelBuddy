# Travel Planner Backend

A FastAPI-based backend for generating personalized travel itineraries using AI agents.

## Features

- Goal Understanding Agent: Converts natural language preferences into structured data
- POI Agent: Finds and ranks points of interest based on user preferences
- Scheduler Agent: Creates optimized daily schedules
- Restaurant Agent: Finds suitable dining options
- Hotel Agent: Recommends accommodations
- Summary Agent: Generates natural language itineraries

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_api_key_here
GOOGLE_PLACES_API_KEY=your_api_key_here
YELP_API_KEY=your_api_key_here
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST /api/plan
Generate a travel itinerary based on user preferences.

Request Body:
```json
{
    "user_query": "I want a 4-day foodie trip to Tokyo with a mix of luxury and culture",
    "diet": "vegetarian",
    "price_range": "high",
    "regenerate": false,
    "edit_part": null
}
```

Response:
```json
{
    "itinerary": "Your personalized itinerary...",
    "details": {
        "schedule": [...],
        "restaurants": [...],
        "hotel": {...}
    }
}
```

## Development

The project follows a modular architecture with separate agents for each functionality:

```
app/
├── agents/           # AI agents for different tasks
├── models/          # Pydantic models for data validation
├── routes/          # API route definitions
└── utils/          # Helper functions and utilities
```

Each agent is designed to be independent and can be tested individually.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
