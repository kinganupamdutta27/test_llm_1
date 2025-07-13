from langchain_core.messages import AIMessage, HumanMessage, AnyMessage, SystemMessage, BaseMessage, ToolMessage
from langchain.chat_models import init_chat_model
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from datetime import datetime
from IPython.display import display, Image
from dotenv import dotenv_values
import requests
import os


dotenv_values()

# Stting The State which will be the class of the commmon object containing the chat over the methonds and nodes
class State(TypedDict):
    messages : Annotated[List[AnyMessage],add_messages]
    query:str

# defing the tools

def add(a: int, b: int) -> int:
    """Tool for addition or sum of two numbers."""
    return a + b

def subtract(a: int, b: int) -> int:
    """Tool for subtraction of two numbers (a - b)."""
    return a - b

def multiply(a: int, b: int) -> int:
    """Tool for multiplication of two numbers."""
    return a * b

def divide(a: int, b: int) -> float:
    """Tool for division of two numbers (a / b). Raises error if b is 0."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def modulus(a: int, b: int) -> int:
    """Tool to get remainder (a % b)."""
    if b == 0:
        raise ValueError("Cannot perform modulus with zero.")
    return a % b

def exponent(a: int, b: int) -> int:
    """Tool for exponentiation (a ** b)."""
    return a ** b

def getWeather(city:str)->dict:
    """Tool for get corrent weather bassed on provided city in Argument"""
    url = os.environ.get("BASE_WEATHER_URL")
    api_key = os.environ.get("WEATHER_API")

    params = {
        "key":api_key,
        "q":city,
        "aqi":"no"
    }

    response = requests.get(url=url,params=params)

    if response.status_code==200:
        return response.json()
    
    return response.json()

def getCurrentDateandTime():
    """Returns current date and time in formatted string. In DD-MM-YYYY , HH:MM:SS:AM/PM, Month, Day format"""
    return "current Date And Time In DD-MM-YYYY , HH:MM:SS:AM/PM, Month, Day format-> "+datetime.now().strftime("%d-%m-%Y, %H:%M:%S:%p, %B, %a")


tools = [add, multiply, divide, subtract, modulus, exponent, getWeather, getCurrentDateandTime]

#creating llm
llm = init_chat_model(model="gpt-4o", model_provider="openai")
llm_tools = llm.bind_tools(tools)

def chatbot(state:State):
    history = state.get("messages",None)
    humanMessage = [HumanMessage(state["query"])]
    systemMessage = [SystemMessage(content="Hi, You are a helpfull Ai chatbot, your name is Webi and You will help people to solve there issues and please always mentain a cute attitude. Always greet and at the first querry just ceck the current date time and greet first like goodmorning, goodafternoon etc")]
    
    if not history:
        print("no history")
        response = llm_tools.invoke(systemMessage+humanMessage)

    else:
        print("with History")
        response = llm_tools.invoke(history+humanMessage)


    state["messages"] =response
    return state


ms =  MemorySaver()

builder = StateGraph(State)

builder.add_node("chatbot",chatbot)
builder.add_node("tools",ToolNode(tools=tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

graph = builder.compile(ms)
config ={"configurable": {"thread_id": "43"}}

def stream_graph_updates(user_input: str):
    config = {
        "configurable": {
            "thread_id": "43",
            "checkpoint_ns": "default",
            "checkpoint_id": "1"
        }
    }

    inputs = {"query": user_input}
    print("🔄 Streaming response...\n")

    for event in graph.stream(inputs, config=config):
        for node_name, node_output in event.items():
            if "messages" in node_output:
                messages = node_output["messages"]

                if isinstance(messages, list):
                    for msg in messages:
                        if isinstance(msg, ToolMessage):
                            print(f"🔧 Tool '{msg.name}' output: {msg.content}")
                elif isinstance(messages, AIMessage):
                    if messages.content:
                        print(f"🤖 Assistant: {messages.content}")
    print("-" * 50)  # separator between turns


def chat_loop():
    print("🧠 Webi AI Chatbot — Type 'exit' to quit\n")

    while True:
        user_input = input("🧑 You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break
        stream_graph_updates(user_input)


if __name__ == "__main__":
    chat_loop()