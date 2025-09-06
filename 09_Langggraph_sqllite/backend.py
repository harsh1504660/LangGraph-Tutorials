from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os 
import sqlite3
load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv('hf_token')
    
)

model = ChatHuggingFace(llm=llm)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}


conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrive_all_thread():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    # return in the same dict format expected elsewhere
    return [{"id": thread_id, "name": "Old Chat"} for thread_id in all_threads]