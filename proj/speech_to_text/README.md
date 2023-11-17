# Speech to Text

## Running Local dockerfile

To build the local dockerfile, run the following command:

```bash
docker build -t twiml:speech_to_text . -f Dockerfile.local
```

This will use the `Dockerfile.local` to create a docker image in your computer with the tag `twiml:speech_to_text`.

To run the local dockerfile, run the following command:

```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 twiml:speech_to_text
```

We use the tag `twiml:speech_to_tex` to run the docker image. It will run `run.py` when it starts up. If you want to use it interactively, you have to use `--it` flag and you can get inside the docker image.