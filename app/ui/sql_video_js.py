"""
Mangesh Nano Pro AI Studio - 9:16 SQL Short Video Client-Side Engine
Handles HTML5 Canvas 1080x1920 9:16 rendering, dynamic arrow motion, 
typewriter SQL code animations, multilingual voiceover, and MediaRecorder export with audio multiplexing.
"""

def get_sql_video_js() -> str:
    return r'''
    <script>
    /* ==========================================================================
       9:16 SQL SHORT & REEL ENGINE (CLIENT-SIDE ZERO-SERVER-LOAD)
       ========================================================================== */
    const SQL_CLIENT_PRESETS = {};

    let sqlShortState = {
        currentTime: 0.0,
        maxDuration: 56.0,
        isPlaying: false,
        playbackSpeed: 1.0,
        audioLang: 'mr',
        textStyle: 'minglish',
        showAvatar: true,
        activePreset: null,
        activeVideoSpec: null,
        selectedAvatar: "Nadim_public_5",
        avatarVideoElement: null,
        avatarVideoLoaded: false,
        backgroundVideoElement: null,
        backgroundVideoLoaded: false,
        animationFrameId: null,
        lastTimestamp: null,
        isExporting: false,
        mediaRecorder: null,
        recordedChunks: [],
        audioUrl: "/audio/preset_sql_q1_second_highest_salary_en.mp3"
    };

    // Dynamic duration calibration & proportional stage scaling (<60s Shorts & Reels standard)
    function calibrateAudioDuration() {
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (!audioEl) return;
        const realDur = audioEl.duration;
        if (realDur && !isNaN(realDur) && isFinite(realDur) && realDur > 5.0) {
            // Strictly cap at 58.5s so video is ALWAYS placed on YouTube Shorts & Instagram Reels shelf
            const boundedDur = Math.min(58.5, realDur);
            sqlShortState.maxDuration = boundedDur;
            const sc = document.getElementById("sqlShortScrubber");
            if (sc) {
                sc.max = boundedDur;
                sc.step = "0.1";
            }
            scaleScenesToRealDuration(boundedDur);
            updatePlayerScrubberUI(sqlShortState.currentTime);
        }
    }

    function scaleScenesToRealDuration(dur) {
        const p = sqlShortState.activeVideoSpec || sqlShortState.activePreset;
        if (!p) {
            renderPromptStandbyScreen(ctx, W, H, t);
            return;
        }
        if (!p) return;
        const stagesList = (p.stages && p.stages.length > 0) ? p.stages : (p.scenes && p.scenes.length > 0 ? p.scenes : null);
        if (!stagesList || stagesList.length === 0) return;
        const lastScene = stagesList[stagesList.length - 1];
        const origMax = p.max_duration_seconds || lastScene.orig_end || lastScene.end || 56.0;
        const ratio = dur / origMax;
        stagesList.forEach(s => {
            if (s.orig_start === undefined) s.orig_start = s.start;
            if (s.orig_end === undefined) s.orig_end = s.end;
            s.start = Number((s.orig_start * ratio).toFixed(2));
            s.end = Number((s.orig_end * ratio).toFixed(2));
        });
        if (p.orig_outro_start === undefined) p.orig_outro_start = (p.outro_start !== undefined) ? p.outro_start : Math.max(0, origMax - 3.5);
        p.outro_start = Math.max(0, Number((p.orig_outro_start * ratio).toFixed(2)));
        p.max_duration_seconds = dur;
    }

    function attachAudioSyncListeners(audioEl) {
        if (!audioEl || audioEl._hasSyncListeners) return;
        audioEl._hasSyncListeners = true;
        audioEl.addEventListener("loadedmetadata", calibrateAudioDuration);
        audioEl.addEventListener("durationchange", calibrateAudioDuration);
        audioEl.addEventListener("canplay", calibrateAudioDuration);
        audioEl.addEventListener("ended", () => {
            sqlShortState.currentTime = sqlShortState.maxDuration;
            pauseSqlShortPlay();
            renderSqlShortFrame(sqlShortState.currentTime);
            updatePlayerScrubberUI(sqlShortState.currentTime);
        });
    }

    // Initialize Workspace on Page Load
    document.addEventListener("DOMContentLoaded", () => {
        initSqlShortWorkspace();
    });

    // Also initialize immediately in case script is injected after DOMContentLoaded
    setTimeout(() => {
        if (!document.getElementById("sqlShortQuestion") || !document.getElementById("sqlShortQuestion").value) {
            initSqlShortWorkspace();
        }
    }, 150);

    const DEMO_MASTER_PROMPT = `# MASTER PROMPT — AI SQL TEACHER: INTERACTIVE SQL INTERVIEW SHORTS

## 1. VIDEO CONFIGURATION
* Aspect Ratio: 9:16
* Target Duration: 55 seconds (YouTube Shorts & Reels <60s)
* Voice: Natural Indian AI teacher
* Branding: @Code_With_Mangesh

## 2. SQL INTERVIEW QUESTION
**Video Title:**
SQL Interview Question #1 — Find the Second-Highest Salary

**Question:**
Using the EMPLOYEES table, write a SQL query to find the second-highest distinct salary.

**Sample Data:**
| EMP_ID | EMP_NAME | DEPARTMENT | SALARY |
| 101 | Amit | IT | 60000 |
| 102 | Rahul | HR | 50000 |
| 103 | Priya | IT | 80000 |
| 104 | Neha | Finance | 70000 |
| 105 | Kiran | IT | 80000 |

**Expected SQL Query:**
\`\`\`sql
SELECT MAX(SALARY) AS SECOND_HIGHEST_SALARY
FROM EMPLOYEES
WHERE SALARY < (
    SELECT MAX(SALARY)
    FROM EMPLOYEES
);
\`\`\`

**Expected Output:**
SECOND_HIGHEST_SALARY: 70000`;

    function loadDemoMasterPrompt() {
        const qEl = document.getElementById("sqlShortQuestion");
        if (qEl) {
            qEl.value = DEMO_MASTER_PROMPT;
            qEl.focus();
        }
    }

    function clearMasterPrompt() {
        const qEl = document.getElementById("sqlShortQuestion");
        if (qEl) {
            qEl.value = "";
            qEl.focus();
        }
    }

    function initSqlShortWorkspace() {
        const p = sqlShortState.activeVideoSpec || sqlShortState.activePreset;
        if (p) {
            updateSqlBlueprintUI(p);
        }
        renderSqlShortFrame(0);
    }

    // Audio Loading & Synthesis
    async function loadPresetVoiceAudio() {
        const p = sqlShortState.activePreset;
        const lang = sqlShortState.audioLang;
        const audioEl = document.getElementById("sqlVoiceAudio");
        const badge = document.getElementById("activeVoiceBadge");

        if (badge) {
            badge.innerText = lang === "mr" ? "🇮🇳 मराठी शिक्षिका (Aarohi Neural)" : (lang === "hi" ? "🇮🇳 हिन्दी शिक्षिका (Swara Neural)" : "🇬🇧 English Teacher (Neerja Neural)");
        }

        try {
            const res = await fetch("/api/sql_video/synthesize_voice", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    preset_id: p.id,
                    language: lang,
                    text: p.question
                })
            });
            const data = await res.json();
            if (data.status === "success" && data.audio_url) {
                sqlShortState.audioUrl = data.audio_url;
                if (audioEl) {
                    attachAudioSyncListeners(audioEl);
                    audioEl.src = data.audio_url;
                    audioEl.load();
                    calibrateAudioDuration();
                }
            }
        } catch(e) {
            console.warn("Audio loading notice:", e);
        }
    }

    function setSqlAudioLang(lang) {
        sqlShortState.audioLang = lang;
        document.querySelectorAll(".sql-lang-btn").forEach(b => b.classList.remove("active"));
        const btn = document.getElementById("btnAudio" + lang.charAt(0).toUpperCase() + lang.slice(1));
        if (btn) btn.classList.add("active");
        
        loadPresetVoiceAudio();
        updateSqlBlueprintUI(sqlShortState.activePreset);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function setSqlTextStyle(style) {
        sqlShortState.textStyle = style;
        document.querySelectorAll(".sql-text-btn").forEach(b => b.classList.remove("active"));
        const btn = document.getElementById("btnText" + style.charAt(0).toUpperCase() + style.slice(1));
        if (btn) btn.classList.add("active");
        updateSqlBlueprintUI(sqlShortState.activePreset);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function toggleSqlAvatar(enabled) {
        sqlShortState.showAvatar = !!enabled;
        const btnOn = document.getElementById("btnAvatarToggleOn");
        const btnOff = document.getElementById("btnAvatarToggleOff");
        if (enabled) {
            if (btnOn) btnOn.classList.add("active");
            if (btnOff) btnOff.classList.remove("active");
        } else {
            if (btnOn) btnOn.classList.remove("active");
            if (btnOff) btnOff.classList.add("active");
        }
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function handleSqlPresetChange(val) {
        if (val === "custom") {
            const qEl = document.getElementById("sqlShortQuestion");
            if (qEl) qEl.value = "";
            const cEl = document.getElementById("sqlShortCodePreview");
            if (cEl) cEl.value = "";
            return;
        }
        const p = SQL_CLIENT_PRESETS[val];
        if (p) {
            sqlShortState.activePreset = p;
            const qEl = document.getElementById("sqlShortQuestion");
            if (qEl) qEl.value = p.question;
            const cEl = document.getElementById("sqlShortCodePreview");
            if (cEl) cEl.value = p.solution_sql || "";
            updateSqlBlueprintUI(p);
            loadPresetVoiceAudio();
            restartSqlShortPlay();
        }
    }

    function updateSqlBlueprintUI(p) {
        if (!p) return;
        const hookText = p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr || p.hook || "";
        const hookEl = document.getElementById("bpTimelineHook");
        if (hookEl) hookEl.innerText = hookText;
        const arrowEl = document.getElementById("bpArrowTarget");
        if (arrowEl) arrowEl.innerText = p.arrow_target || p.golden_rule || "OVER ()";
    }

    async function generateSqlShortBlueprint() {
        const q = document.getElementById("sqlShortQuestion").value.trim();
        const btn = document.getElementById("btnGenerateSqlBlueprint");
        if (!q) { alert("तुमचा मास्टर प्रॉम्प्ट किंवा प्रश्न प्रविष्ट करा (Please enter your master prompt or SQL question)!"); return; }

        btn.innerHTML = `<span>⏳ Synthesizing AI Video & Voice Blueprint...</span>`;
        btn.disabled = true;

        try {
            const res = await fetch("/api/sql_video/generate_prompt", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    question: q,
                    language: sqlShortState.audioLang || "mr"
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                const targetDur = data.max_duration_seconds || 56.0;
                sqlShortState.maxDuration = targetDur;
                const dynamicSpec = Object.assign({
                    id: data.id || "custom_ai",
                    content_type: data.content_type || "sql_query",
                    title: data.title || "SQL Interview Preparation",
                    difficulty: data.difficulty || "Core Interview",
                    question: data.question || q,
                    stages: data.stages || data.scenes || [],
                    scenes: data.stages || data.scenes || [],
                    outro_start: (data.outro_start !== undefined) ? data.outro_start : Math.max(0, targetDur - 3.5),
                    pipeline_stages: data.pipeline_stages || [],
                    sample_rows: data.sample_rows || [],
                    col_headers: data.col_headers || ["ID", "ATTRIBUTE", "AMOUNT", "STATUS"],
                    filter_evaluations: data.filter_evaluations || [],
                    output_rows: data.output_rows || [],
                    output_value: data.output_value || "",
                    pro_tip: data.pro_tip || "💡 Senior Interviewer Pro-Tip: Explain query logic step-by-step."
                }, data);
                sqlShortState.activeVideoSpec = dynamicSpec;
                sqlShortState.activePreset = dynamicSpec;

                // Update Code Preview
                const codePreviewEl = document.getElementById("sqlShortCodePreview");
                if (codePreviewEl) {
                    codePreviewEl.value = data.solution_sql || data.syntax_a_code || "-- Query solution";
                }

                // Load and play synthesized audio
                if (data.audio_url) {
                    sqlShortState.audioUrl = data.audio_url;
                    const audioEl = document.getElementById("sqlVoiceAudio");
                    if (audioEl) {
                        attachAudioSyncListeners(audioEl);
                        audioEl.src = data.audio_url;
                        audioEl.load();
                        calibrateAudioDuration();
                    }
                }

                updateSqlBlueprintUI(sqlShortState.activePreset);
                restartSqlShortPlay();
            } else {
                alert("Blueprint generation error: " + (data.message || "Failed"));
            }
        } catch (e) {
            console.warn("Using local generator fallback:", e);
        } finally {
            btn.innerHTML = `<span>✨ Generate AI Teacher Video &amp; Voice from Prompt</span>`;
            btn.disabled = false;
        }
    }

    function setSqlAvatarPresenter(val) {
        sqlShortState.selectedAvatar = val;
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    async function renderAiAvatarVideo() {
        const avatar = sqlShortState.selectedAvatar || "Nadim_public_5";
        const statusEl = document.getElementById("avatarRenderStatus");
        const btn = document.getElementById("btnRenderAvatar");

        const p = sqlShortState.activePreset;
        const promptText = (document.getElementById("sqlShortQuestion")?.value || "").trim();
        const script = (p && (p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr || p.speech_mr))
            || promptText.slice(0, 150)
            || "Welcome to today's tech masterclass with Code with Mangesh!";

        statusEl.style.display = "block";
        statusEl.style.color = "#38BDF8";
        statusEl.innerHTML = `<span>⚡ Submitting to Autonomous Avatar Router (Auto-failover HeyGen ➔ D-ID ➔ Cyber Canvas)...</span>`;
        btn.disabled = true;

        try {
            const preferred = avatar.startsWith("did") ? "did" : (avatar !== "none" ? "heygen" : "auto");
            const res = await fetch("/api/video/avatar_cascade", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    script: script,
                    preferred_provider: preferred,
                    avatar_id: avatar.startsWith("did") ? null : avatar,
                    language: sqlShortState.audioLang
                })
            });
            const data = await res.json();

            if (data.status === "success") {
                if (data.provider === "HeyGen" && data.video_id) {
                    const failoverTag = data.failover_used ? " (Auto-switched)" : "";
                    statusEl.innerHTML = `<span>✅ HeyGen 4K Video #${data.video_id} queued${failoverTag}! Generating lip-sync...</span>`;
                    pollHeyGenVideo(data.video_id, statusEl, btn);
                } else if (data.provider === "D-ID" && data.talk_id) {
                    const failoverTag = data.failover_used ? " (Auto-switched from HeyGen)" : "";
                    statusEl.innerHTML = `<span>✅ D-ID Talk #${data.talk_id} queued${failoverTag}! Generating lip-sync...</span>`;
                    pollDIDVideo(data.talk_id, statusEl, btn);
                } else {
                    btn.disabled = false;
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `🛡️ <b>Live Cyber Avatar Active:</b> Auto-switched to High-Tech Presenter with zero watermark!`;
                }
            } else {
                statusEl.style.color = "#EF4444";
                statusEl.innerText = "Router Error: " + (data.message || "Failed");
                btn.disabled = false;
            }
        } catch (e) {
            statusEl.style.color = "#EF4444";
            statusEl.innerText = "Network Error: " + e.message;
            btn.disabled = false;
        }
    }

    function loadAvatarVideoToEngine(url) {
        let vid = document.getElementById("sqlShortAvatarVideo");
        if (!vid) {
            vid = document.createElement("video");
            vid.id = "sqlShortAvatarVideo";
            vid.crossOrigin = "anonymous";
            vid.loop = true;
            vid.muted = true;
            vid.playsInline = true;
            vid.style.display = "none";
            document.body.appendChild(vid);
        }
        vid.src = url;
        vid.onloadeddata = () => {
            sqlShortState.avatarVideoElement = vid;
            sqlShortState.avatarVideoLoaded = true;
            vid.play().catch(e => console.warn("Avatar video autoplay:", e));
            renderSqlShortFrame(sqlShortState.currentTime);
        };
        vid.load();
    }

    async function pollHeyGenVideo(videoId, statusEl, btn) {
        let attempts = 0;
        const maxAttempts = 25;
        const interval = setInterval(async () => {
            attempts++;
            try {
                let res = await fetch(`/api/heygen/status/${videoId}`);
                if (!res.ok) res = await fetch(`/api/video/heygen/status/${videoId}`);
                const data = await res.json();
                if (data.status === "completed" && data.video_url) {
                    clearInterval(interval);
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `<span>🎉 HeyGen 4K Avatar Ready! Synced to Video Player.</span>`;
                    btn.disabled = false;
                    loadAvatarVideoToEngine(data.video_url);
                } else if (data.status === "failed") {
                    clearInterval(interval);
                    statusEl.style.color = "#EF4444";
                    statusEl.innerText = "HeyGen Generation Failed: " + (data.error || "Unknown");
                    btn.disabled = false;
                } else {
                    statusEl.innerText = `⏳ HeyGen Rendering: ${data.status || 'processing'} (${attempts}/${maxAttempts})...`;
                }
            } catch (e) {
                console.warn("HeyGen Poll error:", e);
            }
            if (attempts >= maxAttempts) {
                clearInterval(interval);
                statusEl.style.color = "#F59E0B";
                statusEl.innerText = "HeyGen took longer than expected. Using High-Tech Cyber Canvas Presenter.";
                btn.disabled = false;
            }
        }, 3000);
    }

    async function pollDIDVideo(talkId, statusEl, btn) {
        let attempts = 0;
        const maxAttempts = 25;
        const interval = setInterval(async () => {
            attempts++;
            try {
                let res = await fetch(`/api/did/status/${talkId}`);
                if (!res.ok) res = await fetch(`/api/video/did/status/${talkId}`);
                const data = await res.json();
                if (data.status === "done" && data.result_url) {
                    clearInterval(interval);
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `<span>🎉 D-ID Lip-Sync Ready! Synced to Video Player.</span>`;
                    btn.disabled = false;
                    loadAvatarVideoToEngine(data.result_url);
                } else if (data.status === "error") {
                    clearInterval(interval);
                    statusEl.style.color = "#EF4444";
                    statusEl.innerText = "D-ID Generation Error: " + (data.error || "Unknown");
                    btn.disabled = false;
                } else {
                    statusEl.innerText = `⏳ D-ID Rendering: ${data.status || 'started'} (${attempts}/${maxAttempts})...`;
                }
            } catch (e) {
                console.warn("D-ID Poll error:", e);
            }
            if (attempts >= maxAttempts) {
                clearInterval(interval);
                statusEl.style.color = "#F59E0B";
                statusEl.innerText = "D-ID took longer than expected. Using High-Tech Cyber Canvas Presenter.";
                btn.disabled = false;
            }
        }, 2500);
    }

    async function renderCinematicBackgroundVideo() {
        const bgChoice = document.getElementById("sqlCinematicBgSelect")?.value || "cyber_matrix";
        const statusEl = document.getElementById("cinematicBgRenderStatus");
        const btn = document.getElementById("btnRenderCinematicBg");

        if (bgChoice === "cyber_matrix") {
            sqlShortState.backgroundVideoElement = null;
            sqlShortState.backgroundVideoLoaded = false;
            statusEl.style.display = "block";
            statusEl.style.color = "#10B981";
            statusEl.innerText = "⚡ Using Transparent Cyber Glass Canvas (Ultra-Fast 60 FPS)";
            renderSqlShortFrame(sqlShortState.currentTime);
            return;
        }

        statusEl.style.display = "block";
        statusEl.style.color = "#C084FC";
        statusEl.innerHTML = `<span>⏳ Synthesizing 3D Motion Video (Runway Gen-4 / Luma)...</span>`;
        btn.disabled = true;

        try {
            const isLuma = bgChoice.startsWith("luma");
            const endpoint = isLuma ? "/api/video/luma_cascade" : "/api/runway/generate";
            const promptText = isLuma 
                ? "3D cinematic golden tech database particles flowing vertically in dark cyberspace, 9:16 aspect ratio, volumetric lighting, 4k"
                : "Hyper-realistic high-tech server room and cloud analytics cluster, glowing neon cyan data racks, server status lights, 9:16 vertical view, photorealistic, 8k";

            const res = await fetch(endpoint, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ prompt: promptText, aspect_ratio: "9:16" })
            });
            const data = await res.json();
            if (data.status === "success") {
                statusEl.style.color = "#10B981";
                statusEl.innerHTML = `<span>✅ 3D Motion Generation Queued! Polling stream...</span>`;
                btn.disabled = false;
            } else {
                statusEl.style.color = "#EF4444";
                statusEl.innerText = "Motion Engine: " + (data.message || "Failed");
                btn.disabled = false;
            }
        } catch (e) {
            statusEl.style.color = "#EF4444";
            statusEl.innerText = "Network Error: " + e.message;
            btn.disabled = false;
        }
    }

    async function runInMemorySqlSandbox() {
        const code = document.getElementById("sqlShortCodePreview").value;
        const p = sqlShortState.activePreset;
        const latencyEl = document.getElementById("sandboxLatency");
        const outTableEl = document.getElementById("sandboxOutputTable");

        latencyEl.innerText = "Executing...";
        try {
            const res = await fetch("/api/sql_video/run_sandbox", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    schema_sql: p.schema_sql,
                    query_sql: code
                })
            });
            const data = await res.json();
            latencyEl.innerText = `⏱️ ${data.latency_ms || 1.2} ms (SQLite In-Memory)`;

            if (data.status === "success" && data.columns && data.rows) {
                let html = `<table style="width:100%; border-collapse:collapse; text-align:left;">`;
                html += `<thead><tr style="border-bottom:1px solid #1E2D4A; color:#38BDF8;">`;
                data.columns.forEach(c => html += `<th style="padding:4px 6px;">${c}</th>`);
                html += `</tr></thead><tbody>`;
                data.rows.forEach(r => {
                    html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">`;
                    r.forEach(v => html += `<td style="padding:4px 6px; color:#F8FAFC;">${v}</td>`);
                    html += `</tr>`;
                });
                html += `</tbody></table>`;
                outTableEl.innerHTML = html;
            } else {
                outTableEl.innerHTML = `<span style="color:#EF4444;">Error: ${data.message || 'Execution failed'}</span>`;
            }
        } catch (e) {
            latencyEl.innerText = "Error";
            outTableEl.innerHTML = `<span style="color:#EF4444;">Sandbox Error: ${e.message}</span>`;
        }
    }

    /* ==========================================================================
       3D HIGH-TECH GLASSMORPHISM & DYNAMIC MOTION VECTOR ENGINE
       ========================================================================== */
    let _sqlCyberAudioCtx = null;
    function playCyberBleep(freq = 880, dur = 0.08) {
        try {
            if (!_sqlCyberAudioCtx) {
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (AudioCtx) _sqlCyberAudioCtx = new AudioCtx();
            }
            if (_sqlCyberAudioCtx && _sqlCyberAudioCtx.state === 'suspended') {
                _sqlCyberAudioCtx.resume();
            }
            if (!_sqlCyberAudioCtx) return;
            const osc = _sqlCyberAudioCtx.createOscillator();
            const gain = _sqlCyberAudioCtx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(freq, _sqlCyberAudioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(freq * 1.4, _sqlCyberAudioCtx.currentTime + dur);
            gain.gain.setValueAtTime(0.04, _sqlCyberAudioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, _sqlCyberAudioCtx.currentTime + dur);
            osc.connect(gain);
            gain.connect(_sqlCyberAudioCtx.destination);
            osc.start();
            osc.stop(_sqlCyberAudioCtx.currentTime + dur);
        } catch (e) {}
    }

    // 1. Draw 3D Frosted Crystal Glass Tile with Specular Rim & Depth Layering
    function drawGlassTile(ctx, x, y, w, h, radius = 20, glowColor = "#38BDF8", elevation = false, isFront = true, alpha = 1.0) {
        ctx.save();
        ctx.globalAlpha = Math.max(0, Math.min(1.0, alpha));

        // Depth perspective scaling
        if (!isFront) {
            const cx = x + w / 2;
            const cy = y + h / 2;
            ctx.translate(cx, cy);
            ctx.scale(0.93, 0.93);
            ctx.translate(-cx, -cy);
            ctx.globalAlpha *= 0.38;
        } else if (elevation) {
            const cx = x + w / 2;
            const cy = y + h / 2;
            ctx.translate(cx, cy);
            ctx.scale(1.015, 1.015);
            ctx.translate(-cx, -cy);
        }

        // Frosted Glass Body Gradient (Grey/Navy Translucent Mirror)
        const grad = ctx.createLinearGradient(x, y, x + w * 0.3, y + h);
        if (isFront) {
            grad.addColorStop(0, "rgba(255, 255, 255, 0.09)");
            grad.addColorStop(0.2, "rgba(22, 33, 62, 0.78)");
            grad.addColorStop(0.8, "rgba(10, 16, 34, 0.88)");
            grad.addColorStop(1, "rgba(6, 10, 22, 0.94)");
        } else {
            grad.addColorStop(0, "rgba(255, 255, 255, 0.04)");
            grad.addColorStop(1, "rgba(12, 18, 36, 0.55)");
        }

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, y, w, h, radius);
        ctx.fill();

        // Glowing border
        if (isFront && glowColor) {
            ctx.shadowColor = glowColor;
            ctx.shadowBlur = elevation ? 26 : 12;
            ctx.strokeStyle = glowColor;
            ctx.lineWidth = elevation ? 3.5 : 2.0;
        } else {
            ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
            ctx.lineWidth = 1.5;
        }
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Specular Mirror Top Reflection Line (Crystal Clear Bevel Effect)
        if (isFront) {
            const specGrad = ctx.createLinearGradient(x + 20, y + 2, x + w - 20, y + 2);
            specGrad.addColorStop(0, "rgba(255, 255, 255, 0.0)");
            specGrad.addColorStop(0.25, "rgba(255, 255, 255, 0.55)");
            specGrad.addColorStop(0.75, "rgba(255, 255, 255, 0.55)");
            specGrad.addColorStop(1, "rgba(255, 255, 255, 0.0)");
            ctx.strokeStyle = specGrad;
            ctx.lineWidth = 2.0;
            ctx.beginPath();
            ctx.moveTo(x + 25, y + 2);
            ctx.lineTo(x + w - 25, y + 2);
            ctx.stroke();

            // Cyber corner crosshairs (+)
            ctx.fillStyle = "rgba(56, 189, 248, 0.5)";
            ctx.font = "14px monospace";
            ctx.fillText("+", x + 12, y + 20);
            ctx.fillText("+", x + w - 20, y + 20);
        }

        ctx.restore();
    }

    // 2. Draw Dynamic Animated Laser Connector with Traveling Photon Energy Pulse
    function drawDynamicConnector(ctx, x1, y1, x2, y2, color = "#38BDF8", t = 0, label = "") {
        ctx.save();
        const midY = (y1 + y2) / 2;

        // Glowing dashed laser path
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.setLineDash([10, 8]);
        ctx.lineDashOffset = -t * 40;
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.bezierCurveTo(x1, midY, x2, midY, x2, y2);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.shadowBlur = 0;

        // Traveling Photon Energy Particle (Light Spark Pulse)
        const u = (t * 0.9) % 1.0;
        const pu = 1 - u;
        const px = pu * pu * pu * x1 + 3 * pu * pu * u * x1 + 3 * pu * u * u * x2 + u * u * u * x2;
        const py = pu * pu * pu * y1 + 3 * pu * pu * u * midY + 3 * pu * u * u * midY + u * u * u * y2;

        ctx.save();
        ctx.shadowColor = "#FFFFFF";
        ctx.shadowBlur = 16;
        ctx.fillStyle = "#FFFFFF";
        ctx.beginPath();
        ctx.arc(px, py, 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(px, py, 11, 0, Math.PI * 2);
        ctx.globalAlpha = 0.5;
        ctx.fill();
        ctx.restore();

        // Arrowhead at destination
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(x2, y2);
        ctx.lineTo(x2 - 10, y2 - 16);
        ctx.lineTo(x2 + 10, y2 - 16);
        ctx.closePath();
        ctx.fill();

        // Optional Central Glass Pill Label
        if (label) {
            const lx = (x1 + x2) / 2;
            const ly = midY;
            ctx.fillStyle = "rgba(10, 16, 32, 0.92)";
            ctx.beginPath();
            ctx.roundRect(lx - 120, ly - 18, 240, 36, 18);
            ctx.fill();
            ctx.strokeStyle = color;
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.fillStyle = color;
            ctx.font = "bold 16px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(label, lx, ly + 6);
            ctx.textAlign = "left";
        }
        ctx.restore();
    }

    // 3. Draw Dynamic Architectural Pipeline (Table -> Window -> Filter -> Output)
    function drawArchitecturePipeline(ctx, x, y, w, h, stages, activeIndex = 0, t = 0) {
        ctx.save();
        const stageW = (w - (stages.length - 1) * 20) / stages.length;

        stages.forEach((st, idx) => {
            const sx = x + idx * (stageW + 20);
            const isActive = idx === activeIndex;
            const isDone = idx < activeIndex;
            const nodeColor = isActive ? "#38BDF8" : (isDone ? "#10B981" : "#64748B");

            // Glass Node Tile
            drawGlassTile(ctx, sx, y, stageW, h, 14, nodeColor, isActive, true, isActive ? 1.0 : 0.75);

            // Icon + Label
            ctx.fillStyle = nodeColor;
            ctx.font = "bold 22px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(st.icon, sx + stageW / 2, y + 36);

            ctx.fillStyle = isActive ? "#FFFFFF" : (isDone ? "#10B981" : "#94A3B8");
            ctx.font = isActive ? "bold 15px monospace" : "14px monospace";
            ctx.fillText(st.name, sx + stageW / 2, y + 66);

            if (st.sub) {
                ctx.fillStyle = isActive ? "#38BDF8" : "#64748B";
                ctx.font = "12px 'Segoe UI', sans-serif";
                ctx.fillText(st.sub, sx + stageW / 2, y + 86);
            }

            // Arrow connector to next
            if (idx < stages.length - 1) {
                const arrX = sx + stageW + 10;
                ctx.fillStyle = isDone ? "#10B981" : "rgba(255, 255, 255, 0.3)";
                ctx.font = "bold 20px monospace";
                ctx.fillText("▶", arrX, y + h / 2 + 6);
            }
        });
        ctx.textAlign = "left";
        ctx.restore();
    }

    // 4. Draw Dynamic Micro-Sparks Burst (Photon Energy Burst)
    function drawPhotonSparks(ctx, cx, cy, color = "#38BDF8", t = 0) {
        ctx.save();
        const sparkCount = 8;
        for (let i = 0; i < sparkCount; i++) {
            const angle = (i / sparkCount) * Math.PI * 2 + (t * 2.0);
            const dist = 18 + Math.sin(t * 8 + i) * 12;
            const sx = cx + Math.cos(angle) * dist;
            const sy = cy + Math.sin(angle) * dist;
            const r = 2.5 + Math.sin(t * 10 + i) * 1.5;

            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(sx, sy, Math.max(1, r), 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();
    }

    // Helper: Dynamic Client Pipeline Stages Generator
    function getClientPipelineStages(p) {
        if (p.pipeline_stages && Array.isArray(p.pipeline_stages) && p.pipeline_stages.length >= 3) {
            return p.pipeline_stages;
        }
        const sql = (p.solution_sql || "").toUpperCase();
        const q = (p.question || "").toUpperCase();
        if (sql.includes("NTILE") || q.includes("TOP 10%")) {
            return [
                {icon: "📁", name: p.table_name || "TRANSACTIONS", sub: "Raw Dataset"},
                {icon: "🧮", name: "SUM() / CTE", sub: "Aggregate Totals"},
                {icon: "📊", name: "NTILE(10)", sub: "10-Bucketing"},
                {icon: "🎯", name: "QUALIFY = 1", sub: "Top 10% Filter"}
            ];
        }
        if (sql.includes("ROW_NUMBER") || sql.includes("QUALIFY") || q.includes("LATEST")) {
            return [
                {icon: "📁", name: p.table_name || "TRANSACTIONS", sub: "Raw Rows"},
                {icon: "🪟", name: "PARTITION BY", sub: "Customer Key"},
                {icon: "🔢", name: "ROW_NUMBER()", sub: "Date DESC"},
                {icon: "🎯", name: "QUALIFY = 1", sub: "Latest Record"}
            ];
        }
        if (sql.includes("DENSE_RANK")) {
            return [
                {icon: "📁", name: p.table_name || "EMPLOYEES", sub: "Raw Records"},
                {icon: "🔢", name: "DENSE_RANK()", sub: "Ordered Ranks"},
                {icon: "🛡️", name: "TIE HANDLING", sub: "No Rank Skips"},
                {icon: "🎯", name: "WHERE RNK = 2", sub: "Target Value"}
            ];
        }
        if (sql.includes("LAG") || sql.includes("LEAD")) {
            return [
                {icon: "📁", name: p.table_name || "DATA", sub: "Time Series"},
                {icon: "⏮️", name: "LAG() WINDOW", sub: "Offset Fetch"},
                {icon: "🧮", name: "DELTA / RATIO", sub: "Difference"},
                {icon: "🎯", name: "FLAGGED ROWS", sub: "Trigger Condition"}
            ];
        }
        if (sql.includes("JOIN")) {
            return [
                {icon: "📁", name: "TABLE A", sub: "Left Source"},
                {icon: "📁", name: "TABLE B", sub: "Right Source"},
                {icon: "⚡", name: "JOIN ON KEY", sub: "Record Match"},
                {icon: "🎯", name: "RESULT SET", sub: "Merged Output"}
            ];
        }
        if (sql.includes("GROUP BY")) {
            return [
                {icon: "📁", name: p.table_name || "RECORDS", sub: "Input Rows"},
                {icon: "🪟", name: "GROUP BY", sub: "Cluster Keys"},
                {icon: "🧮", name: "AGGREGATE", sub: "SUM/COUNT/AVG"},
                {icon: "🎯", name: "HAVING FILTER", sub: "Filtered Groups"}
            ];
        }
        return [
            {icon: "📁", name: p.table_name || "INPUT_TABLE", sub: "All Records"},
            {icon: "⚡", name: "SUBQUERY / CTE", sub: "Compute Logic"},
            {icon: "🛡️", name: "FILTER / EXCLUSION", sub: "Condition Logic"},
            {icon: "🎯", name: "TARGET OUTPUT", sub: "Final Selection"}
        ];
    }

    // Helper: Dynamic Client Filter Evaluations Generator
    function getClientFilterEvals(p) {
        if (p.filter_evaluations && Array.isArray(p.filter_evaluations) && p.filter_evaluations.length > 0) {
            return p.filter_evaluations;
        }
        if (p.sample_rows && Array.isArray(p.sample_rows) && p.sample_rows.length > 0) {
            return p.sample_rows.slice(0, 5).map((r, i) => {
                const isTarget = r.is_target !== undefined ? r.is_target : (i === 0 || i === 2 || (r.balance && (r.balance.includes("🎯") || r.balance.includes("1"))));
                return {
                    name: r.account || ("Record #" + (i + 1)),
                    salary: r.amt || r.date || "Val",
                    cond: isTarget ? "MATCH = TRUE" : "MATCH = FALSE",
                    res: isTarget ? "TRUE" : "FALSE",
                    action: isTarget ? "KEEP" : "EXCLUDE",
                    status: isTarget ? "keep" : "exclude"
                };
            });
        }
        return [
            {name: "Row 1", salary: "Val 1", cond: "Condition = TRUE", res: "TRUE", action: "KEEP", status: "keep"},
            {name: "Row 2", salary: "Val 2", cond: "Condition = FALSE", res: "FALSE", action: "EXCLUDE", status: "exclude"},
            {name: "Row 3", salary: "Val 3", cond: "Condition = TRUE", res: "TRUE", action: "KEEP", status: "keep"}
        ];
    }

    /* ==========================================================================
       THEORY & CONCEPTUAL MASTER STORYBOARD (1080 x 1920 9:16)
       ========================================================================== */
    function renderTheoryShortStoryboard(ctx, W, H, p, t, currentStageIdx, activeStage, isOutro, outroStart, stageProg, stageAlpha) {
        // SCENE 7 (Outro Branding): Rendered ONLY when isOutro is true!
        if (isOutro) {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            // Senior Interviewer Pro-Tip Card
            ctx.fillStyle = "rgba(139, 92, 246, 0.16)";
            ctx.beginPath();
            ctx.roundRect(60, 220, W - 120, 620, 22);
            ctx.fill();
            ctx.strokeStyle = "#8B5CF6";
            ctx.lineWidth = 3.5;
            ctx.shadowColor = "rgba(139, 92, 246, 0.35)";
            ctx.shadowBlur = 18;
            ctx.stroke();
            ctx.shadowBlur = 0;

            ctx.fillStyle = "#8B5CF6";
            ctx.font = "bold 32px 'Segoe UI', sans-serif";
            ctx.fillText("💡 SENIOR FAANG INTERVIEWER PRO-TIP:", 90, 280);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("1️⃣ Production Query Optimization:", 90, 340);
            ctx.fillStyle = "#C7D2FE";
            ctx.font = "22px 'Segoe UI', sans-serif";
            ctx.fillText("   Never put a non-aggregated filter in HAVING!", 90, 380);
            ctx.fillText("   Putting it in WHERE allows the optimizer to use B-Tree indexes.", 90, 420);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("2️⃣ Universal ANSI SQL Portability:", 90, 480);
            ctx.fillStyle = "#C7D2FE";
            ctx.font = "22px 'Segoe UI', sans-serif";
            ctx.fillText("   This execution model is identical across Snowflake, PostgreSQL,", 90, 520);
            ctx.fillText("   Oracle, MySQL, and Microsoft SQL Server.", 90, 560);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("3️⃣ Key Interviewer Impress Point:", 90, 620);
            ctx.fillStyle = "#10B981";
            ctx.font = "bold 22px monospace";
            ctx.fillText(`   ${p.pro_tip || "Filter early with WHERE to minimize memory footprint!"}`, 90, 665);

            // Outro Branding Card (@Code_With_Mangesh)
            drawGlassTile(ctx, 60, 870, W - 120, 630, 24, "#F59E0B", true, true, 1.0);

            ctx.fillStyle = "#F59E0B";
            ctx.font = "bold 44px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("👑 @Code_With_Mangesh", W / 2, 950);

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("FAANG & Top MNC SQL Interview Preparation Studio", W / 2, 1005);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "28px 'Segoe UI', sans-serif";
            ctx.fillText("⭐ SAVE THIS REEL FOR YOUR UPCOMING INTERVIEWS!", W / 2, 1100);
            ctx.fillText("🔔 Follow @Code_With_Mangesh for daily SQL questions", W / 2, 1160);

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("🚀 100% Free AI High-Tech Education for Every Student!", W / 2, 1260);

            ctx.fillStyle = "#94A3B8";
            ctx.font = "italic 22px 'Segoe UI', sans-serif";
            ctx.fillText("Empowering students from rural to global tech careers", W / 2, 1320);

            drawPhotonSparks(ctx, W / 2 - 280, 950, "#F59E0B", t);
            drawPhotonSparks(ctx, W / 2 + 280, 950, "#F59E0B", t);

            ctx.textAlign = "left";
            ctx.restore();
            return;
        }

        // SCENE 1: THEORY TOPIC & CONCEPT INTRODUCTION
        if (currentStageIdx === 1) {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            drawGlassTile(ctx, 60, 220, W - 120, 230, 20, "#38BDF8", true, true, 1.0);

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 28px 'Segoe UI', sans-serif";
            ctx.fillText("📋 SQL THEORY INTERVIEW TOPIC:", 90, 275);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            const qLines = wrapCanvasText(ctx, p.question, W - 180);
            qLines.slice(0, 3).forEach((l, i) => {
                ctx.fillText(l, 90, 325 + i * 38);
            });

            // Target Highlight Badge
            const pulse = 1.0 + Math.sin(t * 6) * 0.05;
            ctx.save();
            ctx.translate(W / 2, 490);
            ctx.scale(pulse, pulse);
            ctx.fillStyle = "rgba(245, 158, 11, 0.2)";
            ctx.beginPath();
            ctx.roundRect(-300, -24, 600, 48, 14);
            ctx.fill();
            ctx.strokeStyle = "#F59E0B";
            ctx.lineWidth = 2.5;
            ctx.stroke();
            ctx.fillStyle = "#F59E0B";
            ctx.font = "bold 20px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("🎯 TARGET: QUERY EXECUTION LIFECYCLE & CORE MECHANISM", 0, 7);
            ctx.restore();

            // Architectural Overview Glass Container
            drawGlassTile(ctx, 60, 540, W - 120, 410, 20, "#10B981", false, true, 1.0);

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("🧠 CORE ARCHITECTURAL DEFINITION:", 90, 590);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            const defLines = wrapCanvasText(ctx, p.concept_summary || "WHERE filters individual rows before grouping; HAVING filters aggregated groups after GROUP BY.", W - 180);
            defLines.forEach((l, i) => {
                ctx.fillText(l, 90, 645 + i * 38);
            });

            drawGlassTile(ctx, 90, 780, 420, 50, 10, "#38BDF8", false, true, 0.85);
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 20px monospace";
            ctx.fillText("1. WHERE: ROW-LEVEL FILTER", 110, 812);

            drawGlassTile(ctx, 530, 780, 420, 50, 10, "#10B981", false, true, 0.85);
            ctx.fillStyle = "#10B981";
            ctx.font = "bold 20px monospace";
            ctx.fillText("2. HAVING: GROUP-LEVEL FILTER", 550, 812);

            drawGlassTile(ctx, 60, 980, W - 120, 500, 20, "rgba(255, 255, 255, 0.15)", false, false, 0.9);

            ctx.fillStyle = "#1E293B";
            ctx.fillRect(60, 980, W - 120, 50);
            ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 1005, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 1005, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 1005, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#94A3B8";
            ctx.font = "bold 20px monospace";
            ctx.fillText("theory_roadmap.sql — Step-by-Step Understanding", 180, 1012);

            ctx.fillStyle = "#64748B";
            ctx.font = "italic 24px monospace";
            ctx.fillText("/* Step 1: Understand why interviewers ask this question */", 90, 1080);
            ctx.fillText("/* Step 2: Grasp database query execution order (ANSI SQL) */", 90, 1140);
            ctx.fillText("/* Step 3: Compare code syntax & aggregate functions */", 90, 1200);
            ctx.fillText("/* Step 4: Avoid the fatal interview traps & score bonus points! */", 90, 1260);

            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.beginPath();
            ctx.roundRect(90, 1370, W - 180, 80, 14);
            ctx.fill();
            ctx.strokeStyle = "#38BDF8";
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 22px 'Segoe UI', sans-serif";
            ctx.fillText("🧠 LEARNING GOAL: Master the difference & explain with confidence!", 120, 1420);

            ctx.restore();
        }

        // SCENE 2: CANDIDATE CONFUSION & WHY INTERVIEWERS TEST THIS
        else if (currentStageIdx === 2) {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            ctx.fillStyle = "rgba(239, 68, 68, 0.18)";
            ctx.beginPath();
            ctx.roundRect(60, 220, W - 120, 100, 16);
            ctx.fill();
            ctx.strokeStyle = "#EF4444";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#EF4444";
            ctx.font = "bold 28px 'Segoe UI', sans-serif";
            ctx.fillText("⚠️ THE COMMON CONFUSION: WHY 90% OF CANDIDATES STUMBLE", 90, 268);
            ctx.fillStyle = "#F8FAFC";
            ctx.font = "20px 'Segoe UI', sans-serif";
            ctx.fillText("Both WHERE and HAVING filter data — but WHEN and WHAT do they filter?", 90, 302);

            ctx.fillStyle = "rgba(239, 68, 68, 0.12)";
            ctx.beginPath();
            ctx.roundRect(60, 345, W - 120, 320, 18);
            ctx.fill();
            ctx.strokeStyle = "#EF4444";
            ctx.lineWidth = 2.5;
            ctx.stroke();

            ctx.fillStyle = "#EF4444";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("❌ WHY CANDIDATES GET CONFUSED:", 90, 390);

            ctx.fillStyle = "#CBD5E1";
            ctx.font = "23px 'Segoe UI', sans-serif";
            ctx.fillText("• Candidates see boolean conditions in both and assume they are interchangeable.", 90, 440);
            ctx.fillText("• Writing 'WHERE COUNT(*) > 2' causes an instant SQL syntax error!", 90, 490);
            ctx.fillText("• Writing 'HAVING salary > 50000' without GROUP BY wastes CPU memory!", 90, 540);

            ctx.fillStyle = "rgba(16, 185, 129, 0.15)";
            ctx.beginPath();
            ctx.roundRect(60, 690, W - 120, 420, 18);
            ctx.fill();
            ctx.strokeStyle = "#10B981";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("✅ THE CORE DISTINCTION SENIOR INTERVIEWERS TEST:", 90, 740);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("1️⃣ WHERE CLAUSE — PRE-FILTER (ROW LEVEL)", 90, 800);
            ctx.fillStyle = "#94A3B8";
            ctx.font = "22px 'Segoe UI', sans-serif";
            ctx.fillText("   Filters individual rows BEFORE the database groups or aggregates them.", 90, 840);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("2️⃣ HAVING CLAUSE — POST-FILTER (GROUP LEVEL)", 90, 910);
            ctx.fillStyle = "#94A3B8";
            ctx.font = "22px 'Segoe UI', sans-serif";
            ctx.fillText("   Filters aggregated buckets AFTER GROUP BY has assembled the groups.", 90, 950);

            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.beginPath();
            ctx.roundRect(60, 1140, W - 120, 340, 18);
            ctx.fill();
            ctx.strokeStyle = "#38BDF8";
            ctx.lineWidth = 2.5;
            ctx.stroke();

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("💡 PERFORMANCE BENEFIT IN PRODUCTION:", 90, 1195);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "24px 'Segoe UI', sans-serif";
            ctx.fillText("• Filtering rows with WHERE reduces the row count BEFORE grouping.", 90, 1255);
            ctx.fillText("• In large tables with 10M rows, this slashes RAM usage by over 90%!", 90, 1315);
            ctx.fillText("• Next: Let's see the step-by-step query execution lifecycle!", 90, 1375);

            ctx.restore();
        }

        // SCENE 3: QUERY EXECUTION LIFECYCLE FLOWCHART
        else if (currentStageIdx === 3) {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            ctx.fillStyle = "rgba(99, 102, 241, 0.15)";
            ctx.beginPath();
            ctx.roundRect(60, 220, W - 120, 95, 16);
            ctx.fill();
            ctx.strokeStyle = "#818CF8";
            ctx.lineWidth = 2.5;
            ctx.stroke();

            ctx.fillStyle = "#818CF8";
            ctx.font = "bold 28px 'Segoe UI', sans-serif";
            ctx.fillText("⚙️ DATABASE ENGINE QUERY EXECUTION LIFECYCLE (ANSI SQL)", 90, 265);
            ctx.fillStyle = "#CBD5E1";
            ctx.font = "20px 'Segoe UI', sans-serif";
            ctx.fillText("How the database engine executes clauses in strict logical sequence:", 90, 296);

            const pipeline = [
                { num: "1️⃣", stage: "FROM & JOIN", desc: "Loads target tables & resolves joins into memory buffer", color: "#38BDF8" },
                { num: "2️⃣", stage: "WHERE (ROW-LEVEL FILTER)", desc: "⚡ Prunes rows BEFORE grouping (Indexes are used!)", color: "#F59E0B" },
                { num: "3️⃣", stage: "GROUP BY & AGGREGATION", desc: "Clusters remaining rows & computes SUM, COUNT, AVG", color: "#EC4899" },
                { num: "4️⃣", stage: "HAVING (GROUP-LEVEL FILTER)", desc: "🎯 Filters entire groups failing aggregate conditions", color: "#10B981" }
            ];

            const activePipelineIdx = Math.min(pipeline.length - 1, Math.floor(stageProg * pipeline.length));

            pipeline.forEach((st, idx) => {
                const boxY = 335 + idx * 195;
                const isActive = idx === activePipelineIdx;

                ctx.fillStyle = isActive ? "rgba(15, 23, 42, 0.98)" : "rgba(15, 23, 42, 0.8)";
                ctx.beginPath();
                ctx.roundRect(60, boxY, W - 120, 130, 16);
                ctx.fill();

                ctx.strokeStyle = isActive ? st.color : "#1E2D4A";
                ctx.lineWidth = isActive ? 3.5 : 2;
                if (isActive) {
                    ctx.shadowColor = st.color;
                    ctx.shadowBlur = 18;
                }
                ctx.stroke();
                ctx.shadowBlur = 0;

                ctx.fillStyle = st.color;
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText(`${st.num} ${st.stage}`, 90, boxY + 45);

                ctx.fillStyle = isActive ? "#F8FAFC" : "#94A3B8";
                ctx.font = "bold 22px monospace";
                ctx.fillText(st.desc, 90, boxY + 95);

                if (idx < 3) {
                    ctx.fillStyle = "#818CF8";
                    ctx.font = "bold 32px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("↓", W / 2, boxY + 168);
                    ctx.textAlign = "left";
                }
            });

            ctx.fillStyle = "rgba(16, 185, 129, 0.15)";
            ctx.beginPath();
            ctx.roundRect(60, 1140, W - 120, 360, 18);
            ctx.fill();
            ctx.strokeStyle = "#10B981";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("🎯 THE KEY TAKEAWAY FOR INTERVIEWS:", 90, 1195);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "24px 'Segoe UI', sans-serif";
            ctx.fillText("• WHERE executes at Step 2; HAVING executes at Step 4!", 90, 1255);
            ctx.fillText("• Because WHERE runs before GROUP BY, it CANNOT evaluate aggregates.", 90, 1315);
            ctx.fillText("• Next: Let's see the code syntax comparison side by side!", 90, 1375);

            ctx.restore();
        }

        // SCENE 4: SIDE-BY-SIDE SQL SYNTAX COMPARISON
        else if (currentStageIdx === 4) {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            drawGlassTile(ctx, 60, 220, W - 120, 520, 20, "#38BDF8", true, true, 1.0);

            ctx.fillStyle = "#1E293B";
            ctx.fillRect(60, 220, W - 120, 48);
            ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 244, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 244, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 244, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 20px monospace";
            ctx.fillText(p.syntax_a_title || "WHERE CLAUSE SYNTAX (ROW FILTER)", 180, 252);

            const codeALines = (p.syntax_a_code || "SELECT name, department, salary\nFROM employees\nWHERE salary > 50000;").split("\n");
            codeALines.forEach((ln, idx) => {
                const lineY = 320 + idx * 56;
                ctx.fillStyle = "#475569";
                ctx.font = "bold 24px monospace";
                ctx.fillText((idx + 1).toString().padStart(2, "0"), 90, lineY);
                renderSqlSyntaxLine(ctx, ln, 160, lineY);
            });

            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.fillRect(90, 580, W - 180, 130);
            ctx.strokeStyle = "#38BDF8";
            ctx.strokeRect(90, 580, W - 180, 130);
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 22px 'Segoe UI', sans-serif";
            ctx.fillText("⚡ ROW-LEVEL ATTRIBUTE: 'salary > 50000'", 120, 625);
            ctx.fillStyle = "#F8FAFC";
            ctx.font = "20px 'Segoe UI', sans-serif";
            ctx.fillText("Evaluated row by row directly from table or index scan.", 120, 670);

            drawGlassTile(ctx, 60, 770, W - 120, 580, 20, "#10B981", false, true, 1.0);

            ctx.fillStyle = "#1E293B";
            ctx.fillRect(60, 770, W - 120, 48);
            ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 794, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 794, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 794, 8, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#10B981";
            ctx.font = "bold 20px monospace";
            ctx.fillText(p.syntax_b_title || "HAVING CLAUSE SYNTAX (GROUP FILTER)", 180, 802);

            const codeBLines = (p.syntax_b_code || "SELECT department, COUNT(*)\nFROM employees\nGROUP BY department\nHAVING COUNT(*) > 5;").split("\n");
            codeBLines.forEach((ln, idx) => {
                const lineY = 870 + idx * 56;
                ctx.fillStyle = "#475569";
                ctx.font = "bold 24px monospace";
                ctx.fillText((idx + 1).toString().padStart(2, "0"), 90, lineY);
                renderSqlSyntaxLine(ctx, ln, 160, lineY);
            });

            ctx.fillStyle = "rgba(16, 185, 129, 0.15)";
            ctx.fillRect(90, 1150, W - 180, 160);
            ctx.strokeStyle = "#10B981";
            ctx.strokeRect(90, 1150, W - 180, 160);
            ctx.fillStyle = "#10B981";
            ctx.font = "bold 22px 'Segoe UI', sans-serif";
            ctx.fillText("⚡ AGGREGATE FUNCTION: 'HAVING COUNT(*) > 5'", 120, 1200);
            ctx.fillStyle = "#F8FAFC";
            ctx.font = "20px 'Segoe UI', sans-serif";
            ctx.fillText("Evaluates only after rows are clustered into departments.", 120, 1245);
            ctx.fillText("Discarding entire department groups with fewer than 5 people.", 120, 1285);

            const arrowBounce = Math.sin(t * 6) * 10;
            ctx.fillStyle = "#F59E0B";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("👉 Notice: HAVING requires GROUP BY & Aggregate functions!", 90 + arrowBounce, 1420);

            ctx.restore();
        }

        // SCENE 5: COMPREHENSIVE COMPARISON MATRIX TABLE
        else if (currentStageIdx === 5) {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            drawGlassTile(ctx, 60, 220, W - 120, 95, 16, "#38BDF8", false, true, 1.0);

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 28px 'Segoe UI', sans-serif";
            ctx.fillText(`🔍 ${p.comparison_title || 'WHERE vs HAVING COMPARISON MATRIX'}`, 90, 265);
            ctx.fillStyle = "#CBD5E1";
            ctx.font = "20px 'Segoe UI', sans-serif";
            ctx.fillText("Memorize these 4 pillars for immediate high marks in your interview:", 90, 296);

            const headers = p.comparison_headers || ["FEATURE / ASPECT", "WHERE CLAUSE", "HAVING CLAUSE"];
            ctx.fillStyle = "rgba(56, 189, 248, 0.25)";
            ctx.fillRect(60, 340, W - 120, 60);
            ctx.strokeStyle = "#38BDF8";
            ctx.strokeRect(60, 340, W - 120, 60);

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 22px monospace";
            ctx.fillText(headers[0], 90, 378);
            ctx.fillText(headers[1], 420, 378);
            ctx.fillText(headers[2], 740, 378);

            const matrixRows = p.comparison_rows || [
                {feature: "Execution Stage", col_a: "Pre-Filter (Before GROUP BY)", col_b: "Post-Filter (After GROUP BY)"},
                {feature: "Aggregate Functions", col_a: "❌ CANNOT use (SUM, COUNT)", col_b: "✅ CAN use (e.g. COUNT > 5)"},
                {feature: "Target Scope", col_a: "Individual table rows", col_b: "Aggregated groups"},
                {feature: "Index Optimization", col_a: "Uses Table Indexes fast", col_b: "Cannot use B-Tree indexes"}
            ];

            const rowsToShow = Math.min(matrixRows.length, Math.floor(stageProg * (matrixRows.length + 1)) + 1);

            matrixRows.slice(0, rowsToShow).forEach((r, idx) => {
                const rowY = 415 + idx * 175;
                const isLatest = idx === rowsToShow - 1;

                drawGlassTile(ctx, 60, rowY, W - 120, 155, 14, isLatest ? "#10B981" : "#1E2D4A", isLatest, true, isLatest ? 1.0 : 0.85);

                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 22px 'Segoe UI', sans-serif";
                ctx.fillText(r.feature, 90, rowY + 45);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 20px monospace";
                ctx.fillText(`WHERE: ${r.col_a}`, 90, rowY + 90);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 20px monospace";
                ctx.fillText(`HAVING: ${r.col_b}`, 90, rowY + 130);
            });

            drawGlassTile(ctx, 60, 1180, W - 120, 320, 18, "#10B981", false, true, 1.0);

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 26px 'Segoe UI', sans-serif";
            ctx.fillText("💡 INTERVIEW CHECKLIST SUMMARY:", 90, 1235);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "24px 'Segoe UI', sans-serif";
            ctx.fillText("• Need to filter individual rows? ➔ Use WHERE.", 90, 1295);
            ctx.fillText("• Need to filter COUNT, SUM, AVG of groups? ➔ Use HAVING.", 90, 1355);
            ctx.fillText("• You can combine both in the same query for maximum speed!", 90, 1415);

            ctx.restore();
        }

        // SCENE 6: FATAL INTERVIEW TRAPS & GOLDEN TAKEAWAY
        else {
            ctx.save();
            ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

            drawGlassTile(ctx, 60, 220, W - 120, 480, 20, "#EF4444", true, true, 1.0);

            ctx.fillStyle = "#EF4444";
            ctx.font = "bold 28px 'Segoe UI', sans-serif";
            ctx.fillText(`❌ ${p.traps_title || 'FATAL INTERVIEW TRAPS TO AVOID'}`, 90, 275);

            const trapsList = p.traps && p.traps.length > 0 ? p.traps : [
                "❌ Trap: Writing WHERE COUNT(*) > 2 fails with a syntax error (aggregates illegal in WHERE)!",
                "✅ Rule: Always filter non-aggregated rows with WHERE first to cut group memory by 90%!"
            ];

            trapsList.forEach((trp, idx) => {
                const trapY = 330 + idx * 160;
                ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
                ctx.fillRect(90, trapY, W - 180, 130);
                ctx.strokeStyle = trp.startsWith("❌") ? "#EF4444" : "#10B981";
                ctx.strokeRect(90, trapY, W - 180, 130);

                ctx.fillStyle = trp.startsWith("❌") ? "#FCA5A5" : "#A7F3D0";
                ctx.font = "bold 22px 'Segoe UI', sans-serif";
                const tLines = wrapCanvasText(ctx, trp, W - 220);
                tLines.forEach((tl, ti) => {
                    ctx.fillText(tl, 115, trapY + 45 + ti * 36);
                });
            });

            drawGlassTile(ctx, 60, 740, W - 120, 440, 22, "#10B981", true, true, 1.0);

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 32px 'Segoe UI', sans-serif";
            ctx.fillText("🏆 THE UNIVERSAL GOLDEN RULE:", 90, 805);

            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            ctx.fillRect(90, 840, W - 180, 220);
            ctx.strokeStyle = "#10B981";
            ctx.strokeRect(90, 840, W - 180, 220);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 28px 'Segoe UI', sans-serif";
            const ruleText = p.golden_rule || "Golden Rule: Filter individual rows with WHERE; filter aggregated groups with HAVING.";
            const rLines = wrapCanvasText(ctx, `"${ruleText}"`, W - 220);
            rLines.forEach((rl, ri) => {
                ctx.fillText(rl, 120, 920 + ri * 46);
            });

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 22px 'Segoe UI', sans-serif";
            ctx.fillText("✅ Saying this one sentence guarantees full points in an interview!", 90, 1130);

            drawGlassTile(ctx, 60, 1220, W - 120, 260, 18, "#38BDF8", false, true, 1.0);

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 24px 'Segoe UI', sans-serif";
            ctx.fillText("🚀 HOW TO SAY THIS TO AN INTERVIEWER:", 90, 1270);
            ctx.fillStyle = "#F8FAFC";
            ctx.font = "22px 'Segoe UI', sans-serif";
            ctx.fillText("\"I use WHERE to prune individual rows before grouping,", 90, 1320);
            ctx.fillText("and HAVING to filter post-aggregation group metrics.\"", 90, 1365);
            ctx.fillText("Next: Senior Interviewer Pro-Tip & Outro!", 90, 1415);

            ctx.restore();
        }
    }

    /* ==========================================================================
       CANVAS RENDERING ENGINE (1080 x 1920 9:16 VERTICAL REEL FORMAT)
       ========================================================================== */
    /* ==========================================================================
       PROMPT-DRIVEN AWAITING STATE (NO STATIC TEMPLATES)
       ========================================================================== */
    function renderPromptStandbyScreen(ctx, W, H, t) {
        // 1. Dark Cyber/Fintech Neon Background
        ctx.fillStyle = "#070B16";
        ctx.fillRect(0, 0, W, H);

        // Tech grid lines
        ctx.strokeStyle = "rgba(56, 189, 248, 0.05)";
        ctx.lineWidth = 2;
        for (let x = 0; x < W; x += 80) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 0; y < H; y += 80) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        // Ambient cyber lighting
        const radGrad = ctx.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, 800);
        radGrad.addColorStop(0, "rgba(56, 189, 248, 0.20)");
        radGrad.addColorStop(0.5, "rgba(99, 102, 241, 0.10)");
        radGrad.addColorStop(1, "rgba(7, 11, 22, 0)");
        ctx.fillStyle = radGrad;
        ctx.fillRect(0, 0, W, H);

        // Top Header Bar
        ctx.fillStyle = "#0B1120";
        ctx.fillRect(0, 0, W, 180);
        ctx.strokeStyle = "#1E293B";
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(0, 180); ctx.lineTo(W, 180); ctx.stroke();

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 32px 'Segoe UI', sans-serif";
        ctx.fillText("👑 @Code_With_Mangesh", 60, 68);

        ctx.fillStyle = "#10B981";
        ctx.beginPath();
        ctx.roundRect(W - 270, 32, 210, 48, 12);
        ctx.fill();
        ctx.fillStyle = "#000000";
        ctx.font = "bold 18px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("⚡ 100% PROMPT AI", W - 165, 62);
        ctx.textAlign = "left";

        ctx.fillStyle = "#94A3B8";
        ctx.font = "bold 23px 'Segoe UI', sans-serif";
        ctx.fillText("Dynamic AI Video Generator • Shorts & Reels (<60s)", 60, 125);

        // Floating Center 3D Frosted Mirror Tile
        drawGlassTile(ctx, 70, 320, W - 140, 950, 28, "#38BDF8", true, true, 1.0);

        // Center Pulsating Cyber Radar Ring
        const pulse = 1.0 + Math.sin(t * 4) * 0.08;
        ctx.save();
        ctx.translate(W / 2, 480);
        ctx.scale(pulse, pulse);
        ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
        ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(0, 0, 75, 0, Math.PI * 2); ctx.stroke();
        ctx.strokeStyle = "rgba(16, 185, 129, 0.3)";
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(0, 0, 95, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
        ctx.beginPath(); ctx.arc(0, 0, 55, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#38BDF8";
        ctx.font = "52px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("✨", 0, 18);
        ctx.restore();

        // Title and Status
        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 34px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("PROMPT-DRIVEN AI VIDEO STUDIO", W / 2, 630);

        ctx.fillStyle = "rgba(16, 185, 129, 0.2)";
        ctx.beginPath();
        ctx.roundRect(W / 2 - 160, 660, 320, 42, 20);
        ctx.fill();
        ctx.strokeStyle = "#10B981";
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.fillStyle = "#10B981";
        ctx.font = "bold 20px 'Segoe UI', sans-serif";
        ctx.fillText("🟢 Awaiting Master Prompt", W / 2, 688);

        // Instructions
        ctx.fillStyle = "#FFFFFF";
        ctx.font = "bold 25px 'Segoe UI', sans-serif";
        ctx.fillText("व्हिडिओ कसा तयार करायचा?", W / 2, 760);

        ctx.font = "22px 'Segoe UI', sans-serif";
        ctx.fillStyle = "#CBD5E1";
        ctx.fillText("1️⃣ Column 1 मध्ये तुमचा कोणताही SQL प्रश्न लिहा", W / 2, 820);
        ctx.fillText("   किंवा व्हिडिओ कसा हवा आहे याचे स्पष्ट मार्गदर्शन लिहा.", W / 2, 855);

        ctx.fillText("2️⃣ [Generate AI Video & Voice from Master Prompt] वर क्लिक करा.", W / 2, 920);

        ctx.fillText("3️⃣ AI मॉडेल स्वतः प्रश्नानुसार व्हिडिओची रचना ठरवेल,", W / 2, 985);
        ctx.fillText("   सॅम्पल टेबल, कोड ॲनिमेशन आणि ऑडिओ तयार करेल!", W / 2, 1020);

        // Feature Highlights
        ctx.fillStyle = "#F59E0B";
        ctx.font = "bold 22px 'Segoe UI', sans-serif";
        ctx.fillText("🛡️ 100% Dynamic • Zero Static Templates • (<60s Reels)", W / 2, 1110);

        ctx.fillStyle = "#94A3B8";
        ctx.font = "italic 21px 'Segoe UI', sans-serif";
        ctx.fillText("Follow @Code_With_Mangesh for daily SQL mastery", W / 2, 1170);

        drawPhotonSparks(ctx, 110, 360, "#38BDF8", t);
        drawPhotonSparks(ctx, W - 110, 360, "#10B981", t);
        drawPhotonSparks(ctx, 110, 1220, "#F59E0B", t);
        drawPhotonSparks(ctx, W - 110, 1220, "#818CF8", t);

        ctx.textAlign = "left";
    }

    function renderSqlShortFrame(t) {
        const canvas = document.getElementById("sqlShortCanvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const W = 1080;
        const H = 1920;
        const p = sqlShortState.activePreset;

        // 1. Dark Cyber/Fintech Neon Background
        ctx.fillStyle = "#070B16";
        ctx.fillRect(0, 0, W, H);

        // Tech grid lines
        ctx.strokeStyle = "rgba(56, 189, 248, 0.04)";
        ctx.lineWidth = 2;
        for (let x = 0; x < W; x += 80) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 0; y < H; y += 80) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        // Render 3D Motion Video (if loaded)
        const bgVid = sqlShortState.backgroundVideoElement;
        if (bgVid && sqlShortState.backgroundVideoLoaded && bgVid.readyState >= 2) {
            ctx.save();
            ctx.globalAlpha = 0.35;
            const bgW = bgVid.videoWidth || 720;
            const bgH = bgVid.videoHeight || 1280;
            const cropX = bgW * 0.06;
            const cropY = bgH * 0.06;
            const cropW = bgW * 0.88;
            const cropH = bgH * 0.88;
            ctx.drawImage(bgVid, cropX, cropY, cropW, cropH, 0, 0, W, H);
            ctx.restore();
        }

        // Ambient cyber lighting
        const radGrad = ctx.createRadialGradient(W / 2, 450, 40, W / 2, 450, 750);
        radGrad.addColorStop(0, "rgba(56, 189, 248, 0.16)");
        radGrad.addColorStop(0.5, "rgba(14, 165, 233, 0.06)");
        radGrad.addColorStop(1, "rgba(7, 11, 22, 0)");
        ctx.fillStyle = radGrad;
        ctx.fillRect(0, 0, W, H);

        // Top Header Bar
        ctx.fillStyle = "#0B1120";
        ctx.fillRect(0, 0, W, 180);
        ctx.strokeStyle = "#1E293B";
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(0, 180); ctx.lineTo(W, 180); ctx.stroke();

        // Studio Branding Pill & Difficulty Tag
        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 32px 'Segoe UI', sans-serif";
        ctx.fillText("👑 @Code_With_Mangesh", 60, 68);

        ctx.fillStyle = "#F59E0B";
        ctx.beginPath();
        ctx.roundRect(W - 270, 32, 210, 48, 12);
        ctx.fill();
        ctx.fillStyle = "#000000";
        ctx.font = "bold 20px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("🔥 " + (p.difficulty || "FAANG SQL").toUpperCase(), W - 165, 63);
        ctx.textAlign = "left";

        ctx.fillStyle = "#94A3B8";
        ctx.font = "bold 24px 'Segoe UI', sans-serif";
        const subtitleBar = p.title ? p.title.slice(0, 46) : "Interactive AI SQL Interview Masterclass";
        ctx.fillText(`⚡ ${subtitleBar}`, 60, 125);

        // Visual Audio Waveform Equalizer Bars
        if (sqlShortState.isPlaying) {
            ctx.fillStyle = "#38BDF8";
            for (let i = 0; i < 9; i++) {
                const bh = 10 + Math.sin(t * 14 + i * 1.2) * 14;
                ctx.fillRect(W - 270 + i * 12, 110 + (24 - bh), 6, bh);
            }
        }

        // Floating AI Avatar Presenter Bubble
        if (sqlShortState.showAvatar) {
            ctx.save();
            const avatarX = W - 140;
            const avatarY = 260;
            const radius = 64;

            ctx.shadowColor = "#38BDF8";
            ctx.shadowBlur = 18;
            ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
            ctx.beginPath();
            ctx.arc(avatarX, avatarY, radius, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = "#38BDF8";
            ctx.lineWidth = 3.5;
            ctx.stroke();
            ctx.shadowBlur = 0;

            const vid = sqlShortState.avatarVideoElement;
            if (vid && sqlShortState.avatarVideoLoaded && vid.readyState >= 2) {
                ctx.save();
                ctx.beginPath();
                ctx.arc(avatarX, avatarY, radius - 2, 0, Math.PI * 2);
                ctx.clip();

                const vw = vid.videoWidth || 640;
                const vh = vid.videoHeight || 480;
                const sx = vw * 0.15;
                const sy = vh * 0.05;
                const sw = vw * 0.70;
                const sh = vh * 0.70;

                ctx.drawImage(vid, sx, sy, sw, sh, avatarX - radius, avatarY - radius, radius * 2, radius * 2);
                ctx.restore();
            } else {
                ctx.fillStyle = "#38BDF8";
                ctx.font = "38px 'Segoe UI', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("🧑‍💼", avatarX, avatarY + 12);
                ctx.textAlign = "left";
            }

            ctx.restore();
        }

        // =========================================================================
        // DYNAMIC AUDIO-SYNCHRONIZED STORYBOARD ENGINE (<60s Shorts & Reels Standard)
        // =========================================================================
        const maxDur = sqlShortState.maxDuration || 56.0;
        const stages = (p.stages && p.stages.length > 0) ? p.stages : (p.scenes && p.scenes.length > 0 ? p.scenes : []);
        const outroStart = (p.outro_start !== undefined) ? p.outro_start : Math.max(0, maxDur - 3.5);
        const isOutro = (t >= outroStart);

        let currentStageIdx = 0;
        let activeStage = null;

        if (isOutro) {
            currentStageIdx = stages.length > 0 ? stages.length : 7;
        } else if (stages.length > 0) {
            for (let i = 0; i < stages.length; i++) {
                if (t >= stages[i].start && t < stages[i].end) {
                    currentStageIdx = i + 1;
                    activeStage = stages[i];
                    break;
                }
            }
            if (!activeStage) {
                if (t < stages[0].start) {
                    activeStage = stages[0];
                    currentStageIdx = 1;
                } else {
                    activeStage = stages[stages.length - 1];
                    currentStageIdx = stages.length;
                }
            }
        } else {
            const estIdx = Math.min(6, Math.floor((t / Math.max(1, outroStart)) * 6) + 1);
            currentStageIdx = estIdx;
        }

        // Audio Chime on Stage Advance
        if (sqlShortState.lastBleepScene !== currentStageIdx && sqlShortState.isPlaying) {
            sqlShortState.lastBleepScene = currentStageIdx;
            playCyberBleep(880 + (currentStageIdx * 60), 0.08);
        }

        let stageProg = 0.5;
        let stageAlpha = 1.0;
        if (activeStage && activeStage.end > activeStage.start) {
            const sDur = activeStage.end - activeStage.start;
            const sElapsed = Math.max(0, t - activeStage.start);
            stageProg = Math.min(1.0, sElapsed / sDur);
            const alphaIn = Math.min(1.0, sElapsed / 0.35);
            const alphaOut = Math.min(1.0, (activeStage.end - t) / 0.35);
            stageAlpha = Math.max(0, Math.min(1.0, Math.min(alphaIn, alphaOut)));
        } else if (isOutro) {
            const oElapsed = Math.max(0, t - outroStart);
            stageAlpha = Math.min(1.0, oElapsed / 0.4);
            stageProg = Math.min(1.0, oElapsed / 3.5);
        }

        if (p.content_type === "theory") {
            renderTheoryShortStoryboard(ctx, W, H, p, t, currentStageIdx, activeStage, isOutro, outroStart, stageProg, stageAlpha);
        } else {
            const pipelineStages = getClientPipelineStages(p);
            const filterEvals = getClientFilterEvals(p);
            const actionType = isOutro ? "summary_outro" : (activeStage ? (activeStage.action_type || ("stage_" + currentStageIdx)) : ("stage_" + currentStageIdx));

            // =========================================================================
            // SCENE 7 (Branding & Outro): RENDERED STRICTLY ONLY WHEN isOutro IS TRUE!
            // =========================================================================
            if (isOutro) {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Senior Interviewer Pro-Tip Glass Card
                drawGlassTile(ctx, 60, 220, W - 120, 620, 22, "#8B5CF6", true, true, 1.0);

                ctx.fillStyle = "#8B5CF6";
                ctx.font = "bold 32px 'Segoe UI', sans-serif";
                ctx.fillText("💡 SENIOR FAANG INTERVIEWER PRO-TIP:", 90, 280);

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText("1️⃣ Why Interviewers Value This Approach:", 90, 340);
                ctx.fillStyle = "#C7D2FE";
                ctx.font = "22px 'Segoe UI', sans-serif";
                ctx.fillText("   " + (p.pro_tip || "Explaining query mechanics before writing code demonstrates senior-level clarity!"), 90, 380);

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText("2️⃣ Universal SQL Compatibility & Performance:", 90, 480);
                ctx.fillStyle = "#C7D2FE";
                ctx.font = "22px 'Segoe UI', sans-serif";
                ctx.fillText("   Optimizers use B-Tree indexes & partition pruning for low latency.", 90, 520);
                ctx.fillText("   Handles edge cases, nulls, and duplicate values gracefully.", 90, 560);

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText("3️⃣ FAANG Best Practice:", 90, 640);
                ctx.fillStyle = "#10B981";
                ctx.font = "bold 22px monospace";
                ctx.fillText("   Always state time complexity O(N log K) and memory footprint!", 90, 685);

                // 2. Outro Branding Card (@Code_With_Mangesh) on Glowing Amber Glass
                drawGlassTile(ctx, 60, 870, W - 120, 630, 24, "#F59E0B", true, true, 1.0);

                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 44px 'Segoe UI', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("👑 @Code_With_Mangesh", W / 2, 950);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 26px 'Segoe UI', sans-serif";
                ctx.fillText("FAANG & Top MNC SQL Interview Preparation Studio", W / 2, 1005);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "28px 'Segoe UI', sans-serif";
                ctx.fillText("⭐ SAVE THIS REEL FOR YOUR UPCOMING INTERVIEWS!", W / 2, 1100);
                ctx.fillText("🔔 Follow @Code_With_Mangesh for daily SQL questions", W / 2, 1160);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 26px 'Segoe UI', sans-serif";
                ctx.fillText("🚀 100% Free AI High-Tech Education for Every Student!", W / 2, 1260);

                ctx.fillStyle = "#94A3B8";
                ctx.font = "italic 22px 'Segoe UI', sans-serif";
                ctx.fillText("Empowering students from rural to global tech careers", W / 2, 1320);

                drawPhotonSparks(ctx, W / 2 - 280, 950, "#F59E0B", t);
                drawPhotonSparks(ctx, W / 2 + 280, 950, "#F59E0B", t);

                ctx.textAlign = "left";
                ctx.restore();
            }

            // =========================================================================
            // SCENE 1: PROBLEM STATEMENT & ARCHITECTURE PIPELINE
            // =========================================================================
            else if (actionType === "problem_intro" || currentStageIdx === 1) {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Floating 3D Frosted Glass Question Tile
                drawGlassTile(ctx, 60, 220, W - 120, 200, 20, "#38BDF8", true, true, 1.0);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 26px 'Segoe UI', sans-serif";
                ctx.fillText("📋 SQL INTERVIEW PROBLEM STATEMENT:", 95, 272);

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "bold 25px 'Segoe UI', sans-serif";
                const qLines = wrapCanvasText(ctx, p.question, W - 190);
                qLines.slice(0, 2).forEach((l, i) => {
                    ctx.fillText(l, 95, 318 + i * 36);
                });

                // Target Highlight Badge with Neon Pulse
                const pulse = 1.0 + Math.sin(t * 6) * 0.05;
                ctx.save();
                ctx.translate(W / 2, 385);
                ctx.scale(pulse, pulse);
                ctx.fillStyle = "rgba(245, 158, 11, 0.22)";
                ctx.beginPath();
                ctx.roundRect(-280, -22, 560, 44, 12);
                ctx.fill();
                ctx.strokeStyle = "#F59E0B";
                ctx.lineWidth = 2.5;
                ctx.stroke();
                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 20px 'Segoe UI', sans-serif";
                ctx.textAlign = "center";
                const targetText = p.target_badge || ("🎯 TARGET: " + (p.title || "OPTIMAL SQL QUERY").toUpperCase().slice(0, 36));
                ctx.fillText(targetText, 0, 7);
                ctx.restore();

                // 2. High-Tech Architecture Pipeline Diagram (Frosted Glass Nodes)
                drawArchitecturePipeline(ctx, 60, 440, W - 120, 105, pipelineStages, 0, t);

                // 3. Dynamic Frosted Glass Table View
                drawGlassTile(ctx, 60, 565, W - 120, 420, 18, "rgba(56, 189, 248, 0.4)", false, true, 0.95);

                const headers = p.col_headers && p.col_headers.length >= 3 ? p.col_headers : ["ID / KEY", "DATE / ATTR", "AMOUNT", "STATUS"];
                ctx.fillStyle = "rgba(56, 189, 248, 0.16)";
                ctx.fillRect(80, 585, W - 160, 52);
                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 21px monospace";
                ctx.fillText(headers[0], 105, 618);
                ctx.fillText(headers[1], 315, 618);
                ctx.fillText(headers[2] || "VAL", 560, 618);
                ctx.fillText(headers[3] || "STATUS", 810, 618);

                // Sample Rows in Glass Table
                const sampleRows = p.sample_rows && p.sample_rows.length > 0 ? p.sample_rows : [
                    {account: "REC-101", date: "2026-03-15", amt: "45000", balance: "Row #1"},
                    {account: "REC-102", date: "2026-03-12", amt: "95000", balance: "Row #2"},
                    {account: "REC-103", date: "2026-03-10", amt: "25000", balance: "Row #3"},
                    {account: "REC-104", date: "2026-03-01", amt: "12000", balance: "Row #4"}
                ];
                sampleRows.slice(0, 4).forEach((r, idx) => {
                    const rowY = 645 + idx * 76;
                    ctx.fillStyle = idx % 2 === 0 ? "rgba(15, 23, 42, 0.85)" : "rgba(30, 41, 59, 0.70)";
                    ctx.fillRect(80, rowY, W - 160, 66);
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
                    ctx.strokeRect(80, rowY, W - 160, 66);

                    ctx.fillStyle = "#FFFFFF";
                    ctx.font = "21px monospace";
                    ctx.fillText(r.account || "", 105, rowY + 42);
                    ctx.fillText(r.date || "", 315, rowY + 42);
                    ctx.fillText(r.amt || "", 560, rowY + 42);

                    ctx.fillStyle = "#38BDF8";
                    ctx.font = "bold 22px monospace";
                    ctx.fillText(r.balance || "", 810, rowY + 42);
                });

                // 4. Dynamic Laser Connector linking Table to Pipeline Stage 1
                drawDynamicConnector(ctx, 200, 645, 170, 545, "#38BDF8", t, "⚡ PIPELINE INPUT");

                // 5. Floating Frosted Glass IDE Tile (Empty Editor with Roadmap)
                drawGlassTile(ctx, 60, 1005, W - 120, 480, 20, "rgba(255, 255, 255, 0.15)", false, false, 0.9);

                ctx.fillStyle = "#1E293B";
                ctx.fillRect(60, 1005, W - 120, 50);
                ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 1030, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 1030, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 1030, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 20px monospace";
                ctx.fillText("query_roadmap.sql — Step-by-Step AI Teacher Logic", 180, 1037);

                ctx.fillStyle = "#64748B";
                ctx.font = "italic 23px monospace";
                ctx.fillText(`/* Step 1: Inspect ${p.table_name || 'table'} & identify key columns */`, 90, 1105);
                ctx.fillText(`/* Step 2: ${pipelineStages[1] ? pipelineStages[1].name + ' — ' + pipelineStages[1].sub : 'Analyze partitions and candidate rows'} */`, 90, 1155);
                ctx.fillText(`/* Step 3: ${pipelineStages[2] ? pipelineStages[2].name + ' — ' + pipelineStages[2].sub : 'Build core window/aggregate specification'} */`, 90, 1205);
                ctx.fillText(`/* Step 4: ${pipelineStages[3] ? pipelineStages[3].name + ' — ' + pipelineStages[3].sub : 'Filter target records & verify output'} */`, 90, 1255);

                // Learning Goal Glass Pill
                drawGlassTile(ctx, 90, 1370, W - 180, 80, 14, "#38BDF8", false, true, 1.0);
                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 22px 'Segoe UI', sans-serif";
                ctx.fillText("🧠 LEARNING GOAL: Grasp problem logic before typing SQL!", 120, 1420);

                ctx.restore();
            }

            // =========================================================================
            // SCENE 2: DATA INSPECTION & INTERVIEW TRAP
            // =========================================================================
            else if (actionType === "data_inspection" || currentStageIdx === 2) {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Data Inspection Glass Tile (Front Layer)
                drawGlassTile(ctx, 60, 220, W - 120, 410, 20, "#F59E0B", true, true, 1.0);

                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 26px 'Segoe UI', sans-serif";
                ctx.fillText("🔍 DATA INSPECTION — NOTICE DATA PATTERNS & EDGE CASES:", 90, 268);

                const sampleRows = p.sample_rows && p.sample_rows.length > 0 ? p.sample_rows : [
                    {account: "REC-101", date: "2026-03-15", amt: "45000", balance: "Target Row", is_target: true},
                    {account: "REC-102", date: "2026-03-12", amt: "95000", balance: "Active", is_target: false},
                    {account: "REC-103", date: "2026-03-10", amt: "25000", balance: "Target Row", is_target: true},
                    {account: "REC-104", date: "2026-03-01", amt: "12000", balance: "Active", is_target: false}
                ];

                sampleRows.slice(0, 4).forEach((r, idx) => {
                    const rowY = 295 + idx * 74;
                    const isTarget = r.is_target !== undefined ? r.is_target : (idx === 0 || idx === 2);
                    ctx.fillStyle = isTarget ? "rgba(16, 185, 129, 0.22)" : "rgba(15, 23, 42, 0.85)";
                    ctx.fillRect(85, rowY, W - 170, 64);
                    ctx.strokeStyle = isTarget ? "#10B981" : "rgba(255, 255, 255, 0.1)";
                    ctx.lineWidth = isTarget ? 2.5 : 1.5;
                    ctx.strokeRect(85, rowY, W - 170, 64);

                    ctx.fillStyle = "#FFFFFF";
                    ctx.font = "21px monospace";
                    ctx.fillText(r.account || "", 110, rowY + 40);
                    ctx.fillText(r.date || "", 320, rowY + 40);
                    ctx.fillText(r.amt || "", 560, rowY + 40);

                    if (isTarget) {
                        ctx.fillStyle = "#10B981";
                        ctx.font = "bold 21px monospace";
                        ctx.fillText("🎯 CANDIDATE (Rank 1)", 760, rowY + 40);
                    } else {
                        ctx.fillStyle = "#94A3B8";
                        ctx.font = "20px monospace";
                        ctx.fillText(r.balance || "PASS", 760, rowY + 40);
                    }
                });

                // 2. High-Tech Partition / Data Buckets Diagram (Middle Tile)
                drawGlassTile(ctx, 60, 650, W - 120, 320, 18, "#38BDF8", false, true, 1.0);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText(`🪟 ${pipelineStages[1] ? pipelineStages[1].name.toUpperCase() : 'DATA PARTITION'} & CANDIDATE BREAKDOWN:`, 90, 695);

                const sampleKeys = sampleRows.slice(0, 3);
                sampleKeys.forEach((r, i) => {
                    const by = 725 + i * 70;
                    ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                    ctx.fillRect(90, by, W - 180, 58);
                    ctx.strokeStyle = i === 0 ? "#10B981" : (i === 1 ? "#38BDF8" : "#F59E0B");
                    ctx.lineWidth = 1.5;
                    ctx.strokeRect(90, by, W - 180, 58);

                    ctx.fillStyle = i === 0 ? "#10B981" : (i === 1 ? "#38BDF8" : "#F59E0B");
                    ctx.font = "bold 20px monospace";
                    ctx.fillText(`👥 ${r.account || 'Group ' + (i + 1)}:`, 110, by + 37);

                    ctx.fillStyle = "#FFFFFF";
                    ctx.font = "20px monospace";
                    ctx.fillText(`${r.date || ''} • ${r.amt || ''} ➔ ${r.is_target ? '🎯 Selected' : 'Evaluated'}`, 340, by + 37);
                });

                // 3. The Fatal Interview Trap Card (Bottom Tile)
                drawGlassTile(ctx, 60, 990, W - 120, 500, 20, "#EF4444", true, true, 1.0);

                ctx.fillStyle = "#EF4444";
                ctx.font = "bold 28px 'Segoe UI', sans-serif";
                ctx.fillText("❌ THE FATAL INTERVIEW TRAP: COMMON PITFALLS TO AVOID!", 90, 1045);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "22px monospace";
                const trapCode = p.trap_code || "SELECT * FROM ... ORDER BY ... LIMIT 1 OFFSET 1; -- FAILS ON TIES / GROUPS!";
                ctx.fillText(trapCode, 90, 1100);

                ctx.fillStyle = "#CBD5E1";
                ctx.font = "24px 'Segoe UI', sans-serif";
                const trapsList = (p.traps && p.traps.length > 0) ? p.traps : [
                    "• Naive LIMIT/OFFSET or MAX() fails when duplicate values or ties exist!",
                    "• Basic GROUP BY drops row-level attributes, forcing messy self-joins.",
                    "• In FAANG interviews, failing to handle duplicate ties costs 50% points!"
                ];
                trapsList.slice(0, 3).forEach((tr, ti) => {
                    ctx.fillText(tr.startsWith("•") ? tr : ("• " + tr), 90, 1160 + ti * 55);
                });

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 25px 'Segoe UI', sans-serif";
                ctx.fillText("✅ Solution: Build dynamic multi-stage query logic with zero data loss!", 90, 1345);

                // Dynamic Connector Line between Middle Diagram and Trap Tile
                drawDynamicConnector(ctx, 300, 970, 300, 1030, "#EF4444", t, "⚠️ TRAP DETECTED");

                ctx.restore();
            }

            // =========================================================================
            // SCENE 3: 4-STEP LOGICAL STRATEGY FLOWCHART
            // =========================================================================
            else if (actionType === "logic_flowchart" || currentStageIdx === 3) {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Header Banner Glass Tile
                drawGlassTile(ctx, 60, 220, W - 120, 95, 16, "#818CF8", false, true, 1.0);

                ctx.fillStyle = "#818CF8";
                ctx.font = "bold 28px 'Segoe UI', sans-serif";
                ctx.fillText("💡 LOGICAL ALGORITHM FLOWCHART (BEFORE WRITING CODE)", 90, 265);
                ctx.fillStyle = "#CBD5E1";
                ctx.font = "20px 'Segoe UI', sans-serif";
                ctx.fillText("Step-by-step query construction to explain clearly to the interviewer:", 90, 296);

                // 2. Flowchart Steps with Depth Layering
                const steps = pipelineStages.map((st, i) => ({
                    num: `${i + 1}️⃣`,
                    icon: st.icon || "⚙️",
                    title: st.name || ("STEP " + (i + 1)),
                    query: st.sub || "Execution block",
                    sub: `Stage ${i + 1} processing pipeline`,
                    color: i === 0 ? "#38BDF8" : (i === 1 ? "#F59E0B" : (i === 2 ? "#EC4899" : "#10B981"))
                }));

                const activeStepIdx = Math.min(steps.length - 1, Math.floor(stageProg * steps.length));
                const stepSpacing = steps.length <= 3 ? 240 : 190;

                steps.forEach((st, idx) => {
                    const boxY = 335 + idx * stepSpacing;
                    const isActive = idx === activeStepIdx;

                    drawGlassTile(ctx, 60, boxY, W - 120, steps.length <= 3 ? 175 : 135, 18, st.color, isActive, isActive, isActive ? 1.0 : 0.45);

                    ctx.fillStyle = st.color;
                    ctx.font = "bold 26px 'Segoe UI', sans-serif";
                    ctx.fillText(`${st.num} ${st.icon} ${st.title}`, 95, boxY + 45);

                    ctx.fillStyle = isActive ? "#FFFFFF" : "#94A3B8";
                    ctx.font = "bold 24px monospace";
                    ctx.fillText(st.query, 95, boxY + 95);

                    if (st.sub && steps.length <= 3) {
                        ctx.fillStyle = isActive ? "#38BDF8" : "#64748B";
                        ctx.font = "20px 'Segoe UI', sans-serif";
                        ctx.fillText(st.sub, 95, boxY + 140);
                    }

                    if (isActive) {
                        drawPhotonSparks(ctx, W - 120, boxY + 50, st.color, t);
                    }

                    // Dynamic Laser Connector to next step
                    if (idx < steps.length - 1) {
                        const connY1 = boxY + (steps.length <= 3 ? 175 : 135);
                        const connY2 = connY1 + (steps.length <= 3 ? 65 : 55);
                        drawDynamicConnector(ctx, W / 2, connY1, W / 2, connY2, st.color, t, "");
                    }
                });

                // Strategy Takeaway Card at bottom
                drawGlassTile(ctx, 60, steps.length <= 3 ? 1160 : 1150, W - 120, 340, 20, "#10B981", false, true, 1.0);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 27px 'Segoe UI', sans-serif";
                ctx.fillText("🎯 STRATEGY VALIDATED BY SENIOR INTERVIEWERS:", 90, 1205);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "24px 'Segoe UI', sans-serif";
                ctx.fillText("• Explaining the execution pipeline demonstrates engineering depth.", 90, 1265);
                ctx.fillText("• Eliminates redundant subqueries, temporary tables, and cartesian joins.", 90, 1320);
                ctx.fillText("• Next step: Let's write the query step-by-step in our SQL editor!", 90, 1375);

                ctx.restore();
            }

            // =========================================================================
            // SCENE 4: KINETIC TYPEWRITER BUILD ON GLASS IDE
            // =========================================================================
            else if (actionType === "code_build" || currentStageIdx === 4) {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Architecture Pipeline (Stage 2 / 3 Active)
                drawArchitecturePipeline(ctx, 60, 220, W - 120, 105, pipelineStages, 1, t);

                // 2. Kinetic Frosted Glass SQL IDE Window
                drawGlassTile(ctx, 60, 350, W - 120, 500, 20, "#38BDF8", true, true, 1.0);

                ctx.fillStyle = "#1E293B";
                ctx.fillRect(60, 350, W - 120, 52);
                ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 376, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 376, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 376, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 20px monospace";
                ctx.fillText("query_builder.sql — Step 1: Core Specification", 180, 384);

                // Typewriter Animation
                const allLines = (p.solution_sql || "SELECT * FROM TRANSACTIONS;").split("\n");
                const linesToShow = Math.max(1, Math.min(allLines.length, Math.floor(stageProg * (allLines.length + 1)) + 1));

                for (let i = 0; i < linesToShow; i++) {
                    const lineY = 460 + i * 50;
                    ctx.fillStyle = "#475569";
                    ctx.font = "bold 25px monospace";
                    ctx.fillText((i + 1).toString().padStart(2, "0"), 95, lineY);
                    renderSqlSyntaxLine(ctx, allLines[i], 160, lineY);
                }

                // Laser Focus Box on active clause
                const highlightY = 450 + Math.min(linesToShow - 1, 2) * 50;
                ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
                ctx.beginPath();
                ctx.roundRect(150, highlightY - 26, W - 240, 48, 10);
                ctx.fill();
                ctx.strokeStyle = "#38BDF8";
                ctx.lineWidth = 2.5;
                ctx.stroke();

                drawPhotonSparks(ctx, W - 140, highlightY, "#38BDF8", t);

                // 3. Engine Simulation Intermediate Output Glass Card
                drawGlassTile(ctx, 60, 880, W - 120, 600, 20, "#10B981", false, true, 1.0);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 28px 'Segoe UI', sans-serif";
                ctx.fillText("⚡ DATABASE ENGINE: IN-MEMORY EVALUATION", 90, 935);

                filterEvals.slice(0, 5).forEach((row, i) => {
                    const ry = 970 + i * 74;
                    const isTop = row.status === "keep";
                    ctx.fillStyle = isTop ? "rgba(16, 185, 129, 0.22)" : "rgba(15, 23, 42, 0.85)";
                    ctx.fillRect(90, ry, W - 180, 64);
                    ctx.strokeStyle = isTop ? "#10B981" : "rgba(255, 255, 255, 0.08)";
                    ctx.lineWidth = isTop ? 2.5 : 1;
                    ctx.strokeRect(90, ry, W - 180, 64);

                    ctx.fillStyle = "#FFFFFF";
                    ctx.font = "22px monospace";
                    ctx.fillText(row.name, 120, ry + 42);
                    ctx.fillText(row.salary || row.cond, 350, ry + 42);

                    ctx.fillStyle = isTop ? "#10B981" : "#94A3B8";
                    ctx.font = "bold 22px monospace";
                    ctx.fillText(row.action || (isTop ? "TARGET" : "PASS"), 760, ry + 42);
                });

                // Dynamic Connector Line between IDE and Simulation
                drawDynamicConnector(ctx, W / 2, 850, W / 2, 880, "#38BDF8", t, "⚡ ENGINE EXECUTION");

                ctx.restore();
            }

            // =========================================================================
            // SCENE 5: APPLY FILTER & ROW-BY-ROW SIMULATION
            // =========================================================================
            else if (actionType === "simulation_execution" || currentStageIdx === 5) {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Frosted Glass IDE Tile showing Filter
                drawGlassTile(ctx, 60, 220, W - 120, 420, 20, "#F59E0B", true, true, 1.0);

                ctx.fillStyle = "#1E293B";
                ctx.fillRect(60, 220, W - 120, 50);
                ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 245, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 245, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 245, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 20px monospace";
                ctx.fillText("query_solution.sql — Step 2: Apply Target Filter", 180, 253);

                const filterLines = (p.solution_sql || "SELECT * FROM TRANSACTIONS;").split("\n");
                filterLines.slice(0, 7).forEach((ln, idx) => {
                    const lineY = 310 + idx * 46;
                    ctx.fillStyle = "#475569";
                    ctx.font = "bold 24px monospace";
                    ctx.fillText((idx + 1).toString().padStart(2, "0"), 95, lineY);

                    const isFilterLine = ln.toUpperCase().includes("QUALIFY") || ln.toUpperCase().includes("WHERE") || ln.toUpperCase().includes("HAVING");
                    if (isFilterLine) {
                        ctx.fillStyle = "rgba(245, 158, 11, 0.22)";
                        ctx.fillRect(150, lineY - 26, W - 260, 36);
                    }
                    renderSqlSyntaxLine(ctx, ln, 160, lineY);
                });

                // Dynamic Bouncing Laser Arrow on QUALIFY / Filter
                const arrowBounce = Math.sin(t * 6) * 12;
                const arrowX = 660 + arrowBounce;
                const arrowY = 430;
                ctx.fillStyle = "#F59E0B";
                ctx.beginPath();
                ctx.moveTo(arrowX, arrowY);
                ctx.lineTo(arrowX + 35, arrowY - 16);
                ctx.lineTo(arrowX + 35, arrowY - 8);
                ctx.lineTo(arrowX + 90, arrowY - 8);
                ctx.lineTo(arrowX + 90, arrowY + 8);
                ctx.lineTo(arrowX + 35, arrowY + 8);
                ctx.lineTo(arrowX + 35, arrowY + 16);
                ctx.closePath();
                ctx.fill();

                ctx.fillStyle = "#F59E0B";
                ctx.fillRect(arrowX + 100, arrowY - 18, 220, 36);
                ctx.fillStyle = "#000000";
                ctx.font = "bold 17px 'Segoe UI', sans-serif";
                ctx.fillText("⚡ FILTER EVALUATION", arrowX + 110, arrowY + 6);

                // 2. Row-by-Row Evaluation Simulation Table on Frosted Glass
                drawGlassTile(ctx, 60, 670, W - 120, 530, 20, "#38BDF8", false, true, 1.0);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 25px 'Segoe UI', sans-serif";
                ctx.fillText("🔍 DATABASE ENGINE: ROW-BY-ROW FILTER EVALUATION:", 90, 715);

                const rowsToShow = Math.min(filterEvals.length, Math.floor(stageProg * (filterEvals.length + 1)) + 1);

                filterEvals.slice(0, rowsToShow).forEach((ev, i) => {
                    const rY = 745 + i * 76;
                    const isExclude = ev.status === "exclude";

                    ctx.fillStyle = isExclude ? "rgba(239, 68, 68, 0.22)" : "rgba(16, 185, 129, 0.18)";
                    ctx.fillRect(80, rY, W - 160, 66);
                    ctx.strokeStyle = isExclude ? "#EF4444" : "#10B981";
                    ctx.strokeRect(80, rY, W - 160, 66);

                    ctx.fillStyle = isExclude ? "#FCA5A5" : "#FFFFFF";
                    ctx.font = "22px monospace";
                    ctx.fillText(ev.name, 105, rY + 42);
                    ctx.fillText(ev.salary || "", 350, rY + 42);
                    ctx.fillText(ev.cond, 560, rY + 42);

                    ctx.fillStyle = isExclude ? "#EF4444" : "#10B981";
                    ctx.font = "bold 22px monospace";
                    ctx.fillText(isExclude ? "❌ EXCLUDE" : "✅ KEEP", 830, rY + 42);
                });

                // 3. Filtered Candidates Outcome Glass Card
                drawGlassTile(ctx, 60, 1225, W - 120, 275, 18, "#10B981", false, true, 1.0);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 26px 'Segoe UI', sans-serif";
                ctx.fillText("🎯 FILTERED CANDIDATE DATA POOL:", 90, 1275);

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "bold 23px monospace";
                const keptRows = filterEvals.filter(e => e.status === "keep").map(e => e.name).slice(0, 3).join(", ");
                ctx.fillText(`KEPT RECORDS: { ${keptRows || 'Evaluated Top Candidates'} }`, 90, 1330);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "22px 'Segoe UI', sans-serif";
                ctx.fillText("All invalid and duplicate entries have been cleanly eliminated!", 90, 1385);
                ctx.fillText("Next: View verified final query execution output!", 90, 1435);

                // Dynamic Connector Line linking IDE filter line to Kept Rows
                drawDynamicConnector(ctx, 500, 640, 500, 670, "#10B981", t, "✅ FILTER = TRUE");

                ctx.restore();
            }

            // =========================================================================
            // SCENE 6: FINAL PRODUCTION QUERY & VERIFIED OUTPUT
            // =========================================================================
            else {
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1.0, stageAlpha));

                // 1. Complete Production SQL IDE Window on Frosted Glass
                drawGlassTile(ctx, 60, 220, W - 120, 500, 20, "#10B981", true, true, 1.0);

                ctx.fillStyle = "#1E293B";
                ctx.fillRect(60, 220, W - 120, 50);
                ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(95, 245, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(120, 245, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 245, 8, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = "#10B981";
                ctx.font = "bold 20px monospace";
                ctx.fillText("production_solution.sql — Final Verified Execution", 180, 253);

                const finalLines = (p.solution_sql || "SELECT * FROM TRANSACTIONS;").split("\n");
                finalLines.forEach((ln, idx) => {
                    const lineY = 310 + idx * 48;
                    ctx.fillStyle = "#475569";
                    ctx.font = "bold 24px monospace";
                    ctx.fillText((idx + 1).toString().padStart(2, "0"), 95, lineY);

                    if (idx === 0) {
                        ctx.fillStyle = "rgba(16, 185, 129, 0.22)";
                        ctx.fillRect(150, lineY - 30, W - 260, 42);
                        ctx.strokeStyle = "#10B981";
                        ctx.strokeRect(150, lineY - 30, W - 260, 42);
                    }
                    renderSqlSyntaxLine(ctx, ln, 160, lineY);
                });

                // 2. Outer Execution Calculation Summary Tile
                drawGlassTile(ctx, 60, 745, W - 120, 280, 18, "#38BDF8", false, true, 1.0);

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 25px 'Segoe UI', sans-serif";
                ctx.fillText("🧮 EXECUTION CALCULATION SUMMARY:", 90, 790);

                ctx.fillStyle = "#CBD5E1";
                ctx.font = "24px monospace";
                ctx.fillText(`TABLE EVALUATED: ${p.table_name || 'TRANSACTIONS'} (${filterEvals.length} Records)`, 90, 845);
                ctx.fillStyle = "#10B981";
                ctx.font = "bold 25px monospace";
                ctx.fillText("EXECUTION STATUS: 100% Verified Production Output", 90, 905);
                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 22px 'Segoe UI', sans-serif";
                ctx.fillText("⚡ Engine Complexity: O(N log K) Linear Sorting • Zero Cartesian Join", 90, 965);

                // 3. Big Glowing Neon 3D Glass Output Card
                drawGlassTile(ctx, 60, 1050, W - 120, 450, 22, "#10B981", true, true, 1.0);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 32px 'Segoe UI', sans-serif";
                ctx.fillText("🏆 VERIFIED FINAL QUERY OUTPUT:", 90, 1110);

                ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
                ctx.fillRect(90, 1145, W - 180, 230);
                ctx.strokeStyle = "#10B981";
                ctx.lineWidth = 2;
                ctx.strokeRect(90, 1145, W - 180, 230);

                if (p.output_rows && Array.isArray(p.output_rows) && p.output_rows.length > 0) {
                    ctx.fillStyle = "#38BDF8";
                    ctx.font = "bold 22px monospace";
                    const colHeaders = (p.col_headers || ["ID", "COL2", "COL3", "VALUE"]).slice(0, 4).join("   ");
                    ctx.fillText(colHeaders, 120, 1195);
                    ctx.fillStyle = "#475569";
                    ctx.fillText("---------------------------------------------", 120, 1225);

                    ctx.fillStyle = "#10B981";
                    ctx.font = "bold 24px monospace";
                    p.output_rows.slice(0, 3).forEach((row, ri) => {
                        const rowStr = Array.isArray(row) ? row.join("   ") : Object.values(row).join("   ");
                        ctx.fillText(rowStr, 120, 1265 + ri * 40);
                    });
                } else if (p.output_value) {
                    ctx.fillStyle = "#38BDF8";
                    ctx.font = "bold 26px monospace";
                    ctx.fillText("RESULT_VALUE", 130, 1205);
                    ctx.fillStyle = "#475569";
                    ctx.fillText("-------------------------------------", 130, 1240);

                    ctx.fillStyle = "#10B981";
                    ctx.font = "bold 72px monospace";
                    ctx.fillText(p.output_value.toString(), 130, 1320);
                } else {
                    ctx.fillStyle = "#38BDF8";
                    ctx.font = "bold 22px monospace";
                    ctx.fillText("CUSTOMER_ID   TOTAL_AMOUNT   STATUS", 120, 1195);
                    ctx.fillStyle = "#475569";
                    ctx.fillText("---------------------------------------------", 120, 1225);

                    ctx.fillStyle = "#10B981";
                    ctx.font = "bold 24px monospace";
                    ctx.fillText("C103          95000          🎯 TOP 10%", 120, 1265);
                    ctx.fillText("C101          45000          🎯 TOP 10%", 120, 1305);
                }

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText("✅ 100% Accurate & Duplicate-Safe • Production-Ready FAANG Query!", 90, 1435);

                drawPhotonSparks(ctx, W - 140, 1260, "#10B981", t);

                ctx.restore();
            }
        } // Close else block for sql_query storyboard

        // =========================================================================
        // BOTTOM SUBTITLE / TEXT OVERLAY BANNER (Multilingual & Synchronized)
        // =========================================================================
        ctx.fillStyle = "rgba(15, 23, 42, 0.96)";
        ctx.fillRect(40, H - 360, W - 80, 220);
        ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
        ctx.lineWidth = 2.5;
        ctx.strokeRect(40, H - 360, W - 80, 220);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 24px 'Segoe UI', sans-serif";
        const langBadge = (sqlShortState.audioLang === "mr" ? "मराठी" : (sqlShortState.audioLang === "hi" ? "हिन्दी" : "ENGLISH")) + " AI TEACHER";
        ctx.fillText(`🎙️ ${langBadge} • 👑 @Code_With_Mangesh`, 70, H - 315);

        // Dynamic Active Scene Speech Subtitles (Frame-Perfect Sync to Audio Narration)
        let subtitleText = "";
        if (isOutro) {
            subtitleText = sqlShortState.audioLang === "mr" 
                ? "👑 @Code_With_Mangesh: रोजच्या नवीन SQL ट्रिक्स आणि FAANG इंटरव्ह्यू तयारीसाठी आताच फॉलो करा!"
                : (sqlShortState.audioLang === "hi"
                    ? "👑 @Code_With_Mangesh: डेली SQL इंटरव्यू ट्रिक्स के लिए अभी फॉलो करें!"
                    : "👑 @Code_With_Mangesh: Follow for daily FAANG SQL interview preparation!");
        } else if (activeStage) {
            subtitleText = activeStage.speech || activeStage['speech_' + sqlShortState.audioLang] || activeStage.speech_mr || activeStage.speech_hi || activeStage.speech_en || "";
        } else if (p.scenes && p.scenes.length > 0) {
            const sc = p.scenes.find(s => t >= s.start && t < s.end) || p.scenes[p.scenes.length - 1];
            subtitleText = sc['speech_' + sqlShortState.audioLang] || sc['speech_en'] || "";
        } else {
            subtitleText = p['explanation_' + sqlShortState.textStyle] || p['explanation_' + sqlShortState.audioLang] || p.explanation_en;
        }

        ctx.fillStyle = "#FFFFFF";
        ctx.font = "bold 28px 'Segoe UI', sans-serif";
        const subLines = wrapCanvasText(ctx, subtitleText, W - 140);
        subLines.slice(0, 3).forEach((line, idx) => {
            ctx.fillText(line, 70, H - 262 + idx * 42);
        });

        // =========================================================================
        // ZERO-WATERMARK SHIELD (Bottom Footer)
        // =========================================================================
        ctx.fillStyle = "#070B16";
        ctx.fillRect(0, H - 120, W, 120);

        // Tri-Color Glowing Ribbon
        const mGrad = ctx.createLinearGradient(0, H - 120, W, H - 120);
        mGrad.addColorStop(0, "#0284C7");
        mGrad.addColorStop(0.5, "#38BDF8");
        mGrad.addColorStop(1, "#10B981");
        ctx.fillStyle = mGrad;
        ctx.fillRect(0, H - 120, W, 5);

        ctx.fillStyle = "#F8FAFC";
        ctx.font = "bold 26px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("👑 @Code_With_Mangesh • TOP MNC & FAANG SQL STUDIO", W / 2, H - 70);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 20px 'Segoe UI', sans-serif";
        ctx.fillText("✨ 100% Clean Zero-Watermark Studio • Step-by-Step Code Mastery", W / 2, H - 32);
        ctx.textAlign = "left";
    }

    // Syntax Highlight Helper
    function renderSqlSyntaxLine(ctx, text, startX, lineY) {
        const tokens = text.split(/(\s+|[(),;])/);
        let currX = startX;

        const KEYWORDS = ["SELECT", "FROM", "WHERE", "ORDER", "BY", "DESC", "ASC", "OVER", "PARTITION", "ROWS", "BETWEEN", "UNBOUNDED", "PRECEDING", "AND", "CURRENT", "ROW", "WITH", "AS", "GROUP", "HAVING", "LIMIT", "OFFSET", "JOIN", "LEFT", "ON", "DATE", "ROUND", "COUNT", "MIN", "MAX"];
        const FUNCTIONS = ["DENSE_RANK", "RANK", "ROW_NUMBER", "SUM", "LAG", "LEAD", "AVG"];

        ctx.font = "bold 26px monospace";

        tokens.forEach(tok => {
            const clean = tok.toUpperCase().trim();
            if (KEYWORDS.includes(clean)) {
                ctx.fillStyle = "#38BDF8";
            } else if (FUNCTIONS.includes(clean)) {
                ctx.fillStyle = "#F472B6";
            } else if (/^\d+(\.\d+)?$/.test(clean)) {
                ctx.fillStyle = "#F59E0B";
            } else if (clean.startsWith("'") || clean.startsWith('"')) {
                ctx.fillStyle = "#10B981";
            } else {
                ctx.fillStyle = "#F8FAFC";
            }
            ctx.fillText(tok, currX, lineY);
            currX += ctx.measureText(tok).width;
        });
    }

    function wrapCanvasText(ctx, text, maxWidth) {
        if (!text) return [];
        const words = text.split(" ");
        const lines = [];
        let currLine = "";

        words.forEach(w => {
            const testLine = currLine ? (currLine + " " + w) : w;
            if (ctx.measureText(testLine).width > maxWidth && currLine) {
                lines.push(currLine);
                currLine = w;
            } else {
                currLine = testLine;
            }
        });
        if (currLine) lines.push(currLine);
        return lines;
    }

    /* ==========================================================================
       SMARTPHONE TRANSPORT & PLAYBACK
       ========================================================================== */
    function toggleSqlShortPlay() {
        if (sqlShortState.isPlaying) {
            pauseSqlShortPlay();
        } else {
            playSqlShort();
        }
    }

    function playSqlShort() {
        if (sqlShortState.currentTime >= sqlShortState.maxDuration) {
            sqlShortState.currentTime = 0;
        }
        sqlShortState.isPlaying = true;
        document.getElementById("btnPlayPause").innerText = "⏸ Pause";

        // Play synchronized natural voice audio
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl && audioEl.src && !audioEl.error) {
            attachAudioSyncListeners(audioEl);
            audioEl.currentTime = sqlShortState.currentTime;
            audioEl.playbackRate = sqlShortState.playbackSpeed;
            audioEl.play().catch(e => console.warn("Audio play prevented:", e));
        }

        let lastTime = performance.now();

        function step(now) {
            if (!sqlShortState.isPlaying) return;
            const deltaSec = (now - lastTime) / 1000.0;
            lastTime = now;

            // Frame-perfect hardware audio clock locking (Zero Drift)
            const audioEl = document.getElementById("sqlVoiceAudio");
            if (audioEl && !audioEl.paused && !audioEl.ended && audioEl.currentTime > 0) {
                sqlShortState.currentTime = audioEl.currentTime;
            } else {
                sqlShortState.currentTime += deltaSec * sqlShortState.playbackSpeed;
            }

            if (sqlShortState.currentTime >= sqlShortState.maxDuration) {
                sqlShortState.currentTime = sqlShortState.maxDuration;
                pauseSqlShortPlay();
            }

            renderSqlShortFrame(sqlShortState.currentTime);
            updatePlayerScrubberUI(sqlShortState.currentTime);

            if (sqlShortState.isPlaying) {
                sqlShortState.animationFrameId = requestAnimationFrame(step);
            }
        }
        sqlShortState.animationFrameId = requestAnimationFrame(step);
    }

    function pauseSqlShortPlay() {
        sqlShortState.isPlaying = false;
        if (sqlShortState.animationFrameId) {
            cancelAnimationFrame(sqlShortState.animationFrameId);
            sqlShortState.animationFrameId = null;
        }
        document.getElementById("btnPlayPause").innerText = "▶ Play";
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl) audioEl.pause();
    }

    function restartSqlShortPlay() {
        pauseSqlShortPlay();
        sqlShortState.currentTime = 0.0;
        updatePlayerScrubberUI(0);
        renderSqlShortFrame(0);
        playSqlShort();
    }

    function seekSqlShortPlayer(val) {
        sqlShortState.currentTime = parseFloat(val);
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl) audioEl.currentTime = sqlShortState.currentTime;
        updatePlayerScrubberUI(sqlShortState.currentTime);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function setSqlShortSpeed(val) {
        sqlShortState.playbackSpeed = parseFloat(val);
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl) audioEl.playbackRate = sqlShortState.playbackSpeed;
    }

    function updatePlayerScrubberUI(t) {
        const sc = document.getElementById("sqlShortScrubber");
        if (sc) sc.value = t;
        const tm = document.getElementById("playerTimer");
        if (tm) {
            const mins = Math.floor(t / 60);
            const secs = Math.floor(t % 60).toString().padStart(2, "0");
            const maxT = sqlShortState.maxDuration || 58.0;
            const maxMins = Math.floor(maxT / 60);
            const maxSecs = Math.floor(maxT % 60).toString().padStart(2, "0");
            tm.innerText = `${mins}:${secs} / ${maxMins}:${maxSecs}`;
        }
    }

    function downloadVoiceoverMp3() {
        const audioEl = document.getElementById("sqlVoiceAudio");
        const url = (audioEl && audioEl.src) ? audioEl.src : sqlShortState.audioUrl;
        if (!url) {
            alert("Voiceover audio is still loading, please wait 2 seconds.");
            return;
        }
        const a = document.createElement("a");
        a.href = url;
        a.download = `Voiceover_${sqlShortState.activePreset.id}_${sqlShortState.audioLang}.mp3`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    /* ==========================================================================
       MEDIARECORDER AUDIO-MULTIPLEXED EXPORT & DOWNLOAD
       ========================================================================== */
    async function exportSqlShortVideo(durationSec = null) {
        const canvas = document.getElementById("sqlShortCanvas");
        const audioEl = document.getElementById("sqlVoiceAudio");
        const btn = document.getElementById("btnDownloadShortVideo");
        const btnLabel = document.getElementById("exportBtnLabel");
        const pContainer = document.getElementById("exportProgressBarContainer");
        const pFill = document.getElementById("exportProgressFill");
        const pDesc = document.getElementById("exportStageDesc");
        const pPctText = document.getElementById("exportPercentNum");
        const pEstTime = document.getElementById("exportEstTime");
        const pFrameStats = document.getElementById("exportFrameStats");
        const badgeEl = document.getElementById("exportLiveBadge");
        const celebrationBox = document.getElementById("videoReadyCelebration");

        if (!canvas || !canvas.captureStream) {
            alert("Your browser does not support Canvas.captureStream. Please use Chrome or Edge.");
            return;
        }

        pauseSqlShortPlay();

        // Enforce strictly <60s for YouTube Shorts / Reels standard
        let totalDuration = durationSec;
        if (!totalDuration || totalDuration > 60) {
            if (audioEl && audioEl.duration && !isNaN(audioEl.duration) && isFinite(audioEl.duration) && audioEl.duration > 5) {
                totalDuration = Math.min(58.5, audioEl.duration);
            } else {
                totalDuration = Math.min(58.5, sqlShortState.maxDuration || 56.0);
            }
        }
        totalDuration = Math.min(59.5, totalDuration);

        if (celebrationBox) celebrationBox.style.display = "none";
        if (pContainer) pContainer.style.display = "block";
        if (badgeEl) {
            badgeEl.innerText = "रेंडरिंग चालू (Rendering...)";
            badgeEl.style.color = "#38BDF8";
            badgeEl.style.background = "rgba(56, 189, 248, 0.15)";
        }
        if (btn) btn.disabled = true;
        if (btnLabel) btnLabel.innerText = `⏳ Shorts / Reels व्हिडिओ रेंडर होत आहे (${Math.round(totalDuration)}s <60s)...`;

        // Audio Multiplexing Setup
        let audioTracks = [];
        let audioCtx = null;
        if (audioEl && audioEl.src && !audioEl.error) {
            try {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') {
                    await audioCtx.resume();
                }
                const audioDest = audioCtx.createMediaStreamDestination();
                const audioSource = audioCtx.createMediaElementSource(audioEl);
                audioSource.connect(audioDest);
                audioSource.connect(audioCtx.destination);
                audioTracks = audioDest.stream.getAudioTracks();
            } catch(e) {
                console.warn("AudioContext stream capture notice:", e);
            }
        }

        const videoTracks = canvas.captureStream(30).getVideoTracks();
        const combinedStream = new MediaStream([...videoTracks, ...audioTracks]);

        let mimeType = "video/webm;codecs=vp9,opus";
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = "video/webm;codecs=vp8,opus";
        }
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = "video/webm";
        }

        const chunks = [];
        const recorder = new MediaRecorder(combinedStream, {
            mimeType: mimeType,
            videoBitsPerSecond: 8000000
        });

        recorder.ondataavailable = e => {
            if (e.data && e.data.size > 0) chunks.push(e.data);
        };

        const totalFrames = Math.round(totalDuration * 30);
        let frameCount = 0;
        const dt = 1.0 / 30.0;
        const startTime = performance.now();

        recorder.onstop = () => {
            if (audioEl) audioEl.pause();
            if (pFill) pFill.style.width = "100%";
            if (pPctText) pPctText.innerText = "100%";
            if (pDesc) pDesc.innerText = "✅ रेंडरिंग पूर्ण झाले! व्हिडिओ व ऑडिओ डाऊनलोड होत आहे...";
            if (badgeEl) {
                badgeEl.innerText = "पूर्ण झाले (Completed)";
                badgeEl.style.color = "#10B981";
                badgeEl.style.background = "rgba(16, 185, 129, 0.2)";
            }



            const blob = new Blob(chunks, { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const filename = `Clean_9x16_${sqlShortState.activePreset.id}_${sqlShortState.audioLang}_${Math.round(totalDuration)}s.webm`;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            setTimeout(() => {
                if (celebrationBox) {
                    celebrationBox.style.display = "block";
                    celebrationBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    const btnAgain = document.getElementById("btnDownloadAgain");
                    if (btnAgain) {
                        btnAgain.href = url;
                        btnAgain.download = filename;
                    }
                }
                if (btn) btn.disabled = false;
                if (btnLabel) btnLabel.innerText = "DOWNLOAD 9:16 SHORT / REEL (<60s) (WITH SYNCHRONIZED VOICE)";
            }, 300);
        };

        recorder.start();
        if (audioEl && audioEl.src) {
            audioEl.currentTime = 0;
            audioEl.play().catch(e => console.warn("Audio play during export:", e));
        }



        function recordStep() {
            if (frameCount < totalFrames) {
                const stepBatch = totalDuration <= 15 ? 1 : 2;
                for (let b = 0; b < stepBatch && frameCount < totalFrames; b++) {
                    sqlShortState.currentTime = (frameCount * dt);
                    const t = sqlShortState.currentTime;
                    const p = sqlShortState.activePreset;
                    const stages = (p.stages && p.stages.length > 0) ? p.stages : (p.scenes && p.scenes.length > 0 ? p.scenes : []);
                    const outroStart = (p.outro_start !== undefined) ? p.outro_start : Math.max(0, totalDuration - 3.5);
                    const isOutro = (t >= outroStart);

                    let currentStage = 1;
                    let stageText = "पायरी १/७: 📋 प्रश्न ओळख";

                    if (isOutro) {
                        currentStage = 7;
                        stageText = "पायरी ७/७: 💡 सीनियर इंटरव्ह्यूअर प्रो-टिप व @Code_With_Mangesh";
                    } else if (stages.length > 0) {
                        const actIdx = stages.findIndex(s => t >= s.start && t < s.end);
                        if (actIdx !== -1) {
                            currentStage = Math.min(6, actIdx + 1);
                            const st = stages[actIdx];
                            stageText = `पायरी ${currentStage}/${Math.max(6, stages.length)}: ${st.title || st.action_type || ''}`;
                        } else if (t < stages[0].start) {
                            currentStage = 1;
                            stageText = `पायरी 1/${stages.length}: ${stages[0].title || ''}`;
                        } else {
                            currentStage = Math.min(6, stages.length);
                            stageText = `पायरी ${currentStage}/${stages.length}: ${stages[stages.length - 1].title || ''}`;
                        }
                    } else {
                        const estStage = Math.min(6, Math.floor((t / Math.max(1, outroStart)) * 6) + 1);
                        currentStage = estStage;
                        stageText = `पायरी ${currentStage}/6: विश्लेषण चालू`;
                    }

                    
                    if (pDesc) pDesc.innerText = stageText;

                    if (sqlShortState.avatarVideoElement && sqlShortState.avatarVideoElement.duration > 0) {
                        sqlShortState.avatarVideoElement.currentTime = t % sqlShortState.avatarVideoElement.duration;
                    }

                    renderSqlShortFrame(t);
                    updatePlayerScrubberUI(t);
                    frameCount++;
                }

                if (frameCount % 15 === 0 || frameCount >= totalFrames) {
                    const pct = Math.min(100, Math.floor((frameCount / totalFrames) * 100));
                    if (pFill) pFill.style.width = pct + "%";
                    if (pPctText) pPctText.innerText = pct + "%";

                    const elapsedSec = (performance.now() - startTime) / 1000.0;
                    if (elapsedSec > 0.2) {
                        const framesPerSec = frameCount / elapsedSec;
                        const remainingSec = Math.max(1, Math.ceil((totalFrames - frameCount) / framesPerSec));
                        if (pEstTime) pEstTime.innerText = `⏱️ अंदाजे वेळ: ${remainingSec} सेकंद बाकी (${remainingSec}s left)`;
                    }
                    if (pFrameStats) pFrameStats.innerText = `🎞️ फ्रेम: ${frameCount} / ${totalFrames}`;
                }

                requestAnimationFrame(recordStep);
            } else {
                recorder.stop();
            }
        }
        requestAnimationFrame(recordStep);
    }

    function downloadCurrentFrameAsPng() {
        const canvas = document.getElementById("sqlShortCanvas");
        if (!canvas) return;
        const dataUrl = canvas.toDataURL("image/png");
        const a = document.createElement("a");
        a.href = dataUrl;
        a.download = `SQL_Interview_Frame_${sqlShortState.activePreset.id}_${Math.floor(sqlShortState.currentTime)}s.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // Expose Functions to Global Window
    window.setSqlAudioLang = setSqlAudioLang;
    window.setSqlTextStyle = setSqlTextStyle;
    window.toggleSqlAvatar = toggleSqlAvatar;
    window.setSqlAvatarPresenter = setSqlAvatarPresenter;
    window.generateSqlShortBlueprint = generateSqlShortBlueprint;
    window.renderAiAvatarVideo = renderAiAvatarVideo;
    window.renderCinematicBackgroundVideo = renderCinematicBackgroundVideo;
    window.seekSqlShortPlayer = seekSqlShortPlayer;
    window.toggleSqlShortPlay = toggleSqlShortPlay;
    window.restartSqlShortPlay = restartSqlShortPlay;
    window.setSqlShortSpeed = setSqlShortSpeed;
    window.exportSqlShortVideo = exportSqlShortVideo;
    window.downloadCurrentFrameAsPng = downloadCurrentFrameAsPng;
    window.runInMemorySqlSandbox = runInMemorySqlSandbox;
    window.handleSqlPresetChange = handleSqlPresetChange;
    window.downloadVoiceoverMp3 = downloadVoiceoverMp3;
    window.loadPresetVoiceAudio = loadPresetVoiceAudio;
    window.loadDemoMasterPrompt = loadDemoMasterPrompt;
    window.clearMasterPrompt = clearMasterPrompt;
    </script>
    '''
