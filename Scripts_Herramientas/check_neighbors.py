from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def check_neighbors():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Ver filas alrededor de Maria Elvira (Fila 40)
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A38:F45").execute()
    rows = result.get('values', [])
    
    print("Neighbors of Maria Elvira:")
    for i, row in enumerate(rows):
        print(f"Row {i+38}: {row}")

if __name__ == "__main__":
    check_neighbors()
