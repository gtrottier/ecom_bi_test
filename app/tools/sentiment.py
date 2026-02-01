import random
from langchain_core.tools import tool

from app.schema import ToolResult


@tool
def analyze_sentiment(
    product_name: str,
) -> ToolResult:
    """
    Analyse les avis clients sur le produit
    Cet outil pourrait faire appel à des plateformes externes pour récupérer les avis clients
    """
    try:
        sentiment_score = random.randint(0, 5)  # étoiles

        themes = [
            "battery life",
            "customer support",
            "price/value",
            "durability",
            "design",
            "shipping speed",
        ]
        positive_themes = random.sample(themes, 2)
        negative_themes = random.sample(
            [t for t in themes if t not in positive_themes], 2
        )

        sentiment_label = "Neutral"
        if sentiment_score > 0.3:
            sentiment_label = "Positive"
        elif sentiment_score < -0.3:
            sentiment_label = "Negative"

        data = {
            "product": product_name,
            "overall_sentiment": sentiment_label,
            "sentiment_score": round(sentiment_score, 2),
            "total_mentions": random.randint(1000, 50000),
            "key_positives": positive_themes,
            "key_negatives": negative_themes,
            # Ici on pourrait retourner des insights provenant d'autres outils/fonctions etc plus complexes
            "insights": "Un vrai insight",
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": str(e) if e else "Unknown error",
            "retryable": False,
        }
    return {"status": "ok", "data": data}
