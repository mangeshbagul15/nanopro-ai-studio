"""
Mangesh Nano Pro AI Studio - 9:16 SQL Short Video Creation Workspace
FAANG & Top MNC Technical Interview Preparation Studio (Max 60 Seconds).
Zero Server Load: Client-Side Canvas & MediaRecorder Video Generation.
"""

def get_sql_video_workspace_html() -> str:
    return r'''
    <style>
    .sql-shorts-container {
        width: 100%;
        overflow-x: hidden;
        overflow-y: visible;
        padding-bottom: 20px;
        -webkit-overflow-scrolling: touch;
    }
    /* Highly Visible Custom Glowing Horizontal Scrollbar */
    .sql-shorts-container::-webkit-scrollbar {
        height: 12px;
    }
    .sql-shorts-container::-webkit-scrollbar-track {
        background: #070B16;
        border-radius: 6px;
        border: 1px solid #1E2D4A;
    }
    .sql-shorts-container::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #0284C7, #38BDF8, #10B981);
        border-radius: 6px;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.6);
        border: 2px solid #070B16;
    }
    .sql-shorts-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(90deg, #38BDF8, #10B981);
    }
    .sql-studio-grid {
        display: grid;
        grid-template-columns: minmax(320px, 0.8fr) minmax(380px, 1.2fr);
        width: 100%;
        max-width: 100%;
        gap: 20px;
        align-items: start;
        box-sizing: border-box;
    }
    @media (max-width: 1220px) {
        .sql-studio-grid {
            grid-template-columns: minmax(280px, 0.8fr) minmax(320px, 1.2fr);
        }
        #exportCardContainer {
            grid-column: 1 / -1;
        }
    }
    @media (max-width: 768px) {
        .sql-studio-grid {
            grid-template-columns: 1fr;
        }
        #exportCardContainer {
            grid-column: 1;
        }
    }
    .sql-shorts-container #phoneBezel {
        width: min(100%, 405px) !important;
        height: auto !important;
        aspect-ratio: 9 / 16;
    }
    .sql-shorts-container #sqlShortCanvas {
        display: block;
        width: 100% !important;
        height: auto !important;
        aspect-ratio: 9 / 16;
        object-fit: contain;
    }
    @keyframes laserPulse {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    @keyframes learnPulse {
        0%, 100% { box-shadow: 0 0 8px rgba(168, 85, 247, 0.3); border-color: #A855F7; }
        50% { box-shadow: 0 0 22px rgba(168, 85, 247, 0.85); border-color: #C084FC; }
    }
    .agent-pipeline-container {
        background: #090E1D;
        border: 1.5px solid #1E2D4A;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.5);
    }
    .agent-nodes-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        overflow-x: auto;
        padding: 8px 0;
    }
    @keyframes activeNodePulse {
        0%, 100% {
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.4), inset 0 0 8px rgba(56, 189, 248, 0.2);
            border-color: #38BDF8;
            transform: translateY(-2px);
        }
        50% {
            box-shadow: 0 0 24px rgba(56, 189, 248, 0.95), inset 0 0 14px rgba(56, 189, 248, 0.4);
            border-color: #7DD3FC;
            transform: translateY(-4px) scale(1.02);
        }
    }
    @keyframes badgeBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.55; }
    }
    .agent-node {
        background: #0B132B;
        border: 1.5px solid #1E293B;
        border-radius: 10px;
        padding: 8px 6px;
        min-width: 100px;
        max-width: 140px;
        flex: 1;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        overflow: hidden;
        word-break: break-word;
        box-sizing: border-box;
        position: relative;
    }
    .agent-node:hover {
        border-color: #38BDF8;
        background: #0f1c3d;
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25);
    }
    .agent-node .agent-badge {
        display: inline-block;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 8px;
        padding: 2px 5px;
        border-radius: 3px;
        box-sizing: border-box;
        transition: all 0.25s ease;
    }
    .agent-node.active {
        border-color: #38BDF8 !important;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.22), rgba(99, 102, 241, 0.22)) !important;
        animation: activeNodePulse 1.5s ease-in-out infinite;
    }
    .agent-node.completed {
        border-color: #10B981 !important;
        background: rgba(16, 185, 129, 0.12) !important;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.25) !important;
    }
    .agent-node.training {
        border-color: #A855F7 !important;
        background: rgba(168, 85, 247, 0.18) !important;
        animation: learnPulse 1.4s infinite;
    }
    .agent-badge.badge-running {
        color: #000 !important;
        background: #38BDF8 !important;
        font-weight: 800 !important;
        animation: badgeBlink 1s infinite ease-in-out !important;
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.8) !important;
    }
    .agent-badge.badge-done {
        color: #10B981 !important;
        background: rgba(16, 185, 129, 0.2) !important;
        font-weight: 700 !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
    }
    .agent-badge.badge-pending {
        color: #64748B !important;
        background: rgba(100, 116, 139, 0.15) !important;
    }
    .agent-connector {
        height: 3px;
        flex: 0.35;
        min-width: 14px;
        background: #1E293B;
        position: relative;
        overflow: hidden;
        border-radius: 2px;
        transition: all 0.3s ease;
    }
    .agent-connector.active {
        background: linear-gradient(90deg, #38BDF8, #6366F1, #10B981);
        background-size: 200% 100%;
        animation: laserPulse 1s linear infinite;
        box-shadow: 0 0 10px #38BDF8;
    }
    .agent-connector.completed {
        background: #10B981;
        box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
    }
    .stage-pill {
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid #1E2D4A;
        background: #0B1120;
        color: #64748B;
        transition: all 0.25s ease;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .stage-pill.active {
        background: rgba(56, 189, 248, 0.15);
        border-color: #38BDF8;
        color: #38BDF8;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
    }
    .stage-pill.done {
        background: rgba(16, 185, 129, 0.12);
        border-color: #10B981;
        color: #10B981;
    }

    /* High-Visibility Selected States for Voice Language Buttons */
    .sql-lang-btn {
        flex: 1;
        font-size: 10.5px;
        line-height: 1.2;
        padding: 7px 4px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font-weight: 600;
        white-space: normal;
        word-break: break-word;
        overflow-wrap: break-word;
        text-align: center;
        min-width: 0;
        box-sizing: border-box;
    }
    .sql-lang-btn:hover {
        border-color: #38BDF8 !important;
        color: #F8FAFC !important;
    }
    .sql-lang-btn.active {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25)) !important;
        border: 2px solid #38BDF8 !important;
        color: #38BDF8 !important;
        font-weight: 800 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.45) !important;
    }
    .sql-lang-btn.active .btn-check {
        display: inline-block;
    }

    /* High-Visibility Selected States for Subtitle Buttons */
    .sql-text-btn {
        flex: 1;
        font-size: 10.5px;
        line-height: 1.2;
        padding: 7px 4px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font-weight: 600;
        white-space: normal;
        word-break: break-word;
        overflow-wrap: break-word;
        text-align: center;
        min-width: 0;
        box-sizing: border-box;
    }
    .sql-text-btn:hover {
        border-color: #F59E0B !important;
        color: #F8FAFC !important;
    }
    .sql-text-btn.active {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(236, 72, 153, 0.25)) !important;
        border: 2px solid #F59E0B !important;
        color: #F59E0B !important;
        font-weight: 800 !important;
        box-shadow: 0 0 14px rgba(245, 158, 11, 0.45) !important;
    }
    .sql-text-btn.active .btn-check {
        display: inline-block;
    }

    /* High-Visibility Selected States for Avatar Toggle Buttons */
    .sql-avatar-btn {
        flex: 1;
        font-size: 10.5px;
        line-height: 1.2;
        padding: 7px 4px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font-weight: 600;
        white-space: normal;
        word-break: break-word;
        overflow-wrap: break-word;
        text-align: center;
        min-width: 0;
        box-sizing: border-box;
    }
    .sql-avatar-btn:hover {
        border-color: #818CF8 !important;
        color: #F8FAFC !important;
    }
    .sql-avatar-btn.active {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.25)) !important;
        border: 2px solid #818CF8 !important;
        color: #C7D2FE !important;
        font-weight: 800 !important;
        box-shadow: 0 0 14px rgba(99, 102, 241, 0.45) !important;
    }
    /* High-Visibility Selected States for 3D Motion Background Chips */
    .sql-motion-bg-chip {
        font-size: 10px;
        line-height: 1.25;
        padding: 7px 8px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 5px;
        font-weight: 600;
        white-space: normal;
        word-break: break-word;
        box-sizing: border-box;
        text-align: left;
    }
    .sql-motion-bg-chip:hover {
        border-color: #C084FC !important;
        color: #F8FAFC !important;
    }
    .sql-motion-bg-chip.active {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(56, 189, 248, 0.25)) !important;
        border: 2px solid #C084FC !important;
        color: #E9D5FF !important;
        font-weight: 800 !important;
        box-shadow: 0 0 14px rgba(168, 85, 247, 0.45) !important;
    }
    .sql-motion-bg-chip.active .btn-check {
        display: inline-block;
    }
    /* High-Visibility Selected States for Creation Mode Buttons */
    .sql-mode-btn {
        font-size: 10px;
        line-height: 1.25;
        padding: 6px 6px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #070B16 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 5px;
        font-weight: 600;
        white-space: normal;
        word-break: break-word;
        overflow-wrap: break-word;
        min-width: 0;
        box-sizing: border-box;
        text-align: left;
    }
    .sql-mode-btn span:not(.btn-check) {
        flex: 1;
        min-width: 0;
        overflow: hidden;
        word-break: break-word;
    }
    .sql-mode-btn:hover {
        border-color: #38BDF8 !important;
        color: #F8FAFC !important;
    }
    .sql-mode-btn.active {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25)) !important;
        border: 2px solid #38BDF8 !important;
        color: #38BDF8 !important;
        font-weight: 800 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.45) !important;
    }
    .sql-mode-btn.active .btn-check {
        display: inline-block;
    }

    .btn-check {
        display: none;
        font-weight: 900;
    }

    /* Complete Text Overflow & Responsive Clamping Protection */
    .text-truncate-safe {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 100% !important;
    }
    .text-break-word {
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        hyphens: auto !important;
    }
    .panel-card, .agent-node, .agent-pipeline-container {
        min-width: 0 !important;
        box-sizing: border-box !important;
    }
    .sql-shorts-container * {
        box-sizing: border-box;
    }
    .sql-shorts-container .btn {
        min-width: 0;
        box-sizing: border-box;
        overflow-wrap: break-word;
    }
    .pipeline-btn {
        white-space: nowrap !important;
        font-size: 10px !important;
        padding: 3px 8px !important;
        min-width: 0 !important;
    }
    </style>

    <!-- Hidden Native Audio Player for Voiceover Sync & Multiplexing -->
    <audio id="sqlVoiceAudio" preload="auto" crossorigin="anonymous" style="display:none;"></audio>

    <!-- 9:16 UNIVERSAL TECH SHORT & REEL STUDIO -->
    <div class="sql-shorts-container" style="margin-bottom: 24px;">
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.15)); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 26px;">🎬</span>
                    <div>
                        <h2 style="margin: 0; font-size: 18px; color: #38BDF8; font-weight: 800; letter-spacing: 0.5px;">UNIVERSAL TECH AI VIDEO MAKER (9:16 SHORTS &amp; REELS)</h2>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">SQL • Python • Snowflake • AWS • Data Engineering • AI/RAG • Cloud • Docker • Git • ML • 100% Prompt-Driven • Zero Watermark</div>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="status-pill" style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #10B981; font-size: 11px; padding: 4px 10px; border-radius: 20px;">⚡ All Video APIs Active</span>
                <span class="status-pill" style="background: rgba(236, 72, 153, 0.15); border: 1px solid #EC4899; color: #EC4899; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🛡️ 100% Watermark-Free</span>
                <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; font-size: 11px; padding: 4px 10px; border-radius: 20px;">📱 Full-Length 9:16 Video</span>
                <span class="status-pill" style="background: rgba(139, 92, 246, 0.15); border: 1px solid #8B5CF6; color: #8B5CF6; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🔊 Regional AI Voice Live</span>
                <span class="status-pill" style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #F59E0B; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🤖 Coding Intelligence Models Live</span>
            </div>
        </div>


        <!-- Main Studio Grid (Controls + Phone Preview + Sandbox) -->
        <div class="sql-studio-grid" id="sqlStudioMainGrid">
            
            <!-- COLUMN 1: AI Prompt Generator & Language Controls -->
            <!-- COLUMN 1: AI Prompt Generator & Language Controls -->
            <div class="panel-card" style="margin: 0; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 12px; padding: 18px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <h3 style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 700;">1. MASTER PROMPT &amp; TECH SCENARIO INPUT</h3>
                    <span style="font-size: 11px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 8px; border-radius: 6px; font-weight: 700;">✨ Prompt-Led Animation</span>
                </div>

                <!-- Hidden inputs to preserve JS state compatibility -->
                <input type="hidden" id="sqlShortCreationMode" value="dynamic_ai" />
                <input type="hidden" id="sqlCinematicBgSelect" value="cyber_matrix" />

                <!-- Master Prompt Input Textarea -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <label class="input-label" style="font-size: 12px; color: #38BDF8; font-weight: 700; margin: 0;">
                        📝 Tech Concept / Master Prompt Input:
                    </label>
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary" onclick="clearMasterPrompt()" style="font-size: 10px; padding: 4px 10px; border-color: #EF4444; color: #EF4444; font-weight: 700;" title="Clear prompt input">
                            🧹 Clear Prompt
                        </button>
                    </div>
                </div>

                <textarea class="studio-input" id="sqlShortQuestion" rows="9" placeholder="तुमचा कोणताही मास्टर प्रॉम्प्ट (Master Prompt) इथे प्रविष्ट करा:

१. थेट प्रश्न (Question): 'Find 2nd highest salary in SQL' किंवा 'Clustered vs Non-Clustered index'
२. तयार व्हॉईस स्क्रिप्ट (TTS Script): 'नमस्कार मित्रांनो, आज आपण पाहणार आहोत...'
३. थेट कोड (Raw Code): 'SELECT emp_id, DENSE_RANK() OVER (ORDER BY salary DESC)...'
४. संकल्पना / आर्किटेक्चर (Topic): 'Local server vs Claude server' किंवा 'Microservices vs Monolith'

✨ तुमच्या prompt मधील विषय आणि narration नुसार प्रत्येक scene चे animated visuals बनतील. कोणताही ठराविक video template वापरला जाणार नाही." style="width: 100%; margin-bottom: 16px; background: #070B16; border: 1.5px solid #283C62; color: #F8FAFC; font-size: 13px; font-family: monospace; border-radius: 8px; padding: 12px; line-height: 1.6; resize: vertical;"></textarea>

                <!-- Natural Teacher Voice Language Selection -->
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1E2D4A; border-radius: 8px; padding: 14px; margin-bottom: 18px;">
                    <div style="font-size: 11px; font-weight: 700; color: #38BDF8; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; display:flex; justify-content:space-between; align-items:center;">
                        <span>🎙️ Natural Teacher Voice Language</span>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span id="activeVoiceBadge" style="color:#10B981; font-weight:700;">मराठी शिक्षक</span>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 8px;">
                        <button type="button" class="sql-lang-btn active" id="btnAudioMr" onclick="setSqlAudioLang('mr')">
                            <span class="btn-check">✓</span> <span>🇮🇳 मराठी</span>
                        </button>
                        <button type="button" class="sql-lang-btn" id="btnAudioHi" onclick="setSqlAudioLang('hi')">
                            <span class="btn-check">✓</span> <span>🇮🇳 हिन्दी</span>
                        </button>
                        <button type="button" class="sql-lang-btn" id="btnAudioEn" onclick="setSqlAudioLang('en')">
                            <span class="btn-check">✓</span> <span>🇬🇧 English</span>
                        </button>
                    </div>
                </div>

                <!-- Generate from the prompt. The final full-length export is below the preview. -->
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button type="button" class="btn btn-primary" id="btnGenerateSqlBlueprint" onclick="generateSqlShortBlueprint()" style="width: 100%; padding: 14px; font-weight: 800; font-size: 14px; background: linear-gradient(135deg, #0284C7, #6366F1); border: none; border-radius: 8px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 15px rgba(2,132,199,0.4);">
                        <span>⚡ Generate AI Video &amp; Voice from Master Prompt</span>
                    </button>

                </div>
            </div>

            <!-- COLUMN 2: 9:16 Smartphone Mockup Live Player (Trending UI) -->
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">
                    <span style="font-size: 12px; font-weight: 700; color: #38BDF8;">2. 9:16 SMARTPHONE PREVIEW (PROMPT-DRIVEN)</span>
                    <span id="playerTimer" style="font-size: 12px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 0:00</span>
                </div>

                <!-- Smartphone Bezel Mockup -->
                <div id="phoneBezel" style="width: 340px; height: 604px; background: #000000; border: 4px solid #1E2D4A; border-radius: 36px; box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 25px rgba(56,189,248,0.2); position: relative; overflow: hidden; display: flex; flex-direction: column;">
                    
                    <!-- Top Phone Island Notch -->
                    <div style="height: 28px; width: 100%; display: flex; justify-content: center; align-items: center; position: absolute; top: 0; left: 0; z-index: 10; pointer-events: none;">
                        <div style="width: 85px; height: 16px; background: #0F172A; border-radius: 20px; border: 1px solid #1E293B; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                            <div style="width: 6px; height: 6px; background: #0284C7; border-radius: 50%;"></div>
                        </div>
                    </div>

                    <!-- 9:16 Canvas Viewport (1080x1920 logical, scaled via CSS) -->
                    <canvas id="sqlShortCanvas" width="1080" height="1920" style="width: 100%; height: 100%; background: #070B16; object-fit: contain;"></canvas>

                    <!-- Bottom Audio Wave Indicator -->
                    <div id="canvasAudioWave" style="position: absolute; bottom: 8px; left: 16px; right: 16px; height: 18px; display: flex; align-items: center; justify-content: space-between; z-index: 10; pointer-events: none;">
                        <div style="font-size: 10px; color: #38BDF8; font-weight: 700; text-shadow: 0 1px 3px #000;">@Code_With_Mangesh</div>
                        <div style="display: flex; gap: 3px; align-items: center;">
                            <span class="wave-bar" style="width: 3px; height: 8px; background: #10B981; border-radius: 2px;"></span>
                            <span class="wave-bar" style="width: 3px; height: 14px; background: #38BDF8; border-radius: 2px;"></span>
                            <span class="wave-bar" style="width: 3px; height: 10px; background: #6366F1; border-radius: 2px;"></span>
                            <span class="wave-bar" style="width: 3px; height: 6px; background: #EC4899; border-radius: 2px;"></span>
                        </div>
                    </div>
                </div>

                <!-- Player Transport Controls -->
                <div style="width: 100%; max-width: 340px; margin-top: 12px; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 10px; padding: 10px;">
                    <!-- Timeline Scrubber -->
                    <input type="range" id="sqlShortScrubber" min="0" max="60" value="0" step="0.1" oninput="seekSqlShortPlayer(this.value)" style="width: 100%; accent-color: #38BDF8; cursor: pointer; margin-bottom: 8px;" />
                    
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; gap: 6px;">
                            <button type="button" class="btn btn-secondary" id="btnPlayPause" onclick="toggleSqlShortPlay()" style="padding: 4px 10px; font-size: 12px;">▶ Play</button>
                            <button type="button" class="btn btn-secondary" onclick="restartSqlShortPlay()" style="padding: 4px 10px; font-size: 12px;">🔄 Replay</button>
                        </div>
                        <div style="font-size: 11px; color: #94A3B8;">
                            Speed: 
                            <select id="sqlShortSpeed" onchange="setSqlShortSpeed(this.value)" style="background:#070B16; color:#F8FAFC; border:1px solid #283C62; border-radius:4px; padding:2px 4px; font-size:11px;">
                                <option value="1">1x</option>
                                <option value="1.25">1.25x</option>
                                <option value="1.5">1.5x</option>
                                <option value="2">2x</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <!-- COLUMN 3: 1-CLICK EXPORT & STATUS MONITOR -->
            <div id="exportCardContainer" style="display: flex; flex-direction: column; gap: 16px;">
                
                <!-- 1. PRIMARY EXPORT CARD -->
                <div class="panel-card" style="margin: 0; background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(6, 182, 212, 0.12)); border: 1.5px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 800; color: #10B981; display: flex; align-items: center; gap: 6px;">
                            <span>🎬</span> <span>1-CLICK 9:16 VIDEO EXPORT</span>
                        </span>
                        <span style="font-size: 10px; background: rgba(236,72,153,0.2); color: #F472B6; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(236,72,153,0.4); font-weight: 700;">🛡️ 100% Zero-Watermark</span>
                    </div>
                    <div style="font-size: 11px; color: #94A3B8; margin-bottom: 14px; line-height: 1.5;">
                        1080x1920 फुल-एचडी रेंडरिंग सोबत नॅचरल AI शिक्षक ऑडिओ इंटिग्रेटेड, पूर्ण narration duration सह! कोपऱ्यातील वॉटरमार्क 100% रिमूव्ह केले जातात.
                    </div>

                    <!-- Direct Download Button Group -->
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 12px 10px; font-weight: 900; font-size: 12px; letter-spacing: 0.3px; background: linear-gradient(135deg, #10B981, #06B6D4); border: none; border-radius: 8px; cursor: pointer; color: #000; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 15px rgba(16,185,129,0.35); white-space: normal; line-height: 1.3; text-align: center; word-break: break-word; box-sizing: border-box;">
                            <span style="font-size: 18px; flex-shrink: 0;">📥</span>
                            <span id="exportBtnLabel">DOWNLOAD FULL 9:16 VIDEO (VOICE SYNCED MP4)</span>
                        </button>

                        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                            <button type="button" class="btn btn-secondary" onclick="downloadVoiceoverMp3()" id="btnDownloadAudioOnly" style="flex: 1 1 90px; padding: 7px 4px; font-size: 10.5px; font-weight: 700; border-color: #10B981; color: #10B981; white-space: normal; line-height: 1.2; text-align: center; word-break: break-word; min-width: 0;" title="Download Teacher Audio (MP3)">
                                🎵 Save Voice
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="downloadCurrentFrameAsPng()" style="flex: 1 1 90px; padding: 7px 4px; font-size: 10.5px; font-weight: 700; border-color: #F59E0B; color: #F59E0B; white-space: normal; line-height: 1.2; text-align: center; word-break: break-word; min-width: 0;" title="Save current frame as HD PNG">
                                📸 Save Frame
                            </button>
                        </div>
                    </div>

                    <!-- Progress Bar & Remaining Time Stats (Shows during export) -->
                    <div id="exportProgressBarContainer" style="display:none; background: #0B1120; border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; margin-top: 14px;">
                        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #38BDF8; font-weight: 700; margin-bottom: 6px;">
                            <span id="exportStageDesc">⏳ व्हिडिओ व ऑडिओ एकत्र रेंडर होत आहे...</span>
                            <span id="exportPercentNum" style="font-family: monospace; font-size: 13px; color: #10B981;">0%</span>
                        </div>
                        <div style="height: 12px; width: 100%; background: #1E2D4A; border-radius: 6px; overflow: hidden; margin-bottom: 8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.6);">
                            <div id="exportProgressFill" style="height: 100%; width: 0%; background: linear-gradient(90deg, #0284C7, #38BDF8, #10B981); transition: width 0.1s linear; border-radius: 6px;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94A3B8; font-family: monospace;">
                            <span id="exportEstTime" style="color: #F59E0B; font-weight: 700;">⏱️ अंदाजे वेळ: मोजत आहे...</span>
                            <span id="exportFrameStats">🎞️ फ्रेम: 0 / narration duration</span>
                        </div>
                    </div>

                    <!-- Celebration & Video Ready Card -->
                    <div id="videoReadyCelebration" style="display:none; background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(6,182,212,0.25)); border: 2px solid #10B981; border-radius: 8px; padding: 14px; text-align: center; margin-top: 14px; animation: popIn 0.3s ease-out;">
                        <div style="font-size: 26px;">🎉 🏆 🎬</div>
                        <div style="font-size: 14px; font-weight: 800; color: #10B981; margin-top: 4px;">व्हिडिओ यशस्वीरित्या तयार झाला!</div>
                        <div style="font-size: 11px; color: #CBD5E1; margin: 4px 0 10px;">100% वॉटरमार्क-फ्री • ऑडिओ इंटिग्रेटेड • 1080x1920 (9:16) डाऊनलोड पूर्ण झाले!</div>
                        <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
                            <a id="btnDownloadAgain" href="#" class="btn btn-primary" style="font-size: 11px; padding: 7px 14px; background: linear-gradient(135deg, #10B981, #06B6D4); color: #000; font-weight: 800; border-radius: 6px; text-decoration: none; display: flex; align-items: center; gap: 4px;">
                                <span>📥 पुन्हा सेव्ह करा (Save File)</span>
                            </a>
                            <button type="button" class="btn btn-secondary" onclick="restartSqlShortPlay()" style="font-size: 11px; padding: 7px 14px; border-color: #38BDF8; color: #38BDF8; font-weight: 700;">
                                <span>▶ फोनवर पाहा (Preview)</span>
                            </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- NANO PRO 12-AGENT BRAIN MATRIX & PERFECTIONIST AUDIT MODAL -->
    <div id="agentBrainModal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(10px); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
        <div style="background: #090E1D; border: 2px solid #38BDF8; border-radius: 14px; width: 100%; max-width: 980px; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 50px rgba(0,0,0,0.85), 0 0 35px rgba(56,189,248,0.3);">
            <!-- Modal Header -->
            <div style="background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,241,0.2)); border-bottom: 1.5px solid #1E2D4A; padding: 16px 22px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 24px;">🧠</span>
                    <div>
                        <h3 style="margin: 0; font-size: 16px; color: #38BDF8; font-weight: 800; letter-spacing: 0.5px;">NANOPRO MASTER AGENT BRAIN MATRIX &amp; 6-TRIAL AUDIT</h3>
                        <div style="font-size: 11px; color: #94A3B8;">12 Autonomous Specialist Agents • 6 Validation Trials • Real-Time Model Thoughts &amp; AST Verifications</div>
                    </div>
                </div>
                <button type="button" onclick="closeAgentBrainModal()" style="background: #1E293B; border: 1px solid #334155; color: #F8FAFC; border-radius: 6px; padding: 6px 14px; cursor: pointer; font-size: 13px; font-weight: 700;">✕ Close</button>
            </div>

            <!-- Modal Content (Scrollable) -->
            <div style="padding: 20px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 18px;">
                <!-- 6-Trial Perfectionist Audit Card -->
                <div style="background: rgba(16,185,129,0.08); border: 1.5px solid rgba(16,185,129,0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 13px; font-weight: 800; color: #10B981; display: flex; align-items: center; gap: 6px;">
                            <span>🛡️</span> <span>6-TRIAL PERFECTIONIST AUDIT LEDGER (100% ACCURACY ASSURANCE)</span>
                        </span>
                        <span id="modalAuditScoreBadge" style="font-size: 12px; font-weight: 800; background: rgba(16,185,129,0.2); color: #10B981; padding: 3px 12px; border-radius: 20px; border: 1px solid #10B981;">
                            Score: 99.8% (AAA+ Enterprise Ready)
                        </span>
                    </div>
                    <div id="modalAuditTrialsGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 8px;">
                        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 6px; padding: 8px 10px; font-size: 11px;">
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 1: Python AST &amp; ANSI SQL Syntax</div>
                            <div style="color: #94A3B8; font-size: 10px;">Zero syntax errors, balanced clauses, valid keywords</div>
                        </div>
                        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 6px; padding: 8px 10px; font-size: 11px;">
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 2: Speech Pacing &amp; Full Duration</div>
                            <div style="color: #94A3B8; font-size: 10px;">Scene timings follow the complete generated narration; no 60-second cutoff.</div>
                        </div>
                        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 6px; font-size: 11px; padding: 8px 10px;">
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 3: 6-Stage Curriculum Progression</div>
                            <div style="color: #94A3B8; font-size: 10px;">Problem ➔ Component ➔ Flow ➔ Build ➔ Sim ➔ Golden Takeaway</div>
                        </div>
                        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 6px; font-size: 11px; padding: 8px 10px;">
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 4: Enterprise Edge-Case Traps</div>
                            <div style="color: #94A3B8; font-size: 10px;">NULL handling, ties, partition boundary traps embedded</div>
                        </div>
                        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 6px; font-size: 11px; padding: 8px 10px;">
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 5: Kinetic Neon Arrow Highlights</div>
                            <div style="color: #94A3B8; font-size: 10px;">Arrow pointer strictly locked to spoken keywords</div>
                        </div>
                        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 6px; font-size: 11px; padding: 8px 10px;">
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 6: Zero Voice Overrun Guarantee</div>
                            <div style="color: #94A3B8; font-size: 10px;">Outro branding scheduled strictly post-narration completion</div>
                        </div>
                    </div>
                </div>

                <!-- 12 Specialist Agents Brain Thoughts Stream -->
                <div>
                    <div style="font-size: 13px; font-weight: 800; color: #38BDF8; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <span>🤖 12 SPECIALIST AGENTS — REAL-TIME THOUGHT STREAM &amp; SLAs</span>
                        <span style="font-size: 11px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 8px; border-radius: 6px;">All 12 Agents Active</span>
                    </div>
                    <div id="modalAgentsStreamGrid" style="display: flex; flex-direction: column; gap: 8px;">
                        <!-- Agent rows populated dynamically via JS -->
                    </div>
                </div>
            </div>
        </div>
    </div>



    <!-- ELEVENLABS VOICE AI STUDIO & 28-32Y INDIAN MALE TECH YOUTUBER PERSONA MODAL -->
    <div id="elevenLabsVoiceModal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(10px); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
        <div style="background: #090E1D; border: 2px solid #8B5CF6; border-radius: 14px; width: 100%; max-width: 940px; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 50px rgba(0,0,0,0.85), 0 0 35px rgba(139,92,246,0.35);">
            <!-- Modal Header -->
            <div style="background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(6,182,212,0.25)); border-bottom: 1.5px solid #1E2D4A; padding: 16px 22px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 26px;">🎙️</span>
                    <div>
                        <h3 style="margin: 0; font-size: 16px; color: #C4B5FD; font-weight: 800; letter-spacing: 0.5px;">ELEVENLABS HUMANLIKE VOICE AI STUDIO &amp; REGIONAL VOICE ENGINE</h3>
                        <div style="font-size: 11px; color: #94A3B8;">Natural Human Delivery • Videos/Shorts, Audiobooks, Podcasts, Ads • Infallible Edge-TTS Cascade</div>
                    </div>
                </div>
                <button type="button" onclick="closeElevenLabsModal()" style="background: #1E293B; border: 1px solid #334155; color: #F8FAFC; border-radius: 6px; padding: 6px 14px; cursor: pointer; font-size: 13px; font-weight: 700;">✕ Close</button>
            </div>

            <!-- Modal Content (Scrollable) -->
            <div style="padding: 20px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 16px;">
                <!-- Highlighted Persona Card: 25-35y Indian Male Tech Educator -->
                <div style="background: linear-gradient(135deg, rgba(56,189,248,0.12), rgba(16,185,129,0.12)); border: 2px solid #10B981; border-radius: 12px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 26px;">🇮🇳</span>
                            <div>
                                <div style="font-size: 15px; font-weight: 800; color: #10B981;">INDIAN MALE TECH EDUCATOR &amp; YOUTUBE CREATOR (25–35 Years Old)</div>
                                <div style="font-size: 11px; color: #94A3B8;">Natural Hindi + English Technical Words • Model: <b>Eleven v4</b> (Flagship) • Edge-TTS Madhur Cascade</div>
                            </div>
                        </div>
                        <span style="font-size: 11px; background: rgba(16,185,129,0.2); color: #10B981; border: 1.5px solid #10B981; padding: 4px 12px; border-radius: 20px; font-weight: 800;">
                            ✨ Default Primary Persona (Eleven v4 Active)
                        </span>
                    </div>

                    <!-- 12-Attribute Specification Matrix Table -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 8px; font-size: 11px; color: #CBD5E1;">
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">🗣️ <b>Language:</b> Hindi + English tech terms</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">🎙️ <b>Voice:</b> Indian Male (25–35 years)</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">🤝 <b>Tone:</b> Friendly + Professional</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">💡 <b>Emotion:</b> Curious + Confident</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">⚡ <b>Speed:</b> Medium-Fast (Reel Pacing)</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">🇮🇳 <b>Accent:</b> Natural Indian Hindi</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">🔥 <b>Energy:</b> Medium-High</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">⏸️ <b>Pauses:</b> प्रश्नानंतर, महत्त्वाच्या मुद्द्यांनंतर</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">📈 <b>Expression:</b> Natural, engaging cadence</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">💻 <b>Pronunciation:</b> SQL, Python, JOIN स्पष्ट</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #1E293B;">👨‍🏫 <b>Delivery:</b> Coding teacher + Tech creator</div>
                        <div style="background: rgba(15,23,42,0.85); padding: 7px 10px; border-radius: 6px; border: 1px solid #A855F7; color: #C084FC;">🤖 <b>Model:</b> Eleven v4 (Flagship AI)</div>
                    </div>
                </div>

                <!-- Model & Category Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
                    <!-- Model Selector -->
                    <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 10px; padding: 14px;">
                        <label style="font-size: 12px; font-weight: 700; color: #38BDF8; display: block; margin-bottom: 8px;">
                            🤖 ElevenLabs Model Architecture:
                        </label>
                        <select id="modalElevenLabsModelSelect" style="width: 100%; background: #070B16; color: #F8FAFC; border: 1px solid #283C62; border-radius: 6px; padding: 8px; font-size: 12px;">
                            <option value="eleven_v4" selected>⚡ Eleven v4 (Flagship Next-Gen • Context-Aware Emotional Voice AI)</option>
                            <option value="eleven_v4_turbo">Eleven v4 Turbo (Ultra-Low Latency ~100ms • Real-Time)</option>
                            <option value="eleven_multilingual_v2">Eleven Multilingual v2 (Proven Natural • 29+ Langs)</option>
                            <option value="eleven_turbo_v2_5">Eleven Turbo v2.5 (Low Latency ~250ms • High Quality)</option>
                            <option value="eleven_flash_v2_5">Eleven Flash v2.5 (Super Fast ~75ms • Realtime)</option>
                        </select>
                        <div style="font-size: 10px; color: #94A3B8; margin-top: 6px;">
                            Eleven v4 infers intent, emotional curiosity on questions, and confident delivery from context.
                        </div>
                    </div>

                    <!-- Category / Use Case -->
                    <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 10px; padding: 14px;">
                        <label style="font-size: 12px; font-weight: 700; color: #38BDF8; display: block; margin-bottom: 8px;">
                            🎯 Audio Production Category:
                        </label>
                        <select id="modalElevenLabsCategorySelect" style="width: 100%; background: #070B16; color: #F8FAFC; border: 1px solid #283C62; border-radius: 6px; padding: 8px; font-size: 12px;">
                            <option value="indian_tech_youtuber" selected>📱 Indian Tech Educator (Reels &amp; YouTube Shorts)</option>
                            <option value="videos">🎬 General Videos &amp; Explainer Content</option>
                            <option value="audiobooks">📚 Audiobooks &amp; Deep Educational Narration</option>
                            <option value="podcasts">🎙️ Technical Podcasts &amp; Discussions</option>
                            <option value="ads">📢 Commercial Ads &amp; High Energy Promos</option>
                        </select>
                        <div style="font-size: 10px; color: #94A3B8; margin-top: 6px;">
                            Optimizes stability, similarity boost, and style cadence for the format.
                        </div>
                    </div>
                </div>

                <!-- Live Voice Synthesis & Preview Box -->
                <div style="background: #070B16; border: 1px solid #1E2D4A; border-radius: 10px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <label style="font-size: 12px; font-weight: 700; color: #C4B5FD;">
                            🔊 Live Voice Synthesis Preview:
                        </label>
                        <span id="modalElevenLabsQuotaStatus" style="font-size: 10px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 8px; border-radius: 4px;">
                            Checking Quota...
                        </span>
                    </div>
                    <textarea id="modalElevenLabsSampleText" rows="3" style="width: 100%; background: #0B132B; border: 1.5px solid #283C62; color: #F8FAFC; font-size: 12px; border-radius: 6px; padding: 8px; resize: vertical;" placeholder="Enter text to synthesize...">हेलो दोस्तों! क्या आप जानते हैं कि SQL में DENSE_RANK और ROW_NUMBER में क्या फर्क होता है? चलिए 60 सेकंड में समझते हैं!</textarea>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; flex-wrap: wrap; gap: 8px;">
                        <audio id="modalElevenLabsAudioPlayer" controls style="height: 34px; max-width: 320px; display: none;"></audio>
                        <div style="display: flex; gap: 8px; margin-left: auto;">
                            <button type="button" class="btn btn-secondary" onclick="synthesizeElevenLabsSample()" id="btnSynthesizeSample" style="font-size: 11px; padding: 6px 14px; font-weight: 700; border-color: #8B5CF6; color: #C4B5FD; display: flex; align-items: center; gap: 6px;">
                                <span>▶ Synthesize &amp; Listen Now</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- API Key Vault 1-Click Update Card -->
                <div style="background: rgba(245,158,11,0.06); border: 1.5px solid rgba(245,158,11,0.3); border-radius: 10px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 12px; font-weight: 700; color: #F59E0B;">🔑 ElevenLabs API Key (Stored Securely in Credentials Vault):</span>
                        <span id="modalKeySavedBadge" style="font-size: 10px; color: #10B981; display: none;">✓ Key Saved!</span>
                    </div>
                    <div style="display: flex; gap: 8px; margin-top: 6px;">
                        <input type="password" id="modalElevenLabsApiKeyInput" placeholder="sk_... (Paste your ElevenLabs API Key here)" style="flex: 1; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; border-radius: 6px; padding: 8px 10px; font-size: 12px; font-family: monospace;" />
                        <button type="button" class="btn btn-primary" onclick="saveElevenLabsKeyFromModal()" style="font-size: 11px; padding: 8px 16px; background: linear-gradient(135deg, #F59E0B, #10B981); color: #000; font-weight: 800; border: none; border-radius: 6px; cursor: pointer;">
                            💾 Save Key
                        </button>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; margin-top: 6px;">
                        Shield Guarantee: If your ElevenLabs quota runs out, the studio automatically cascades to <b>hi-IN-MadhurNeural</b> with zero interruption or crashes.
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
    <!-- END 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    '''
