import os

TEMPLATE_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/plantilla_email_premium.html'
OUTPUT_DIR = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/previews'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    template = f.read()

proposals = [
    {
        "filename": "preview_senior.html",
        "data": {
            "NOMBRE": "Andrés",
            "OFERTA_TITULO": "Contigo Senior: Protección 360º para tu independencia",
            "OFERTA_DESC": "Capital por accidente de 65.000€, asistencia Sanitas con geriatría y podología, y 6 meses de bonificación exclusiva si contratas este mes.",
            "PAIN_POINT_TEXT": "¿De qué sirve el ahorro de toda una vida si no tienes garantizada la mejor asistencia cuando más la necesitas? Mantén tu autonomía pase lo que pase.",
            "CTA_TEXT": "Activar mis 6 meses de bonificación ahora",
            "CTA_LINK": "#",
            "UNSUBSCRIBE_LINK": "#"
        }
    },
    {
        "filename": "preview_familia.html",
        "data": {
            "NOMBRE": "Ana María",
            "OFERTA_TITULO": "Plan Salud + Vida: Medicina Sanitas + Vida GRATIS",
            "OFERTA_DESC": "Acceso total a la red Sanitas, seguro de vida gratis el primer año y un ahorro recurrente del 12,5% + 4% adicional en tu prima anual.",
            "PAIN_POINT_TEXT": "Tu familia no puede esperar a que las listas de espera de la sanidad pública se despejen. Su salud y tu tranquilidad son hoy, no mañana.",
            "CTA_TEXT": "Ver mi ahorro personalizado en Sanitas",
            "CTA_LINK": "#",
            "UNSUBSCRIBE_LINK": "#"
        }
    },
    {
        "filename": "preview_ahorro.html",
        "data": {
            "NOMBRE": "Carlos",
            "OFERTA_TITULO": "SIALP: Haz crecer tus ahorros sin pagar a Hacienda",
            "OFERTA_DESC": "Exención fiscal total del 100% de rendimientos a partir del año 5. El plan de ahorro más eficiente de España, ahora disponible en Xàtiva.",
            "PAIN_POINT_TEXT": "La inflación y los impuestos se comen tu ahorro cada día de forma silenciosa. Es hora de que el 100% de los beneficios de tu esfuerzo sean solo para ti.",
            "CTA_TEXT": "Empezar a ahorrar sin impuestos",
            "CTA_LINK": "#",
            "UNSUBSCRIBE_LINK": "#"
        }
    }
]

for p in proposals:
    html = template
    for key, val in p["data"].items():
        html = html.replace("{{" + key + "}}", val)
    
    with open(os.path.join(OUTPUT_DIR, p["filename"]), 'w', encoding='utf-8') as f:
        f.write(html)

print("Previews generated in " + OUTPUT_DIR)
