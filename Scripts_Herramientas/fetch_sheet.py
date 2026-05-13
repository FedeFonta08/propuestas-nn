import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json', ['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=creds)
sheet_id = '17axy3xp7ktqgYCy1_-aBZsdeHN5OLxRwXWxa27oZcGc'
sheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
sheets = sheet_metadata.get('sheets', '')

output = ""
for s in sheets:
    title = s.get('properties', {}).get('title', '')
    output += f"\n--- TAB: {title} ---\n"
    try:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=title).execute()
        values = result.get('values', [])
        for row in values:
            output += " | ".join([str(c) for c in row]) + "\n"
    except Exception as e:
        output += str(e) + "\n"

with open('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/tablero_temp.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print('Done')
