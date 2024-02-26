import os
import re
import unicodedata
from tqdm import tqdm

def sanitize_filename(filename):
    """
    Sanitize the filename to remove any characters that are not allowed in filenames
    @param filename:  Filename to sanitize
    @return: Sanitized filename
    """
    # Normalize unicode characters
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')

    # Replace invalid characters with an underscore
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)

    # Truncate to 255 characters to handle length limits
    filename = filename[:255]

    # Avoid reserved filenames in Windows
    reserved_names = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in
                                                                                         range(1, 10)}
    if filename in reserved_names:
        filename = "_" + filename

    return filename

def get_data_filepath(dir, name):
    """
    Get the filepath of the filename
    :param filename: Filename
    :return: Filepath
    """
    return os.path.join(get_data_dirpath(dir), name)

def get_data_dirpath(dir):
    """
    Get the directory path
    :param dir: Directory
    :return: Directory path
    """
    return os.path.join("data", dir)

def tqdm_file_list(directory, desc="Processing", position=None, leave=True):
    file_list = os.listdir(directory)
    return tqdm(enumerate(file_list), total=len(file_list), desc=desc)