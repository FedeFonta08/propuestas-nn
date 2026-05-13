import csv
from collections import Counter
import os

path = '../Sistema_Gestion_NN_v4_BuyerPersona - CRM MAESTRO.csv'
if not os.path.exists(path):
    path = 'Sistema_Gestion_NN_v4_BuyerPersona - CRM MAESTRO.csv'

with open(path, mode='r', encoding='utf-8') as f:
    next(f)
    reader = csv.DictReader(f)
    data = list(reader)

bp = Counter([r.get('Buyer Persona', '').strip() for r in data])
prod = Counter([r.get('Producto NN recomendado', '').strip() for r in data])
urgency = Counter([r.get('Urgencia', '').strip() for r in data])

print(f"Total Contacts: {len(data)}")
print("\n--- Buyer Persona ---")
for k, v in bp.most_common():
    print(f"{k.encode('ascii', 'ignore').decode()}: {v}")

print("\n--- Recommended Product ---")
for k, v in prod.most_common():
    print(f"{k.encode('ascii', 'ignore').decode()}: {v}")

print("\n--- Urgency/Month ---")
for k, v in urgency.most_common():
    print(f"{k.encode('ascii', 'ignore').decode()}: {v}")
