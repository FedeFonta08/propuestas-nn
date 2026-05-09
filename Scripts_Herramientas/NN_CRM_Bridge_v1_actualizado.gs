// ============================================================
// NN CRM BRIDGE v1 — Sistema de Gestión Integrado
// Fede Fontanals · Agente Dinamizador Punto Naranja · Xàtiva
// ============================================================
// FUNCIONES:
//   1. Registrar resultado de llamada en CRM Maestro
//   2. Crear nuevo contacto en CRM + Google Contacts
//   3. Crear evento en Google Calendar automáticamente
//
// INSTALACIÓN:
//   1. Abre tu Google Sheet "Sistema_Gestion_NN_v4_BuyerPersona"
//   2. Extensiones > Apps Script > pega este código
//   3. Guarda el proyecto (Ctrl+S)
//   4. Ejecuta "configurarScript" una sola vez (permisos)
//   5. Despliega como Web App:
//      Implementar > Nueva implementación > Web App
//      Ejecutar como: Yo (fefontanals@gmail.com)
//      Acceso: Cualquier usuario
//      Copiar la URL generada → pégala en el HTML (SCRIPT_URL)
// ============================================================

// ── CONFIGURACIÓN ────────────────────────────────────────────
const CFG = {
  HOJA_CRM:        'CRM MAESTRO',
  FILA_CABECERA:   2,       // fila 2 tiene los nombres de columna
  FILA_DATOS:      3,       // los datos empiezan en fila 3
  EMAIL_AGENTE:    'fefontanals@gmail.com',
  NOMBRE_AGENTE:   'Fede Fontanals',
  CAL_ID:          'fefontanals@gmail.com',  // calendario principal
  TZ:              'Europe/Madrid',
};

// ── MAPA DE COLUMNAS (basado en CRM v4) ──────────────────────
// Posición 1-indexed de cada campo en el CRM Maestro
const COL = {
  NOMBRE:            1,
  TEL1:              2,
  TEL2:              3,
  EMAIL:             4,
  LOCALIDAD:         5,
  CUMPLEANOS:        6,
  ESTADO:            7,
  URGENCIA:          8,
  VTO_MES:           9,
  PRODUCTOS:         10,
  // Pólizas 11-25
  ESTADO_CIVIL:      26,
  REGIMEN_SS:        27,
  ANIOS_SS:          28,
  HIJOS:             29,
  PAREJA:            30,
  SALARIO:           31,
  PAGAS:             32,
  AHORRO:            33,
  GASTOS:            34,
  NIVEL_ECO:         35,
  NECESIDAD:         36,
  PRODUCTO_COT:      37,
  EXPEDIENTE:        38,
  ADN:               39,
  SEMAFORO:          40,
  WHATSAPP:          41,
  FECHA_CONTACTO:    42,
  RESULTADO:         43,
  PRODUCTO_OFRECIDO: 44,
  FECHA_PROX:        45,
  PROX_ACCION:       46,
  CANAL:             47,
  RECOMENDADO:       48,
  OBSERVACIONES:     49,
  BUYER_PERSONA:     50,
  PRODUCTO_REC:      51,
};

