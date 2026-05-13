import base64
import os

# Leer los Base64 de los archivos temporales
def read_b64(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return f.read().strip()
    return None

b64_nn = read_b64('nn_logo_base64.txt')
b64_sanitas = read_b64('sanitas_logo_base64.txt')
b64_fede = read_b64('fede_photo_base64.txt')

# Actualizar Plantilla
if os.path.exists('plantilla_email_premium.html'):
    with open('plantilla_email_premium.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Inyectar Foto Fede en la firma (reemplazando el círculo naranja)
    if b64_fede:
        fede_img_html = f'<img src="data:image/jpeg;base64,{b64_fede}" width="80" height="80" style="display:block; border-radius:50%; border:3px solid #E85D26; box-shadow: 0 5px 15px rgba(0,0,0,0.2);" />'
        # Buscar el placeholder de la firma (el div con FF)
        old_signature_box = '<div style="width: 35px; height: 35px; border-radius: 50%; color: #ffffff; font-weight: bold; font-size: 20px; text-align: center; line-height: 35px;">N</div>'
        # En la nueva plantilla minimalista es un poco diferente, busquemos el bloque de firma
        html = html.replace('<div style="width: 80px; height: 80px; background-color: #E85D26; border-radius: 50%; text-align: center; color: #ffffff; font-size: 35px; font-weight: bold; line-height: 80px; box-shadow: 0 10px 20px rgba(0,0,0,0.4);">FF</div>', fede_img_html)
        # También el de la cabecera minimalista
        if b64_nn:
            html = html.replace('<td bgcolor="#E85D26" style="width: 35px; height: 35px; border-radius: 50%; color: #ffffff; font-weight: bold; font-size: 20px; text-align: center; line-height: 35px;">N</td>', f'<td><img src="data:image/png;base64,{b64_nn}" width="35" style="display:block;"/></td>')

    with open('plantilla_email_premium.html', 'w', encoding='utf-8') as f:
        f.write(html)

# Actualizar Script
if os.path.exists('enviar_campana_nn.py'):
    with open('enviar_campana_nn.py', 'r', encoding='utf-8') as f:
        script = f.read()
    
    if b64_sanitas:
        script = script.replace('https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Logo_Sanitas.svg/512px-Logo_Sanitas.svg.png', f'data:image/png;base64,{b64_sanitas}')
    
    with open('enviar_campana_nn.py', 'w', encoding='utf-8') as f:
        f.write(script)
