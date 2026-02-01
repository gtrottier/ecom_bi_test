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
    try:
        initial_state = {
            "messages": [
                HumanMessage(
                    content=f"Analyze the product '{request.product_name}' by brand '{request.brand}'. Competitors: {', '.join(request.competitors) if request.competitors else 'None'}."
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
