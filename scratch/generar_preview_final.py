import csv
import os
import sys

# Añadir el directorio actual al path para importar el motor
sys.path.append(os.getcwd())
import enviar_campana_nn as engine

TEMPLATE_PATH = "plantilla_email_premium.html"
CRM_PATH = "../Sistema_Gestion_NN_v4_BuyerPersona - CRM MAESTRO.csv"

def generate_preview():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_template = f.read()
    
    with open(CRM_PATH, mode='r', encoding='utf-8') as f:
        next(f) # Skip header line 1
        reader = csv.DictReader(f)
        row = next(reader) # Tomamos el primer contacto (Ana Maria Sarrio)
        
        nombre_pila = row.get('Nombre completo', '').split(' ')[0].capitalize()
        p = engine.get_personalization(row)
        
        html_final = html_template
        for key, value in p.items():
            # Corregir el CID para previsualización local (apuntar al archivo físico)
            if value == "cid:banner_maestro":
                value = "assets/banner_hook_salud_vida_gratis.jpg"
            html_final = html_final.replace(f"{{{{{key}}}}}", value)
        
        html_final = html_final.replace("{{NOMBRE}}", nombre_pila)
        
        # Inyectar estilos para visualización de escritorio
        with open("preview_final_despegue.html", "w", encoding="utf-8") as out:
            out.write(html_final)
        
        print("✅ Previsualización generada: preview_final_despegue.html")

if __name__ == "__main__":
    generate_preview()
