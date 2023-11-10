from google.auth.transport.requests import Request
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

def gcloud_auth():
  credentials = None

  try:
    credentials, _ = default(
        scopes=['https://www.googleapis.com/auth/drive'],
    )
  except DefaultCredentialsError:
    print('No credentials found. Run gcloud auth application-default login'
          ' --impersonate-service-account SERVICE_ACCOUNT_EMAIL to configure '
          'the service account, or set the GOOGLE_APPLICATION_CREDENTIALS '
          'environment variable to a service account key file.')

  if credentials and not credentials.valid:
    credentials.refresh(Request())

  if credentials and credentials.valid:
    print("Credentials valid.")
    return credentials
  else:
    print("Credentials invalid.")
    return None

if __name__ == '__main__':
    gcloud_auth()