/**
 * SEGMENTACIÓN AUTOMÁTICA CRM NN — VERSIÓN 2 CORREGIDA
 * Detecta automáticamente las columnas por nombre
 * No depende de posiciones fijas
 * 
 * INSTRUCCIONES:
 * 1. Borra el script anterior en Apps Script
 * 2. Copia y pega ESTE código completo
 * 3. Guarda (Ctrl+S)
 * 4. Ejecuta: añadirSegmentacionCRM_v2()
 * 5. Las columnas viejas con #ERROR se borran automáticamente
 */

function añadirSegmentacionCRM_v2() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('CRM MAESTRO');
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Error: No se encuentra la pestaña "CRM MAESTRO"');
    return;
  }
  
  // PASO 1: Detectar columnas por nombre
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  
  // Buscar columnas críticas
  const colCumpleaños = buscarColumna(headers, 'Cumpleaños');
  const colBuyerPersona = buscarColumna(headers, 'Buyer Persona');
  const colProductoNN = buscarColumna(headers, 'Producto NN recomendado');
  const colProductosActuales = buscarColumna(headers, 'Productos actuales');
  
  Logger.log('📍 Columnas detectadas:');
  Logger.log(`- Cumpleaños: ${colCumpleaños !== -1 ? columnToLetter(colCumpleaños + 1) : 'NO ENCONTRADA'}`);
  Logger.log(`- Buyer Persona: ${colBuyerPersona !== -1 ? columnToLetter(colBuyerPersona + 1) : 'NO ENCONTRADA'}`);
  Logger.log(`- Producto NN recomendado: ${colProductoNN !== -1 ? columnToLetter(colProductoNN + 1) : 'NO ENCONTRADA'}`);
  Logger.log(`- Productos actuales: ${colProductosActuales !== -1 ? columnToLetter(colProductosActuales + 1) : 'NO ENCONTRADA'}`);
  
  if (colCumpleaños === -1) {
    SpreadsheetApp.getUi().alert('Error', 'No se encuentra la columna "Cumpleaños"', SpreadsheetApp.getUi().ButtonSet.OK);
    return;
  }
  
  // PASO 2: Borrar columnas viejas con #ERROR si existen
  const colSegmentoViejo = headers.indexOf('SEGMENTO_BP');
  const colProductoViejo = headers.indexOf('PRODUCTO_PPAL_NN');
  const colAutonomoViejo = headers.indexOf('ES_AUTONOMO');
  
  if (colSegmentoViejo !== -1 || colProductoViejo !== -1 || colAutonomoViejo !== -1) {
    Logger.log('🗑️ Borrando columnas viejas con #ERROR...');
    
    // Borrar en orden inverso para no afectar índices
    const columnasABorrar = [colSegmentoViejo, colProductoViejo, colAutonomoViejo]
      .filter(col => col !== -1)
      .sort((a, b) => b - a);
    
    columnasABorrar.forEach(col => {
      sheet.deleteColumn(col + 1);
    });
    
    // Recalcular headers después de borrar
    const newLastCol = sheet.getLastColumn();
    const newHeaders = sheet.getRange(1, 1, 1, newLastCol).getValues()[0];
  }
  
  // PASO 3: Añadir nuevas columnas al final
  const nuevaCol = sheet.getLastColumn() + 1;
  
  sheet.getRange(1, nuevaCol).setValue('SEGMENTO_BP');
  sheet.getRange(1, nuevaCol + 1).setValue('PRODUCTO_PPAL_NN');
  sheet.getRange(1, nuevaCol + 2).setValue('ES_AUTONOMO');
  
  // Formatear headers
  sheet.getRange(1, nuevaCol, 1, 3)
    .setFontWeight('bold')
    .setBackground('#FF6B35')
    .setFontColor('#FFFFFF')
    .setHorizontalAlignment('center');
  
  // PASO 4: Construir fórmulas dinámicas
  const letraCumple = columnToLetter(colCumpleaños + 1);
  const letraBP = colBuyerPersona !== -1 ? columnToLetter(colBuyerPersona + 1) : '';
  const letraProdNN = colProductoNN !== -1 ? columnToLetter(colProductoNN + 1) : '';
  const letraProdActuales = colProductosActuales !== -1 ? columnToLetter(colProductosActuales + 1) : '';
  const letraSegmento = columnToLetter(nuevaCol);
  
  // FÓRMULA 1: SEGMENTO_BP (detección automática de buyer persona)
  let formulaSegmento = `=SI(ESVACIO(${letraCumple}2),"S0 - Sin datos",`;
  
  // Detectar autónomo (si existe columna Buyer Persona o Productos actuales)
  if (letraBP || letraProdActuales) {
    const condicionesAutonomo = [];
    if (letraBP) {
      condicionesAutonomo.push(`REGEXMATCH(SUPERIOR(${letraBP}2),"AUTON[OÓ]M")`);
    }
    if (letraProdActuales) {
      condicionesAutonomo.push(`REGEXMATCH(SUPERIOR(${letraProdActuales}2),"NEGOCIO")`);
    }
    formulaSegmento += `SI(O(${condicionesAutonomo.join(',')}),"S3A - Autónomo",`;
  }
  
  // Segmentación por edad
  formulaSegmento += `SI((HOY()-${letraCumple}2)/365.25>=65,"S5 - Senior",`;
  formulaSegmento += `SI((HOY()-${letraCumple}2)/365.25>=50,"S4 - Planificador",`;
  formulaSegmento += `SI((HOY()-${letraCumple}2)/365.25>=35,"S3 - Protector",`;
  formulaSegmento += `SI((HOY()-${letraCumple}2)/365.25>=25,"S2 - Constructor",`;
  formulaSegmento += `SI((HOY()-${letraCumple}2)/365.25<25,"S1 - Joven",`;
  formulaSegmento += `"S0 - Sin datos")))))))`;
  
  if (letraBP || letraProdActuales) {
    formulaSegmento += ')';
  }
  
  // FÓRMULA 2: PRODUCTO_PPAL_NN (según segmento)
  const formulaProducto = `=SI(${letraSegmento}2="S5 - Senior","Contigo Senior + AGE",` +
    `SI(${letraSegmento}2="S4 - Planificador","Plan Creciente SIALP",` +
    `SI(${letraSegmento}2="S3A - Autónomo","Contigo Autónomo + PPSA",` +
    `SI(${letraSegmento}2="S3 - Protector","Plan Salud+Vida",` +
    `SI(${letraSegmento}2="S2 - Constructor","Contigo Familia + Hipoteca",` +
    `SI(${letraSegmento}2="S1 - Joven","Contigo Familia",` +
    `"— Actualizar datos —"))))))`;
  
  // FÓRMULA 3: ES_AUTONOMO
  const formulaAutonomo = `=SI(${letraSegmento}2="S3A - Autónomo","SÍ","NO")`;
  
  // PASO 5: Aplicar fórmulas
  sheet.getRange(2, nuevaCol).setFormula(formulaSegmento);
  sheet.getRange(2, nuevaCol + 1).setFormula(formulaProducto);
  sheet.getRange(2, nuevaCol + 2).setFormula(formulaAutonomo);
  
  // Copiar a todas las filas
  if (lastRow > 2) {
    sheet.getRange(2, nuevaCol, 1, 3).copyTo(
      sheet.getRange(3, nuevaCol, lastRow - 2, 3),
      SpreadsheetApp.CopyPasteType.PASTE_FORMULA
    );
  }
  
  // PASO 6: Formatear
  sheet.getRange(2, nuevaCol, lastRow - 1, 1)
    .setHorizontalAlignment('center')
    .setFontWeight('bold');
  
  sheet.getRange(2, nuevaCol + 1, lastRow - 1, 1)
    .setHorizontalAlignment('left');
  
  sheet.getRange(2, nuevaCol + 2, lastRow - 1, 1)
    .setHorizontalAlignment('center');
  
  // Aplicar formato condicional
  aplicarFormatoCondicionalSegmento(sheet, nuevaCol, lastRow);
  
  // Ajustar anchos
  sheet.setColumnWidth(nuevaCol, 150);
  sheet.setColumnWidth(nuevaCol + 1, 200);
  sheet.setColumnWidth(nuevaCol + 2, 120);
  
  // Mensaje final
  SpreadsheetApp.getUi().alert(
    '✅ SEGMENTACIÓN COMPLETADA V2',
    `Se han añadido 3 columnas:\n\n` +
    `• Columna ${columnToLetter(nuevaCol)}: SEGMENTO_BP\n` +
    `• Columna ${columnToLetter(nuevaCol + 1)}: PRODUCTO_PPAL_NN\n` +
    `• Columna ${columnToLetter(nuevaCol + 2)}: ES_AUTONOMO\n\n` +
    `Fórmulas aplicadas a ${lastRow - 1} contactos.\n\n` +
    `Columnas antiguas con #ERROR eliminadas.`,
    SpreadsheetApp.getUi().ButtonSet.OK
  );
  
  // Generar estadísticas
  generarEstadisticasSegmento(sheet, nuevaCol, lastRow);
}

