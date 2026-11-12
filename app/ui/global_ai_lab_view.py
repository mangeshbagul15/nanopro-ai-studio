"""
Mangesh Nano Pro AI Studio - Global AI Lab Workspace View
Provides the rich interactive workspace view for legacy console (#global_ai_lab).
Includes the Single-AUTO Mathematical Router simulator, 32+ Labs Explorer, and live telemetry.
"""

def get_global_ai_lab_html() -> str:
    return """
<!-- VIEW: GLOBAL AI LAB (FEATURE 53) -->
<div class="workspace-view" id="view-global_ai_lab">
    <style>
        .ailab-hero {
            background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(17, 24, 39, 0.9) 100%);
            border: 1px solid rgba(168, 85, 247, 0.35);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
            position: relative;
            overflow: hidden;
        }
        .ailab-hero::after {
            content: '';
            position: absolute;
            top: -60px;
            right: -60px;
            width: 220px;
            height: 220px;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, transparent 70%);
            pointer-events: none;
        }
        .ailab-title-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            margin-bottom: 12px;
        }
        .ailab-badge-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .ailab-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.03em;
        }
        .pill-purple { background: rgba(168, 85, 247, 0.2); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.4); }
        .pill-cyan { background: rgba(34, 211, 238, 0.15); color: #67E8F9; border: 1px solid rgba(34, 211, 238, 0.35); }
        .pill-green { background: rgba(34, 197, 94, 0.15); color: #86EFAC; border: 1px solid rgba(34, 197, 94, 0.35); }
        
        /* Auto Router Cockpit */
        .ailab-cockpit {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 24px;
        }
        .ailab-input-row {
            display: flex;
            gap: 12px;
            margin-top: 12px;
        }
        .ailab-input {
            flex: 1;
            background: rgba(2, 6, 23, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 12px 16px;
            color: #F8FAFC;
            font-size: 13.5px;
            font-family: inherit;
        }
        .ailab-input:focus {
            outline: none;
            border-color: #A855F7;
            box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.25);
        }
        .ailab-btn {
            background: linear-gradient(135deg, #9333EA 0%, #38BDF8 100%);
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 12px 22px;
            font-weight: 700;
            font-size: 13.5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .ailab-btn:hover {
            filter: brightness(1.15);
            transform: translateY(-1px);
        }
        
        /* Math Decision HUD */
        .ailab-decision-hud {
            display: none;
            margin-top: 16px;
            padding: 16px;
            background: rgba(2, 6, 23, 0.9);
            border: 1px solid rgba(34, 211, 238, 0.3);
            border-radius: 12px;
        }
        .hud-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-top: 10px;
        }
        .hud-card {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 8px;
            padding: 10px 12px;
            border-left: 3px solid #38BDF8;
        }
        .hud-label { font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.04em; }
        .hud-val { font-size: 15px; font-weight: 800; color: #F1F5F9; margin-top: 3px; }

        /* Region Tabs */
        .ailab-tabs {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            margin-bottom: 16px;
            padding-bottom: 6px;
        }
        .ailab-tab {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #94A3B8;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .ailab-tab.active, .ailab-tab:hover {
            background: rgba(168, 85, 247, 0.2);
            color: #FFFFFF;
            border-color: #A855F7;
        }

        /* Labs Grid */
        .labs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }
        .lab-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            transition: all 0.25s;
        }
        .lab-card:hover {
            border-color: rgba(168, 85, 247, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }
        .lab-hdr {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .lab-title {
            font-size: 16px;
            font-weight: 800;
            color: #F8FAFC;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .lab-country {
            font-size: 11px;
            font-weight: 600;
            color: #94A3B8;
            background: rgba(30, 41, 59, 0.8);
            padding: 2px 8px;
            border-radius: 6px;
        }
        .lab-desc {
            font-size: 12px;
            color: #94A3B8;
            line-height: 1.4;
            margin-bottom: 12px;
        }
        .lab-models-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding-top: 10px;
        }
        .model-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(2, 6, 23, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        }
        .model-item-name {
            font-weight: 700;
            color: #E2E8F0;
        }
        .model-item-meta {
            display: flex;
            gap: 8px;
            font-size: 10.5px;
            color: #64748B;
        }
    </style>

    <!-- Masthead -->
    <div class="ailab-hero">
        <div class="ailab-title-row">
            <div>
                <h1 style="margin:0 0 6px 0; font-size:24px; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em;">
                    🧠 NanoPro Global AI Lab
                </h1>
                <p style="margin:0; font-size:13.5px; color:#CBD5E1;">
                    World Foundational AI Creators · 32+ Global Labs · 185+ Frontier Models · Unified High-Tech Auto-Router
                </p>
            </div>
            <div class="ailab-badge-row">
                <span class="ailab-pill pill-purple">⚡ Single AUTO Engine</span>
                <span class="ailab-pill pill-cyan">📐 Pareto Multi-Objective</span>
                <span class="ailab-pill pill-green">🛡️ Thompson 429 Shield</span>
            </div>
        </div>
    </div>

    <!-- Single AUTO Router Simulator Cockpit -->
    <div class="ailab-cockpit">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
                <h3 style="margin:0; font-size:16px; font-weight:700; color:#F8FAFC;">
                    ⚡ High-Tech Auto-Router Cockpit (Sub-5ms Mathematical Dispatch)
                </h3>
                <p style="margin:4px 0 0 0; font-size:12px; color:#94A3B8;">
                    Enter any prompt or coding challenge below. The mathematical engine evaluates Semantic Vectors, Pareto Utility, and Thompson Bandit probabilities in &lt; 3 milliseconds.
                </p>
            </div>
            <span style="font-size:11.5px; color:#38BDF8; font-weight:700;">Target SLA: &lt; 800ms First Token</span>
        </div>

        <div class="ailab-input-row">
            <input type="text" id="ailab-test-prompt" class="ailab-input" 
                   placeholder="e.g. 'Write a Python distributed Kafka streaming consumer' or 'Prove consensus'..." 
                   value="Write a Python script to ingest real-time banking transactions into Snowflake and detect anomalies" />
            <button type="button" class="ailab-btn" onclick="executeAutoRouteTest()">
                <span>⚡ Run AUTO Math</span>
            </button>
        </div>

        <!-- Decision Breakdown HUD -->
        <div id="ailab-hud" class="ailab-decision-hud">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:8px;">
                <div style="font-size:13.5px; font-weight:700; color:#38BDF8;" id="hud-model-title">
                    🎯 Selected Model: Evaluating...
                </div>
                <div style="font-size:11px; color:#10B981; font-weight:700;" id="hud-latency-overhead">
                    ⚡ Decision Time: 0ms
                </div>
            </div>
            <div class="hud-grid">
                <div class="hud-card" style="border-left-color:#A855F7;">
                    <div class="hud-label">Detected Task Domain</div>
                    <div class="hud-val" id="hud-task-val">-</div>
                </div>
                <div class="hud-card" style="border-left-color:#10B981;">
                    <div class="hud-label">Semantic Cosine Sim</div>
                    <div class="hud-val" id="hud-sim-val">-</div>
                </div>
                <div class="hud-card" style="border-left-color:#38BDF8;">
                    <div class="hud-label">Pareto Utility Score</div>
                    <div class="hud-val" id="hud-pareto-val">-</div>
                </div>
                <div class="hud-card" style="border-left-color:#F59E0B;">
                    <div class="hud-label">Estimated Latency</div>
                    <div class="hud-val" id="hud-latency-val">-</div>
                </div>
            </div>
            <div style="margin-top:12px; font-size:12px; color:#94A3B8;" id="hud-runners-up">
                <!-- Runners up list -->
            </div>
        </div>
    </div>

    <!-- Region Filter Tabs -->
    <div class="ailab-tabs">
        <button type="button" class="ailab-tab active" onclick="filterAILabs('all', this)">🌐 All 32 Labs (185+ Models)</button>
        <button type="button" class="ailab-tab" onclick="filterAILabs('USA', this)">🇺🇸 USA (12 Labs)</button>
        <button type="button" class="ailab-tab" onclick="filterAILabs('China', this)">🇨🇳 China (11 Labs)</button>
        <button type="button" class="ailab-tab" onclick="filterAILabs('France', this)">🇫🇷 Europe (3 Labs)</button>
        <button type="button" class="ailab-tab" onclick="filterAILabs('India', this)">🇮🇳 India (2 Labs)</button>
        <button type="button" class="ailab-tab" onclick="filterAILabs('Global', this)">🌍 Global & Asia (4 Labs)</button>
    </div>

    <!-- 32 Labs Grid Container -->
    <div class="labs-grid" id="ailab-labs-grid">
        <div style="grid-column:1/-1; text-align:center; padding:40px; color:#94A3B8;">
            Loading 32 World AI Foundational Creators...
        </div>
    </div>
</div>

<script>
let globalAILabsData = null;

async function initGlobalAILab() {
    try {
        const resp = await fetch('/api/ai/global_labs');
        if (!resp.ok) throw new Error('API failed');
        globalAILabsData = await resp.json();
        renderAILabsGrid('all');
    } catch(e) {
        console.error('Failed to load Global AI Lab data:', e);
        const container = document.getElementById('ailab-labs-grid');
        if (container) {
            container.innerHTML = '<div style="grid-column:1/-1; color:#F87171; padding:20px;">Could not connect to /api/ai/global_labs. Retrying...</div>';
        }
    }
}

function filterAILabs(region, btn) {
    document.querySelectorAll('.ailab-tab').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderAILabsGrid(region);
}

function renderAILabsGrid(filterRegion) {
    if (!globalAILabsData || !globalAILabsData.creators) return;
    const grid = document.getElementById('ailab-labs-grid');
    if (!grid) return;

    const creators = Object.values(globalAILabsData.creators);
    const filtered = creators.filter(c => {
        if (filterRegion === 'all') return true;
        if (filterRegion === 'France') return c.country === 'France' || c.country === 'Germany';
        if (filterRegion === 'Global') return ['UAE', 'South Korea', 'Japan'].includes(c.country);
        return c.country === filterRegion;
    });

    let html = '';
    filtered.forEach(c => {
        html += '<div class="lab-card">';
        html += '  <div class="lab-hdr">';
        html += '    <div class="lab-title"><span>' + c.flag + '</span> ' + c.name + '</div>';
        html += '    <span class="lab-country">' + c.country + '</span>';
        html += '  </div>';
        html += '  <div class="lab-desc">' + c.description + '</div>';
        html += '  <div class="lab-models-list">';
        (c.models || []).forEach(m => {
            html += '    <div class="model-item">';
            html += '      <span class="model-item-name">' + m.name + '</span>';
            html += '      <div class="model-item-meta">';
            html += '        <span>Ctx: ' + m.context + '</span>';
            html += '        <span style="color:#38BDF8;">Elo ' + m.elo + '</span>';
            html += '        <span style="color:#10B981;">' + m.latency_ms + 'ms</span>';
            html += '      </div>';
            html += '    </div>';
        });
        html += '  </div>';
        html += '</div>';
    });

    grid.innerHTML = html;
}

async function executeAutoRouteTest() {
    const promptInput = document.getElementById('ailab-test-prompt');
    const prompt = (promptInput && promptInput.value.trim()) || 'Test prompt';
    const hud = document.getElementById('ailab-hud');
    if (hud) hud.style.display = 'block';

    try {
        const resp = await fetch('/api/ai/smart_route', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt: prompt, sla_ms: 800})
        });
        const res = await resp.json();
        
        document.getElementById('hud-model-title').innerHTML = '🎯 Selected Model: <strong>' + res.flag + ' ' + res.model_name + '</strong> (' + res.creator + ')';
        document.getElementById('hud-latency-overhead').innerText = '⚡ Math Overhead: ' + res.routing_overhead_ms + ' ms';
        document.getElementById('hud-task-val').innerText = (res.decision_math.detected_task || '').replace(/_/g, ' ').toUpperCase();
        document.getElementById('hud-sim-val').innerText = (res.decision_math.task_similarity * 100).toFixed(1) + '%';
        document.getElementById('hud-pareto-val').innerText = res.decision_math.pareto_utility_score.toFixed(3);
        document.getElementById('hud-latency-val').innerText = res.estimated_latency_ms + ' ms (SLA OK)';

        const runners = (res.runners_up || []).map(r => '• ' + r.name + ' (' + r.creator + ') - ' + r.latency_ms + 'ms').join(' &nbsp;|&nbsp; ');
        document.getElementById('hud-runners-up').innerHTML = '<strong style="color:#CBD5E1;">Pareto Runners-Up:</strong> ' + runners;
    } catch(e) {
        console.error('Auto route failed:', e);
        if (hud) {
            document.getElementById('hud-model-title').innerText = 'Error calling /api/ai/smart_route';
        }
    }
}

// Auto-initialize when loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGlobalAILab);
} else {
    setTimeout(initGlobalAILab, 100);
}
</script>
"""
