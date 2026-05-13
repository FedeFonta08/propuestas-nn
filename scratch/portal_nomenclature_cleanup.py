import os

directory = r'd:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN'
sub_directory = os.path.join(directory, 'Scripts_Herramientas')

replacements = {
    "Plan de Ahorro Remunerado": "Flexicuenta Asegurada",
    "Plan de Ahorro Garantizado": "Ahorro Garantizado Extra",
    "Plan SIALP": "SIALP",
    "Plan Creciente SIALP": "SIALP"
}

def process_dir(target_dir):
    for filename in os.listdir(target_dir):
        if filename.endswith(".html") or filename.endswith(".md"):
            path = os.path.join(target_dir, filename)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            modified = False
            for old, new in replacements.items():
                if old in content:
                    print(f"Updating {old} -> {new} in {filename}...")
                    content = content.replace(old, new)
                    modified = True
            
            if modified:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

process_dir(directory)
process_dir(sub_directory)
