# Run the Embeddings Pipeline

We will use local qdrant for storing embeddings. Here we assume that we have the transcripts and the speaker information. 

We will use the BGE embeddings to create the embeddings and store them in qdrant.

1. **Setup the qdrant docker image.** Instructions are here: https://qdrant.tech/documentation/quick-start/

First create a directory for your qdrant data outside the TWIML-RAG directory. Then `cd` into that directory. Then run the following commands to get qdrant up and running. The `docker run` command will create and populate the 'qdrant_storage' directory automatically.
   ```
   docker pull qdrant/qdrant
   docker run -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_storage:/qdrant/storage:z qdrant/qdrant

   ```
You can access the dashboard on the local qdrant at http://localhost:6333/dashboard

2. **Install requirements.** The next step is to install the BGE and Qdrant-related requirements for the `embeddings` pipeline. If you are using a tool to manage python environments, you can create a new one now, or if you have already run the `speech_to_text` pipeline locally, you can just install the requirements to the same environment.
   ```
   cd proj/embeddings
   pip install -r requirements.txt
   ```

3. **Create a qdrant config file.** The Qdrant client requires a Key and URL, though these can be left blank since we are using local versions of qdrant and embaas.
   ```
   cp config.py.example config.py
   ```

4. **Download required data files.** The embeddings pipeline assumes that the `speech_to_text` pipeline has run and has created the transcription artifacts locally. If you haven't run the pipeline locally you must download the `asr` folder for the speaker information and the `transcripts` folder for the episode transcripts and save them in the `proj/data` folder. Download these folders from the 'output transcripts' directory on the shared TWIML-RAG Google Drive. (Request access via the TWIML slack community twiml-rag channel). 

5. **Run the embeddings pipeline.**  Now you're ready to run the embeddings pipeline. (Note that this will be very slow on CPU only machines. GPU took about 5 minutes but CPU only took over 3 hours).

   ```
   cd proj
   python -m embeddings.pipeline
   ```

This will create (in the `proj/data` folder):
1. `info` folder with information about the episodes
2. `embeddings` folder with the dialogs cut up with 250 word size patches
3. `rss` folder with the RSS feed file twiml_rss.xml

In addition, you should now have a `qdrant_storage/collections` folder in the qdrant directory you created earlier, with embeddings using BGE and saved to qdrant
   1. Summary information from the transcripts (twiml_ai_podcast_summary)
   2. Patches of dialogs from the transcripts (twiml_ai_podcast)
