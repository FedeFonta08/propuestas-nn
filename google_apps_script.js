/**
 * 🚀 GOOGLE APPS SCRIPT: MASTER SYNC BRIDGE
 * Ecosistema Despegue 360 — Punto Naranja Xàtiva
 * 
 * Este script actúa como el servidor middleware en tu cuenta de Google Drive.
 * Recibe las interacciones del portal Cockpit-CRM 360 en caliente y realiza:
 *   1. Registro y actualización en Google Sheets (Base de Datos Centralizada).
 *   2. Agendamiento automático de citas y re-contactos en Google Calendar.
 *   3. Inserción y enriquecimiento de contactos en Google Contacts / People API
 *      (Sincronizado nativamente con tu teléfono Samsung para el Caller ID).
 * 
 * 🛠️ INSTRUCCIONES DE DESPLIEGUE:
 *   1. Abre Google Drive con tu cuenta de Google.
 *   2. Crea una Hoja de Cálculo nueva y llámala "SISTEMA_MAESTRO_DESPEGUE".
 *   3. Entra en Extensiones > Apps Script.
 *   4. Borra todo el código del editor y pega este archivo completo.
 *   5. En el menú izquierdo de Apps Script, entra en "Configuración del proyecto" (icono de engranaje)
 *      y activa la casilla: "Mostrar archivo appsscript.json en el editor".
 *   6. Regresa al editor, abre el archivo "appsscript.json" y añade los scopes de Contacts y Calendar
 *      (ver plantilla al final de este script).
 *   7. Pulsa "Desplegar" > "Nueva implementación". Selecciona tipo "Aplicación web".
 *   8. Configura:
 *      - Ejecutar como: "Yo" (tu cuenta de Google).
 *      - Quién tiene acceso: "Cualquiera".
 *   9. Copia la URL de la Web App generada y pégala en el botón de engranaje (Configuración) de tu Cockpit-CRM 360.
 */

// CONFIGURACIÓN DE IDENTIFICADORES DE HOJAS
const SHEET_CONTACTOS_NAME = "Contactos";
const SHEET_INTERACCIONES_NAME = "Interacciones";

/**
 * Módulo de escucha de peticiones GET (bypasseo CORS nativo local)
 */
function doGet(e) {
  try {
    const payload = JSON.parse(e.parameter.payload);
    e.postData = { contents: JSON.stringify(payload) };
    return doPost(e);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: "doGet error: " + error.toString() }))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Módulo de escucha de peticiones POST del Cockpit-CRM 360
 */
