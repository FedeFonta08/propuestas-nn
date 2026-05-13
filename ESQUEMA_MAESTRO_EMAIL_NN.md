# 🛡️ Esquema Maestro: Arquitectura de Email de Alta Autoridad (NN v18/10)

Este documento define la estructura técnica y estratégica para las comunicaciones de élite de Nationale-Nederlanden.

## 1. Especificaciones Técnicas Globales
- **Ancho Maestro:** 600px (fijo para evitar descuadres en móvil/escritorio).
- **Arquitectura:** Modular (Bloques de tabla independientes para cada sección).
- **Paleta de Colores:** 
  - Naranja NN: `#E85D26`
  - Chocolate Premium: `#1C1714` / `#2A2420`
  - Fondo Crema: `#F8F6F4`
  - Salmón Legal: `#FFE5D9`
- **Tipografía:** Georgia (Serif para autoridad) / Helvetica Neue (Sans-serif para claridad).

## 2. La Secuencia Lógica (El Funnel)

### Bloque A: Autoridad Institucional (Texto)
- **Objetivo:** Posicionamiento inmediato.
- **Formato:** Texto centrado, tipografía Serif grande, sin distracciones visuales.

### Bloque B: Identidad del Agente
- **Objetivo:** Humanizar la propuesta.
- **Recurso:** Banner horizontal de Federico Fontanals.

### Bloque C: El "Hook" (Banner de Producto)
- **Objetivo:** Deseo visual.
- **Recurso:** Imagen de alta resolución con la propuesta de valor comercial (ej. Salud + Vida gratis).

### Bloque D: Narrativa Consultiva
- **Objetivo:** Empatía y personalización.
- **Contenido:** Saludo directo + Análisis de situación + Línea de empatía destacada con borde naranja lateral.

### Bloque E: Acción y Lógica (CTA + FAQs)
- **Objetivo:** Conversión sin fricción.
- **Contenido:** Botón naranja con sombra y cajas de preguntas frecuentes compactas.

### Bloque F: Cierre de Solvencia (Tarjetas Premium)
- **Objetivo:** Eliminar el miedo al riesgo.
- **Formato:** 6 Micro-tarjetas de estadísticas (fondo chocolate) + 3 Tarjetas de testimonios. Diseño miniaturizado y sofisticado.

### Bloque G: El Footer "Perfecto" (Blindaje Legal)
- **Objetivo:** Profesionalidad y cumplimiento.
- **Contenido:** Bloque salmón con cláusula RGPD, botones de derechos ARCO y firma interactiva del agente.

---
**Nota para futuras campañas:** Cualquier nuevo bloque debe encapsularse en una `<table width="600">` independiente para mantener la integridad del alineado "cuadrado".
