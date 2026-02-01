from typing import Literal
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.schema import AgentState
from app.tools.reporter import generate_report
from app.tools.scraper import scrape_product_data
from app.tools.sentiment import analyze_sentiment
from app.tools.trends import analyze_trends

load_dotenv()

tools = [scrape_product_data, analyze_sentiment, analyze_trends, generate_report]
tool_node = ToolNode(tools)

llm = ChatOpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
        model="google/gemini-2.5-flash",
        temperature=0,
    )

llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    """Invoke le llm avec 'state' actuel"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Détermine si le processus doit continuer basé sur le dernier message"""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"
    
#Note : typechecker 'ty' renvoi erreur, mais fonctionne correctement. À suivre
workflow = StateGraph(AgentState) # ty: ignore[invalid-argument-type]

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

graph_app = workflow.compile()
