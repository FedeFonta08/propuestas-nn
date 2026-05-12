import json
import datetime
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# CONFIG
TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token_drive.json'
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
OUTPUT_HTML = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/Felicitaciones_Cumple_NN.html'

CALENDAR_BIRTHDAYS = [
    {"name": "Amparo Gimenez Torres", "date": "2026-05-12", "type": "CLIENTE"},
    {"name": "Fernando Aranda Arguello", "date": "2026-05-12", "type": "CLIENTE"},
    {"name": "Javier López Esteve", "date": "2026-05-12", "type": "CLIENTE"},
    {"name": "Maria Josefa Cano Crespo", "date": "2026-05-12", "type": "CLIENTE"},
    {"name": "Andrea Tormo", "date": "2026-05-14", "type": "HIJO", "parent": "Jose Arturo Tormo Sanchis"},
    {"name": "Angel Urio Reig Calabuig", "date": "2026-05-14", "type": "CLIENTE"},
    {"name": "Jose Luis Olmeda Villar", "date": "2026-05-14", "type": "CLIENTE"},
    {"name": "Maria Dolores Martí Cardos", "date": "2026-05-14", "type": "CLIENTE"},
    {"name": "Pablo Garcia", "date": "2026-05-14", "type": "HIJO", "parent": "Amparo Pérez Sanegre"},
    {"name": "Ángel Carmona García", "date": "2026-05-14", "type": "CLIENTE"},
    {"name": "Maria Dolores Gaya Tormo", "date": "2026-05-15", "type": "CLIENTE"},
    {"name": "Concepcion Montserrat Pont Chafer", "date": "2026-05-16", "type": "CLIENTE"},
    {"name": "Maria José Rubio Tudela", "date": "2026-05-16", "type": "CLIENTE"},
    {"name": "Rebeca Gorrita Samuel", "date": "2026-05-16", "type": "CLIENTE"},
    {"name": "Ángeles Moreno Peiro", "date": "2026-05-16", "type": "CLIENTE"},
    {"name": "Carla González", "date": "2026-05-17", "type": "HIJO", "parent": "Mari Carmen Gracia Díaz"},
    {"name": "Carmen Sanchez Molina", "date": "2026-05-17", "type": "CLIENTE"},
    {"name": "Maria García Francés", "date": "2026-05-17", "type": "CLIENTE"},
    {"name": "Alexis Molto Mestre", "date": "2026-05-18", "type": "CLIENTE"},
    {"name": "Antonio García Díaz", "date": "2026-05-18", "type": "CLIENTE"},
    {"name": "Dolores Bustamante Pardo", "date": "2026-05-18", "type": "CLIENTE"},
    {"name": "Elena Solomon", "date": "2026-05-18", "type": "CLIENTE"},
    {"name": "Yolanda", "date": "2026-05-18", "type": "CLIENTE"},
    {"name": "José Joaquín Oltra Moscardó", "date": "2026-05-19", "type": "CLIENTE"},
    {"name": "Ricardo Ortega Fernández", "date": "2026-05-19", "type": "CLIENTE"},
]

def get_crm_data():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A3:AY2500").execute()
    return result.get('values', [])

def fuzzy_match(name, rows):
    name = name.lower()
    for row in rows:
        if not row: continue
        full_name = (row[0] + " " + (row[1] if len(row) > 1 else "")).lower()
        if name in full_name or full_name in name:
            return {
                "nombre": row[0],
                "apellidos": row[1] if len(row) > 1 else "",
                "tel": row[3] if len(row) > 3 else "",
                "buyer": row[48] if len(row) > 48 else "Cliente"
            }
    return None

