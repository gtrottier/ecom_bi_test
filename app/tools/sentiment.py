from langchain_core.tools import tool

from app.schema import ToolResult


@tool
def analyze_sentiment(
    product_name: str, brand: str, competitors: list[str]
) -> ToolResult:
    """
    Analyse les avis clients du produit et de ses concurrents
    """
    # TODO : Logique
    try:
        data = {
            "product_name": product_name,
            "brand": brand,
            "competitors": competitors,
            "data": {},
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": str(e) if e else "Unknown error",
            "retryable": False,
        }
    return {"status": "ok", "data": data}
