from app.schema import AnalysisRequest, AnalysisResponse
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from app.agent import graph_app


app = FastAPI(title="Ecom BI Agent")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Ecom BI Agent\nGo to /docs for the API documentation"
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_product(request: AnalysisRequest):
    """
    Lance l'analyse d'un produit à partir des données fournies et retourne un rapport.
    """

    # TODO: Config + fonctions réutilisables
    try:
        initial_state = {
            # NOTE: Dans un système réel, on pourrait avoir un champ pour la langue
            "messages": [
                HumanMessage(
                    content=f"Analysez ce produit '{request.product_name}' de la marque '{request.brand}'. Concurrents: {', '.join(request.competitors) if request.competitors else 'None'}."
                )
            ],
            "product_name": request.product_name,
            "competitors": request.competitors or [],
            "collected_data": {},
        }

        result = await graph_app.ainvoke(initial_state)
        messages = result["messages"]
        last_message = messages[-1]

        return AnalysisResponse(
            report_content=last_message.content, metadata={"steps_taken": len(messages)}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
