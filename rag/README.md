Some basic set of rules for the RAG part:

1. Use `requirements.txt` to install the required packages via pip.
2. Ingest the groundtruths, i.e, *.txt files from './content/data' to pinecone vectorDB via the `Pinecone_Indexing.ipynb` file
3. Put in `openaiKey` & `pineconeKey` in `utils.py`
4. Run the streamlit app by executing `streamlit run main.py` from command line