function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const action = payload.action;
    
    // Abrir o crear las hojas de cálculo del Sistema Maestro
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    verificarYCrearTablas(ss);
    
    let responseText = "Acción ejecutada correctamente";
    
    if (action === 'create_contact') {
      // 1. Alta de contacto en Google Sheet y Google Contacts
      registrarContactoEnSheet(ss, payload);
      upsertGoogleContact(payload);
      responseText = "Contacto guardado en Sheet y Google Contacts";
      
    } else if (action === 'get_agenda') {
      // 2. Consulta de agenda en tiempo real desde Cockpit
      const agenda = obtenerAgendaDelDia(ss, payload.fecha);
      return ContentService.createTextOutput(JSON.stringify({ status: "success", agenda: agenda }))
                           .setMimeType(ContentService.MimeType.JSON);
      
    } else if (action === 'log_call') {
      // 3. Registro de interacción y sincronización con Calendar/Contacts
      
      // Control preventivo de conflictos sólo para Entrevistas (Citas fijadas)
      if (payload.resultado === 'cita_fijada') {
        const conflicto = verificarConflictoAgenda(payload);
        if (conflicto) {
          return ContentService.createTextOutput(JSON.stringify({ status: "conflict", message: conflicto }))
                               .setMimeType(ContentService.MimeType.JSON);
        }
      }

      registrarInteraccionEnSheet(ss, payload);
      
      // Manejo de compromisos (Google Calendar & Contact Tags)
      if (payload.resultado === 'cita_fijada') {
        crearEventoGoogleCalendar(payload, "🤝 Cita Diagnóstico");
        tagGoogleContactStatus(payload, "Cita Fijada");
      } else if (payload.resultado === 'llamar_despues') {
        crearEventoGoogleCalendar(payload, "⏳ Volver a Llamar");
        tagGoogleContactStatus(payload, "Llamar Después");
      } else if (payload.resultado === 'presupuesto_enviado') {
        crearEventoGoogleCalendar(payload, "📋 Seg. Presupuesto");
        tagGoogleContactStatus(payload, "Presupuesto Enviado");
      } else if (payload.resultado === 'contactado') {
        tagGoogleContactStatus(payload, "Contactado");
      } else if (payload.resultado === 'no_contactado') {
        crearEventoGoogleCalendar(payload, "❌ NC Pendiente");
        tagGoogleContactStatus(payload, "No Contactado");
      }
      
      responseText = "Interacción y compromisos guardados en Google Cloud";
    }
    
    // Responder con CORS habilitado
    return ContentService.createTextOutput(JSON.stringify({ status: "success", message: responseText }))
                         .setMimeType(ContentService.MimeType.JSON);
                         
  } catch (error) {
    Logger.log("Error en doPost: " + error.toString());
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Configura la base de datos de Google Sheets si es un archivo nuevo
 */
function verificarYCrearTablas(ss) {
  let sheetContactos = ss.getSheetByName(SHEET_CONTACTOS_NAME);
  if (!sheetContactos) {
    sheetContactos = ss.insertSheet(SHEET_CONTACTOS_NAME);
    sheetContactos.appendRow(["ID Cliente", "Nombre", "Teléfono", "Localidad", "Perfil", "Producto Vto", "Mes Vto", "Notas Alta", "Fecha Registro"]);
    sheetContactos.getRange("A1:I1").setFontWeight("bold").setBackground("#FFEDE0").setFontColor("#C94D00");
  }
  
  let sheetInteracciones = ss.getSheetByName(SHEET_INTERACCIONES_NAME);
  if (!sheetInteracciones) {
    sheetInteracciones = ss.insertSheet(SHEET_INTERACCIONES_NAME);
    sheetInteracciones.appendRow(["Fecha", "Agente", "ID Cliente", "Nombre", "Resultado", "Producto", "Notas de Llamada", "Fecha Compromiso", "Hora Compromiso"]);
    sheetInteracciones.getRange("A1:I1").setFontWeight("bold").setBackground("#FFEDE0").setFontColor("#C94D00");
  }
}

/**
 * Guarda el prospecto en la base de datos Sheet
 */
function registrarContactoEnSheet(ss, data) {
  const sheet = ss.getSheetByName(SHEET_CONTACTOS_NAME);
  const fechaHoy = new Date().toLocaleDateString("es-ES");
  sheet.appendRow([
    data.clienteId,
    data.nombre,
    data.telefono,
    data.localidad,
    data.perfil,
    data.producto,
    data.vtoMes,
    data.notas,
    fechaHoy
  ]);
}

/**
 * Guarda el resultado de llamada en la base de datos Sheet
 */
function registrarInteraccionEnSheet(ss, data) {
  const sheet = ss.getSheetByName(SHEET_INTERACCIONES_NAME);
  const fechaHoy = new Date().toLocaleDateString("es-ES");
  sheet.appendRow([
    fechaHoy,
    data.agente,
    data.clienteId,
    data.nombre,
    data.resultado,
    data.producto,
    data.notas,
    data.fechaCompromiso || "-",
    data.horaCompromiso || "-"
  ]);
}

/**
 * Módulo de Google Contacts (People API)
 * Crea el contacto con el formato especial de identificador en el móvil
 */
function upsertGoogleContact(data) {
  try {
    // Formatear el primer nombre para incluir el producto principal: "Juan Pérez [NN SIALP]"
    const formattedName = `${data.nombre} [NN - ${data.producto}]`;
    
    // Crear el recurso de contacto para People API
    const contactResource = {
      names: [{
        givenName: formattedName
      }],
      phoneNumbers: [{
        value: data.telefono,
        type: 'mobile'
      }],
      organizations: [{
        name: 'Nationale-Nederlanden',
        department: 'Punto Naranja Xàtiva',
        title: `Prospecto - ${data.perfil}`,
        primary: true
      }],
      biographies: [{
        value: `Alta inicial en CRM: ${new Date().toLocaleDateString("es-ES")}\nLocalidad: ${data.localidad}\nNotas: ${data.notas}`
      }]
    };
    
    // Llamar a People API para insertar
    People.People.createContact(contactResource);
    Logger.log(`Contacto creado exitosamente en Google Contacts: ${formattedName}`);
    
  } catch (err) {
    Logger.log("Error al crear contacto en Google Contacts: " + err.toString());
  }
}

/**
 * Módulo de Google Contacts (Enriquecimiento en caliente)
 * Modifica la etiqueta o el nombre del contacto en tu agenda según el resultado
 */
function tagGoogleContactStatus(data, statusLabel) {
  try {
    // Buscamos el contacto por su número de teléfono
    const query = data.telefono.replace(/ /g, "");
    const searchResults = People.People.searchContacts({
      query: query,
      readMask: 'names,phoneNumbers,organizations,biographies'
    });
    
    if (searchResults.results && searchResults.results.length > 0) {
      const person = searchResults.results[0].person;
      const resourceName = person.resourceName;
      
      // Obtener el contacto completo para actualizarlo
      const contact = People.People.get(resourceName, {
        personFields: 'names,phoneNumbers,organizations,biographies,metadata'
      });
      
      // Formatear nombre enriquecido con el estado comercial
      const cleanName = data.nombre;
      let newFormattedName = `${cleanName} [NN - ${data.producto}]`;
      
      if (statusLabel === "Cita Fijada") {
        newFormattedName = `${cleanName} [NN Cita: ${data.fechaCompromiso.split('-').reverse().slice(0,2).join('/')}]`;
      } else if (statusLabel === "Llamar Después") {
        newFormattedName = `${cleanName} [NN Pendiente: ${data.fechaCompromiso.split('-').reverse().slice(0,2).join('/')}]`;
      } else if (statusLabel === "Presupuesto Enviado") {
        newFormattedName = `${cleanName} [NN Presup: ${data.fechaCompromiso.split('-').reverse().slice(0,2).join('/')}]`;
      }
      
      // Actualizar nombre
      contact.names = [{
        givenName: newFormattedName,
        etag: contact.names && contact.names[0] ? contact.names[0].etag : undefined
      }];
      
      // Actualizar cargo y biografía
      contact.organizations = [{
        name: 'Nationale-Nederlanden',
        department: 'Punto Naranja Xàtiva',
        title: `${statusLabel} - ${data.perfil}`,
        primary: true
      }];
      
      const prevBio = contact.biographies && contact.biographies[0] ? contact.biographies[0].value : "";
      contact.biographies = [{
        value: `${prevBio}\n\nActualizado (${statusLabel}): ${new Date().toLocaleDateString("es-ES")}\nNotas de llamada: ${data.notas}`
      }];
      
      // Enviar actualización
      People.People.updateContact(contact, resourceName, {
        updatePersonFields: 'names,organizations,biographies'
      });
      
      Logger.log(`Contacto actualizado exitosamente con etiqueta: ${newFormattedName}`);
    }
  } catch (err) {
    Logger.log("Error al etiquetar contacto en Google Contacts: " + err.toString());
  }
}

/**
 * Módulo de Google Calendar
 * Agenda citas de negocio y tareas de re-contacto en tu calendario de Drive
 */
function crearEventoGoogleCalendar(data, prefijoTitulo) {
  try {
    const calendar = CalendarApp.getDefaultCalendar();
    
    // Parsear fecha y hora: data.fechaCompromiso es "YYYY-MM-DD", data.horaCompromiso es "HH:MM"
    const partesFecha = data.fechaCompromiso.split("-"); // [YYYY, MM, DD]
    const partesHora = data.horaCompromiso.split(":"); // [HH, MM]
    
    const fechaInicio = new Date(
      parseInt(partesFecha[0]),
      parseInt(partesFecha[1]) - 1, // En JS los meses van de 0 a 11
      parseInt(partesFecha[2]),
      parseInt(partesHora[0]),
      parseInt(partesHora[1])
    );
    
    // Duración estimada del diagnóstico: 30 minutos
    const fechaFin = new Date(fechaInicio.getTime() + 30 * 60 * 1000);
    
    let tituloEvento = `${prefijoTitulo}: ${data.nombre} (${data.telefono})`;
    
    // Si tenemos edad y motivo de llamada inicial, enriquecer el título
    if (data.edad || data.motivo) {
      const edadLabel = data.edad && data.edad !== 'Preguntar' ? ` (${data.edad})` : '';
      const motivoLabel = data.motivo ? ` - ${data.motivo}` : '';
      tituloEvento = `${prefijoTitulo}: ${data.nombre}${edadLabel}${motivoLabel} (${data.telefono})`;
    }
    
    const descripcionEvento = `
🚀 COCKPIT-CRM 360 - PUNTO NARANJA XÀTIVA
───────────────────────────────────
👤 Cliente: ${data.nombre}
📞 Teléfono: ${data.telefono}
📍 Localidad: ${data.localidad}
💼 Perfil: ${data.perfil}
📦 Ramo/Producto: ${data.producto}
📋 Notas comerciales: "${data.notas}"
───────────────────────────────────
Registrado por: ${data.agente}
    `;
    
    const opciones = {
      description: descripcionEvento,
      location: "Punto Naranja Nationale-Nederlanden Xàtiva"
    };
    
    const ev = calendar.createEvent(tituloEvento, fechaInicio, fechaFin, opciones);
    
    // Asignar códigos de color correspondientes
    try {
      if (prefijoTitulo.includes("🤝")) {
        // Citas / Entrevistas en color Azul Blueberry (9)
        ev.setColor("9");
      } else if (prefijoTitulo.includes("⏳") || prefijoTitulo.includes("📋")) {
        // Llamar después / Presupuesto en color Naranja (6)
        ev.setColor("6");
      } else if (prefijoTitulo.includes("❌")) {
        // No contesta (Auto-tarea pendiente) en color Rojo Tomate (11)
        ev.setColor("11");
      }
    } catch (colorErr) {
      Logger.log("Error al asignar color al evento: " + colorErr.toString());
    }
    
    Logger.log(`Evento creado exitosamente en Google Calendar: ${tituloEvento}`);
    
  } catch (err) {
    Logger.log("Error al crear evento en Google Calendar: " + err.toString());
  }
}

/**
 * Consulta en caliente de los eventos agendados para un día dado
 */
function obtenerAgendaDelDia(ss, fechaStr) {
  try {
    const calendar = CalendarApp.getDefaultCalendar();
    const partesFecha = fechaStr.split("-");
    const y = parseInt(partesFecha[0]);
    const m = parseInt(partesFecha[1]) - 1;
    const d = parseInt(partesFecha[2]);
    
    const inicioDia = new Date(y, m, d, 0, 0, 0);
    const finDia = new Date(y, m, d, 23, 59, 59);
    
    const events = calendar.getEvents(inicioDia, finDia);
    const agenda = events.map(ev => {
      return {
        title: ev.getTitle(),
        start: ev.getStartTime().toLocaleTimeString("es-ES", { hour: '2-digit', minute: '2-digit' }),
        end: ev.getEndTime().toLocaleTimeString("es-ES", { hour: '2-digit', minute: '2-digit' }),
        allDay: ev.isAllDayEvent()
      };
    });
    
    agenda.sort((a, b) => a.start.localeCompare(b.start));
    return agenda;
  } catch (err) {
    Logger.log("Error al obtener agenda: " + err.toString());
    return [];
  }
}

/**
 * Verifica si hay conflicto de horario (otra reunión fijada) en el rango propuesto
 */
function verificarConflictoAgenda(data) {
  try {
    const calendar = CalendarApp.getDefaultCalendar();
    const partesFecha = data.fechaCompromiso.split("-");
    const partesHora = data.horaCompromiso.split(":");
    
    const fechaInicio = new Date(
      parseInt(partesFecha[0]),
      parseInt(partesFecha[1]) - 1,
      parseInt(partesFecha[2]),
      parseInt(partesHora[0]),
      parseInt(partesHora[1])
    );
    
    const fechaFin = new Date(fechaInicio.getTime() + 30 * 60 * 1000); // Rango de 30 minutos
    
    const events = calendar.getEvents(fechaInicio, fechaFin);
    
    if (events.length > 0) {
      const e = events[0];
      const startStr = e.getStartTime().toLocaleTimeString("es-ES", { hour: '2-digit', minute: '2-digit' });
      const endStr = e.getEndTime().toLocaleTimeString("es-ES", { hour: '2-digit', minute: '2-digit' });
      return `Conflicto de horario: Ya tienes la cita "${e.getTitle()}" de ${startStr} a ${endStr}.`;
    }
    return null;
  } catch (err) {
    Logger.log("Error al verificar conflicto de agenda: " + err.toString());
    return null;
  }
}

/* ══════════════════════════════════════════════════════════════
   PLANTILLA DE CONFIGURACIÓN appsscript.json (COPIAR EN EL EDITOR)
   ══════════════════════════════════════════════════════════════
   {
     "timeZone": "Europe/Madrid",
     "dependencies": {
       "enabledAdvancedServices": [
         {
           "userSymbol": "People",
           "serviceId": "peopleapi",
           "version": "v1"
         }
       ]
     },
     "exceptionLogging": "STACKDRIVER",
     "runtimeVersion": "V8",
     "oauthScopes": [
       "https://www.googleapis.com/auth/spreadsheets",
       "https://www.googleapis.com/auth/calendar",
       "https://www.googleapis.com/auth/contacts",
       "https://www.googleapis.com/auth/script.external_request"
     ]
   }
   ══════════════════════════════════════════════════════════════ */
