// ============================================================
// SISTEMA DE EMAILS AUTOMATIZADOS - NATIONALE-NEDERLANDEN
// Agente Dinamizador Punto Naranja | Xàtiva y Comarca La Costera
// ============================================================
// INSTRUCCIONES DE USO:
// 1. Abre Google Sheets con tu base de datos
// 2. Ve a Extensiones > Apps Script y pega este código
// 3. Configura los datos en la sección CONFIGURACIÓN
// 4. Ejecuta la función "enviarEmails" (primera vez pedirá permisos)
// 5. Acepta los permisos de Gmail y Google Sheets
// ============================================================

// ============================================================
// CONFIGURACIÓN - EDITA ESTOS VALORES
// ============================================================
const CONFIG = {
  NOMBRE_AGENTE: "Tu Nombre y Apellidos",
  TELEFONO: "666 000 000",
  EMAIL_AGENTE: "tu@email.com",
  DIRECCION: "C/ Tu Dirección, Xàtiva",
  // Nombre exacto de la hoja de cálculo (pestaña)
  NOMBRE_HOJA: "Contactos",
  // Columnas (A=1, B=2, C=3...) — ajusta si tu hoja difiere
  COL_NOMBRE: 1,      // Columna A: Nombre
  COL_EMAIL: 2,       // Columna B: Email
  COL_GRUPO: 3,       // Columna C: Grupo de Edad
  COL_AUTONOMO: 4,    // Columna D: Autónomo (Sí/No)
  COL_ENVIADO: 5,     // Columna E: Estado envío (se marca automáticamente)
  FILA_INICIO: 2,     // Empieza en fila 2 (la 1 son cabeceras)
  // Pausa entre envíos en milisegundos (evita límites de Gmail)
  PAUSA_MS: 1500,
  // ¿Enviar de verdad? false = modo prueba (solo log, no envía)
  MODO_REAL: true
};

