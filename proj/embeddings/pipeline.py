import json
import os
import requests
import time
from tqdm import tqdm

from common.files import sanitize_filename, get_data_filepath, get_data_dirpath, tqdm_file_list

from FlagEmbedding import FlagModel

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct

from .config import QDRANT_URL, QDRANT_API_KEY
from speech_to_text.rss_process import get_rss_feed_data, RSS_FILENAME, get_rss_feed, RSS_URL

def get_redirect_url(url):
    """
    Get the redirect URL from the URL
    :param url: URL to get the redirect URL from
    :return: Redirect URL
    """
    # Get the redirect URL from the URL
    response = requests.head(url, allow_redirects=True)
    redirect_url = response.url

    return redirect_url


def fix_description(description, episode_num):
    """
    This is based on the assumption that there is a sentence "The complete show ..." and we remove that sentence and get
    the show notes url from it
    """

    # Get the show notes url that starts with twimlai.com/go/
    url_index = description.find('twimlai.com/go/')
    if url_index == -1:
        show_notes_url = 'https://twimlai.com/go/' + episode_num
    else:
        show_notes_url = description[url_index:]

        # remove a period if it has it at the end
        if show_notes_url[-1] == '.':
            show_notes_url = show_notes_url[:-1]

        # If there is not http or https in front, add to it
        if show_notes_url[:4] != 'http':
            show_notes_url = 'https://' + show_notes_url

    # This url is a forward. Find the forwarding link from this
    show_notes_url = get_redirect_url(show_notes_url)

    # Find the index of the phrase "The complete show ..."
    index = description.find('The complete show notes for this episode')

    # Remove that sentence from the text
    description = description[:index]

    # Remove any trailing new lines
    description = description.strip()

    return show_notes_url, description


def make_episode_data():
    """
    Get the episode data from the RSS feed and save it as json files
    @return:
    """
    # Get the podcast data from RSS
    podcast_data = get_rss_feed_data(RSS_FILENAME)

    # Iterate through the podcast data and fix the description and the show notes url
    for episode in tqdm(podcast_data, desc="Making Episode Data"):
        # Name of the json file that has the info
        json_filename = f'{episode}.info.json'

        # Remove any characters that are illegal in filenames
        json_filename = sanitize_filename(json_filename)
        json_filename = get_data_filepath('info', json_filename)

        # Check if the file exists. If it doesn't, then process and create the file
        if not os.path.exists(json_filename):
            show_notes_url, description = fix_description(podcast_data[episode]['description'], episode)
            podcast_data[episode]['summary'] = description
            podcast_data[episode]['link'] = show_notes_url

            # For each episode, save the data as json file in the info directory with the episode number.info.json
            # as the filename
            with open(json_filename, 'w') as f:
                json.dump(podcast_data[episode], f, indent=4)


def word_count(text):
    """
    Count the number of words in the text
    @param text: Text to count the number of words in
    @return:
    """
    return len(text.split())


def get_episode_text(id, word_size):
    """
    Get the text for the episode as a list of dialogs split into patches of word_size
    @param id: ID of the episode
    @param word_size: How many words to use in the embedding
    @return: List of dialogs split into patches of word_size
    """

    # Get the transcript file for the episode and create the text for it.
    # Format is speaker: text speaker: text

    # Get the transcript file for the episode and check if it exists or not
    transcript_filename = get_data_filepath('transcripts', f'{id}.corrected.json')
    speakers_filename = get_data_filepath('asr', f'{id}.speakers.json')

    if not os.path.exists(transcript_filename):
        return None

    if not os.path.exists(speakers_filename):
        return None

    # Read the speakers file
    with open(speakers_filename, 'r') as f:
        speakers = json.load(f)

    # Read the transcript file
    with open(transcript_filename, 'r') as f:
        transcript = json.load(f)

    # Some constants that we will be referencing often
    transcript_speakers = transcript['speakers']

    # Get the text from the transcript as dialogs
    text = []
    for dialog in transcript['dialogs']:
        if dialog['text'] == '':
            continue

        speaker_idx = dialog['speaker']
        speaker = speakers.get(transcript_speakers[speaker_idx], 'Unknown Speaker')
        atext = f'{speaker}: {dialog["text"]}'
        atext = atext.replace('"', '')
        text.append(atext)

    # Join the text together until word_size is reached. Then start a new patch.
    # We want the last dialog to overlap with the next patch so that we can get the context of the dialog.
    patches = []
    patch = ''
    prev_dialog = ''
    for dialog in text:
        if word_count(patch) >= word_size:
            patches.append(patch)
            patch = prev_dialog + '\n'

        patch += dialog + '\n'
        prev_dialog = dialog

    return patches


