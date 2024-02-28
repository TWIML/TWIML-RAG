from google_cloud_auth import gcloud_auth
from googleapiclient.discovery import build
from google_cloud_utils import get_latest_episode_from_drive
from utils import check_required_dirs
from pipeline import run_pipeline
from rss_process import get_rss_feed, get_rss_feed_data, RSS_URL, RSS_FILENAME
from common.files import get_data_filepath

# Get latest episode number from RSS feed

def get_latest_ep_from_rss():
    # Download the latest RSS feed
    get_rss_feed(RSS_URL, get_data_filepath('rss', RSS_FILENAME))

    # Get the latest episode number from the RSS feed
    rss_data = get_rss_feed_data(RSS_FILENAME)
    latest_ep = max([int(episode) for episode in rss_data.keys() if episode.isnumeric()])
    return latest_ep

def run():
    last_processed = get_latest_episode_from_drive()
    last_published = get_latest_ep_from_rss()

    print(f'Last processed episode: {last_processed}')
    print(f'Last published episode: {last_published}')

    if last_published > last_processed:
        run_pipeline(last_processed + 1, last_published)

if __name__ == '__main__':
    check_required_dirs()
    run()

