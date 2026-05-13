from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def deep_inspect_elvira():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!40:40").execute()
    row = result.get('values', [])[0]
    
    for i, val in enumerate(row):
        print(f"Col {i}: {val}")

if __name__ == "__main__":
    deep_inspect_elvira()
