import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

CRM_SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json'

def get_crm_headers():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)
    
    # Fetch from CRM MAESTRO tab
    result = service.spreadsheets().values().get(spreadsheetId=CRM_SHEET_ID, range='CRM MAESTRO!A1:AZ2').execute()
    values = result.get('values', [])
    
    if not values:
        print("No values found")
        return

    headers = values[0]
    print("\n--- CRM MAESTRO HEADERS ---")
    for i, h in enumerate(headers):
        print(f"Col {i}: {h}")

if __name__ == "__main__":
    get_crm_headers()
