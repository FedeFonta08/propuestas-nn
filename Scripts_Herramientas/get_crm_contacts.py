import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Using the ID from Guion_Operacional_NN.md
CRM_SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json'

def get_contacts():
    if not os.path.exists(TOKEN_PATH):
        print(f"Error: Token not found at {TOKEN_PATH}")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)
    
    # Get the first sheet (usually the main one)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=CRM_SHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    if not sheets:
        print("No sheets found")
        return
        
    title = sheets[0].get('properties', {}).get('title', 'Hoja 1')
    print(f"Fetching from: {title}")
    
    result = service.spreadsheets().values().get(spreadsheetId=CRM_SHEET_ID, range=title).execute()
    values = result.get('values', [])
    
    if not values:
        print("No values found")
        return

    # Just show headers and first 5 rows to understand structure
    for i, row in enumerate(values[:6]):
        print(f"Row {i}: {' | '.join([str(c) for c in row[:15]])}") # Only first 15 columns for brevity

if __name__ == "__main__":
    get_contacts()
