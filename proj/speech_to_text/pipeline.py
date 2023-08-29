import argparse
import os

from rss_process import get_rss_feed, get_rss_feed_data, RSS_URL, RSS_FILENAME
from utils import check_required_dirs


def process_episode(episode):
    print(episode['episode'])


def run_pipeline(start, end=None):
    """
    Run the pipeline of getting the RSS feed and converting all the podcasts to text
    """

    # Prerequisites
    # Check the folders exist
    check_required_dirs()

    # Download the RSS feed if the file does not exist, or if we have -1 as the start
    if not os.path.exists(RSS_FILENAME) or start == -1:
        get_rss_feed(RSS_URL, RSS_FILENAME)

    # Get the podcast data as a list of dictionaries
    podcast_data = get_rss_feed_data(RSS_FILENAME)

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
    parser.add_argument("--end", type=int, required=True, help="End of the range")

    args = parser.parse_args()

    run_pipeline(args.start, args.end)
