import json
import os
import whisper_pyannote_fusion

from google_cloud_utils import get_secret
from pipeline import download_mp3, add_speaker_identification

HUGGING_FACE_API_KEY = get_secret('HUGGING_FACE_API_KEY')


def process_episode_whisper_x(episode):
    """
    Run WhisperX on the episode.
    Todo: Test code and remove duplicate code from pipeline.py
    """

    file_prefix = episode['episode']

    # Download the mp3 file if it does not exist into the podcasts folder
    mp3_filename = os.path.join('podcasts', file_prefix + '.mp3')
    if not os.path.exists(mp3_filename):
        print(f'Downloading {episode["episode"]}...')
        download_mp3(episode['url'], mp3_filename)
    audio_filename = mp3_filename

    # Set up the filename that we will use to save the text from the asr
    whisper_json_filename = os.path.join('asr', file_prefix + '.whisper.json')
    pyannote_json_filename = os.path.join('asr', file_prefix + '.pyannote.json')
    pyannote_whisper_json_filename = os.path.join('asr', file_prefix + '.pyannote_whisper.json')
    whisperx_alignment_json_filename = os.path.join('asr', file_prefix + '.whisperx.json')
    speakers_json_filename = os.path.join('asr', file_prefix + '.speakers.json')

    initial_prompt = 'TWIML with Sam Charrington. ' + episode['title'] + ' ' + episode['description']

    output2_json_file = os.path.join('transcripts', file_prefix + '.output2.json')
    markdown1_output = os.path.join('markdown', file_prefix + '.1.md')

    try:
        whisper_pyannote_fusion.whisper_pyannote_fusion(audio_filename, 'whisperx_align_pyannote',
                                                        whisper_json_file=whisper_json_filename,
                                                        pyannote_json_file=pyannote_json_filename,
                                                        pyannote_whisper_json_filename=pyannote_whisper_json_filename,
                                                        whisperx_alignment_json_filename=whisperx_alignment_json_filename,
                                                        output_json_file=output2_json_file,
                                                        initial_prompt=initial_prompt,
                                                        HUGGING_FACE_API_KEY=HUGGING_FACE_API_KEY)
        with open(output2_json_file, 'r') as f:
            corrected_json = json.load(f)
        corrected_json['title'] = episode['title']
        corrected_json['description'] = episode['description']
        corrected_json['link'] = episode['url']
        corrected_json = add_speaker_identification(corrected_json, speakers_json_filename)
        whisper_pyannote_fusion.transcript_to_workdown(corrected_json, markdown1_output)
    except Exception as e:
        print(f'Error processing whisperx episode {episode["episode"]}: {e}. Skipping ...')


def run_pipeline_whisper_x():
    """
    Run the whisperX pipeline
    TODO: Figure out what alternate pipelines are what to do about them
    """
    pass
