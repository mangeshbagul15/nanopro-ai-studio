# -*- coding: utf-8 -*-

"""

Mangesh Nano Pro AI Studio - 2026 VFX-Style Universal Tech AI Video Maker

State-of-the-art 9:16 Shorts & Reels Studio:

- 4-Tier Multi-Stage API Docks: Prompt-to-Voice • Voice-to-Video Lip-Sync • Prompt-to-Video B-Roll • Unified Aggregators

- 100% AI Generated, Live Dynamic APIs, Titanium Smartphone Preview, and VFX 1-Click Export!

"""



def get_sql_video_workspace_html() -> str:

    return """

    <style>

    /* =========================================================================

       ↔️ FULL VIEW HORIZONTAL SCROLLBAR & TECH CONTAINER

       ========================================================================= */

    .vfx-horizontal-scroll-container {

        width: 100%;

        max-width: 100%;

        overflow-x: auto !important;

        overflow-y: visible;

        padding-bottom: 24px;

        box-sizing: border-box;

        scroll-behavior: smooth;

    }

    .vfx-horizontal-scroll-container::-webkit-scrollbar {

        height: 12px;

        background: #070B16;

        border-radius: 8px;

    }

    .vfx-horizontal-scroll-container::-webkit-scrollbar-track {

        background: rgba(15, 23, 42, 0.9);

        border: 1px solid rgba(56, 189, 248, 0.3);

        border-radius: 8px;

    }

    .vfx-horizontal-scroll-container::-webkit-scrollbar-thumb {

        background: linear-gradient(90deg, #0284C7, #38BDF8, #10B981);

        border-radius: 8px;

        border: 2px solid #070B16;

        box-shadow: 0 0 14px rgba(56, 189, 248, 0.6);

    }

    .vfx-horizontal-scroll-container::-webkit-scrollbar-thumb:hover {

        background: linear-gradient(90deg, #38BDF8, #818CF8, #34D399);

    }



    .vfx-video-root {

        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

        color: #F8FAFC;

        width: 100%;

        max-width: 1440px;

        margin: 0 auto;

        box-sizing: border-box;

    }



    /* =========================================================================

       KOKONUT UI, BLACKLIST UI & MOTION.DEV MODERN STYLING

       ========================================================================= */

    :root {

        --spring-smooth: cubic-bezier(0.16, 1, 0.3, 1);

        --spring-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

        --kokonut-glow: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.25), transparent 70%);

        --blacklist-dark: #050811;

        --blacklist-card: rgba(10, 16, 32, 0.88);

        --blacklist-border: rgba(56, 189, 248, 0.28);

    }



    /* Kokonut UI Frosted Glass Card with Hover Sheen */

    .kokonut-card {

        background: var(--blacklist-card);

        border: 1.5px solid var(--blacklist-border);

        border-radius: 16px;

        backdrop-filter: blur(20px);

        -webkit-backdrop-filter: blur(20px);

        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);

        position: relative;

        overflow: hidden;

        transition: all 0.35s var(--motion-smooth);

    }

    .kokonut-card:hover {

        border-color: rgba(56, 189, 248, 0.65);

        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.25);

        transform: translateY(-2px);

    }



    /* Kokonut UI Shimmering Conic Glow Sheen */

    .kokonut-card::after {

        content: '';

        position: absolute;

        top: 0; left: 0; right: 0;

        height: 2px;

        background: linear-gradient(90deg, transparent, #38BDF8, #10B981, #8B5CF6, transparent);

        opacity: 0.8;

    }



    /* Kokonut UI Pill Badge with Pulsing Neon Dot */

    .kokonut-badge {

        display: inline-flex;

        align-items: center;

        gap: 6px;

        padding: 3px 10px;

        border-radius: 9999px;

        font-size: 10.5px;

        font-weight: 700;

        letter-spacing: 0.3px;

        background: rgba(15, 23, 42, 0.85);

        border: 1px solid rgba(56, 189, 248, 0.3);

        color: #F8FAFC;

    }

    .kokonut-pulse-dot {

        width: 6px;

        height: 6px;

        border-radius: 50%;

        background: #10B981;

        box-shadow: 0 0 8px #10B981;

        animation: kokonutDotPulse 2s infinite ease-in-out;

    }

    @keyframes kokonutDotPulse {

        0%, 100% { opacity: 1; transform: scale(1); }

        50% { opacity: 0.35; transform: scale(0.85); }

    }



    /* Blacklist UI Cyber Dark HUD Container */

    .blacklist-hud {

        background: var(--blacklist-dark);

        border: 1.5px solid #1E293B;

        border-radius: 12px;

        font-family: 'JetBrains Mono', 'Fira Code', monospace;

        position: relative;

    }

    .blacklist-tag {

        font-family: 'JetBrains Mono', 'Fira Code', monospace;

        font-size: 10px;

        font-weight: 800;

        letter-spacing: 0.5px;

        color: #38BDF8;

    }



    /* Motion.dev Tactile Spring Button Feedback */

    .motion-spring-btn {

        transition: transform 0.2s var(--spring-bounce), box-shadow 0.2s var(--spring-smooth);

        cursor: pointer;

    }

    .motion-spring-btn:hover {

        transform: translateY(-2px) scale(1.01);

        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.35);

    }

    .motion-spring-btn:active {

        transform: translateY(1px) scale(0.97);

    }



    /* Anime.js Kinetic Typography Highlights */

    .kinetic-subtitle-glow {

        text-shadow: 0 0 16px rgba(56, 189, 248, 0.8), 0 2px 4px rgba(0, 0, 0, 0.9);

    }



    /* 2026 VFX Holographic Cyber Studio Styling */

    .vfx-video-root {

        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

        color: #F8FAFC;

    }



    .vfx-glow-box {

        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(7, 11, 22, 0.98));

        border: 1px solid rgba(56, 189, 248, 0.35);

        border-radius: 14px;

        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.12);

        backdrop-filter: blur(12px);

        transition: border-color 0.3s ease, box-shadow 0.3s ease;

    }

    .vfx-glow-box:hover {

        border-color: rgba(56, 189, 248, 0.65);

        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8), 0 0 35px rgba(56, 189, 248, 0.2);

    }



    .vfx-dock-grid {

        display: grid;

        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));

        gap: 12px;

        margin-bottom: 18px;

    }



    .vfx-dock-card {

        background: rgba(11, 19, 43, 0.85);

        border: 1.5px solid #1E2D4A;

        border-radius: 10px;

        padding: 12px 14px;

        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

        display: flex;

        flex-direction: column;

        justify-content: space-between;

        position: relative;

        overflow: hidden;

    }

    .vfx-dock-card::before {

        content: '';

        position: absolute;

        top: 0;

        left: 0;

        right: 0;

        height: 2px;

        background: linear-gradient(90deg, transparent, #38BDF8, transparent);

        opacity: 0;

        transition: opacity 0.3s ease;

    }

    .vfx-dock-card:hover {

        border-color: #38BDF8;

        transform: translateY(-2px);

        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.2);

    }

    .vfx-dock-card:hover::before {

        opacity: 1;

    }



    .vfx-dock-title {

        font-size: 11px;

        font-weight: 800;

        letter-spacing: 0.5px;

        text-transform: uppercase;

        display: flex;

        align-items: center;

        gap: 6px;

        margin-bottom: 8px;

    }



    .vfx-dock-select {

        width: 100%;

        background: #070B16;

        border: 1px solid #283C62;

        color: #F8FAFC;

        font-size: 11.5px;

        font-weight: 700;

        border-radius: 6px;

        padding: 7px 10px;

        outline: none;

        transition: border-color 0.2s ease;

        cursor: pointer;

    }

    .vfx-dock-select:focus {

        border-color: #38BDF8;

        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);

    }



    .vfx-quick-chip {

        font-size: 10px;

        padding: 4px 10px;

        border-radius: 20px;

        background: rgba(15, 23, 42, 0.8);

        border: 1px solid #1E2D4A;

        color: #94A3B8;

        cursor: pointer;

        transition: all 0.2s ease;

        display: inline-flex;

        align-items: center;

        gap: 4px;

        white-space: nowrap;

    }

    .vfx-quick-chip:hover {

        background: rgba(56, 189, 248, 0.15);

        border-color: #38BDF8;

        color: #38BDF8;

        transform: scale(1.03);

    }



    /* Studio Main 3-Column Grid */

    .vfx-studio-grid {

        display: grid;

        grid-template-columns: 1.15fr 360px 1fr;

        gap: 20px;

        align-items: start;

    }



    @media (max-width: 1200px) {

        .vfx-studio-grid {

            grid-template-columns: 1fr 360px;

        }

    }

    @media (max-width: 900px) {

        .vfx-studio-grid {

            grid-template-columns: 1fr;

        }

    }



    /* Audio wave animation: ONLY active when playing */

    @keyframes wavePulse {

        0%, 100% { height: 4px; opacity: 0.4; }

        50% { height: 16px; opacity: 1; }

    }

    .vfx-wave-bar {

        width: 3px;

        height: 4px;

        background: #10B981;

        border-radius: 2px;

        transition: height 0.2s ease;

    }

    .vfx-wave-bar:nth-child(2) { background: #38BDF8; }

    .vfx-wave-bar:nth-child(3) { background: #8B5CF6; }

    .vfx-wave-bar:nth-child(4) { background: #EC4899; }

    .vfx-wave-bar.playing,

    .vfx-wave-bar.active,

    .is-playing .vfx-wave-bar {

        animation: wavePulse 1.2s ease-in-out infinite;

    }

    .vfx-wave-bar.playing:nth-child(2),

    .vfx-wave-bar.active:nth-child(2),

    .is-playing .vfx-wave-bar:nth-child(2) { animation-delay: 0.2s; }

    .vfx-wave-bar.playing:nth-child(3),

    .vfx-wave-bar.active:nth-child(3),

    .is-playing .vfx-wave-bar:nth-child(3) { animation-delay: 0.4s; }

    .vfx-wave-bar.playing:nth-child(4),

    .vfx-wave-bar.active:nth-child(4),

    .is-playing .vfx-wave-bar:nth-child(4) { animation-delay: 0.6s; }



    /* Language Buttons */

    .sql-lang-btn {

        font-size: 11px;

        padding: 8px 14px;

        border-radius: 8px;

        cursor: pointer;

        border: 1.5px solid #1E2D4A;

        background: #070B16;

        color: #94A3B8;

        transition: all 0.2s ease;

        display: flex;

        align-items: center;

        gap: 6px;

        font-weight: 700;

        flex: 1;

        justify-content: center;

    }

    .sql-lang-btn:hover {

        border-color: #38BDF8;

        color: #F8FAFC;

    }

    .sql-lang-btn.active {

        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25));

        border: 2px solid #38BDF8;

        color: #38BDF8;

        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);

    }

    .sql-lang-btn .btn-check { display: none; font-weight: 900; }

    .sql-lang-btn.active .btn-check { display: inline-block; }



    /* Pulse Laser Button */

    @keyframes laserPulse {

        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.5), inset 0 0 15px rgba(99, 102, 241, 0.5); }

        50% { box-shadow: 0 0 25px rgba(56, 189, 248, 0.8), inset 0 0 25px rgba(16, 185, 129, 0.6); }

        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.5), inset 0 0 15px rgba(99, 102, 241, 0.5); }

    }

    .vfx-laser-btn {

        animation: laserPulse 2.5s infinite;

    }



    /* Quick Topic Chips */

    .vfx-chips-dock {

        display: flex;

        flex-wrap: wrap;

        gap: 6px;

        margin-bottom: 10px;

    }

    .vfx-quick-chip {

        font-size: 11px;

        font-weight: 600;

        padding: 5px 12px;

        border-radius: 20px;

        background: rgba(15, 23, 42, 0.85);

        border: 1px solid #1E2D4A;

        color: #94A3B8;

        cursor: pointer;

        transition: all 0.2s var(--spring-smooth);

        display: inline-flex;

        align-items: center;

        gap: 5px;

        white-space: nowrap;

    }

    .vfx-quick-chip:hover {

        background: rgba(56, 189, 248, 0.15);

        border-color: #38BDF8;

        color: #38BDF8;

        transform: translateY(-1px);

    }



    /* Live Media Provider Toggles */

    .vfx-provider-grid {

        display: grid;

        grid-template-columns: 1fr 1fr;

        gap: 8px;

    }

    .provider-toggle-card {

        display: flex;

        align-items: center;

        gap: 8px;

        font-size: 11px;

        font-weight: 700;

        color: #CBD5E1;

        cursor: pointer;

        background: rgba(15, 23, 42, 0.7);

        padding: 8px 10px;

        border-radius: 8px;

        border: 1px solid #1E2D4A;

        transition: all 0.2s ease;

        user-select: none;

    }

    .provider-toggle-card:hover {

        border-color: #38BDF8;

        color: #F8FAFC;

    }

    .provider-toggle-card input[type="checkbox"] {

        width: 15px;

        height: 15px;

        accent-color: #10B981;

        cursor: pointer;

    }



    /* 5-Step Pipeline Progress */

    .vfx-pipeline-tracker {

        display: flex;

        flex-direction: column;

        gap: 6px;

        background: rgba(11, 19, 43, 0.95);

        border: 1.5px solid rgba(56, 189, 248, 0.35);

        border-radius: 10px;

        padding: 12px 14px;

        margin-top: 10px;

    }

    .pipeline-step-row {

        display: flex;

        align-items: center;

        gap: 10px;

        font-size: 11.5px;

        color: #94A3B8;

        transition: color 0.2s ease;

    }

    .pipeline-step-row.active {

        color: #38BDF8;

        font-weight: 700;

    }

    .pipeline-step-row.completed {

        color: #10B981;

        font-weight: 600;

    }

    .pipeline-step-icon {

        width: 18px;

        height: 18px;

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 12px;

    }

    </style>



    <!-- Hidden Native Audio Player for Voiceover Sync -->

    <audio id="sqlVoiceAudio" preload="auto" crossorigin="anonymous" style="display:none;"></audio>



    <!-- Cleaned State Inputs -->

    <input type="hidden" id="sqlShortCreationMode" value="dynamic_ai" />

    <input type="hidden" id="selectedModernVideoModel" value="openai/gpt-oss-120b" />

    <input type="hidden" id="selectedVoiceActor" value="mr-IN-AarohiNeural" />



        <!-- 🎬 Anime.js Animation Engine & Motion Physics CDN with Offline Fallback -->

    <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>

    <script>

    if (typeof anime === 'undefined') {

        window.anime = function(opts) {

            if (opts && typeof opts.complete === 'function') setTimeout(opts.complete, opts.duration || 300);

            return { pause: function(){}, play: function(){}, restart: function(){} };

        };

        window.anime.stagger = function(val) { return function(el, i) { return i * (val || 100); }; };

    }

    </script>



    <div class="vfx-horizontal-scroll-container" id="vfxHorizontalScrollContainer">

    <div class="vfx-video-root" style="margin-bottom: 28px;">



        <!-- CLEAN MASTER STUDIO HEADER -->

        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; padding: 12px 18px; background: rgba(10, 15, 29, 0.95); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">

            <div style="display: flex; align-items: center; gap: 12px;">

                <div style="width: 42px; height: 42px; border-radius: 10px; background: linear-gradient(135deg, #0284C7, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);">

                    🎬

                </div>

                <div>

                    <h2 style="margin: 0; font-size: 17px; color: #38BDF8; font-weight: 900; letter-spacing: 0.5px;">

                        UNIVERSAL TECH AI VIDEO MAKER (9:16 SHORTS &amp; REELS)

                    </h2>

                    <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">

                        Prompt-led tech lessons • scene-specific 2D motion • neural voice

                    </div>

                </div>

            </div>

            <div style="display: flex; gap: 8px; align-items: center;">

                <span id="badgeActiveApis" class="kokonut-badge" style="color: #10B981; border-color: rgba(16,185,129,0.4); background: rgba(16,185,129,0.15);">

                    <span class="kokonut-pulse-dot"></span> AI STORY + NEURAL VOICE

                </span>

                <span class="kokonut-badge" style="color: #38BDF8; border-color: rgba(56,189,248,0.4); background: rgba(56,189,248,0.15);">

                    📱 9:16 VERTICAL FORMAT

                </span>

            </div>

        </div>



        <!-- =========================================================================

             MAIN STUDIO 3-COLUMN WORKSPACE

             ========================================================================= -->

        <div class="vfx-studio-grid" id="sqlStudioMainGrid">

            

            <!-- COLUMN 1: MASTER PROMPT & TECH SCENARIO CONSOLE -->

            <div class="vfx-glow-box" style="padding: 20px;">

                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">

                    <div style="display: flex; align-items: center; gap: 8px;">

                        <span style="font-size: 16px;">📝</span>

                        <h3 style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 800;">MASTER PROMPT &amp; TECH SCENARIO INPUT</h3>

                    </div>

                    <span style="font-size: 10.5px; color: #38BDF8; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 8px; border-radius: 6px; font-weight: 700;">

                        ✨ Live Multi-Stage Synth

                    </span>

                </div>







                <!-- Model routing: automatic fallback or selected model only -->

                <div style="background: rgba(11, 19, 43, 0.9); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">

                        <span style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">

                            🔄 Model Routing

                        </span>

                        <span id="activePatternBadge" style="font-size: 10px; font-weight: 800; color: #10B981; background: rgba(16,185,129,0.15); border: 1px solid #10B981; padding: 2px 8px; border-radius: 6px;">

                            AUTO FALLBACK

                        </span>

                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">

                        <button type="button" class="sql-pattern-btn active" id="btnPatternHybrid" onclick="setGenerationPattern('hybrid')" style="padding: 8px 10px; font-size: 11px; border-radius: 8px; border: 1px solid #10B981; background: rgba(16,185,129,0.2); color: #34D399; font-weight: 700; cursor: pointer; text-align: left; display: flex; flex-direction: column; gap: 2px;">

                            <span>✨ Automatic model fallback</span>

                            <span style="font-size: 9.5px; opacity: 0.8; font-weight: normal;">Try configured backups if the selected model fails</span>

                        </button>

                        <button type="button" class="sql-pattern-btn" id="btnPatternUnified" onclick="setGenerationPattern('unified')" style="padding: 8px 10px; font-size: 11px; border-radius: 8px; border: 1px solid #334155; background: rgba(15,23,42,0.8); color: #94A3B8; font-weight: 700; cursor: pointer; text-align: left; display: flex; flex-direction: column; gap: 2px;">

                            <span>🎯 Selected model only</span>

                            <span style="font-size: 9.5px; opacity: 0.8; font-weight: normal;">Do not try backup models</span>

                        </button>

                    </div>

                </div>



                <!-- 🧠 Verified Active LLM Script Engine Selector -->

                <div style="background: rgba(11, 19, 43, 0.9); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">

                        <span style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">

                            🧠 Script Reasoning Engine (LLM)

                        </span>

                        <span id="modelLatencyBadge" style="font-size: 10px; color: #38BDF8; font-family: monospace; font-weight: 700;">Technical Accuracy Engine</span>
                    </div>
                    <select id="selectModernVideoModelMaster" class="studio-input" onchange="onModernModelSelected(this.value)" style="width: 100%; background: #070B16; border: 1px solid #38BDF8; color: #F8FAFC; font-size: 12px; font-weight: 700; border-radius: 8px; padding: 8px; cursor: pointer;">
                        <option value="gemini-2.5-flash" selected>🌟 Google Gemini 2.5 Flash (Technical Accuracy Engine)</option>
                        <option value="wan_21">🏗️ Architecture storyboard (Groq model route)</option>
                        <option value="openai/gpt-oss-120b">⚡ Groq route: openai/gpt-oss-120b</option>
                        <option value="codestral-latest">🧪 Mistral: codestral-latest (Clean Code &amp; Architecture)</option>
                        <option value="command-r-plus-08-2024">🏢 Cohere: command-r-plus-08-2024 (Enterprise Structured)</option>
                        <option value="Meta-Llama-3.3-70B-Instruct">🚀 Meta-Llama-3.3-70B-Instruct</option>
                        <option value="deepseek-chat">🧬 DeepSeek: DeepSeek-V3 / R1 (Algorithmic Reasoning)</option>
                        <option value="openrouter/auto">🌐 OpenRouter: Multi-Model Gateway (Auto-Cascade)</option>
                    </select>
                    <div id="modelSpecsQuickPill" style="font-size: 10.5px; color: #38BDF8; margin-top: 6px; display: flex; align-items: center; gap: 6px;">
                        <span>● Active:</span> <b style="color: #38BDF8;" id="modelSpecsNameText">Google Gemini 2.5 Flash (Technical Accuracy Engine)</b>
                        <span style="color: #94A3B8;">• Multimodal &amp; Audio-Synced Architecture</span>
                    </div>

                </div>



                <!-- ⚡ 5 Quick Tech Topic Presets -->

                <div style="margin-bottom: 8px;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">

                        <span style="font-size: 11px; font-weight: 800; color: #94A3B8; text-transform: uppercase;">

                            ⚡ Quick Tech Topic Presets

                        </span>

                        <span style="font-size: 10px; color: #64748B;">1-Click Load</span>

                    </div>

                    <div class="vfx-chips-dock" id="quickTopicChipsContainer">

                        <button type="button" class="vfx-quick-chip" onclick="applyQuickPromptPreset('sql_window')">💻 SQL Window Functions</button>

                        <button type="button" class="vfx-quick-chip" onclick="applyQuickPromptPreset('python_asyncio')">🐍 Python Asyncio</button>

                        <button type="button" class="vfx-quick-chip" onclick="applyQuickPromptPreset('docker_k8s')">🐳 Docker vs K8s</button>

                        <button type="button" class="vfx-quick-chip" onclick="applyQuickPromptPreset('snowflake_medallion')">☁️ AWS Lakehouse</button>

                        <button type="button" class="vfx-quick-chip" onclick="applyQuickPromptPreset('rag_vector')">🤖 Agentic AI RAG</button>

                    </div>

                </div>



                <!-- Master Prompt Textarea -->

                <textarea class="studio-input" id="sqlShortQuestion" rows="5" placeholder="तुमचा मास्टर प्रॉम्प्ट (Master Prompt) इथे प्रविष्ट करा:

उदा. 'Explain DENSE_RANK() vs RANK() in SQL with live salary table' किंवा 'Microservices vs Monolith Architecture'



✨ तुमच्या topic नुसार 9:16 Shorts / Reels व्हिडिओ थेट कोड डायग्राम, B-Roll, व व्हॉईसओव्हरसह तयार होईल." style="width: 100%; margin-bottom: 14px; background: #070B16; border: 1.5px solid #1E2D4A; color: #F8FAFC; font-size: 12.5px; font-family: 'Fira Code', monospace; border-radius: 10px; padding: 12px; line-height: 1.6; resize: vertical; box-shadow: inset 0 2px 8px rgba(0,0,0,0.6);"></textarea>



                <!-- 🎙️ Regional Language & Neural Voice Actor Selection -->

                <div style="background: rgba(11, 19, 43, 0.85); border: 1px solid #1E2D4A; border-radius: 10px; padding: 12px 14px; margin-bottom: 14px;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">

                        <div style="display: flex; align-items: center; gap: 8px;">

                            <span style="font-size: 14px;">🎙️</span>

                            <span style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">Regional Language &amp; Voice Actor</span>

                        </div>

                        <!-- Live Reactive Waveform Visualizer -->

                        <div style="display: flex; align-items: center; gap: 4px; height: 16px;" id="audioWaveformVisualizer">

                            <span class="vfx-wave-bar"></span>

                            <span class="vfx-wave-bar"></span>

                            <span class="vfx-wave-bar"></span>

                            <span class="vfx-wave-bar"></span>

                            <span id="activeVoiceBadge" style="margin-left: 6px; font-size: 11px; color: #10B981; font-weight: 800;">मराठी शिक्षक</span>

                        </div>

                    </div>

                    

                    <!-- 3 Regional Language Buttons -->

                    <div style="display: flex; gap: 8px; margin-bottom: 10px;">

                        <button type="button" class="sql-lang-btn active" id="btnAudioMr" onclick="onWorkspaceLanguageSelect('mr')">

                            <span class="btn-check">✓</span> <span>🇮🇳 Marathi (मराठी)</span>

                        </button>

                        <button type="button" class="sql-lang-btn" id="btnAudioHi" onclick="onWorkspaceLanguageSelect('hi')">

                            <span class="btn-check">✓</span> <span>🇮🇳 Hindi (हिन्दी)</span>

                        </button>

                        <button type="button" class="sql-lang-btn" id="btnAudioEn" onclick="onWorkspaceLanguageSelect('en')">

                            <span class="btn-check">✓</span> <span>🇬🇧 English (English)</span>

                        </button>

                    </div>



                    <!-- Dynamic Voice Actor Dropdown -->

                    <div>

                        <label for="selectVoiceActor" style="font-size: 10px; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; display: block;">

                            Select Voice Actor:

                        </label>

                        <select id="selectVoiceActor" onchange="onVoiceActorSelected(this.value)" style="width: 100%; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; font-size: 11.5px; font-weight: 700; border-radius: 6px; padding: 7px 10px; outline: none; cursor: pointer;">

                            <option value="mr-IN-AarohiNeural" selected>Edge-TTS: mr-IN-AarohiNeural (Female - Clear Educator)</option>

                            <option value="mr-IN-ManoharNeural">Edge-TTS: mr-IN-ManoharNeural (Male - Formal Tech)</option>

                        </select>

                    </div>

                </div>



                <!-- 🌐 Dynamic Live Media Provider Toggles (5 Verified Active APIs) -->

                <div style="background: rgba(11, 19, 43, 0.85); border: 1px solid #1E2D4A; border-radius: 10px; padding: 12px 14px; margin-bottom: 16px;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">

                        <div style="display: flex; align-items: center; gap: 8px;">

                            <span style="font-size: 14px;">🌐</span>

                            <span style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">Optional Media &amp; Research APIs</span>

                        </div>

                        <span style="font-size: 10px; color: #FBBF24; font-weight: 700;">● Off by default · enable only when needed</span>

                    </div>

                    <div class="vfx-provider-grid" id="mediaProviderTogglesGrid">

                        <label class="provider-toggle-card">

                            <input type="checkbox" id="togglePixabay" />

                            <span>🎬 Pixabay 4K B-Roll</span>

                        </label>

                        <label class="provider-toggle-card">

                            <input type="checkbox" id="toggleUnsplash" />

                            <span>📸 Unsplash 4K Photos</span>

                        </label>

                        <label class="provider-toggle-card">

                            <input type="checkbox" id="toggleGiphy" />

                            <span>✨ Giphy Stickers</span>

                        </label>

                        <label class="provider-toggle-card">

                            <input type="checkbox" id="toggleFreesound" />

                            <span>🔊 Freesound SFX</span>

                        </label>

                        <label class="provider-toggle-card" style="grid-column: span 2;">

                            <input type="checkbox" id="toggleTavily" />

                            <span>📡 Tavily Real-Time News &amp; Facts</span>
                        </label>

                        <label class="provider-toggle-card" style="grid-column: span 2;">

                            <input type="checkbox" id="toggleCaptions" />

                            <span>🗣️ Deepgram word-level caption alignment (extra API call)</span>

                        </label>

                    </div>

                </div>



                <!-- Launch Action Button -->

                <button type="button" class="btn btn-primary vfx-laser-btn motion-spring-btn" id="btnGenerateSqlBlueprint" onclick="generateSqlShortBlueprint()" style="width: 100%; padding: 14px; font-weight: 900; font-size: 14px; letter-spacing: 0.5px; background: linear-gradient(135deg, #0284C7, #6366F1, #10B981); border: none; border-radius: 10px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 6px 25px rgba(2,132,199,0.55);">

                    <span style="font-size: 18px;">🚀</span>

                    <span>GENERATE 9:16 AI REEL (1-CLICK)</span>

                </button>

                <div id="sqlVideoGenerationStatus" role="status" aria-live="polite" style="margin-top: 8px; min-height: 18px; color: #7DD3FC; font-size: 11.5px; text-align: center; font-weight: 600;"></div>



                <!-- 📊 Live 5-Step Generation Pipeline Progress Indicator -->

                <div id="genPipelineSteps" class="vfx-pipeline-tracker" style="display: none;">

                    <div style="font-size: 11px; font-weight: 800; color: #38BDF8; margin-bottom: 4px; text-transform: uppercase; display: flex; justify-content: space-between;">

                        <span>🚀 Generation Pipeline Progress</span>

                        <span id="pipelineOverallPercent" style="font-family: monospace; color: #10B981;">0%</span>

                    </div>

                    <div class="pipeline-step-row" id="stepLlm">

                        <span class="pipeline-step-icon" id="stepIconLlm">⏳</span>

                        <span>1. Prompt → teacher-led storyboard (<span id="activeLlmLabel">Selected model</span>)</span>

                    </div>

                    <div class="pipeline-step-row" id="stepVoice">

                        <span class="pipeline-step-icon" id="stepIconVoice">⏳</span>

                        <span>2. Neural teacher voice (<span id="activeVoiceLabel">Edge-TTS</span>)</span>

                    </div>

                    <div class="pipeline-step-row" id="stepMedia">

                        <span class="pipeline-step-icon" id="stepIconMedia">⏳</span>

                        <span>3. Scene-specific 2D motion &amp; learner interaction</span>

                    </div>

                    <div class="pipeline-step-row" id="stepSfx">

                        <span class="pipeline-step-icon" id="stepIconSfx">⏳</span>

                        <span>4. Optional media APIs / precise captions (when enabled)</span>

                    </div>

                    <div class="pipeline-step-row" id="stepRender">

                        <span class="pipeline-step-icon" id="stepIconRender">⏳</span>

                        <span>5. Browser Canvas export (starts when you choose Export)</span>

                    </div>

                </div>

            </div>



            <!-- COLUMN 2: 9:16 TITANIUM SMARTPHONE PREVIEW -->

            <div style="display: flex; flex-direction: column; align-items: center;">

                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">

                    <span style="font-size: 12px; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;">📱 9:16 SMARTPHONE PREVIEW</span>

                    <span id="playerTimer" style="font-size: 11px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 0:00</span>

                </div>



                <!-- Futuristic Smartphone Bezel -->

                <div id="phoneBezel" style="width: 340px; height: 604px; aspect-ratio: 9 / 16; background: #000000; border: 4px solid #1E2D4A; border-radius: 38px; box-shadow: 0 25px 60px rgba(0,0,0,0.9), 0 0 30px rgba(56,189,248,0.25); position: relative; overflow: hidden; display: flex; flex-direction: column;">

                    

                    <!-- Dynamic Island Notch -->

                    <div style="height: 30px; width: 100%; display: flex; justify-content: center; align-items: center; position: absolute; top: 0; left: 0; z-index: 20; pointer-events: none;">

                        <div style="width: 90px; height: 18px; background: #0A0F1D; border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.3); display: flex; align-items: center; justify-content: space-between; padding: 0 8px;">

                            <div style="width: 6px; height: 6px; background: #10B981; border-radius: 50%; box-shadow: 0 0 6px #10B981;"></div>

                            <div style="font-size: 8px; color: #38BDF8; font-weight: 800; font-family: monospace;">NANOPRO</div>

                            <div style="width: 5px; height: 5px; background: #0284C7; border-radius: 50%;"></div>

                        </div>

                    </div>



                    <!-- Video Layer (Generative AI Video Stream: Kling, Luma, Runway, Seedance, Pollinations) -->

                    <video id="sqlShortRealVideo" playsinline loop muted autoplay style="display:none; position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; z-index:1; border-radius:34px;"></video>

                    

                    <!-- 60 FPS Canvas Viewport (1080x1920 logical, scaled via CSS, Overlay on Video) -->

                    <canvas id="sqlShortCanvas" width="1080" height="1920" style="position:relative; z-index:2; width: 100%; height: 100%; background: transparent; object-fit: contain;"></canvas>



                    <!-- Bottom Audio Wave Indicator -->

                    <div id="canvasAudioWave" style="position: absolute; bottom: 10px; left: 16px; right: 16px; height: 20px; display: flex; align-items: center; justify-content: space-between; z-index: 10; pointer-events: none;">

                        <div style="font-size: 10px; color: #38BDF8; font-weight: 800; text-shadow: 0 1px 4px #000;">@Code_With_Mangesh</div>

                        <div style="display: flex; gap: 3px; align-items: center;">

                            <span class="vfx-wave-bar"></span>

                            <span class="vfx-wave-bar"></span>

                            <span class="vfx-wave-bar"></span>

                            <span class="vfx-wave-bar"></span>

                        </div>

                    </div>

                </div>



                <!-- Player Transport Controls -->

                <div style="width: 100%; max-width: 340px; margin-top: 12px; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 10px; padding: 10px;">

                    <!-- Timeline Scrubber -->

                    <input type="range" id="sqlShortScrubber" min="0" max="0" value="0" step="0.1" oninput="seekSqlShortPlayer(this.value)" style="width: 100%; accent-color: #38BDF8; cursor: pointer; margin-bottom: 8px;" />

                    

                    <div style="display: flex; justify-content: space-between; align-items: center;">

                        <div style="display: flex; gap: 6px;">

                            <button type="button" class="btn btn-secondary" id="btnPlayPause" onclick="toggleSqlShortPlay()" style="padding: 4px 10px; font-size: 11.5px; font-weight: 700;">▶ Play</button>

                            <button type="button" class="btn btn-secondary" onclick="restartSqlShortPlay()" style="padding: 4px 10px; font-size: 11.5px; font-weight: 700;">🔄 Replay</button>

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



            <!-- COLUMN 3: 1-CLICK 9:16 VIDEO EXPORT STATION -->

            <div id="exportCardContainer" style="display: flex; flex-direction: column; gap: 16px;">

                

                <div class="vfx-glow-box" style="padding: 16px; border-color: rgba(16, 185, 129, 0.45); background: #0A0F1D;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">

                        <span style="font-size: 13px; font-weight: 900; color: #10B981; display: flex; align-items: center; gap: 6px;">

                            <span>🎬</span> <span>1-CLICK 9:16 VIDEO EXPORT</span>

                        </span>

                        <select id="sqlExportResolution" aria-label="Resolution" style="background:#0B1120;color:#F8FAFC;border:1px solid #334155;border-radius:6px;padding:4px 8px;font-size:11px;font-weight:700;">

                            <option value="1080">1080×1920 (Full HD)</option>

                            <option value="4k">2160×3840 (4K UHD)</option>

                        </select>

                    </div>



                    <!-- Direct Download Button Group -->

                    <div style="display: flex; flex-direction: column; gap: 8px;">

                        <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 13px; font-weight: 900; font-size: 13.5px; background: linear-gradient(135deg, #0284C7, #10B981); border: none; border-radius: 8px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 20px rgba(2,132,199,0.5);">

                            <span style="font-size: 18px;">📥</span>

                            <span id="exportBtnLabel">RENDER ON THIS DEVICE · 1080×1920</span>

                        </button>

                        <button type="button" class="btn btn-secondary" id="btnServerReelFast" onclick="renderServerReelFast()" style="width: 100%; padding: 9px; font-weight: 800; font-size: 11.5px; border: 1px solid #1E2D4A; border-radius: 8px; cursor: pointer; color: #FBBF24; display: flex; align-items: center; justify-content: center; gap: 8px; background: rgba(14,21,40,0.85);">

                            <span style="font-size: 15px;">⚠️</span>

                            <span>HEAVY SERVER RENDER · uses Render CPU/RAM</span>

                        </button>

                        <div style="font-size:10px;color:#94A3B8;line-height:1.5;">
                            Recommended: browser export renders on your laptop. Server rendering runs FFmpeg on the hosted instance and can slow NanoPro; 4K also uses substantially more device memory.
                        </div>



                        <div style="display: flex; gap: 6px;">

                            <button type="button" class="btn btn-secondary" onclick="downloadVoiceoverMp3()" id="btnDownloadAudioOnly" style="flex: 1; padding: 7px; font-size: 11px; font-weight: 700; border-color: #10B981; color: #10B981;">

                                🎵 Voice (.mp3)

                            </button>

                            <button type="button" class="btn btn-secondary" onclick="downloadCurrentFrameAsPng()" style="flex: 1; padding: 7px; font-size: 11px; font-weight: 700; border-color: #F59E0B; color: #F59E0B;">

                                📸 Frame (.png)

                            </button>

                        </div>

                    </div>



                    <!-- Progress Bar & Remaining Time Stats -->

                    <div id="exportProgressBarContainer" style="display:none; background: #0B1120; border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; margin-top: 14px;">

                        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #38BDF8; font-weight: 700; margin-bottom: 6px;">

                            <span id="exportStageDesc">⏳ 60 FPS Compositor रेंडर होत आहे...</span>

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



                    <!-- 🧬 AI ENGINES & COMPONENT ATTRIBUTION LEDGER (Post-Generation Report Card) -->

                    <div id="aiAttributionLedgerContainer" style="display:none; background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 70%), #0A0F1D; border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 12px; padding: 18px; margin-top: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.6);">

                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">

                            <div style="display: flex; align-items: center; gap: 10px;">

                                <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #0284C7, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 16px;">

                                    🧬

                                </div>

                                <div>

                                    <h4 style="margin: 0; font-size: 13px; color: #38BDF8; font-weight: 800; letter-spacing: 0.5px;">

                                        AUTHENTIC ASSET ATTRIBUTION LEDGER

                                    </h4>

                                    <div style="font-size: 10.5px; color: #94A3B8;">Verified Live Providers • Scene Composition Provenance</div>

                                </div>

                            </div>

                            <span id="ledgerPatternBadge" style="font-size: 10px; font-weight: 800; color: #10B981; background: rgba(16,185,129,0.15); border: 1px solid #10B981; padding: 3px 10px; border-radius: 6px;">

                                AUTHENTIC ASSETS VERIFIED

                            </span>

                        </div>



                        <!-- Scene Breakdown Grid -->

                        <div id="ledgerScenesList" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px;">

                            <!-- Dynamically injected scene attribution cards -->

                        </div>



                        <!-- Hardware & Voice Pipeline Summary -->

                        <div style="background: rgba(7, 11, 22, 0.8); border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">

                            <div>

                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🧠 Reasoning LLM</div>

                                <div id="ledgerScriptModel" style="font-size: 11.5px; color: #38BDF8; font-weight: 800; margin-top: 2px;">Groq openai/gpt-oss-120b</div>

                                <div id="ledgerScriptSpeed" style="font-size: 9.5px; color: #94A3B8;">Sub-second LPU Inference</div>

                            </div>

                            <div>

                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🎙️ Voiceover Actor</div>

                                <div id="ledgerVoiceName" style="font-size: 11.5px; color: #34D399; font-weight: 800; margin-top: 2px;">Edge Neural Marathi</div>

                                <div id="ledgerVoiceDuration" style="font-size: 9.5px; color: #94A3B8;">Neural Cloud Synthesis</div>

                            </div>

                            <div>

                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🎬 B-Roll &amp; Visuals</div>

                                <div id="ledgerBrollInfo" style="font-size: 11.5px; color: #FBBF24; font-weight: 800; margin-top: 2px;">Pixabay 4K / Unsplash</div>

                                <div id="ledgerVisualStats" style="font-size: 9.5px; color: #94A3B8;">Vertical 9:16 Dynamic Cropping</div>

                            </div>

                            <div>

                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">⏱️ Total Generation Time</div>

                                <div id="ledgerElapsedTime" style="font-size: 11.5px; color: #A78BFA; font-weight: 800; margin-top: 2px;">2.4s elapsed</div>

                                <div style="font-size: 9.5px; color: #94A3B8;">Real-Time End-to-End Pipeline</div>

                            </div>

                        </div>

                    </div>



                    <!-- Celebration & Video Ready Card -->

                    <div id="videoReadyCelebration" style="display:none; background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(6,182,212,0.25)); border: 2px solid #10B981; border-radius: 8px; padding: 14px; text-align: center; margin-top: 14px;">

                        <div style="font-size: 26px;">🎉 🏆 🎬</div>

                        <div style="font-size: 14px; font-weight: 800; color: #10B981; margin-top: 4px;">व्हिडिओ यशस्वीरित्या तयार झाला!</div>

                        <div id="videoReadyQuality" style="font-size: 11px; color: #CBD5E1; margin: 4px 0 10px;">Watermark-free • 9:16 • 1080×1920 60FPS</div>

                        <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">

                            <a id="btnDownloadAgain" href="#" class="btn btn-primary" style="font-size: 11px; padding: 7px 14px; background: linear-gradient(135deg, #10B981, #06B6D4); color: #000; font-weight: 800; border-radius: 6px; text-decoration: none;">

                                <span>📥 पुन्हा सेव्ह करा</span>

                            </a>

                            <button type="button" class="btn btn-secondary" onclick="restartSqlShortPlay()" style="font-size: 11px; padding: 7px 14px; border-color: #38BDF8; color: #38BDF8; font-weight: 700;">

                                <span>▶ फोनवर पाहा</span>

                            </button>

                        </div>

                    </div>

                </div>



            </div>



        </div>



    </div>

    </div> <!-- Close vfxHorizontalScrollContainer -->



    <!-- Interactive Helper Functions for Prompt Chips and Model Docks -->

    <script>

    // 1. Quick Tech Topic Presets

    function applyQuickPromptPreset(type) {

        const input = document.getElementById('sqlShortQuestion');

        if (!input) return;

        const presets = {

            sql_window: 'Explain DENSE_RANK() vs RANK() in SQL with live employee salaries table and duplicate rank resolution.',

            python_asyncio: 'Explain Python Asyncio Event Loop, async/await tasks, and high-concurrency non-blocking API calls.',

            snowflake_medallion: 'Design Enterprise Lakehouse Medallion Architecture: Raw S3 ➔ Bronze L0 ➔ Silver L1 ➔ Gold L2 DuckDB Marts.',

            docker_k8s: 'Explain Docker Container vs Virtual Machine with Kubernetes Pod deployment and Zero-Downtime rollouts.',

            rag_vector: 'Explain Agentic AI RAG with Vector Embeddings, Hybrid Semantic Search, and LLM Context Grounding.'

        };

        input.value = presets[type] || presets.sql_window;

        input.focus();

    }



    // 2. Language & Dynamic Voice Actor Sync

    const WORKSPACE_VOICE_MAP = {

        mr: [

            { value: 'mr-IN-AarohiNeural', label: 'Edge-TTS: mr-IN-AarohiNeural (Female - Clear Educator)', default: true },

            { value: 'mr-IN-ManoharNeural', label: 'Edge-TTS: mr-IN-ManoharNeural (Male - Formal Tech)' }

        ],

        hi: [

            { value: 'hi-IN-MadhurNeural', label: 'Edge-TTS: hi-IN-MadhurNeural (Male - Professional Teacher)', default: true },

            { value: 'hi-IN-SwaraNeural', label: 'Edge-TTS: hi-IN-SwaraNeural (Female - Conversational)' }

        ],

        en: [

            { value: 'en-US-JennyNeural', label: 'Edge-TTS: en-US-JennyNeural (Female - Studio Tech)', default: true },

            { value: 'en-US-GuyNeural', label: 'Edge-TTS: en-US-GuyNeural (Male - Tech Educator)' },

            { value: 'aura-asteria-en', label: 'Deepgram Aura: aura-asteria-en (Female - Human Conversational)' },

            { value: 'aura-luna-en', label: 'Deepgram Aura: aura-luna-en (Female - Natural Calm)' }

        ]

    };



    function updateVoiceActorDropdown(lang) {

        const select = document.getElementById('selectVoiceActor');

        if (!select) return;

        const actors = WORKSPACE_VOICE_MAP[lang] || WORKSPACE_VOICE_MAP.mr;

        select.innerHTML = '';

        actors.forEach(actor => {

            const opt = document.createElement('option');

            opt.value = actor.value;

            opt.textContent = actor.label;

            if (actor.default) opt.selected = true;

            select.appendChild(opt);

        });

        const hiddenVoice = document.getElementById('selectedVoiceActor');

        if (hiddenVoice && select.value) hiddenVoice.value = select.value;

    }



    function onWorkspaceLanguageSelect(lang) {

        if (typeof setSqlAudioLang === 'function') {

            setSqlAudioLang(lang);

        }

        updateVoiceActorDropdown(lang);

    }



    function onVoiceActorSelected(val) {

        const hiddenVoice = document.getElementById('selectedVoiceActor');

        if (hiddenVoice) hiddenVoice.value = val;

    }



    // 3. Provider Toggles Serialization

    function getSelectedMediaProviders() {

        return {

            pixabay: document.getElementById('togglePixabay')?.checked ?? true,

            unsplash: document.getElementById('toggleUnsplash')?.checked ?? true,

            giphy: document.getElementById('toggleGiphy')?.checked ?? true,

            freesound: document.getElementById('toggleFreesound')?.checked ?? true,

            tavily: document.getElementById('toggleTavily')?.checked ?? true

        };

    }



    // 4. Reactive Waveform State Helper

    function setAudioWaveformPlaying(isPlaying) {

        const bars = document.querySelectorAll('.vfx-wave-bar');

        bars.forEach(b => {

            if (isPlaying) b.classList.add('playing');

            else b.classList.remove('playing');

        });

        const visualizer = document.getElementById('audioWaveformVisualizer');

        if (visualizer) {

            if (isPlaying) visualizer.classList.add('is-playing');

            else visualizer.classList.remove('is-playing');

        }

    }

    </script>

    """
