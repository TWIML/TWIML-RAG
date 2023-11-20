import json
import os

import pinecone

from config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, OPENAI_API_KEY
from rss_process import get_rss_feed_data, RSS_FILENAME


def get_episode_text(id):
    # Get the transcript file for the episode and create the text for it.
    # Format is speaker: text speaker: text

    # Get the transcript file for the episode and check if it exists or not
    transcript_filename = f'transcripts/{id}.corrected.json'
    speakers_filename = f'asr/{id}.speakers.json'

    if not os.path.exists(transcript_filename):
        return None

    # Read the speakers file
    with open(speakers_filename, 'r') as f:
        speakers = json.load(f)

    # Read the transcript file
    with open(transcript_filename, 'r') as f:
        transcript = json.load(f)

    # Some constants that we will be referencing often
    transcript_speakers = transcript['speakers']

    # Get the text from the transcript
    text = ''
    for dialog in transcript['dialogs']:
        if dialog['text'] == '':
            continue

        speaker_idx = dialog['speaker']
        speaker = speakers.get(transcript_speakers[speaker_idx], 'Unknown Speaker')
        text += f'{speaker}: {dialog["text"]} '

    return text


def make_jsonl(episode_data, force_create=False):
    # ID of the episode
    id = episode_data['episode']

    # Name of the jsonl file
    jsonl_filename = f'pinecone/{id}.jsonl'

    # Check if the file exists and if it does and we are not forcing the creation of the file, then skip
    if os.path.exists(jsonl_filename) and not force_create:
        return

    # Data to create the JSONL for pinecone
    source = episode_data['url']

    episode_title = episode_data['title']
    episode_description = episode_data['description']

    # Remove the following characters from the title and description
    episode_title = episode_title.replace('"', '')
    episode_description = episode_description.replace('"', '')

    metadata = {
        "title": episode_title,
        "description": episode_description,
    }
    text = get_episode_text(id)

    # Check if we have text or not. If no text, the file was not present or there was an error processing it.
    if text is None:
        return

    text = text.replace('"', '')

    # Create the JSONL file in the pinecone folder
    with open(jsonl_filename, 'w') as f:
        f.write(f'{{"id": "{id}", "text": "{text}", "source": "{source}", "metadata": {json.dumps(metadata)}}}')


def make_all_jsonl(force_create=False):
    # Parse the RSS feed and get the all of the episodes
    episodes = get_rss_feed_data(RSS_FILENAME)

    # Iterate through the episodes
    episode_list = []
    for episode in episodes:
        # Process the episode
        episode_data = episodes[episode]

        # Create the JSONL file for the episode
        make_jsonl(episode_data, force_create)

        # Add the episode to the list of episodes
        episode_list.append(episode_data)

    return episode_list


def pipeline_pinecone():
    # Make all the jsonl files
    episode_list = make_all_jsonl(force_create=True)

    # Start up pinecone
    pinecone.init(api_key=PINECONE_API_KEY, environment='gcp-starter')

    # Set a bunch of environment variables to make the command line work
    os.environ['PINECONE_ENVIRONMENT'] = PINECONE_ENVIRONMENT
    os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.system(f'canopy upsert pinecone --index-name twiml')


if __name__ == '__main__':
    pipeline_pinecone()
