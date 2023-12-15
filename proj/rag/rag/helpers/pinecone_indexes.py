import os
from warnings import warn
from typing import List, Tuple

import pinecone
from pinecone import Index, IndexDescription
from langchain.vectorstores import Pinecone

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings

# local imports
from rag.configs.rag_settings import SettingsHolder

# getting vars (best to use a dataclass to ensure types & do exceptions etc.)
input_directory = os.getenv('TRANSCRIPTS_DOWNLOAD_DIR')

pineconeKey = os.getenv('PINECONE_KEY')
pineconeEnvironment = os.getenv('PINECONE_ENVIRONMENT')
pineconeIndexName = os.getenv('PINECONE_INDEX_NAME')

# getting settings (for pinecone embeddings etc. - hardcoded in `settings.py`)
settings_objects = SettingsHolder()
pinecone_embeddings_settings = settings_objects.Pinecone
EMBEDDING_MODEL_NAME = pinecone_embeddings_settings.EMBEDDING_MODEL
EMBEDDING_MODEL_DIMENSIONS = pinecone_embeddings_settings.EMBEDDING_DIMENSIONS

def load_docs(input_directory) -> Tuple[List[Document], int]:
    '''Loads docs from the transcripts directory'''
    loader = DirectoryLoader(input_directory)
    documents = loader.load()
    num_documents = len(documents)
    return documents, num_documents

def split_docs(documents, chunk_size=500, chunk_overlap=20) -> Tuple[List[Document], int]:
    '''Chunks up documents into smaller sizes for embedding model digestion'''
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_docs = text_splitter.split_documents(documents)
    num_doc_chunks = len(chunked_docs)
    return chunked_docs, num_doc_chunks


def set_embedding_dimensions(embedder: Embeddings) -> int:
    query_result = embedder.embed_query("Hello world")
    resp_dimensions = len(query_result) # BUG: verify this is the right/best way to get model dimensions
    if resp_dimensions != EMBEDDING_MODEL_DIMENSIONS:
        warn(f"""
        There is a mismatch between the specified embedding dimensions in `settings.py`
        and the dimension size returned by the model stated there.
        
        You stated {EMBEDDING_MODEL_DIMENSIONS} dimensions,
        but the model has {resp_dimensions} dimensions.
        
        We will use the dimension returned by the model for the rest of
        the pinecone document embedding and indexing.
        """)
        return resp_dimensions
    else:
        return EMBEDDING_MODEL_DIMENSIONS

def initialise_pinecone_index() -> IndexDescription:
    embedder: Embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    dimensions: int = set_embedding_dimensions(embedder=embedder)

    # initialize pinecone
    pinecone.init(
        api_key=pineconeKey,
        environment=pineconeEnvironment
    )
    # Create and configure index if doesn't already exist
    if pineconeIndexName not in pinecone.list_indexes():
        pinecone.create_index(
            name=pineconeIndexName, 
            metric="cosine",
            dimension=dimensions
        )
    index_metadata = pinecone.describe_index(pineconeIndexName)
    return index_metadata

def run_pinecone_setup():
    documents, num_documents = load_docs(input_directory)
    chunked_docs, num_doc_chunks = split_docs(documents)
    index_metadata = initialise_pinecone_index()
    print(index_metadata)
    return index_metadata

if __name__ == "__main__":
    run_pinecone_setup()
