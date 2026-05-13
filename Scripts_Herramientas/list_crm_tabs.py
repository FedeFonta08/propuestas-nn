import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

CRM_SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json'

def list_tabs():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)
    metadata = service.spreadsheets().get(spreadsheetId=CRM_SHEET_ID).execute()
    for s in metadata.get('sheets', []):
        print(f"Tab: {s.get('properties', {}).get('title')}")

if __name__ == "__main__":
    list_tabs()
