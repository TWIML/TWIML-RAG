"""Python file to serve as the frontend"""
import os
import re

import streamlit as st
from streamlit_chat import message

import openai 

openai.api_key  = os.environ['OPENAI_API_KEY']
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

## Prep.
#
if 'embedder' not in st.session_state:
    with st.spinner('Loading the embedder'):
        model_name = "sentence-transformers/all-mpnet-base-v2"
        embedder = HuggingFaceEmbeddings(model_name=model_name)
        st.session_state['embedder'] = embedder

if 'vdb' not in st.session_state:
    with st.spinner('Loading vector database'):
        vdb = Chroma(persist_directory='chroma_db/huberman', 
                     embedding_function=st.session_state['embedder'])
        st.session_state['vdb'] = vdb

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if 'bot' not in st.session_state:
    llm = OpenAI(temperature=0.0)
    retriever = st.session_state['vdb'].as_retriever(search_kwargs={'k':10})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    bot = ConversationalRetrievalChain.from_llm(llm, 
                                               retriever=retriever, 
                                               memory=memory)
    st.session_state['bot'] = bot

if 'chat_on' not in st.session_state:
    st.session_state['chat_on'] = True

## GUI
#

st.header("Huberman Lab Podcast Chat")
st.write("A TWIML generative_ai demo.")

user_message = st.text_input(label="Your question: ")
if user_message:
    result = st.session_state['bot']({"question": user_message})
    for message in st.session_state['bot'].memory.chat_memory.messages:
        st.write(f"{message.type}: {message.content}\n")
