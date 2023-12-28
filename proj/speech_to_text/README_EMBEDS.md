## Steps

1. Setup the qdrant docker image. Instructions are here: https://qdrant.tech/documentation/quick-start/
Basically just do the following (in a new directory where you want to store the qdrant data) and qdrant should be running. The run command will create and populate the 'qdrant_storage' directory automatically.
```
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334  -v $(pwd)/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
```
You can access the dashboard on the local qdrant on http://localhost:6333/dashboard

2. Install the pip packages on `requirements_embeddings.txt`. It is BGE and Qdrant-related packages

3. Run `pipeline_embeddins.py` (in the speach_to_text application/dir). You must download the `asr` folder for the speaker information and the `transcripts` folder for the episode transcripts. Download these folders from the 'output transcripts' directory on the shared TWIML-RAG Google Drive (request access via the TWIML slack community twiml-rag channel.

This will create
1. `info` folder with information about the episodes
2. `embeddings` folder with the dialogs cut up with 250 word size patches
3. Create embeddings using BGE and save to qdrant
  1. Summary information from the info
  2. Patches of dialogs from the transcripts