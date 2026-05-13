import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']

# Rutas relativas al script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(BASE_DIR, 'credentials.json')
token_path = os.path.join(BASE_DIR, 'token_drive.json')

if os.path.exists(token_path):
    os.remove(token_path)

print("--- REGENERACIÓN DE TOKEN GOOGLE DRIVE ---")
print("Abriendo navegador para autorizar permisos...")

try:
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    print("\n✅ EXITO: Token guardado localmente en Scripts_Herramientas/token_drive.json")
    print("\n--- INSTRUCCIONES PARA GITHUB ---")
    print("Para que GitHub Actions vuelva a funcionar, debes actualizar el Secret:")
    print("1. Abre el archivo Scripts_Herramientas/token_drive.json")
    print("2. Copia TODO su contenido.")
    print("3. Ve a GitHub > Settings > Secrets > Actions.")
    print("4. Actualiza 'GOOGLE_TOKEN_JSON' con el nuevo contenido.")
except Exception as e:
    print(f"\n❌ Error durante la autenticación: {e}")

