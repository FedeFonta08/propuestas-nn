import smtplib
import time
import csv
import os
import base64
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN MAESTRA
# ═══════════════════════════════════════════════════════════════
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "fefontanals@gmail.com"
SENDER_PASSWORD = "hkmn hkqi kjwn akiz"

CRM_PATH = "../Sistema_Gestion_NN_v4_BuyerPersona - CRM MAESTRO.csv"
TEMPLATE_PATH = "plantilla_email_premium.html"

def get_base64_image(image_filename):
    ALIASES = {
        "agent_header_bar.png": "assets/agent_header_bar.png",
        "banner_hook_salud": "assets/banner_hook_salud_vida_gratis.png",
        "nn_proteccion_banner.png": "Marketing_Branding/4_Proteccion-para-lo-que-mas-importa.png",
        "blindaje_fiscal.png": "Marketing_Branding/Blindaje fiscal para trabajadores autnomos.png"
    }
    filename = ALIASES.get(image_filename, image_filename)
    try:
        paths_to_try = [os.path.join(os.getcwd(), filename), os.path.join(os.getcwd(), "Marketing_Branding", image_filename), os.path.join(os.getcwd(), "assets", image_filename)]
        target_path = None
        for p in paths_to_try:
            if os.path.exists(p): target_path = p; break
        if not target_path: return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        with open(target_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            ext = target_path.split('.')[-1].lower()
            if ext == 'jpg': ext = 'jpeg'
            return f"data:image/{ext};base64,{encoded_string}"
    except Exception: return ""

# ═══════════════════════════════════════════════════════════════
# GENERADORES DE COMPONENTES (v18/10 - PUNTO DE PERFECCIÓN)
# ═══════════════════════════════════════════════════════════════

def get_agent_header_html(fede_photo_b64):
    """Genera una cabecera de agente en HTML puro para máxima nitidez."""
    return """
    <table width="600" cellpadding="0" cellspacing="0" border="0" align="center" style="background-color: #2A2420; color: #ffffff;">
        <tr>
            <td style="padding: 20px 30px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td width="50">
                            <img src="https://raw.githubusercontent.com/fedefonta08/propuestas-nn/main/fede_profile_github.jpg" width="40" height="40" style="display:block; border-radius: 50%; border: 2px solid #E85D26;" alt="Federico Fontanals">
                        </td>
                        <td align="left">
                            <div style="font-size: 14px; font-weight: 700; color: #ffffff;">Federico Fontanals</div>
                            <div style="font-size: 11px; color: #A6A09C;">Agente Dinamizador · Punto Naranja</div>
                            <div style="font-size: 11px; color: #A6A09C;">Nationale-Nederlanden | Xàtiva · La Costera</div>
                        </td>
                        <td align="right" style="font-size: 11px; color: #ffffff;">
                            <div style="margin-bottom: 2px;">
                                <span style="color: #E85D26;">📞</span> <a href="tel:680507186" style="color: #ffffff !important; text-decoration: none; font-weight: 700;"><span style="color: #ffffff !important;">680 507 186</span></a>
                            </div>
                            <div>
                                <span style="color: #E85D26;">✉️</span> <a href="mailto:federico.fontanals@nnespana.es" style="color: #ffffff !important; text-decoration: none;">federico.fontanals@nnespana.es</a>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>"""

def get_header_block():
    """Cabecera con tipografía elevada (v21)."""
    return f"""
    <table width="600" cellpadding="0" cellspacing="0" border="0" align="center" style="background-color: #ffffff; padding: 30px 0 10px 0;">
        <tr>
            <td align="center">
                <div style="font-family: 'Georgia', serif; font-size: 32px; color: #1C1714; font-weight: 700; line-height: 1.1;">Seguridad Global, Salud de Élite</div>
                <div style="font-size: 16px; color: #E85D26; margin-top: 8px; font-weight: 700; letter-spacing: 0.5px;">La solidez de Nationale-Nederlanden y la medicina líder de Sanitas</div>
            </td>
        </tr>
    </table>"""

def get_authority_block():
    """Bloque de autoridad MAESTRO: 6 Tarjetas + 3 Testimonios detallados."""
    card_bg = "#2A2420"
    card_border = "#3A3430"
    orange_text = "#E85D26"
    
    # 6 Tarjetas Detalladas
    cards = [
        ("🏛️", "63 años", "Presencia en España desde 1963", "Generaciones de familias confían en nosotros"),
        ("👥", "800K+", "Clientes en España", "Una de cada 50 familias españolas es cliente NN"),
        ("⭐", "AA-", "Calificación S&P (Solvencia)", "Standard & Poor's: Capacidad sólida de pagar"),
        ("✅", "98.5%", "Siniestros pagados dentro de plazo", "Sin demoras ni sorpresas"),
        ("🌍", "11", "Países europeos", "Grupo Nationale-Nederlanden: presencia continental"),
        ("💡", "100%", "Digitalizado y mobile-first", "Apps gratuitas: Salud + Legal incluidas")
    ]
    
    html = f"""
    <table width="600" cellpadding="0" cellspacing="0" border="0" align="center" style="background-color: #1C1714; border-radius: 12px; margin-top: 25px; padding: 30px 20px;">
        <tr><td align="center" style="padding-bottom: 10px;">
            <div style="font-family: 'Georgia', serif; font-size: 24px; color: #ffffff; font-weight: 700;">¿Por qué elegir Nationale-Nederlanden?</div>
            <div style="font-size: 13px; color: #8B7D75; margin-top: 5px;">Solidez, experiencia y confianza</div>
        </td></tr>
        <tr><td><table width="100%" cellpadding="0" cellspacing="10" border="0">"""
        
    for i in range(0, 6, 3):
        html += "<tr>"
        for j in range(3):
            ico, val, tit, desc = cards[i+j]
            html += f"""
            <td width="33%" align="center" valign="top" style="background-color: {card_bg}; border: 1px solid {card_border}; border-radius: 10px; padding: 15px 10px;">
                <div style="font-size: 20px; margin-bottom: 8px;">{ico}</div>
                <div style="font-size: 18px; font-weight: 700; color: {orange_text};">{val}</div>
                <div style="font-size: 11px; font-weight: 700; color: #ffffff; margin-top: 4px; line-height: 1.2;">{tit}</div>
                <div style="font-size: 9px; color: #AFA6A0; margin-top: 5px; line-height: 1.3;">{desc}</div>
            </td>"""
        html += "</tr>"
        
    html += f"""</table></td></tr>
        <tr><td align="center" style="padding: 25px 0 15px 0;">
            <div style="width: 100%; border-top: 1px solid #3A3430; margin-bottom: 25px;"></div>
            <div style="font-family: 'Georgia', serif; font-size: 18px; color: #ffffff; font-weight: 700;">Lo que dicen nuestros clientes</div>
        </td></tr>
        <tr><td><table width="100%" cellpadding="0" cellspacing="8" border="0"><tr>"""
        
    testimonials = [
        ('"Me salvó la vida. Sin Contigo Autónomo, habría quebrado."', "Javier M. · Barcelona (Autónomo)"),
        ('"El pago fue en 3 días. Sin burocracia, sin sorpresas."', "María L. · Valencia (Siniestro Hogar)"),
        ('"Plan Creciente SIALP: el mejor ahorro sin tributar que conozco."', "Carlos P. · Madrid (Planificador)")
    ]
    
    for txt, sig in testimonials:
        html += f"""
        <td width="33%" align="left" valign="top" style="background-color: #241F1C; border-radius: 10px; padding: 15px 12px; border: 1px solid #3A3430;">
            <div style="color: #FFD700; font-size: 12px; margin-bottom: 8px;">★★★★★</div>
            <div style="font-size: 10px; color: #ffffff; font-style: italic; line-height: 1.5; margin-bottom: 10px;">{txt}</div>
            <div style="font-size: 9px; color: {orange_text}; font-weight: 700;">{sig}</div>
        </td>"""
        
    html += "</tr></table></td></tr></table>"
    return html

def get_footer_block():
    """Footer 'Imagen 30' - El Punto de Perfección."""
    return """
    <table width="600" cellpadding="0" cellspacing="0" border="0" align="center" style="background-color: #F4F1EE; padding: 35px 0;">
        <tr>
            <td align="center" style="padding-bottom: 25px; font-size: 11px; color: #6D6661; line-height: 1.5;">
                <strong style="color: #4A4440; font-size: 12px;">NATIONALE-NEDERLANDEN VIDA Y GENERALES</strong><br/>
                Av. de Bruselas, 16 · Parque Arroyo de la Vega · 28108 Alcobendas (Madrid)<br/>
                <a href="tel:+34916026000" style="color: #E85D26; text-decoration: none; font-weight: 700; font-size: 12px;">☎ +34 91 602 60 00</a>
            </td>
        </tr>
        <tr>
            <td align="center" style="padding-bottom: 25px;">
                <div style="font-size: 10px; color: #8B7D75; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">DERECHOS RGPD/LOPDGDD</div>
                <a href="mailto:dpo@nnespana.es" style="color: #E85D26; font-size: 11px; text-decoration: underline; font-weight: 700;">Ejercer derechos ARCO · DPO</a><br/>
                <a href="https://www.aepd.es" style="color: #E85D26; font-size: 11px; text-decoration: underline; font-weight: 700;">Reclamaciones ante AEPD</a>
            </td>
        </tr>
        <tr>
            <td align="center" style="padding: 0 45px 35px 45px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border: 1.5px solid #E85D26; border-radius: 12px; background-color: #ffffff; padding: 22px;">
                    <tr>
                        <td align="center">
                            <div style="font-size: 19px; font-weight: 700; color: #1C1714; margin-bottom: 3px;">🟠 Federico Fontanals</div>
                            <div style="font-size: 10px; color: #8B7D75; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 18px;">AGENTE DINAMIZADOR PUNTO NARANJA · XÀTIVA</div>
                            <table align="center" cellpadding="0" cellspacing="10" border="0">
                                <tr>
                                    <td><a href="mailto:federico.fontanals@nnespana.es" style="background-color: #FDFCFB; border: 1px solid #EEE9E5; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: #1C1714; font-size: 11px; font-weight:700;"><img src="https://cdn-icons-png.flaticon.com/32/542/542689.png" width="14" style="display:inline; vertical-align:middle; margin-right:5px;"> Email</a></td>
                                    <td><a href="tel:+34680507186" style="background-color: #FDFCFB; border: 1px solid #EEE9E5; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: #1C1714; font-size: 11px; font-weight:700;"><img src="https://cdn-icons-png.flaticon.com/32/159/159832.png" width="14" style="display:inline; vertical-align:middle; margin-right:5px;"> Llamada</a></td>
                                    <td><a href="https://wa.me/34680507186" style="background-color: #FDFCFB; border: 1px solid #EEE9E5; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: #1C1714; font-size: 11px; font-weight:700;"><img src="https://cdn-icons-png.flaticon.com/32/1384/1384055.png" width="14" style="display:inline; vertical-align:middle; margin-right:5px;"> WhatsApp</a></td>
                                </tr>
                            </table>
                            <div style="font-size: 9px; color: #AFA6A0; margin-top: 15px; line-height:1.4;">Documento informativo no contractual · Datos verificados NN</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 25px 40px; background-color: #FFE5D9; border-radius: 8px;">
                <div style="font-size: 11px; color: #E85D26; text-align: center; margin-bottom: 12px; font-weight:700;">⚖️ Información sobre Protección de Datos (RGPD)</div>
                <div style="font-size: 10px; color: #7A3E26; line-height: 1.6; text-align: justify;">
                    <strong>Responsable:</strong> Nationale-Nederlanden Vida y Generales S.A.E. (Madrid).<br/>
                    <strong>Derechos:</strong> Acceso, Rectificación, Cancelación y Oposición. Puede revocar su consentimiento en cualquier momento.
                </div>
                <table width="100%" cellpadding="0" cellspacing="8" border="0" style="margin-top: 15px;">
                    <tr>
                        <td><a href="mailto:dpo@nnespana.es" style="display:block; background-color:#ffffff; border:1px solid #E85D26; border-radius:15px; padding:8px; color:#E85D26; text-decoration:none; font-size:9px; font-weight:700; text-align:center;">Ejercer derechos ARCO</a></td>
                        <td><a href="https://www.nnespana.es" style="display:block; background-color:#ffffff; border:1px solid #E85D26; border-radius:15px; padding:8px; color:#E85D26; text-decoration:none; font-size:9px; font-weight:700; text-align:center;">Política privacidad</a></td>
                        <td><a href="https://www.aepd.es" style="display:block; background-color:#ffffff; border:1px solid #E85D26; border-radius:15px; padding:8px; color:#E85D26; text-decoration:none; font-size:9px; font-weight:700; text-align:center;">Reclamar AEPD</a></td>
                    </tr>
                </table>
                <div style="font-size: 9px; color: #7A3E26; text-align: center; margin-top: 15px; border-top: 1px solid #FFD1BC; padding-top: 10px;">
                    Responda "BAJA" para excluirse de comunicaciones comerciales.
                </div>
            </td>
        </tr>
    </table>"""

def get_faq_block(segmento):
    faqs_data = {"AHORRO": [("¿Puedo sacar el dinero antes?", "Sí, liquidez total desde el primer día."), ("¿Qué garantía real tengo?", "Capital blindado por la solvencia de NN.")], "SALUD": [("¿Hay carencias?", "Sí, pero el contador empieza hoy."), ("¿Especialista directo?", "Acceso directo a la red Sanitas.")], "GENERAL": [("¿Es compatible?", "Totalmente. Actúa como mejora o capa extra."), ("¿Qué solvencia?", "63 años en España y calificación AA-.")]}
    items = faqs_data.get(segmento, faqs_data["GENERAL"])
    html = '<table width="100%" cellpadding="0" cellspacing="0" border="0">'
    for q, a in items:
        html += f'<tr><td style="padding-bottom: 6px;"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border: 1px solid #EEE9E5; border-radius: 8px; background-color: #FDFCFB;"><tr><td style="padding: 10px 15px;"><div style="font-size: 12px; font-weight: 700; color: #1C1714; margin-bottom: 3px;">{q}</div><div style="font-size: 11px; color: #6A5F5A; line-height: 1.4;">{a}</div></td></tr></table></td></tr>'
    return html + '</table>'

def get_personalization(row):
    segmento_bp = str(row.get('SEGMENTO_BP', '')).upper(); nombre_pila = row.get('Nombre_Pila', 'Cliente')
    
    # Cargar fotos y banner maestro OPTIMIZADO (Base64)
    try:
        import base64
        with open("fede_profile_github.jpg", "rb") as f: fede_photo_b64 = base64.b64encode(f.read()).decode()
        banner_maestro_b64 = get_base64_image("assets/banner_hook_salud_vida_gratis.jpg")
    except: fede_photo_b64 = banner_maestro_b64 = ""
    
    data = {
        "PREHEADER": f"Documentación Consultiva para {nombre_pila}.",
        "BRAND_HEADER_BLOCK": get_header_block(),
        "AGENT_HEADER_HTML": get_agent_header_html(fede_photo_b64),
        "AUTHORITY_BLOCK": get_authority_block(),
        "MASTER_BANNER_IMAGE": "cid:banner_maestro",
        "OFERTA_TITULO": "Salud Premium con Blindaje de Vida",
        "PAIN_POINT_TEXT": "Acceder a la medicina de élite es una prioridad. Garantizamos acceso inmediato a especialistas Sanitas, sin esperas.",
        "CTA_TEXT": "Ver Mi Propuesta de Salud",
        "CTA_LINK": "https://wa.me/34680507186",
        "FAQ_BLOCK": get_faq_block("SALUD"),
        "FOOTER_BLOCK": get_footer_block(),
        "EMPATHY_LINE": "Esta propuesta integra el acceso médico Élite con un seguro de vida sin coste el primer año."
    }
    return data
    return data

def enviar_campana(test_mode=True, limit=None, skip=0):
    priority_mode = "--priority" in sys.argv
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            html_template = f.read()
            
        with open(CRM_PATH, mode='r', encoding='utf-8') as f:
            next(f) # Saltar cabecera 1
            reader = csv.DictReader(f, delimiter=',')
            count = 0
            
            print(f"Conectando al servidor SMTP para {'ENVÍO REAL' if not test_mode else 'MODO TEST'}...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            for row in reader:
                count += 1
                if count <= skip:
                    continue
                
                urgencia = row.get('Urgencia', '').upper()
                if priority_mode and not any(m in urgencia for m in ['MAYO', 'ABRIL', 'URGENTE']):
                    continue
                
                nombre_completo = row.get('Nombre completo', '').strip()
                email_destinatario = row.get('Email', '').strip()
                
                if not email_destinatario or "@" not in email_destinatario:
                    continue
                    
                nombre_pila = nombre_completo.split(' ')[0].capitalize() if nombre_completo else "Cliente"
                row['Nombre_Pila'] = nombre_pila
                
                if test_mode:
                    email_destinatario = SENDER_EMAIL
                    
                p = get_personalization(row)
                html_final = html_template
                for key, value in p.items():
                    html_final = html_final.replace(f"{{{{{key}}}}}", value)
                html_final = html_final.replace("{{NOMBRE}}", nombre_pila)
                
                msg = MIMEMultipart()
                msg['From'] = f"Federico Fontanals <{SENDER_EMAIL}>"
                msg['To'] = email_destinatario
                msg['Subject'] = f"Documentación Consultiva: Propuesta Estratégica para {nombre_pila}"
                msg.attach(MIMEText(html_final, 'html'))
                
                # Adjuntar Banner Maestro como CID
                try:
                    with open("assets/banner_hook_salud_vida_gratis.jpg", "rb") as img_f:
                        msg_img = MIMEImage(img_f.read())
                        msg_img.add_header('Content-ID', '<banner_maestro>')
                        msg_img.add_header('Content-Disposition', 'inline', filename="banner_maestro.jpg")
                        msg.attach(msg_img)
                except Exception as e:
                    print(f"Error adjuntando imagen CID: {e}")

                server.send_message(msg)
                print(f"OK [{'REAL' if not test_mode else 'TEST'}]: Enviado a {email_destinatario} ({nombre_pila})")
                count += 1
                
                if not test_mode:
                    time.sleep(2) # Cadencia de seguridad
                
                if limit and count >= limit:
                    break
            
            server.quit()
            print(f"\n✅ Proceso finalizado. Total correos procesados: {count}")
            
    except Exception as e:
        print(f"Error crítico en el motor de envío: {e}")

if __name__ == "__main__":
    import sys
    if "--send" in sys.argv: enviar_campana(test_mode=False)
    else: enviar_campana(test_mode=True, limit=1)
