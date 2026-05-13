from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def search_by_date():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A:AY").execute()
    rows = result.get('values', [])
    
    print(f"Buscando todos los cumpleaños del 11 de mayo...")
    
    for i, row in enumerate(rows):
        try:
            full_text = " ".join(row)
            if "05-11" in full_text or "11-05" in full_text or "11/05" in full_text:
                clean_name = row[0] if len(row) > 0 else "N/A"
                print(f"Match found at Row {i+1}: {clean_name} | {row[5] if len(row) > 5 else ''}")
        except:
            continue

if __name__ == "__main__":
    search_by_date()
