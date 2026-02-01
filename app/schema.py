import operator
from typing import Annotated, Any, Literal, TypedDict

from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class AnalysisRequest(BaseModel):
    product_name: str
    brand: str
    competitors: list[str] | None = Field(default_factory=list, description="List of competitors")
    # Pas certain si nécessaire, mais potentiellement utile pour raisonnement additionnel
    #additional_info: dict[str, str] | None = Field(default_factory=dict, description="Additional information")

class AnalysisResponse(BaseModel):
    summary: str = Field(description="Summary of the analysis")
    recommendations: list[str] = Field(description="Recommendations")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    product_name: str
    competitors: list[str]
    # Idées, à traiter dans outils peut-être
    collected_data: dict[str, Any]
    insights: Annotated[list[str], operator.add]
    recommendations: Annotated[list[str], operator.add]