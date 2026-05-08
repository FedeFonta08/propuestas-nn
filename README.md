# 🟠 Ecosistema Comercial NN — Punto Naranja Xàtiva

**Sistema integrado de herramientas comerciales · Nationale-Nederlanden**  
*Federico Fontanals Serra · Delegado Punto Naranja · La Costera (Valencia)*

---

## 📦 Herramientas del ecosistema

| Herramienta | Archivo | URL | Propósito |
|-------------|---------|-----|-----------|
| **Panel DESPEGUE** | `index.html` | [Ver dashboard](https://fedefonta08.github.io/propuestas-nn/) | Dashboard principal: PVM, estado sprint, tareas pendientes |
| **Portal Propuestas** | `propuestas.html` | [Ver portal](https://fedefonta08.github.io/propuestas-nn/propuestas.html) | Propuestas personalizadas por URL parametrizada |
| **CRM Panel v2** | `nn_crm_panel_v2.html` | [Ver CRM](https://fedefonta08.github.io/propuestas-nn/nn_crm_panel_v2.html) | Gestión de contactos, búsqueda, historial |
| **Sistema Llamadas** | `aperturas_desktop_v4.html` | [Ver sistema](https://fedefonta08.github.io/propuestas-nn/aperturas_desktop_v4.html) | Workflow de llamadas comerciales |
| **Modo Enfoque Pro** | Standalone HTML | Local/Drive | Call scripting + registro CRM integrado |
| **Reclutamiento NN** | `Reclutamiento_NN_v2.html` | Local/Drive | Gestión pipeline de candidatos |

---

## 🏗️ Arquitectura del sistema

### Frontend
- **Tecnología:** HTML5 + CSS3 + JavaScript vanilla
- **Design System:** Bebas Neue + DM Sans, naranja NN (#C94D00, #FF6200), navy (#0A1628)
- **Responsive:** Mobile-first, compatible iPad/Desktop
- **Dependencias:** Google Fonts únicamente (sin CDN externos)
- **Analytics:** Google Analytics 4 (`G-5P41S83SWG`)

### Backend
- **Apps Script Endpoint:**  
  `https://script.google.com/macros/s/AKfycbxpYhW-S9OvA3w1NTR_Mu6GHffGTtHKE1ENKgoM98ySB8gyxt-j4BbaKF7Mk48grrcr_g/exec`
- **Patrón de llamada:** GET con payload JSON en query string (compatibilidad CORS)
- **Acciones disponibles:** `buscar_contacto`, `ficha_contacto`, `registrar_llamada`, `crear_evento_calendar`
- **Calendario:** `fefontanals@gmail.com`, timezone `Europe/Madrid`

### Datos
- **CRM Master:** `Sistema_Gestion_NN_v4_BuyerPersona.xlsx` (965 contactos × 51 columnas × 8 tabs)
- **Radar Comercial:** Google Sheet ([ver](https://docs.google.com/spreadsheets/d/1mYKiIdoglAxzFwJOE_0V8CyHwNUsKkh_oPtkUKg4GCQ)) — tab `🟠 Campañas Activas`
- **Almacenamiento local:** localStorage para sesiones y preferencias

---

## 🔄 Workflows principales

### 1️⃣ Portal de Propuestas Personalizadas

**Caso de uso:** Enviar propuestas visuales por enlace directo

**URL base:**
```
https://fedefonta08.github.io/propuestas-nn/propuestas.html
```

**Parámetros disponibles:**

| Parámetro | Valores | Ejemplo |
|-----------|---------|---------|
| `producto` | `autonomo` / `familia` / `futuro` / `senior` | `autonomo` |
| `nombre` | Nombre del cliente | `Salvador` |
| `beneficiario` | Nombre beneficiario (opcional) | `María` |
| `prima` | Prima mensual | `39,94 €` |
| `capital` | Capital asegurado (opcional) | `266.000 €` |

**Ejemplo real — Contigo Autónomo:**
```
https://fedefonta08.github.io/propuestas-nn/propuestas.html?producto=autonomo&nombre=Salvador&prima=39,94 €
```

**Workflow típico:**
1. Contacto telefónico inicial → recoger datos básicos
2. Generar URL personalizada con parámetros
3. Enviar por email/WhatsApp desde cuenta NN
4. Seguimiento en 24-48h

**Plantilla email:**
```
Hola [Nombre],

Como hablamos, aquí está tu propuesta de [Producto]:

👉 Ver propuesta personalizada: [ENLACE]

¿Tienes dudas? Llámame o escríbeme.

Un saludo,
Fede Fontanals
Delegado Punto Naranja NN · Xàtiva
680 507 186
```

---

### 2️⃣ Sistema de Llamadas Comerciales

**Caso de uso:** Workflow estructurado de llamadas diarias (objetivo: 8 llamadas/día, 2 bloques)

**Flujo operativo:**
1. **Preparación noche anterior:** seleccionar 8-10 contactos del CRM
2. **Pre-WhatsApp:** mensaje 5 min antes de llamar (mejora tasa de respuesta)
3. **Llamada:** script by buyer persona, evitar palabra "seguro" primeros 30s
4. **Registro:** resultado + notas + próxima acción en CRM
5. **Seguimiento:** calendario automático si fija cita

**Integración con CRM:**
- Búsqueda de contacto en tiempo real
- Carga automática de historial de llamadas
- Selección dinámica de buyer persona según segmento CRM
- Registro directo a Google Sheets

---

### 3️⃣ CRM Panel — Gestión de Contactos

**Caso de uso:** Búsqueda rápida, historial, próximas acciones

**Funcionalidades:**
- Búsqueda por nombre/teléfono con autocompletado
- Ficha completa: datos personales, productos Santalucía, buyer persona, historial
- Registro de llamadas con timestamp
- Creación de eventos en Google Calendar
- Exportación CSV de sesión

**Nota importante:** Los 965 contactos base son **prospectos fríos NN**, no clientes existentes. Sus productos listados (Decesos, Hogar, Vida) son de Santalucía. NN no ofrece Decesos → mapear a Contigo Senior (55+), Plan Salud+Vida, MiHogar Seguro o PPSA según edad/perfil.

---

### 4️⃣ Modo Enfoque Pro

**Caso de uso:** Sesión de llamadas intensiva con scripting integrado

**Características:**
- 3 fases: Preparar → Llamar → Registrar
- 8 perfiles buyer persona con inyección dinámica de nombre
- WhatsApp pre-llamada + countdown 5 min
- Timer de llamada en vivo
- 10 objeciones con respuestas predefinidas
- 4 botones resultado (venta, cita, seguimiento, no interés)
- Registro automático a Sheets + Calendar

---

## ⚙️ Configuración inicial

### 1. GitHub Pages
El repositorio está configurado para desplegar automáticamente en:
```
https://fedefonta08.github.io/propuestas-nn/
```

**Rama activa:** `main`

### 2. Google Analytics
Tracking ID: `G-5P41S83SWG`  
Configurado en todos los archivos HTML del proyecto.

### 3. Apps Script Backend
Endpoint público configurado con permisos de ejecución.  
**Acciones disponibles:** ver sección Arquitectura.

### 4. Datos del CRM
Ubicación: Drive `fefontanals@gmail.com`  
**⚠️ CRÍTICO:** Todas las operaciones de escritura deben ir a esta cuenta, NO a `fede.fonta.cuba@gmail.com`

---

## 🐛 Troubleshooting común

### ❌ "La propuesta no carga los datos del cliente"
**Causa:** Parámetros URL mal formateados o caracteres especiales sin codificar  
**Solución:** Usar `encodeURIComponent()` para valores con espacios o caracteres especiales

### ❌ "El CRM no encuentra el contacto"
**Causa:** Búsqueda por columna incorrecta o formato de datos inconsistente  
**Solución:** Verificar que el nombre/teléfono coincida exactamente con el formato del Excel

### ❌ "Error CORS en llamadas al backend"
**Causa:** Apps Script requiere patrón GET con payload en query string  
**Solución:** Usar `?payload=` + JSON codificado, no POST

### ❌ "Las URLs de GitHub Pages no funcionan"
**Causa:** Push reciente no ha desplegado aún  
**Solución:** Esperar 2-3 minutos tras hacer `git push`, verificar en Settings > Pages

---

## 🛠️ Mantenimiento y advertencias

### ⚠️ CUIDADO con el borrado de archivos
**Regla de oro:** No eliminar ningún archivo sin estar 100% seguro de que no se usa.

**Archivos críticos (NO TOCAR):**
- `index.html` — Panel DESPEGUE principal
- `propuestas.html` — Portal de propuestas
- `nn_crm_panel_v2.html` — CRM Panel
- `aperturas_desktop_v4.html` — Sistema de llamadas

**Archivos reemplazables:**
- `fede.jpg` / `fede_profile_github.jpg` — Foto de perfil (actualizar con imagen real)

### 🔄 Actualización de contenido
1. Modificar el archivo HTML localmente
2. Probar en navegador local (`file://` o servidor local)
3. Commit y push a GitHub:
```bash
git add .
git commit -m "Descripción del cambio"
git push https://[TOKEN]@github.com/FedeFonta08/propuestas-nn.git main
```
4. Esperar 2-3 min para despliegue automático en Pages

**Nota:** Los tokens de GitHub expiran entre sesiones. Generar nuevo token en Settings > Developer settings > Personal access tokens cuando sea necesario.

---

## 📊 Productos NN disponibles

| Producto | Código | PVM típico | Perfil ideal |
|----------|--------|------------|--------------|
| **Contigo Familia** | Plan Salud+Vida | 150-300 pts | S3 Protector Familiar (36-52) |
| **Contigo Autónomo ILT** | ILT | 200-400 pts | S3A Autónomo |
| **Contigo Senior 55+** | Salud Senior | 200-350 pts | S5 Senior (55+) |
| **SIALP / Plan Creciente** | Goldman Sachs | 1.500-2.500 pts | S2/S3/S4 (ahorro) |
| **PPSA** | Plan Pensiones | Variable | S4 Planificador (50-64) |
| **MiHogar Seguro** | Hogar | 80-150 pts | S3 Protector + hogar |

**Referencia de PVM:** consultar siempre el Marco de Operaciones Anexo J5 para valores exactos. **No estimar PVM sin datos confirmados.**

---

## 👥 Buyer Personas (segmentación CRM)

| Código | Segmento | Edad | Prioridad |
|--------|----------|------|-----------|
| **S1** | Joven | 18-30 | Baja |
| **S2** | Constructor | 28-38 | Media |
| **S3** | Protector Familiar | 36-52 | Alta |
| **S3A** | Autónomo | 30-55 | Alta |
| **S4** | Planificador | 50-64 | Alta |
| **S5** | Senior | 55+ | Media-Alta |

---

## 📞 Contacto

**Federico Fontanals Serra**  
Delegado Punto Naranja NN · Xàtiva (La Costera)  
📧 federico.fontanals@nnespana.com | fefontanals@gmail.com  
📱 +34 680 507 186

**Coordinador:** Antonio Morote (Valencia)  
**Manager Territorial:** Ricardo Montaner (Levante)

---

## 📄 Licencia y uso

Herramientas de uso interno comercial para Nationale-Nederlanden.  
Desarrollo y mantenimiento: Federico Fontanals Serra.  
Última actualización: Mayo 2026.

---

*🟠 Punto Naranja NN Xàtiva · La persona que hace al profesional*
