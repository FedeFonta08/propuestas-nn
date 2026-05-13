from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def deep_search():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A:AY").execute()
    rows = result.get('values', [])
    
    print(f"Deep search for Maria Elvira related info...")
    
    for i, row in enumerate(rows):
        full_text = " ".join(row).lower()
        if "maria elvira" in full_text:
            print(f"Row {i+1}: {row}")
        if "hijo" in full_text and "elvira" in full_text:
            print(f"Row {i+1} (HIJO): {row}")

if __name__ == "__main__":
    deep_search()
