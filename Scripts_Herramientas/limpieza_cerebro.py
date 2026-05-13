import os
import sys
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ID del Google Sheet
SPREADSHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_gspread_client():
    carpeta_scripts = os.path.dirname(__file__)
    token_path = os.path.join(carpeta_scripts, 'token.json')
    creds_path = os.path.join(carpeta_scripts, 'credentials.json')

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return gspread.authorize(creds)

def clean_and_lift():
    client = get_gspread_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    
    print("Iniciando limpieza del 'Cerebro de la Bestia'...")
    
    all_sheets = spreadsheet.worksheets()
    for s in all_sheets:
        print(f"Hoja: {s.title.encode('ascii', 'ignore').decode()}")
    
    # 1. Pestañas a eliminar (el "Altillo")
    pestañas_viejas = ["MAYO", "JUNIO"]
    
    for nombre in pestañas_viejas:
        target = None
        for s in all_sheets:
            if nombre in s.title.upper():
                target = s
                break
        
        if target:
            try:
                spreadsheet.del_worksheet(target)
                print(f"Eliminada pestana antigua: {nombre}")
            except Exception as e:
                print(f"No se pudo eliminar {nombre}: {e}")

    # 2. Asegurar que RADAR COMERCIAL y DASHBOARD AGENCIA tengan cabeceras premium
    # Buscamos por coincidencia parcial para evitar problemas de emojis
    radar = None
    for s in all_sheets:
        if "RADAR" in s.title.upper():
            radar = s
            break
            
    if radar:
        try:
            # Si está vacía, poner cabeceras
            if not radar.get('A1:A1'):
                headers = ["Producto", "Tipo Campaña", "Beneficio", "Inicio", "Fin", "Cupo", "Descuento", "Segmento", "Vulnerabilidad/Apertura", "Estado"]
                radar.update('A1:J1', [headers])
                # Formato: Negrita y fondo naranja
                radar.format('A1:J1', {
                    "backgroundColor": {"red": 0.79, "green": 0.30, "blue": 0.0}, # #C94D00
                    "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                })
                print("Cabeceras premium añadidas a RADAR COMERCIAL.")
        except Exception as e:
            print(f"Error configurando RADAR: {e}")
    else:
        print("No se encontró la pestaña RADAR COMERCIAL.")

    print("\nOperacion Limpieza completada! Revisa tu Google Sheet.")

if __name__ == "__main__":
    clean_and_lift()
