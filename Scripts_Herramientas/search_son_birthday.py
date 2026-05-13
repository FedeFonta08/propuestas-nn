from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def search_son():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A:AY").execute()
    rows = result.get('values', [])
    
    print(f"Buscando menciones de 'hijo' en el CRM...")
    
    for i, row in enumerate(rows):
        full_text = " ".join(row).lower()
        if "hijo" in full_text and ("11-05" in full_text or "05-11" in full_text or "11/05" in full_text):
            print(f"Row {i+1}: {row}")

if __name__ == "__main__":
    search_son()
