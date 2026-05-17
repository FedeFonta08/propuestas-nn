/**
 * SISTEMA DE BITÁCORA LEO - GOOGLE APPS SCRIPT
 * VERSIÓN COCKPIT MILITAR CON MOTOR DE EMAILS PREMIUM & COMPACTO ESTOICO
 * 
 * Instrucciones de instalación:
 * 1. Abre tu Google Sheet de Bitácora.
 * 2. Ve a Extensiones -> Apps Script.
 * 3. Borra todo el código existente y pega este bloque completo.
 * 4. Guarda (💾).
 * 5. Haz clic en "Implementar" -> "Nueva implementación".
 * 6. Selecciona "Aplicación web".
 * 7. Configura:
 *    - Descripción: Bitácora HUD v2 Premium
 *    - Ejecutar como: Yo (tu correo fefontanals@gmail.com)
 *    - Quién tiene acceso: Cualquier usuario (Crucial para que tu HUD local envíe datos sin CORS).
 * 8. Copia la URL de la web app y pégala en script.js (USER_CONFIG.sheets_url).
 */

var DESTINATARIO_EMAIL = "fefontanals@gmail.com";

// Lista oficial de festivos de la Comunidad Valenciana 2026
var FESTIVOS_VALENCIA_2026 = [
  "2026-01-01", // Año Nuevo
  "2026-01-06", // Día de Reyes
  "2026-03-19", // Día de San José
  "2026-04-03", // Viernes Santo
  "2026-04-06", // Lunes de Pascua
  "2026-05-01", // Fiesta del Trabajo
  "2026-06-24", // Día de San Juan
  "2026-10-09", // Día de la Comunidad Valenciana
  "2026-10-12", // Fiesta Nacional de España
  "2026-12-08", // La Inmaculada Concepción
  "2026-12-25"  // Navidad
];

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(15000); // Bloqueo de concurrencia por seguridad
    
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Si la hoja está vacía, creamos cabeceras con estilo premium LEO
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Fecha",
        "Meta de la Mañana",
        "Foco Comercial 8-IA",
        "Pasos Previstos (Salud)",
        "Impactos Previstos (Comercial)",
        "Reflexión de la Noche",
        "Pasos Reales",
        "Impactos Reales",
        "Sacos de Abono (NOes)"
      ]);
      sheet.getRange(1, 1, 1, 9)
        .setBackground("#E85D26") // Naranja LEO NN corporativo
        .setFontColor("#FFFFFF")
        .setFontWeight("bold")
        .setHorizontalAlignment("center")
        .setFontFamily("Arial");
      sheet.setFrozenRows(1);
    }
    
    var date = data.date; // Formato yyyy-MM-dd
    var morningGoal = data.morningGoal || "";
    var phase8ia = data.phase8ia || "";
    var stepGoal = data.stepGoal || "";
    var impactsGoal = data.impactsGoal || "";
    
    var eveningReflection = data.eveningReflection || "";
    var stepsActual = data.stepsActual || "";
    var impactsActual = data.impactsActual || "";
    var abonosActual = data.abonosActual || "";
    
    // Buscar si ya existe una fila para hoy
    var rows = sheet.getDataRange().getValues();
    var rowIndex = -1;
    for (var i = 1; i < rows.length; i++) {
      var rowDate = rows[i][0];
      if (rowDate instanceof Date) {
        rowDate = Utilities.formatDate(rowDate, Session.getScriptTimeZone(), "yyyy-MM-dd");
      }
      if (rowDate === date) {
        rowIndex = i + 1;
        break;
      }
    }
    
    var rowData = [
      date,
      morningGoal,
      phase8ia,
      stepGoal,
      impactsGoal,
      eveningReflection,
      stepsActual,
      impactsActual,
      abonosActual
    ];
    
    var isMorningReport = false;
    var isEveningReport = false;
    
    if (rowIndex > -1) {
      // Fila existe. Detectamos si es actualización matutina o nocturna
      // Si recibimos reflexión de la noche y antes no había, es el balance de la noche
      var oldReflection = rows[rowIndex - 1][5];
      if (eveningReflection !== "" && (oldReflection === "" || oldReflection === undefined)) {
        isEveningReport = true;
      }
      
      // Actualizar solo las celdas que traen datos
      for (var col = 1; col <= rowData.length; col++) {
        var newVal = rowData[col - 1];
        if (newVal !== "" && newVal !== undefined && newVal !== null) {
          sheet.getRange(rowIndex, col).setValue(newVal);
        }
      }
    } else {
      // Fila nueva. Es un despegue de la mañana
      sheet.appendRow(rowData);
      isMorningReport = true;
    }
    
    sheet.autoResizeColumns(1, 9);
    
    // -------------------------------------------------------------
    // MOTOR DE CORREOS PREMIUM LEO HUD
    // -------------------------------------------------------------
    
    // Determinar si hoy es fin de semana o festivo en Valencia
    var dt = new Date(date + "T00:00:00");
    var dayOfWeek = dt.getDay(); // 0 = Domingo, 6 = Sábado
    var esFestivo = FESTIVOS_VALENCIA_2026.indexOf(date) > -1;
    var esFinDeSemanaOFiesta = (dayOfWeek === 0 || dayOfWeek === 6 || esFestivo);
    var horaCaminar = esFinDeSemanaOFiesta ? "07:00 AM" : "06:00 AM";
    var tipoDiaStr = esFestivo ? "DÍA FESTIVO (Comunitat Valenciana) 🏖️" : (esFinDeSemanaOFiesta ? "FIN DE SEMANA 🔋" : "DÍA LABORABLE 🚶‍♂️");
    
    if (isMorningReport) {
      enviarEmailDespegue(date, morningGoal, phase8ia, stepGoal, impactsGoal, horaCaminar, tipoDiaStr);
    } else if (isEveningReport) {
      enviarEmailAterrizaje(date, eveningReflection, stepsActual, stepGoal || rows[rowIndex - 1][3], impactsActual, impactsGoal || rows[rowIndex - 1][4], abonosActual);
    }
    
    return ContentService.createTextOutput(JSON.stringify({ status: "success", message: "Sincronizado en la nube con Google Sheets y correo enviado." }))
      .setMimeType(ContentService.MimeType.JSON)
      .setHeaders({ 'Access-Control-Allow-Origin': '*' });
      
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON)
      .setHeaders({ 'Access-Control-Allow-Origin': '*' });
  } finally {
    lock.releaseLock();
  }
}