def make_embedding(episode_data, force_create, word_size):
    """
    Make the embedding for the episode
    @param episode_data: Episode data
    @param force_create: If True, then force the creation of the file even if it exists
    @param word_size: How many words to use in the embedding
    """
    # ID of the episode
    id = episode_data['episode']

    # Name of the json file that we will store the embedding in
    json_filename = get_data_filepath('embeddings', f'{id}.json')

    # Check if the file exists and if it does and we are not forcing the creation of the file, then skip
    if os.path.exists(json_filename) and not force_create:
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
    text = get_episode_text(id, word_size)

    # Check if we have text or not. If no text, the file was not present or there was an error processing it.
    if text is None:
        return

    # Create the JSONL file in the embeddings folder
    json_str = f'{{"id": "{id}", "text": {json.dumps(text)}, "source": "{source}", "metadata": {json.dumps(metadata)}}}'

    # Pretty format the json string
    json_str = json.dumps(json.loads(json_str), indent=2)

    with open(json_filename, 'w') as f:
        f.write(json_str)


def make_embedding_file(force_create, word_size):
    """
    Make the embedding file for each of the episodes
    @param force_create: If True, then force the creation of the file even if it exists
    @param word_size: How many words to use in the embedding
    @return: List of episodes
    """
    # Parse the RSS feed and get the all of the episodes
    episodes = get_rss_feed_data(RSS_FILENAME)

    # Iterate through the episodes
    episode_list = []
    for episode in tqdm(episodes,desc="Making Embedding Files"):
        # Process the episode
        episode_data = episodes[episode]

        # Create the JSONL file for the episode
        make_embedding(episode_data, force_create, word_size)

        # Add the episode to the list of episodes
        episode_list.append(episode_data)

    return episode_list


def get_client(mode='local'):
    """
    Get the qdrant client
    @param mode: Mode to run in. Can be 'local' or 'remote'
    @return: Qdrant client
    """
    if mode == 'local':
        qdrant_client = QdrantClient("localhost", port=6333)
    else:  # if mode == 'remote'
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

    return qdrant_client


def create_collection(client, collection_name, size):
    """
    Create the collection if it does not exist
    @param client:  Qdrant client
    @param collection_name:  Name of the collection to create
    @param size: Size of the vector
    """
    all_collections = [collection_name.name for collection_name in client.get_collections().collections]

    # Check if the collection exists
    if collection_name not in all_collections:
        # If it does not have it, then create the collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=size, distance=Distance.DOT),
        )


def run_embedding_summary():
    # Start the qdrant client
    client = get_client()

    # Name of the collection
    collection_name = 'twiml_ai_podcast_summary'
    collection_size = 1024

    # Create the collection
    create_collection(client, collection_name, collection_size)

    query_instruction_for_retrevial = ('Generate a representation for this podcast excerpt that can be used to '
                                       'find what the podcast is about?')
    model = FlagModel('BAAI/bge-large-en-v1.5', query_instruction_for_retrieval=query_instruction_for_retrevial,
                      use_fp16=True)

    # Time the function
    start_time = time.time()

    # Create a list of points of the embeddings
    points = []

    # Get all the files in the pinecone directory
    for i, filename in tqdm_file_list(get_data_dirpath('info'), desc="Building Embedding Summary"):
        # Get the full filename
        json_filename = get_data_filepath('info', filename)

        with open(json_filename, 'r') as f:
            podcast_data = json.load(f)

        # Get the embedding for the text
        embedding = model.encode(podcast_data['summary'])

        # Turn it into a list of floats
        embedding_list = [float(x) for x in embedding]

        # Create the payload
        payload = {'text': podcast_data['summary'], 'episode': podcast_data['episode'], 'title': podcast_data['title'],
                   'link': podcast_data['link']}

        point = PointStruct(id=i, vector=embedding_list, payload=payload)
        points.append(point)

        operation_info = client.upsert(
            collection_name=collection_name,
            wait=True,
            points=[point],
        )

    end_time = time.time()
    # print(f"Time taken: {end_time - start_time}")


