from langchain.chat_models import init_chat_model
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_stock_price(symbol: str) -> float:
    """Get the latest stock price for a given symbol."""
    # Dummy implementation for illustration
    stock_prices = {"MSFT": 300.0, "AAPL": 150.0, "GOOGL": 2800.0}
    return stock_prices.get(symbol.upper(), 0.0)

tools = [get_stock_price]
llm = init_chat_model("google_genai:gemini-2.0-flash")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder = StateGraph(State)
builder.add_node("chatbot_node", chatbot)
builder.add_node('tools', ToolNode(tools))

builder.add_edge(START, "chatbot_node")
builder.add_conditional_edges("chatbot_node", tools_condition)
builder.add_edge('tools', "chatbot_node")
graph_5 = builder.compile()

from IPython.display import Image, display

img_bytes = graph_5.get_graph().draw_mermaid_png()
with open("graph_5.png", "wb") as f:
    f.write(img_bytes)
print("Graph saved to graph.png")


state = graph_5.invoke({"messages" : [{"role": "user", "content": "What is the latest price of MSFT stock?"}]})
print(state["messages"][-1].content)


state = graph_5.invoke({"messages": [{"role": "user", "content": "USA President in 2004?"}]})
print(state["messages"][-1].content)

msg = "I want to buy 20 AAPL stocks using current price. Then 15 MSFT. What will be the total cost?"

state = graph_5.invoke({"messages": [{"role": "user", "content": msg}]})
print(state["messages"][-1].content)