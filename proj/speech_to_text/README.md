# Speech to Text

## Building the Container

To build the local dockerfile, run the following command:

```bash
cd proj
docker build -t twiml:speech_to_text -f speech_to_text/Dockerfile.local .
```

Notes: 

- This will use the `Dockerfile.local` to create a docker image in your computer with the tag `twiml:speech_to_text`.
- The Dockerfile preloads whisper-large model. You can replace `large` with `tiny` for smoke-testing.

## Preparing to Run the Pipeline

In this section you will collect the required API keys and access rights.

The STT pipeline depends on pretrained pyannote models for diarization and voice activity detection. These are gated models and you will need to accept their terms and conditions in order to run the pipeline. To do this:

1. Create a Hugging Face account if don't already have one, or log in to your existing account.
2. Visit each of the following model pages to review the conditions and enable access the model weights:
  - https://huggingface.co/pyannote/speaker-diarization
  - https://huggingface.co/pyannote/voice-activity-detection

The pipeline will need your OpenAI and Hugging Face API keys to operate. To do this, create a file, e.g. ~/.env and add your keys:

```
HUGGING_FACE_API_KEY=hf_*********
OPENAI_API_KEY=sk-**********
```

You will pass the path to this file to the `docker run` command in the next step.

Finally, the pipeline accesses data in a TWIML-RAG folder on Google Drive using a service account. In order to do this, you must pass it the service account credentials, which you can get from any TWIML-RAG committer. The pass to this file will also be passed to `docker run`.

## Running the Speech-to-Text Pipeline

The pipeline will automatically download the model weights from the Huggingface hub, but in order to do so you will first need to 
To run the local dockerfile, run the following command:

```bash
docker run --env-file [PATH_TO_ENV_FILE] -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/credentials.json -v [PATH_TO_CREDENTIALS_FILE]:/tmp/keys/credentials.json:ro --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it twiml:speech_to_text
```

Notes:

- The tag `twiml:speech_to_tex` is used to identify the docker image. It will automatically run `speech_to_text/run.py` when it starts up. 
- Replace `[PATH_TO_CREDENTIALS_FILE]` with the path to your local copy of the credentials file for the Google Cloud service account. 
- You can remove `--gpus all` if your machine doesn't have GPUs. 

If you want to access the container interactively, you can use the `--it` flag to get inside the docker image:

```bash
docker run --env-file [PATH_TO_ENV_FILE] -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/credentials.json -v [PATH_TO_CREDENTIALS_FILE]:/tmp/keys/credentials.json:ro --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it twiml:speech_to_text /bin/sh
```


To run the pipeline once you're in the container use the following command:

```bash
python3 -m speech_to_text.run
```

You can use this to run the pipeline on your local machine as well. Be sure you're in the `proj` directory when you run it.