/**
 * Busca una columna por nombre (parcial)
 */
function buscarColumna(headers, nombreBuscado) {
  for (let i = 0; i < headers.length; i++) {
    const headerStr = String(headers[i]).toUpperCase();
    if (headerStr.includes(nombreBuscado.toUpperCase())) {
      return i;
    }
  }
  return -1;
}

/**
 * Aplica formato condicional a la columna SEGMENTO_BP
 */
function aplicarFormatoCondicionalSegmento(sheet, colSegmento, lastRow) {
  const range = sheet.getRange(2, colSegmento, lastRow - 1, 1);
  
  const colores = {
    'S0 - Sin datos': '#E0E0E0',
    'S1 - Joven': '#B3E5FC',
    'S2 - Constructor': '#81C784',
    'S3 - Protector': '#FFD54F',
    'S3A - Autónomo': '#FF8A65',
    'S4 - Planificador': '#9575CD',
    'S5 - Senior': '#EF5350'
  };
  
  const nuevasReglas = [];
  
  for (const [segmento, color] of Object.entries(colores)) {
    const rule = SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo(segmento)
      .setBackground(color)
      .setRanges([range])
      .build();
    nuevasReglas.push(rule);
  }
  
  const rules = sheet.getConditionalFormatRules();
  sheet.setConditionalFormatRules([...rules, ...nuevasReglas]);
}