def generate_html(today_list, week_list):
    # (Reuse logic from birthday_automation.py but with better layout if needed)
    # I'll use the same template for consistency but update it with the new data.
    
    with open('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/birthday_automation.py', 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # Extract template from original code
    start_tag = 'html_template = """'
    end_tag = '"""'
    start_idx = original_code.find(start_tag) + len(start_tag)
    end_idx = original_code.find(end_tag, start_idx)
    html_template = original_code[start_idx:end_idx]

    def create_card(p, is_today=True):
        initials = (p['nombre'][0] + (p['apellidos'][0] if p['apellidos'] else "")).upper()
        
        default_img = "assets/fede_card.png"
        buyer_str = p['buyer'].upper()
        if "HIJO" in buyer_str or p.get('type') == 'HIJO': 
            default_img = "assets/hijo.png"
            buyer_label = f"HIJO DE {p.get('parent', '').upper()}" if p.get('parent') else "HIJO / FAMILIA"
        elif "SENIOR" in buyer_str: 
            default_img = "assets/senior.png"
            buyer_label = buyer_str
        else:
            buyer_label = buyer_str
        
        if p.get('manual'):
            msg = p['msg']
        elif p.get('type') == 'HIJO':
            msg = f"¡Hola {p.get('parent_name', 'familia')}! Soy Fede de Nationale-Nederlanden. Me he acordado de que hoy es el cumple de {p['nombre']}. ¡Muchísimas felicidades para el peque y para vosotros! Que paséis un gran día."
        else:
            msg = f"¡Hola {p['nombre']}! Soy Fede de Nationale-Nederlanden. Te deseo un muy feliz cumpleaños y que pases un día genial con los tuyos. ¡Un fuerte abrazo!"
        
        wa_url = f"https://wa.me/{p['tel'].replace(' ', '').replace('+', '')}?text={msg}"
        card_id = p['tel'] if p['tel'] else p['nombre'].replace(" ","")
        
        return f"""
<div class="card">
  <div class="image-selector">
    <img src="assets/fede_card.png" class="thumb-opt {"active" if default_img=="assets/fede_card.png" else ""}" onclick="selectCard('{card_id}', 'assets/fede_card.png', this)" title="Fede Personalizada">
    <img src="assets/senior.png" class="thumb-opt {"active" if default_img=="assets/senior.png" else ""}" onclick="selectCard('{card_id}', 'assets/senior.png', this)" title="Senior">
    <img src="assets/adulto.png" class="thumb-opt {"active" if default_img=="assets/adulto.png" else ""}" onclick="selectCard('{card_id}', 'assets/adulto.png', this)" title="Adulto">
    <img src="assets/hijo.png" class="thumb-opt {"active" if default_img=="assets/hijo.png" else ""}" onclick="selectCard('{card_id}', 'assets/hijo.png', this)" title="Familiar / Hijo">
  </div>
  <div class="card-img-wrap">
    <img src="{default_img}" id="main-img-{card_id}" class="card-img" alt="Tarjeta">
  </div>
  <div class="card-header">
    <div class="avatar-small">{initials}</div>
    <div class="info">
      <div class="name">{p['nombre']} {p['apellidos']}</div>
      <div class="buyer">{buyer_label}</div>
    </div>
  </div>
  <div class="card-body">
    <div class="msg-box">{msg}</div>
    <div class="actions">
      <a href="{wa_url}" target="_blank" class="btn btn-wa">1. Enviar Texto WhatsApp</a>
      <button id="btn-copy-{card_id}" class="btn btn-copy" onclick="copyMsg('{card_id}', '{msg}')">2. Copiar Texto</button>
    </div>
    <p class="tip">🖼️ Selecciona arriba la imagen, Click derecho > Copiar y pega.</p>
  </div>
</div>
        """

    today_cards = "".join([create_card(p) for p in today_list]) or '<div class="empty">No hay cumpleaños registrados para hoy.</div>'
    week_cards = "".join([create_card(p, False) for p in week_list]) or '<div class="empty">No hay cumpleaños para el resto de la semana.</div>'

    final_html = html_template.replace("{{today_count}}", str(len(today_list)))
    final_html = final_html.replace("{{week_count}}", str(len(week_list)))
    final_html = final_html.replace("{{today_cards}}", today_cards)
    final_html = final_html.replace("{{week_cards}}", week_cards)

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"HTML INTERACTIVO actualizado en: {OUTPUT_HTML}")

def main():
    rows = get_crm_data()
    today = datetime.date(2026, 5, 12) # Fixed today for current session
    
    final_today = []
    final_week = []
    
    for cb in CALENDAR_BIRTHDAYS:
        dt = datetime.datetime.strptime(cb['date'], '%Y-%m-%d').date()
        
        # Search for contact in CRM
        search_name = cb['parent'] if cb.get('type') == 'HIJO' else cb['name']
        contact = fuzzy_match(search_name, rows)
        
        if contact:
            p = {
                "nombre": cb['name'],
                "apellidos": contact['apellidos'] if cb.get('type') != 'HIJO' else "",
                "tel": contact['tel'],
                "buyer": contact['buyer'],
                "type": cb['type'],
                "parent": cb.get('parent', ''),
                "parent_name": contact['nombre']
            }
        else:
            p = {
                "nombre": cb['name'],
                "apellidos": "",
                "tel": "",
                "buyer": "Desconocido",
                "type": cb['type'],
                "parent": cb.get('parent', '')
            }
            
        if dt == today:
            final_today.append(p)
        elif today < dt <= today + datetime.timedelta(days=7):
            final_week.append(p)

    generate_html(final_today, final_week)

if __name__ == "__main__":
    main()
