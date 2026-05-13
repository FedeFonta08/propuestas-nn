import json
import datetime
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import sys

# CONFIG (Rutas relativas para compatibilidad con GitHub Actions y ejecución local)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token_drive.json')
SHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
OUTPUT_HTML = os.path.join(BASE_DIR, 'Felicitaciones_Cumple_NN.html')

def get_data():
    # Intenta leer desde el archivo local, si no, usa la variable de entorno (para GitHub Actions)
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    else:
        token_data = json.loads(os.environ.get('GOOGLE_TOKEN_JSON'))
        creds = Credentials.from_authorized_user_info(token_data)
        
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'CRM MAESTRO'!A3:AY2500").execute()
    return result.get('values', [])

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

/* SELECTOR DE IMAGEN */
.image-selector { padding: 15px 10px; background: #f8fafc; border-bottom: 1px solid var(--brd); display: flex; gap: 12px; justify-content: center; }
.opt-container { display: flex; flex-direction: column; align-items: center; gap: 5px; }
.thumb-opt { width: 44px; height: 44px; border-radius: 10px; cursor: pointer; border: 2px solid transparent; transition: all 0.2s; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.thumb-opt:hover { border-color: var(--nn); transform: translateY(-2px); }
.thumb-opt.active { border-color: var(--nn); transform: scale(1.1); box-shadow: 0 4px 12px rgba(255,102,0,0.3); }
.opt-label { font-size: 9px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }

.card-img-wrap { position: relative; width: 100%; height: 260px; background: #f1f5f9; overflow: hidden; }
.card-img { width: 100%; height: 100%; object-fit: cover; transition: opacity 0.3s; }

.card-header { padding: 1.5rem; display: flex; align-items: center; gap: 15px; }
.avatar-small { width: 44px; height: 44px; border-radius: 12px; background: var(--nn); color: #fff; display: flex; align-items: center; justify-content: center; font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800; }
.info { flex: 1; }
.name { font-size: 16px; font-weight: 700; color: var(--navy); }
.buyer { font-size: 11px; color: var(--nn); font-weight: 700; text-transform: uppercase; }

.card-body { padding: 0 1.5rem 1.5rem; flex: 1; display: flex; flex-direction: column; }
.msg-box { background: var(--nn-l); border-radius: 16px; padding: 1.25rem; font-size: 14px; line-height: 1.7; border: 1px solid rgba(255,102,0,0.2); margin-bottom: 1.5rem; }

.actions { display: grid; grid-template-columns: 1fr; gap: 10px; margin-top: auto; }
.btn { width: 100%; padding: 14px; border-radius: 14px; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 700; text-align: center; cursor: pointer; text-decoration: none; border: none; }
.btn-wa { background: var(--green); color: #fff; display: block; }
.btn-copy { background: #fff; color: var(--nn); border: 2px solid var(--nn); }

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
    
    // Update active thumb
    const thumbs = thumbEl.parentElement.querySelectorAll('.thumb-opt');
    thumbs.forEach(t => t.classList.remove('active'));
    thumbEl.classList.add('active');
}

function copyMsg(id, msg) {
  navigator.clipboard.writeText(msg).then(() => {
    const btn = document.getElementById('btn-copy-' + id);
    btn.innerHTML = '✓ Copiado';
    btn.style.background = 'var(--nn)';
    btn.style.color = '#fff';
    setTimeout(() => {
      btn.innerHTML = 'Copiar Mensaje';
      btn.style.background = '#fff';
      btn.style.color = 'var(--tx)';
    }, 2000);
  });
}
</script>
</body>
</html>
    """

    def create_card(p, is_today=True):
        initials = (p['nombre'][0] + (p['apellidos'][0] if p['apellidos'] else "")).upper()
        
        # Default image logic
        default_img = "assets/fede_card.png"
        buyer_str = p['buyer'].upper()
        if "HIJO" in buyer_str: default_img = "assets/hijo.png"
        elif "SENIOR" in buyer_str: default_img = "assets/senior.png"
        
        # Custom message
        if p.get('manual'):
            msg = p['msg']
        else:
            msg = f"¡Hola {p['nombre']}! Soy Fede de Nationale-Nederlanden. Te deseo un muy feliz cumpleaños y que pases un día genial con los tuyos. ¡Un fuerte abrazo!"
        
        wa_url = f"https://wa.me/{p['tel'].replace(' ', '').replace('+', '')}?text={msg}"
        card_id = p['tel'] if p['tel'] else p['nombre'].replace(" ","")
        
        return f"""
<div class="card">
  <div class="image-selector">
    <div class="opt-container">
      <img src="assets/fede_card.png" class="thumb-opt {"active" if default_img=="assets/fede_card.png" else ""}" onclick="selectCard('{card_id}', 'assets/fede_card.png', this)" title="Fede Personalizada">
      <span class="opt-label">Fede</span>
    </div>
    <div class="opt-container">
      <img src="assets/senior.png" class="thumb-opt {"active" if default_img=="assets/senior.png" else ""}" onclick="selectCard('{card_id}', 'assets/senior.png', this)" title="Senior">
      <span class="opt-label">Senior</span>
    </div>
    <div class="opt-container">
      <img src="assets/adulto.png" class="thumb-opt {"active" if default_img=="assets/adulto.png" else ""}" onclick="selectCard('{card_id}', 'assets/adulto.png', this)" title="Adulto">
      <span class="opt-label">Adulto</span>
    </div>
    <div class="opt-container">
      <img src="assets/hijo.png" class="thumb-opt {"active" if default_img=="assets/hijo.png" else ""}" onclick="selectCard('{card_id}', 'assets/hijo.png', this)" title="Familiar / Hijo">
      <span class="opt-label">Fami</span>
    </div>
  </div>
  <div class="card-img-wrap">
    <img src="{default_img}" id="main-img-{card_id}" class="card-img" alt="Tarjeta">
  </div>
  <div class="card-header">
    <div class="avatar-small">{initials}</div>
    <div class="info">
      <div class="name">{p['nombre']} {p['apellidos']}</div>
      <div class="buyer">{p['buyer']}</div>
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
    print(f"HTML INTERACTIVO generado en: {OUTPUT_HTML}")

def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.datetime.strptime(date_str.strip(), fmt).date()
        except:
            continue
    return None

def main():
    rows = get_data()
    today = datetime.date.today()
    target_month = today.month
    target_day = today.day
    today_list = []
    week_list = []
    
    # MANUAL OVERRIDES
    elvira_msg = "¡Hola Maria Elvira! Me he acordado de que hoy es el cumpleaños de tu hijo Alex. ¡Muchísimas felicidades para él y para ti también! Espero que lo disfrutéis mucho en familia. ¡Un fuerte abrazo!"
    today_list.append({
        "nombre": "Maria Elvira", "apellidos": "(Hijo Alex)", "tel": "+34609148712", 
        "cumple": "Hoy", "buyer": "HIJO / FAMILIA", 
        "manual": True, "msg": elvira_msg
    })

    for row in rows:
        if len(row) < 6: continue
        nombre = row[0]; apellidos = row[1] if len(row) > 1 else ""; tel = row[3] if len(row) > 3 else ""; cumple_raw = row[5]
        buyer = row[48] if len(row) > 48 else "Cliente"
        if not cumple_raw: continue
        dt = parse_date(cumple_raw)
        if dt:
            if dt.month == target_month and dt.day == target_day:
                if nombre != "Maria Elvira": today_list.append({"nombre": nombre, "apellidos": apellidos, "tel": tel, "cumple": cumple_raw, "buyer": buyer})
            elif dt.month == target_month and target_day < dt.day <= target_day + 7:
                week_list.append({"nombre": nombre, "apellidos": apellidos, "tel": tel, "cumple": cumple_raw, "buyer": buyer})

    generate_html(today_list, week_list)

if __name__ == "__main__":
    try:
        main()
    except RefreshError:
        print("\n❌ ERROR: El token de Google ha caducado o ha sido revocado.")
        print("Para solucionarlo, ejecuta localmente: python Scripts_Herramientas/auth_drive.py")
        sys.exit(0) # Salimos con éxito para no disparar alertas de GitHub
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        sys.exit(0)
