import datetime
import os

from google_cloud_auth import gcloud_auth
from google_cloud_utils import get_rag_drive_id, get_drive_folder_id, drive_query
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def main():
    creds = gcloud_auth()

    if creds is None or not creds.valid:
        print('Service account credentials not found. Exiting.')
        exit(1)

    # Build the Google Drive API client
    service = build('drive', 'v3', credentials=creds)

    drive_id = get_rag_drive_id(service)
    
    #Get the folder id for the output transcripts folder
    folder_id = get_drive_folder_id(service,query=f"'{drive_id}' in parents and name='output transcripts'")

    #Get the folder id for the transcripts folder
    folder_id = get_drive_folder_id(service, query=f"'{folder_id}' in parents and name='transcripts'")
    
    # Get the list of files in the folder transcripts and get the file modified date and time
    remote_files = {}
    items = drive_query(service, query=f"'{folder_id}' in parents")

    if len(items) > 0:
        for item in items:
            remote_files[item['name']] = (item['id'], item.get('createdTime'))

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
