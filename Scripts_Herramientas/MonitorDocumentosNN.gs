// ============================================================
// MONITOR DOCUMENTOS NN - Apps Script
// Autor: Federico Fontanals | Agente NN Xativa
// Funcion: Detecta documentos nuevos o modificados en el
//          Portal Comercial NN y avisa por email.
// Ejecucion: Automatica cada lunes a las 8:00h
// ============================================================

// --- CONFIGURACION - edita solo esta seccion ---
var CONFIG = {
  EMAIL_DESTINO:   'federico.fontanals@nnespana.es',
  EMAIL_CC:        'fefontanals@gmail.com',
  SHEET_ID:        '1Xilsgicwnckkd4cFLfcsYbTbyiZ886GFT2-h1QxSOwQ',
  HOJA_INVENTARIO: 'Inventario',
  HOJA_LOG:        'Log Cambios',
  GITHUB_REPO:     'https://github.com/FedeFonta08/propuestas-nn'
};

// --- PRODUCTOS DEL PORTAL Y SUS URLs ---
var PRODUCTOS = [
  { nombre: 'Contigo Autonomo (CAN)',               url: 'https://portalcomercial.nnespana.es/productos/Paginas/contigo-autonomo.aspx',                                          categoria: 'Autonomos y Empresas' },
  { nombre: 'Salud Completo Copago (SCC)',           url: 'https://portalcomercial.nnespana.es/productos/Paginas/salud-completo-copago.aspx',                                     categoria: 'Riesgo' },
  { nombre: 'Salud Completo sin Copago (SC)',        url: 'https://portalcomercial.nnespana.es/productos/Paginas/salud-completo-sin-copago.aspx',                                 categoria: 'Riesgo' },
  { nombre: 'Salud Completo Copago Autonomo (SCCA)', url: 'https://portalcomercial.nnespana.es/productos/Paginas/salud-completo-copago-autonomo.aspx',                            categoria: 'Autonomos y Empresas' },
  { nombre: 'Contigo Familia (CF)',                  url: 'https://portalcomercial.nnespana.es/productos/Paginas/Contigo-Familia.aspx',                                           categoria: 'Riesgo' },
  { nombre: 'Contigo Senior (CS)',                   url: 'https://portalcomercial.nnespana.es/productos/Paginas/contigo-senior.aspx',                                            categoria: 'Riesgo' },
  { nombre: 'LiderPlus Accidentes (LPA)',            url: 'https://portalcomercial.nnespana.es/productos/Paginas/LPA.aspx',                                                       categoria: 'Riesgo' },
  { nombre: 'Proteccion Plus (PP)',                  url: 'https://portalcomercial.nnespana.es/productos/Paginas/proteccion-plus.aspx',                                           categoria: 'Riesgo' },
  { nombre: 'Contigo Futuro (CFU)',                  url: 'https://portalcomercial.nnespana.es/productos/Paginas/contigo-futuro.aspx',                                            categoria: 'Ahorro-Inversion' },
  { nombre: 'Plan Creciente y SIALP (PC)',           url: 'https://portalcomercial.nnespana.es/productos/Paginas/Plan%20Creciente%20y%20Plan%20Creciente%20Sialp%20(PC).aspx',   categoria: 'Ahorro-Inversion' },
  { nombre: 'Ahorro Garantizado Extra (AGE)',        url: 'https://portalcomercial.nnespana.es/productos/Paginas/ahorro-garantizado-extra.aspx',                                  categoria: 'Ahorro-Inversion' },
  { nombre: 'Plan Garantizado Inversion (PGI)',      url: 'https://portalcomercial.nnespana.es/productos/Paginas/plan-garantizado-de-inversion.aspx',                             categoria: 'Ahorro-Inversion' },
  { nombre: 'Plan Pensiones Autonomos (PPSA)',       url: 'https://portalcomercial.nnespana.es/productos/Paginas/plan-pensiones-empleo-simplificado-autonomos.aspx',              categoria: 'Ahorro-Inversion' },
  { nombre: 'Hipotecas ING (INGAB)',                 url: 'https://portalcomercial.nnespana.es/productos/Paginas/Hipotecas.aspx',                                                 categoria: 'Ahorro-Inversion' },
  { nombre: 'MiHogar Seguro (MHS)',                  url: 'https://portalcomercial.nnespana.es/productos/Paginas/Mihogar-Seguro.aspx',                                            categoria: 'Patrimoniales' },
  { nombre: 'Contigo Pyme (CP)',                     url: 'https://portalcomercial.nnespana.es/productos/Paginas/Contigo%20Pyme.aspx',                                            categoria: 'Autonomos y Empresas' }
];

