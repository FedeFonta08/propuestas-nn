import os
import glob
import re
import sys
import json
import datetime
import subprocess
import email
from email import policy
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

# ID del Google Sheet Real (Sistema_Gestion_NN_v4_BuyerPersona)
SPREADSHEET_ID = '1mYKiIdoglAxzFwJOE_0V8CyHwNUsKkh_oPtkUKg4GCQ'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def extraer_texto_email(ruta_archivo):
    print(f"🔄 Leyendo correo: {os.path.basename(ruta_archivo)}")
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()

        # Check if it looks like an MHT/EML by parsing with email module
        if "Content-Type: multipart" in contenido or ruta_archivo.lower().endswith(('.mht', '.eml')):
            msg = email.message_from_string(contenido, policy=policy.default)
            partes_texto = []
            for part in msg.walk():
                # We only want text/plain or text/html
                if part.get_content_type() in ['text/plain', 'text/html']:
                    try:
                        partes_texto.append(part.get_content())
                    except:
                        pass
            if partes_texto:
                contenido = " ".join(partes_texto)

        # Then apply HTML cleanup
        contenido = re.sub(r'<style[^>]*>.*?</style>', '', contenido, flags=re.DOTALL)
        contenido = re.sub(r'<script[^>]*>.*?</script>', '', contenido, flags=re.DOTALL)
        texto_puro = re.sub(r'<[^>]+>', ' ', contenido)
        
        # Remove any large base64 chunks that might have snuck in (long words without spaces)
        texto_puro = re.sub(r'\b[A-Za-z0-9+/]{100,}={0,2}\b', '', texto_puro)
        
        texto_puro = re.sub(r'\s+', ' ', texto_puro).strip()
        
        # Limit the size just in case, first 30,000 chars should be enough for any email
        return texto_puro[:30000]
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
      "Campañas_Activas": [
        {{
          "Producto": "Nombre del producto",
          "Tipo_de_campaña": "Ej. Descuento, Ampliación...",
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
        "Campañas_nuevas": "Nombres de campañas",
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
    campañas_viejas_para_html = []
    try:
        sheet = client.open_by_key(SPREADSHEET_ID)
        fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y")
        
        # 1. RADAR COMERCIAL (Integradas en RADAR COMERCIAL o Campañas Activas)
        ws_camp = None
        for s in sheet.worksheets():
            if "RADAR" in s.title.upper() or "CAMPA" in s.title.upper():
                ws_camp = s
                break
        if not ws_camp:
            ws_camp = sheet.worksheet("RADAR COMERCIAL")
        
        registros_existentes = ws_camp.get_all_values()
        productos_existentes = [row[0].strip().lower() if row else "" for row in registros_existentes]
        
        nuevas_campañas_nombres = [c.get("Producto", "").strip().lower() for c in datos.get("Campañas_Activas", [])]

        for camp in datos.get("Campañas_Activas", []):
            prod_nombre = camp.get("Producto", "").strip()
            fila_nueva = [
                prod_nombre, camp.get("Tipo_de_campaña", ""), camp.get("Descripcion_del_beneficio", ""),
                camp.get("Fecha_inicio", ""), camp.get("Fecha_fin", ""), camp.get("Cupo_max", ""),
                camp.get("Descuento_Bonus", ""), camp.get("Segmento_objetivo", ""),
                f"Vulnerabilidad: {camp.get('Vulnerabilidad_Detectada', '')} | Apertura: {camp.get('Pregunta_Apertura', '')}",
                camp.get("Estado", "")
            ]
            
            if prod_nombre.lower() in productos_existentes:
                # Actualizar
                idx = productos_existentes.index(prod_nombre.lower()) + 1
                try:
                    ws_camp.update(f"A{idx}:J{idx}", [fila_nueva])
                except Exception:
                    ws_camp.update([fila_nueva], f"A{idx}:J{idx}") # Fallback for different gspread versions
                print(f"🔄 Campaña actualizada en la nube: {prod_nombre}")
            else:
                ws_camp.append_row(fila_nueva)
                productos_existentes.append(prod_nombre.lower())
                print(f"✅ Campaña insertada en la nube: {prod_nombre}")
                
        # Extraer las campañas viejas que siguen activas para el HTML
        for row in registros_existentes[1:]:
            if not row or not row[0].strip(): continue
            prod_viejo = row[0].strip()
            if prod_viejo.lower() not in nuevas_campañas_nombres:
                estado_viejo = row[9] if len(row) > 9 else ""
                if "FINALIZADA" not in estado_viejo.upper():
                    vul_ap = row[8] if len(row) > 8 else ""
                    vul = vul_ap
                    ap = ""
                    if " | Apertura: " in vul_ap:
                        partes = vul_ap.split(" | Apertura: ")
                        vul = partes[0].replace("Vulnerabilidad: ", "").strip()
                        ap = partes[1].strip() if len(partes) > 1 else ""
                    
                    campañas_viejas_para_html.append({
                        "Producto": prod_viejo,
                        "Segmento_objetivo": row[7] if len(row) > 7 else "",
                        "Estado": estado_viejo,
                        "Descripcion_del_beneficio": row[2] if len(row) > 2 else "",
                        "Vulnerabilidad_Detectada": vul,
                        "Pregunta_Apertura": ap,
                    })

        # 2. NOVEDADES PRODUCTO
        ws_nov = ws_camp # Usamos la misma si no hay una específica
        for s in sheet.worksheets():
            if "NOVEDADES" in s.title.upper():
                ws_nov = s
                break
        for nov in datos.get("Novedades_Producto", []):
            ws_nov.append_row([
                nov.get("Producto", ""), nov.get("Que_ha_cambiado", ""), nov.get("Tipo", ""),
                nov.get("Vigente_desde", ""), nov.get("Afecta_guia_comercial", ""), nov.get("Accion_sobre_CRM", ""),
                nov.get("Impacto_segmento", ""), nov.get("Fuente", "")
            ])
            print(f"✅ Novedad insertada en la nube: {nov.get('Producto')}")

        # 3. Historial (DASHBOARD AGENCIA)
        ws_hist = ws_camp
        for s in sheet.worksheets():
            if "DASHBOARD" in s.title.upper() or "HISTORIAL" in s.title.upper():
                ws_hist = s
                break
        hist = datos.get("Historial", {})
        if hist:
            ws_hist.append_row([
                hist.get("N_Edicion", ""), fecha_hoy, str(hist.get("Resumen_ejecutivo", "")),
                str(hist.get("Campañas_nuevas", "")), str(hist.get("Cambios_producto", "")),
                str(hist.get("N_acciones", "")), f"{fecha_hoy} · Gemini AI Automático"
            ])
            print(f"✅ Historial insertado en la nube.")

        print(f"\n✅ ¡GOOGLE DRIVE ACTUALIZADO CON ÉXITO!")
        
        # Exportar a JSON para el Dashboard dinámico
        exportar_json_dashboard(datos, campañas_viejas_para_html)
        
        return campañas_viejas_para_html
    except Exception as e:
        print(f"❌ Error al comunicar con Google Sheets: {e}")
        return campañas_viejas_para_html

def exportar_json_dashboard(datos, campañas_viejas):
    print("📂 Exportando base de datos JSON para el Panel Despegue...")
    ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), "radar_db.json")
    
    # Combinar campañas nuevas y viejas
    todas = datos.get("Campañas_Activas", [])
    nombres_nuevas = [c.get("Producto", "").lower() for c in todas]
    
    for c in campañas_viejas:
        if c.get("Producto", "").lower() not in nombres_nuevas:
            todas.append(c)
            
    db = {
        "ultima_actualizacion": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "campanas": todas,
        "novedades": datos.get("Novedades_Producto", []),
        "historial": datos.get("Historial", {})
    }
    
    try:
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        print(f"✅ Archivo {os.path.basename(ruta_json)} generado.")
    except Exception as e:
        print(f"❌ Error al exportar JSON: {e}")

def generar_briefing_html(datos, campañas_viejas):
    print("🎨 Generando Briefing_Lunes_ADN.html en el repositorio público...")
    ruta_html = r"D:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\Scripts_Herramientas\Briefing_Lunes_ADN.html"
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Briefing ADN Lunes · NN</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --orange: #B33600; /* Naranja más oscuro para mayor contraste */
            --orange-l: #D94A00;
            --dark: #EAEAEA; /* Fondo general un poco más oscuro para contrastar con las tarjetas blancas */
            --navy: #000000; /* Texto principal en negro puro */
            --text2: #111111; /* Texto secundario casi negro */
            --card-bg: #FFFFFF;
            --card-border: rgba(0,0,0,0.3); /* Bordes más oscuros */
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
        
        .section-title {{ max-width: 1000px; margin: 3rem auto 1.5rem; font-family: 'Bebas Neue', sans-serif; font-size: 28px; color: var(--navy); letter-spacing: 1px; display: flex; align-items: center; gap: 10px; }}
        .section-desc {{ max-width: 1000px; margin: -1rem auto 2rem; font-size: 14px; color: var(--text2); background: #FFF8F5; border-left: 4px solid var(--orange); padding: 1rem; border-radius: 4px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto; }}
        .card {{ background: var(--card-bg); border: 2px solid var(--orange); border-radius: 14px; padding: 1.5rem; box-shadow: 0 8px 24px rgba(201,77,0,0.08); position: relative; overflow: hidden; }}
        .card.vieja {{ border-color: rgba(0,0,0,0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
        .card.vieja::before {{ background: #9CA3AF; }}
        .card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--orange); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }}
        .badge {{ background: #FFF8F5; color: var(--orange); padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: 1px solid rgba(201,77,0,0.2); }}
        .card.vieja .badge {{ background: #F3F4F6; color: #4B5563; border-color: rgba(0,0,0,0.1); }}
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
    
    <div class="section-title">✨ NOVEDADES DE LA SEMANA</div>
    <div class="grid">
"""
    
    for camp in datos.get("Campañas_Activas", []):
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
    
    <div class="section-title" style="margin-top: 4rem;">🔄 CAMPAÑAS EN RADAR</div>
    <div class="section-desc">
        <strong>Recuerda:</strong> Sabes que estas campañas siguen muy activas en nuestro Radar Comercial. 
        Son extremadamente beneficiosas para ti y tus clientes. ¡No dejes de ofrecerlas!
    </div>
    <div class="grid">
"""

    for camp in campañas_viejas:
        html += f"""
        <div class="card vieja">
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
            
            <div class="apertura-box" style="background:#F9FAFB; border-color:rgba(0,0,0,0.1);">
                <div class="apertura-title" style="color:var(--text2)">🗣️ Pregunta de Apertura Consultiva</div>
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
               glob.glob(os.path.join(carpeta_base, "*Entre Nosotros*.mht")) + \
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
    
    # 3. Escribir en Google Sheets y obtener antiguas
    campañas_viejas = []
    if datos:
        campañas_viejas = actualizar_google_sheets(datos, client)
        
    # 4. Generar Briefing HTML
    if datos:
        generar_briefing_html(datos, campañas_viejas)
        
    # 5. Subir a GitHub Pages automáticamente
    if datos:
        print("🚀 Subiendo actualizaciones a GitHub Pages...")
        try:
            ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), "radar_db.json")
            # Subir archivos clave
            subprocess.run(["git", "add", "-f", "Briefing_Lunes_ADN.html", "procesador_emails_nn.py"], cwd=carpeta_scripts, check=False)
            if os.path.exists(ruta_json):
                subprocess.run(["git", "add", "-f", "../radar_db.json"], cwd=carpeta_scripts, check=False)
            
            subprocess.run(["git", "commit", "-m", "Auto-update Briefing and Radar DB"], cwd=carpeta_scripts, check=True)
            subprocess.run(["git", "push"], cwd=carpeta_scripts, check=True)
            print("✅ ¡Sincronización con GitHub completada! Tu panel online ya está actualizado.")
        except Exception as e:
            print(f"❌ Error al subir a GitHub: {e}")

if __name__ == "__main__":
    main()
