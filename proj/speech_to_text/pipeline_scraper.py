import requests

from proj.speech_to_text.rss_process import get_rss_feed_data, RSS_FILENAME
from proj.speech_to_text.scraper import run_scrape, blacklist_sites


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


def pipeline_scraper():
    # Parse the RSS feed and get the episodes
    episodes = get_rss_feed_data(RSS_FILENAME)

    # Iterate through the episodes
    episode_list = []
    for episode in episodes:
        # Get the episode data
        episode_data = episodes[episode]

        # Get the URL for the link to the TWIML show notes page from the redirect URL
        redirect_url = f'https://twimlai.com/go/{episode_data["episode"]}'
        show_notes_url = get_redirect_url(redirect_url)

        # Scrape the data and then write to file
        scrape_textfile = f'scraper/{episode_data["episode"]}.txt'
        run_scrape(show_notes_url, scrape_textfile, blacklist=blacklist_sites, enforce_subdir_depth=0, depth=5)


if __name__ == '__main__':
    pipeline_scraper()
