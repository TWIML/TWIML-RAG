import os
import random
import requests
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup

blacklist_sites = ['podcasts.apple.com', 'open.spotify.com', 'youtu.be', 'overcast.fm',
                   'podcastaddict.com', 'castbox.fm', 'pca.st', 'twitter.com', 'twimlai.com',
                   'facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com', 'reddit.com',
                   ]


def scrape_page(url):
    """
    Scape the text content from the url page and the links and return them
    :param url: URL to scrape
    :return: text, links
    """

    # Get the contents of hte url page
    r = requests.get(url)

    # Check that there were no errors in getting the page
    if r.status_code != 200:
        raise Exception(f'Error getting {url}: {r.status_code}')

    soup = BeautifulSoup(r.content, 'html.parser')

    # Extract all the text
    page_text = soup.get_text()

    # Extract all the links
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))

    return page_text, links


def in_blacklist(url, blacklist):
    """
    Check if the given URL is in the list of blacklisted websites
    :param url: URL to check
    :param blacklist: List of blacklisted websites
    :return: True if the URL is in the blacklist, False otherwise
    """

    # Get the website name of the url
    parsed_url = urlparse(url)
    website_name = parsed_url.netloc

    # Remove the www. from the website name
    if website_name.startswith('www.'):
        website_name = website_name[4:]

    # Check if the website name is in the blacklist
    if website_name in blacklist:
        return True
    else:
        return False


def get_url_dir(url):
    """
    Given a URL, return the URL directory that the page is in.
    If the last segment of the path contains a file extension, it's considered a page and removed.
    Otherwise, the entire path is considered part of the directory.
    :param url: URL to get the directory from
    :return: URL directory
    """
    parsed_url = urlparse(url)

    # Split the path into segments
    path_segments = parsed_url.path.split('/')
    if len(path_segments) > 1:
        # Check if the last segment contains a file extension
        _, ext = os.path.splitext(path_segments[-1])
        if ext:
            # If it's a file/page, remove the last segment
            path_without_page = '/'.join(path_segments[:-1])
        else:
            # If not, consider the whole path
            path_without_page = parsed_url.path
    else:
        path_without_page = ''

    # Construct the new URL without the page, query, or fragment
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, path_without_page, '', '', ''))
    return new_url


def is_local_link(url):
    """
    Check if the link is a local link
    :param url:
    :return:  True if the link is a local link, False otherwise
    """
    parsed_url = urlparse(url)
    return not parsed_url.scheme and not parsed_url.netloc


def get_url_extension(url):
    """
    Get the extension of the url
    :param url:
    :return:  The extension of the url
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    _, extension = os.path.splitext(path)
    return extension


def run_scrape(url, outfile, blacklist=None, enforce_subdir_depth=0, depth=5, width=-1):
    """
    Given the url, get the text and links, get the text and do a depth first search over all of the links
    and save the text of each of the file encountered to the outfile
    After the first page, only go to a link that is in the same domain and at the same level or below the level
    in the web page.
    :param url: URL to start the scrape
    :param outfile: Output file to save the text
    :param blacklist: List of urls to not scrape
    :param enforce_subdir_depth: Enforce that the link is in the same directory or below the directory of the url
    :param depth: Depth to go to
    :return: None
    """

    # Maintain a list of the visited pages
    visited_pages = []

    # This is the text that will be saved to the outfile
    all_page_text = ''

    # Add all the links to a stack for depth first search that are in the blacklist
    s = [(0, url)]

    # Do a depth first search over the links
    while len(s) > 0:
        # Get the next link
        link_depth, link = s.pop()

        # Get the text and links from the url
        print('Scraping', link, '(', link_depth, ')')
        try:
            page_text, links = scrape_page(link)
        except Exception as e:
            print('Error scraping', link, ':', e)
            continue

        # Append the text to the outfile
        all_page_text += page_text

        # If we have reached the link depth, do not go any further
        if link_depth == depth:
            continue

        # Check the width of the links and if it is greater than the width, choose width number of random
        # links to go to
        if 0 < width < len(links):
            links = random.sample(links, width)

        # Add all the links to a stack for depth first search that are in the blacklist, and not visited
        for new_link in links:
            # Ignore links that are None
            if new_link is None:
                continue
            # Ignore links that start with # as they are links to the same page
            if new_link.startswith('#'):
                continue
            # Ignore links that are in the blacklist
            if in_blacklist(new_link, blacklist):
                continue
            # Only go to a link that is in the same domain and at the same level or below the level in the web page.
            link_dir = get_url_dir(link)
            if link_depth > enforce_subdir_depth and link_dir not in new_link:
                continue
            # If this is a local link, add the url to the link
            if is_local_link(new_link):
                if new_link.startswith('/'):
                    continue
                new_link = urljoin(link, new_link)

            # Remove everything after # in the links as they are links to the same page
            if '#' in new_link:
                new_link = new_link.split('#')[0]

            # Check that we are scraping a html page (and not pdfs and ppts)
            if get_url_extension(new_link) != '' and get_url_extension(new_link) != '.html' and get_url_extension(
                    new_link) != '.htm':
                continue

            # Ignore links that are already visited
            if new_link in visited_pages or new_link in [link for _, link in s]:
                continue

            s.append((link_depth + 1, new_link))

            # Add the link to the visited pages
            visited_pages.append(new_link)

    # Remove all the blank lines in the full text
    all_page_text = '\n'.join([line for line in all_page_text.split('\n') if line.strip() != ''])

    # Append the text to the outfile
    with open(outfile, 'w') as f:
        f.write(all_page_text)


if __name__ == '__main__':
    scrape_textfile = 'visual-generative-ai-ecosystem-challenges.txt'
    scrape_url = 'https://twimlai.com/podcast/twimlai/visual-generative-ai-ecosystem-challenges/'

    # print(get_url_extension(scrape_url))
    run_scrape(scrape_url, scrape_textfile, blacklist=blacklist_sites, enforce_subdir_depth=0, depth=5)