// ============================================================
// FUNCION PRINCIPAL
// ============================================================
function escanearPortalNN() {
  var ss       = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  var sheetInv = obtenerOCrearHoja(ss, CONFIG.HOJA_INVENTARIO);
  var sheetLog = obtenerOCrearHoja(ss, CONFIG.HOJA_LOG);
  inicializarCabeceras(sheetInv, sheetLog);

  var cambios  = [];
  var fechaHoy = new Date();

  for (var i = 0; i < PRODUCTOS.length; i++) {
    var producto = PRODUCTOS[i];
    try {
      var docsPortal = obtenerDocumentosProducto(producto.url);
      for (var j = 0; j < docsPortal.length; j++) {
        var resultado = procesarDocumento(sheetInv, producto, docsPortal[j], fechaHoy);
        if (resultado) cambios.push(resultado);
      }
    } catch(e) {
      Logger.log('Error en ' + producto.nombre + ': ' + e.message);
    }
  }

  if (cambios.length > 0) {
    registrarCambiosEnLog(sheetLog, cambios, fechaHoy);
    enviarEmailAlertas(cambios, fechaHoy);
    Logger.log('Cambios detectados: ' + cambios.length);
  } else {
    Logger.log('Sin cambios detectados - ' + fechaHoy.toLocaleDateString('es-ES'));
  }
}

// ============================================================
// OBTENER DOCUMENTOS DE UNA PAGINA DE PRODUCTO
// ============================================================
function obtenerDocumentosProducto(url) {
  var docs = [];
  try {
    var resp = UrlFetchApp.fetch(url, {
      muteHttpExceptions: true,
      headers: { 'Accept': 'text/html' }
    });
    var html = resp.getContentText();

    // Buscar enlaces a PDFs en carpeta /Productos/
    var patron = /href="([^"]*\/Productos\/[^"]*\.pdf)"/gi;
    var match;
    while ((match = patron.exec(html)) !== null) {
      var href    = match[1];
      var archivo = href.split('/').pop().split('?')[0];
      var nombre  = decodeURIComponent(archivo).replace('.pdf', '').replace(/-/g, ' ').replace(/_/g, ' ');
      var urlDoc  = href.startsWith('http') ? href : 'https://portalcomercial.nnespana.es' + href;
      // Evitar duplicados
      var existe = false;
      for (var k = 0; k < docs.length; k++) {
        if (docs[k].archivo === archivo) { existe = true; break; }
      }
      if (!existe && archivo.length > 3) {
        docs.push({ nombre: nombre, url: urlDoc, archivo: archivo });
      }
    }
  } catch(e) {
    Logger.log('Error fetch ' + url + ': ' + e.message);
  }
  return docs;
}