// ============================================================
// FUNCIÓN PRINCIPAL - Esta es la que ejecutas
// ============================================================
function enviarEmails() {
  const hoja = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName(CONFIG.NOMBRE_HOJA);
  
  if (!hoja) {
    SpreadsheetApp.getUi().alert(
      '❌ No encuentro la hoja "' + CONFIG.NOMBRE_HOJA + 
      '". Verifica el nombre en CONFIG.NOMBRE_HOJA'
    );
    return;
  }
  
  const datos = hoja.getDataRange().getValues();
  let enviados = 0;
  let errores = 0;
  let omitidos = 0;
  
  Logger.log("=== INICIO DE ENVÍO === " + new Date());
  
  for (let i = CONFIG.FILA_INICIO - 1; i < datos.length; i++) {
    const fila = datos[i];
    const nombre    = fila[CONFIG.COL_NOMBRE - 1]?.toString().trim();
    const email     = fila[CONFIG.COL_EMAIL - 1]?.toString().trim();
    const grupo     = fila[CONFIG.COL_GRUPO - 1]?.toString().trim();
    const autonomo  = fila[CONFIG.COL_AUTONOMO - 1]?.toString().trim().toUpperCase();
    const yaEnviado = fila[CONFIG.COL_ENVIADO - 1]?.toString().trim();
    
    // Omitir filas vacías o ya enviadas
    if (!email || !grupo) {
      Logger.log("Fila " + (i+1) + ": omitida (datos incompletos)");
      continue;
    }
    if (yaEnviado === "ENVIADO") {
      omitidos++;
      Logger.log("Fila " + (i+1) + ": ya enviada, omitiendo - " + email);
      continue;
    }
    
    // Validar formato de email básico
    if (!email.includes("@") || !email.includes(".")) {
      Logger.log("Fila " + (i+1) + ": email inválido - " + email);
      hoja.getRange(i+1, CONFIG.COL_ENVIADO).setValue("ERROR - email inválido");
      errores++;
      continue;
    }
    
    try {
      // Determinar si es autónomo
      const esAutonomo = (autonomo === "SÍ" || autonomo === "SI" || 
                          autonomo === "S" || autonomo === "YES" || 
                          autonomo === "1");
      
      // Obtener asunto y cuerpo HTML según el grupo
      const emailData = obtenerEmailPorGrupo(grupo, nombre, esAutonomo);
      
      if (!emailData) {
        Logger.log("Fila " + (i+1) + ": grupo no reconocido - '" + grupo + "'");
        hoja.getRange(i+1, CONFIG.COL_ENVIADO).setValue("ERROR - grupo desconocido");
        errores++;
        continue;
      }
      
      // Enviar o simular
      if (CONFIG.MODO_REAL) {
        GmailApp.sendEmail(email, emailData.asunto, "", {
          htmlBody: emailData.html,
          name: CONFIG.NOMBRE_AGENTE + " | Nationale-Nederlanden"
        });
        hoja.getRange(i+1, CONFIG.COL_ENVIADO).setValue("ENVIADO");
        Logger.log("✓ Enviado a: " + email + " [" + grupo + "]");
      } else {
        Logger.log("🔵 SIMULACIÓN - Se enviaría a: " + email + " [" + grupo + "] Asunto: " + emailData.asunto);
        hoja.getRange(i+1, CONFIG.COL_ENVIADO).setValue("SIMULADO");
      }
      
      enviados++;
      Utilities.sleep(CONFIG.PAUSA_MS); // Pausa entre envíos
      
    } catch (error) {
      Logger.log("✗ Error en fila " + (i+1) + " (" + email + "): " + error.toString());
      hoja.getRange(i+1, CONFIG.COL_ENVIADO).setValue("ERROR: " + error.message.substring(0, 50));
      errores++;
    }
  }
  
  const resumen = "=== RESUMEN ===\n" +
    "✓ Enviados: " + enviados + "\n" +
    "⏭ Omitidos (ya enviados): " + omitidos + "\n" +
    "✗ Errores: " + errores;
  
  Logger.log(resumen);
  SpreadsheetApp.getUi().alert(resumen);
}

// ============================================================
// ENRUTADOR: selecciona plantilla según grupo de edad
// ============================================================
function obtenerEmailPorGrupo(grupo, nombre, esAutonomo) {
  const g = grupo.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  
  if (g.includes("joven") || g.includes("<28") || g.includes("menor")) {
    return { asunto: "Novedad | Tu dinero puede crecer sin pagar impuestos — te cuento cómo", html: plantillaJoven(nombre) };
  }
  if (g.includes("constructor") || g.includes("28-35") || g.includes("28 35")) {
    return { asunto: "Novedad | Salud + vida para ti y tu familia — el primer año, gratis", html: plantillaConstructor(nombre, esAutonomo) };
  }
  if (g.includes("protector") || g.includes("36-50") || g.includes("36 50")) {
    return { asunto: "Novedad | La protección que tu familia necesita, al mejor precio", html: plantillaProtector(nombre, esAutonomo) };
  }
  if (g.includes("planificador") || g.includes("51-65") || g.includes("51 65")) {
    return { asunto: "Novedad | Diseñado para personas como tú: tranquilidad y respaldo real", html: plantillaPlanificador(nombre) };
  }
  if (g.includes("senior") || g.includes("+65") || g.includes("65")) {
    return { asunto: "Información | Un servicio creado para que sigas siendo independiente", html: plantillaSenior(nombre) };
  }
  
  return null; // Grupo no reconocido
}

