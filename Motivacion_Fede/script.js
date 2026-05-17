// ==========================================
// CONFIGURACIÓN DE USUARIO (CAMBIA ESTO)
// ==========================================
const USER_CONFIG = {
    name: "Fede Fontanals",
    initials: "FF",
    sign: "LEO",
    priority: "FEDE JR.",
    stats: {
        s1: "Salud: 🔥",
        s2: "Fede Jr.: 💎",
        s3: "IA: 🚀"
    },
    quotes: {
        main: "¿QUIÉN DECIDES SER HOY?",
        secondary: "EL TRABAJO MÁS DURO ES NO RENDIRSE"
    },
    sheets_url: "https://script.google.com/macros/s/AKfycbyZHqOOO5BmKEYps8oE1LWTZ3AWYKUVBWbwfEzTItxu_YXB31yLcL1DXs0SaT-AFAzVFw/exec" // PEGA AQUÍ LA URL DE TU WEB APP DE GOOGLE SHEETS
};

// ==========================================
// LÓGICA DEL HUD
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    try {
        initHUD();
        loadHistory();
        setupNavigation();
        setupAudioEvents();
        initHolidays(); // Cargar calendario y próximo festivo
    } catch (e) {
        console.error("HUD Init Error:", e);
    }
});

function initHUD() {
    const updateEl = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val;
    };

    updateEl('user-name-display', USER_CONFIG.name);
    updateEl('initials-display', USER_CONFIG.initials);
    updateEl('user-sign', USER_CONFIG.sign);
    updateEl('priority-label', USER_CONFIG.priority);
    updateEl('main-quote', USER_CONFIG.quotes.main);
    updateEl('sec-quote', USER_CONFIG.quotes.secondary);
    
    updateEl('stat-1', USER_CONFIG.stats.s1);
    updateEl('stat-2', USER_CONFIG.stats.s2);
    updateEl('stat-3', USER_CONFIG.stats.s3);
}

// NAVEGACIÓN
function setupNavigation() {
    const btnToday = document.getElementById('nav-today');
    const btnHistory = document.getElementById('nav-history');
    const viewToday = document.getElementById('view-today');
    const viewHistory = document.getElementById('view-history');

    if (!btnToday || !btnHistory) return;

    btnToday.addEventListener('click', () => {
        btnToday.classList.add('active');
        btnHistory.classList.remove('active');
        viewToday.classList.remove('hidden');
        viewHistory.classList.add('hidden');
    });

    btnHistory.addEventListener('click', () => {
        btnHistory.classList.add('active');
        btnToday.classList.remove('active');
        viewHistory.classList.remove('hidden');
        viewToday.classList.add('hidden');
        renderHistory();
    });
}

// PERSISTENCIA DE DATOS
function getDiary() {
    try {
        const data = localStorage.getItem('fede_diary');
        return data ? JSON.parse(data) : {};
    } catch (e) {
        return {};
    }
}

function saveDiary(diary) {
    localStorage.setItem('fede_diary', JSON.stringify(diary));
    updateMissionCount();
}

function getTodayStr() {
    return new Date().toISOString().split('T')[0];
}

// PROTOCOLO LEO
let isLeoActive = false;

const LEO_MANTRAS = [
    "\"La vida no te pregunta quién eras. Te pregunta quién decides ser hoy.\"",
    "\"El pasado no juega este partido. ¡Mañana será HOY!\"",
    "\"Tus probabilidades de éxito aumentan cada vez que insistes. ¡NO TE RESIGNES!\"",
    "\"Ganar control es el resultado del conocimiento y la experiencia.\"",
    "\"Abonar la tierra y enterrar semillas. Ese es tu proceso comercial.\""
];

