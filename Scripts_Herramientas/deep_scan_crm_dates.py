from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def deep_scan_crm():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Obtener las primeras 10 filas para ver datos reales
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!1:10").execute()
    rows = result.get('values', [])
    
    if not rows:
        print("No rows found")
        return

    headers = rows[1] # La fila 2 son los headers reales según el script anterior
    data = rows[2:]

    print(f"Scanning {len(headers)} columns...")
    
    date_cols = []
    for i, header in enumerate(headers):
        # Buscar palabras clave o patrones de fecha en los datos
        is_date = False
        if any(keyword in header.lower() for keyword in ['fecha', 'vto', 'mes', 'nacimiento', 'cumple', 'cita']):
            is_date = True
        
        # O verificar si los datos parecen fechas (ej: dd/mm/aaaa)
        for row in data:
            if i < len(row):
                val = str(row[i])
                if '/' in val and len(val) >= 8:
                    is_date = True
                    break
        
        if is_date:
            date_cols.append((i, header))

    for idx, name in date_cols:
        print(f"Column {idx} ({chr(65+idx) if idx < 26 else '?' }): {name}")

if __name__ == "__main__":
    deep_scan_crm()
