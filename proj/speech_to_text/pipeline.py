import argparse
import json
import os

import whisper_pyannote_fusion

from speaker_identification import add_speaker_identification
from common.rss import download_mp3, get_rss_feed, get_rss_feed_data, RSS_URL, RSS_FILENAME
from common.checks import check_required_dirs, check_environment_vars
from google_drive.utils import upload_files_to_drive
from common.files import get_data_dirpath, get_data_filepath

check_environment_vars()
HUGGING_FACE_API_KEY = os.environ['HUGGING_FACE_API_KEY']


def process_episode(episode):
    file_prefix = episode['episode']

    # Download the mp3 file if it does not exist into the podcasts folder
    mp3_filename = get_data_filepath('podcasts', file_prefix + '.mp3')
    if not os.path.exists(mp3_filename):
        if not os.path.exists(get_data_dirpath('podcasts')):
            os.makedirs(get_data_dirpath('podcasts'))
        print(f'Downloading {episode["episode"]}...')
        download_mp3(episode['url'], mp3_filename)
    audio_filename = mp3_filename

    # Set up the filename that we will use to save the text from the asr
    whisper_json_filename = get_data_filepath('asr', file_prefix + '.whisper.json')
    pyannote_json_filename = get_data_filepath('asr', file_prefix + '.pyannote.json')
    pyannote_whisper_json_filename = get_data_filepath('asr', file_prefix + '.pyannote_whisper.json')
    output_json_file = get_data_filepath('transcripts', file_prefix + '.output.json')
    corrected_json_file = get_data_filepath('transcripts', file_prefix + '.corrected.json')
    markdown_output = get_data_filepath('markdown', file_prefix + '.md')
    speakers_json_filename = get_data_filepath('asr', file_prefix + '.speakers.json')

    initial_prompt = 'TWIML with Sam Charrington. ' + episode['title'] + ' ' + episode['description']

    try:
        print(f'Processing {episode["episode"]}...')
        whisper_pyannote_fusion.whisper_pyannote_fusion(audio_filename, 'correct_pyannote_with_whisper',
                                                        whisper_json_file=whisper_json_filename,
                                                        pyannote_json_file=pyannote_json_filename,
                                                        pyannote_whisper_json_filename=pyannote_whisper_json_filename,
                                                        whisperx_alignment_json_filename=None,
                                                        output_json_file=output_json_file,
                                                        corrected_json_file=corrected_json_file,
                                                        initial_prompt=initial_prompt,
                                                        HUGGING_FACE_API_KEY=HUGGING_FACE_API_KEY)
        with open(corrected_json_file, 'r') as f:
            corrected_json = json.load(f)
        corrected_json['title'] = episode['title']
        corrected_json['description'] = episode['description']
        corrected_json['link'] = episode['url']
        corrected_json = add_speaker_identification(corrected_json, speakers_json_filename)
        whisper_pyannote_fusion.transcript_to_workdown(corrected_json, markdown_output)

        # Upload the files to google drive into the appropriate folders
        upload_files_to_drive(
            [whisper_json_filename, pyannote_json_filename, pyannote_whisper_json_filename, speakers_json_filename],
            'asr')
        upload_files_to_drive([corrected_json_file], 'transcripts')
        upload_files_to_drive([markdown_output], 'markdown')

    except Exception as e:
        print(f'Error processing episode {episode["episode"]}: {e}. Skipping ...')


def run_pipeline(start, end=None):
    """
    Run the pipeline of getting the RSS feed and converting all the podcasts to text
    """

    # Prerequisites
    # Check the folders exist
    check_required_dirs()
    check_environment_vars()

    # Download the RSS feed if the file does not exist, or if we have -1 as the start
    if not os.path.exists(get_data_filepath('rss', RSS_FILENAME)) or start == -1:
        get_rss_feed(RSS_URL, get_data_filepath('rss', RSS_FILENAME))

    # Get the podcast data as a list of dictionaries
    podcast_data = get_rss_feed_data(get_data_filepath('rss', RSS_FILENAME))

    # If start is -1, process all the episodes
    if start == -1:
        for episode in podcast_data:
            process_episode(episode)
    else:
        # If end is not specified, process only the episode specified in start
        if end is None:
            process_episode(podcast_data[str(start)])
        else:
            # Process all the episodes from start to end
            for episode in range(start, end + 1):
                # Check if the key is in the dictionary
                if str(episode) in podcast_data:
                    process_episode(podcast_data[str(episode)])
                else:
                    print(f'Episode {episode} not found. Skipping...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Speech to Text Pipeline.")

    parser.add_argument("--start", type=int, required=True, help="Start of the range")
    parser.add_argument("--end", type=int, required=False, help="End of the range")

    args = parser.parse_args()

    run_pipeline(args.start, args.end)
