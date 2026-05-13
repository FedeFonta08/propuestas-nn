from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def check_birthday_data():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Obtener nombres y cumpleaños
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A3:F50").execute()
    rows = result.get('values', [])
    
    print("Sample birthday data:")
    for row in rows:
        nombre = row[0] if len(row) > 0 else "N/A"
        cumple = row[5] if len(row) > 5 else "N/A"
        if cumple != "N/A" and cumple.strip():
            print(f"{nombre}: {cumple}")

if __name__ == "__main__":
    check_birthday_data()