/**
 * Genera estadísticas de segmentación
 */
function generarEstadisticasSegmento(sheet, colSegmento, lastRow) {
  const valores = sheet.getRange(2, colSegmento, lastRow - 1, 1).getValues();
  
  const stats = {};
  valores.forEach(row => {
    const segmento = row[0];
    stats[segmento] = (stats[segmento] || 0) + 1;
  });
  
  Logger.log('📊 ESTADÍSTICAS DE SEGMENTACIÓN:');
  Logger.log('═'.repeat(50));
  
  const orden = [
    'S5 - Senior',
    'S4 - Planificador',
    'S3 - Protector',
    'S3A - Autónomo',
    'S2 - Constructor',
    'S1 - Joven',
    'S0 - Sin datos'
  ];
  
  let total = 0;
  orden.forEach(segmento => {
    const count = stats[segmento] || 0;
    total += count;
    if (count > 0) {
      Logger.log(`${segmento.padEnd(25)} ${count.toString().padStart(4)} contactos`);
    }
  });
  
  Logger.log('═'.repeat(50));
  Logger.log(`TOTAL:${' '.repeat(20)}${total} contactos`);
}

/**
 * Convierte número de columna a letra
 */
function columnToLetter(column) {
  let temp;
  let letter = '';
  while (column > 0) {
    temp = (column - 1) % 26;
    letter = String.fromCharCode(temp + 65) + letter;
    column = (column - temp - 1) / 26;
  }
  return letter;
}

/**
 * Menú personalizado
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🟠 NN Segmentación V2')
    .addItem('📊 Añadir Segmentación (V2 Corregida)', 'añadirSegmentacionCRM_v2')
    .addItem('📈 Ver Estadísticas', 'mostrarEstadisticas')
    .addToUi();
}

/**
 * Muestra estadísticas
 */
function mostrarEstadisticas() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('CRM MAESTRO');
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Error: No se encuentra la pestaña "CRM MAESTRO"');
    return;
  }
  
  const headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const colSegmento = headerRow.indexOf('SEGMENTO_BP');
  
  if (colSegmento === -1) {
    SpreadsheetApp.getUi().alert(
      'Segmentación no encontrada',
      'Primero ejecuta "Añadir Segmentación (V2 Corregida)"',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    return;
  }
  
  const lastRow = sheet.getLastRow();
  const valores = sheet.getRange(2, colSegmento + 1, lastRow - 1, 1).getValues();
  
  const stats = {};
  valores.forEach(row => {
    const segmento = row[0];
    stats[segmento] = (stats[segmento] || 0) + 1;
  });
  
  let mensaje = '📊 ESTADÍSTICAS DE SEGMENTACIÓN\n\n';
  
  const orden = [
    'S5 - Senior',
    'S4 - Planificador',
    'S3 - Protector',
    'S3A - Autónomo',
    'S2 - Constructor',
    'S1 - Joven',
    'S0 - Sin datos'
  ];
  
  let total = 0;
  orden.forEach(segmento => {
    const count = stats[segmento] || 0;
    total += count;
    if (count > 0) {
      mensaje += `${segmento}: ${count} contactos\n`;
    }
  });
  
  mensaje += `\nTOTAL: ${total} contactos`;
  
  SpreadsheetApp.getUi().alert('Estadísticas CRM NN', mensaje, SpreadsheetApp.getUi().ButtonSet.OK);
}
