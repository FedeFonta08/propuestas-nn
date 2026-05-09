import os
import glob
import re
import sys
import json
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
carpeta_scripts = os.path.dirname(__file__)
load_dotenv(os.path.join(carpeta_scripts, ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERROR: No se ha encontrado GEMINI_API_KEY en el archivo .env")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ID del Google Sheet Real
SPREADSHEET_ID = '1mYKiIdoglAxzFwJOE_0V8CyHwNUsKkh_oPtkUKg4GCQ'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def extraer_texto_email(ruta_archivo):
    print(f"🔄 Leyendo correo: {os.path.basename(ruta_archivo)}")
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()
            
        contenido = re.sub(r'<style[^>]*>.*?</style>', '', contenido, flags=re.DOTALL)
        contenido = re.sub(r'<script[^>]*>.*?</script>', '', contenido, flags=re.DOTALL)
        texto_puro = re.sub(r'<[^>]+>', ' ', contenido)
        texto_puro = re.sub(r'\s+', ' ', texto_puro).strip()
        return texto_puro
    except Exception as e:
        print(f"❌ Error al leer el email: {e}")
        return ""

def procesar_con_ia(texto_email):
    print("🧠 Analizando el correo con el Super Prompt ADN (leyendo tu Manual Maestro)...")
    
    # Leer las reglas del ADN
    ruta_reglas = os.path.join(carpeta_scripts, 'reglas_adn.txt')
    reglas_adn = ""
    if os.path.exists(ruta_reglas):
        with open(ruta_reglas, 'r', encoding='utf-8') as f:
            reglas_adn = f.read()
            
    prompt = f"""
    Eres el Asistente Analítico de Élite de un Agente Dinamizador de Nationale-Nederlanden (Federico Fontanals). 
    Tu tarea es procesar el correo semanal corporativo 'Entre Nosotros' y estructurar la información para actualizar el Radar Comercial del agente.
    Aplica SIEMPRE la filosofía de venta consultiva (Análisis de Necesidades - ADN) basándote ESTRICTAMENTE en este manual:
    
    === MANUAL MAESTRO DEL ADN ===
    {reglas_adn}
    ==============================

    Devuelve ESTRICTAMENTE un objeto JSON válido con las siguientes tres claves principales. No devuelvas ningún texto fuera del JSON.

    {{
      "Campanias_Activas": [
        {{
          "Producto": "Nombre del producto",
          "Tipo_de_campania": "Ej. Descuento, Ampliación...",
          "Descripcion_del_beneficio": "Qué ofrece",
          "Fecha_inicio": "DD/MM/YYYY",
          "Fecha_fin": "DD/MM/YYYY",
          "Cupo_max": "Límite",
          "Descuento_Bonus": "Cifra",
          "Segmento_objetivo": "A quién va dirigido",
          "Vulnerabilidad_Detectada": "La debilidad o preocupación principal del cliente que este producto soluciona",
          "Pregunta_Apertura": "Pregunta consultiva para iniciar la conversación sin vender",
          "Estado": "🟢 ACTIVA o ⚡ URGENTE"
        }}
      ],
      "Novedades_Producto": [
        {{
          "Producto": "Nombre",
          "Que_ha_cambiado": "Descripción del cambio",
          "Tipo": "🟢 Mejora, 🔵 Operativo, o 🔴 Proceso Crítico",
          "Vigente_desde": "DD/MM/YYYY",
          "Afecta_guia_comercial": "SÍ / NO",
          "Accion_sobre_CRM": "Qué hacer en el CRM",
          "Impacto_segmento": "A qué segmento afecta",
          "Fuente": "Ej. Entre Nosotros"
        }}
      ],
      "Historial": {{
        "N_Edicion": "Número",
        "Resumen_ejecutivo": "Resumen de 3 líneas",
        "Campanias_nuevas": "Nombres de campañas",
        "Cambios_producto": "Cambios de productos",
        "N_acciones": "Número"
      }}
    }}

    TEXTO DEL CORREO:
    {texto_email}
    """
    
    try:
        response = model.generate_content(prompt)
        resultado = response.text.strip()
        if resultado.startswith("```json"):
            resultado = resultado.replace("```json", "", 1)
        if resultado.endswith("```"):
            resultado = resultado[:-3]
            
        return json.loads(resultado.strip())
    except Exception as e:
        print(f"❌ Error en la IA al procesar: {e}")
        return None

def get_gspread_client():
    creds = None
    token_path = os.path.join(carpeta_scripts, 'token.json')
    creds_path = os.path.join(carpeta_scripts, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"\\n❌ ATENCIÓN: Falta el archivo 'credentials.json'.")
                print("Debes descargarlo de Google Cloud Console y colocarlo en la carpeta Scripts_Herramientas.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return gspread.authorize(creds)

def actualizar_google_sheets(datos, client):
    print(f"🌐 Conectando directamente a Google Drive (Radar Online)...")
    try:
        sheet = client.open_by_key(SPREADSHEET_ID)
        fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y")
        
        # 1. Campañas Activas
        ws_camp = sheet.worksheet("🟠 Campañas Activas")
        for camp in datos.get("Campanias_Activas", []):
            ws_camp.append_row([
                camp.get("Producto", ""), camp.get("Tipo_de_campania", ""), camp.get("Descripcion_del_beneficio", ""),
                camp.get("Fecha_inicio", ""), camp.get("Fecha_fin", ""), camp.get("Cupo_max", ""),
                camp.get("Descuento_Bonus", ""), camp.get("Segmento_objetivo", ""),
                f"Vulnerabilidad: {camp.get('Vulnerabilidad_Detectada', '')} | Apertura: {camp.get('Pregunta_Apertura', '')}",
                camp.get("Estado", "")
            ])
            print(f"✅ Campaña insertada en la nube: {camp.get('Producto')}")

        # 2. Novedades Producto
        ws_nov = sheet.worksheet("📦 Novedades Producto")
        for nov in datos.get("Novedades_Producto", []):
            ws_nov.append_row([
                nov.get("Producto", ""), nov.get("Que_ha_cambiado", ""), nov.get("Tipo", ""),
                nov.get("Vigente_desde", ""), nov.get("Afecta_guia_comercial", ""), nov.get("Accion_sobre_CRM", ""),
                nov.get("Impacto_segmento", ""), nov.get("Fuente", "")
            ])
            # La parte del coloreado en Google Sheets requiere un poco más de código con batch_update,
            # lo añadiremos en cuanto verifiquemos que la inserción de texto en la nube funciona perfecto.
            print(f"✅ Novedad insertada en la nube: {nov.get('Producto')}")

        # 3. Historial
        ws_hist = sheet.worksheet("📋 Historial Entre Nosotros")
        hist = datos.get("Historial", {})
        if hist:
            ws_hist.append_row([
                hist.get("N_Edicion", ""), fecha_hoy, str(hist.get("Resumen_ejecutivo", "")),
                str(hist.get("Campanias_nuevas", "")), str(hist.get("Cambios_producto", "")),
                str(hist.get("N_acciones", "")), f"{fecha_hoy} · Gemini AI Automático"
            ])
            print(f"✅ Historial insertado en la nube.")

        print(f"\n✅ ¡GOOGLE DRIVE ACTUALIZADO CON ÉXITO!")
        return True
    except Exception as e:
        print(f"❌ Error al comunicar con Google Sheets: {e}")
        return False

def generar_briefing_html(datos):
    print("🎨 Generando Briefing_Lunes_ADN.html con tu branding corporativo...")
    ruta_html = os.path.join(carpeta_scripts, "Briefing_Lunes_ADN.html")
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Briefing ADN Lunes · NN</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --orange: #C94D00;
            --orange-l: #E85C0D;
            --dark: #F5F5F0;
            --navy: #111827;
            --text2: #374151;
            --card-bg: #FFFFFF;
            --card-border: rgba(0,0,0,0.12);
        }}
        body {{
            font-family: 'DM Sans', sans-serif;
            background-color: var(--dark);
            color: var(--navy);
            margin: 0;
            padding: 2rem;
            background-image: radial-gradient(ellipse 80% 50% at 10% 0%, rgba(201,77,0,0.04) 0%, transparent 60%);
        }}
        .header {{ max-width: 1000px; margin: 0 auto 2rem; border-bottom: 3px solid var(--orange); padding-bottom: 1rem; }}
        .logo-text {{ font-family: 'Bebas Neue', sans-serif; font-size: 32px; letter-spacing: 1.5px; color: var(--navy); }}
        .logo-text span {{ color: var(--orange); }}
        .subtitle {{ font-size: 13px; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto; }}
        .card {{ background: var(--card-bg); border: 2px solid var(--orange); border-radius: 14px; padding: 1.5rem; box-shadow: 0 8px 24px rgba(201,77,0,0.08); position: relative; overflow: hidden; }}
        .card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--orange); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }}
        .badge {{ background: #FFF8F5; color: var(--orange); padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: 1px solid rgba(201,77,0,0.2); }}
        .producto {{ font-family: 'Bebas Neue', sans-serif; font-size: 26px; line-height: 1.1; margin-top: 8px; }}
        .segmento {{ color: #16A34A; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
        .novedad {{ font-size: 14px; color: var(--text2); margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--card-border); }}
        
        .adn-box {{ background: #F9FAFB; border-left: 4px solid var(--navy); padding: 1rem; margin-bottom: 1rem; border-radius: 0 8px 8px 0; }}
        .adn-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--navy); margin-bottom: 4px; }}
        .adn-text {{ font-size: 14px; color: var(--text2); }}
        
        .apertura-box {{ background: #FFF8F5; border: 1.5px solid rgba(201,77,0,0.3); border-radius: 8px; padding: 1rem; }}
        .apertura-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--orange); margin-bottom: 6px; }}
        .apertura-text {{ font-size: 15px; font-weight: 600; font-style: italic; color: var(--navy); line-height: 1.4; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="subtitle">Briefing Semanal para Agentes</div>
        <div class="logo-text">TRADUCCIÓN ADN · <span>PANEL NN</span></div>
    </div>
    <div class="grid">
"""
    
    for camp in datos.get("Campanias_Activas", []):
        html += f"""
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="segmento">🎯 {camp.get('Segmento_objetivo', '')}</div>
                    <div class="producto">{camp.get('Producto', '')}</div>
                </div>
                <div class="badge">{camp.get('Estado', 'Activa')}</div>
            </div>
            <div class="novedad">{camp.get('Descripcion_del_beneficio', '')}</div>
            
            <div class="adn-box">
                <div class="adn-title">🔪 Vulnerabilidad Detectada (Bisturí ADN)</div>
                <div class="adn-text">{camp.get('Vulnerabilidad_Detectada', '')}</div>
            </div>
            
            <div class="apertura-box">
                <div class="apertura-title">🗣️ Pregunta de Apertura Consultiva</div>
                <div class="apertura-text">"{camp.get('Pregunta_Apertura', '')}"</div>
            </div>
        </div>
        """
        
    html += """
    </div>
</body>
</html>
"""
    with open(ruta_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ ¡Briefing Visual generado con éxito!")

def main():
    carpeta_base = r"D:\\Users\\ffont\\Downloads"
    archivos = glob.glob(os.path.join(carpeta_base, "*Entre Nosotros*.htm")) + \
               glob.glob(os.path.join(carpeta_base, "*Entre Nosotros*.eml")) + \
               glob.glob(os.path.join(carpeta_base, "*Urgente*.htm"))
    
    if not archivos:
        print("❌ No se encontró ningún correo para procesar.")
        return
        
    archivo_reciente = max(archivos, key=os.path.getctime)
    texto = extraer_texto_email(archivo_reciente)
    if not texto: return
    
    # 1. Autorizar primero (para fallar rápido si no hay token)
    client = get_gspread_client()
    
    # 2. Pensar con IA
    datos = procesar_con_ia(texto)
    
    # 3. Escribir en Google Sheets
    if datos:
        actualizar_google_sheets(datos, client)
        
    # 4. Generar Briefing HTML
    if datos:
        generar_briefing_html(datos)

if __name__ == "__main__":
    main()
