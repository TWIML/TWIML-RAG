Some basic set of rules for the RAG part:

1. Use `requirements.txt` to install the required packages via pip.
2. Put in all the `KEYS` in `rag/.env`
3. Ingest the groundtruths
   - Create a `./content/data` base folder
   - Copy the *.txt & *.md files from the https://drive.google.com/drive/folders/1yZgXoeQhtytEQBlW2aOUrk4IsAAAzqn2 folder to the `./content/data` folder
   - Initially, the above folder contains about 20 .md files and 15 .txt files. The Drive's `markdown` folder contains the original .md files which you will have to rename with the guests names, to add more .md files for ingestion.
   - For ingesting to the Pinecone VectorDB, run the `Pinecone_Indexing.ipynb` file
4. Run the streamlit app by executing `streamlit run main.py` from command line
