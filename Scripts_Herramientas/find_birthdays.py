from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def find_todays_birthdays():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Obtener datos del CRM
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A3:AY2000").execute()
    rows = result.get('values', [])
    
    today = datetime.date.today()
    # Para pruebas, supongamos que hoy es 11 de Mayo (según el prompt el tiempo actual es 2026-05-11)
    target_month = today.month
    target_day = today.day
    
    print(f"Buscando cumplea\u00f1os para hoy: {target_day}/{target_month}")
    
    found_today = []
    found_week = []
    
    for row in rows:
        if len(row) < 6: continue
        
        nombre = row[0]
        apellidos = row[1] if len(row) > 1 else ""
        tel = row[3] if len(row) > 3 else "N/A"
        cumple_raw = row[5]
        buyer = row[48] if len(row) > 48 else "Desconocido"
        
        if not cumple_raw or '-' not in cumple_raw: continue
        
        try:
            # Formato YYYY-MM-DD
            parts = cumple_raw.split('-')
            b_month = int(parts[1])
            b_day = int(parts[2])
            
            if b_month == target_month and b_day == target_day:
                found_today.append({
                    "nombre": nombre,
                    "apellidos": apellidos,
                    "tel": tel,
                    "cumple": cumple_raw,
                    "buyer": buyer
                })
            elif b_month == target_month and target_day < b_day <= target_day + 7:
                found_week.append({
                    "nombre": nombre,
                    "apellidos": apellidos,
                    "tel": tel,
                    "cumple": cumple_raw,
                    "buyer": buyer
                })
        except:
            continue

    print(f"\n--- CUMPLEA\u00d1OS DE HOY ({len(found_today)}) ---")
    for p in found_today:
        print(f"ALERTA: {p['nombre']} {p['apellidos']} | Tel: {p['tel']} | Buyer: {p['buyer']}")

    print(f"\n--- PR\u00d3XIMOS 7 D\u00cdAS ({len(found_week)}) ---")
    for p in found_week:
        print(f"{p['cumple']} | {p['nombre']} {p['apellidos']} | Buyer: {p['buyer']}")

if __name__ == "__main__":
    find_todays_birthdays()