// ── CORS + ROUTER PRINCIPAL ───────────────────────────────────
function doPost(e) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const data = JSON.parse(e.postData.contents);
    let result;

    switch (data.accion) {
      case 'registrar_llamada':
        result = registrarLlamada(data);
        break;
      case 'nuevo_contacto':
        result = nuevoContacto(data);
        break;
      case 'buscar_contacto':
        result = buscarContacto(data.nombre);
        break;
      default:
        result = { ok: false, error: 'Acción no reconocida: ' + data.accion };
    }

    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  // Comprobación de estado
  if (!e.parameter.payload) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: true, msg: 'NN CRM Bridge v1 activo', ts: new Date().toISOString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  // Petición real con payload
  try {
    const data = JSON.parse(decodeURIComponent(e.parameter.payload));
    let result;
    switch (data.accion) {
      case 'registrar_llamada':  result = registrarLlamada(data); break;
      case 'nuevo_contacto':     result = nuevoContacto(data); break;
      case 'buscar_contacto':    result = buscarContacto(data.nombre); break;
      default: result = { ok: false, error: 'Acción no reconocida: ' + data.accion };
    }
    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
  } catch(err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// ── 1. REGISTRAR LLAMADA ──────────────────────────────────────
// Recibe: { accion, nombre, resultado, notas, proxAccion, fechaProx, productoOfrecido }
// resultado: 'contactado' | 'no_contactado' | 'cita_fijada' | 'llamar_despues'
function registrarLlamada(data) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CFG.HOJA_CRM);
  if (!sheet) return { ok: false, error: 'Hoja CRM MAESTRO no encontrada' };

  const fila = encontrarFila(sheet, data.nombre);
  if (!fila) return { ok: false, error: 'Contacto no encontrado: ' + data.nombre };

  const ahora = new Date();
  const fechaHoy = Utilities.formatDate(ahora, CFG.TZ, 'dd/MM/yyyy HH:mm');

  // Mapear resultado a texto legible
  const resultadoTexto = {
    'contactado':      '✅ Contactado',
    'no_contactado':   '❌ No contactado',
    'cita_fijada':     '📅 Cita fijada',
    'llamar_despues':  '🔄 Llamar después'
  }[data.resultado] || data.resultado;

  // Escribir en el CRM
  sheet.getRange(fila, COL.FECHA_CONTACTO).setValue(fechaHoy);
  sheet.getRange(fila, COL.RESULTADO).setValue(resultadoTexto);
  if (data.productoOfrecido) sheet.getRange(fila, COL.PRODUCTO_OFRECIDO).setValue(data.productoOfrecido);
  if (data.notas)       sheet.getRange(fila, COL.OBSERVACIONES).setValue(data.notas);
  if (data.proxAccion)  sheet.getRange(fila, COL.PROX_ACCION).setValue(data.proxAccion);
  if (data.fechaProx)   sheet.getRange(fila, COL.FECHA_PROX).setValue(data.fechaProx);

  let calEventId = null;

  // Si hay cita, crear evento en Calendar
  if (data.resultado === 'cita_fijada' && data.fechaProx) {
    calEventId = crearEventoCalendar({
      nombre:   data.nombre,
      tel:      sheet.getRange(fila, COL.TEL1).getValue(),
      fecha:    data.fechaProx,
      hora:     data.horaCita || '10:00',
      producto: data.productoOfrecido || '',
      notas:    data.notas || ''
    });
  }

  return {
    ok: true,
    msg: 'Llamada registrada correctamente',
    fila: fila,
    calEventId: calEventId
  };
}

// ── 2. NUEVO CONTACTO ─────────────────────────────────────────
// Escribe en CRM Maestro + crea contacto en Google Contacts
function nuevoContacto(data) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CFG.HOJA_CRM);
  if (!sheet) return { ok: false, error: 'Hoja CRM MAESTRO no encontrada' };

  // Verificar que no existe ya
  const existente = encontrarFila(sheet, data.nombre);
  if (existente) return { ok: false, error: 'El contacto ya existe en la fila ' + existente };

  // Preparar fila nueva
  const ahora = Utilities.formatDate(new Date(), CFG.TZ, 'dd/MM/yyyy HH:mm');
  const ultimaFila = sheet.getLastRow() + 1;

  const fila = new Array(COL.PRODUCTO_REC).fill('');
  fila[COL.NOMBRE - 1]            = data.nombre || '';
  fila[COL.TEL1 - 1]              = data.tel1 || '';
  fila[COL.TEL2 - 1]              = data.tel2 || '';
  fila[COL.EMAIL - 1]             = data.email || '';
  fila[COL.LOCALIDAD - 1]         = data.localidad || '';
  fila[COL.CUMPLEANOS - 1]        = data.cumpleanos || '';
  fila[COL.ESTADO - 1]            = data.estado || 'Potencial';
  fila[COL.URGENCIA - 1]          = data.urgencia || '⚪ RESTO';
  fila[COL.ESTADO_CIVIL - 1]      = data.estadoCivil || '';
  fila[COL.REGIMEN_SS - 1]        = data.regimenSS || '';
  fila[COL.ANIOS_SS - 1]          = data.aniosSS || '';
  fila[COL.HIJOS - 1]             = data.hijos || '';
  fila[COL.PAREJA - 1]            = data.pareja || '';
  fila[COL.SALARIO - 1]           = data.salario || '';
  fila[COL.PAGAS - 1]             = data.pagas || '';
  fila[COL.AHORRO - 1]            = data.ahorro || '';
  fila[COL.GASTOS - 1]            = data.gastos || '';
  fila[COL.NIVEL_ECO - 1]         = data.nivelEco || '';
  fila[COL.NECESIDAD - 1]         = data.necesidad || '';
  fila[COL.PRODUCTO_COT - 1]      = data.productoCotizado || '';
  fila[COL.CANAL - 1]             = data.canal || '';
  fila[COL.RECOMENDADO - 1]       = data.recomendado || '';
  fila[COL.OBSERVACIONES - 1]     = data.observaciones || '';
  fila[COL.BUYER_PERSONA - 1]     = data.buyerPersona || '';
  fila[COL.PRODUCTO_REC - 1]      = data.productoRecomendado || '';
  fila[COL.FECHA_CONTACTO - 1]    = ahora;
  fila[COL.RESULTADO - 1]         = '🆕 Primer contacto';

  sheet.getRange(ultimaFila, 1, 1, fila.length).setValues([fila]);

  // Crear en Google Contacts (People API)
  let contactId = null;
  try {
    contactId = crearContactoGoogle(data);
  } catch (err) {
    Logger.log('Google Contacts error: ' + err.toString());
    // No bloqueamos — el CRM sí se guardó
  }

  return {
    ok: true,
    msg: 'Contacto creado en CRM' + (contactId ? ' y Google Contacts' : ' (Google Contacts: revisar permisos)'),
    fila: ultimaFila,
    contactId: contactId
  };
}

