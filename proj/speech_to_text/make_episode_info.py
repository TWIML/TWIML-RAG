import os
import json


def make_episode_info(episode_info_json_filename):
    # Iterate through all the files in the info folder and create a dictionary by the episode number

    # Get all the files in the info directory
    info_files = os.listdir('info')

    # Sort the files by the episode number
    info_files = sorted(info_files)

    # Create a dictionary to store the info
    info_dict = {}
    for file in info_files:
        # Read the json file
        with open(os.path.join('info', file), 'r') as f:
            info = json.load(f)

        # Get the episode number
        episode_number = info['episode']

        # Get the title of the episode
        title = info['title']

        # Add it to the dictionary
        info_dict[episode_number] = title

    # Save the dictionary to a json file
    with open(episode_info_json_filename, 'w') as f:
        json.dump(info_dict, f, indent=2)


def get_episode_title(episode_info_json_filename, episode_num):
    # Read the json file
    with open(episode_info_json_filename, 'r') as f:
        info = json.load(f)

    # Get the episode number
    episode_title = info[str(episode_num)]

    return episode_title


if __name__ == '__main__':
    episode_info_json_filename = '../fn_rag/episode_info.json'
    make_episode_info(episode_info_json_filename)
    episode_title = get_episode_title(episode_info_json_filename, '123')
    print(episode_title)
