import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# IDs de las hojas
ID_RADAR_ORIGEN = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
ID_CRM_DESTINO = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

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

def fusionar_datos():
    client = get_gspread_client()
    
    print("Iniciando la Fusion de Inteligencia...")
    
    radar_origen = client.open_by_key(ID_RADAR_ORIGEN)
    crm_destino = client.open_by_key(ID_CRM_DESTINO)
    
    tabs_a_mover = {
        "RADAR COMERCIAL": "RADAR COMERCIAL",
        "NOVEDADES PRODUCTO": "NOVEDADES PRODUCTO",
        "DASHBOARD AGENCIA": "DASHBOARD AGENCIA"
    }
    
    for nombre_origen, nombre_destino in tabs_a_mover.items():
        try:
            ws_origen = radar_origen.worksheet(nombre_origen)
            datos = ws_origen.get_all_values()
            
            if not datos:
                print(f"La pestaña {nombre_origen} esta vacia.")
                continue
                
            # Intentar encontrar la pestaña de destino (o crearla)
            try:
                ws_destino = crm_destino.worksheet(nombre_destino)
            except gspread.exceptions.WorksheetNotFound:
                # Si no existe, la creamos (o usamos una que se parezca)
                print(f"Creando pestaña {nombre_destino} en el CRM Maestro...")
                ws_destino = crm_destino.add_worksheet(title=nombre_destino, rows=100, cols=20)
            
            # Limpiar y escribir
            ws_destino.clear()
            ws_destino.update('A1', datos)
            
            # Aplicar formato básico a la cabecera
            ws_destino.format('A1:Z1', {
                "backgroundColor": {"red": 0.79, "green": 0.30, "blue": 0.0}, # #C94D00
                "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
            })
            
            print(f"Migrados {len(datos)} registros a {nombre_destino}")
            
        except Exception as e:
            print(f"Error migrando {nombre_origen}: {e}")

    print("\nFusion completada con éxito! La Bestia ahora tiene su Radar integrado.")

if __name__ == "__main__":
    fusionar_datos()
