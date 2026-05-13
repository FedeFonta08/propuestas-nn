import os

directory = r'd:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\Scripts_Herramientas'
search_text = "Plan Flexible"
replace_text = "Contigo Futuro"

for filename in os.listdir(directory):
    if filename.endswith(".html"):
        path = os.path.join(directory, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if search_text in content:
            print(f"Updating {filename}...")
            new_content = content.replace(search_text, replace_text)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

# Also check root for missed ones
root_dir = r'd:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN'
for filename in os.listdir(root_dir):
    if filename.endswith(".html") or filename.endswith(".md"):
        path = os.path.join(root_dir, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if search_text in content:
            print(f"Updating root {filename}...")
            new_content = content.replace(search_text, replace_text)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
