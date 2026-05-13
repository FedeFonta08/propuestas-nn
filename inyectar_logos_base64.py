import base64
import requests
import os

def get_base64(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# URLs
url_nn = "https://www.nnespana.es/etc.clientlibs/nn-espana/clientlibs/clientlib-site/resources/images/nn-logo.png"
url_sanitas = "https://www.sanitas.es/portal/img/logo-sanitas.png"

print("Obteniendo Base64 de los logos...")
base64_nn = get_base64(url_nn)
base64_sanitas = get_base64(url_sanitas)

if base64_nn:
    print("Actualizando plantilla_email_premium.html...")
    with open('plantilla_email_premium.html', 'r', encoding='utf-8') as f:
        content = f.read()
    # Reemplazar cualquier URL de logo por el Base64
    content = content.replace('https://logodownload.org/wp-content/uploads/2019/09/nationale-nederlanden-logo.png', f'data:image/png;base64,{base64_nn}')
    with open('plantilla_email_premium.html', 'w', encoding='utf-8') as f:
        f.write(content)

if base64_sanitas:
    print("Actualizando enviar_campana_nn.py...")
    with open('enviar_campana_nn.py', 'r', encoding='utf-8') as f:
        content = f.read()
    # Reemplazar URL de Sanitas
    content = content.replace('https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Logo_Sanitas.svg/512px-Logo_Sanitas.svg.png', f'data:image/png;base64,{base64_sanitas}')
    with open('enviar_campana_nn.py', 'w', encoding='utf-8') as f:
        f.write(content)

print("¡Hecho! Logos inyectados.")