// -------------------------------------------------------------
// PLANTILLA 1: REPORT MATUTINO (DESPEGUE)
// -------------------------------------------------------------
function enviarEmailDespegue(fecha, meta, foco8ia, pasos, impactos, horaCaminar, tipoDia) {
  var asunto = "🚀 [DESPEGUE] Piloto LEO en Cabina - Foco: " + (foco8ia || "General");
  
  var html = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <title>Despegue Táctico</title>
  </head>
  <body style="margin:0; padding:0; background-color:#0b0b0d; font-family:'Helvetica Neue', Arial, sans-serif; color:#ffffff;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0b0b0d; padding:30px 0;">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%; background-color:#121216; border:2px solid #E85D26; border-radius:12px; overflow:hidden; box-shadow:0 10px 30px rgba(232,93,38,0.15);">
            
            <!-- HEADER TÁCTICO -->
            <tr>
              <td style="background: linear-gradient(135deg, #E85D26 0%, #B33600 100%); padding:30px; text-align:center;">
                <p style="margin:0; font-size:11px; letter-spacing:4px; text-transform:uppercase; color:rgba(255,255,255,0.8); font-weight:bold;">SISTEMA LEO HUD · CABINA DE MANDO</p>
                <h1 style="margin:10px 0 0 0; font-size:28px; font-weight:800; letter-spacing:1px; color:#ffffff;">DESPEGUE CONFIRMADO</h1>
                <p style="margin:5px 0 0 0; font-size:13px; color:#FFD700; font-weight:bold;">PILOTO: Federico Fontanals (Sol y Ascendente LEO 🦁)</p>
              </td>
            </tr>
            
            <!-- CONTENIDO BRIEFING -->
            <tr>
              <td style="padding:35px 30px;">
                
                <!-- ALERTA DE CAMINATA ESTOICA -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#1c1917; border-left:4px solid #FFD700; border-radius:4px; margin-bottom:25px;">
                  <tr>
                    <td style="padding:15px;">
                      <p style="margin:0 0 5px 0; font-size:11px; color:#FFD700; font-weight:bold; letter-spacing:1px; text-transform:uppercase;">⌚ HORARIO DE CAMINATA Y PLANIFICACIÓN</p>
                      <p style="margin:0; font-size:15px; font-weight:bold; color:#ffffff;">Hoy es <span style="color:#FFD700;">${tipoDia}</span></p>
                      <p style="margin:4px 0 0 0; font-size:14px; color:#a8a29e;">Tu despertador para salir a caminar se ha fijado a las: <strong style="color:#ffffff; font-size:15px;">${horaCaminar}</strong> 🚶‍♂️</p>
                    </td>
                  </tr>
                </table>
                
                <!-- PRIORIDAD FEDE JR -->
                <p style="margin:0 0 25px 0; font-size:14px; text-align:center; color:#e7e5e4; font-style:italic; background:#1c1917; padding:12px; border-radius:6px; border:1.5px dashed rgba(255,215,0,0.2);">
                  🛡️ <strong>Blindaje Absoluto:</strong> Tu día y tu energía pertenecen al 100% a <strong style="color:#FFD700;">FEDE JR. 💎</strong> y a tu Salud. Ninguna provocación externa entra hoy en tu zona de paz.
                </p>

                <!-- FOCO COMERCIAL -->
                <div style="margin-bottom:25px;">
                  <span style="font-size:11px; font-weight:bold; color:#E85D26; letter-spacing:1px; text-transform:uppercase;">🎯 FOCO COMERCIAL 8-IA DE HOY</span>
                  <div style="background-color:#18181f; border:1px solid #292524; padding:16px; border-radius:8px; margin-top:6px; font-size:18px; font-weight:bold; color:#FFD700;">
                    ${foco8ia}
                  </div>
                </div>

                <!-- META PRINCIPAL -->
                <div style="margin-bottom:30px;">
                  <span style="font-size:11px; font-weight:bold; color:#E85D26; letter-spacing:1px; text-transform:uppercase;">🚀 META PRINCIPAL DEL DÍA (SIMPLIFICA)</span>
                  <div style="background-color:#18181f; border:1px solid #292524; padding:18px; border-radius:8px; margin-top:6px; font-size:15px; line-height:1.6; color:#ffffff;">
                    ${meta}
                  </div>
                </div>

                <!-- MÉTRICAS DE COMBATE -->
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td width="48%" style="background-color:#18181f; border:1px solid #292524; padding:15px; border-radius:8px; text-align:center;">
                      <span style="font-size:10px; color:#a8a29e; font-weight:bold; text-transform:uppercase;">🔥 PASOS PREVISTOS</span>
                      <p style="margin:5px 0 0 0; font-size:24px; font-weight:bold; color:#ffffff;">${pasos} <span style="font-size:14px; color:#E85D26;">Pasos</span></p>
                    </td>
                    <td width="4%"></td>
                    <td width="48%" style="background-color:#18181f; border:1px solid #292524; padding:15px; border-radius:8px; text-align:center;">
                      <span style="font-size:10px; color:#a8a29e; font-weight:bold; text-transform:uppercase;">📞 IMPACTOS PREVISTOS</span>
                      <p style="margin:5px 0 0 0; font-size:24px; font-weight:bold; color:#ffffff;">${impactos} <span style="font-size:14px; color:#FFD700;">Leads</span></p>
                    </td>
                  </tr>
                </table>
                
                <!-- FIRMA ESTOICA -->
                <p style="margin:30px 0 0 0; font-size:12px; color:#78716c; text-align:center; border-top:1px solid #292524; padding-top:20px;">
                  Misión registrada desde Cabina LEO HUD. Mañana será hoy. ¡Insiste, no te resignes!
                </p>
                
              </td>
            </tr>
            
          </table>
        </td>
      </tr>
    </table>
  </body>
  </html>
  `;
  
  MailApp.sendEmail({
    to: DESTINATARIO_EMAIL,
    subject: asunto,
    htmlBody: html
  });
}

// -------------------------------------------------------------
// PLANTILLA 2: REPORT NOCTURNO (ATERRIZAJE)
// -------------------------------------------------------------
function enviarEmailAterrizaje(fecha, reflexion, pasosReal, pasosGoal, impactosReal, impactosGoal, abonos) {
  var asunto = "🛬 [ATERRIZAJE] Misión Cerrada - Balance de Cabina LEO";
  
  var pasosPorcentaje = pasosGoal > 0 ? Math.round((pasosReal / pasosGoal) * 100) : 100;
  var impactosPorcentaje = impactosGoal > 0 ? Math.round((impactosReal / impactosGoal) * 100) : 100;
  
  var html = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <title>Aterrizaje Táctico</title>
  </head>
  <body style="margin:0; padding:0; background-color:#0b0b0d; font-family:'Helvetica Neue', Arial, sans-serif; color:#ffffff;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0b0b0d; padding:30px 0;">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%; background-color:#121216; border:2px solid #FFD700; border-radius:12px; overflow:hidden; box-shadow:0 10px 30px rgba(255,215,0,0.12);">
            
            <!-- HEADER TÁCTICO -->
            <tr>
              <td style="background: linear-gradient(135deg, #1c1917 0%, #0c0a09 100%); padding:30px; text-align:center; border-bottom:1px solid #292524;">
                <p style="margin:0; font-size:11px; letter-spacing:4px; text-transform:uppercase; color:#FFD700; font-weight:bold;">SISTEMA LEO HUD · BALANCES DE NOCHE</p>
                <h1 style="margin:10px 0 0 0; font-size:28px; font-weight:800; letter-spacing:1px; color:#ffffff;">MISIÓN DIARIA CERRADA</h1>
                <p style="margin:5px 0 0 0; font-size:13px; color:#E85D26; font-weight:bold;">Comandante Federico Fontanals · Escudo Lionheart Activo 🛡️</p>
              </td>
            </tr>
            
            <!-- CONTENIDO BRIEFING -->
            <tr>
              <td style="padding:35px 30px;">

                <!-- REFLEXIÓN DE LA NOCHE -->
                <div style="margin-bottom:30px;">
                  <span style="font-size:11px; font-weight:bold; color:#FFD700; letter-spacing:1px; text-transform:uppercase;">📝 REFLEXIÓN DIARIA DEL COMANDANTE</span>
                  <div style="background-color:#18181f; border-left:4px solid #FFD700; padding:18px; border-radius:0 8px 8px 0; margin-top:6px; font-size:15px; line-height:1.6; color:#ffffff; font-style:italic;">
                    "${reflexion}"
                  </div>
                </div>

                <!-- ESTADÍSTICAS DE COMBATE (RESULTADOS) -->
                <span style="font-size:11px; font-weight:bold; color:#E85D26; letter-spacing:1px; text-transform:uppercase;">📊 BALANCE DE MÉTRICAS FISICO-COMERCIALES</span>
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px; margin-bottom:30px;">
                  <tr>
                    <!-- PASOS -->
                    <td width="48%" style="background-color:#18181f; border:1px solid #292524; padding:20px; border-radius:8px; text-align:center;">
                      <span style="font-size:10px; color:#a8a29e; font-weight:bold; text-transform:uppercase;">🔥 PASOS DE SALUD</span>
                      <p style="margin:8px 0 8px 0; font-size:26px; font-weight:bold; color:#ffffff;">${pasosReal} <span style="font-size:12px; color:#a8a29e;">/ ${pasosGoal}</span></p>
                      <span style="font-size:12px; color:#22c55e; font-weight:bold; background:rgba(34,197,94,0.1); padding:4px 8px; border-radius:4px;">${pasosPorcentaje}% Objetivo</span>
                    </td>
                    <td width="4%"></td>
                    <!-- IMPACTOS -->
                    <td width="48%" style="background-color:#18181f; border:1px solid #292524; padding:20px; border-radius:8px; text-align:center;">
                      <span style="font-size:10px; color:#a8a29e; font-weight:bold; text-transform:uppercase;">📞 IMPACTOS COMERCIALES</span>
                      <p style="margin:8px 0 8px 0; font-size:26px; font-weight:bold; color:#ffffff;">${impactosReal} <span style="font-size:12px; color:#a8a29e;">/ ${impactosGoal}</span></p>
                      <span style="font-size:12px; color:#e85d26; font-weight:bold; background:rgba(232,93,38,0.1); padding:4px 8px; border-radius:4px;">${impactosPorcentaje}% Objetivo</span>
                    </td>
                  </tr>
                </table>

                <!-- SACOS DE ABONO -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#1c1917; border:1.5px solid #FFD700; border-radius:8px; margin-bottom:30px;">
                  <tr>
                    <td style="padding:20px; text-align:center;">
                      <span style="font-size:11px; color:#FFD700; font-weight:bold; letter-spacing:2px; text-transform:uppercase;">📦 COSECHA DE RECHAZOS (SACOS DE ABONO)</span>
                      <p style="margin:10px 0 5px 0; font-size:32px; font-weight:900; color:#ffffff;">${abonos} <span style="font-size:18px; color:#FFD700; font-weight:bold;">NOes</span></p>
                      <p style="margin:0; font-size:13px; color:#a8a29e; line-height:1.4;">Cada "NO" es abono de primera clase para la tierra comercial que vas a cosechar mañana. ¡Sigue nutriendo tu éxito!</p>
                    </td>
                  </tr>
                </table>

                <!-- AUTO-ANÁLISIS E IDEAS MATUTINAS -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0b0b0d; border:1px solid #292524; border-radius:6px; margin-bottom:20px;">
                  <tr>
                    <td style="padding:15px; font-size:13px; color:#a8a29e; line-height:1.5;">
                      💡 <strong>¿Grabaste tus ideas?</strong> Abre tu Bóveda LEO en Google Drive para subir tus notas de voz grabadas al volver a casa. Dejar tus pensamientos grabados te liberará la mente para descansar como un león.
                    </td>
                  </tr>
                </table>
                
                <!-- FIRMA ESTOICA -->
                <p style="margin:25px 0 0 0; font-size:12px; color:#78716c; text-align:center; border-top:1px solid #292524; padding-top:20px;">
                  Misión cerrada con éxito absoluto y total templanza. Mañana será hoy. ¡Insiste, no te resignes!
                </p>
                
              </td>
            </tr>
            
          </table>
        </td>
      </tr>
    </table>
  </body>
  </html>
  `;
  
  MailApp.sendEmail({
    to: DESTINATARIO_EMAIL,
    subject: asunto,
    htmlBody: html
  });
}
