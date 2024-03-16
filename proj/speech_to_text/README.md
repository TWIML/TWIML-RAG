# Speech to Text

## Test Environment Details: Google Cloud

The speech_to_text module and the steps below have been tested on a Google Cloud instance with the following specs:
- T4 GPU
- N1-Standard-4 (15GB Ram)
- 200 GB Boot Disk
- Boot Image: Deep Learning VM for PyTorch 2.1 with CUDA 12.1 M118

You can create a comparable instance via the console, or using the gcloud CLI using the following command:

```bash
gcloud compute instances create trag-20240312-044840 
  --project=[PROJECT-NAME] 
  --zone=[ZONE] 
  --machine-type=n1-standard-4 
  --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default 
  --maintenance-policy=TERMINATE 
  --provisioning-model=STANDARD  
  --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append 
  --accelerator=count=1,type=nvidia-tesla-t4 
  --create-disk=auto-delete=yes,boot=yes,device-name=trag,image=projects/ml-images/global/images/c2-deeplearning-pytorch-2-1-cu121-v20240306-debian-11-py310,mode=rw,size=200,type=projects/[PROJECT-NAME]/zones/[ZONE]/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud --reservation-affinity=any
```

PLEASE NOTE:
- This instance type costs approximately $300/mo to run. Don't forget to shut it down when you're not using it!
- You will need to create a Google Cloud project with billing enabled.
- You will need to have appropriate quota (e.g. GPU) in the Zone you are launching your instances.
- If you decide to use a cloud instance, any files/actions referred to as "local" below, need to be on your cloud instance.

## Testing on Your Personal Machine

If you decide to run the Docker container on your personal machine, you need to ensure that the `docker build` environment can see and use your GPU(s).

You can use the following Docker file to test your environment.  

```bash
cd proj
docker build -t twiml:speech_to_text -f speech_to_text/deploy/Dockerfile.cuda_test .
```

You need to confirm that "Is CUDA available" returns "True" in the output of `torch.utils.collect_env` before proceeding. 

If you haven't previously done the following, you will likely need to do the following:
1. Install the [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
2. Set your [default runtime](https://stackoverflow.com/questions/59691207/docker-build-with-nvidia-runtime).

## Building the Container

To build the local dockerfile, run the following command:

```bash
cd proj
docker build -t twiml:speech_to_text -f speech_to_text/deploy/Dockerfile.local .
```

Notes: 

- This will use the `Dockerfile.local` to create a docker image in your computer with the tag `twiml:speech_to_text`.
- The Dockerfile preloads whisper large-v2 model. Changing this does not accomplish anything, b/c large-v2 is hard-coded in whisper_pyannote_fusion.
- You can also use the pre-built image via the [Docker Hub](https://hub.docker.com/repository/docker/twiml/speech_to_text/general).

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