// ============================================================
// BLOQUE LEGAL Y FIRMA (compartido por todas las plantillas)
// ============================================================
function bloqueBase(nombre, colorAcento, tituloProducto, logoEmoji) {
  const firma = `
    <table width="100%" cellpadding="0" cellspacing="0" style="border-top:2px solid ${colorAcento};margin-top:28px;padding-top:16px;">
      <tr>
        <td>
          <p style="margin:0 0 2px 0;font-size:15px;font-weight:700;color:#1a1a1a;">${CONFIG.NOMBRE_AGENTE}</p>
          <p style="margin:0 0 2px 0;font-size:13px;color:#555;">Agente Dinamizador · Punto Naranja Nationale-Nederlanden</p>
          <p style="margin:0 0 2px 0;font-size:13px;color:#555;">📍 Xàtiva y Comarca La Costera</p>
          <p style="margin:0 0 2px 0;font-size:13px;color:#555;">📞 ${CONFIG.TELEFONO} &nbsp;|&nbsp; ✉ <a href="mailto:${CONFIG.EMAIL_AGENTE}" style="color:${colorAcento};text-decoration:none;">${CONFIG.EMAIL_AGENTE}</a></p>
        </td>
        <td align="right" style="vertical-align:middle;">
          <span style="font-size:36px;opacity:0.15;">${logoEmoji}</span>
        </td>
      </tr>
    </table>
    <p style="margin:18px 0 6px 0;font-size:11px;color:#999;border-top:1px solid #eee;padding-top:12px;">
      Si no desea recibir más comunicaciones comerciales, responda a este correo con la palabra <strong>BAJA</strong> en el asunto.
    </p>
  `;
  
  const legal = `
    <table width="100%" cellpadding="12" cellspacing="0" style="background:#f7f7f7;border-radius:6px;margin-top:8px;">
      <tr><td style="font-size:10px;color:#888;line-height:1.5;">
        <strong>AVISO DE CONFIDENCIALIDAD Y PROTECCIÓN DE DATOS</strong><br><br>
        Este mensaje y sus archivos adjuntos van dirigidos exclusivamente a su destinatario, pudiendo contener información 
        confidencial sometida a secreto profesional. No está permitida su comunicación, reproducción o distribución sin la 
        autorización expresa del remitente. Si usted no es el destinatario final, por favor, elimínelo e infórmenos por esta vía.<br><br>
        <strong>Protección de Datos:</strong> De conformidad con el RGPD (UE) 2016/679 y la LOPDGDD 3/2018, le informamos 
        que sus datos personales son tratados por ${CONFIG.NOMBRE_AGENTE} con la finalidad de gestionar y mantener las 
        relaciones profesionales y/o comerciales. La base legal es el interés legítimo, la ejecución de un contrato o su 
        consentimiento. Sus datos no serán cedidos a terceros salvo obligación legal. Puede ejercer sus derechos de acceso, 
        rectificación, supresión, oposición, limitación y portabilidad dirigiéndose a 
        <a href="mailto:${CONFIG.EMAIL_AGENTE}" style="color:#888;">${CONFIG.EMAIL_AGENTE}</a>.
      </td></tr>
    </table>
  `;
  
  return { firma, legal };
}

// ============================================================
// WRAPPER HTML DE EMAIL (estructura exterior)
// ============================================================
function wrapEmail(contenido, colorAcento, nombre, firma, legal) {
  return `<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
        
        <!-- CABECERA -->
        <tr><td style="background:${colorAcento};padding:28px 32px;text-align:center;">
          <p style="margin:0 0 4px 0;font-size:11px;letter-spacing:3px;color:rgba(255,255,255,0.75);text-transform:uppercase;">Nationale-Nederlanden · Punto Naranja Xàtiva</p>
          <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;">Hola, ${nombre} 👋</p>
        </td></tr>
        
        <!-- CUERPO -->
        <tr><td style="padding:32px 36px;">
          ${contenido}
          ${firma}
          ${legal}
        </td></tr>
        
        <!-- PIE -->
        <tr><td style="background:#f7f7f7;padding:16px 32px;text-align:center;border-top:1px solid #eee;">
          <p style="margin:0;font-size:11px;color:#aaa;">© ${new Date().getFullYear()} Nationale-Nederlanden · Comunicación comercial autorizada</p>
        </td></tr>
        
      </table>
    </td></tr>
  </table>
</body></html>`;
}

