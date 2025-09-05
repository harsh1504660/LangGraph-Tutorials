import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]

config = {'configurable':{'thread_id':'thread-1'}}

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



    respose = chatbot.invoke({'messages':[HumanMessage(content=user_message)]},config=config)
    ai_message = respose['messages'][-1].content
    st.session_state['message_history'].append({'role':'assistant',"content":ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)