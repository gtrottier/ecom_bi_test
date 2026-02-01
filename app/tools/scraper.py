from typing import Any
from langchain_core.tools import tool

@tool
def scrape_product_data(product_name: str, brand: str, competitors: list[str]) -> dict[str, Any]:
    """
    Scrape les données du produit
    Pour l'instant, réutilise directement les données fournies
    """
    #TODO : Logique
    try:
        data = {
            "product_name": product_name,
            "brand": brand,
            "competitors": competitors,
            "data": {}
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": str(e) if e else "Unknown error",
            "retryable": False,
        }
    return {"status": "ok", "data": data}