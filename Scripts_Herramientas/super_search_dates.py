from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def super_search():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    
    result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A:ZZ").execute()
    rows = result.get('values', [])
    
    print(f"Super search for '05-11' or '11/05' in ALL columns...")
    
    for i, row in enumerate(rows):
        full_text = " ".join(row)
        if "05-11" in full_text or "11/05" in full_text or "11-05" in full_text:
            clean_name = row[0] if len(row) > 0 else "N/A"
            print(f"Found at Row {i+1}: {clean_name} | Content: {full_text[:100]}...")

if __name__ == "__main__":
    super_search()
