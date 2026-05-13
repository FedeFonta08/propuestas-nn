import os
import re

# Directorios a procesar
DIRS = [
    r'd:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN',
    r'd:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\Scripts_Herramientas'
]

# Mapa de reemplazos
REPLACEMENTS = {
    '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0': '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0',
    'RADAR COMERCIAL': 'RADAR COMERCIAL',
    'RADAR COMERCIAL': 'RADAR COMERCIAL',
    'RADAR COMERCIAL': 'RADAR COMERCIAL',
    'NOVEDADES PRODUCTO': 'NOVEDADES PRODUCTO',
    'NOVEDADES PRODUCTO': 'NOVEDADES PRODUCTO',
    'DASHBOARD AGENCIA': 'DASHBOARD AGENCIA',
    'DASHBOARD AGENCIA': 'DASHBOARD AGENCIA'
}

def rewire():
    count_files = 0
    count_replaces = 0
    
    for d in DIRS:
        for filename in os.listdir(d):
            if filename.endswith(('.html', '.js', '.py', '.md', '.txt', '.bat')):
                filepath = os.path.join(d, filename)
                
                # Leer contenido
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(filepath, 'r', encoding='cp1252') as f:
                            content = f.read()
                    except:
                        continue

                new_content = content
                file_changed = False
                
                for old, new in REPLACEMENTS.items():
                    if old in new_content:
                        new_content = new_content.replace(old, new)
                        file_changed = True
                        count_replaces += 1
                
                if file_changed:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Re-cableado: {filename}")
                    count_files += 1

    print(f"\nRe-cableado completado! {count_files} archivos actualizados con {count_replaces} reemplazos.")

if __name__ == "__main__":
    rewire()
