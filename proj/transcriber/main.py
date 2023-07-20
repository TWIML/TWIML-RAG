import streamlit as st
import os
from io import StringIO
import openai
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

st.title("🎙️ Whisper Podcast Transcription")

uploaded_file = st.file_uploader("Upload an audio file", type=("mp3")) #, "mp4", "mpeg", "mpga", "m4a", "wav", "webm"))

if uploaded_file is None:
  st.stop()

st.audio(uploaded_file, format='audio/mp3')

# Get the size of the file in bytes
file_size = uploaded_file.size

# Convert bytes to megabytes
file_size_in_mb = file_size / (1024 * 1024)

# Check if the file size is less than 25 MB
if file_size_in_mb > 25:
  episode = AudioSegment.from_mp3(uploaded_file)
  # split episode up into 25 MB chunks
  episode_chunks = episode[::25 * 1024 * 1024]


prompt = st.text_input(
  "What is this episode about?",
  placeholder="Please provide a short episode summary?",
  disabled=not uploaded_file,
) 

if prompt is None:
  st.stop()
  # st.error("Please provide a short episode summary.")

# Call the Whisper API with the audio file and the prompt
openai.api_key = os.getenv("OPENAI_API_KEY")
transcription = openai.Audio.transcribe("whisper-1", file=uploaded_file, prompt=prompt)

# Display the transcription
st.header("Transcription")

st.write(transcription)

