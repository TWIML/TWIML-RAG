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
            os.makedirs(get_data_dirpath(required_dir))

def check_environment_vars():
    """
    Check if the required environment variables exist
    :return: None
    """
    required_env_vars = ['HUGGING_FACE_API_KEY', 'OPENAI_API_KEY']
    for required_env_var in required_env_vars:
        if required_env_var not in os.environ:
            raise Exception(f"Environment variable {required_env_var} not found")

if __name__ == '__main__':
    check_required_dirs()
    check_environment_vars()
