"""Python file to serve as the frontend"""
import os
import re

import streamlit as st
from streamlit_chat import message

# from langchain.chains import ConversationChain
# from langchain.llms import OpenAI

from langchain.schema import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import DocArrayInMemorySearch

import openai
openai.api_key  = os.environ['OPENAI_API_KEY']


## Load and munge data.
#

def remove_prefixes(input_string):
    # This regular expression pattern matches any number of non-word characters
    # or digits at the beginning of the string
    pattern = r'^[\W\d]*'
    output_string = re.sub(pattern, '', input_string)
    return output_string

def gen_page_text(trans):
    """ remove prefix and join lines. """
    texts_lines = []
    for line in trans.split('\n'):
        text = remove_prefixes(line)
        texts_lines.append(text)
    page_cont = ' '.join(texts_lines)
    return page_cont

def load_trans(dpath):
    """ Convert all page content to docs """
    docs = []   
    for filename in os.listdir(dpath)[:1]:
        with open(f"{dpath}/{filename}") as fl:
            trans_text = fl.read()
            page_text = gen_page_text(trans_text)
    return page_text

# @st.cache_data
def gen_page_docs():
    chunks = 
    for chunk_text in chunks:
        doc = Document(page_content=chunk_text)
        docs.append(doc)
        

dpath = 'data_input/hubberman/transcripts'
docs = load_trans(dpath)

## Conifture the chat bot.
#
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


with st.spinner('Loading transcripts to vector DB'):
    # index = VectorstoreIndexCreator(
        # vectorstore_cls=DocArrayInMemorySearch
    # ).from_documents(docs)
    index = VectorstoreIndexCreator(
                vectorstore_cls=Chroma, 
                embedding=OpenAIEmbeddings(),
                text_splitter=CharacterTextSplitter(chunk_size=100, chunk_overlap=10).
    
    if "index" not in st.session_state:
        st.session_state["index"] = index


### GPT
st.header("TWIML-RAG Demo")
st.subheader("Huberman Lab Podcast")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
 
user_input = st.text_input('Ask a podcase question:', '')
if user_input:
    response = index.query(user_input)
    st.session_state["chat_history"].append({'user': user_input, 'bot': response})

if st.session_state["chat_history"]:
    for chat in st.session_state["chat_history"]:
        st.write(f"User: {chat['user']}")
        st.write(f"Bot: {chat['bot']}")

with st.expander("See explanation"):
    st.write(docs[0])


# From here down is all the StreamLit UI.

# st.set_page_config(page_title="TWIMLRAG", page_icon=":robot:")
# st.header("TWIML-RAG Demo")

# if "generated" not in st.session_state:
    # st.session_state["generated"] = []

# if "past" not in st.session_state:
    # st.session_state["past"] = []


# def get_text():
    # input_text = st.text_input("You: ", "Hello, how are you?", key="input")
    # return input_text
    
# user_input = get_text()

# if user_input:
    # output = chain.run(input=user_input)
    # output = index.query(user_input)
    # st.session_state.past.append(user_input)
    # st.session_state.generated.append(output)

# if st.session_state["generated"]:
    # for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        # message(st.session_state["generated"][i], key=str(i))
        # message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
