# 🟠 Ecosistema Comercial NN — Punto Naranja Xàtiva

**Federico Fontanals** | Agente Dinamizador | La Costera, Valencia

---

## 📦 Herramientas del Ecosistema

| Herramienta | Archivo | URL Accesible | Propósito |
|-------------|---------|---------------|-----------|
| 🎯 **Panel DESPEGUE** | `index.html` | [Ver dashboard](https://fedefonta08.github.io/propuestas-nn/) | Dashboard principal: PVM, estado sprint, tareas pendientes, Radar Comercial NN |
| 📋 **Portal Propuestas v2** | `propuestas-nn-v2.html` | [Ver portal](https://fedefonta08.github.io/propuestas-nn/propuestas-nn-v2.html) | **NUEVO** · Propuestas personalizadas por URL (28 productos NN) · Rectificado con foto fija, precio €, email actualizado |
| ⚙️ **Generador URLs** | `generador_urls_propuestas.html` | [Ver generador](https://fedefonta08.github.io/propuestas-nn/generador_urls_propuestas.html) | **NUEVO** · Genera URLs de propuestas + template email listo para copiar |
| 👥 **CRM Panel v2** | `nn_crm_panel_v2.html` | [Ver CRM](https://fedefonta08.github.io/propuestas-nn/nn_crm_panel_v2.html) | Gestión de contactos, búsqueda, historial (965 contactos) |
| 📞 **Sistema Llamadas** | `aperturas_desktop_v4.html` | [Ver sistema](https://fedefonta08.github.io/propuestas-nn/aperturas_desktop_v4.html) | Workflow de llamadas comerciales (8/día, pre-WhatsApp, cronómetro, registro inmediato) |
| 🎬 **Modo Enfoque Pro** | `modo_enfoque_pro_v3_RGPD.html` | [Ver herramienta](https://fedefonta08.github.io/propuestas-nn/modo_enfoque_pro_v3_RGPD.html) | Call scripting + CRM sync + registros automáticos + objecciones accordion |
| 🤝 **Reclutamiento NN** | `Reclutamiento_NN_v2_RGPD.html` | [Ver pipeline](https://fedefonta08.github.io/propuestas-nn/Reclutamiento_NN_v2_RGPD.html) | **NUEVO** · Gestión pipeline candidatos (objetivo 4-5 agentes antes sept) |

---

## 🏗️ Arquitectura del Sistema

```
Frontend (HTML5 + JS localStorage + GA4)
    ↓
Google Apps Script Backend (CORS compatible)
    ↓
Google Sheets (CRM Master 965 contactos + Radar Comercial)
    ↓
Google Calendar (eventos + citas fijadas · timezone Europe/Madrid)
```

### Apps Script Endpoint

```
https://script.google.com/macros/s/AKfycbxpYhW-S9OvA3w1NTR_Mu6GHffGTtHKE1ENKgoM98ySB8gyxt-j4BbaKF7Mk48grrcr_g/exec
```

### Patrón GET para CORS

```javascript
const url = SCRIPT_URL + '?payload=' + encodeURIComponent(JSON.stringify(data));
```

### Acciones disponibles

- `buscar_contacto` — búsqueda en CRM
- `ficha_contacto` — detalle contacto
- `registrar_llamada` — registro de llamadas
- `crear_evento_calendar` — citas fijadas

---

## 📊 Base de Datos

### CRM Master (`Sistema_Gestion_NN_v4_BuyerPersona.xlsx`)

- **965 contactos** ex-Santalucía (prospectos fríos NN — **NO son clientes existentes**)
- **51 columnas × 8 pestañas**
- **Segmentación:** S1 Joven (18–30) | S2 Constructor (28–38) | S3 Protector (36–52) | S3A Autónomo (36–52) | S4 Planificador (50–64) | S5 Senior (55+)
- **Drive ID:** `1d8rC3bxlquGSGgYb0j9Ap7J04H3sc_Lz`

> **Nota:** Los productos de Santalucía (Decesos, Hogar, Vida) requieren mapeo a equivalentes NN (Contigo Senior 55+, MiHogar Seguro, Plan Salud+Vida, PPSA, etc.)

### Radar Comercial NN (Google Sheet)

- **ID:** `1mYKiIdoglAxzFwJOE_0V8CyHwNUsKkh_oPtkUKg4GCQ`
- **3 pestañas:** Campañas Activas | Novedades Producto | Historial Entre Nosotros
- **Actualización:** Semanal (viernes)
- **Integración:** Panel DESPEGUE sincroniza automáticamente con datos inline

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

📍 Avenida de Bruselas, 16 · Parque empresarial Arroyo de la Vega · 28108 Alcobendas (Madrid)

**Contactos RGPD:**
- **Derechos ARCO-POL:** seleccion.redcomercial@nnespana.com
- **DPO:** dpo@nnespana.es
- **Reclamaciones:** AEPD
- **Derecho de oposición:** Responde "BAJA" a cualquier email para excluirte de comunicaciones comerciales

### Herramientas de Cumplimiento

- ✅ **Facilita RGPD (AEPD)** — base documental oficial para consentimientos
- ✅ **Banner RGPD** integrado en todas las propuestas (derechos ARCO, DPO, reclamaciones)
- ✅ **Control de consentimiento** antes de automatizaciones masivas

---

## 📋 Productos NN (28 total · Clasificación por Fase)

### Fase 1: Ahorro e Inversión (7 productos)

1. **Plan SIALP** (exención fiscal año 5+) · [Guía completa](https://fedefonta08.github.io/propuestas-nn/guias-comerciales/Gu%C3%ADa%20Maestra%20Profesional%20SIALP%20-%20Punto%20Naranja%20X%C3%A0tiva.pdf)
2. **Plan Flexible** (unit linked internacional)
3. **Plan Garantizado** (90/100/110% según plazo)
4. **Flexicuenta** (ahorro remunerado sin penalización)
5. **Plan Ahorro Garantizado** (rentabilidad fija contrato)
6. **Contigo Futuro** (garantía diaria 80% máximo histórico)
7. **Sistema Duplo** (plan pensiones individual)

### Fase 2: Salud, Vida y Accidentes (6 productos)

1. **Plan Salud + Vida** (híbrido sanitas + vida, 1er año gratis)
2. **Seguro Salud Completo** (medicina privada Sanitas)
3. **Salud Copago** (Sanitas con copago reducido)
4. **Seguro Vida y Familia** (protección cáncer mama incluido)
5. **Contigo Senior 55+** (asistencia + capital + servicios autonomía, **6 meses bonificados mayo 2026**)
6. **Accidentes LiderPlus** (90K € u 50K € · desde 74,77 €/año)

### Fase 3: Hogar y Automóvil (2 productos)

1. **MiHogar Seguro** (multirriesgo, propuesta en 3 min)
2. **Seguro Coche y Moto** (alianza NN + Mutua Madrileña, valor a nuevo 2 años)

### Fase 4: Pensiones (2 productos)

1. **PPSA** (plan empleo autónomos, deducción 5.750 €/año, Goldman Sachs, +8,49% desde inicio)
2. **Duplo** (plan individual, disponibilidad anticipada año 10)

### Fase 5: Profesional y Empresa (5 productos)

1. **Contigo Autónomo** (ILT 30 €/día, capital 266K €, desde 39,94 €/mes)
2. **ILT** (baja laboral, 10–200 €/día configurable)
3. **Contigo Pyme** (colectivo empleados, sin examen médico mayoría)
4. **Seguro Comercios** (continente, contenido, RC, garantía continuidad)
5. **Salud Copago Autónomos** (Sanitas deducible IRPF)

### Fase 6: Hipotecas (2 productos)

1. **Hipoteca ABANCA** (sin comisión apertura)
2. **Hipoteca Naranja ING** (100% digital, ING asume notaría/registro/gestoría/IAJD, hasta 100% <36 años)

---

## 🎯 Buyer Personas

| Segmento | Edad | Contexto | Productos Clave |
|----------|------|----------|-----------------|
| **S1 Joven** | 18–30 | Independencia, primer hogar | SIALP, Plan Salud+Vida, Hipoteca ING <36 |
| **S2 Constructor** | 28–38 | Hipoteca, familia en formación | MiHogar Seguro, Hipotecas, Vida Familia, Contigo Futuro |
| **S3 Protector Familiar** | 36–52 | Hijos, cargas familiares | Contigo Familia, PPSA, Previsión Familiar |
| **S3A Autónomo** | 36–52 | Negocio propio | Contigo Autónomo, ILT, PPSA, Salud Autónomos |
| **S4 Planificador** | 50–64 | Jubilación próxima | PPSA, Duplo, Flexicuenta, Protección |
| **S5 Senior** | 55+ | Protección/legado | Contigo Senior 55+, Previsión Familiar |

---

## 🚀 Workflows Principales

### 1. Sistema de Llamadas (8/día, 2 bloques)

```
Noche anterior: seleccionar 8 contactos pre-seleccionados
    ↓
5 min antes: enviar WhatsApp pre-llamada (mejora tasa respuesta +40%)
    ↓
Llamada (evitar palabra "seguro" primer 30s, reduce hang-ups)
    ↓
Registro inmediato en CRM (resultado, próx. contacto, notas)
    ↓
Si cita fijada → evento automático en Calendar (Europe/Madrid)
```

### 2. Propuesta Personalizada

```
URL parámetros: ?producto=SIALP&nombre=Xevi&beneficiario=Aina&prima=300€/mes
    ↓
Portal propuestas-nn-v2.html genera propuesta 3-page
    ↓
Incluye: social proof + deadline warning + FAQ + RGPD banner
    ↓
CTA: Llamar a Federico (+34 680 507 186)
```

### 3. Generador de URLs (nuevo)

```
Interfaz: selecciona producto + nombre cliente + prima
    ↓
Genera URL lista para compartir
    ↓
Genera plantilla email lista para copiar
    ↓
Email incluye firma, descargo RGPD, derechos ARCO
```

### 4. Reclutamiento (objetivo 4–5 agentes antes sept 2026)

```
Buscar candidatos en zona La Costera + Levante
    ↓
Cargar en pipeline Reclutamiento_NN_v2_RGPD.html
    ↓
Proceso ADN personalizado (iPad exclusivo)
    ↓
Alta DGS + formación completa
    ↓
Cartera desde día 1 (base 965 contactos ex-Santalucía)
```

---

## ⚙️ Configuración Inicial

### GitHub Pages

- ✅ **Repo activado:** github.com/FedeFonta08/propuestas-nn
- ✅ **Branch:** main
- ✅ **URLs vivas en:** https://fedefonta08.github.io/propuestas-nn/
- ✅ **Deploy automático** desde push a main

### Google Apps Script

- ✅ **Endpoint verificado** (CORS compatible)
- ✅ **Acciones:** buscar_contacto, ficha_contacto, registrar_llamada, crear_evento_calendar
- ✅ **Timezone:** Europe/Madrid
- ✅ **Publicado como aplicación web** (ejecución como "Yo")

### GA4 Tracking

- **ID:** `G-5P41S83SWG` (habilitado en todos los dashboards)
- **Eventos rastreados:** clicks propuestas, registros CRM, llamadas completadas, citas fijadas

---

## 📱 Herramientas Rectificadas (8 mayo 2026)

### `propuestas-nn-v2.html`

- ✅ **Foto:** URL jsDelivr (sin CORS issues, carga garantizada)
- ✅ **Precio:** símbolo € y período (/mes, /año, etc.)
- ✅ **Email:** "Nationale-Nederlanden Vida y Generales" completo
- ✅ **WhatsApp:** removido del footer (solo email + teléfono)
- ✅ **28 productos NN** con datos reales
- ✅ **Secciones de social proof** + deadline warnings (SIALP, Contigo Senior)
- ✅ **FAQ** con objecciones resueltas (auto-comprobación de conocimiento)
- ✅ **Banner RGPD** integrado (derechos ARCO, DPO, oposición)

### `generador_urls_propuestas.html` (NUEVO)

- ✅ **Radio buttons** para 20 productos principales
- ✅ **Campos:** nombre cliente + prima
- ✅ **Genera URL live** + qr code
- ✅ **Plantilla email** con firma completa + disclaimer RGPD
- ✅ **Copia a portapapeles**
- ✅ **Diseño mobile-first** (Bebas Neue + DM Sans + naranja NN)

### `index.html` (Panel DESPEGUE actualizado)

- ✅ **7 herramientas activas** (añadidas Reclutamiento + Generador URLs)
- ✅ **Radar Comercial NN** con datos inline (7 campañas activas)
- ✅ **Enlace SIALP corregido** (apunta al PDF correcto con codificación URL)
- ✅ **Badges de estado** (🟢 ACTIVA, 🔵 INFORMATIVA, 🟡 BAJA PRIORIDAD)

---

## 🗑️ Eliminación Recomendada

### `propuestas.html` ❌

- **Estado:** DEPRECATED (obsoleto desde propuestas-nn-v2.html)
- **Razón:** Causa confusión · Links antiguos · Versión mejorada lista
- **Acción:** ELIMINAR DE GITHUB

**Cómo:**
```bash
git rm propuestas.html
git commit -m "chore: remove deprecated propuestas.html — replaced by propuestas-nn-v2.html"
git push origin main
```

---

## 🔧 Troubleshooting

### CORS no funciona
→ Verifica que Apps Script esté publicado como aplicación web con ejecución como "Yo"

### Búsqueda CRM lenta
→ Aumenta `pageSize` en Apps Script; considera índice en Sheets

### GitHub Pages no actualiza
→ Espera 2-3 min después de push; limpia caché del navegador (Ctrl+Shift+Del)

### WhatsApp pre-llamada no se abre
→ Valida formato: `https://wa.me/34680507186?text=...` (sin +)

### Propuesta no carga foto
→ Verifica URL jsDelivr: `https://cdn.jsdelivr.net/gh/FedeFonta08/propuestas-nn/fede_profile_github.jpg` (sin CORS issues)

---

## 📞 Contactos Clave

| Persona | Rol | Email | Teléfono |
|---------|-----|-------|----------|
| **Federico Fontanals** | Agente Dinamizador | federico.fontanals@nnespana.es | +34 680 507 186 |
| **Antonio Morote** | Coordinador Valencia | antonio.morote@nnespana.es | (reporte semanal) |
| **Ricardo Montaner** | Manager Territorial Levante | ricardo.montaner@nnespana.es | (soporte) |
| **NN DPO** | Protección de Datos | dpo@nnespana.es | +34 91 602 60 00 |

---

## 📅 Próximos Pasos

- [ ] Eliminar `propuestas.html` de GitHub
- [x] Subir `propuestas-nn-v2.html` (RECTIFICADO)
- [x] Subir `generador_urls_propuestas.html` (NUEVO)
- [x] Actualizar `index.html` (tarjeta "Portal Propuestas" apunta a propuestas-nn-v2.html)
- [x] Añadir herramientas Reclutamiento + Generador URLs al Panel DESPEGUE
- [x] Corregir enlace SIALP en Panel DESPEGUE
- [ ] Matriz de consentimiento RGPD (por contacto)
- [ ] Automatización emails con validación consentimiento previa
- [ ] Integración Samsung A56 + Google Contacts
- [ ] Activación Synology NAS
- [ ] Guías pendientes: Salud Completo Copago, Hogar
- [ ] Reclutamiento activo: objetivo 4-5 agentes antes sept

---

**Última actualización:** 8 mayo 2026  
**Versión:** 2.3 (RGPD compliant, GitHub Pages activo, propuestas-nn-v2 + generador URLs, 7 herramientas activas, Radar Comercial inline)
