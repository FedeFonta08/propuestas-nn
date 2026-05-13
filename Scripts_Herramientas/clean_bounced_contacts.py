import os
import sys
import gspread
import json
from google.oauth2.credentials import Credentials

# Configuration
SPREADSHEET_ID = '16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0'
TOKEN_PATH = 'd:/Users/ffont/Downloads/06_NATIONALE_NEDERLANDEN/Scripts_Herramientas/token.json'
CRM_TAB = 'CRM MAESTRO'

sys.stdout.reconfigure(encoding='utf-8')

bounced_emails = [
    "lilianaborissova6@hotmail.com",
    "eelnectardelsol@gmail.com",
    "amadeannauir@gmail.com",
    "alfabo46@hotmail.com",
    "isabeltalontortosa@gamil.com",
    "carolinapallarosa04@gmail.com",
    "eduportes655@gmail.com",
    "ntmxativa@hotmail.co",
    "jfca1210@gmail.com",
    "keisymolinab@gmail.com",
    "farandaarguelleo@gmail.com",
    "antoniopastormorell@gmail.com",
    "francesxativa@hotmail.com",
    "jonathanlangaromero@gmail.com",
    "horno-hispania@hotmail.com",
    "rafalarage@gmail.com",
    "chimoperezgomez@gmail.com",
    "p.nehaus@hotmail.com",
    "jobellro@gmal.com",
    "jorquescirilo@gmail.com",
    "trinidadcayuelasoler@gmail.com",
    "noelitaxtv@gmail.com",
    "juanrtsto@gmail.com",
    "saraide@hotmail.com",
    "ximon8094@gmail.com"
]

def suggest_correction(email):
    # Technical domain corrections
    corrections = {
        "@gamil.com": "@gmail.com",
        "@gmal.com": "@gmail.com",
        "@hotmail.co": "@hotmail.com",
        "@hotmai.com": "@hotmail.com",
        "@outlok.com": "@outlook.com",
        "@protonmial.com": "@protonmail.com"
    }
    
    for typo, fixed in corrections.items():
        if email.endswith(typo):
            return email.replace(typo, fixed)
    
    # Specific common cases found in the list
    if email == "ntmxativa@hotmail.co": return "ntmxativa@hotmail.com"
    
    return None

def main():
    if not os.path.exists(TOKEN_PATH):
        print(f"Error: Token not found at {TOKEN_PATH}")
        return

    print("🌐 Connecting to Google Sheets...")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets'])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(CRM_TAB)
    
    print("📊 Fetching CRM data...")
    data = sheet.get_all_values()
    headers = data[1] # Row 2 contains headers
    
    try:
        email_col = headers.index('Email')
        name_col = headers.index('Nombre completo')
        phone_col = headers.index('Teléfono 1')
        status_col = headers.index('Estado')
    except ValueError as e:
        print(f"Error: Could not find required columns in headers. {e}")
        return

    to_call = []
    corrections_made = []
    cleared_count = 0
    
    print(f"🔎 Scanning {len(data)-2} contacts for {len(bounced_emails)} bounces...")
    
    # Start from row 3 (index 2) to skip headers
    for i in range(2, len(data)):
        row = data[i]
        if len(row) <= email_col: continue
        
        current_email = row[email_col].strip().lower()
        if not current_email: continue
        
        if current_email in bounced_emails:
            name = row[name_col]
            phone = row[phone_col]
            
            # Check for correction
            corrected = suggest_correction(current_email)
            
            if corrected:
                print(f"✅ Correcting: {current_email} -> {corrected} for {name}")
                sheet.update_cell(i + 1, email_col + 1, corrected)
                corrections_made.append({"name": name, "old": current_email, "new": corrected})
            else:
                print(f"❌ Clearing: {current_email} for {name}")
                # Clear email and set status
                sheet.update_cell(i + 1, email_col + 1, "")
                sheet.update_cell(i + 1, status_col + 1, "Llamar - Email Mal")
                
                to_call.append({
                    "Nombre": name,
                    "Teléfono": phone,
                    "Email_Erróneo": current_email
                })
                cleared_count += 1

    # Generate Call List Artifact
    if to_call:
        print("📝 Generating call list artifact...")
        artifact_path = "C:/Users/ffont/.gemini/antigravity/brain/66cd440b-b1ef-482a-b95f-827f7a1ffb96/lista_llamadas_emails_mal.md"
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write("# 📞 Lista de Llamadas: Corrección de Emails\n\n")
            f.write("Estos contactos tenían un email erróneo que no se pudo corregir automáticamente. Se ha borrado el email en el CRM y marcado como 'Llamar - Email Mal'.\n\n")
            f.write("| Nombre | Teléfono | Email Antiguo |\n")
            f.write("| :--- | :--- | :--- |\n")
            for contact in to_call:
                f.write(f"| {contact['Nombre']} | {contact['Teléfono']} | {contact['Email_Erróneo']} |\n")
        print(f"✅ Call list generated at {artifact_path}")

    print("\n--- SUMMARY ---")
    print(f"Corrections applied: {len(corrections_made)}")
    print(f"Contacts cleared and added to call list: {cleared_count}")
    print("----------------")

if __name__ == "__main__":
    main()
