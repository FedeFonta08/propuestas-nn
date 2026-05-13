import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('drive', 'v3', credentials=creds)

def scan_all():
    service = get_service()
    
    # 1. Listar Hojas de Cálculo (Spreadsheets)
    print("Listing Spreadsheets...")
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
        fields="files(id, name, modifiedTime)",
        pageSize=100
    ).execute()
    spreadsheets = results.get('files', [])
    
    # 2. Listar Archivos HTML y PDFs en carpetas clave
    # Carpetas clave: Herramientas Comerciales (13_9tYkprgZdGTKZZN-I-2QSfVAgrplAe), 03 · Guías Maestras (1yWhmtI9k4mFDPAeEy4Mb0oVNELwgZ-ke)
    print("Listing HTML and PDF tools...")
    results = service.files().list(
        q="(mimeType='text/html' or mimeType='application/pdf') and trashed=false",
        fields="files(id, name, parents, modifiedTime)",
        pageSize=200
    ).execute()
    tools = results.get('files', [])

    analysis = {
        "spreadsheets": spreadsheets,
        "tools": tools
    }

    with open('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/analisis_exhaustivo_drive.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis saved to analisis_exhaustivo_drive.json. Found {len(spreadsheets)} spreadsheets and {len(tools)} tools.")

if __name__ == "__main__":
    scan_all()
