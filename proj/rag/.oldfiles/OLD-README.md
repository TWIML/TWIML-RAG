Some basic set of rules for the RAG part:

1. Use `requirements.txt` to install the required packages via pip.
2. Creat a .env file and Enter all the `KEYS` and configs in `rag/.env`. Sample:
    PREPED_TRANSCRIPTS_DIR=data_input/RAG_ingestion
    EMB_MODEL=multi-qa-mpnet-base-dot-v1
    PINECONE_KEY=
    PINECONE_INDEX_NAME=twiml-rag
    PINECONE_ENVIRONMENT=us-west1-gcp
    OPENAI_API_KEY=
    MEMORY_K=5
    VECT_TOP_P=8
3. Use the `Pinecone_Indexing.ipynb` file to ingest prepped transcripts found on the shared google drive - https://drive.google.com/drive/folders/0AL0-_RLA7pqDUk9PVA.
    * Download the files to your environment (e.g.to data_input/RAG_ingestion)
    * If needed request access via the twiml-rag slack channel.
    * Alternatively create your own prepped transcript data for vector store from the 'transcripts' directory.
4. Alternatively Ingest the groundtruths
   - Create a `./content/data` base folder
   - Copy the *.txt & *.md files from the https://drive.google.com/drive/folders/1yZgXoeQhtytEQBlW2aOUrk4IsAAAzqn2 folder to the `./content/data` folder
   - Initially, the above folder contains about 20 .md files and 15 .txt files. The Drive's `markdown` folder contains the original .md files which you will have to rename with the guests names, to add more .md files for ingestion.
   - For ingesting to the Pinecone VectorDB, run the `Pinecone_Indexing.ipynb` file
5. Run the streamlit app by executing `streamlit run main.py` from command line
