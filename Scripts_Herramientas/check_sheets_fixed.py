from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def check_sheets():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheets = spreadsheet.get('sheets', [])
    
    print("Sheets in this spreadsheet:")
    for s in sheets:
        title = s['properties']['title']
        clean_title = title.encode('ascii', 'ignore').decode('ascii')
        print(f"- {clean_title}")

if __name__ == "__main__":
    check_sheets()
