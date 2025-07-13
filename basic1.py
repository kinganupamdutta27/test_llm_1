from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
load_dotenv()

ms = MemorySaver()

class State(MessagesState):
    query:str

llm_gpt_4o=init_chat_model(model="gpt-4o", model_provider="openai")

msg = [HumanMessage(content="Hi, How are you")]

res = llm_gpt_4o.invoke(msg)

def print_response(state:State):
    pass

if isinstance(res, AIMessage):
    #print(res.content)
    print(res.response_metadata["token_usage"]["total_tokens"])

def chatbot(state:State):
    msg = llm_gpt_4o.invoke([state["query"]])
    state["messages"] = msg
    return state



builder = StateGraph(State)

builder.add_node("chatbot",chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot",END)

graph = builder.compile(checkpointer=ms)


print(graph.invoke({"query":"Hi, I am ANuopam"}, config={"configurable": {"thread_id": "1"}}))




