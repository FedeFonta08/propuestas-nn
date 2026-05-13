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
        try:
            full_text = " ".join(row).lower()
            if "maria elvira" in full_text or ("hijo" in full_text and "elvira" in full_text):
                clean_row = [str(x).encode('ascii', 'ignore').decode('ascii') for x in row]
                print(f"Match at Row {i+1}: {clean_row}")
        except:
            continue

if __name__ == "__main__":
    deep_search()
