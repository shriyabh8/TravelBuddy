from typing import List, Dict, Any, Optional
import logging
from app.utils.api_wrappers import fetch_places
from app.utils.embeddings import cosine_similarity
from app.utils.embeddings import get_embedding

logger = logging.getLogger(__name__)

class POIAgent:
    def __init__(self, location: str, themes: List[str], budget: Optional[Dict[str, float]] = None):
        """
        POI Recommendation Agent that fetches and ranks points of interest based on user preferences.
        
        Args:
            location: Destination city/country
            themes: List of user's interest themes (e.g., ['food', 'culture', 'adventure'])
            budget: Optional budget dictionary with min/max values
        """
        self.location = location
        self.themes = themes
        self.budget = budget
        self.theme_embeddings = self._get_theme_embeddings()

    def _get_theme_embeddings(self) -> List[List[float]]:
        """Get embeddings for all user themes."""
        return [get_embedding(theme) for theme in self.themes]

    def get_pois(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch and rank POIs based on user preferences.
        
        Args:
            max_results: Maximum number of POIs to return
            
        Returns:
            List of ranked POIs with additional scoring information
        """
        try:
            pois = fetch_places(self.location)
            ranked = self.rank_by_theme(pois)
            return ranked[:max_results]
        except Exception as e:
            logger.error(f"Error fetching POIs: {str(e)}")
            raise

    def rank_by_theme(self, pois: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank POIs by relevance to user themes using cosine similarity.
        
        Args:
            pois: List of POI dictionaries with 'name', 'description', and 'price' fields
            
        Returns:
            List of POIs sorted by relevance score
        """
        def calculate_score(poi: Dict[str, Any]) -> float:
            """Calculate relevance score for a POI based on themes and budget."""
            poi_emb = get_embedding(poi['description'])
            theme_scores = [cosine_similarity(poi_emb, theme_emb) for theme_emb in self.theme_embeddings]
            theme_score = max(theme_scores) if theme_scores else 0.0
            
            # Apply budget filter if provided
            if self.budget:
                price = poi.get('price', 0)
                if price < self.budget['min'] or price > self.budget['max']:
                    return 0.0
            
            return theme_score

        # Add scores and sort POIs
        ranked_pois = [{**poi, 'relevance_score': calculate_score(poi)} for poi in pois]
        return sorted(ranked_pois, key=lambda x: x['relevance_score'], reverse=True)

    def get_theme_embeddings(self) -> List[List[float]]:
        """Get the embeddings for the user's themes."""
        return self.theme_embeddings

if __name__ == "__main__":
    poi_agent = POIAgent("New York", ["food", "culture", "adventure"])
    print(poi_agent.get_pois()) 