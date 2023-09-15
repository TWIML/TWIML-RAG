from sentence_transformers import SentenceTransformer
import pinecone
import openai
import streamlit as st

openaiKey = ""
pineconeKey = ''

openai.api_key = openaiKey
model = SentenceTransformer('all-MiniLM-L6-v2')

pinecone.init(api_key=pineconeKey, environment='gcp-starter')
index = pinecone.Index('demo')

def find_match(input):
    input_em = model.encode(input).tolist()
    result = index.query(input_em, top_k=3, includeMetadata=True)
    return result['matches'][0]['metadata']['text']+"\n"+result['matches'][1]['metadata']['text']+"\n"+ \
        result['matches'][2]['metadata']['text']

def query_refiner(conversation, query):
    prompt = f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        # {"role": "system", "content":"I am going to ask you a question, which I would like you to answer based only on the provided context, and not any other information."},
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):    
        conversation_string += "Human: " + st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: " + st.session_state['responses'][i+1] + "\n"

    return conversation_string