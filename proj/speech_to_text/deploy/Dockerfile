FROM nvcr.io/nvidia/pytorch:22.04-py3

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update -q && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean autoclean && apt-get autoremove --yes && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    pip3 install protobuf==3.20.0 && \ 
    pip install -U pydantic

COPY . .

# Create the default /.cache directory for various caches & configs & set permissions
RUN mkdir -p /.cache
RUN chmod -R 777 /.cache
RUN mkdir -p /.config/matplotlib
RUN chmod -R 777 /.config

RUN mkdir -p /.triton
RUN chmod -R 777 /.triton

# Set permissions on the various working folders
RUN chmod -R 777 /app/asr
RUN chmod -R 777 /app/markdown
RUN chmod -R 777 /app/rss
RUN chmod -R 777 /app/podcasts
RUN chmod -R 777 /app/transcripts

# Link the cuda libraries to the default location
USER root
RUN echo /usr/local/nvidia/lib64/ >/etc/ld.so.conf.d/libcuda.conf && ldconfig

USER 2000
CMD [ "python3", "run.py"]