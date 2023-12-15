# running setup before imports to load singletons - NOTE: this is probably poor practice, please advise any better architecture
from rag.setup import run_setup; run_setup()

import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from streamlit_chat import message

# local imports
from rag.configs.rag_settings import SettingsHolder
from rag.helpers.chatbot import find_match, get_conversation_string, query_refiner

# load settings for openai, pinecone etc.
settings_objects = SettingsHolder()
streamlit_application_settings = settings_objects.Streamlit

# Load the dotenv file
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


if __name__ == "__main__": # app entry point (to avoid reloading whole file)

    # Streamlit's header at the topmost page
    st.subheader("RAG with Langchain, GPT-4, Pinecone, and Streamlit on TWIML Podcasts")

    if 'responses' not in st.session_state:
        st.session_state['responses'] = ["How can I assist you?"]

    if 'requests' not in st.session_state:
        st.session_state['requests'] = []

    if 'buffer_memory' not in st.session_state:             # Using 1 in Conversational memory
        memory_k = streamlit_application_settings.MEMORY_K
        st.session_state.buffer_memory = ConversationBufferWindowMemory(k=memory_k, return_messages=True)

    system_msg_template = SystemMessagePromptTemplate.from_template(
        template="""Answer the question as truthfully as possible using the provided context, 
    and if the answer is not contained within the text below, say 'I don't know'""")

    human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

    prompt_template = ChatPromptTemplate.from_messages(
        [system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])


    # ChatOpenAI uses GPT-4 as its model, coupled with openAPI key from utils.py
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY) # type: ignore # NOTE: added because the lib doesn't seem to have defined it's accepted args in a standard/identifiable manner
    # Not fully using the buffered memory here, as has been reduced to k=1 above.
    # May increase the conversational buffer above to see effects
    conversation = ConversationChain(
        memory=st.session_state.buffer_memory, 
        prompt=prompt_template, 
        llm=llm, 
        verbose=True
    )


    # container for chat history
    response_container = st.container()
    # container for text box
    textcontainer = st.container()


    # This context-block signifies where users can input a query, and the app processes the query using the 
    # find_match function, updates the conversation context, and then makes a prediction using a LLM 
    # model ('conversation.predict')
    with textcontainer:
        query = st.text_input("Query: ", key="input")
        if query:
            with st.spinner("thinking..."):
                conversation_string = get_conversation_string()
                # st.code(conversation_string)
                # refined_query = query_refiner(conversation_string, query)
                # st.subheader("Refined Query: ")
                # st.write(refined_query)
                context = find_match(query)     # refined_query
                print(context)                  # To see n contexts in the command line 
                response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
            st.session_state.requests.append(query)
            st.session_state.responses.append(response)

    # Using a Streamlits container, 'response_container', this context block checks to see if there are 
    # responses stored in the session state, and uses them to display the bot responses and user requests.
    with response_container:
        if st.session_state['responses']:

            for i in range(len(st.session_state['responses'])):
                message(st.session_state['responses'][i], key=str(i))
                if i < len(st.session_state['requests']):
                    message(st.session_state["requests"][i], is_user=True, key=str(i)+ '_user')