// ============================================================
// PLANTILLA 1: JOVEN (<28) — SIALP
// ============================================================
function plantillaJoven(nombre) {
  const COLOR = "#4A2FC7";
  const { firma, legal } = bloqueBase(nombre, COLOR, "Plan SIALP", "📈");
  
  const contenido = `
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 16px 0;">
      Me presento: soy el nuevo Agente Dinamizador de Nationale-Nederlanden en Xàtiva y la Comarca La Costera. 
      Me pongo en contacto contigo porque tengo algo que me parece importante compartirte.
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#f3f0ff,#e8e0ff);border-radius:10px;padding:0;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:24px 28px;">
        <p style="margin:0 0 8px 0;font-size:11px;letter-spacing:2px;color:${COLOR};text-transform:uppercase;font-weight:700;">🚀 Producto destacado para ti</p>
        <p style="margin:0 0 10px 0;font-size:20px;font-weight:700;color:#1a1a1a;">Plan de Inversión SIALP</p>
        <p style="margin:0;font-size:14px;color:#555;line-height:1.6;">Seguro Individual de Ahorro a Largo Plazo con <strong>exención fiscal total de beneficios</strong> a partir del 5.º año. Máximo 5.000 € al año. Tu dinero crece sin tributar.</p>
      </td></tr>
    </table>
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 12px 0;">
      La gente que empieza a los 25 llega a los 35 con un capital real, sin haber pagado un euro de impuestos sobre lo ganado. 
      Es legal, es sencillo y está gestionado por una de las aseguradoras más sólidas de Europa.
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
      <tr>
        <td width="33%" style="padding:12px;text-align:center;background:#f3f0ff;border-radius:8px;margin-right:8px;">
          <p style="margin:0 0 4px 0;font-size:24px;font-weight:700;color:${COLOR};">0€</p>
          <p style="margin:0;font-size:11px;color:#888;">impuestos sobre beneficios</p>
        </td>
        <td width="4%"></td>
        <td width="33%" style="padding:12px;text-align:center;background:#f3f0ff;border-radius:8px;">
          <p style="margin:0 0 4px 0;font-size:24px;font-weight:700;color:${COLOR};">5.000€</p>
          <p style="margin:0;font-size:11px;color:#888;">aportación máx. anual</p>
        </td>
        <td width="4%"></td>
        <td width="33%" style="padding:12px;text-align:center;background:#f3f0ff;border-radius:8px;">
          <p style="margin:0 0 4px 0;font-size:24px;font-weight:700;color:${COLOR};">5 años</p>
          <p style="margin:0;font-size:11px;color:#888;">para exención total</p>
        </td>
      </tr>
    </table>
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 20px 0;">
      Estaré encantado de explicarte cómo funciona en una llamada de 15 minutos, sin compromiso. 
      ¿Te parece bien que lo hablemos?
    </p>
    
    <div style="text-align:center;margin:24px 0;">
      <a href="mailto:${CONFIG.EMAIL_AGENTE}?subject=Me interesa el Plan SIALP" 
         style="display:inline-block;background:${COLOR};color:#fff;padding:14px 36px;border-radius:50px;font-size:15px;font-weight:700;text-decoration:none;">
        Quiero saber más →
      </a>
    </div>
  `;
  
  return wrapEmail(contenido, COLOR, nombre, firma, legal);
}

