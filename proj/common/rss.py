import requests
import xml.etree.ElementTree as ET
from common.files import get_data_filepath

# URL of the TWIML RSS feed
RSS_URL = 'https://feeds.megaphone.fm/MLN2155636147'

# Name of the RSS file to save it to
RSS_FILENAME = 'twiml_rss.xml'


def get_rss_feed(rss_url, rss_filepath):
    """
    Get RSS feed from a website and save it to twiml_rss.xml
    :return: None
    """
    # Send a GET request to the URL
    response = requests.get(rss_url)

    # If the response was successful, save the RSS file as xml
    if response.status_code == 200:
        with open(rss_filepath, 'wb') as f:
            f.write(response.content)


def get_rss_feed_data(rss_filepath):
    """
    Given a rss feed from, read it and convert it into a format that is easy to use
    :param rss_filename: Name of the rss feed file
    :return: List of dictionaries where each dictionary is a podcast episode
    """

    # Create an empty dictionary
    rss_data = {}

    # Define the namespace
    namespaces = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}

    tree = ET.parse(rss_filepath)
    root = tree.getroot()
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        description = item.find('description').text
        url = item.find('enclosure').get('url')

        if item.find("itunes:episode", namespaces) is not None:
            episode = item.find("itunes:episode", namespaces).text
        else:
            # Check if title ends as '#xxx` where xxx is the episode number but is not always 3 digits
            # Search from the end of the string for the # character
            # If it is found, then get the number after it
            # If not, then add it to the 'other' list
            if title.rfind('#') != -1:
                episode = title[title.rfind('#') + 1:]
            else:
                # Episode is the title but changed so that it can be used as a filename
                episode = title.replace(' ', '_').replace(':', '').replace('?', '').replace('!', '').replace('\'', '')

        rss_data[episode] = {
            'episode': episode,
            'title': title,
            'url': url,
            'description': description
        }

    return rss_data


def download_mp3(url_data, filename_mp3):
    """
    Download the mp3 file from the url
    :param url_data: MP3 podcast url
    :param filename_mp3: Filename of the mp3 file
    :return:
    """
    # Download the mp3 file
    r = requests.get(url_data)
    with open(filename_mp3, 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    get_rss_feed(RSS_URL, get_data_filepath('rss', RSS_FILENAME))
    podcast_data = get_rss_feed_data(get_data_filepath('rss', RSS_FILENAME))
    print('Total episodes: ', len(podcast_data))
    print('Latest episode: ', list(podcast_data)[0])
    print(podcast_data[list(podcast_data)[0]])
