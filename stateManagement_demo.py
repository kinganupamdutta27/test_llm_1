from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from dotenv import load_dotenv
import random

load_dotenv()

class State(TypedDict):
    graph_state:str

def node_1(state:State):
    print("--Node 1--")
    return {"graph_state" : state["graph_state"] + " I am"}

def node_2(state:State):
    print("-- Node 2 --")
    return {"graph_state" : state["graph_state"]+" Happy"}

def node_3(state:State):
    print("--Node 3--")
    return {"graph_state" : state["graph_state"]+ " Sad"}

def branch_condition(state:State) -> Literal["node_2","node_3"]:
    x = random.randrange(0,10)
    if x>5:
        return "node_2"
    return "node_3"


builder = StateGraph(State)

builder.add_node("node_1",node_1)
builder.add_node("node_2",node_2)
builder.add_node("node_3",node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1",branch_condition)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()

#print(graph.get_graph().draw_mermaid())

print(graph.invoke({"graph_state":"Hi I am ANUPAM"}))