// ============================================================
// PLANTILLA 2: CONSTRUCTOR (28-35) — Plan Salud Vida + PPSA condicional
// ============================================================
function plantillaConstructor(nombre, esAutonomo) {
  const COLOR = "#0A7EA4";
  const { firma, legal } = bloqueBase(nombre, COLOR, "Plan Salud + Vida", "🏗️");
  
  const ctaAutonomo = esAutonomo ? `
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff8e6;border:2px solid #F5A623;border-radius:10px;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:20px 24px;">
        <p style="margin:0 0 6px 0;font-size:13px;color:#B07D00;font-weight:700;text-transform:uppercase;letter-spacing:1px;">⚡ Información adicional para autónomos</p>
        <p style="margin:0 0 10px 0;font-size:16px;font-weight:700;color:#1a1a1a;">Dedúcete hasta 5.750 € en el IRPF este año</p>
        <p style="margin:0 0 14px 0;font-size:14px;color:#555;line-height:1.6;">
          Como autónomo tienes acceso al <strong>PPSA (Plan de Pensiones de Empleo Simplificado)</strong>, 
          con una deducción fiscal casi cuatro veces superior a la de los planes individuales. 
          Lo gestiona Goldman Sachs. Es una ventaja que muy pocos conocen.
        </p>
        <p style="margin:0;font-size:14px;color:#333;">
          👉 <strong>Responde a este email</strong> con el asunto <em>"PPSA Autónomo"</em> y te envío toda la información específica.
        </p>
      </td></tr>
    </table>
  ` : "";
  
  const contenido = `
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 16px 0;">
      Me presento: acabo de incorporarme como Agente Dinamizador de Nationale-Nederlanden en Xàtiva y la Comarca La Costera. 
      Quería escribirte personalmente porque creo que tengo algo que puede interesarte.
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#e8f5fb,#d0ecf7);border-radius:10px;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:24px 28px;">
        <p style="margin:0 0 8px 0;font-size:11px;letter-spacing:2px;color:${COLOR};text-transform:uppercase;font-weight:700;">⭐ Producto estrella</p>
        <p style="margin:0 0 10px 0;font-size:20px;font-weight:700;color:#1a1a1a;">Plan Salud + Vida</p>
        <p style="margin:0;font-size:14px;color:#555;line-height:1.6;">Cobertura sanitaria completa con Sanitas <strong>más seguro de vida incluido gratis el primer año</strong>. Dos protecciones por el precio de una. Diseñado para familias que quieren optimizar su presupuesto sin renunciar a nada.</p>
      </td></tr>
    </table>
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 12px 0;">
      Es el producto más solicitado en nuestra cartera porque el cálculo es muy sencillo: 
      al final del año has tenido salud y vida cubiertos, y has pagado solo por la salud.
    </p>
    
    ${ctaAutonomo}
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 20px 0;">
      ¿Tienes 15 minutos esta semana para que te lo explique sin ningún compromiso?
    </p>
    
    <div style="text-align:center;margin:24px 0;">
      <a href="mailto:${CONFIG.EMAIL_AGENTE}?subject=Me interesa el Plan Salud Vida" 
         style="display:inline-block;background:${COLOR};color:#fff;padding:14px 36px;border-radius:50px;font-size:15px;font-weight:700;text-decoration:none;">
        Cuéntame más →
      </a>
    </div>
  `;
  
  return wrapEmail(contenido, COLOR, nombre, firma, legal);
}

