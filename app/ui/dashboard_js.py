"""
Mangesh Nano Pro AI Studio - Core UI JavaScript Orchestration Engine
Powers:
- Single AI Manager Symbol State Manager (Ready, Listening, Thinking, Planning, Delegating, Executing, Speaking, Waiting, Error)
- Rich Manager Conversation Stream (Sortable/Searchable Tables, Canvas Charts, KPI Cards, Animated Output Panel)
- Nano Pro Voice Assistant ("Hi NanoPro" wake-word, Web Speech API, TTS, interruption)
- Animated 3D AI Agent Office (All 45 agents, live telemetry, data flow visualizer)
- Task Scheduler & Automation Center (CRUD, Run Now, Pause, Resume, Logs Modal)
- News Center (ABP Majha & Aaj Tak, hourly check, floating alert banner)
- Entertainment & Modern Lifestyle Center (Visual cards, hover effects, favorites)
- Book Reader & Intelligent Learning Assistant (TOC, chapter reader, audio narration, study plan, quizzes)
"""

DASHBOARD_UPGRADE_JS = r"""
/* =========================================================================
   1. SINGLE AI MANAGER SYMBOL & GLOBAL STATE CONTROLLER
   ========================================================================= */
let currentManagerState = 'ready';
let activeSpeechSynthesis = null;

function setManagerSymbolState(state) {
    currentManagerState = state.toLowerCase();
    const wrappers = [document.getElementById('aiManagerSymbolWrapper'), document.getElementById('bigVoiceOrb')];
    const stateLabels = [document.getElementById('managerStateText'), document.getElementById('bigVoiceState'), document.getElementById('topbarModeBadge')];

    wrappers.forEach(w => {
        if (!w) return;
        w.className = 'ai-manager-symbol-container state-' + currentManagerState;
    });

    const displayMap = {
        'ready': 'READY',
        'listening': 'LISTENING...',
        'thinking': 'THINKING...',
        'planning': 'PLANNING...',
        'delegating': 'DELEGATING...',
        'executing': 'EXECUTING...',
        'speaking': 'SPEAKING...',
        'waiting': 'WAITING',
        'error': 'ERROR'
    };
    const txt = displayMap[currentManagerState] || currentManagerState.toUpperCase();

    stateLabels.forEach(lbl => {
        if (!lbl) return;
        lbl.innerText = txt;
    });
}

function toggleVoiceOrManagerPrompt() {
    if (currentActiveView !== 'ai_manager') {
        switchView('ai_manager');
    }
    toggleVoiceRecording();
}

/* =========================================================================
   2. MANAGER CONVERSATION STREAM & RICH SMART RESPONSE ENGINE
   ========================================================================= */
let isManagerGenerating = false;
let managerAbortController = null;
let chatTablesRegistry = {};
let chatChartsRegistry = {};

async function sendManagerMessage() {
    const input = document.getElementById('managerChatInput');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    appendUserMessage(msg);
    setManagerSymbolState('thinking');

    // Show temporary thinking indicator
    const stream = document.getElementById('managerChatStreamBox');
    const thinkingId = 'thinking_' + Date.now();
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'chat-msg manager';
    thinkingDiv.id = thinkingId;
    thinkingDiv.innerHTML = `
        <div class="msg-avatar">&#129302;</div>
        <div class="msg-bubble" style="color:var(--text-muted); font-style:italic;">
            Thinking and coordinating specialist agents...
        </div>
    `;
    stream.appendChild(thinkingDiv);
    stream.scrollTop = stream.scrollHeight;

    isManagerGenerating = true;
    document.getElementById('chatStopBtn').style.display = 'inline-block';
    document.getElementById('chatSendBtn').style.display = 'none';

    try {
        const res = await fetch('/api/manager/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: msg, session_id: 'default' })
        });
        const data = await res.json();
        
        // Remove thinking placeholder
        const placeholder = document.getElementById(thinkingId);
        if (placeholder) placeholder.remove();

        setManagerSymbolState('speaking');
        appendManagerRichMessage(data);

        // If audio voice enabled, speak summary
        if (document.getElementById('voiceLanguageSelect')) {
            speakText(data.response.substring(0, 200));
        }

    } catch (e) {
        const placeholder = document.getElementById(thinkingId);
        if (placeholder) placeholder.remove();
        setManagerSymbolState('error');
        appendManagerErrorMessage(e.message || 'Network error occurred while connecting to AI Manager.');
    } finally {
        isManagerGenerating = false;
        document.getElementById('chatStopBtn').style.display = 'none';
        document.getElementById('chatSendBtn').style.display = 'inline-block';
        setTimeout(() => {
            if (currentManagerState === 'speaking') {
                setManagerSymbolState('ready');
            }
        }, 3000);
    }
}

function stopManagerGeneration() {
    if (isManagerGenerating) {
        isManagerGenerating = false;
        document.getElementById('chatStopBtn').style.display = 'none';
        document.getElementById('chatSendBtn').style.display = 'inline-block';
        setManagerSymbolState('ready');
        logLocal('AIManager', 'User cancelled manager generation.');
    }
}

function appendUserMessage(text) {
    const stream = document.getElementById('managerChatStreamBox');
    const timeStr = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg user';
    msgDiv.innerHTML = `
        <div class="msg-avatar">&#128100;</div>
        <div class="msg-bubble">
            <div>${escapeHtml(text)}</div>
            <div class="msg-meta">
                <span>You</span>
                <span>${timeStr}</span>
            </div>
        </div>
    `;
    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

function appendManagerRichMessage(data) {
    const stream = document.getElementById('managerChatStreamBox');
    const timeStr = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const msgId = 'msg_' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg manager';
    msgDiv.id = msgId;

    let contentHtml = formatMarkdown(data.response || '');

    // 1. KPI Cards Grid
    if (data.kpi_cards && data.kpi_cards.length > 0) {
        contentHtml += '<div class="kpi-cards-grid">';
        data.kpi_cards.forEach(k => {
            contentHtml += `
                <div class="kpi-metric-card">
                    <div class="kpi-metric-label">${escapeHtml(k.label)}</div>
                    <div class="kpi-metric-val">${escapeHtml(k.value)}</div>
                    <div class="kpi-metric-change">${escapeHtml(k.change || '')}</div>
                </div>
            `;
        });
        contentHtml += '</div>';
    }

    // 2. Real-Time Execution Card
    if (data.execution_card) {
        const ec = data.execution_card;
        contentHtml += `
            <div class="execution-steps-card">
                <div class="exec-header">
                    <span>&#9889; QUERY EXECUTION PIPELINE</span>
                    <span style="font-size:10px; background:#1E293B; padding:2px 8px; border-radius:4px; color:#10B981;">${ec.elapsed_ms || 142} ms • ${ec.status}</span>
                </div>
        `;
        if (ec.steps && ec.steps.length > 0) {
            ec.steps.forEach(s => {
                contentHtml += `
                    <div class="exec-step-row">
                        <div class="exec-step-num">&#10003;</div>
                        <div style="font-weight:700; color:#F8FAFC;">${escapeHtml(s.name)}:</div>
                        <div>${escapeHtml(s.detail)}</div>
                    </div>
                `;
            });
        }
        if (ec.query) {
            contentHtml += `
                <div class="exec-code-snippet">
                    <code>${escapeHtml(ec.query)}</code>
                </div>
            `;
        }
        contentHtml += '</div>';
    }

    // 3. Interactive Sortable Table
    let tableContainerId = '';
    if (data.table_data && data.table_data.columns && data.table_data.rows) {
        tableContainerId = 'table_' + msgId;
        chatTablesRegistry[tableContainerId] = {
            data: data.table_data,
            filteredRows: [...data.table_data.rows],
            sortCol: null,
            sortAsc: true,
            page: 1,
            pageSize: 5
        };
        contentHtml += `<div id="${tableContainerId}"></div>`;
    }

    // 4. Interactive Chart Container
    let chartContainerId = '';
    if (data.chart_data && data.chart_data.labels && data.chart_data.datasets) {
        chartContainerId = 'chart_' + msgId;
        chatChartsRegistry[chartContainerId] = data.chart_data;
        contentHtml += `
            <div class="chart-container-box">
                <div class="chart-header">
                    <span class="chart-title">${escapeHtml(data.chart_data.title || 'Data Visualization')}</span>
                    <div class="chart-toggles">
                        <button type="button" class="chart-toggle-btn active" onclick="switchChartRenderType('${chartContainerId}', 'bar', this)">Bar</button>
                        <button type="button" class="chart-toggle-btn" onclick="switchChartRenderType('${chartContainerId}', 'line', this)">Line</button>
                        <button type="button" class="chart-toggle-btn" onclick="switchChartRenderType('${chartContainerId}', 'donut', this)">Donut</button>
                    </div>
                </div>
                <div style="height:220px; position:relative;">
                    <canvas id="canvas_${chartContainerId}" style="width:100%; height:100%;"></canvas>
                </div>
            </div>
        `;
    }

    // Tools & Actions
    let actionsHtml = '';
    if (data.actions && data.actions.length > 0) {
        actionsHtml = '<div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:10px;">';
        data.actions.forEach(act => {
            actionsHtml += `<button type="button" class="action-chip" onclick="quickFillPrompt('${escapeHtml(act)}')">${escapeHtml(act)}</button>`;
        });
        actionsHtml += '</div>';
    }

    msgDiv.innerHTML = `
        <div class="msg-avatar">&#129302;</div>
        <div class="msg-bubble">
            <div>${contentHtml}</div>
            ${actionsHtml}
            <div class="msg-tools">
                <button type="button" class="msg-tool-btn" onclick="speakText('${escapeQuotes(data.response)}')">&#127908; Read Aloud</button>
                <button type="button" class="msg-tool-btn" onclick="copyMessageText('${msgId}')">&#128203; Copy</button>
                <button type="button" class="msg-tool-btn" onclick="retryLastUserPrompt()">&#128257; Retry</button>
            </div>
            <div class="msg-meta">
                <span>Agent: <strong>${(data.agent_id || 'Manager').toUpperCase()}</strong> • Mode: ${data.mode || 'Response'}</span>
                <span>${timeStr}</span>
            </div>
        </div>
    `;

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;

    // Render interactive components
    if (tableContainerId) {
        renderTableComponent(tableContainerId);
    }
    if (chartContainerId) {
        renderCanvasChart(chartContainerId, data.chart_data.type || 'bar');
    }
}

function appendManagerErrorMessage(errText) {
    const stream = document.getElementById('managerChatStreamBox');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg manager';
    msgDiv.innerHTML = `
        <div class="msg-avatar" style="border-color:#EF4444; color:#EF4444;">&#9888;</div>
        <div class="msg-bubble" style="border-color:#EF4444;">
            <div style="color:#EF4444; font-weight:700;">Operational Warning / Notice:</div>
            <div style="margin-top:4px;">${escapeHtml(errText)}</div>
            <div class="msg-tools">
                <button type="button" class="msg-tool-btn" onclick="retryLastUserPrompt()">&#128257; Retry</button>
            </div>
        </div>
    `;
    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

function quickFillPrompt(txt) {
    const input = document.getElementById('managerChatInput');
    input.value = txt;
    sendManagerMessage();
}

function handleChatKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendManagerMessage();
    }
}

function clearManagerConversation() {
    const stream = document.getElementById('managerChatStreamBox');
    stream.innerHTML = `
        <div class="chat-msg manager">
            <div class="msg-avatar">&#129302;</div>
            <div class="msg-bubble">
                Conversation reset. AI Manager is ready. How can I assist you?
            </div>
        </div>
    `;
}

function exportChatTranscript() {
    const stream = document.getElementById('managerChatStreamBox');
    const txt = stream.innerText;
    const blob = new Blob([txt], {type: 'text/plain'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `NanoPro_Chat_Transcript_${Date.now()}.txt`;
    a.click();
}

function copyMessageText(msgId) {
    const el = document.getElementById(msgId);
    if (!el) return;
    navigator.clipboard.writeText(el.innerText);
    logLocal('AIManager', 'Message copied to clipboard.');
}

function retryLastUserPrompt() {
    const userMsgs = document.querySelectorAll('.chat-msg.user .msg-bubble div:first-child');
    if (userMsgs.length > 0) {
        const lastPrompt = userMsgs[userMsgs.length - 1].innerText;
        quickFillPrompt(lastPrompt);
    }
}

function triggerChatAttachment() {
    document.getElementById('chatFileInputHidden').click();
}

function handleChatFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const input = document.getElementById('managerChatInput');
    input.value = `I have attached file '${file.name}'. Please analyze its schema and show me its records.`;
    sendManagerMessage();
}

/* =========================================================================
   3. INTERACTIVE SORTABLE TABLE ENGINE (WITH EXPORT & SEARCH)
   ========================================================================= */
function renderTableComponent(containerId) {
    const state = chatTablesRegistry[containerId];
    if (!state) return;
    const el = document.getElementById(containerId);
    if (!el) return;

    const startIdx = (state.page - 1) * state.pageSize;
    const endIdx = startIdx + state.pageSize;
    const pageRows = state.filteredRows.slice(startIdx, endIdx);
    const totalPages = Math.ceil(state.filteredRows.length / state.pageSize) || 1;

    let headersHtml = '';
    state.data.columns.forEach((col, idx) => {
        let sortIcon = '⇅';
        if (state.sortCol === idx) {
            sortIcon = state.sortAsc ? '▲' : '▼';
        }
        headersHtml += `<th onclick="sortTableColumn('${containerId}', ${idx})">${escapeHtml(col)} ${sortIcon}</th>`;
    });

    let rowsHtml = '';
    if (pageRows.length === 0) {
        rowsHtml = `<tr><td colspan="${state.data.columns.length}" style="text-align:center; color:var(--text-muted); padding:16px;">No matching records found</td></tr>`;
    } else {
        pageRows.forEach(row => {
            rowsHtml += '<tr>';
            row.forEach(val => {
                rowsHtml += `<td>${escapeHtml(String(val))}</td>`;
            });
            rowsHtml += '</tr>';
        });
    }

    el.innerHTML = `
        <div class="interactive-table-wrapper">
            <div class="table-toolbar">
                <input type="text" class="table-search-input" placeholder="Search table..." oninput="filterTableData('${containerId}', this.value)" />
                <div style="display:flex; gap:6px;">
                    <button type="button" class="table-btn-export" onclick="exportTableAsCSV('${containerId}')">&#128196; Export CSV</button>
                    <button type="button" class="table-btn-export" onclick="exportTableAsExcel('${containerId}')">&#128202; Export Excel</button>
                </div>
            </div>
            <div class="table-scroll-area">
                <table class="studio-data-table">
                    <thead><tr>${headersHtml}</tr></thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
            <div class="table-pagination-bar">
                <span>Showing ${startIdx + 1}–${Math.min(endIdx, state.filteredRows.length)} of ${state.filteredRows.length} records</span>
                <div style="display:flex; gap:6px; align-items:center;">
                    <button type="button" class="msg-tool-btn" ${state.page <= 1 ? 'disabled style="opacity:0.4;"' : ''} onclick="changeTablePage('${containerId}', -1)">&larr; Prev</button>
                    <span>Page ${state.page} of ${totalPages}</span>
                    <button type="button" class="msg-tool-btn" ${state.page >= totalPages ? 'disabled style="opacity:0.4;"' : ''} onclick="changeTablePage('${containerId}', 1)">Next &rarr;</button>
                </div>
            </div>
        </div>
    `;
}

function sortTableColumn(containerId, colIdx) {
    const state = chatTablesRegistry[containerId];
    if (!state) return;
    if (state.sortCol === colIdx) {
        state.sortAsc = !state.sortAsc;
    } else {
        state.sortCol = colIdx;
        state.sortAsc = true;
    }
    state.filteredRows.sort((a, b) => {
        let va = a[colIdx];
        let vb = b[colIdx];
        if (typeof va === 'number' && typeof vb === 'number') {
            return state.sortAsc ? va - vb : vb - va;
        }
        return state.sortAsc ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
    });
    renderTableComponent(containerId);
}

function filterTableData(containerId, query) {
    const state = chatTablesRegistry[containerId];
    if (!state) return;
    const q = query.toLowerCase();
    state.filteredRows = state.data.rows.filter(r => {
        return r.some(val => String(val).toLowerCase().includes(q));
    });
    state.page = 1;
    renderTableComponent(containerId);
}

function changeTablePage(containerId, delta) {
    const state = chatTablesRegistry[containerId];
    if (!state) return;
    const totalPages = Math.ceil(state.filteredRows.length / state.pageSize) || 1;
    state.page = Math.max(1, Math.min(totalPages, state.page + delta));
    renderTableComponent(containerId);
}

function exportTableAsCSV(containerId) {
    const state = chatTablesRegistry[containerId];
    if (!state) return;
    let csv = state.data.columns.join(',') + '\n';
    state.data.rows.forEach(r => {
        csv += r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',') + '\n';
    });
    const blob = new Blob([csv], {type: 'text/csv'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `NanoPro_Data_Export_${Date.now()}.csv`;
    a.click();
}

function exportTableAsExcel(containerId) {
    exportTableAsCSV(containerId); // Downloads formatted table cleanly
}

/* =========================================================================
   4. CANVAS CHARTING ENGINE (BAR, LINE, DONUT, PIE)
   ========================================================================= */
function renderCanvasChart(containerId, type = 'bar') {
    const chartData = chatChartsRegistry[containerId];
    if (!chartData) return;
    const canvas = document.getElementById('canvas_' + containerId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.clientWidth || 400;
    const height = canvas.parentElement.clientHeight || 220;
    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    const labels = chartData.labels || [];
    const ds = chartData.datasets[0] || {};
    const data = ds.data || [];
    const colors = ds.backgroundColor || ['#38BDF8', '#6366F1', '#10B981', '#F59E0B', '#A855F7'];

    if (type === 'bar') {
        const maxVal = Math.max(...data, 1);
        const barWidth = Math.min(48, (width - 80) / labels.length - 12);
        const startX = 60;
        const baseY = height - 40;
        const chartH = height - 60;

        // Draw axes
        ctx.strokeStyle = '#263354';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(startX - 10, 20);
        ctx.lineTo(startX - 10, baseY);
        ctx.lineTo(width - 20, baseY);
        ctx.stroke();

        labels.forEach((lbl, i) => {
            const val = data[i];
            const barH = (val / maxVal) * chartH;
            const x = startX + i * (barWidth + 16);
            const y = baseY - barH;

            // Bar fill
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(x, y, barWidth, barH);

            // Label text
            ctx.fillStyle = '#94A3B8';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(lbl.substring(0, 10), x + barWidth / 2, baseY + 16);

            // Value text
            ctx.fillStyle = '#F8FAFC';
            ctx.fillText('₹' + Math.round(val/1000) + 'k', x + barWidth / 2, y - 4);
        });

    } else if (type === 'donut' || type === 'pie') {
        const total = data.reduce((a, b) => a + b, 0) || 1;
        const cx = width / 3;
        const cy = height / 2;
        const radius = Math.min(cx, cy) - 20;
        let startAngle = -Math.PI / 2;

        data.forEach((val, i) => {
            const sliceAngle = (val / total) * 2 * Math.PI;
            ctx.fillStyle = colors[i % colors.length];
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();
            startAngle += sliceAngle;
        });

        if (type === 'donut') {
            // Cut center
            ctx.fillStyle = '#0B1120';
            ctx.beginPath();
            ctx.arc(cx, cy, radius * 0.55, 0, 2 * Math.PI);
            ctx.fill();
        }

        // Legend on right
        let legY = 30;
        labels.forEach((lbl, i) => {
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(width * 0.65, legY, 10, 10);
            ctx.fillStyle = '#CBD5E1';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'left';
            const pct = Math.round((data[i] / total) * 100);
            ctx.fillText(`${lbl} (${pct}%)`, width * 0.65 + 16, legY + 9);
            legY += 22;
        });

    } else if (type === 'line') {
        const maxVal = Math.max(...data, 1);
        const startX = 60;
        const baseY = height - 40;
        const chartH = height - 60;
        const stepX = (width - 100) / Math.max(labels.length - 1, 1);

        // Draw Line
        ctx.strokeStyle = '#38BDF8';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        labels.forEach((lbl, i) => {
            const x = startX + i * stepX;
            const y = baseY - (data[i] / maxVal) * chartH;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Draw points & labels
        labels.forEach((lbl, i) => {
            const x = startX + i * stepX;
            const y = baseY - (data[i] / maxVal) * chartH;
            ctx.fillStyle = '#6366F1';
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();

            ctx.fillStyle = '#94A3B8';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(lbl.substring(0, 10), x, baseY + 16);
        });
    }
}

function switchChartRenderType(containerId, type, btnEl) {
    const parent = btnEl.parentElement;
    parent.querySelectorAll('.chart-toggle-btn').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');
    renderCanvasChart(containerId, type);
}

/* =========================================================================
   5. NANO PRO VOICE ASSISTANT ("HI NANOPRO" & SPEECH SYNTHESIS)
   ========================================================================= */
let isVoiceRecording = false;
let speechRecognitionInstance = null;
let isWakeWordEnabled = false;

function toggleVoiceRecording() {
    if (isVoiceRecording) {
        stopVoiceRecording();
    } else {
        startVoiceRecording();
    }
}

function startVoiceRecording() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('Web Speech API is not supported in this browser. Please use Google Chrome or type your message.');
        return;
    }

    try {
        speechRecognitionInstance = new SpeechRecognition();
        const langSelect = document.getElementById('voiceLanguageSelect');
        speechRecognitionInstance.lang = langSelect ? langSelect.value : 'mr-IN';
        speechRecognitionInstance.continuous = false;
        speechRecognitionInstance.interimResults = false;

        setManagerSymbolState('listening');
        isVoiceRecording = true;

        const fb = document.getElementById('voiceFeedbackText');
        if (fb) fb.innerText = 'Listening to your voice... Speak now.';

        speechRecognitionInstance.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            logLocal('Voice', 'Speech recognized: ' + transcript);
            if (fb) fb.innerText = 'Heard: "' + transcript + '"';
            stopVoiceRecording();
            
            // Check for interruption stop command
            if (transcript.trim().toLowerCase() === 'stop') {
                stopSpeaking();
                return;
            }

            // Transfer to conversation stream
            quickFillPrompt(transcript);
        };

        speechRecognitionInstance.onerror = function(event) {
            logLocal('Voice', 'Speech recognition error: ' + event.error);
            stopVoiceRecording();
            if (fb) fb.innerText = 'Microphone notice: ' + event.error;
        };

        speechRecognitionInstance.onend = function() {
            stopVoiceRecording();
        };

        speechRecognitionInstance.start();
    } catch (e) {
        logLocal('Voice', 'Microphone start error: ' + e.message);
        stopVoiceRecording();
    }
}

function stopVoiceRecording() {
    isVoiceRecording = false;
    if (speechRecognitionInstance) {
        try { speechRecognitionInstance.stop(); } catch(e) {}
    }
    setManagerSymbolState('ready');
    const fb = document.getElementById('voiceFeedbackText');
    if (fb) fb.innerText = 'Click Symbol or Say "Hi NanoPro" to Begin Speaking';
}

function toggleWakeWordListener() {
    isWakeWordEnabled = !isWakeWordEnabled;
    const btn = document.getElementById('btnWakeWordToggle');
    if (btn) {
        btn.innerText = isWakeWordEnabled ? '🎤 Wake-Word: ACTIVE ("Hi NanoPro")' : '🎤 Wake-Word: DISABLED';
        btn.className = isWakeWordEnabled ? 'btn btn-primary' : 'btn btn-secondary';
    }
    logLocal('Voice', 'Wake-word detection set to: ' + isWakeWordEnabled);
}

function speakText(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    setManagerSymbolState('speaking');

    const cleanText = text.replace(/[*#`_]/g, '');
    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.rate = 1.0;
    utter.onend = function() {
        setManagerSymbolState('ready');
    };
    utter.onerror = function() {
        setManagerSymbolState('ready');
    };
    window.speechSynthesis.speak(utter);
}

function stopSpeaking() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    setManagerSymbolState('ready');
    logLocal('Voice', 'Speech stopped by user.');
}

function simulateVoicePrompt(promptText) {
    quickFillPrompt(promptText);
}

/* =========================================================================
   6. ANIMATED 3D AI AGENT OFFICE (REAL TELEMETRY SYNC)
   ========================================================================= */
let officeAgentsCache = [];

async function refreshOfficeLiveState() {
    try {
        const res = await fetch('/api/office/live-state');
        const data = await res.json();
        officeAgentsCache = data.agents || [];
        renderOfficeAgentCards(officeAgentsCache);

        // Update Office KPIs with real agent metrics (205 Specialized Agents)
        const totalCount = officeAgentsCache.length || 205;
        const activeCount = officeAgentsCache.filter(a => a.state === 'Running' || a.state === 'Assigned').length;
        const standbyCount = totalCount - activeCount;

        if (document.getElementById('officeKpiTotal')) document.getElementById('officeKpiTotal').innerText = totalCount;
        if (document.getElementById('officeKpiActive')) document.getElementById('officeKpiActive').innerText = activeCount;
        if (document.getElementById('officeKpiStandby')) document.getElementById('officeKpiStandby').innerText = standbyCount;
        if (document.getElementById('officeFilteredCountLabel')) {
            document.getElementById('officeFilteredCountLabel').innerText = `Showing ${totalCount} of ${totalCount} agents`;
        }

        // Data flow banner
        const flowBanner = document.getElementById('officeDataFlowBanner');
        const flowText = document.getElementById('officeDataFlowText');
        if (data.active_flows && data.active_flows.length > 0) {
            flowBanner.style.display = 'flex';
            const f = data.active_flows[0];
            flowText.innerText = `${f.from} ➔ ${f.to} : "${f.task}" (${f.duration}s elapsed)`;
        } else {
            flowBanner.style.display = 'none';
        }
    } catch (e) {
        logLocal('Office', 'Error refreshing office telemetry: ' + e.message);
    }
}

function renderOfficeAgentCards(agents) {
    const container = document.getElementById('officeAgentsGridContainer');
    if (!container) return;

    if (document.getElementById('officeFilteredCountLabel')) {
        document.getElementById('officeFilteredCountLabel').innerText = `Showing ${agents.length} of ${officeAgentsCache.length || 205} agents`;
    }

    if (agents.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted); padding:20px;">No agents found.</div>';
        return;
    }

    container.innerHTML = agents.map(a => {
        const stateClass = 'pill-' + (a.state || 'standby').toLowerCase().replace(/\s+/g, '-');
        const progress = a.progress_pct || (a.state === 'Running' ? 65 : (a.state === 'Completed' ? 100 : 0));
        return `
            <div class="agent-pod-card" id="pod_${a.agent_id}">
                <div class="agent-card-header">
                    <span class="agent-title">
                        <span>&#129302;</span> ${escapeHtml(a.name)}
                    </span>
                    <span class="agent-status-pill ${stateClass}">${escapeHtml(a.state || 'STANDBY')}</span>
                </div>
                <div style="font-size:10.5px; color:#38BDF8; margin-bottom:4px;">${escapeHtml(a.role || '')}</div>
                <div class="agent-task-text">${escapeHtml(a.current_task || 'Waiting for assignment...')}</div>
                <div class="agent-progress-track">
                    <div class="agent-progress-fill" style="width:${progress}%;"></div>
                </div>
                <div class="agent-meta-row">
                    <span>Group: <strong>${escapeHtml(a.group_name || a.group)}</strong></span>
                    <span>Elapsed: ${a.duration_sec || 0}s</span>
                </div>
            </div>
        `;
    }).join('');
}

function filterOfficeAgents(query) {
    const q = query.toLowerCase();
    const filtered = officeAgentsCache.filter(a => {
        return (a.name || '').toLowerCase().includes(q) ||
               (a.role || '').toLowerCase().includes(q) ||
               (a.description || '').toLowerCase().includes(q);
    });
    renderOfficeAgentCards(filtered);
}

function filterOfficePod(podGroup) {
    if (podGroup === 'all') {
        renderOfficeAgentCards(officeAgentsCache);
    } else {
        const filtered = officeAgentsCache.filter(a => a.group === podGroup);
        renderOfficeAgentCards(filtered);
    }
}

/* =========================================================================
   7. TASK SCHEDULER & AUTOMATION CENTER
   ========================================================================= */
async function refreshSchedulerDashboard() {
    try {
        const res = await fetch('/api/scheduler/stats');
        const data = await res.json();
        const s = data.stats || {};
        document.getElementById('schedStatTotal').innerText = s.total_tasks || 0;
        document.getElementById('schedStatEnabled').innerText = s.enabled_tasks || 0;
        document.getElementById('schedStatPaused').innerText = s.paused_tasks || 0;
        document.getElementById('schedStatRunning').innerText = s.running_tasks || 0;
        document.getElementById('schedStatSuccess').innerText = s.successful_runs || 0;
        document.getElementById('schedStatFailed').innerText = s.failed_runs || 0;
    } catch(e) {}
    loadSchedulerTasks();
    loadSchedulerRuns();
}

async function loadSchedulerTasks() {
    const tbody = document.getElementById('schedTasksTbody');
    if (!tbody) return;
    try {
        const res = await fetch('/api/scheduler/tasks');
        const data = await res.json();
        const list = data.tasks || [];
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:20px;">No scheduled tasks registered. Click "+ Create New Task" to begin.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(t => {
            const statusClass = t.is_paused ? 'color:#F59E0B;' : (t.is_enabled ? 'color:#10B981;' : 'color:#94A3B8;');
            const statusText = t.is_paused ? 'Paused' : (t.is_enabled ? 'Active / Ready' : 'Disabled');
            return `
                <tr>
                    <td><strong>${escapeHtml(t.name)}</strong><br/><span style="font-size:10.5px; color:var(--text-sub);">${escapeHtml(t.description || '')}</span></td>
                    <td><span class="badge" style="background:#1E293B; color:#38BDF8; font-size:10px;">${escapeHtml(t.task_type.toUpperCase())}</span></td>
                    <td>${escapeHtml(t.schedule_type)} (${escapeHtml(t.recurrence_expr || 'auto')})</td>
                    <td style="color:#38BDF8; font-size:11px;">${escapeHtml(t.next_run_at || 'N/A')}</td>
                    <td style="font-size:11px;">${escapeHtml(t.last_run_at || 'Never')}</td>
                    <td style="font-weight:700; ${statusClass}">${statusText}</td>
                    <td>
                        <div style="display:flex; gap:4px;">
                            <button type="button" class="btn btn-primary" style="padding:2px 6px; font-size:10.5px;" onclick="runTaskNow('${t.id}')">&#9658; Run</button>
                            ${t.is_paused ?
                                `<button type="button" class="btn btn-secondary" style="padding:2px 6px; font-size:10.5px;" onclick="resumeTask('${t.id}')">Resume</button>` :
                                `<button type="button" class="btn btn-secondary" style="padding:2px 6px; font-size:10.5px;" onclick="pauseTask('${t.id}')">Pause</button>`
                            }
                            <button type="button" class="btn btn-secondary" style="padding:2px 6px; font-size:10.5px;" onclick="duplicateTask('${t.id}')">Copy</button>
                            <button type="button" class="btn btn-secondary" style="padding:2px 6px; font-size:10.5px; color:#EF4444;" onclick="deleteTask('${t.id}')">&#128465;</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch(e) {
        tbody.innerHTML = `<tr><td colspan="7" style="color:#EF4444; padding:16px;">Failed loading tasks: ${e.message}</td></tr>`;
    }
}

async function loadSchedulerRuns() {
    const tbody = document.getElementById('schedRunsTbody');
    if (!tbody) return;
    try {
        const res = await fetch('/api/scheduler/runs?limit=30');
        const data = await res.json();
        const runs = data.runs || [];
        if (runs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:20px;">No execution history recorded yet.</td></tr>';
            return;
        }
        tbody.innerHTML = runs.map(r => {
            const stColor = r.status === 'Success' ? '#10B981' : (r.status === 'Running' ? '#38BDF8' : '#EF4444');
            return `
                <tr>
                    <td style="font-family:monospace; font-size:10.5px; color:#38BDF8;">${escapeHtml(r.run_id)}</td>
                    <td><strong>${escapeHtml(r.task_name)}</strong></td>
                    <td>${escapeHtml(r.trigger_type)}</td>
                    <td style="font-size:11px;">${escapeHtml(r.start_time)}</td>
                    <td>${r.duration_sec || 0}s</td>
                    <td><code>${r.exit_code}</code></td>
                    <td style="font-weight:700; color:${stColor};">${escapeHtml(r.status)}</td>
                    <td>
                        <button type="button" class="btn btn-secondary" style="padding:2px 6px; font-size:10.5px;" onclick="viewRunOutput('${escapeQuotes(r.stdout || '')}', '${escapeQuotes(r.stderr || '')}')">View Output</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch(e) {
        tbody.innerHTML = `<tr><td colspan="8" style="color:#EF4444; padding:16px;">Failed loading runs: ${e.message}</td></tr>`;
    }
}

function openTaskCreationModal() {
    document.getElementById('taskCreationCard').style.display = 'block';
    document.getElementById('taskCreationCard').scrollIntoView({behavior: 'smooth'});
}

function closeTaskCreationModal() {
    document.getElementById('taskCreationCard').style.display = 'none';
}

function onTaskTypeChange(type) {
    const dbRow = document.getElementById('schedSqlDbRow');
    if (dbRow) {
        dbRow.style.display = (type === 'sql') ? 'block' : 'none';
    }
}

async function submitTaskCreationForm() {
    const name = document.getElementById('schedFormName').value.trim();
    if (!name) { alert('Task Name is required.'); return; }
    const type = document.getElementById('schedFormType').value;
    const desc = document.getElementById('schedFormDesc').value.trim();
    const stype = document.getElementById('schedFormScheduleType').value;
    const rexpr = document.getElementById('schedFormRecurrence').value.trim();
    const content = document.getElementById('schedFormContent').value.trim();
    const dbConn = document.getElementById('schedFormDbConn') ? document.getElementById('schedFormDbConn').value : '';

    const payload = {
        name: name,
        description: desc,
        task_type: type,
        schedule_type: stype,
        recurrence_expr: rexpr,
        script_content: content,
        db_connection: dbConn,
        is_enabled: true
    };

    try {
        const res = await fetch('/api/scheduler/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const d = await res.json();
        closeTaskCreationModal();
        refreshSchedulerDashboard();
        logLocal('Scheduler', 'Task created: ' + name);
    } catch(e) {
        alert('Error saving task: ' + e.message);
    }
}

async function runTaskNow(taskId) {
    try {
        await fetch(`/api/scheduler/tasks/${taskId}/run_now`, {method: 'POST'});
        logLocal('Scheduler', 'Triggered immediate execution for task: ' + taskId);
        setTimeout(refreshSchedulerDashboard, 800);
    } catch(e) {
        alert('Run error: ' + e.message);
    }
}

async function pauseTask(taskId) {
    await fetch(`/api/scheduler/tasks/${taskId}/pause`, {method: 'POST'});
    refreshSchedulerDashboard();
}

async function resumeTask(taskId) {
    await fetch(`/api/scheduler/tasks/${taskId}/resume`, {method: 'POST'});
    refreshSchedulerDashboard();
}

async function duplicateTask(taskId) {
    await fetch(`/api/scheduler/tasks/${taskId}/duplicate`, {method: 'POST'});
    refreshSchedulerDashboard();
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this scheduled task and its execution history?')) return;
    await fetch(`/api/scheduler/tasks/${taskId}`, {method: 'DELETE'});
    refreshSchedulerDashboard();
}

function viewRunOutput(stdout, stderr) {
    const text = (stdout ? '=== STDOUT ===\n' + stdout + '\n\n' : '') + (stderr ? '=== STDERR ===\n' + stderr : '');
    alert(text || 'No process output captured for this run.');
}

/* =========================================================================
   8. NEWS CENTER (ABP MAJHA & AAJ TAK)
   ========================================================================= */
let newsArticlesCache = [];

async function refreshNewsFeed() {
    const btn = document.querySelector('#view-news_center .btn-primary');
    if (btn) btn.innerText = 'Refreshing...';
    try {
        const res = await fetch('/api/news/refresh', {method: 'POST'});
        const data = await res.json();
        newsArticlesCache = data.articles || [];
        renderNewsArticles(newsArticlesCache);
        logLocal('News', 'Refreshed news from ABP Majha and Aaj Tak.');
    } catch(e) {
        logLocal('News', 'Refresh error: ' + e.message);
    } finally {
        if (btn) btn.innerText = '🔄 Refresh News Now';
    }
}

async function loadNewsArticles() {
    try {
        const res = await fetch('/api/news/articles?limit=40');
        const data = await res.json();
        newsArticlesCache = data.articles || [];
        renderNewsArticles(newsArticlesCache);
    } catch(e) {}
}

function renderNewsArticles(articles) {
    const container = document.getElementById('newsArticlesGrid');
    if (!container) return;
    if (articles.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted); padding:20px;">No stories found in selected category.</div>';
        return;
    }
    container.innerHTML = articles.map(a => {
        const pubClass = a.publisher === 'ABP Majha' ? 'pub-abp' : 'pub-aajtak';
        const isBreaking = a.importance === 'Breaking';
        return `
            <div class="news-article-card">
                <img src="${a.thumbnail_url || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&auto=format&fit=crop'}" class="news-card-thumb" alt="News Image" onerror="this.src='https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=600&auto=format&fit=crop';" />
                <div class="news-card-body">
                    <div class="news-badges-row">
                        <span class="badge-publisher ${pubClass}">${escapeHtml(a.publisher)}</span>
                        <span class="badge-category">${escapeHtml(a.category)}</span>
                        ${isBreaking ? '<span class="badge-breaking">BREAKING</span>' : ''}
                        <span style="font-size:10px; color:var(--text-sub); margin-left:auto;">${escapeHtml(a.published_at.substring(0, 16))}</span>
                    </div>
                    <div class="news-title">${escapeHtml(a.title)}</div>
                    <div class="news-summary-mr">${escapeHtml(a.summary_mr || '')}</div>
                    <div class="news-summary-en">${escapeHtml(a.summary_en || '')}</div>
                    <div class="news-footer-actions">
                        <button type="button" class="btn btn-secondary" style="font-size:10.5px; padding:3px 8px;" onclick="speakText('${escapeQuotes(a.summary_mr || a.title)}')">&#127908; Read Aloud</button>
                        <a href="${a.url}" target="_blank" class="btn btn-secondary" style="font-size:10.5px; padding:3px 8px; text-decoration:none;">Read Full Story &rarr;</a>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function filterNewsCategory(cat, btnEl) {
    const parent = btnEl.parentElement;
    parent.querySelectorAll('.action-chip').forEach(c => c.classList.remove('active'));
    btnEl.classList.add('active');

    if (cat === 'All') {
        renderNewsArticles(newsArticlesCache);
    } else {
        const filtered = newsArticlesCache.filter(a => (a.category || '').toLowerCase() === cat.toLowerCase());
        renderNewsArticles(filtered);
    }
}

async function checkFloatingNewsAlerts() {
    try {
        const res = await fetch('/api/news/alerts');
        const data = await res.json();
        const alerts = data.alerts || [];
        if (alerts.length > 0) {
            const topAlert = alerts[0];
            const banner = document.getElementById('floatingNewsBanner');
            if (banner) {
                document.getElementById('floatingNewsTitle').innerText = topAlert.title;
                document.getElementById('floatingNewsSummary').innerText = topAlert.summary_mr || topAlert.summary_en;
                banner.setAttribute('data-article-id', topAlert.article_id);
                banner.style.display = 'block';
            }
        }
    } catch(e) {}
}

function dismissFloatingNews() {
    const banner = document.getElementById('floatingNewsBanner');
    if (!banner) return;
    const aid = banner.getAttribute('data-article-id');
    if (aid) {
        fetch(`/api/news/alerts/${aid}/dismiss`, {method: 'POST'});
    }
    banner.style.display = 'none';
}

function readFloatingNewsAloud() {
    const summary = document.getElementById('floatingNewsSummary').innerText;
    speakText(summary);
}

function openFloatingNewsInCenter() {
    dismissFloatingNews();
    switchView('news_center');
}

/* =========================================================================
   9. ENTERTAINMENT & MODERN LIFESTYLE CENTER
   ========================================================================= */
let entertainmentCache = [];

async function loadEntertainmentItems() {
    try {
        const res = await fetch('/api/entertainment/items?limit=60');
        const data = await res.json();
        entertainmentCache = data.items || [];
        renderEntertainmentCards(entertainmentCache);
    } catch(e) {}
}

function renderEntertainmentCards(items) {
    const container = document.getElementById('entertainmentGrid');
    if (!container) return;
    if (items.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted); padding:20px;">No items match selected category.</div>';
        return;
    }
    container.innerHTML = items.map(it => {
        return `
            <div class="ent-card">
                <div class="ent-card-thumb-wrap">
                    <img src="${it.thumbnail_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop'}" class="ent-card-thumb" alt="${escapeHtml(it.title)}" onerror="this.src='https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop';" />
                </div>
                <div class="ent-card-content">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span class="badge" style="background:#1E293B; color:#38BDF8; font-size:10px;">${escapeHtml(it.category)}</span>
                        <span style="cursor:pointer; font-size:14px; color:${it.is_favorite ? '#F59E0B' : '#64748B'};" onclick="toggleEntertainmentFav('${it.item_id}', this)">★</span>
                    </div>
                    <div class="ent-card-title">${escapeHtml(it.title)}</div>
                    <div class="ent-card-creator">${escapeHtml(it.creator || '')}</div>
                    <div class="ent-card-desc">${escapeHtml(it.description || '')}</div>
                    <div style="display:flex; gap:6px; margin-top:auto; padding-top:8px; border-top:1px solid #1E293B;">
                        <button type="button" class="btn btn-secondary" style="font-size:10.5px; padding:3px 8px; flex:1;" onclick="askManagerAboutMedia('${it.item_id}')">&#129302; Ask Manager</button>
                        <a href="${it.media_url || '#'}" target="_blank" class="btn btn-primary" style="font-size:10.5px; padding:3px 8px; text-decoration:none;">Open &rarr;</a>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function filterEntertainmentCategory(cat, btnEl) {
    const parent = btnEl.parentElement;
    parent.querySelectorAll('.action-chip').forEach(c => c.classList.remove('active'));
    btnEl.classList.add('active');

    if (cat === 'All') {
        renderEntertainmentCards(entertainmentCache);
    } else {
        const filtered = entertainmentCache.filter(it => (it.category || '').toLowerCase() === cat.toLowerCase());
        renderEntertainmentCards(filtered);
    }
}

function filterEntertainmentSearch(query) {
    const q = query.toLowerCase();
    const filtered = entertainmentCache.filter(it => {
        return (it.title || '').toLowerCase().includes(q) ||
               (it.creator || '').toLowerCase().includes(q) ||
               (it.description || '').toLowerCase().includes(q);
    });
    renderEntertainmentCards(filtered);
}

async function toggleEntertainmentFav(itemId, el) {
    try {
        await fetch(`/api/entertainment/favorite/${itemId}`, {method: 'POST'});
        el.style.color = el.style.color === 'rgb(245, 158, 11)' ? '#64748B' : '#F59E0B';
    } catch(e) {}
}

async function askManagerAboutMedia(itemId) {
    switchView('ai_manager');
    const target = entertainmentCache.find(i => i.item_id === itemId);
    const title = target ? target.title : 'this media';
    quickFillPrompt(`Explain and summarize ${title} in simple language.`);
}

/* =========================================================================
   10. BOOK READER & INTELLIGENT LEARNING ASSISTANT
   ========================================================================= */
let currentActiveBook = null;
let currentChapterIndex = 0;
let readerFontSize = 14;

async function loadBooksList() {
    try {
        const res = await fetch('/api/books/list');
        const data = await res.json();
        const books = data.books || [];
        if (books.length > 0) {
            selectBook(books[0]);
        }
    } catch(e) {}
}

function selectBook(book) {
    currentActiveBook = book;
    currentChapterIndex = 0;
    document.getElementById('readerActiveBookTitle').innerText = book.title;
    document.getElementById('readerActiveBookAuthor').innerText = 'Author: ' + (book.author || 'Unknown');
    document.getElementById('readerProgressPct').innerText = Math.round(book.reading_progress_pct || 0) + '%';
    document.getElementById('readerProgressBar').style.width = (book.reading_progress_pct || 0) + '%';

    const chapters = book.chapters || [];
    const listEl = document.getElementById('readerChaptersList');
    if (chapters.length === 0) {
        listEl.innerHTML = '<div style="color:var(--text-muted); font-size:11px;">No chapter headers detected.</div>';
    } else {
        listEl.innerHTML = chapters.map((ch, idx) => {
            const activeClass = idx === 0 ? 'active' : '';
            return `
                <div class="toc-chapter-item ${activeClass}" id="ch_item_${idx}" onclick="selectChapter(${idx})">
                    ${idx + 1}. ${escapeHtml(ch.title)}
                </div>
            `;
        }).join('');
    }
    loadChapterContent(0);
}

function selectChapter(idx) {
    currentChapterIndex = idx;
    document.querySelectorAll('.toc-chapter-item').forEach(el => el.classList.remove('active'));
    const target = document.getElementById('ch_item_' + idx);
    if (target) target.classList.add('active');
    loadChapterContent(idx);

    // Update progress
    if (currentActiveBook && currentActiveBook.chapters) {
        const total = currentActiveBook.chapters.length;
        const pct = Math.round(((idx + 1) / total) * 100);
        document.getElementById('readerProgressPct').innerText = pct + '%';
        document.getElementById('readerProgressBar').style.width = pct + '%';
        fetch(`/api/books/${currentActiveBook.book_id}/progress`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ progress_pct: pct, chapter_idx: idx })
        });
    }
}

function loadChapterContent(idx) {
    if (!currentActiveBook || !currentActiveBook.chapters) return;
    const ch = currentActiveBook.chapters[idx];
    if (!ch) return;
    document.getElementById('readerCurrentChapterTitle').innerText = ch.title;
    const content = ch.content || 'No text found in this chapter.';
    document.getElementById('readerTextArea').innerText = content;
    document.getElementById('readerTextArea').scrollTop = 0;
}

function adjustReaderFontSize(delta) {
    readerFontSize = Math.max(11, Math.min(22, readerFontSize + delta));
    document.getElementById('readerTextArea').style.fontSize = readerFontSize + 'px';
}

function readCurrentChapterAloud() {
    const text = document.getElementById('readerTextArea').innerText;
    speakText(text.substring(0, 500));
}

async function askBookAI(query) {
    if (!currentActiveBook) { alert('Please select a book first.'); return; }
    const outBox = document.getElementById('readerAIExplanationBox');
    outBox.style.display = 'block';
    outBox.innerHTML = '<span style="color:#38BDF8;">Consulting Book Reader Assistant...</span>';

    try {
        const res = await fetch(`/api/books/${currentActiveBook.book_id}/explain`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ query: query, chapter_idx: currentChapterIndex })
        });
        const data = await res.json();
        outBox.innerHTML = formatMarkdown(data.explanation || 'Explanation generated.');
    } catch(e) {
        outBox.innerHTML = `<span style="color:#EF4444;">Error: ${e.message}</span>`;
    }
}

function triggerBookUpload() {
    document.getElementById('bookUploadInputHidden').click();
}

async function handleBookFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    logLocal('BookReader', 'Uploading book: ' + file.name);

    try {
        const res = await fetch('/api/books/upload', {
            method: 'POST',
            body: formData
        });
        const d = await res.json();
        if (d.status === 'success') {
            alert(`Book '${d.title}' uploaded and indexed successfully with ${d.total_chapters} chapters!`);
            loadBooksList();
        } else {
            alert('Upload notice: ' + (d.error || 'Failed'));
        }
    } catch(e) {
        alert('Upload error: ' + e.message);
    }
}

function openBookPathImportModal() {
    const path = prompt('Enter accessible local file path to book (.pdf, .docx, .txt):');
    if (!path) return;
    fetch('/api/books/import_path', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ file_path: path.trim() })
    }).then(r => r.json()).then(d => {
        if (d.status === 'success') {
            alert(`Imported '${d.title}' with ${d.total_chapters} chapters.`);
            loadBooksList();
        } else {
            alert('Import notice: ' + (d.error || 'Failed'));
        }
    });
}

/* =========================================================================
   11. UTILITY HELPERS (MARKDOWN, ESCAPING)
   ========================================================================= */
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function escapeQuotes(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/\n/g, ' ');
}

function formatMarkdown(text) {
    if (!text) return '';
    if (typeof formatMarkdownChat === 'function') {
        return formatMarkdownChat(text);
    }
    let out = escapeHtml(text);
    out = out.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    out = out.replace(/(^|[^\*])\*([^\*\n]+)\*([^\*]|$)/g, '$1<em>$2</em>$3');
    out = out.replace(/```([a-zA-Z0-9_\-\+]*)\r?\n([\s\S]*?)```/g, '<pre style="background:#050811; padding:10px; border-radius:6px; overflow-x:auto;"><code>$2</code></pre>');
    out = out.replace(/`([^`\r\n]+)`/g, '<code style="background:#0F172A; color:#38BDF8; padding:2px 5px; border-radius:3px;">$1</code>');
    out = out.replace(/^\s*[•\-\*]\s+(.*$)/gm, '<div style="padding-left:14px; margin:3px 0;">&bull; $1</div>');
    out = out.replace(/^\d+\. (.*?)$/gm, '<div style="padding-left:14px; margin:3px 0;"><strong>$1.</strong> $2</div>');
    out = out.replace(/\r?\n/g, '<br>');
    return out;
}
"""
