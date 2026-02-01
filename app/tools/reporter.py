from typing import Any
from langchain_core.tools import tool

@tool
def generate_report(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Génère un rapport d'analyse.
    Pour l'instant, il retourne juste un message de succès.
    À améliorer plus tard.
    """
    try: 
        data = {"report": "Rapport généré avec succès"}
    except Exception as e:
        return {
            "status": "error", 
            "error_type": "unknown", 
            "message": str(e) if e else "Unknown error", 
            "retryable": False
            }
    return {"status": "ok", "data": data} 