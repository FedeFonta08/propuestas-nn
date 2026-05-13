<div align="center">

<img src="https://cdn.jsdelivr.net/gh/FedeFonta08/propuestas-nn/fede_profile_github.jpg" width="100" style="border-radius:50%" alt="Fede Fontanals"/>

# 🟠 ECOSISTEMA COMERCIAL — PUNTO NARANJA XÀTIVA

**Federico Fontanals** · Agente Dinamizador · Nationale-Nederlanden · La Costera, Valencia

[![GitHub Pages](https://img.shields.io/badge/LIVE-GitHub%20Pages-FF6600?style=for-the-badge&logo=github)](https://fedefonta08.github.io/propuestas-nn/)
[![Última actualización](https://img.shields.io/badge/Actualizado-Mayo%202026-orange?style=for-the-badge)](#)
[![RGPD](https://img.shields.io/badge/RGPD-Compliant-green?style=for-the-badge)](#-cumplimiento-rgpdlopdgdd)
[![Herramientas](https://img.shields.io/badge/Herramientas-8%20activas-blue?style=for-the-badge)](#-herramientas-del-ecosistema)

> *"No estoy aquí para venderte nada. Estoy aquí para descubrir si tienes algún agujero en tu protección que no has visto."*  
> — Metodología ADN · Mayéutica Financiera

</div>

---

## 🧠 ¿Qué es el Ecosistema Despegue?

El **Ecosistema Despegue** es una suite de herramientas de inteligencia comercial construida desde cero para maximizar la productividad diaria de un agente de Nationale-Nederlanden. Integra datos en tiempo real desde Google Sheets (CRM Maestro + Radar Comercial), automatización de scripts de venta, gestión de llamadas y propuestas personalizadas, todo desplegado como aplicación web accesible desde cualquier dispositivo.

**No es un CRM genérico. Es una herramienta construida para un solo objetivo: más citas, más conversiones, menos fricción.**

---

## 🛠️ Herramientas del Ecosistema

| # | Herramienta | Archivo | Estado | Propósito |
|---|-------------|---------|--------|-----------|
| 1 | 🎯 **Panel DESPEGUE** | [`index.html`](https://fedefonta08.github.io/propuestas-nn/) | 🟢 Live | Dashboard principal: PVM, sprint activo, Radar Comercial NN con pulsadores expandibles |
| 2 | 📡 **Sistema Aperturas Pro** | [`aperturas_desktop_v4.html`](https://fedefonta08.github.io/propuestas-nn/aperturas_desktop_v4.html) | 🟢 Live | Workflow de llamadas: 8 perfiles psicológicos, cronómetro, Radar integrado, estadísticas |
| 3 | 📞 **Cockpit de Llamadas** | [`cockpit_llamadas.html`](https://fedefonta08.github.io/propuestas-nn/cockpit_llamadas.html) | 🟢 Live | Cola de contactos por vencimiento, guion ADN dinámico, registro de resultados |
| 4 | 🎬 **Modo Enfoque Pro** | [`modo_enfoque_pro_v3_RGPD.html`](https://fedefonta08.github.io/propuestas-nn/modo_enfoque_pro_v3_RGPD.html) | 🟢 Live | Call scripting consultivo + objeciones accordion + sincronización CRM |
| 5 | 📋 **Portal Propuestas v2** | [`propuestas-nn-v2.html`](https://fedefonta08.github.io/propuestas-nn/propuestas-nn-v2.html) | 🟢 Live | Propuestas personalizadas por URL (28 productos NN) · RGPD integrado |
| 6 | ⚙️ **Generador de URLs** | [`generador_urls_propuestas.html`](https://fedefonta08.github.io/propuestas-nn/generador_urls_propuestas.html) | 🟢 Live | Genera URLs de propuestas + template email listo para copiar |
| 7 | 👥 **CRM Panel v2** | [`nn_crm_panel_v2.html`](https://fedefonta08.github.io/propuestas-nn/nn_crm_panel_v2.html) | 🟢 Live | Gestión de 965 contactos ex-Santalucía, búsqueda, historial |
| 8 | 🤝 **Pipeline Reclutamiento** | [`Reclutamiento_NN_v2_RGPD.html`](https://fedefonta08.github.io/propuestas-nn/Reclutamiento_NN_v2_RGPD.html) | 🟢 Live | Gestión candidatos (objetivo: 4–5 agentes antes sept 2026) |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (HTML5 + JS)                 │
│  Panel Despegue · Aperturas Pro · Cockpit · Propuestas  │
└────────────────────────┬────────────────────────────────┘
                         │ gviz/tq (JSON) + OAuth2
                         ▼
┌─────────────────────────────────────────────────────────┐
│              GOOGLE SHEETS — FUENTE DE VERDAD           │
│  CRM Maestro (965 contactos) · Radar Comercial NN       │
│  ID: 16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0     │
└────────────────────────┬────────────────────────────────┘
                         │ Apps Script Backend
                         ▼
┌─────────────────────────────────────────────────────────┐
│              GOOGLE CALENDAR + GMAIL                    │
│        Citas · Eventos · Briefing Lunes ADN             │
└─────────────────────────────────────────────────────────┘
                         │ Git push
                         ▼
┌─────────────────────────────────────────────────────────┐
│              GITHUB PAGES (DESPLIEGUE)                  │
│     fedefonta08.github.io/propuestas-nn/                │
└─────────────────────────────────────────────────────────┘
```

### Regla de Oro del Ecosistema

| Capa | Dónde vive | Qué contiene |
|------|-----------|--------------|
| **Datos** | Google Drive / Sheets | CRM Maestro, campañas, PVM, contactos |
| **Código** | GitHub (este repo) | UI, scripts, propuestas, workflows |
| **Protocolo de cambio** | `git add → commit → push` | **Sin push = sin despliegue** |

---

## 📡 Radar Comercial NN — Campañas Activas (Mayo 2026)

> El Radar se carga dinámicamente desde Google Sheets en tiempo real. Cada fila del Excel genera una **ficha pulsador expandible** con la acción comercial ADN asociada.

| Producto | Campaña | Beneficio | Estado |
|----------|---------|-----------|--------|
| Salud Completo / Copago | Descuento autonomía comercial | **4% dto** primera anualidad (hasta 260 asegurados) | 🟢 ACTIVA |
| Salud Completo / Copago | Descuento Anual | **12,5% dto** primera anualidad, acumulable | 🟢 ACTIVA |
| PC SIALP | Ampliación edad | Contratación hasta **75 años**, vencimiento 85 | 🟢 ACTIVA |
| PC SIALP + Contigo Futuro | Indexación automática 5% | Argumento anti-inflación en primas regulares | 🟢 ACTIVA |
| AGE / Plan Creciente | Mejora tipos | **+40pb** → 2,40% AGE / 2,60% AGE VIP | 🟢 ACTIVA |
| Contigo Senior | Bonificación prima | **6 meses gratis** primer año — hasta 29/05/2026 | 🟢 ACTIVA |
| Contigo Familia | Descuento vitalicio | **25% de por vida** para profesionales de colectivos | 🟢 ACTIVA |
| Hipotecas ABANCA | Actualización precios | Solo recomendar Mari Carmen Fija Valor | 🔵 INFORMATIVA |
| Hipoteca ABANCA | Incentivo agente | **250 € / 500 €** por hipoteca formalizada | 🟡 BAJA PRIORIDAD |

---

## 📊 Base de Datos CRM Maestro

- **965 contactos** ex-Santalucía (prospectos fríos NN — NO son clientes activos)
- **51 columnas × 8 pestañas** | Actualización semanal (viernes)
- **ID del Sheet:** `16lui0o9wPYe9tL-9PaU6_H2heG8uIBYrCIL9vvfpdC0`

### Segmentación Buyer Persona

| Segmento | Edad | Perfil | Productos Clave |
|----------|------|--------|-----------------|
| **S1 Joven** | 18–30 | Independencia, primer hogar | SIALP, Plan Salud+Vida, Hipoteca ING <36 |
| **S2 Constructor** | 28–38 | Hipoteca, familia en formación | MiHogar, Hipotecas, Vida Familia |
| **S3 Protector** | 36–52 | Hijos, cargas familiares | Contigo Familia, PPSA, Salud |
| **S3A Autónomo** | 36–52 | Negocio propio, ILT crítica | Contigo Autónomo, ILT, PPSA |
| **S4 Planificador** | 50–64 | Jubilación próxima | PPSA, Plan Creciente, AGE, Flexicuenta |
| **S5 Senior** | 55+ | Protección y legado | Contigo Senior 55+, Previsión Familiar |

---

## 🎯 Metodología ADN — El Motor de Todo

El sistema no es solo una herramienta. Es la extensión digital de la **Metodología ADN de Venta Consultiva** (Mayéutica Financiera):

```
1. APERTURA     → Permiso para diagnosticar, no para vender
2. DESCUBRIMIENTO → Sus números, no los tuyos
3. CONCIENCIA   → Activar el dolor del "¿qué pasa si...?"
4. RECAPITULACIÓN → "Tú has dicho que..." — imbatible
5. CIERRE NATURAL → La solución emerge sola
```

Cada herramienta del ecosistema tiene los guiones, objeciones y árboles de decisión integrados. El agente solo necesita enfocarse en escuchar.

---

## 📋 Catálogo de Productos NN (28 total)

<details>
<summary><b>Fase 1 — Ahorro e Inversión (6 productos)</b></summary>

1. **Plan SIALP** — exención fiscal total año 5 · [Guía](https://fedefonta08.github.io/propuestas-nn/guias-comerciales/Gu%C3%ADa%20Maestra%20Profesional%20SIALP%20-%20Punto%20Naranja%20X%C3%A0tiva.pdf)
2. **Plan Garantizado** — 90/100/110% capital según plazo
3. **Flexicuenta** — ahorro remunerado sin penalización
4. **Plan Ahorro Garantizado** — rentabilidad fija en contrato
5. **Contigo Futuro** — garantía diaria 80% máximo histórico
6. **Sistema Duplo** — plan pensiones individual
</details>

<details>
<summary><b>Fase 2 — Salud, Vida y Accidentes (6 productos)</b></summary>

1. **Plan Salud + Vida** — híbrido Sanitas + Vida, 1er año gratis
2. **Seguro Salud Completo** — medicina privada Sanitas, 12,5% dto
3. **Salud Copago** — Sanitas con copago reducido, 4% dto autonomía
4. **Seguro Vida y Familia** — protección cáncer mama incluido
5. **Contigo Senior 55+** — asistencia + capital + servicios autonomía · **6 meses bonificados**
6. **Accidentes LiderPlus** — 90K € u 50K€ desde 74,77 €/año
</details>

<details>
<summary><b>Fases 3–6 — Hogar, Automóvil, Pensiones, Empresa, Hipotecas (15 productos)</b></summary>

- **Hogar:** MiHogar Seguro · Seguro Coche y Moto
- **Pensiones:** PPSA (deducción 5.750 €/año) · Duplo
- **Empresa:** Contigo Autónomo · ILT · Contigo Pyme · Seguro Comercios · Salud Copago Autónomos
- **Hipotecas:** ABANCA (sin comisión apertura) · ING Naranja (100% digital, ING asume todos los gastos)
</details>

---

## ⚡ Últimas Actualizaciones (Mayo 2026)

### 🆕 Radar Comercial — Rediseño total (10 mayo 2026)
- **Nuevo sistema de pulsadores expandibles** en `aperturas_desktop_v4.html` e `index.html`
- Cada campaña se muestra como ficha compacta que se abre con animación suave
- Corrección crítica: cada oferta (ej. 4% y 12.5% de Salud) aparece en ficha **individual**, sin agrupaciones que oculten información
- Consulta optimizada con `headers=0&range=A3:J100` para recuperar el 100% de los datos del sheet

### 🔧 Correcciones de Integración
- Fix del ID del contenedor `radar-body` en Aperturas Pro (era `radar-body-content` → desconectado del JS)
- Desactivada la agrupación automática de duplicados que suprimía ofertas distintas del mismo producto
- Sincronización completa con CRM Maestro en Cockpit de Llamadas

### 📄 Guión Operacional
- Creado y versionado `Guion_Operacional_NN.md` con mapa completo del ecosistema
- Incluye Índice de Productos con sus fuentes de verdad (Drive vs GitHub)
- Protocolo de cierre de sesión: siempre `git add → commit → push`

---

## 🔐 Cumplimiento RGPD / LOPDGDD

Todas las herramientas cumplen con:

- ✅ **RGPD (UE) 2016/679** — Protección de datos personales
- ✅ **LOPDGDD 3/2018** — Adaptación española
- ✅ **LSSI 34/2002** — Comercio electrónico

**Responsables del tratamiento:** Nationale-Nederlanden Vida S.A.E. y Nationale-Nederlanden Generales S.A.E.  
📍 Avda. de Bruselas, 16 · Parque Empresarial Arroyo de la Vega · 28108 Alcobendas (Madrid)

| Contacto RGPD | Email |
|--------------|-------|
| Derechos ARCO-POL | seleccion.redcomercial@nnespana.com |
| DPO | dpo@nnespana.es |
| Reclamaciones | AEPD (www.aepd.es) |

---

## ⚙️ Configuración Técnica

### GitHub Pages
```
Repo:    github.com/FedeFonta08/propuestas-nn
Branch:  main
URL:     https://fedefonta08.github.io/propuestas-nn/
Deploy:  Automático tras cada push
```

### Google Apps Script Backend
```
Endpoint: https://script.google.com/macros/s/AKfycbxpYhW-S9OvA3w1NTR_Mu6GHffGTtHKE1ENKgoM98ySB8gyxt-j4BbaKF7Mk48grrcr_g/exec
Acciones: buscar_contacto · ficha_contacto · registrar_llamada · crear_evento_calendar
Zona:     Europe/Madrid
```

### Patrón CORS (GET)
```javascript
const url = SCRIPT_URL + '?payload=' + encodeURIComponent(JSON.stringify(data));
```

### GA4 Tracking
```
ID: G-5P41S83SWG
Eventos: clicks propuestas · registros CRM · llamadas · citas
```

---

## 🔧 Troubleshooting Rápido

| Problema | Solución |
|----------|---------|
| Radar no carga | Verificar que el sheet sea público (compartir → cualquiera con el enlace) |
| GitHub Pages sin cambios | Esperar 2-3 min tras push · Ctrl+Shift+Del para limpiar caché |
| CORS en Apps Script | Publicar como app web con ejecución como "Yo" |
| Foto no carga en propuesta | Usar URL jsDelivr: `cdn.jsdelivr.net/gh/FedeFonta08/propuestas-nn/fede_profile_github.jpg` |

---

## 📞 Contactos del Equipo

| Persona | Rol | Email | Teléfono |
|---------|-----|-------|----------|
| **Federico Fontanals** | Agente Dinamizador | federico.fontanals@nnespana.es | +34 680 507 186 |
| **Antonio Morote** | Coordinador Valencia | antonio.morote@nnespana.es | (reporte semanal) |
| **Ricardo Montaner** | Manager Territorial Levante | ricardo.montaner@nnespana.es | (soporte) |
| **NN DPO** | Protección de Datos | dpo@nnespana.es | +34 91 602 60 00 |

---

## 🚀 Roadmap

- [x] Radar Comercial dinámico con pulsadores expandibles
- [x] Cockpit de Llamadas sincronizado con CRM Maestro
- [x] Portal de Propuestas v2 con 28 productos y RGPD
- [x] Sistema de Aperturas Pro con 8 perfiles psicológicos
- [x] Pipeline de Reclutamiento (objetivo: 4-5 agentes sept 2026)
- [x] Guión Operacional e Índice de Productos versionado
- [ ] Botón DESPEGUE: ejecutar procesador Python desde el navegador
- [ ] Integración Samsung A56 + Google Contacts
- [ ] Activación Synology NAS
- [ ] Matriz de consentimiento RGPD por contacto
- [ ] Automatización emails con validación previa de consentimiento

---

<div align="center">

**Versión 3.0** · Mayo 2026  
Construido con ❤️ y mucho café en Xàtiva, Valencia

`#DespegueNN` · `#PuntoNaranja` · `#ADNMethod`

</div>