// ── 3. BUSCAR CONTACTO ────────────────────────────────────────
function buscarContacto(nombre) {
  if (!nombre || nombre.length < 3) return { ok: false, resultados: [] };

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CFG.HOJA_CRM);
  const datos = sheet.getDataRange().getValues();
  const nombreBuscar = nombre.toLowerCase().trim();

  const resultados = [];
  for (let i = CFG.FILA_DATOS - 1; i < datos.length; i++) {
    const n = (datos[i][COL.NOMBRE - 1] || '').toString().toLowerCase();
    if (n.includes(nombreBuscar)) {
      resultados.push({
        fila:     i + 1,
        nombre:   datos[i][COL.NOMBRE - 1],
        tel1:     datos[i][COL.TEL1 - 1],
        estado:   datos[i][COL.ESTADO - 1],
        necesidad: datos[i][COL.NECESIDAD - 1],
        producto: datos[i][COL.PRODUCTO_COT - 1],
      });
    }
  }

  return { ok: true, resultados: resultados };
}

// ── HELPER: encontrar fila por nombre ────────────────────────
function encontrarFila(sheet, nombre) {
  if (!nombre) return null;
  const datos = sheet.getDataRange().getValues();
  const buscar = nombre.toLowerCase().trim();
  for (let i = CFG.FILA_DATOS - 1; i < datos.length; i++) {
    const n = (datos[i][COL.NOMBRE - 1] || '').toString().toLowerCase().trim();
    if (n === buscar) return i + 1;
  }
  return null;
}

// ── HELPER: crear evento en Google Calendar ──────────────────
function crearEventoCalendar(params) {
  try {
    const cal = CalendarApp.getCalendarById(CFG.CAL_ID);
    if (!cal) return null;

    // Parsear fecha y hora
    // fechaProx puede venir como 'dd/MM/yyyy' o 'yyyy-MM-dd'
    let fecha;
    if (params.fecha.includes('/')) {
      const p = params.fecha.split('/');
      fecha = new Date(p[2], p[1] - 1, p[0]);
    } else {
      fecha = new Date(params.fecha);
    }

    const [h, m] = (params.hora || '10:00').split(':').map(Number);
    fecha.setHours(h, m, 0);

    const fin = new Date(fecha.getTime() + 60 * 60 * 1000); // +1 hora

    const titulo = `📋 Visita NN · ${params.nombre}`;
    const desc = [
      `📞 Teléfono: ${params.tel}`,
      params.producto ? `📦 Producto: ${params.producto}` : '',
      params.notas ? `📝 Notas: ${params.notas}` : '',
      '',
      `Agente: ${CFG.NOMBRE_AGENTE} | NN Xàtiva`,
    ].filter(Boolean).join('\n');

    const evento = cal.createEvent(titulo, fecha, fin, {
      description: desc,
      reminders: [{ method: 'popup', minutes: 60 }, { method: 'popup', minutes: 15 }]
    });

    return evento.getId();
  } catch (err) {
    Logger.log('Error Calendar: ' + err.toString());
    return null;
  }
}

