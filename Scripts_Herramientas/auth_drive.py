import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']
creds_path = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/credentials.json'
token_path = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'

if os.path.exists(token_path):
    os.remove(token_path)

print("Abriendo navegador para autorizar permisos de Drive...")
flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
creds = flow.run_local_server(port=0)

with open(token_path, 'w') as token:
    token.write(creds.to_json())

print("✅ Token guardado con éxito. Ya tengo permisos.")