// ============================================================
// PLANTILLA 3: PROTECTOR (36-50) — Plan Salud Vida + PPSA condicional
// ============================================================
function plantillaProtector(nombre, esAutonomo) {
  const COLOR = "#1E7D4A";
  const { firma, legal } = bloqueBase(nombre, COLOR, "Plan Salud + Vida", "🛡️");
  
  const ctaAutonomo = esAutonomo ? `
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0faf4;border:2px solid #1E7D4A;border-radius:10px;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:20px 24px;">
        <p style="margin:0 0 6px 0;font-size:13px;color:#1E7D4A;font-weight:700;text-transform:uppercase;letter-spacing:1px;">⚡ Ventaja exclusiva para autónomos</p>
        <p style="margin:0 0 10px 0;font-size:16px;font-weight:700;color:#1a1a1a;">Reduce tu factura fiscal hasta 5.750 € al año</p>
        <p style="margin:0 0 14px 0;font-size:14px;color:#555;line-height:1.6;">
          El <strong>PPSA</strong> te permite deducirte casi cuatro veces más que un plan de pensiones normal, 
          con gestión profesional de Goldman Sachs. A tu edad, cada año que pasa sin aprovecharlo 
          es dinero que podrías haberte quedado.
        </p>
        <p style="margin:0;font-size:14px;color:#333;">
          👉 <strong>Responde a este email</strong> con el asunto <em>"PPSA Autónomo"</em> y te mando toda la información detallada.
        </p>
      </td></tr>
    </table>
  ` : "";
  
  const contenido = `
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 16px 0;">
      Me llamo ${CONFIG.NOMBRE_AGENTE} y soy el nuevo Agente Dinamizador de Nationale-Nederlanden en Xàtiva y la Comarca La Costera. 
      Me pongo en contacto contigo con una propuesta concreta.
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#e8f5ed,#d0eddb);border-radius:10px;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:24px 28px;">
        <p style="margin:0 0 8px 0;font-size:11px;letter-spacing:2px;color:${COLOR};text-transform:uppercase;font-weight:700;">🛡️ Protección completa para tu familia</p>
        <p style="margin:0 0 10px 0;font-size:20px;font-weight:700;color:#1a1a1a;">Plan Salud + Vida</p>
        <p style="margin:0;font-size:14px;color:#555;line-height:1.6;">Sanitas completo para ti y los tuyos, <strong>con seguro de vida regalado el primer año</strong>. Una solución integral para quienes saben que proteger a su familia es la inversión más importante.</p>
      </td></tr>
    </table>
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 12px 0;">
      En esta etapa de la vida tener la salud cubierta y dejar a los tuyos protegidos ya no es opcional. 
      Lo que sí es opcional es pagar más de lo necesario por ello.
    </p>
    
    ${ctaAutonomo}
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 20px 0;">
      Si tienes 15 minutos, te lo explico con números reales adaptados a tu situación. Sin rodeos, sin presión.
    </p>
    
    <div style="text-align:center;margin:24px 0;">
      <a href="mailto:${CONFIG.EMAIL_AGENTE}?subject=Me interesa el Plan Salud Vida" 
         style="display:inline-block;background:${COLOR};color:#fff;padding:14px 36px;border-radius:50px;font-size:15px;font-weight:700;text-decoration:none;">
        Quiero saber más →
      </a>
    </div>
  `;
  
  return wrapEmail(contenido, COLOR, nombre, firma, legal);
}