function toggleLeoProtocol() {
    isLeoActive = !isLeoActive;
    const card = document.getElementById('leo-card');
    const label = document.getElementById('identity-label');
    const icon = document.getElementById('leo-icon');
    const tacticalPanel = document.getElementById('leo-tactical-panel');
    
    if (isLeoActive) {
        card.classList.remove('protocol-off');
        card.classList.add('highlight', 'leo-active-glow');
        label.innerText = "NIVEL MÁXIMO";
        label.style.color = "var(--text-primary)";
        icon.style.filter = "none";
        
        // Mostrar panel táctico militar
        if (tacticalPanel) {
            tacticalPanel.classList.remove('hidden');
            // Cargar mantra dinámico aleatorio
            const randomMantra = LEO_MANTRAS[Math.floor(Math.random() * LEO_MANTRAS.length)];
            const mantraEl = document.getElementById('leo-dynamic-mantra');
            if (mantraEl) mantraEl.innerText = randomMantra;
        }
        
        // TRANSFORMACIÓN SUPER SAIYAN LEO
        document.body.classList.add('super-leo-mode');
        
        // Efecto de Explosión de Energía (Flash Goku)
        const flash = document.createElement('div');
        flash.className = 'flash-bang';
        document.body.appendChild(flash);
        setTimeout(() => flash.remove(), 1000);

        playTrack('Mañana será HOY.mp3'); // Auto-play mantra track
    } else {
        card.classList.remove('highlight', 'leo-active-glow');
        card.classList.add('protocol-off');
        label.innerText = "Activar LEO";
        label.style.color = "#666";
        icon.style.filter = "grayscale(1)";
        
        // Ocultar panel táctico
        if (tacticalPanel) {
            tacticalPanel.classList.add('hidden');
        }
        
        document.body.classList.remove('super-leo-mode');
    }
}

function saveMorning() {
    const goal = document.getElementById('morning-goal')?.value;
    const impactsGoal = document.getElementById('impacts-goal')?.value;
    const stepGoal = document.getElementById('step-goal')?.value;
    const phase8ia = document.getElementById('phase-8ia-goal')?.value;
    const date = getTodayStr();

    if (!isLeoActive) {
        alert("COMANDANTE: Active el Protocolo LEO (tarjeta central) antes de despegar.");
        return;
    }

    if (!goal) {
        alert("Comandante, defina su meta de hoy primero.");
        return;
    }

    const diary = getDiary();
    if (!diary[date]) diary[date] = {};
    
    diary[date].morningGoal = goal;
    diary[date].impactsGoal = impactsGoal;
    diary[date].stepGoal = stepGoal;
    diary[date].phase8ia = phase8ia;
    saveDiary(diary);
    
    alert("DESPEGUE REGISTRADO. Su Foco Hoy: " + phase8ia);

    // Enviar a la nube en tiempo real
    if (USER_CONFIG.sheets_url) {
        const memoryStatusEl = document.getElementById('memory-status');
        if (memoryStatusEl) memoryStatusEl.innerText = "NUBE (Sincronizando...)";
        sendToSheets({
            date: date,
            morningGoal: goal,
            phase8ia: phase8ia,
            stepGoal: stepGoal,
            impactsGoal: impactsGoal
        });
    }
}

function saveEvening() {
    const reflection = document.getElementById('evening-reflection')?.value;
    const impactsActual = document.getElementById('impacts-actual')?.value;
    const stepsActual = document.getElementById('steps-actual')?.value;
    const abonosActual = document.getElementById('abonos-actual')?.value;
    const date = getTodayStr();

    if (!reflection) {
        alert("Haga balance de su proceso antes de cerrar.");
        return;
    }

    const diary = getDiary();
    if (!diary[date]) diary[date] = {};
    
    diary[date].eveningReflection = reflection;
    diary[date].impactsActual = impactsActual;
    diary[date].stepsActual = stepsActual;
    diary[date].abonosActual = abonosActual;
    saveDiary(diary);
    
    alert("MISIÓN CERRADA. Mañana volverá a llamarse hoy.");
    renderHistory();
    
    // Enviar a la nube si hay URL
    if (USER_CONFIG.sheets_url) {
        document.getElementById('memory-status').innerText = "NUBE (Sincronizando...)";
        sendToSheets({
            date: date,
            morningGoal: diary[date].morningGoal,
            eveningReflection: reflection,
            impactsActual: impactsActual,
            impactsGoal: diary[date].impactsGoal,
            stepGoal: diary[date].stepGoal,
            stepsActual: stepsActual,
            phase8ia: diary[date].phase8ia,
            abonosActual: abonosActual
        });
    }
}

function sendToSheets(data) {
    fetch(USER_CONFIG.sheets_url, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify(data)
    }).then(() => {
        console.log("Datos enviados a Sheets");
        const statusEl = document.getElementById('memory-status');
        if (statusEl) statusEl.innerText = "NUBE (OK)";
    }).catch(error => {
        console.error('Error al sincronizar con Sheets:', error);
        const statusEl = document.getElementById('memory-status');
        if (statusEl) statusEl.innerText = "ERROR NUBE";
    });
}

