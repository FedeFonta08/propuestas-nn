import json
import datetime
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import urllib.parse

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
        full_name = row[0].lower()
        if name in full_name or full_name in name:
            return {
                "nombre": row[0],
                "apellidos": "", # Already in nombre in this CRM format
                "tel": row[1] if len(row) > 1 else "",
                "buyer": row[48] if len(row) > 48 else "Cliente"
            }
    return None

def generate_html(today_list, week_list):
    html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo de Felicitaciones — Fede Fontanals NN</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
  --nn: #FF6600; --nn-d: #CC5200; --nn-l: #FFF4ED;
  --navy: #0D1B2A; --green: #25D366; --bg: #F1F5F9;
  --tx: #1E293B; --muted: #64748B; --brd: #E2E8F0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--tx); padding-bottom: 5rem; }

.header { background: var(--navy); padding: 3rem 1.5rem; color: #fff; text-align: center; position: relative; overflow: hidden; }
.fede-avatar { width: 100px; height: 100px; border-radius: 50%; border: 4px solid var(--nn); margin-bottom: 15px; object-fit: cover; }
.header h1 { font-family: 'Syne', sans-serif; font-size: 32px; margin-bottom: 5px; }
.header h1 em { color: var(--nn); font-style: normal; }

.summary-bar { background: #fff; border-bottom: 1px solid var(--brd); padding: 1.25rem 1.5rem; display: flex; justify-content: center; gap: 3rem; }
.sum-item { display: flex; flex-direction: column; align-items: center; }
.sum-n { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; }

.section-title { font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; color: var(--muted); margin: 3rem 1.5rem 1.5rem; display: flex; align-items: center; gap: 15px; }
.section-title::after { content: ''; flex: 1; height: 1px; background: var(--brd); }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 2rem; padding: 0 1.5rem; }

.card { background: #fff; border-radius: 24px; border: 1px solid var(--brd); overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04); display: flex; flex-direction: column; }

.image-selector { padding: 10px; background: #f8fafc; border-bottom: 1px solid var(--brd); display: flex; gap: 8px; justify-content: center; }
.thumb-opt { width: 40px; height: 40px; border-radius: 8px; cursor: pointer; border: 2px solid transparent; transition: all 0.2s; object-fit: cover; }
.thumb-opt:hover { border-color: var(--nn); }
.thumb-opt.active { border-color: var(--nn); transform: scale(1.1); }

.card-img-wrap { position: relative; width: 100%; height: 240px; background: #eee; overflow: hidden; }
.card-img { width: 100%; height: 100%; object-fit: cover; transition: opacity 0.3s; }

.card-header { padding: 1.5rem; display: flex; align-items: center; gap: 15px; }
.avatar-small { width: 44px; height: 44px; border-radius: 12px; background: var(--nn); color: #fff; display: flex; align-items: center; justify-content: center; font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800; }
.info { flex: 1; }
.name { font-size: 16px; font-weight: 700; color: var(--navy); }
.buyer { font-size: 11px; color: var(--nn); font-weight: 700; text-transform: uppercase; }

.card-body { padding: 0 1.5rem 1.5rem; flex: 1; display: flex; flex-direction: column; }
.msg-box { background: var(--nn-l); border-radius: 16px; padding: 1.25rem; font-size: 14px; line-height: 1.7; border: 1px solid rgba(255,102,0,0.2); margin-bottom: 1.5rem; }

.actions { display: flex; flex-direction: column; gap: 10px; margin-top: auto; }
.btn { width: 100%; padding: 14px; border-radius: 14px; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 700; text-align: center; cursor: pointer; text-decoration: none; border: none; }
.btn-wa { background: var(--green); color: #fff; }
.btn-copy { background: #fff; color: var(--tx); border: 2px solid var(--brd); }

.tip { font-size: 11px; color: var(--muted); text-align: center; margin-top: 10px; font-weight: 600; }
</style>
</head>
<body>

<div class="header">
    <img src="assets/fede_avatar.jpg" class="fede-avatar">
    <h1>Felicitaciones <em>Premium.</em></h1>
</div>

<div class="summary-bar">
  <div class="sum-item"><span class="sum-n" style="color:var(--nn)">{{today_count}}</span><span class="sum-l">Hoy</span></div>
  <div class="sum-item"><span class="sum-n">{{week_count}}</span><span class="sum-l">Próximos 7 días</span></div>
</div>

<div class="section-title">Envíos de Hoy — Selección de Tarjeta</div>
<div class="grid">
  {{today_cards}}
</div>

<div class="section-title">Próximos de la Semana</div>
<div class="grid">
  {{week_cards}}
</div>

<script>
function selectCard(cardId, imgSrc, thumbEl) {
    const mainImg = document.getElementById('main-img-' + cardId);
    mainImg.style.opacity = '0';
    setTimeout(() => {
        mainImg.src = imgSrc;
        mainImg.style.opacity = '1';
    }, 150);
    
    const thumbs = thumbEl.parentElement.querySelectorAll('.thumb-opt');
    thumbs.forEach(t => t.classList.remove('active'));
    thumbEl.classList.add('active');
}

function safeSend(id, msg, url) {
  navigator.clipboard.writeText(msg).then(() => {
    const btn = document.getElementById('btn-send-' + id);
    const originalText = btn.innerHTML;
    btn.innerHTML = '✓ Texto Copiado - Abriendo Chat...';
    btn.style.background = 'var(--nn)';
    
    setTimeout(() => {
      window.open(url, '_blank');
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = 'var(--green)';
      }, 2000);
    }, 800);
  });
}
</script>
</body>
</html>
    """

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
        
        tel_clean = p['tel'].replace(' ', '').replace('+', '')
        if tel_clean.startswith('00'): tel_clean = tel_clean[2:]
        if len(tel_clean) == 9 and tel_clean.startswith(('6', '7', '8', '9')):
            tel_clean = '34' + tel_clean
            
        # Most compatible official format
        wa_url = f"https://api.whatsapp.com/send?phone={tel_clean}"
        card_id = p['tel'] if p['tel'] else p['nombre'].replace(" ","")
        msg_js = msg.replace("'", "\\'").replace('"', '\\"')
        
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
      <button onclick="safeSend('{card_id}', '{msg_js}', '{wa_url}')" class="btn btn-wa" id="btn-send-{card_id}">1. Abrir Chat (Modo Seguro)</button>
    </div>
    <p class="tip">🛡️ Se copiará el texto: luego pulsa Ctrl+V en el chat.</p>
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
