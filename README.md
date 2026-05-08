# 🟠 Ecosistema Comercial NN — Punto Naranja Xàtiva

**Federico Fontanals** | Agente Dinamizador | La Costera, Valencia

---

## 📦 Herramientas del Ecosistema

| Herramienta | Archivo | URL Accesible | Propósito |
|---|---|---|---|
| **Panel DESPEGUE** | `index.html` | [Ver dashboard](https://fedefonta08.github.io/propuestas-nn/) | Dashboard principal: PVM, estado sprint, tareas pendientes |
| **Portal Propuestas** | `propuestas.html` | [Ver portal](https://fedefonta08.github.io/propuestas-nn/propuestas.html) | Propuestas personalizadas por URL (30 productos) |
| **CRM Panel v2** | `nn_crm_panel_v2.html` | [Ver CRM](https://fedefonta08.github.io/propuestas-nn/nn_crm_panel_v2.html) | Gestión de contactos, búsqueda, historial |
| **Sistema Llamadas** | `aperturas_desktop_v4.html` | [Ver sistema](https://fedefonta08.github.io/propuestas-nn/aperturas_desktop_v4.html) | Workflow de llamadas comerciales (8/día) |
| **Modo Enfoque Pro** | `modo_enfoque_pro_v3.html` | [Ver herramienta](https://fedefonta08.github.io/propuestas-nn/modo_enfoque_pro_v3.html) | Call scripting + CRM sync + registros |
| **Reclutamiento NN** | `Reclutamiento_NN_v2.html` | [Ver pipeline](https://fedefonta08.github.io/propuestas-nn/Reclutamiento_NN_v2.html) | Gestión pipeline candidatos (4-5 agentes) |

---

## 🏗️ Arquitectura del Sistema

```
Frontend (HTML5 + JS localStorage)
    ↓
Google Apps Script Backend
    ↓
Google Sheets (CRM Master 965 contactos + Radar Comercial)
    ↓
Google Calendar (eventos + citas fijadas)
```

**Apps Script Endpoint:**
```
https://script.google.com/macros/s/AKfycbxpYhW-S9OvA3w1NTR_Mu6GHffGTtHKE1ENKgoM98ySB8gyxt-j4BbaKF7Mk48grrcr_g/exec
```

**Patrón GET para CORS:**
```javascript
const url = SCRIPT_URL + '?payload=' + encodeURIComponent(JSON.stringify(data));
```

---

## 📊 Base de Datos

### CRM Master (`Sistema_Gestion_NN_v4_BuyerPersona.xlsx`)
- **965 contactos** ex-Santalucía (prospectos fríos NN)
- **51 columnas** × **8 pestañas**
- **Segmentación:** S1 Joven, S2 Constructor, S3 Protector, S3A Autónomo, S4 Planificador, S5 Senior
- **Drive ID:** `1d8rC3bxlquGSGgYb0j9Ap7J04H3sc_Lz`

### Radar Comercial NN (`Google Sheet`)
- **3 pestañas:** Campañas Activas | Novedades Producto | Historial Entre Nosotros
- **Sheet ID:** `1mYKiIdoglAxzFwJOE_0V8CyHwNUsKkh_oPtkUKg4GCQ`
- **Actualización:** Semanal (viernes)

---

## 🔐 Cumplimiento RGPD/LOPDGDD

Todos los archivos cumplen con:
- ✅ **RGPD (UE) 2016/679** — Protección de datos personales
- ✅ **LOPDGDD 3/2018** — Adaptación española
- ✅ **LSSI 34/2002** — Comercio electrónico

### Datos Oficiales NN

**Responsables del tratamiento:**
- Nationale-Nederlanden Vida, Compañía de Seguros y Reaseguros, S.A.E
- Nationale-Nederlanden Generales, Compañía de Seguros y Reaseguros, S.A.E

**Dirección:** Avenida de Bruselas, 16 · Parque empresarial Arroyo de la Vega · 28108 Alcobendas (Madrid)

**Contactos RGPD:**
- **Derechos ARCO-POL:** `seleccion.redcomercial@nnespana.com`
- **DPO:** `dpo@nnespana.es`
- **Reclamaciones:** [AEPD](https://www.aepd.es)

**Derecho de oposición:** Responde "BAJA" a cualquier email para excluirte de comunicaciones comerciales.

---

## 📋 Productos NN (30 total)

### Fase 1: Ahorro (7 productos)
`SIALP` · `Flexible` · `Garantizado` · `Flexicuenta` · `Ahorro Garantizado` · `Futuro` · `Protección Plus`

### Fase 2: Salud/Vida (6 productos)
`Plan Salud+Vida` · `Salud Completo` · `Salud Copago` · `Vida Familia` · `Contigo Senior 55+` · `Accidentes`

### Fase 3: Hogar/Auto (2 productos)
`MiHogar Seguro` · `Auto`

### Fase 4: Pensiones (2 productos)
`PPSA` · `Duplo`

### Fase 5: Profesional (5 productos)
`Contigo Autónomo` · `ILT` · `PYME` · `Comercios` · `Salud Autónomos`

### Fase 6: Hipotecas (2 productos)
`Hipoteca Abanca` · `Hipoteca ING`

---

## 🎯 Buyer Personas

| Segmento | Edad | Contexto | Productos Clave |
|---|---|---|---|
| **S1 Joven** | 18–30 | Independencia, primer hogar | SIALP, Plan Salud+Vida |
| **S2 Constructor** | 28–38 | Hipoteca, familia en formación | MiHogar, Hipotecas, Vida Familia |
| **S3 Protector Familiar** | 36–52 | Hijos, cargas familiares | Contigo Familia, PPSA, Previsión |
| **S3A Autónomo** | 36–52 | Negocio propio | Contigo Autónomo, ILT, Salud |
| **S4 Planificador** | 50–64 | Jubilación próxima | PPSA, Flexicuenta, Protección |
| **S5 Senior** | 55+ | Protección/legado | Contigo Senior, Previsión Familiar, Decesos (mapeado) |

---

## 🚀 Workflows Principales

### 1. Sistema de Llamadas (8/día)
```
Noche anterior: seleccionar contactos
    ↓
5 min antes: enviar WhatsApp pre-llamada
    ↓
Llamada (evitar "seguro" primer 30s)
    ↓
Registro inmediato en CRM
    ↓
Si cita fijada → evento Calendar
```

### 2. Propuesta Personalizada
```
Parámetros URL: ?producto=SIALP&nombre=Xevi&beneficiario=Aina&prima=300
    ↓
Portal genera propuesta 3-page
    ↓
Social Proof + deadline warning
    ↓
CTA a Federico (+34 680 507 186)
```

### 3. Reclutamiento (4–5 agentes antes sept)
```
Buscar candidatos en zona La Costera
    ↓
Cargar en pipeline Reclutamiento
    ↓
Proceso ADN personalizado
    ↓
Alta DGS + formación
    ↓
Cartera desde día 1
```

---

## ⚙️ Configuración Inicial

### GitHub Pages
1. ✅ Repo activado: `github.com/FedeFonta08/propuestas-nn`
2. ✅ Branch: `main`
3. ✅ URLs vivas en `https://fedefonta08.github.io/propuestas-nn/`

### Google Apps Script
1. Endpoint verificado (CORS compatible)
2. Acciones: `buscar_contacto`, `ficha_contacto`, `registrar_llamada`, `crear_evento_calendar`
3. Timezone: `Europe/Madrid`

### GA4 Tracking
**ID:** `G-5P41S83SWG` (habilitado en todos los dashboards)

---

## 🔧 Troubleshooting

### CORS no funciona
→ Verifica que Apps Script esté publicado como **aplicación web** con ejecución como "Yo"

### Búsqueda CRM lenta
→ Aumenta `pageSize` en Apps Script; considera índice en Sheets

### GitHub Pages no actualiza
→ Espera 2-3 min después de push; limpia caché del navegador (Ctrl+Shift+Del)

### WhatsApp pre-llamada no se abre
→ Valida formato: `https://wa.me/34680507186?text=...` (sin +)

---

## 📞 Contactos Clave

| Persona | Rol | Email | Teléfono |
|---|---|---|---|
| **Federico Fontanals** | Agente Dinamizador | `federico.fontanals@nnespana.es` | `+34 680 507 186` |
| **Antonio Morote** | Coordinador Valencia | `antonio.morote@nnespana.es` | (reporte semanal) |
| **Ricardo Montaner** | Manager Territorial Levante | `ricardo.montaner@nnespana.es` | (soporte) |
| **NN DPO** | Protección de Datos | `dpo@nnespana.es` | +34 91 602 60 00 |

---

## 📅 Próximos Pasos

- [ ] Matriz de consentimiento RGPD (por contacto)
- [ ] Automatización emails con validación previa
- [ ] Guía técnica Apps Script
- [ ] Integración Samsung A56 + Google Contacts
- [ ] Activación Synology NAS
- [ ] Guides: Salud Completo Copago, Hogar

---

**Última actualización:** 8 mayo 2026  
**Versión:** 2.1 (RGPD compliant, GitHub Pages activo, Radar Comercial integrado)

