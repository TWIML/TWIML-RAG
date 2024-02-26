import os
from common.files import get_data_dirpath


def check_required_dirs():
    """
    Check if the required directories exist and create them if they don't
    :return: None
    """
    required_dirs = ['podcasts', 'asr', 'transcripts', 'markdown', 'rss']
    for required_dir in required_dirs:
        if not os.path.exists(get_data_dirpath(required_dir)):
            os.mkdir(get_data_dirpath(required_dir))


if __name__ == '__main__':
    check_required_dirs()
