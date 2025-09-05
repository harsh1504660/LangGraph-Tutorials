import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]

config = {'configurable':{'thread_id':'thread-1'}}
def stream_response():
    for message_chunk, metadata in chatbot.stream(
        {'messages': HumanMessage(content=user_message)},
        config=config,
        stream_mode='messages'
    ):
        if message_chunk.content:   # skip empty chunks
            yield message_chunk.content
#loading the conversation histroy
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_message = st.chat_input('Type here')

if user_message:
    #first add msg to msg histroy
    st.session_state['message_history'].append({'role':'user',"content":user_message})
    with st.chat_message('user'):
        st.text(user_message)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(stream_response())
    st.session_state['message_history'].append({'role':'assistant',"content":ai_message})