import logging
import google.generativeai as genai
import os
import dotenv
dotenv.load_dotenv() 
logger = logging.getLogger(__name__)

def edit_itinerary(itinerary_json: dict, user_message: str, preferences: dict):
    system_prompt = """
You are an autonomous travel itinerary editor.

Your job is to take a JSON itinerary and a user instruction, then return an updated itinerary JSON in the same structure.

Rules:
1. DO NOT ask the user for more info. You must make reasonable assumptions.
2. Only update fields the user asked to change.
3. Preserve the overall structure of the itinerary.
4. Your output must be a single valid JSON object, and nothing else.
5. If the user is vague (e.g. "add a restaurant"), invent a realistic, relevant entry.
6. Do not repeat or explain anything. Output only JSON.
{preferences}

The itinerary must always follow this format exactly:
{
  "day_1": {
    "activities": [ ... ],
    "meals": [ ... ]
  },
  "day_2": { ... },
  "day_3": { ... }
}
"""

    prompt = f"""
Here is the current itinerary in JSON format:

{itinerary_json}

Please apply the following user request:

"{user_message}"
"""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        agent = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
        updated = agent.generate_content(system_prompt + prompt)
        return updated.text
    except Exception as e:
        logger.error(f"Edit failed: {e}")
        return str(e)

# if __name__ == "__main__":
#     itinerary_json = {"day_1": {"activities": [{"name": "Mus\u00e9e de l'Arm\u00e9e", "price": None, "duration": "99 minutes", "website": "http://www.musee-armee.fr/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Mus\u00e9e de l'Assistance Publique H\u00f4pitaux de Paris", "price": None, "duration": "99 minutes", "website": "https://www.aphp.fr/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Mus\u00e9e des Arts D\u00e9coratifs - Mus\u00e9e de la Publicit\u00e9", "price": None, "duration": "99 minutes", "website": "https://madparis.fr/musee-des-arts-decoratifs", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Mus\u00e9e des Arts et M\u00e9tiers", "price": None, "duration": "99 minutes", "website": "https://www.arts-et-metiers.net/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}], "meals": [{"name": "Le Petit March\u00e9 (Fixed Breakfast)", "price": None, "duration": "60 minutes", "website": None, "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Le Caf\u00e9 Marly", "price": "Free", "duration": "60 minutes", "website": "https://cafe-marly.com/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "L\u00e9moni Caf\u00e9", "price": "Free", "duration": "60 minutes", "website": "https://www.lemonicafe.fr", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}]}, "day_2": {"activities": [{"name": "Tour de Jean-sans-Peur", "price": None, "duration": "99 minutes", "website": "http://www.tourjeansanspeur.com/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Mus\u00e9e national Gustave Moreau", "price": None, "duration": "99 minutes", "website": "https://musee-moreau.fr/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Mus\u00e9e Gr\u00e9vin", "price": None, "duration": "99 minutes", "website": "https://www.grevin.com/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Mus\u00e9e Edith Piaf", "price": None, "duration": "99 minutes", "website": "https://www.parisinfo.com/musee-monument-paris/71402/Musee-Edith-Piaf", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}], "meals": [{"name": "Mac\u00e9o (Fixed Breakfast)", "price": None, "duration": "60 minutes", "website": "https://www.maceorestaurant.com", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Les Enfants Rouges", "price": "Free", "duration": "60 minutes", "website": None, "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "The Village Terrazza", "price": "Free", "duration": "60 minutes", "website": None, "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}]}, "day_3": {"activities": [{"name": "Mus\u00e9e Pasteur", "price": None, "duration": "99 minutes", "website": "https://www.pasteur.fr/fr/institut-pasteur/musee-pasteur", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Espace Dali", "price": None, "duration": "99 minutes", "website": "https://www.daliparis.com/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Maison de Victor Hugo", "price": None, "duration": "99 minutes", "website": "https://www.paris.fr/musees/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Maison Europ\u00e9enne de la Photographie", "price": None, "duration": "99 minutes", "website": "https://www.mep-fr.org/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}], "meals": [{"name": "O' Sci\u00e0 (Fixed Breakfast)", "price": None, "duration": "60 minutes", "website": "https://www.pizzeriaoscia.fr/", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "L\u00e9moni Caf\u00e9", "price": "Free", "duration": "60 minutes", "website": "https://www.lemonicafe.fr", "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}, {"name": "Rani Mahal", "price": "Free", "duration": "60 minutes", "website": None, "description": "", "amenities": [], "rating": None, "location": [0.0, 0.0]}]}, "total_price": "$0.00"}
#     preferences = {'osm_tags': [['tourism', 'museum']], 'budget': {'min': None, 'max': None}, 'accommodation': None, 'dietary': None, 'activities': ['Travel to Paris', 'Visit museums'], 'constraints': [], 'themes': []}``
#     user_message = "I want to add a restaurant to day 2"
#     print(edit_itinerary(itinerary_json, user_message, preferences))