import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

CRM_SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json'

def get_crm_sample():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)
    
    # Fetch top 5 rows
    result = service.spreadsheets().values().get(spreadsheetId=CRM_SHEET_ID, range='CRM MAESTRO!A1:AZ5').execute()
    values = result.get('values', [])
    
    if not values:
        print("No values found")
        return

    for i, row in enumerate(values):
        print(f"\nROW {i}:")
        for j, val in enumerate(row):
            print(f"[{j}]: {val}")

if __name__ == "__main__":
    get_crm_sample()
