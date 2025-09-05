import streamlit as st
import uuid
from backend import chatbot
from langchain_core.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
import os
#=============================================utility functions ======================================

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def stream_response(user_message, config):
    for message_chunk, metadata in chatbot.stream(
        {'messages': HumanMessage(content=user_message)},
        config=config,
        stream_mode='messages'
    ):
        if message_chunk.content:
            yield message_chunk.content
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    add_thread(st.session_state['thread_id'], "New Chat")  # placeholder name until first msg


def add_thread(thread_id, session_name):
    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = []
    # store as dict instead of just uuid
    if not any(thread["id"] == thread_id for thread in st.session_state["chat_threads"]):
        st.session_state["chat_threads"].append({"id": thread_id, "name": session_name})

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {"thread_id": thread_id}})
    return state.values.get("messages", [])
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv('hf_token')
    
)

model = ChatHuggingFace(llm=llm)

def name_session(user_message):
    prompt = f"give me a short chat session name based on this user message : {user_message}"
    response = model.invoke(prompt).content
    return response
# =========================================== session setup ========================================
if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'], "New Chat")
# ================================================= sidebar ui =====================================================================

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New chat'):
    reset_chat()

st.sidebar.header("My Conversations")

for thread in st.session_state['chat_threads']:
    if st.sidebar.button(thread["name"]):   # show name instead of uuid
        st.session_state['thread_id'] = thread["id"]
        messages = load_conversation(thread["id"])

        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': message.content})
        st.session_state['message_history'] = temp_messages

# ================================================ main ui ============================================================================
config = {'configurable':{'thread_id':st.session_state['thread_id']}}

#loading the conversation histroy
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_message = st.chat_input('Type here')
if user_message:
    # if session name is still default, update it
    for thread in st.session_state['chat_threads']:
        if thread["id"] == st.session_state["thread_id"] and thread["name"] == "New Chat":
            thread["name"] = name_session(user_message)

    # add user msg
    st.session_state['message_history'].append({'role':'user',"content":user_message})
    with st.chat_message('user'):
        st.text(user_message)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(stream_response(user_message,config))
    st.session_state['message_history'].append({'role':'assistant',"content":ai_message})