// ============================================================
// PROCESAR DOCUMENTO - detecta si es nuevo
// ============================================================
function procesarDocumento(sheet, producto, doc, fecha) {
  var datos    = sheet.getDataRange().getValues();
  var esNuevo  = true;

  for (var i = 1; i < datos.length; i++) {
    if (datos[i][3] === doc.archivo && datos[i][0] === producto.nombre) {
      esNuevo = false;
      break;
    }
  }

  if (esNuevo) {
    sheet.appendRow([
      producto.nombre,
      producto.categoria,
      doc.nombre,
      doc.archivo,
      doc.url,
      fecha,
      'NUEVO',
      'No subido',
      ''
    ]);
    return {
      tipo:      'NUEVO',
      producto:  producto.nombre,
      categoria: producto.categoria,
      doc:       doc.nombre,
      archivo:   doc.archivo,
      url:       doc.url
    };
  }
  return null;
}

// ============================================================
// REGISTRAR CAMBIOS EN LOG
// ============================================================
function registrarCambiosEnLog(sheet, cambios, fecha) {
  var fechaStr = Utilities.formatDate(fecha, 'Europe/Madrid', 'dd/MM/yyyy HH:mm');
  for (var i = 0; i < cambios.length; i++) {
    var c = cambios[i];
    sheet.appendRow([fechaStr, c.tipo, c.producto, c.categoria, c.doc, c.archivo, c.url]);
  }
}

// ============================================================
// ENVIAR EMAIL DE ALERTA
// ============================================================
function enviarEmailAlertas(cambios, fecha) {
  var fechaStr = Utilities.formatDate(fecha, 'Europe/Madrid', 'dd/MM/yyyy');

  var filas = '';
  for (var i = 0; i < cambios.length; i++) {
    var c  = cambios[i];
    var bg = (i % 2 === 0) ? '#ffffff' : '#fff3ea';
    filas += '<tr style="background:' + bg + ';">'
           + '<td style="padding:8px;border-bottom:1px solid #eee;">' + c.producto + '</td>'
           + '<td style="padding:8px;border-bottom:1px solid #eee;"><a href="' + c.url + '">' + c.doc + '</a></td>'
           + '<td style="padding:8px;border-bottom:1px solid #eee;">Subir a GitHub</td>'
           + '</tr>';
  }

  var html = '<div style="font-family:Arial,sans-serif;max-width:700px;">'
    + '<div style="background:#FF6200;padding:20px;border-radius:8px 8px 0 0;">'
    + '<h2 style="color:white;margin:0;">Monitor Documentos NN</h2>'
    + '<p style="color:white;margin:5px 0 0 0;">Revision del ' + fechaStr + ' - ' + cambios.length + ' documento(s) nuevo(s)</p>'
    + '</div>'
    + '<div style="background:#f9f9f9;padding:20px;border:1px solid #ddd;">'
    + '<table style="width:100%;border-collapse:collapse;">'
    + '<tr style="background:#FF6200;color:white;">'
    + '<th style="padding:8px;text-align:left;">Producto</th>'
    + '<th style="padding:8px;text-align:left;">Documento</th>'
    + '<th style="padding:8px;text-align:left;">Accion</th>'
    + '</tr>'
    + filas
    + '</table>'
    + '<br><hr style="border:1px solid #eee;">'
    + '<p style="color:#666;font-size:13px;">'
    + '<a href="https://docs.google.com/spreadsheets/d/' + CONFIG.SHEET_ID + '">Ver inventario en Google Sheets</a> | '
    + '<a href="' + CONFIG.GITHUB_REPO + '">Ver GitHub</a>'
    + '</p></div>'
    + '<div style="background:#eee;padding:10px;text-align:center;border-radius:0 0 8px 8px;">'
    + '<small style="color:#888;">Monitor NN - Federico Fontanals - Agente Punto Naranja Xativa</small>'
    + '</div></div>';

  GmailApp.sendEmail(
    CONFIG.EMAIL_DESTINO,
    'NN Documentos - ' + cambios.length + ' nuevo(s) - ' + fechaStr,
    'Hay documentos nuevos en el portal NN. Revisa el email en formato HTML.',
    { htmlBody: html, cc: CONFIG.EMAIL_CC, name: 'Monitor NN - Fede Fontanals' }
  );
  Logger.log('Email enviado a ' + CONFIG.EMAIL_DESTINO);
}

