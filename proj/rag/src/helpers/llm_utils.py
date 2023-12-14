from sentence_transformers import SentenceTransformer
import pinecone
import openai
import streamlit as st
import os
from dotenv import load_dotenv

# local imports
from src.helpers.config_utils import load_settings_objects

# load settings for openai, pinecone etc.
settings_objects = load_settings_objects()
openai_conversation_settings = settings_objects['openai-conversation']

# Load the dotenv file
load_dotenv(override=True)

openaiKey = os.getenv('OPENAI_API_KEY')
pineconeKey = os.getenv('PINECONE_KEY')

openai.api_key = openaiKey
emb_model_name = os.getenv('EMB_MODEL')
emb_model = SentenceTransformer(emb_model_name)

pineconeEnvironment = os.getenv('PINECONE_ENVIRONMENT')
pineconeIndexName = os.getenv('PINECONE_INDEX_NAME')
pinecone.init(api_key=pineconeKey, environment=pineconeEnvironment)
index = pinecone.Index(pineconeIndexName)

vect_top_p = openai_conversation_settings.VECTOR_TOP_P

"""
This method, takes an input, encodes it using a model, and queries an index to find the top three matches. 
 It then extracts metadata, specifically the source (containing full name), from the JSON results obtained from Pinecone. 
 The method constructs and returns a formatted string with the full name of the top three matches, organized in 
 'full name: rest of the sentence' format. 
"""
def find_match(input):
    input_em = emb_model.encode(input).tolist()
    result = index.query(input_em, top_k=8, includeMetadata=True)
    # For inserting the speakers metadata to the front of each sentence
    # Returns the source (containing full name) and text (contents) of the JSON 
    # that we get from Pinecone in 'source: text' format
    return (result['matches'][0]['metadata']['source'].split('-')[1]).split('.')[0] + ": " + result['matches'][0]['metadata']['text'] \
        + "\n" + (result['matches'][1]['metadata']['source'].split('-')[1]).split('.')[0] + ": " + result['matches'][1]['metadata']['text'] \
        + "\n" + (result['matches'][2]['metadata']['source'].split('-')[1]).split('.')[0] + ": " + result['matches'][2]['metadata']['text']

"""
The 'query_refiner' function takes a conversation log and a user query as input and utilizes OpenAI's ChatGPT API to generate
 a refined question. It uses the GPT-4 model to generate a question that is expected to be the most relevant for obtaining 
 an answer from a knowledge base.
"""
def query_refiner(conversation, query):
    prompt = f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        # {"role": "system", "content":"I am going to ask you a question, which I would like you to answer based only on the provided context, and not any other information."},
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.7,
        max_tokens=256,
        top_p=vect_top_p,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

"""
The 'get_conversation_string' function appears to be designed to retrieve a formatted string representing a conversation. 
It seems to use the Streamlit library (indicated by st) to access a session state containing both user requests and bot responses.
"""
def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):    
        conversation_string += "Human: " + st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: " + st.session_state['responses'][i+1] + "\n"

    return conversation_string