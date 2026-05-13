import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json', ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=creds)

# Buscamos todas las carpetas
results = service.files().list(
    q="mimeType='application/vnd.google-apps.folder' and trashed=false",
    fields="files(id, name)",
    pageSize=100
).execute()

folders = results.get('files', [])

output = "=== CARPETAS EN TU GOOGLE DRIVE ===\n"
for f in folders:
    output += f"- {f['name']} (ID: {f['id']})\n"

with open('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/drive_folders.txt', 'w', encoding='utf-8') as file:
    file.write(output)

print("Done")