// ============================================================
// PLANTILLA 4: PLANIFICADOR (51-65) — Contigo Senior + consolidación
// ============================================================
function plantillaPlanificador(nombre) {
  const COLOR = "#8B3A9E";
  const { firma, legal } = bloqueBase(nombre, COLOR, "Contigo Senior", "🎯");
  
  const contenido = `
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 16px 0;">
      Mi nombre es ${CONFIG.NOMBRE_AGENTE} y acabo de empezar como Agente Dinamizador de Nationale-Nederlanden 
      en Xàtiva y la Comarca La Costera. Me pongo en contacto contigo porque lo que tengo para compartirte 
      es diferente a lo que probablemente hayas visto antes.
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#f7f0ff,#ede0ff);border-radius:10px;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:24px 28px;">
        <p style="margin:0 0 8px 0;font-size:11px;letter-spacing:2px;color:${COLOR};text-transform:uppercase;font-weight:700;">🎯 Diseñado para mayores de 55</p>
        <p style="margin:0 0 10px 0;font-size:20px;font-weight:700;color:#1a1a1a;">Contigo Senior</p>
        <p style="margin:0;font-size:14px;color:#555;line-height:1.6;">
          Protección integral que combina hasta <strong>65.000 € por accidente</strong>, asistencia sanitaria con Sanitas 
          (geriatría, podología) y servicios reales de autonomía: peluquería a domicilio, auxiliar de apoyo 
          y acompañamiento a citas médicas. Todo en un solo contrato.
        </p>
      </td></tr>
    </table>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
      <tr>
        <td style="padding:14px 16px;background:#f7f0ff;border-radius:8px;vertical-align:top;">
          <p style="margin:0 0 4px 0;font-size:15px;font-weight:700;color:${COLOR};">✔ Protección económica</p>
          <p style="margin:0;font-size:13px;color:#666;">Capital por accidente hasta 65.000 €</p>
        </td>
        <td width="12px"></td>
        <td style="padding:14px 16px;background:#f7f0ff;border-radius:8px;vertical-align:top;">
          <p style="margin:0 0 4px 0;font-size:15px;font-weight:700;color:${COLOR};">✔ Salud y bienestar</p>
          <p style="margin:0;font-size:13px;color:#666;">Sanitas, geriatría y podología incluidos</p>
        </td>
      </tr>
      <tr><td colspan="3" height="10px"></td></tr>
      <tr>
        <td colspan="3" style="padding:14px 16px;background:#f7f0ff;border-radius:8px;vertical-align:top;">
          <p style="margin:0 0 4px 0;font-size:15px;font-weight:700;color:${COLOR};">✔ Servicios de autonomía real</p>
          <p style="margin:0;font-size:13px;color:#666;">Auxiliar a domicilio, peluquería, acompañamiento médico — para seguir siendo independiente</p>
        </td>
      </tr>
    </table>
    
    <p style="font-size:15px;color:#333;line-height:1.7;margin:0 0 20px 0;">
      Esta etapa de la vida merece una planificación seria. Si quieres, lo revisamos juntos con calma 
      y te explico cómo se adapta exactamente a tu situación.
    </p>
    
    <div style="text-align:center;margin:24px 0;">
      <a href="mailto:${CONFIG.EMAIL_AGENTE}?subject=Me interesa Contigo Senior" 
         style="display:inline-block;background:${COLOR};color:#fff;padding:14px 36px;border-radius:50px;font-size:15px;font-weight:700;text-decoration:none;">
        Quiero conocer los detalles →
      </a>
    </div>
  `;
  
  return wrapEmail(contenido, COLOR, nombre, firma, legal);
}

