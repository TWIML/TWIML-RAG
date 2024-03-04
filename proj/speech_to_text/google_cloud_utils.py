import os
from google.cloud import secretmanager
from googleapiclient.http import MediaFileUpload
from google_cloud_auth import gcloud_auth
from googleapiclient.discovery import build
from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv(".config"))


def get_drive_client():
    creds = gcloud_auth()

    if creds is None or not creds.valid:
        print('Service account credentials not found. Exiting.')
        exit(1)

    # Build the Google Drive API client
    service = build('drive', 'v3', credentials=creds)
    return service


def get_latest_episode_from_drive():
    service = get_drive_client()
    drive_id = get_rag_drive_id()
    folder_id = get_drive_folder_id(service, query=f"'{drive_id}' in parents and name='output transcripts'")
    folder_id = get_drive_folder_id(service, query=f"'{folder_id}' in parents and name='transcripts'")

    items = drive_query(service, query=f"'{folder_id}' in parents and trashed=false")
    latest_ep = max([int(item['name'].split('.')[0]) for item in items if item['name'].split('.')[0].isnumeric()])
    print(f'Latest episode from drive: {latest_ep}')
    return latest_ep


def get_rag_drive_id():
    return config['DRIVE_FOLDER_ID']


def drive_query(service, query):
    twiml_rag_drive = get_rag_drive_id()
    page_token = None
    items = []
    pages = 0
    while True:
        results = service.files().list(q=query,
                                       corpora='drive', driveId=twiml_rag_drive, supportsAllDrives=True,
                                       includeItemsFromAllDrives=True, pageToken=page_token).execute()

        page = results.get('files')
        # pages += 1
        # if len(page) > 0:
        #     print(f'Page {pages}: {len(page)} items')

        if page:
            items.append(page)

        page_token = results.get('nextPageToken')

        if not page_token:
            break

    items = [item for sublist in items for item in sublist]
    # print(f'Flattened items: {len(items)}')
    return items


def get_drive_folder_id(service, query=''):
    items = drive_query(service, query)

    try:
        folder_id = items[0]['id']
    except IndexError:
        raise Exception(f'Folder not found')

    # print(f'Folder id: {folder_id}')
    return folder_id


def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f'projects/{config["GCP_PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')


def upload_files_to_drive(files, gd_folder_name, skip_existing=True):
    """
    Upload the given files to the given folder in Google Drive
    If the file already exists, the file is trashed and a new file is uploaded if skip_existing is False

    @param files: List of files to upload with path relative to current dir (proj/speech_to_text) or absolute path
    @param gd_folder_name: Name of the folder in Google Drive to upload the files to
    @param skip_existing: If True, skip the file if it already exists in Google Drive. Otherwise trash
    """
    service = get_drive_client()
    drive_id = get_rag_drive_id()

    # Get the folder id for the output transcripts folder
    folder_id = get_drive_folder_id(service, query=f"'{drive_id}' in parents and name='output transcripts'")

    # Get the folder id for the transcripts folder
    folder_id = get_drive_folder_id(service, query=f"'{folder_id}' in parents and name='{gd_folder_name}'")

    # Iterate through all the given files
    for filename in files:
        # Get the file name without the path
        filename_only = os.path.basename(filename)

        # Check that the file exists or not in the google cloud folder and not marked as trashed
        items = drive_query(service, query=f"'{folder_id}' in parents and trashed=false and name='{filename_only}'")
        if len(items) > 0:
            if skip_existing:
                print(f'File {filename} already exists in Google Drive. Skipping ...')
                continue

            # Since we are not skipping existing files, mark the found file as trash
            print(f'File {filename} already exists in Google Drive. Trashing to upload new one ...')
            for item in items:
                service.files().update(fileId=item['id'], body={'trashed': True}, supportsAllDrives=True).execute()

        # Upload the new file
        file_metadata = {'name': filename_only, 'parents': [folder_id]}
        print(f'Uploading file {filename} to Google Drive folder {gd_folder_name} as file {filename_only}')
        media = MediaFileUpload(filename, mimetype='application/json')
        service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True).execute()
        print(f'Uploaded file {filename} to Google Drive')


if __name__ == '__main__':
    print(get_latest_episode_from_drive())
