import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FILE_ID = '1W06sIIN9kZK1Ry59e9-lC_e6ewuvAybS' # index_RADAR_CORREGIDO.html
DEST_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/index.html'

def download_file():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    request = service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    with open(DEST_PATH, 'wb') as f:
        f.write(fh.getvalue())
    
    print(f"File downloaded to {DEST_PATH}")

if __name__ == "__main__":
    download_file()
