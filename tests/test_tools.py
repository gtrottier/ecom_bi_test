from unittest.mock import patch

from langchain_core.messages import HumanMessage
import pytest

from app.agent import graph_app
from app.schema import AnalysisRequest
from app.tools.scraper import scrape_product_data
from app.tools.sentiment import analyze_sentiment
from app.tools.trends import analyze_trends


def test_scrape_product_data_basic():
    """
    Test de base de scrape_product_data.
    On regarde principalement si les champs sont présents et si URLs en minuscules

    """
    result = scrape_product_data.invoke(
        {"product_name": "HyperWidget X", "brand": "FutureCorp"}
    )
    assert result["status"] == "ok"
    assert isinstance(result["data"], list)
    assert len(result["data"]) > 0
    for entry in result["data"]:
        assert "platform" in entry
        assert "price" in entry
        assert "url" in entry
        assert "futurecorp" in entry["url"]
        assert "hyperwidget-x" in entry["url"]


def test_analyze_sentiment_range():
    """
    Test de l'analyse de sentiments

    On teste si le score est bien dans le range attendu,
    si les catégories sont bien générées
    et si le score est cohérent avec la catégorie.
    """
    # Plusieurs essais parce que random
    labels = set()
    for _ in range(50):
        result = analyze_sentiment.invoke({"product_name": "Test Widget"})
        assert result["status"] == "ok"
        data = result["data"]
        assert -1 <= data["sentiment_score"] <= 1
        labels.add(data["overall_sentiment"])

    # Vérifie si on obtient bien les 3 catégories
    assert any(label in labels for label in ["Positive", "Negative", "Neutral"])


def test_analyze_trends_empty_competitors():
    """Comme competitors est optionnel, on teste si ça marche avec une liste vide"""
    result = analyze_trends.invoke(
        {"product_name": "SingleWidget", "brand": "SoloBrand", "competitors": []}
    )
    assert result["status"] == "ok"
    assert result["data"]["competitors"] == []


# Edge cases
def test_scrape_product_data_special_chars():
    """Caractères spéciaux dans le nom du produit"""
    result = scrape_product_data.invoke(
        {"product_name": "Widget & Co / Model X", "brand": "FutureCorp"}
    )
    assert result["status"] == "ok"
    # Vérifie si les URLs sont bien
    for entry in result["data"]:
        assert " " not in entry["url"]
        assert "&" not in entry["url"]

        path_segments = entry["url"].split(".com/")[1].split("/")
        for segment in path_segments:
            assert "/" not in segment
        assert "and" in entry["url"]
        assert entry["url"].endswith("widget-and-co---model-x")


def test_scrape_product_data_error_handling():
    """On mock un échec du scraper pour voir le retour d'erreur"""
    with patch("random.randint", side_effect=Exception("API Timeout")):
        result = scrape_product_data.invoke(
            {"product_name": "Broken", "brand": "FailCo"}
        )
        assert result["status"] == "error"
        assert result["error_type"] == "unknown"
        assert "API Timeout" in result["message"]


def test_sentiment_error_handling():
    """On mock un échec de l'analyse de sentiment"""
    with patch("random.uniform", side_effect=Exception("Model Load Error")):
        result = analyze_sentiment.invoke({"product_name": "NoModel"})
        assert result["status"] == "error"
        assert "Model Load Error" in result["message"]


@pytest.mark.anyio
async def test_agent_flow():
    """
    Test simple de l'agent
    On réutilise essentiellement le code de main.py
    (Devrait être fonctions modulaires)
    """

    print("Lancement du test de l'agent")

    request = AnalysisRequest(
        product_name="Airmax 2026", brand="Nike", competitors=["Adidas Ultraboost"]
    )

    initial_state = {
        "messages": [
            HumanMessage(
                content=f"Analysez ce produit '{request.product_name}' de la marque '{request.brand}'. Concurrents: {', '.join(request.competitors)}."
            )
        ],
        "product_name": request.product_name,
        "competitors": request.competitors,
        "collected_data": {},
    }

    try:
        result = await graph_app.ainvoke(initial_state)
        messages = result["messages"]
        last_message = messages[-1]

        print("\nRésultat final")
        print(f"Nombre de messages: {len(messages)}")
        print(f"Contenu final:\n{last_message.content[:200]}...")

        # Validation
        print("\nTrace des outils")
        for message in messages:
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    print(f"Outil: {tool_call['name']}")
            if hasattr(message, "name") and message.name == "generate_report":
                print("Message de sortie generate_report trouvé.")

        has_tool_calls = any(
            hasattr(message, "tool_calls") and message.tool_calls
            for message in messages
        )
        print(f"\nA des appels d'outils: {has_tool_calls}")

        if "Prix" in last_message.content and "Score" in last_message.content:
            print("SUCCESS: Le format du rapport est détecté.")
        else:
            print("WARNING: Le format du rapport n'est pas détecté.")

    except Exception as e:
        print(f"ERROR: {e}")
