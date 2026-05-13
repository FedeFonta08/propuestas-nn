from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'

def add_salud_campaign():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Datos de la campaña extraídos del PDF
    row = [
        "Salud Completo / Copago",
        "Descuento Anual",
        "12,5% de descuento en la primera anualidad para nuevas altas.",
        "17/03/2026",
        "01/06/2026",
        "Sin límite",
        "12,5%",
        "Nuevos Clientes",
        "Aplicar descuento 12,5% en cotizaciones de Salud. Acumulable a otras promos.",
        "🟢 ACTIVA"
    ]
    
    body = {
        'values': [row]
    }
    
    result = sheet.values().append(
        spreadsheetId=SHEET_ID,
        range="'RADAR COMERCIAL'!A:J",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    print(f"Campañan de Salud añadida al Radar: {result.get('updates').get('updatedRange')}")

if __name__ == "__main__":
    add_salud_campaign()
