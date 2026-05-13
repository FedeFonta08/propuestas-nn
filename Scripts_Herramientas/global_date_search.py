from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def global_search():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    
    spreadsheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheets = [s['properties']['title'] for s in spreadsheet.get('sheets', [])]
    
    print(f"Buscando '11/05' o '05-11' en todo el documento...")
    
    for sheet_name in sheets:
        try:
            result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=f"'{sheet_name}'!A:Z").execute()
            rows = result.get('values', [])
            for i, row in enumerate(rows):
                full_text = " ".join(row)
                if "11/05" in full_text or "05-11" in full_text or "11-05" in full_text:
                    print(f"Sheet: {sheet_name} | Row {i+1}: {row}")
        except:
            continue

if __name__ == "__main__":
    global_search()
