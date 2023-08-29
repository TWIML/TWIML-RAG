import os


def check_required_dirs():
    """
    Check if the required directories exist and create them if they don't
    :return: None
    """
    required_dirs = ['podcasts', 'asr', 'transcripts', 'markdown', 'rss']
    for required_dir in required_dirs:
        if not os.path.exists(required_dir):
            os.mkdir(required_dir)


if __name__ == '__main__':
    check_required_dirs()
