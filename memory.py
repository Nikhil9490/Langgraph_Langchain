from langchain.chat_models import init_chat_model
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
load_dotenv()

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
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
graph_6 = builder.compile(checkpointer=memory)

from IPython.display import Image, display

img_bytes = graph_6.get_graph().draw_mermaid_png()
with open("graph_6.png", "wb") as f:
    f.write(img_bytes)
print("Graph saved to graph.png")

config1 = { 'configurable' : { 'thread_id' : '1'} }

state = graph_6.invoke({"messages" : [{"role": "user", "content": "I want to buy 20 GOOGL stocks using current price. Then 15 MSFT. What will be the total cost"}]}, config = config1)
print(state["messages"][-1].content)

config2 = { 'configurable' : { 'thread_id' : '2'} }

state = graph_6.invoke({"messages": [{"role": "user", "content": "Tell me current price of 5 AAPL stocks."}]}, config=config2)
print(state["messages"][-1].content)

state = graph_6.invoke({"messages": [{"role": "user", "content": "Add $500 to the previous total cost and tell me the answer"}]}, config=config1)
print(state["messages"][-1].content)

state = graph_6.invoke({"messages": [{"role": "user", "content": "Add $500 to the previous total cost and tell me the answer"}]}, config=config2)
print(state["messages"][-1].content)