def run_embedding():
    collection_name = 'twiml_ai_podcast'
    collection_size = 1024

    # Start the qdrant client
    client = get_client()

    # Create the collection
    create_collection(client, collection_name, collection_size)

    # sentence1 = "Sam Charrington:  Welcome to the TwiML AI Podcast. I'm your host, Sam Charrington. Sam Charrington:  All right, so I'm here with Clare Corthell at the Wrangle Conference in San Francisco. Hey, Clare. great to finally meet you in person. Clare Corthell:  Hi, great to meet you in person too, Sam. Sam Charrington:  Yeah, so what's particularly exciting about getting to talk to you is I talked about your post a few, I guess it was one like the second, the second podcast I did, you wrote that post around that same time on the hybrid AI. And"

    query_instruction_for_retrevial = ('Generate a representation for this podcast excerpt that can be used to '
                                       'find what the podcast is about?')
    model = FlagModel('BAAI/bge-large-en-v1.5', query_instruction_for_retrieval=query_instruction_for_retrevial,
                      use_fp16=True)

    # Time the function
    start_time = time.time()

    # Create a list of points of the embeddings
    points = []

    # Get all the files in the pinecone directory
    for i, filename in tqdm_file_list(get_data_dirpath('embeddings'), desc="Building Embedding:  Files", position=0):
        # Get the full filename
        filename_full = get_data_filepath('embeddings', filename)
        # print(filename_full)

        # Get the text from the file
        with open(filename_full, 'r') as f:
            text = json.load(f)['text']

        # Load the file from info to get the show summary and link
        episode_name = filename.split('.')[0]
        json_filename = f'{episode_name}.info.json'
        json_filename = sanitize_filename(json_filename)
        json_filename = get_data_filepath('info', json_filename)
        with open(json_filename, 'r') as f:
            podcast_data = json.load(f)

        # Get the embedding for each of the text portions in the file
        for ti, text_portion in tqdm(enumerate(text), total=len(text), desc="Building Embedding: Points", position=1, leave=False):
            # We are going to embed the text portion with the title
            text_data = podcast_data['title'] + '\n' + text_portion

            embedding = model.encode(text_data)

            # Turn it into a list of floats
            embedding_list = [float(x) for x in embedding]

            # Create the payload
            payload = {'text': text_data, 'episode': episode_name, 'title': podcast_data['title'],
                       'link': podcast_data['link']}

            id = i * 100 + ti
            point = PointStruct(id=id, vector=embedding_list, payload=payload)
            points.append(point)

            operation_info = client.upsert(
                collection_name=collection_name,
                wait=True,
                points=[point],
            )
            # print(id, operation_info) # Status should always be completed since we're waiting for it

    end_time = time.time()
    # print(f"Time taken: {end_time - start_time}")


def query_embedding(questions, collection_name):
    # Start the qdrant client
    client = get_client()

    # This is the query string. Turn into an embedding using the model
    for query in questions:
        query_instruction_for_retrevial = ('Generate a representation for this podcast excerpt that can be used to '
                                           'find what the podcast is about?')
        model = FlagModel('BAAI/bge-large-en-v1.5', query_instruction_for_retrieval=query_instruction_for_retrevial,
                          use_fp16=True)
        embedding = model.encode(query).tolist()

        search_results = client.search(
            collection_name=collection_name, query_vector=embedding, limit=10
        )
        print(query)
        for i, search_result in enumerate(search_results):
            print(i, '. ', search_result.payload['title'], search_result.payload['link'])
        print('')


if __name__ == '__main__':
    # Make sure we have the directories rss, info and embeddings
    folders = ['rss', 'info', 'embeddings']
    for folder in folders:
        if not os.path.exists(get_data_dirpath(folder)):
            os.mkdir(get_data_dirpath(folder))
    
    # Check that the rss file is there
    if not os.path.exists(get_data_filepath('rss', RSS_FILENAME)):
        get_rss_feed(RSS_URL, get_data_filepath('rss', RSS_FILENAME))

    # Generate the info data from the RSS feed
    make_episode_data_flag = True #False
    if make_episode_data_flag:
        make_episode_data()

    # Generate the dialogs data for embeddings
    make_dialogs_flag = True #False
    if make_dialogs_flag:
        make_embedding_file(force_create=True, word_size=250)

    questions = {
        'Which episode is about robotics?',
        'Which episode is about Ethics?',
        'Which episode is about industrial robotics?',
        'Which episode is about dangers of AI?',
        'Which episode is involves Google?'
    }

    # Create the embeddings for the summary text
    run_embedding_summary_flag = True #False
    if run_embedding_summary_flag:
        run_embedding_summary()
        query_embedding(questions, 'twiml_ai_podcast_summary')

    # Create the embeddings for the full text
    run_embedding_flag = True
    if run_embedding_flag:
        run_embedding()
        query_embedding(questions, 'twiml_ai_podcast')