// ============================================================
// INICIALIZAR CABECERAS
// ============================================================
function inicializarCabeceras(sheetInv, sheetLog) {
  if (sheetInv.getLastRow() === 0) {
    sheetInv.appendRow(['Producto','Categoria','Nombre documento','Archivo','URL Portal','Fecha deteccion','Estado portal','Estado GitHub','Notas']);
    sheetInv.getRange(1,1,1,9).setBackground('#FF6200').setFontColor('white').setFontWeight('bold');
    sheetInv.setFrozenRows(1);
    sheetInv.setColumnWidth(1, 220);
    sheetInv.setColumnWidth(3, 280);
    sheetInv.setColumnWidth(4, 240);
    sheetInv.setColumnWidth(7, 100);
    sheetInv.setColumnWidth(8, 100);
  }
  if (sheetLog.getLastRow() === 0) {
    sheetLog.appendRow(['Fecha','Tipo','Producto','Categoria','Documento','Archivo','URL']);
    sheetLog.getRange(1,1,1,7).setBackground('#333333').setFontColor('white').setFontWeight('bold');
    sheetLog.setFrozenRows(1);
  }
}

// ============================================================
// CARGAR INVENTARIO INICIAL (ejecutar una sola vez)
// ============================================================
function cargarInventarioInicial() {
  var ss       = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  var sheetInv = obtenerOCrearHoja(ss, CONFIG.HOJA_INVENTARIO);
  var sheetLog = obtenerOCrearHoja(ss, CONFIG.HOJA_LOG);
  inicializarCabeceras(sheetInv, sheetLog);

  var fecha = new Date();
  var inv = [
    ['Contigo Autonomo (CAN)','Autonomos y Empresas','Condiciones Generales','CCGG Contigo Autonomo.pdf','/productos/Productos/CCGG Contigo Autonomo.pdf','VIGENTE','No subido'],
    ['Contigo Autonomo (CAN)','Autonomos y Empresas','Condiciones Particulares','CCLL Contigo Autonomo.pdf','/productos/Productos/CCLL Contigo Autonomo.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Ficha de producto','ficha-salud-completo-copago.pdf','/productos/Productos/ficha-salud-completo-copago.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','CCGG','CCGG-Salud-Completo-Copago.pdf','/productos/Productos/CCGG-Salud-Completo-Copago-sin-poliza.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','CCLL','CCLL-Salud-Completo-Copago.pdf','/productos/Productos/CCLL-Salud-Completo-Copago-sin-poliza.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Guia de uso','guia-de-uso-del-seguro-salud-completo-copago.pdf','/productos/Productos/guia-de-uso-del-seguro-salud-completo-copago.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Manual de formacion','manual-de-formacion-salud-completo-copago.pdf','/productos/Productos/manual-de-formacion-salud-completo-copago.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Folleto SCC','nn-salud-completo-copago-folleto.pdf','/productos/Productos/nn-salud-completo-copago-folleto.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Condiciones descuento 12,5%','condiciones-descuento-12-5-anual.pdf','/productos/Productos/condiciones-descuento-12-5-anual.pdf','VIGENTE','Subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Condiciones descuento zonas','condiciones-descuento-por-zonas.pdf','/productos/Productos/condiciones-descuento-por-zonas.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Sanitas Dental 21','sanitas-dental-21-nn-servicios-y-tarifas.pdf','/productos/Productos/sanitas-dental-21-nn-servicios-y-tarifas.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Q&A','preguntas-y-respuestas-scc.pdf','/productos/Productos/preguntas-y-respuestas-scc.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Tabla de ventajas','ventajas-salud-vida.pdf','/productos/Productos/ventajas-salud-vida.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago (SCC)','Riesgo','Tabla Campanas e Incentivos','tabla-campanas-e-incentivos-de-salud.pdf','/productos/Productos/tabla-campanas-e-incentivos-de-salud.pdf','VIGENTE','No subido'],
    ['Salud Completo sin Copago (SC)','Riesgo','Ficha de producto','Ficha-Salud.pdf','/productos/Productos/Ficha-Salud.pdf','VIGENTE','Subido'],
    ['Salud Completo sin Copago (SC)','Riesgo','CCGG','CCGG-Salud-Completo.pdf','/productos/Productos/CCGG-Salud-Completo.pdf','VIGENTE','Subido'],
    ['Salud Completo sin Copago (SC)','Riesgo','CCGG ingles','CCGG-Salud-Completo-ingles.pdf','/productos/Productos/CCGG-Salud-Completo-ingles.pdf','VIGENTE','No subido'],
    ['Salud Completo sin Copago (SC)','Riesgo','CCLL','CCLL-Salud-Completo.pdf','/productos/Productos/CCLL-Salud-Completo.pdf','VIGENTE','Subido'],
    ['Contigo Familia (CF)','Riesgo','CCGG','CFA_CCGG_V01_marketing.pdf','/productos/Productos/CFA_CCGG_V01_marketing.pdf','VIGENTE','No subido'],
    ['Contigo Familia (CF)','Riesgo','CCLL','CFA_CCLL_Contigo_Familia.pdf','/productos/Productos/CFA_CCLL_Contigo_Familia.pdf','VIGENTE','No subido'],
    ['Contigo Familia (CF)','Riesgo','FAQ','FAQ-contigo-familia.pdf','/productos/Productos/FAQ-contigo-familia.pdf','VIGENTE','No subido'],
    ['Contigo Familia (CF)','Riesgo','Ficha de producto','Ficha de producto Contigo Familia.pdf','/productos/Productos/Ficha de producto Contigo Familia.pdf','VIGENTE','No subido'],
    ['Contigo Familia (CF)','Riesgo','Folleto web','NN Contigo Familia folleto web.pdf','/productos/Productos/NN Contigo Familia folleto web.pdf','VIGENTE','No subido'],
    ['Contigo Familia (CF)','Riesgo','Presentacion VF','PRESENTACION CONTIGO FAMILIA VF.pdf','/productos/Productos/PRESENTACION CONTIGO FAMILIA VF.pdf','VIGENTE','No subido'],
    ['Contigo Senior (CS)','Riesgo','Presentacion','Presentacion Contigo Senior.pdf','/productos/Productos/Presentacion Contigo Senior.pdf','VIGENTE','No subido'],
    ['Contigo Senior (CS)','Riesgo','Ficha de producto','ficha-de-producto-contigo-senior.pdf','/productos/Productos/ficha-de-producto-contigo-senior.pdf','VIGENTE','No subido'],
    ['Contigo Senior (CS)','Riesgo','Folleto','folleto-contigo-senior.pdf','/productos/Productos/folleto-contigo-senior.pdf','VIGENTE','No subido'],
    ['LiderPlus Accidentes (LPA)','Riesgo','Ficha LiderPlus','Ficha LiderPlus Accidentes.pdf','/productos/Productos/Ficha LiderPlus Accidentes.pdf','VIGENTE','No subido'],
    ['Contigo Futuro (CFU)','Ahorro-Inversion','Ficha de producto','Ficha-de-producto.pdf','/productos/Productos/Ficha-de-producto.pdf','VIGENTE','No subido'],
    ['Contigo Futuro (CFU)','Ahorro-Inversion','FAQs','FAQs Contigo Futuro.pdf','/productos/Productos/FAQs Contigo Futuro.pdf','VIGENTE','No subido'],
    ['Contigo Futuro (CFU)','Ahorro-Inversion','Argumentario Aranceles','Argumentario Politica Arancelaria EEUU Abril 2025.pdf','/productos/Productos/Argumentario Politica Arancelaria EEUU Abril 2025.pdf','VIGENTE','No subido'],
    ['Ahorro Garantizado Extra (AGE)','Ahorro-Inversion','CCGG','CCGG-ahorro-garantizado-extra.pdf','/productos/Productos/CCGG-ahorro-garantizado-extra.pdf','VIGENTE','No subido'],
    ['Ahorro Garantizado Extra (AGE)','Ahorro-Inversion','Ficha','ficha-ahorro-garantizado-extra.pdf','/productos/Productos/ficha-ahorro-garantizado-extra.pdf','VIGENTE','No subido'],
    ['Plan Pensiones Autonomos (PPSA)','Ahorro-Inversion','Argumentario Agentes','argumentario-ppesa-agente.pdf','/productos/Productos/argumentario-ppesa-agente.pdf','VIGENTE','No subido'],
    ['Plan Pensiones Autonomos (PPSA)','Ahorro-Inversion','Ficha Plan Pensiones','Ficha Plan Empleo Simplificado Autonomos.pdf','/productos/Productos/Ficha Plan de Empleo Simplificado de Autonomos.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago Autonomo (SCCA)','Autonomos y Empresas','Ficha','ficha-salud-completo-copago-autonomo.pdf','/productos/Productos/ficha-salud-completo-copago-autonomo.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago Autonomo (SCCA)','Autonomos y Empresas','CCGG','CCGG-salud-completo-copago-autonomo.pdf','/productos/Productos/CCGG-salud-completo-copago-autonomo.pdf','VIGENTE','No subido'],
    ['Salud Completo Copago Autonomo (SCCA)','Autonomos y Empresas','CCLL','CCLL-salud-completo-copago-autonomo.pdf','/productos/Productos/CCLL-salud-completo-copago-autonomo.pdf','VIGENTE','No subido'],
    ['Hipotecas ING (INGAB)','Ahorro-Inversion','Folleto hipoteca','Folleto hipoteca.pdf','','VIGENTE','Subido'],
    ['Hipotecas ING (INGAB)','Ahorro-Inversion','Guia Completa Hipoteca Naranja','Guia Completa Hipoteca NARANJA ING.pdf','','VIGENTE','Subido']
  ];

  for (var i = 0; i < inv.length; i++) {
    var f = inv[i];
    sheetInv.appendRow([f[0],f[1],f[2],f[3],f[4],fecha,f[5],f[6],'']);
  }

  // Formato condicional
  var range     = sheetInv.getRange(2, 8, sheetInv.getLastRow(), 1);
  var reglas    = sheetInv.getConditionalFormatRules();
  var r1 = SpreadsheetApp.newConditionalFormatRule().whenTextContains('Subido').setBackground('#d9ead3').setRanges([range]).build();
  var r2 = SpreadsheetApp.newConditionalFormatRule().whenTextContains('No subido').setBackground('#fce5cd').setRanges([range]).build();
  var r3 = SpreadsheetApp.newConditionalFormatRule().whenTextContains('Verificar').setBackground('#fff2cc').setRanges([range]).build();
  reglas.push(r1, r2, r3);
  sheetInv.setConditionalFormatRules(reglas);

  SpreadsheetApp.flush();
  Logger.log('Inventario inicial cargado: ' + inv.length + ' documentos.');
}

// ============================================================
// INSTALAR ACTIVADOR SEMANAL (ejecutar una sola vez)
// ============================================================
function instalarActivador() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'escanearPortalNN') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  ScriptApp.newTrigger('escanearPortalNN')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .atHour(8)
    .create();
  Logger.log('Activador instalado: cada lunes a las 8:00h');
}

// ============================================================
// OBTENER O CREAR HOJA
// ============================================================
function obtenerOCrearHoja(ss, nombre) {
  var hoja = ss.getSheetByName(nombre);
  if (!hoja) hoja = ss.insertSheet(nombre);
  return hoja;
}
