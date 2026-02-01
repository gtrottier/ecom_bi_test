from app.schema import AnalysisRequest, AnalysisResponse
from fastapi import FastAPI
from langchain.messages import HumanMessage, AIMessage




app = FastAPI(title="Ecom BI Agent")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ecom BI Agent\nGo to /docs for the API documentation"}
