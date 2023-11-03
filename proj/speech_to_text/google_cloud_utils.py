from google.cloud import secretmanager
from google_cloud_auth import gcloud_auth
from googleapiclient.discovery import build

PROJECT_NAME = 'twiml-rag'
PROJECT_ID = '570511745125'
BUCKET = 'twiml-rag-1'
METADATA_FOLDER = 'metadata'
LATEST_EP_BLOB = 'last-ep-processed'

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
    drive_id = get_rag_drive_id(service)
    folder_id = get_drive_folder_id(service,query=f"'{drive_id}' in parents and name='output transcripts'")
    folder_id = get_drive_folder_id(service, query=f"'{folder_id}' in parents and name='transcripts'")

    items = drive_query(service, query=f"'{folder_id}' in parents")
    latest_ep = max([int(item['name'].split('.')[0]) for item in items if item['name'].split('.')[0].isnumeric()])
    print(f'Latest episode from drive: {latest_ep}')
    return latest_ep

def get_rag_drive_id(service):

    # Go to the shared drive TWIML-RAG
    results = service.drives().list().execute()
    # Go to the TWIML-RAG drive
    for drive in results['drives']:
        if drive['name'] == 'TWIML-RAG':
            drive_id = drive['id']
            break
    else:
        raise Exception('TWIML-RAG drive not found')
    
    return drive_id

def drive_query(service, query):
    twiml_rag_drive = get_rag_drive_id(service)
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
    name = f'projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

if __name__ == '__main__':
    print(get_latest_episode_from_drive())
