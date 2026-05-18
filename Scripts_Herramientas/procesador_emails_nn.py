import os
import glob
import re
import sys
import json
import datetime
import subprocess
import email
import difflib
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

# Cargar Catálogo Maestro de Productos NN para el Escudo de Verificación
catalogo_maestro = {}
ruta_catalogo = os.path.join(carpeta_scripts, 'catalogo_maestro_productos.json')
if os.path.exists(ruta_catalogo):
    try:
        with open(ruta_catalogo, 'r', encoding='utf-8') as f:
            catalogo_maestro = json.load(f)
        print(f"📖 Catálogo Maestro cargado con éxito ({len(catalogo_maestro)} productos).")
    except Exception as ce:
        print(f"⚠️ Error al cargar el catálogo maestro: {ce}")
else:
    print("⚠️ ADVERTENCIA: No se encontró 'catalogo_maestro_productos.json' en la carpeta de scripts.")

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
    global catalogo_maestro
    print("🧠 Analizando el correo con el Super Prompt ADN (leyendo tu Manual Maestro y Catálogo)...")
    
    # Leer las reglas del ADN
    ruta_reglas = os.path.join(carpeta_scripts, 'reglas_adn.txt')
    reglas_adn = ""
    if os.path.exists(ruta_reglas):
        with open(ruta_reglas, 'r', encoding='utf-8') as f:
            reglas_adn = f.read()
            
    # Serializar catálogo para el prompt
    catalogo_json = json.dumps(catalogo_maestro, ensure_ascii=False, indent=2)
            
    prompt = f"""
    Eres el Asistente Analítico de Élite de un Agente Dinamizador de Nationale-Nederlanden (Federico Fontanals). 
    Tu tarea es procesar el correo semanal corporativo 'Entre Nosotros' y estructurar la información para actualizar el Radar Comercial del agente.
    Aplica SIEMPRE la filosofía de venta consultiva (Análisis de Necesidades - ADN) basándote ESTRICTAMENTE en este manual:
    
    === MANUAL MAESTRO DEL ADN ===
    {reglas_adn}
    ==============================

    === CATÁLOGO MAESTRO DE PRODUCTOS VIGENTES (SITUACIÓN ACTUAL) ===
    {catalogo_json}
    ==================================================================

    REGLAS DE ORO OBLIGATORIAS (CRÍTICO):
    1. Trata 'Contigo Familia' y 'Contigo Autónomo' SIEMPRE como dos productos y campañas completamente distintos. Tienen coberturas y segmentos objetivo diferentes.
       - Si la campaña 'Contigo Familia' amplía su alcance a autónomos (descuento vitalicio 25%, excluyendo la cobertura ILT), debes generar DOS objetos distintos en 'Campañas_Activas':
         * Un objeto con "Producto": "Contigo Familia", dirigido al segmento familiar/particular general.
         * Otro objeto con "Producto": "Contigo Autónomo", dirigido específicamente al segmento de Autónomos, detallando que tiene el 25% de descuento vitalicio y excluyendo explícitamente la cobertura de Incapacidad Laboral Temporal (ILT).
       ¡NUNCA los fusiones, no dejes uno solo y no los agrupes en la misma fila!
    2. Cruza los productos del email con el Catálogo Maestro de arriba. Para la clave 'Producto', utiliza SIEMPRE el 'nombre_oficial' exacto que corresponda en el Catálogo Maestro (ej. 'Plan SIALP', 'Contigo Autónomo', 'Contigo Senior (+55)', 'Plan Salud + Vida', etc.).
    3. Redacta la 'Vulnerabilidad_Detectada' y la 'Pregunta_Apertura' basándote en la realidad técnica del producto oficial (usa los campos 'coberturas_clave' y 'faqs_objeciones' del catálogo para redactar argumentos extremadamente verídicos y potentes en lugar de inventar generalidades).
    4. Para cualquier novedad en 'Novedades_Producto', el campo 'Fuente' DEBE incluir el número de edición exacto del correo analizado (por ejemplo: 'Entre Nosotros #561' o 'Urgente 18/05/2026'). NUNCA uses texto genérico como 'Entre Nosotros'.
    5. **AUTO-ACTUALIZACIÓN DEL PORTAL (CRÍTICO)**: Si detectas que el correo corporativo anuncia un cambio permanente o muy significativo en las características, precios, descuentos o coberturas de un producto del catálogo (por ejemplo: una bonificación especial de 6 meses para Contigo Senior, un descuento del 12.5% para Salud + Vida, o la exclusión de ILT para Autónomos):
       - Debes rellenar la clave `"Cambios_Catalogo"` dentro de la campaña o novedad correspondiente.
       - Si no hay cambios en la estructura base del producto, la clave `"Cambios_Catalogo"` debe ser `null` u omitirse.

    Devuelve ESTRICTAMENTE un objeto JSON válido con las siguientes tres claves principales. No devuelvas ningún texto fuera del JSON.

    {{
      "Campañas_Activas": [
        {{
          "Producto": "Nombre oficial del producto (debe coincidir con nombre_oficial en el Catálogo)",
          "Tipo_de_campaña": "Ej. Descuento, Ampliación...",
          "Descripcion_del_beneficio": "Qué ofrece",
          "Fecha_inicio": "DD/MM/YYYY",
          "Fecha_fin": "DD/MM/YYYY",
          "Cupo_max": "Límite",
          "Descuento_Bonus": "Cifra",
          "Segmento_objetivo": "A quién va dirigido",
          "Vulnerabilidad_Detectada": "La debilidad o preocupación principal del cliente que este producto soluciona",
          "Pregunta_Apertura": "Pregunta consultiva para iniciar la conversación sin vender",
          "Estado": "🟢 ACTIVA o ⚡ URGENTE",
          "Cambios_Catalogo": {{
            "id_producto": "id_del_producto_en_catalogo (ej. senior, saludvida, sialp, autonomo)",
            "campos_a_actualizar": {{
              "descripcion_breve": "Nueva descripción corta del producto reflejando el cambio actual si aplica",
              "precio_base": "Nueva prima o precio si cambia permanentemente",
              "detalles_adicionales": "Nuevos detalles/costes",
              "estadisticas_clave": [
                {{
                  "valor": "Valor (ej. 6 meses)",
                  "etiqueta": "Etiqueta (ej. Bonificación en mayo 2026)"
                }}
              ],
              "coberturas_clave": [
                {{
                  "cobertura": "Nombre de la cobertura",
                  "concepto": "Explicación/Concepto",
                  "valor_limite": "Límite",
                  "es_clave": true,
                  "tipo": "Tipo de cobertura"
                }}
              ]
            }}
          }}
        }}
      ],
      "Novedades_Producto": [
        {{
          "Producto": "Nombre oficial del producto",
          "Que_ha_cambiado": "Descripción del cambio",
          "Tipo": "🟢 Mejora, 🔵 Operativo, o 🔴 Proceso Crítico",
          "Vigente_desde": "DD/MM/YYYY",
          "Afecta_guia_comercial": "SÍ / NO",
          "Accion_sobre_CRM": "Qué hacer en el CRM",
          "Impacto_segmento": "A qué segmento afecta",
          "Fuente": "Ej. Entre Nosotros #561",
          "Cambios_Catalogo": null
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
                
                # IMPORTANT: Si una campaña se actualiza, la metemos también en Novedades 
                # para que el agente vea el cambio reflejado explícitamente.
                edicion_num = datos.get("Historial", {}).get("N_Edicion", "561")
                fuente_campana = f"Entre Nosotros #{edicion_num}" if edicion_num else "Entre Nosotros"
                
                if "Novedades_Producto" not in datos:
                    datos["Novedades_Producto"] = []
                datos["Novedades_Producto"].append({
                    "Producto": f"Campaña Actualizada: {prod_nombre}",
                    "Que_ha_cambiado": camp.get("Descripcion_del_beneficio", ""),
                    "Tipo": "🟢 Campaña Modificada",
                    "Vigente_desde": camp.get("Fecha_inicio", fecha_hoy),
                    "Afecta_guia_comercial": "SÍ",
                    "Accion_sobre_CRM": f"Ofrecer al segmento: {camp.get('Segmento_objetivo', '')}",
                    "Impacto_segmento": camp.get("Segmento_objetivo", ""),
                    "Fuente": fuente_campana
                })
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
                
        edicion_num = datos.get("Historial", {}).get("N_Edicion", "561")
        fuente_actual = f"Entre Nosotros #{edicion_num}" if edicion_num else "Entre Nosotros"
        
        # Cargar novedades existentes
        novedades_existentes = ws_nov.get_all_values()
        
        # Filtrar duplicados de la misma edición que vamos a meter hoy
        rows_nov_keep = []
        for r in novedades_existentes:
            if not r: continue
            fuente_fila = r[7].strip() if len(r) > 7 else ""
            # Si contiene el número de edición actual, la eliminamos para sobreescribirla limpiamente
            if edicion_num and f"#{edicion_num}" in fuente_fila:
                continue
            rows_nov_keep.append(r)
            
        # Si eliminamos algo, limpiamos la hoja y re-escribimos lo que mantuvimos
        if len(rows_nov_keep) < len(novedades_existentes):
            print(f"🧹 Eliminando novedades previas de la edición #{edicion_num} para evitar duplicados...")
            ws_nov.clear()
            try:
                ws_nov.update(rows_nov_keep)
            except Exception:
                ws_nov.update(rows_nov_keep, 'A1')
            novs_existentes_set = set((row[0].strip().lower(), row[1].strip().lower()) for row in rows_nov_keep if len(row) >= 2)
        else:
            novs_existentes_set = set((row[0].strip().lower(), row[1].strip().lower()) for row in novedades_existentes if len(row) >= 2)

        for nov in datos.get("Novedades_Producto", []):
            prod_nov = nov.get("Producto", "").strip()
            cambio_nov = nov.get("Que_ha_cambiado", "").strip()
            tipo_nov = nov.get("Tipo", "").strip()
            vigente_nov = nov.get("Vigente_desde", "").strip()
            afecta_nov = nov.get("Afecta_guia_comercial", "").strip()
            accion_nov = nov.get("Accion_sobre_CRM", "").strip()
            segmento_nov = nov.get("Impacto_segmento", "").strip()
            
            # Garantizar que Fuente tenga el número de edición exacto
            fuente_nov = nov.get("Fuente", "").strip()
            if "entre nosotros" in fuente_nov.lower() and "#" not in fuente_nov:
                if edicion_num:
                    fuente_nov = f"Entre Nosotros #{edicion_num}"
            if not fuente_nov:
                fuente_nov = fuente_actual

            # Validación de Duplicidad
            if (prod_nov.lower(), cambio_nov.lower()) in novs_existentes_set:
                print(f"⚠️ Novedad ya existe (Duplicado saltado): {prod_nov}")
                continue

            ws_nov.append_row([
                prod_nov, cambio_nov, tipo_nov,
                vigente_nov, afecta_nov, accion_nov,
                segmento_nov, fuente_nov
            ])
            novs_existentes_set.add((prod_nov.lower(), cambio_nov.lower()))
            print(f"✅ Novedad insertada en la nube: {prod_nov}")

        # 3. Historial (DASHBOARD AGENCIA)
        ws_hist = ws_camp
        for s in sheet.worksheets():
            if "DASHBOARD" in s.title.upper() or "HISTORIAL" in s.title.upper():
                ws_hist = s
                break
                
        # Cargar historial existente
        historial_existente = ws_hist.get_all_values()
        rows_hist_keep = []
        for r in historial_existente:
            if not r: continue
            edicion_fila = r[0].strip()
            # Si coincide con la edición actual, la eliminamos para sobreescribir limpiamente
            if edicion_fila == edicion_num:
                continue
            rows_hist_keep.append(r)
            
        if len(rows_hist_keep) < len(historial_existente):
            print(f"🧹 Eliminando registro de historial previo para la edición #{edicion_num}...")
            ws_hist.clear()
            try:
                ws_hist.update(rows_hist_keep)
            except Exception:
                ws_hist.update(rows_hist_keep, 'A1')

        hist = datos.get("Historial", {})
        if hist:
            ws_hist.append_row([
                hist.get("N_Edicion", ""), fecha_hoy, str(hist.get("Resumen_ejecutivo", "")),
                str(hist.get("Campañas_nuevas", "")), str(hist.get("Cambios_producto", "")),
                str(hist.get("N_acciones", "")), f"{fecha_hoy} · Gemini AI Automático"
            ])
            print(f"✅ Historial insertado en la nube.")

        # 4. Formatear visualmente el Google Sheet para que se vea premium
        print("🎨 Aplicando formato visual automático a las tablas (Wrap y Middle)...")
        try:
            # Formatear la pestaña de Campañas Activas (A2:J150)
            ws_camp.format("A2:J150", {
                "wrapStrategy": "WRAP",
                "verticalAlignment": "MIDDLE",
                "horizontalAlignment": "LEFT"
            })
            # Formatear la pestaña de Novedades Producto (A2:H150)
            ws_nov.format("A2:H150", {
                "wrapStrategy": "WRAP",
                "verticalAlignment": "MIDDLE",
                "horizontalAlignment": "LEFT"
            })
            print("✅ Formato aplicado con éxito (Wrap y alineación vertical completados).")
        except Exception as fe:
            print(f"⚠️ No se pudo formatear el Google Sheet: {fe}")

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

def verificar_y_mapear_productos(datos):
    global catalogo_maestro
    if not catalogo_maestro:
        print("⚠️ No hay catálogo maestro cargado. Saltando escudo de verificación.")
        return datos

    nombres_oficiales = [prod["nombre_oficial"] for prod in catalogo_maestro.values()]
    mapa_nombres = {prod["nombre_oficial"].strip().lower(): prod_key for prod_key, prod in catalogo_maestro.items()}
    
    # Procesar Campañas Activas
    for camp in datos.get("Campañas_Activas", []):
        prod_nombre = camp.get("Producto", "").strip()
        prod_nombre_lower = prod_nombre.lower()
        
        # 1. Intento de mapeo exacto o mapeo de subcadena
        mapeado = False
        
        # Exacto
        if prod_nombre_lower in mapa_nombres:
            clave_prod = mapa_nombres[prod_nombre_lower]
            camp["Producto"] = catalogo_maestro[clave_prod]["nombre_oficial"]
            if "Cambios_Catalogo" in camp and camp["Cambios_Catalogo"]:
                camp["Cambios_Catalogo"]["id_producto"] = clave_prod
            mapeado = True
            
        if not mapeado:
            # Búsqueda difusa difflib
            matches = difflib.get_close_matches(prod_nombre, nombres_oficiales, n=1, cutoff=0.7)
            if matches:
                clave_prod = mapa_nombres[matches[0].strip().lower()]
                print(f"⚡ Mapeo automático de precisión: '{prod_nombre}' -> '{matches[0]}'")
                camp["Producto"] = matches[0]
                if "Cambios_Catalogo" in camp and camp["Cambios_Catalogo"]:
                    camp["Cambios_Catalogo"]["id_producto"] = clave_prod
                mapeado = True
                
        if not mapeado:
            # Activar el Escudo Interactivo de Seguridad
            print(f"\n⚠️ ESCUDO DE SEGURIDAD NN: Producto no identificado en catálogo: '{prod_nombre}'")
            print("Este producto no coincide con ninguno de los 25 productos oficiales de tu portal propuestas.")
            print("\nPor favor, selecciona cómo deseas proceder:")
            print(f"  [1] Mapear manualmente a un producto oficial de tu catálogo.")
            print(f"  [2] Proceder e inyectar '{prod_nombre}' como un producto nuevo.")
            print(f"  [3] Abortar la ejecución para revisar el correo manualmente.")
            
            try:
                opcion = input("Introduce una opción [1/2/3] (Enter para abortar): ").strip()
            except KeyboardInterrupt:
                print("\n❌ Ejecución interrumpida. Saliendo de forma segura...")
                sys.exit(0)
                
            if opcion == '1':
                print("\nProductos oficiales de tu cartera:")
                lista_claves = list(catalogo_maestro.keys())
                for idx, clave in enumerate(lista_claves):
                    print(f"  [{idx + 1}] {catalogo_maestro[clave]['nombre_oficial']} ({clave})")
                
                try:
                    sel = input(f"\nSelecciona el número (1-{len(lista_claves)}): ").strip()
                except KeyboardInterrupt:
                    sys.exit(0)
                    
                if sel.isdigit() and 1 <= int(sel) <= len(lista_claves):
                    clave_elegida = lista_claves[int(sel) - 1]
                    prod_nombre_oficial = catalogo_maestro[clave_elegida]["nombre_oficial"]
                    print(f"✅ Mapeado con éxito a: {prod_nombre_oficial}")
                    camp["Producto"] = prod_nombre_oficial
                    if "Cambios_Catalogo" in camp and camp["Cambios_Catalogo"]:
                        camp["Cambios_Catalogo"]["id_producto"] = clave_elegida
                else:
                    print("❌ Selección inválida. Abortando por seguridad...")
                    sys.exit(1)
            elif opcion == '2':
                print(f"⚠️ Procediendo con '{prod_nombre}' como nuevo producto...")
            else:
                print("❌ Operación abortada por seguridad. Tu Excel no ha sido modificado.")
                sys.exit(0)
                
    # Procesar Novedades Producto de la misma forma
    for nov in datos.get("Novedades_Producto", []):
        prod_nombre = nov.get("Producto", "").strip()
        
        # Quitar prefijos comunes si los tiene (ej. "Campaña Actualizada: ")
        if prod_nombre.startswith("Campaña Actualizada: "):
            actual_prod = prod_nombre.replace("Campaña Actualizada: ", "").strip()
            es_camp_actualizada = True
        else:
            actual_prod = prod_nombre
            es_camp_actualizada = False
            
        actual_prod_lower = actual_prod.lower()
        mapeado = False
        
        if actual_prod_lower in mapa_nombres:
            clave_prod = mapa_nombres[actual_prod_lower]
            nombre_final = catalogo_maestro[clave_prod]["nombre_oficial"]
            nov["Producto"] = f"Campaña Actualizada: {nombre_final}" if es_camp_actualizada else nombre_final
            mapeado = True
            
        if not mapeado:
            matches = difflib.get_close_matches(actual_prod, nombres_oficiales, n=1, cutoff=0.7)
            if matches:
                clave_prod = mapa_nombres[matches[0].strip().lower()]
                nombre_final = matches[0]
                nov["Producto"] = f"Campaña Actualizada: {nombre_final}" if es_camp_actualizada else nombre_final
                mapeado = True
                
    return datos

def actualizar_propuestas_html(producto_id, campos_actualizados):
    rutas_html = [
        r"D:\Users\ffont\Downloads\propuestas-nn-v2.html",
        r"D:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\propuestas-nn-v2.html",
        r"D:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\Scripts_Herramientas\propuestas-nn-v2.html"
    ]
    
    PRODUCTOS_REALES = [
        'sialp', 'flexible', 'garantizado', 'flexicuenta', 'ahorrogarantizado', 
        'futuro', 'proteccionplus', 'saludvida', 'saludcompleto', 'saludcopago', 
        'vidafamilia', 'senior', 'accidentes', 'hogar', 'auto', 'moto', 
        'ppsa', 'duplo', 'autonomo', 'ilt', 'pyme', 'comercios', 
        'saludautonomos', 'hipotecaabanca', 'hipotecaing'
    ]
    
    for ruta in rutas_html:
        if not os.path.exists(ruta):
            continue
            
        print(f"✏️ Sincronizando portal de propuestas en: {os.path.basename(ruta)}")
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                html = f.read()
                
            # Encontrar el bloque const PRODS = { ... }
            match_prods = re.search(r'const\s+PRODS\s*=\s*\{(.*?)const\s+PORTADA_FASES', html, re.DOTALL)
            if not match_prods:
                print(f"❌ No se encontró const PRODS en {ruta}")
                continue
                
            prods_content = match_prods.group(1)
            
            # Encontrar la posición de inicio del producto y su final aproximado
            prod_start_match = re.search(r'^\s*' + producto_id + r'\s*:\s*\{', prods_content, re.MULTILINE)
            if not prod_start_match:
                print(f"❌ No se encontró el producto '{producto_id}' en {ruta}")
                continue
                
            start_idx = prod_start_match.start()
            
            # Para encontrar el final, buscamos la siguiente clave de producto real
            siguientes_pos = []
            for p in PRODUCTOS_REALES:
                if p == producto_id:
                    continue
                p_match = re.search(r'^\s*' + p + r'\s*:\s*\{', prods_content[start_idx:], re.MULTILINE)
                if p_match:
                    siguientes_pos.append(start_idx + p_match.start())
                    
            if siguientes_pos:
                end_idx = min(siguientes_pos)
            else:
                end_idx = len(prods_content)
                
            block = prods_content[start_idx:end_idx]
            
            # Realizar reemplazos quirúrgicos en 'block'
            # 1. sub
            if "descripcion_breve" in campos_actualizados:
                val = campos_actualizados["descripcion_breve"].replace("'", "\\'")
                block = re.sub(r"(sub\s*:\s*['\"`]).*?(['\"`]\s*,)", rf"\g<1>{val}\g<2>", block, flags=re.DOTALL)
                
            # 2. prima
            if "precio_base" in campos_actualizados:
                val = campos_actualizados["precio_base"].replace("'", "\\'")
                block = re.sub(r"(prima\s*:\s*['\"`]).*?(['\"`]\s*,?)", rf"\g<1>{val}\g<2>", block, flags=re.DOTALL)
                
            # 3. totalDesc
            if "detalles_adicionales" in campos_actualizados:
                val = campos_actualizados["detalles_adicionales"].replace("'", "\\'")
                block = re.sub(r"(totalDesc\s*:\s*['\"`]).*?(['\"`]\s*,?)", rf"\g<1>{val}\g<2>", block, flags=re.DOTALL)
                
            # 4. estadisticas_clave (sts)
            if "estadisticas_clave" in campos_actualizados and campos_actualizados["estadisticas_clave"]:
                sts_items = []
                for st in campos_actualizados["estadisticas_clave"]:
                    v_val = st["valor"].replace("'", "\\'")
                    l_val = st["etiqueta"].replace("'", "\\'")
                    sts_items.append(f"{{ v: '{v_val}', l: '{l_val}' }}")
                sts_js = f"sts: [{', '.join(sts_items)}],"
                block = re.sub(r"sts\s*:\s*\[.*?\n?\s*\]\s*,", sts_js, block, flags=re.DOTALL)
                
            # 5. coberturas_clave (covs)
            if "coberturas_clave" in campos_actualizados and campos_actualizados["coberturas_clave"]:
                cov_items = []
                for c in campos_actualizados["coberturas_clave"]:
                    cobertura_val = c["cobertura"].replace("'", "\\'")
                    concepto_val = c["concepto"].replace("'", "\\'")
                    limite_val = c["valor_limite"].replace("'", "\\'")
                    k_val = "true" if c.get("es_clave") else "false"
                    t_val = f", t: '{c['tipo']}'" if c.get("tipo") else ""
                    cov_items.append(f"{{ n: '{cobertura_val}', c: '{concepto_val}', p: '{limite_val}', k: {k_val}{t_val} }}")
                covs_js = "covs: [\n      " + ",\n      ".join(cov_items) + "\n    ],"
                block = re.sub(r"covs\s*:\s*\[.*?\n?\s*\]\s*,", covs_js, block, flags=re.DOTALL)
                
            # Re-ensamblar el contenido de PRODS
            nuevo_prods_content = prods_content[:start_idx] + block + prods_content[end_idx:]
            
            # Re-ensamblar el HTML completo
            nuevo_html = html.replace(prods_content, nuevo_prods_content)
            
            with open(ruta, 'w', encoding='utf-8') as f_out:
                f_out.write(nuevo_html)
            print(f"✅ Portal de propuestas actualizado con éxito en: {os.path.basename(ruta)}")
        except Exception as html_err:
            print(f"⚠️ Error al sincronizar el portal propuestas en {ruta}: {html_err}")

def procesar_actualizaciones_catalogo(datos):
    global catalogo_maestro
    actualizado = False
    
    # Revisar campañas activas
    for camp in datos.get("Campañas_Activas", []):
        cambios = camp.get("Cambios_Catalogo")
        if cambios and isinstance(cambios, dict):
            prod_id = cambios.get("id_producto")
            campos = cambios.get("campos_a_actualizar")
            if prod_id and prod_id in catalogo_maestro and isinstance(campos, dict):
                print(f"📢 Se ha detectado un cambio de características para '{prod_id}' en la campaña.")
                # Actualizar catálogo en memoria
                for k, v in campos.items():
                    if v:
                        catalogo_maestro[prod_id][k] = v
                actualizado = True
                # Actualizar HTML en caliente
                actualizar_propuestas_html(prod_id, campos)
                
    # Revisar novedades de producto
    for nov in datos.get("Novedades_Producto", []):
        cambios = nov.get("Cambios_Catalogo")
        if cambios and isinstance(cambios, dict):
            prod_id = cambios.get("id_producto")
            campos = cambios.get("campos_a_actualizar")
            if prod_id and prod_id in catalogo_maestro and isinstance(campos, dict):
                print(f"📢 Se ha detectado un cambio de características para '{prod_id}' en la novedad.")
                # Actualizar catálogo en memoria
                for k, v in campos.items():
                    if v:
                        catalogo_maestro[prod_id][k] = v
                actualizado = True
                # Actualizar HTML en caliente
                actualizar_propuestas_html(prod_id, campos)
                
    if actualizado:
        # Guardar catálogo maestro actualizado
        ruta_catalogo = os.path.join(carpeta_scripts, 'catalogo_maestro_productos.json')
        try:
            with open(ruta_catalogo, 'w', encoding='utf-8') as f:
                json.dump(catalogo_maestro, f, ensure_ascii=False, indent=2)
            print("💾 Base de datos del Catálogo Maestro actualizada y guardada.")
        except Exception as e:
            print(f"❌ Error al guardar el catálogo maestro actualizado: {e}")

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
    
    if datos:
        # A. Escudo de Verificación de Productos (Validación y Mapeo)
        datos = verificar_y_mapear_productos(datos)
        
        # B. Procesar Auto-Actualización de Catálogo y Portal HTML en Caliente
        procesar_actualizaciones_catalogo(datos)
    
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
