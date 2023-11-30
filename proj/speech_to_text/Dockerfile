FROM nvcr.io/nvidia/pytorch:22.04-py3

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /python-docker

COPY requirements.txt requirements.txt

RUN apt-get update -q && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean autoclean && apt-get autoremove --yes && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

#RUN python -m pip install https://github.com/pyannote/pyannote-audio/archive/refs/heads/develop.zip
RUN pip install protobuf==3.20.0
RUN pip install -U pydantic
# RUN pip install -U spacy

# Preload model so that startup time isn't too slow
# RUN python3 -c 'import whisper;whisper.load_model("large", device="cpu")'
# RUN python3 -c 'import torch;import whisper;devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu");model = whisper.load_model("large" , device=devices)'
# RUN python3 -c "from pyannote.audio import Pipeline; pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token='hf_xxxxxxxxxxxxxxxxx')"

COPY . .

# Create the default /.cache directory for various caches & configs & set permissions
RUN mkdir -p /.cache
RUN chmod -R 777 /.cache

# Set permissions on the various working folders
RUN chmod -R 777 /python-docker/asr
RUN chmod -R 777 /python-docker/markdown
RUN chmod -R 777 /python-docker/rss
RUN chmod -R 777 /python-docker/podcasts

CMD [ "python3", "run.py"]