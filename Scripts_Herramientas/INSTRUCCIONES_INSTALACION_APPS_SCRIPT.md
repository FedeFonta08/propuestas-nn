# 📘 INSTALACIÓN APPS SCRIPT — PANEL CRM NN v3

**Objetivo:** Conectar el Panel CRM v2 con tu Google Sheet en 10 pasos

**Tiempo estimado:** 10-15 minutos

---

## 🎯 PASO 1: ABRIR TU GOOGLE SHEET

1. Ve a: https://docs.google.com/spreadsheets/d/1d8rC3bxlquGSGgYb0j9Ap7J04H3sc_Lz/edit
2. Asegúrate de estar logueado con **fede.fonta.cuba@gmail.com**

---

## 🎯 PASO 2: ABRIR EL EDITOR DE APPS SCRIPT

1. En el Sheet, ve al menú: **Extensiones** → **Apps Script**
2. Se abrirá una nueva pestaña con el editor

---

## 🎯 PASO 3: LIMPIAR CÓDIGO ANTIGUO (SI EXISTE)

1. Si hay código antiguo en el editor, **selecciónalo todo** (Ctrl+A)
2. **Bórralo** (Delete)

---

## 🎯 PASO 4: PEGAR EL CÓDIGO NUEVO

1. Abre el archivo `Apps_Script_Panel_CRM_NN_v3.js` que te acabo de dar
2. **Copia TODO el código** (Ctrl+A, Ctrl+C)
3. **Pega en el editor** de Apps Script (Ctrl+V)

---

## 🎯 PASO 5: GUARDAR EL PROYECTO

1. Haz clic en el **icono del disquete** (💾) o presiona **Ctrl+S**
2. Si te pide nombre del proyecto, ponle: **Panel CRM NN v3**

---

## 🎯 PASO 6: TESTEAR QUE FUNCIONA

1. En el editor, arriba a la izquierda, selecciona la función **testBuscar**
2. Haz clic en **Ejecutar** (▶️)
3. **IMPORTANTE:** La primera vez te pedirá permisos:
   - Haz clic en **Revisar permisos**
   - Selecciona tu cuenta **fede.fonta.cuba@gmail.com**
   - Haz clic en **Avanzado**
   - Haz clic en **Ir a Panel CRM NN v3 (no seguro)**
   - Haz clic en **Permitir**

4. Una vez dados los permisos, vuelve a hacer clic en **Ejecutar** (▶️)
5. Abajo debería aparecer: **"Ejecución completada"**
6. Ve a **Ver** → **Registros** para ver el resultado

**✅ Si ves un JSON con resultados de búsqueda, funciona correctamente**

---

## 🎯 PASO 7: PUBLICAR COMO WEB APP

1. En el editor, haz clic en **Implementar** (arriba a la derecha)
2. Selecciona **Nueva implementación**
3. En "Tipo", selecciona **Aplicación web**
4. Configura:
   - **Descripción:** Panel CRM NN v3 - Producción
   - **Ejecutar como:** Yo (fede.fonta.cuba@gmail.com)
   - **Quién tiene acceso:** Cualquier usuario
5. Haz clic en **Implementar**

---

## 🎯 PASO 8: COPIAR LA URL DE LA WEB APP

1. Aparecerá un diálogo con la URL de implementación
2. **COPIA LA URL COMPLETA** — algo como:
   ```
   https://script.google.com/macros/s/AKfycby.../exec
   ```
3. **GUÁRDALA** — la necesitaremos para el siguiente paso

---

## 🎯 PASO 9: ENVIÁRMELA A MÍ (CLAUDE)

**Pega aquí esa URL** y yo actualizaré automáticamente el Panel CRM v2 con la nueva conexión.

Formato:
```
La URL del Apps Script es: https://script.google.com/macros/s/XXXXX/exec
```

---

## 🎯 PASO 10: TESTEAR LA CONEXIÓN COMPLETA

Una vez que yo actualice el panel HTML, haremos estas pruebas:

1. Abrir `nn_crm_panel_v2.html` actualizado
2. Buscar "Alejandro Fontanals"
3. ✅ Debería aparecer en los resultados
4. Clicar sobre el contacto
5. ✅ Debería expandirse mostrando TODO el historial
6. Crear un contacto de prueba "Test Sprint"
7. Guardar
8. Recargar la página
9. Buscar "Test Sprint"
10. ✅ Debería aparecer (datos persistentes)

---

## ⚠️ PROBLEMAS COMUNES

### "Error: No se puede leer la propiedad..."
**Solución:** Verifica que el SHEET_ID en el código sea correcto:
```javascript
SHEET_ID: '1d8rC3bxlquGSGgYb0j9Ap7J04H3sc_Lz'
```

### "No tengo permisos"
**Solución:** Repite el PASO 6 para autorizar la app

### "La URL no funciona"
**Solución:** Asegúrate de que en PASO 7 pusiste "Quién tiene acceso: Cualquier usuario"

---

## 📞 SIGUIENTE PASO

Una vez tengas la URL del Apps Script, **pégala aquí en el chat** y yo:

1. Actualizo el `nn_crm_panel_v2.html` con la nueva URL
2. Te lo subo a GitHub
3. Hacemos las pruebas de conexión
4. Implementamos la función `expandirContacto()` en el frontend

**¡Vamos con todo, Fede!** 🟠
