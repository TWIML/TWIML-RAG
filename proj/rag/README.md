Some basic set of rules for the RAG part:

1. Use `requirements.txt` to install the required packages via pip.
2. Use the `Pinecone_Indexing.ipynb` file to ingest prepped transcripts found on the shared google drive - https://drive.google.com/drive/folders/0AL0-_RLA7pqDUk9PVA.
    * Download the files to your environment.
    * You can request access via the twiml-rag slack channel.
    * Alternatively you can create your own prepped transcript for vector store ingestion directly from the 'transcripts' directory.
3. Put in all the `KEYS` in `rag/.env`
4. Run the streamlit app by executing `streamlit run main.py` from command line
