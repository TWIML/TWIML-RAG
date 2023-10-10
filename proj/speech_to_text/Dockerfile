FROM gcr.io/deeplearning-platform-release/pytorch-gpu.2-0.py310

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /python-docker

COPY requirements.txt requirements.txt

RUN apt-get update -q && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean autoclean && apt-get autoremove --yes && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Preload model so that startup time isn't too slow
#RUN python3 -c 'import whisper;whisper.load_model("large", device="cpu")'

COPY . .

CMD [ "python3", "-m" , "run.py"]