function renderHistory() {
    const diary = getDiary();
    const historyList = document.getElementById('history-list');
    if (!historyList) return;
    
    historyList.innerHTML = '';

    const dates = Object.keys(diary).sort((a, b) => b.localeCompare(a));
    if (dates.length === 0) {
        historyList.innerHTML = '<div class="card-input" style="text-align:center">Bitácora vacía.</div>';
        return;
    }

    dates.forEach(date => {
        const entry = diary[date];
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="date">${formatDate(date)}</div>
            <div>
                <b style="color:var(--gold); font-size:0.7rem;">META / FOCO: ${entry.phase8ia || 'N/A'}</b>
                <div class="text-col">${entry.morningGoal || 'Sin registro'}</div>
            </div>
            <div>
                <b style="color:var(--orange); font-size:0.7rem;">REFLEXIÓN:</b>
                <div class="text-col">${entry.eveningReflection || 'Pendiente...'}</div>
            </div>
            <div>
                <div class="text-col" style="font-size:0.7rem;"><b>PASOS:</b> ${entry.stepsActual || 0} / ${entry.stepGoal || 0}</div>
                <div class="text-col" style="font-size:0.7rem;"><b>IMPACTOS:</b> ${entry.impactsActual || 0} / ${entry.impactsGoal || 0}</div>
                <div class="text-col" style="font-size:0.7rem; color:var(--red);"><b>NOES (Abono):</b> ${entry.abonosActual || 0}</div>
            </div>
        `;
        historyList.appendChild(item);
    });
}

function formatDate(dateStr) {
    const options = { weekday: 'long', day: 'numeric', month: 'long' };
    return new Date(dateStr).toLocaleDateString('es-ES', options);
}

function updateMissionCount() {
    const diary = getDiary();
    const el = document.getElementById('mission-count');
    if (el) el.innerText = Object.keys(diary).length;
}

function loadHistory() {
    updateMissionCount();
    const diary = getDiary();
    const today = getTodayStr();
    if (diary[today]) {
        if (document.getElementById('morning-goal')) document.getElementById('morning-goal').value = diary[today].morningGoal || '';
        if (document.getElementById('impacts-goal')) document.getElementById('impacts-goal').value = diary[today].impactsGoal || 20;
        if (document.getElementById('step-goal')) document.getElementById('step-goal').value = diary[today].stepGoal || 11000;
        if (document.getElementById('phase-8ia-goal')) document.getElementById('phase-8ia-goal').value = diary[today].phase8ia || 'Prospección / Leads';
        
        if (document.getElementById('evening-reflection')) document.getElementById('evening-reflection').value = diary[today].eveningReflection || '';
        if (document.getElementById('impacts-actual')) document.getElementById('impacts-actual').value = diary[today].impactsActual || '';
        if (document.getElementById('steps-actual')) document.getElementById('steps-actual').value = diary[today].stepsActual || '';
        if (document.getElementById('abonos-actual')) document.getElementById('abonos-actual').value = diary[today].abonosActual || '';
    }
}

// SISTEMA DE AUDIO
const mainAudio = document.getElementById('main-audio');
const playPauseBtn = document.getElementById('play-pause-btn');
const visualizer = document.getElementById('hud-visualizer');
const trackLabel = document.getElementById('current-track');

function playTrack(fileName) {
    if (!mainAudio) return;
    mainAudio.src = fileName;
    mainAudio.play();
    if (trackLabel) trackLabel.innerText = fileName.replace('.mp3', '').replace('.MP3', '').toUpperCase();
    if (playPauseBtn) playPauseBtn.innerText = '⏸';
    if (visualizer) visualizer.classList.add('playing');
}

function toggleAudio() {
    if (!mainAudio) return;
    if (mainAudio.paused) {
        if (!mainAudio.src) playTrack('Mañana será HOY.mp3');
        else {
            mainAudio.play();
            if (playPauseBtn) playPauseBtn.innerText = '⏸';
            if (visualizer) visualizer.classList.add('playing');
        }
    } else {
        mainAudio.pause();
        if (playPauseBtn) playPauseBtn.innerText = '▶';
        if (visualizer) visualizer.classList.remove('playing');
    }
}

function setupAudioEvents() {
    if (mainAudio) {
        mainAudio.onended = () => {
            if (playPauseBtn) playPauseBtn.innerText = '▶';
            if (visualizer) visualizer.classList.remove('playing');
        };
    }
}

// ==========================================
// CALENDARIO DE FESTIVOS - C. VALENCIANA 2026
// ==========================================
const VALENCIAN_HOLIDAYS_2026 = [
    { date: "2026-01-01", name: "Año Nuevo 🥂", day: "Jueves", type: "Nacional" },
    { date: "2026-01-06", name: "Día de Reyes (Epifanía) 👑", day: "Martes", type: "Nacional" },
    { date: "2026-03-19", name: "Día de San José 🔥 (Fallas)", day: "Jueves", type: "Autonómico" },
    { date: "2026-04-03", name: "Viernes Santo ⛪", day: "Viernes", type: "Nacional" },
    { date: "2026-04-06", name: "Lunes de Pascua 🥚", day: "Lunes", type: "Autonómico" },
    { date: "2026-05-01", name: "Fiesta del Trabajo 🛠️", day: "Viernes", type: "Nacional" },
    { date: "2026-06-24", name: "Día de San Juan 🏖️", day: "Miércoles", type: "Autonómico" },
    { date: "2026-08-15", name: "Asunción de la Virgen 🌌", day: "Sábado", type: "Nacional" },
    { date: "2026-10-09", name: "Día de la Comunidad Valenciana 🦁", day: "Viernes", type: "Autonómico" },
    { date: "2026-10-12", name: "Fiesta Nacional de España 🇪🇸", day: "Lunes", type: "Nacional" },
    { date: "2026-12-08", name: "La Inmaculada Concepción 🌟", day: "Martes", type: "Nacional" },
    { date: "2026-12-25", name: "Natividad del Señor (Navidad) 🎄", day: "Viernes", type: "Nacional" }
];

function initHolidays() {
    const todayStr = getTodayStr(); // yyyy-MM-dd
    const today = new Date(todayStr);
    
    // Buscar próximo festivo
    let nextHoliday = null;
    for (const h of VALENCIAN_HOLIDAYS_2026) {
        const hDate = new Date(h.date);
        if (hDate >= today) {
            nextHoliday = h;
            break;
        }
    }
    
    // Fallback por si pasa el 2026
    if (!nextHoliday) {
        nextHoliday = { date: "2027-01-01", name: "Año Nuevo 🥂", day: "Viernes", type: "Nacional" };
    }
    
    // Calcular días restantes
    const hDate = new Date(nextHoliday.date);
    const diffTime = hDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    let countdownText = "";
    if (diffDays === 0) {
        countdownText = "¡HOY ES FESTIVO! ☀️";
        const mantraEl = document.getElementById('leo-dynamic-mantra');
        if (mantraEl) {
            mantraEl.innerText = `[ ALERTA LEO: DÍA FESTIVO EN VALENCIA ] Hoy es ${nextHoliday.name}. ¡Soporte Fede Jr. 💎 y Salud 🔥 al 100%!`;
        }
    } else if (diffDays === 1) {
        countdownText = "(¡Mañana es festivo!)";
    } else {
        countdownText = `(Faltan ${diffDays} días)`;
    }
    
    // Formatear fecha para el widget (ej. "24 de junio")
    const options = { day: 'numeric', month: 'long' };
    const formattedDate = hDate.toLocaleDateString('es-ES', options);
    
    const nameEl = document.getElementById('next-holiday-name');
    const countEl = document.getElementById('next-holiday-countdown');
    
    if (nameEl) nameEl.innerText = `${formattedDate} - ${nextHoliday.name}`;
    if (countEl) countEl.innerText = countdownText;
    
    // Renderizar tabla
    renderHolidayTable(nextHoliday.date);
}

function renderHolidayTable(nextHolidayDate) {
    const tableBody = document.getElementById('holiday-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = VALENCIAN_HOLIDAYS_2026.map(h => {
        const hDate = new Date(h.date);
        const options = { day: 'numeric', month: 'long' };
        const formattedDate = hDate.toLocaleDateString('es-ES', options);
        const isNext = h.date === nextHolidayDate;
        
        return `
            <tr class="${isNext ? 'highlighted' : ''}">
                <td><b>${formattedDate}</b></td>
                <td>${h.day}</td>
                <td>${h.name} ${isNext ? '🌟' : ''}</td>
                <td><span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 3px; background: rgba(255,255,255,0.05); color: ${h.type === 'Nacional' ? 'var(--gold)' : 'var(--orange)'};">${h.type}</span></td>
            </tr>
        `;
    }).join('');
}

// MODAL DE FESTIVOS
function openHolidayModal() {
    const modal = document.getElementById('holiday-modal');
    if (modal) modal.classList.remove('hidden');
}

function closeHolidayModal() {
    const modal = document.getElementById('holiday-modal');
    if (modal) modal.classList.add('hidden');
}

// ==========================================
// 🧘‍♂️ SISTEMA INTERACTIVO - ESCUDO MENTAL
// ==========================================

// 1. RESET EMOCIONAL (RESPIRACIÓN TÁCTICA 1 MINUTO)
let breathingInterval = null;
let resetSecondsLeft = 60;
let boxSeconds = 0;

function openResetModal() {
    const modal = document.getElementById('reset-emocional-modal');
    if (!modal) return;
    
    modal.classList.remove('hidden');
    
    // Iniciar audio de resistencia
    const audioEl = document.getElementById('main-audio');
    if (audioEl) {
        audioEl.src = 'NO TE RESIGNES.MP3';
        audioEl.volume = 1.0;
        audioEl.play().catch(e => console.log("Audio bloqueado por navegador", e));
    }
    
    // Iniciar temporizadores de respiración box breathing
    resetSecondsLeft = 60;
    boxSeconds = 0;
    document.getElementById('breathing-timer').innerText = "60s";
    
    // Establecer primer frame
    const circle = document.getElementById('breathing-circle');
    const textEl = document.getElementById('breathing-state-text');
    if (circle && textEl) {
        circle.className = 'breathing-circle inhale';
        textEl.innerText = "INHALA...";
    }
    
    // Loop principal (1 tick por segundo)
    clearInterval(breathingInterval);
    breathingInterval = setInterval(() => {
        resetSecondsLeft--;
        document.getElementById('breathing-timer').innerText = resetSecondsLeft + "s";
        
        boxSeconds = (boxSeconds + 1) % 16;
        
        if (boxSeconds >= 0 && boxSeconds < 4) {
            circle.className = 'breathing-circle inhale';
            textEl.innerText = "INHALA...";
        } else if (boxSeconds >= 4 && boxSeconds < 8) {
            circle.className = 'breathing-circle hold';
            textEl.innerText = "MANTÉN...";
        } else if (boxSeconds >= 8 && boxSeconds < 12) {
            circle.className = 'breathing-circle exhale';
            textEl.innerText = "EXHALA...";
        } else {
            circle.className = 'breathing-circle rest';
            textEl.innerText = "MANTÉN...";
        }
        
        if (resetSecondsLeft <= 0) {
            clearInterval(breathingInterval);
            alert("🛡️ CRISIS CONTROLADA. Comandante Federico: Mantente en silencio y sigue en control. Eres el dueño absoluto de tus respuestas.");
            closeResetModal();
        }
    }, 1000);
}

function closeResetModal() {
    const modal = document.getElementById('reset-emocional-modal');
    if (modal) modal.classList.add('hidden');
    clearInterval(breathingInterval);
    const audioEl = document.getElementById('main-audio');
    if (audioEl) audioEl.pause();
}

// ==========================================
// 2. MEDITACIÓN ESCUDO LIONHEART (3 MINUTOS)
// ==========================================
let meditationTimerInterval = null;
let meditationSecondsLeft = 180;
let isMeditationRunning = false;

function openMeditationModal() {
    const modal = document.getElementById('meditation-modal');
    if (modal) modal.classList.remove('hidden');
    
    // Reset estado
    clearInterval(meditationTimerInterval);
    isMeditationRunning = false;
    meditationSecondsLeft = 180;
    document.getElementById('meditation-timer').innerText = "03:00";
    document.getElementById('meditation-step-title').innerText = "FASE 1: CONCENTRACIÓN Y CALMA";
    document.getElementById('meditation-step-desc').innerText = "Respira hondo. Cierra los ojos. Conecta con tu fuerza interior. Siente el silencio del cockpit. El mundo exterior es solo ruido inútil.";
    
    const btn = document.getElementById('btn-start-meditation');
    if (btn) btn.innerText = "INICIAR BLINDAJE MENTAL";
}

function closeMeditationModal() {
    const modal = document.getElementById('meditation-modal');
    if (modal) modal.classList.add('hidden');
    clearInterval(meditationTimerInterval);
    isMeditationRunning = false;
    const audioEl = document.getElementById('main-audio');
    if (audioEl) audioEl.pause();
}

function startMeditation() {
    const btn = document.getElementById('btn-start-meditation');
    if (!btn) return;
    
    if (isMeditationRunning) {
        // Pausar
        clearInterval(meditationTimerInterval);
        isMeditationRunning = false;
        btn.innerText = "REANUDAR COMBATE MENTAL";
        const audioEl = document.getElementById('main-audio');
        if (audioEl) audioEl.pause();
        return;
    }
    
    isMeditationRunning = true;
    btn.innerText = "PAUSAR MEDITACIÓN";
    
    // 🎵 Iniciar audio de motivación épica
    const audioEl = document.getElementById('main-audio');
    if (meditationSecondsLeft === 180) {
        if (audioEl) {
            audioEl.src = 'Mañana será HOY.mp3';
            audioEl.volume = 1.0; // Volumen al 100%
            audioEl.play().catch(e => console.log("Audio bloqueado por navegador", e));
        }
    } else {
        // Reanudar
        if (audioEl) audioEl.play().catch(e => console.log("Audio bloqueado por navegador", e));
    }
    
    meditationTimerInterval = setInterval(() => {
        meditationSecondsLeft--;
        
        // Formatear minutos y segundos
        const m = Math.floor(meditationSecondsLeft / 60);
        const s = meditationSecondsLeft % 60;
        document.getElementById('meditation-timer').innerText = 
            (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
            
        // Lógica de fases dinámicas
        const titleEl = document.getElementById('meditation-step-title');
        const descEl = document.getElementById('meditation-step-desc');
        
        if (meditationSecondsLeft === 120) {
            // Minuto 2
            titleEl.innerText = "FASE 2: EL ESCUDO DE COMBATE LEO";
            descEl.innerText = "Visualiza cualquier provocación verbal como pequeñas motas de polvo chocando y disolviéndose contra un escudo impenetrable de luz dorada. Tu calma es tu victoria legal.";
        } else if (meditationSecondsLeft === 60) {
            // Minuto 3
            titleEl.innerText = "FASE 3: FEDE JR. 💎 Y PROPÓSITO";
            descEl.innerText = "Enfoca tu mente en tu mayor motivación: Fede Jr. 💎 y tu éxito físico y comercial. Hoy actúas con control de mando. Abre los ojos. Estás listo.";
        } else if (meditationSecondsLeft <= 0) {
            // Fin
            clearInterval(meditationTimerInterval);
            isMeditationRunning = false;
            btn.innerText = "INICIAR BLINDAJE MENTAL";
            meditationSecondsLeft = 180;
            document.getElementById('meditation-timer').innerText = "03:00";
            if (audioEl) audioEl.pause();
            
            setTimeout(() => {
                alert("🦁 MEDITACIÓN COMPLETADA. Armadura estoica LEO al 100% para hoy. Fede Jr. 💎 te necesita en control.");
                closeMeditationModal();
            }, 500);
        }
    }, 1000);
}

// 3. ABRIR BÓVEDA DE AUDIOS (GOOGLE DRIVE)
function openAudioVault() {
    window.open("https://drive.google.com/drive/folders/1Wkfso8GEG-_xe89Gly_V7b0VD8LWtv38", "_blank");
}

// Cerrar cualquier modal al hacer clic fuera del contenido
window.addEventListener('click', (event) => {
    const holidayModal = document.getElementById('holiday-modal');
    const resetModal = document.getElementById('reset-emocional-modal');
    const medModal = document.getElementById('meditation-modal');
    
    if (event.target === holidayModal) {
        closeHolidayModal();
    }
    if (event.target === resetModal) {
        closeResetModal();
    }
    if (event.target === medModal) {
        closeMeditationModal();
    }
});
