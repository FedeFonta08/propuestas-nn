import os
import sys
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Importar configuración del script principal
sys.path.append('d:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN')
from enviar_campana_nn import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, load_template, get_personalization

TEST_EMAILS = [
    "fefontanals@gmail.com", 
    "federico.fontanals@nnespana.es", 
    "fedefontanals01@gmail.com", 
    "fede.fonta.cuba@gmail.com"
]

def send_test():
    print("Enviando 4 pruebas de diseño a tus cuentas...")
    
    if SENDER_PASSWORD == "your_app_password_here":
        print("❌ ERROR: Debes poner tu contraseña en enviar_campana_nn.py")
        return

    html_base = load_template()
    context = ssl.create_default_context()
    
    # Variaciones para que veas los 3 diseños y el toque de empatía
    variaciones = [
        {"segmento": "S5 - Senior", "nombre": "Fede Senior", "obs": "Interés en autonomía y servicios Sanitas"},
        {"segmento": "S3 - Protector", "nombre": "Fede Familia", "obs": "Dos hijos, busca blindaje familiar"},
        {"segmento": "S4 - Planificador", "nombre": "Fede Ahorro", "obs": ""}, # Sin observaciones para ver el default
        {"segmento": "S3A - Autónomo", "nombre": "Fede Autónomo", "obs": "Preocupado por la baja laboral"}
    ]

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            for i, email_dest in enumerate(TEST_EMAILS):
                var = variaciones[i]
                
                # Capa de Inteligencia y Empatía
                perso = get_personalization(var["nombre"], var["segmento"], var["obs"])
                
                message = MIMEMultipart("alternative")
                message["Subject"] = f"🧪 PRUEBA DISEÑO [{var['segmento']}] - NN Xàtiva"
                message["From"] = f"Federico Fontanals <{SENDER_EMAIL}>"
                message["To"] = email_dest
                
                html_final = html_base
                for key, val in perso.items():
                    html_final = html_final.replace("{{" + key + "}}", val)
                
                part = MIMEText(html_final, "html")
                message.attach(part)
                
                server.sendmail(SENDER_EMAIL, email_dest, message.as_string())
                print(f"Enviada prueba {i+1}/4 a: {email_dest} [BP: {var['segmento']}]")
                time.sleep(2)

    except Exception as e:
        print(f"Error critico en el test: {e}")

if __name__ == "__main__":
    send_test()
