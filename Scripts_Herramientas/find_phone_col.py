from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import re

TOKEN_PATH = 'token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def find_phone_column():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A3:AZ10").execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found")
        return

    # Check each column for phone-like patterns
    for col_idx in range(len(values[0])):
        for row in values:
            if col_idx < len(row):
                val = str(row[col_idx]).replace(' ', '').replace('+', '')
                # Check for 9-11 digits (Spanish mobile or international)
                if val.isdigit() and 9 <= len(val) <= 12:
                    print(f"Potential phone column found: {col_idx} (Sample: {row[col_idx]})")
                    return col_idx
    print("No phone column found")
    return None

if __name__ == "__main__":
    find_phone_column()
