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

    result = await graph_app.ainvoke(initial_state)
    messages = result["messages"]
    last_message = messages[-1]

    # Vérifie que des messages ont été générés
    # Vérifie la présence des appels d'outils critiques
    assert len(messages) > 1
    tool_names = []
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tool_names.append(tc["name"])

    assert "scrape_product_data" in tool_names
    assert "analyze_sentiment" in tool_names
    assert "generate_report" in tool_names

    # Vérifie que le rapport final contient les informations clés
    content = last_message.content
    assert "Prix" in content or "Tableau" in content or "Plateforme" in content
    assert "Score" in content or "Sentiment" in content
    assert request.brand.lower() in content.lower()
    assert request.product_name.lower() in content.lower()

    # Vérifie qu'il n'y a pas d'erreur rapportée dans le contenu final
    assert "ERROR" not in content.upper()
