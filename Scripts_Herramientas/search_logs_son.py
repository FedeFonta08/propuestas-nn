from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def search_logs():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="'LOG_LLAMADAS'!A:Z").execute()
        rows = result.get('values', [])
        print(f"Buscando en LOG_LLAMADAS...")
        for i, row in enumerate(rows):
            full_text = " ".join(row).lower()
            if "hijo" in full_text and "elvira" in full_text:
                print(f"Row {i+1}: {row}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_logs()
