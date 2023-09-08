import datetime
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except FileNotFoundError:
        pass

    # If there are no (valid) credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Google Drive API client
    service = build('drive', 'v3', credentials=creds)

    # Go to the shared drive TWIML-RAG
    results = service.drives().list().execute()
    # Go to the TWIML-RAG drive
    for drive in results['drives']:
        if drive['name'] == 'TWIML-RAG':
            drive_id = drive['id']
            break
    else:
        raise Exception('TWIML-RAG drive not found')

    # Go into the folder TWIML-RAG/output transcripts/transcripts
    folder_id = ''
    results = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                   corpora='drive', driveId=drive_id, supportsAllDrives=True,
                                   includeItemsFromAllDrives=True).execute()
    items = results.get('files', [])
    for item in items:
        if item['name'] == 'output transcripts':
            folder_id = item['id']
            break
    if folder_id == '':
        raise Exception('output transcripts folder not found')

    results = service.files().list(corpora='drive', driveId=drive_id, supportsAllDrives=True,
                                   includeItemsFromAllDrives=True, q=f"'{folder_id}' in parents").execute()
    items = results.get('files', [])
    for item in items:
        if item['name'] == 'transcripts':
            folder_id = item['id']
            break

    # Get the list of files in the folder transcripts using pagination and get the file modified date and time
    remote_files = {}
    page_token = None
    while True:
        results = service.files().list(corpora='drive',
                                       fields='nextPageToken, files(id, name, createdTime)',
                                       driveId=drive_id, supportsAllDrives=True,
                                       includeItemsFromAllDrives=True, q=f"'{folder_id}' in parents",
                                       pageToken=page_token).execute()
        items = results.get('files', [])
        for item in items:
            remote_files[item['name']] = (item['id'], item.get('createdTime'))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    # Iterate through the files in the transcripts folder locally and upload them to the transcripts folder in
    # Google Drive
    for filename in os.listdir('transcripts'):
        # Get the created time of the filename
        filename_full = os.path.join('transcripts', filename)
        created_time = os.path.getctime(filename_full)

        # Change the modified time to a string format of '2023-09-03T16:58:42.000Z'
        created_time = datetime.datetime.fromtimestamp(created_time).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        # Check if the file exists in the remote files and if it does check if the modified time is the same
        # print(filename)
        if filename in remote_files:
            # print(f'File {filename} already exists {remote_files[filename][0]}')
            if created_time == remote_files[filename][1]:
                print(f'File {filename} already exists and has the same modified time. Skipping ...')
                continue
            else:
                # This part does not seem to be working

                # Delete the file from Google Drive
                service.files().delete(fileId=remote_files[filename][0], supportsAllDrives=True).execute()
                print (f'File {filename} already exists but has a different created time of {remote_files[filename][1]}')
                print (f'Local file has a created time of {created_time}')
                print(f'Deleted file {filename} from Google Drive')

                # Upload the new file
                file_metadata = {'name': filename, 'parents': [folder_id]}
                media = MediaFileUpload(filename_full, mimetype='application/json')
                service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True).execute()
                print(f'Uploaded file {filename} to Google Drive')
        else:
            # Upload the new file
            file_metadata = {'name': filename, 'parents': [folder_id]}
            print(f'Uploading file {filename} to Google Drive')
            media = MediaFileUpload(filename_full, mimetype='application/json')
            service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True).execute()
            print(f'Uploaded file {filename} to Google Drive')


if __name__ == '__main__':
    main()
