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

## Running the Speech-to-Text Pipeline

To run the local dockerfile, run the following command:

```bash
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/credentials.json -v [LOCAL_PATH_TO_CREDENTIALS_FILE]:/tmp/keys/credentials.json:ro --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it twiml:speech_to_text
```

Notes:

- The tag `twiml:speech_to_tex` is used to identify the docker image. It will automatically run `speech_to_text/run.py` when it starts up. 
- Replace `[LOCAL_PATH_TO_CREDENTIALS_FILE]` with the path to your local copy of the credentials file for the Google Cloud service account. 
- You can remove `--gpus all` if your machine doesn't have GPUs. 

If you want to access the container interactively, you can use the `--it` flag to get inside the docker image:

```bash
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/credentials.json -v /Users/sam/Downloads/twiml-rag-sa-credentials.json:/tmp/keys/credentials.json:ro --gpus all -it twiml:speech_to_text /bin/sh
```

To run the pipeline once you're in the container use the following command:

```bash
python3 -m speech_to_text.run
```

You can use this to run the pipeline on your local machine as well. Be sure you're in the `proj` directory when you run it.

## Deploying to Google Cloud

Deploying the project to Google Cloud is a bit more complex. In order to access required project resources, such as Google Drive files, the project code must be run using a pre-configured GCP service account. You can replicate many of the deployment steps into your own GCP account, but some parts of the code are hard-coded to look in certain Google Drive directories for things, and this will only work if the code runs under the service account. We will try to abstract out some of these linkages in the future.

### Building the Project

To build the project and deploy the container to the GCP Artifact Registry, the following command is used:

```bash
gcloud builds submit --region=us-central1 --tag us-central1-docker.pkg.dev/twiml-rag/twiml-rag-repo/twiml-rag-stt-image:nvcr-base-no-preload
```

The URL component in the command points to a specific artifact repository in the TWIML-RAG project. This can be changed to a repo you create in your own account for testing.

### Deploying to a VM for testing

To deploy the project to a VM in GCP, the following command is used:

```bash
gcloud compute instances create instance-1 \
  --project=twiml-rag \
  --zone=europe-central2-b \
  --machine-type=n1-standard-8 \
  --accelerator=count=1,type=nvidia-tesla-t4 \
  --image=projects/cos-cloud/global/images/cos-stable-109-17800-66-27 \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-balanced \
  --boot-disk-device-name=instance-1 \
  --network-interface=network-tier=PREMIUM,subnet=default \
  --maintenance-policy=TERMINATE \
  --provisioning-model=STANDARD \
  --service-account=rag-drive@twiml-rag.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform \
  --no-shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --labels=goog-ec-src=vm_add-gcloud,container-vm=cos-stable-109-17800-66-27 \
  --metadata-from-file=user-data=gcloud-twimlrag-init.yml
  ```

  Note:
  - This command deploys by default to the europe-central2-b zone because it's one of the few I found that consistently has Tesla T4 GPUs available.
  - The command specifies a specific service account within the twiml-rag project. To test in your own account you can specify your own project and delete the service account refererence and a default service account will be used. (Not tested)
  - The command specifies a cloud config (`gcloud-twimlrag-init.yml`) file which initializes the instance by (a) installing the GPU drivers and (b) pulling and running the project container. 

#### Debugging VM deployment

If everything works correctly, the instance will launch, the GPU drivers will be installed, and the docker container will run. The default entry point for the docker container runs the run.py file at the project root, which pulls the podcast RSS feed and determines if there are episodes that need to be transcribed, and if so, it does it.

Here are some tips for debugging if something goes wrong:

- Open an SSH session to the VM
- Run `docker ps` to see if the container is running. Depending on when the error happened, it likely terminated and was deleted.
- The project runs as a systemd service in the VM instance, so the tools for debugging systemd services apply:
  - To view the service logs, use *journalctl*, e.g. `journalctl -u twiml-rag.service -n 100` or `journalctl -u twiml-rag.service -f` to tail.
  - If you change the service script in /etc/systemd/system/twiml-rag.service, use `sudo systemctl daemon-reload` to reload it.
  - To restart the service, use `sudo systemctl restart twiml-rag.service`. This will re-execute the docker run command in the cloud config. Note that if you've made code changes and rebuilt the docker file, it may be cached on the instance. You can either kill the instance and start over, or delete the previously downloaded image (e.g. `docker image rm [img id]`).
- To debug the container, you can launch a new instance of it and override the entry point so that it doesn't automatically exit using a command like:
```bash
  /usr/bin/docker run \
        --volume /var/lib/nvidia/lib64:/usr/local/nvidia/lib64 \
        --volume /var/lib/nvidia/bin:/usr/local/nvidia/bin \
        --device /dev/nvidia0:/dev/nvidia0 \
        --device /dev/nvidia-uvm:/dev/nvidia-uvm \
        --device /dev/nvidiactl:/dev/nvidiactl \
        --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
        --rm -u 2000 --name=twiml-rag-container \
        us-central1-docker.pkg.dev/twiml-rag/twiml-rag-repo/twiml-rag-stt-image:nvcr-base-no-preload \
        tail -f /dev/null
```
  - You can now open another SSH session, check that the container is running using `docker ps` and shell into the container using `docker exec -it twiml-rag-container /bin/bash`



