from typing import Any
from langchain_core.tools import tool

@tool
def analyze_trends(product_name: str, brand: str, competitors: list[str]) -> dict[str, Any]:
    """
    Analyse les tendances du marché
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
            "message": str(e),
            "retryable": False,
        }
    return {"status": "ok", "data": data}