// ============================================================
// PLANTILLA 5: SENIOR (+65) — Contigo Senior (foco en tranquilidad)
// ============================================================
function plantillaSenior(nombre) {
  const COLOR = "#C0392B";
  const { firma, legal } = bloqueBase(nombre, COLOR, "Contigo Senior", "❤️");
  
  const contenido = `
    <p style="font-size:16px;color:#333;line-height:1.8;margin:0 0 16px 0;">
      Mi nombre es ${CONFIG.NOMBRE_AGENTE}. Soy el nuevo responsable de Nationale-Nederlanden en Xàtiva y la comarca. 
      Me pongo en contacto contigo porque existe un servicio que merece que lo conozcas.
    </p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#fff5f5,#ffe8e8);border-radius:10px;margin:20px 0;overflow:hidden;">
      <tr><td style="padding:24px 28px;">
        <p style="margin:0 0 8px 0;font-size:11px;letter-spacing:2px;color:${COLOR};text-transform:uppercase;font-weight:700;">❤️ Para ti, con todo el respaldo</p>
        <p style="margin:0 0 10px 0;font-size:22px;font-weight:700;color:#1a1a1a;">Contigo Senior</p>
        <p style="margin:0;font-size:15px;color:#555;line-height:1.7;">
          Un servicio integral pensado para que puedas seguir viviendo en tu casa, a tu manera, 
          con todo el apoyo que necesitas cuando lo necesitas.
        </p>
      </td></tr>
    </table>
    
    <p style="font-size:16px;color:#333;line-height:1.8;margin:0 0 16px 0;">Lo que incluye:</p>
    
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px 0;">
      <tr><td style="padding:10px 0;border-bottom:1px solid #f0e0e0;font-size:15px;color:#333;">
        <span style="color:${COLOR};font-size:18px;margin-right:10px;">✔</span> <strong>Hasta 65.000 € de protección</strong> en caso de accidente
      </td></tr>
      <tr><td style="padding:10px 0;border-bottom:1px solid #f0e0e0;font-size:15px;color:#333;">
        <span style="color:${COLOR};font-size:18px;margin-right:10px;">✔</span> <strong>Asistencia sanitaria con Sanitas</strong>, geriatría y podología
      </td></tr>
      <tr><td style="padding:10px 0;border-bottom:1px solid #f0e0e0;font-size:15px;color:#333;">
        <span style="color:${COLOR};font-size:18px;margin-right:10px;">✔</span> <strong>Auxiliar a domicilio</strong> cuando lo necesites
      </td></tr>
      <tr><td style="padding:10px 0;border-bottom:1px solid #f0e0e0;font-size:15px;color:#333;">
        <span style="color:${COLOR};font-size:18px;margin-right:10px;">✔</span> <strong>Peluquería en casa</strong> incluida
      </td></tr>
      <tr><td style="padding:10px 0;font-size:15px;color:#333;">
        <span style="color:${COLOR};font-size:18px;margin-right:10px;">✔</span> <strong>Acompañamiento a citas médicas</strong> sin depender de nadie
      </td></tr>
    </table>
    
    <p style="font-size:16px;color:#333;line-height:1.8;margin:0 0 20px 0;">
      Estaré encantado de explicártelo con tranquilidad, por teléfono o en persona, 
      sin ningún tipo de compromiso. Solo para que tengas toda la información.
    </p>
    
    <div style="text-align:center;margin:24px 0;">
      <a href="mailto:${CONFIG.EMAIL_AGENTE}?subject=Me interesa Contigo Senior" 
         style="display:inline-block;background:${COLOR};color:#fff;padding:16px 40px;border-radius:50px;font-size:16px;font-weight:700;text-decoration:none;">
        Me gustaría saber más
      </a>
    </div>
    
    <p style="font-size:14px;color:#888;text-align:center;margin:8px 0 0 0;">
      También puede llamarme directamente al ${CONFIG.TELEFONO}
    </p>
  `;
  
  return wrapEmail(contenido, COLOR, nombre, firma, legal);
}

// ============================================================
// FUNCIÓN DE PRUEBA — envía UN email de prueba a tu propia cuenta
// ============================================================
function enviarEmailPrueba() {
  const emailPrueba = Session.getActiveUser().getEmail();
  
  // Prueba las 5 plantillas
  const pruebas = [
    { fn: plantillaJoven,        asunto: "[PRUEBA] Joven SIALP",         args: ["Laura"] },
    { fn: plantillaConstructor,  asunto: "[PRUEBA] Constructor sin autónomo", args: ["Carlos", false] },
    { fn: plantillaConstructor,  asunto: "[PRUEBA] Constructor CON autónomo", args: ["Paco", true] },
    { fn: plantillaProtector,    asunto: "[PRUEBA] Protector sin autónomo", args: ["Ana", false] },
    { fn: plantillaProtector,    asunto: "[PRUEBA] Protector CON autónomo", args: ["José", true] },
    { fn: plantillaPlanificador, asunto: "[PRUEBA] Planificador Senior",  args: ["María"] },
    { fn: plantillaSenior,       asunto: "[PRUEBA] Senior +65",           args: ["Antonio"] },
  ];
  
  pruebas.forEach(p => {
    GmailApp.sendEmail(emailPrueba, p.asunto, "", {
      htmlBody: p.fn(...p.args),
      name: "TEST - " + CONFIG.NOMBRE_AGENTE
    });
    Utilities.sleep(500);
  });
  
  SpreadsheetApp.getUi().alert(
    "✓ Emails de prueba enviados a: " + emailPrueba + "\n" +
    "Revisa tu bandeja de entrada (y spam)."
  );
}
