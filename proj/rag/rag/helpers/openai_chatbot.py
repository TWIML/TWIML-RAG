from sentence_transformers import SentenceTransformer
import pinecone
import openai
import streamlit as st
import os

from openai import OpenAI, NotFoundError
from openai.types import Model

# local imports
from rag.configs.rag_settings import SettingsHolder

# load .env keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_KEY = os.getenv('PINECONE_KEY')

# load settings for openai, pinecone etc.
settings_objects = SettingsHolder()
openai_conversation_settings = settings_objects.OpenAi
pinecone_embeddings_settings = settings_objects.Pinecone

# pinecone
PINECONE_ENV = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)
PineconeIndex = pinecone.Index(PINECONE_INDEX_NAME)

# open-ai
openai_conversation_settings = settings_objects.OpenAi
OPENAI_CHAT_MODEL = openai_conversation_settings.CHAT_MODEL
OPENAI_CHAT_MODEL_ALTERNATIVE = openai_conversation_settings.ALTERNATIVE_CHAT_MODEL
VECTOR_TOP_P = openai_conversation_settings.VECTOR_TOP_P
OpenAiClient = OpenAI(api_key=OPENAI_API_KEY)

# embeddings
EMBEDDING_MODEL_NAME = pinecone_embeddings_settings.EMBEDDING_MODEL
EmbeddingModel = SentenceTransformer(EMBEDDING_MODEL_NAME)

def get_usable_openai_model():
    models_list = OpenAiClient.models.list()
    accesible_model_names = []
    print(f'\n\n{models_list}')
    for m in models_list:
        print(m.id)
        accesible_model_names.append(m.id)

    if OPENAI_CHAT_MODEL in accesible_model_names:
        model_name = OPENAI_CHAT_MODEL
    elif OPENAI_CHAT_MODEL_ALTERNATIVE in accesible_model_names:
        model_name = OPENAI_CHAT_MODEL_ALTERNATIVE
    else:
        raise Exception(f'''
        Your OPENAI API settings do not seem to have access to any of the two models in `settings.py`:
            1. {OPENAI_CHAT_MODEL}
            2. {OPENAI_CHAT_MODEL_ALTERNATIVE}
        We might need to configure an alternative way of selecting a chat model from all available options...
        Please see the README taskboard, or contact someone on the slack for implementation discussion
        ''')
    print(f'''
    You will be using `{model_name}` as your openai chatbot model
    ''')
    return model_name

"""
This method, takes an input, encodes it using a model, and queries an index to find the top three matches. 
 It then extracts metadata, specifically the source (containing full name), from the JSON results obtained from Pinecone. 
 The method constructs and returns a formatted string with the full name of the top three matches, organized in 
 'full name: rest of the sentence' format. 
"""
def find_match(input):
    input_em = EmbeddingModel.encode(input).tolist()
    result = PineconeIndex.query(input_em, top_k=8, includeMetadata=True)
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
        top_p=VECTOR_TOP_P,
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