// ── HELPER: crear contacto en Google Contacts (People API) ───
function crearContactoGoogle(data) {
  // Requiere scope: https://www.googleapis.com/auth/contacts
  const url = 'https://people.googleapis.com/v1/people:createContact';

  const nombres = (data.nombre || '').trim().split(' ');
  const primerNombre = nombres[0] || '';
  const apellidos = nombres.slice(1).join(' ');

  const body = {
    names: [{ givenName: primerNombre, familyName: apellidos, displayName: data.nombre }],
    phoneNumbers: [],
    emailAddresses: [],
    organizations: [],
    addresses: [],
    birthdays: [],
    userDefined: [],
    biographies: []
  };

  if (data.tel1) body.phoneNumbers.push({ value: data.tel1, type: 'mobile' });
  if (data.tel2) body.phoneNumbers.push({ value: data.tel2, type: 'other' });
  if (data.email) body.emailAddresses.push({ value: data.email, type: 'home' });
  if (data.empresa) body.organizations.push({ name: data.empresa, title: data.cargo || '' });
  if (data.localidad) body.addresses.push({ city: data.localidad, type: 'home' });
  if (data.apodo) body.nicknames = [{ value: data.apodo }];

  // Cumpleaños
  if (data.cumpleanos) {
    try {
      const f = new Date(data.cumpleanos);
      body.birthdays.push({ date: { year: f.getFullYear(), month: f.getMonth() + 1, day: f.getDate() } });
    } catch(e) {}
  }

  // Notas / observaciones → biografia
  const notas = [
    data.observaciones,
    data.necesidad ? 'Necesidad: ' + data.necesidad : '',
    data.buyerPersona ? 'Buyer Persona: ' + data.buyerPersona : '',
    data.recomendado ? 'Recomendado por: ' + data.recomendado : '',
  ].filter(Boolean).join('\n');
  if (notas) body.biographies.push({ value: notas, contentType: 'TEXT_PLAIN' });

  const token = ScriptApp.getOAuthToken();
  const res = UrlFetchApp.fetch(url, {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });

  const json = JSON.parse(res.getContentText());
  if (json.resourceName) return json.resourceName;
  throw new Error(JSON.stringify(json));
}

// ── FUNCIÓN DE CONFIGURACIÓN (ejecutar una sola vez) ─────────
function configurarScript() {
  // Esta función no hace nada operativo pero fuerza la autorización
  // de todos los scopes necesarios cuando la ejecutas manualmente.
  const sheet = SpreadsheetApp.getActiveSpreadsheet();
  const cal   = CalendarApp.getCalendarById(CFG.CAL_ID);
  const tok   = ScriptApp.getOAuthToken(); // fuerza People API auth

  Logger.log('✅ Configuración correcta');
  Logger.log('   Spreadsheet: ' + sheet.getName());
  Logger.log('   Calendario: ' + (cal ? cal.getName() : '⚠️ no encontrado'));
  Logger.log('   OAuth token: OK');

  SpreadsheetApp.getUi().alert(
    '✅ NN CRM Bridge configurado\n\n' +
    'Siguiente paso:\n' +
    'Implementar > Nueva implementación > Web App\n' +
    'Ejecutar como: Yo\n' +
    'Acceso: Cualquier usuario\n\n' +
    'Copia la URL y pégala en el HTML (SCRIPT_URL)'
  );
}

// ── FUNCIÓN DE PRUEBA ─────────────────────────────────────────
function testRegistrarLlamada() {
  const resultado = registrarLlamada({
    nombre:          'Ana Maria Sarrio Carretón',  // debe existir en tu CRM
    resultado:       'cita_fijada',
    notas:           'Interesada en Plan Salud+Vida. Llamar el lunes.',
    proxAccion:      'Visita presencial',
    fechaProx:       '16/04/2025',
    horaCita:        '11:00',
    productoOfrecido: 'Plan Salud + Vida'
  });
  Logger.log(JSON.stringify(resultado, null, 2));
}
