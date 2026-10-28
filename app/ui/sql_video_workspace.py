# -*- coding: utf-8 -*-
"""
Mangesh Nano Pro AI Studio - 2026 VFX-Style Universal Tech AI Video Maker
State-of-the-art 9:16 Shorts & Reels Studio:
- 4-Tier Multi-Stage API Docks: Prompt-to-Voice • Voice-to-Video Lip-Sync • Prompt-to-Video B-Roll • Unified Aggregators
- 100% Prompt-Driven, Live Dynamic APIs, Titanium Smartphone Preview, and VFX 1-Click Export!
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
        min-width: 1360px; /* guarantees full 3-column deck with zero clipping */
        width: 1360px;
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

    /* Audio wave animation */
    @keyframes wavePulse {
        0%, 100% { height: 4px; }
        50% { height: 16px; }
    }
    .vfx-wave-bar {
        width: 3px;
        background: #10B981;
        border-radius: 2px;
        animation: wavePulse 1.2s ease-in-out infinite;
    }
    .vfx-wave-bar:nth-child(2) { animation-delay: 0.2s; background: #38BDF8; }
    .vfx-wave-bar:nth-child(3) { animation-delay: 0.4s; background: #8B5CF6; }
    .vfx-wave-bar:nth-child(4) { animation-delay: 0.6s; background: #EC4899; }

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
    </style>

    <!-- Hidden Native Audio Player for Voiceover Sync -->
    <audio id="sqlVoiceAudio" preload="auto" crossorigin="anonymous" style="display:none;"></audio>

    <!-- Hidden inputs for legacy JS state compatibility -->
    <input type="hidden" id="sqlShortCreationMode" value="dynamic_ai" />
    <input type="hidden" id="sqlCinematicBgSelect" value="cyber_matrix" />
    <input type="hidden" id="directVideoEngineSelect" value="pollinations_ultra_api" />
    <input type="hidden" id="selectedModernVideoModel" value="seedance_25" />

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

        <!-- =========================================================================
             VFX STUDIO TOP HUD BANNER
             ========================================================================= -->
        <div class="vfx-glow-box" style="padding: 16px 22px; margin-bottom: 18px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.15), transparent 70%), #0A0F1D;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #0284C7, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.5);">
                    🎬
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 18px; color: #38BDF8; font-weight: 900; letter-spacing: 0.5px; text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);">
                        UNIVERSAL TECH AI VIDEO MAKER (9:16 SHORTS &amp; REELS)
                    </h2>
                    <div style="font-size: 11.5px; color: #94A3B8; margin-top: 3px; display: flex; align-items: center; gap: 8px;">
                        <span>VFX-Grade Multi-Stage Pipeline:</span>
                        <b style="color: #F8FAFC;">Prompt ➔ Voice ➔ Lip-Sync Avatar ➔ 4K B-Roll ➔ 1-Click Export</b>
                    </div>
                </div>
            </div>

            <!-- Kokonut UI & Blacklist UI Telemetry Badges -->
            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                <span class="kokonut-badge">
                    <span class="kokonut-pulse-dot"></span>
                    <span style="color: #10B981;">AUTO-PILOT ACTIVE</span>
                </span>
                <span class="kokonut-badge" style="border-color: rgba(56,189,248,0.4);">
                    <span style="color: #38BDF8; font-family: monospace;">⚡ 49+ APIS LIVE</span>
                </span>
                <span class="kokonut-badge" style="border-color: rgba(168,85,247,0.4);">
                    <span style="color: #C084FC;">✨ ANIME.JS &amp; MOTION.DEV</span>
                </span>
                <span class="kokonut-badge" style="border-color: rgba(245,158,11,0.4);">
                    <span style="color: #FBBF24;">🛡️ ZERO WATERMARK • 60 FPS</span>
                </span>
            </div>
        </div>

        <!-- =========================================================================
             🎯 NANOPRO MANAGER & AUTONOMOUS AI VIDEO DIRECTOR (100% AUTO-PILOT)
             Executive Manager Role: Does NOT manually render video; instead commissions
             and orchestrates external APIs, Internet Trends, and Prompts on Auto-Pilot!
             ========================================================================= -->
        <div class="kokonut-card" style="padding: 18px 22px; margin-bottom: 20px; border-color: rgba(16, 185, 129, 0.45); background: linear-gradient(135deg, rgba(6, 78, 59, 0.15), rgba(10, 16, 32, 0.95));">
            
            <!-- Director Header Strip -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 46px; height: 46px; border-radius: 12px; background: linear-gradient(135deg, #10B981, #06B6D4); display: flex; align-items: center; justify-content: center; font-size: 24px; color: #000; font-weight: 900; box-shadow: 0 0 20px rgba(16,185,129,0.5);">
                        🎯
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                            <h3 style="margin: 0; font-size: 16px; color: #34D399; font-weight: 900; letter-spacing: 0.5px;">
                                NanoPro Manager &amp; Autonomous AI Video Director
                            </h3>
                            <span class="kokonut-badge" style="background: rgba(16,185,129,0.2); border-color: #10B981; color: #34D399;">
                                <span class="kokonut-pulse-dot"></span>
                                AUTO-PILOT EXECUTIVE ACTIVE
                            </span>
                            <span class="blacklist-tag" style="background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 2px 8px; border-radius: 4px;">
                                [API_ORCHESTRATOR_V3]
                            </span>
                        </div>
                        <div style="font-size: 11.5px; color: #94A3B8; margin-top: 4px; line-height: 1.5;">
                            <strong style="color: #F8FAFC;">💡 Auto-Pilot Protocol:</strong> NanoPro Manager स्वतः व्हिडिओ मॅन्युअली बनवत नाही — तर तो <span style="color: #38BDF8; font-weight: 700;">इंटरनेट ट्रेंड्स</span>, <span style="color: #FBBF24; font-weight: 700;">प्रॉम्प्ट इंटेलिजन्स</span> आणि जगभरातील <span style="color: #34D399; font-weight: 700;">४९+ Generative APIs</span> (TTS, Lip-Sync Avatars, 4K Diffusion, SFX) चा वापर करून ऑटो-पायलटवर व्हिडिओ <b>कमिशन (Commission)</b> आणि <b>सिंक्रोनाइझ (Assemble)</b> करतो!
                        </div>
                    </div>
                </div>

                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 11px; color: #64748B;">Executive Mode:</span>
                    <span style="font-size: 11px; color: #FBBF24; font-weight: 800; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.4); padding: 4px 12px; border-radius: 8px;">
                        ⚡ 100% Autonomous (Prompt &rarr; Internet &rarr; APIs)
                    </span>
                </div>
            </div>

            <!-- 5 Live Auto-Pilot Commissioning Cards (Kokonut UI & Blacklist HUD) -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 14px;">
                
                <!-- 1. Internet & Viral Trend Scout -->
                <div class="kokonut-card kokonut-director-card" style="padding: 10px 14px; background: rgba(15,23,42,0.85); border-color: #1E2D4A;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="blacklist-tag">[INTERNET_TRENDS]</span>
                        <span style="font-size: 12px;">🌐</span>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 4px;">Viral Trend Scout</div>
                    <div id="aiDirectorTrendDecision" style="font-size: 12px; font-weight: 800; color: #FBBF24; margin-top: 2px;">
                        YouTube &amp; Insta Reels 2026 Pacing
                    </div>
                    <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">3s Curiosity Hook &bull; High Retention</div>
                </div>

                <!-- 2. Auto Voice Engine API -->
                <div class="kokonut-card kokonut-director-card" style="padding: 10px 14px; background: rgba(15,23,42,0.85); border-color: #1E2D4A;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="blacklist-tag">[TTS_API]</span>
                        <span style="font-size: 12px;">🎙️</span>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 4px;">Auto Voice Commissioned</div>
                    <div id="aiDirectorVoiceDecision" style="font-size: 12px; font-weight: 800; color: #34D399; margin-top: 2px;">
                        Edge Neural (Marathi/Hindi) / Kokoro
                    </div>
                    <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">Native Human Cadence &bull; Zero Delay</div>
                </div>

                <!-- 3. Pure Tech 3D Architecture (STRICTLY NO HUMAN FACES) -->
                <div class="kokonut-card kokonut-director-card" style="padding: 10px 14px; background: rgba(15,23,42,0.85); border-color: #1E2D4A;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="blacklist-tag">[PURE_TECH_ENGINE]</span>
                        <span style="font-size: 12px;">🛡️</span>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 4px;">Pure Tech Visuals</div>
                    <div id="aiDirectorAvatarDecision" style="font-size: 12px; font-weight: 800; color: #38BDF8; margin-top: 2px;">
                        3D Isometric Systems &bull; No Human Faces
                    </div>
                    <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">Code &bull; Conduits &bull; Zero Avatars/Faces</div>
                </div>

                <!-- 4. Auto 3D & 4K B-Roll Scene API -->
                <div class="kokonut-card kokonut-director-card" style="padding: 10px 14px; background: rgba(15,23,42,0.85); border-color: #1E2D4A;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="blacklist-tag">[DIFFUSION_API]</span>
                        <span style="font-size: 12px;">🎬</span>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 4px;">Auto 4K B-Roll Scene</div>
                    <div id="aiDirectorBrollDecision" style="font-size: 12px; font-weight: 800; color: #C084FC; margin-top: 2px;">
                        ByteDance Seedance 2.5 + Kling 3.0
                    </div>
                    <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">4K Camera Swoop &bull; Data Centers</div>
                </div>

                <!-- 5. VFX, 3D Engine & Anime.js / Motion.dev -->
                <div class="kokonut-card kokonut-director-card" style="padding: 10px 14px; background: rgba(15,23,42,0.85); border-color: #1E2D4A;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="blacklist-tag">[ANIMEJS_MOTION]</span>
                        <span style="font-size: 12px;">✨</span>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 4px;">VFX &amp; Physics Engine</div>
                    <div id="aiDirectorGatewayDecision" style="font-size: 12px; font-weight: 800; color: #F472B6; margin-top: 2px;">
                        Isometric 3D + Kinetic Typography
                    </div>
                    <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">Spring Physics &bull; Web Audio SFX Cues</div>
                </div>
            </div>

            <!-- 👥 Autonomous AI Video Task Force (Group T Agents 306-320 Active) -->
            <div style="padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 6px;">
                    <span style="font-size: 11px; font-weight: 800; color: #38BDF8; display: flex; align-items: center; gap: 6px;">
                        <span>👥</span> Dedicated Autonomous AI Video Task Force (15 Active Specialists):
                    </span>
                    <span style="font-size: 10px; color: #10B981; background: rgba(16,185,129,0.15); border: 1px solid #10B981; padding: 1px 8px; border-radius: 10px; font-weight: 700;">
                        ● Full Creative Agency Access Granted
                    </span>
                </div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <span style="font-size: 10px; background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 3px 8px; border-radius: 6px; color: #FBBF24;">
                        🔥 Agent-306: Viral Shorts Trend Scout
                    </span>
                    <span style="font-size: 10px; background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 3px 8px; border-radius: 6px; color: #38BDF8;">
                        🎨 Agent-307: 3D Isometric &amp; VFX Architect
                    </span>
                    <span style="font-size: 10px; background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 3px 8px; border-radius: 6px; color: #34D399;">
                        🎙️ Agent-308: Voice &amp; Web Audio SFX Director
                    </span>
                    <span style="font-size: 10px; background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 3px 8px; border-radius: 6px; color: #C084FC;">
                        🧠 Agent-309: Continuous Global Video API Learner
                    </span>
                    <span style="font-size: 10px; background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 3px 8px; border-radius: 6px; color: #F472B6;">
                        📊 Agent-310: Dynamic Metric &amp; Chart Visualizer
                    </span>
                    <span style="font-size: 10px; background: rgba(15,23,42,0.9); border: 1px solid #334155; padding: 3px 8px; border-radius: 6px; color: #A78BFA;">
                        ✍️ Agent-311: Kinetic Typography Stylist
                    </span>
                </div>
            </div>

            <!-- Optional Collapsible Manual Override (Discreetly tucked away so user doesn't have to fiddle) -->
            <details style="margin-top: 10px; font-size: 11px; color: #64748B;">
                <summary style="cursor: pointer; color: #38BDF8; font-weight: 700;">
                    ⚙️ Advanced API Overrides (Optional / Manual Tuning)
                </summary>
                <div class="vfx-dock-grid" style="margin-top: 10px;">
                    <div class="vfx-dock-card">
                        <label style="font-size: 10px; color: #94A3B8;">Voice Engine:</label>
                        <select id="selectVoiceEngine" class="vfx-dock-select" onchange="onVoiceEngineChange(this.value)">
                            <option value="auto" selected>✨ Auto-Pilot Autonomous Selection</option>
                            <option value="kokoro_free">🟢 Kokoro-82M (100% Free CPU • Zero Cost)</option>
                            <option value="edge_tts_free">⚡ Microsoft Edge Neural (Free Native Mr/Hi/En)</option>
                            <option value="elevenlabs_v3">🔥 ElevenLabs v3 Multilingual Studio</option>
                            <option value="cartesia_sonic">⚡ Cartesia Sonic (40ms Low Latency)</option>
                            <option value="browser_speech_free">🎙️ In-Browser Web Speech (0ms Offline)</option>
                        </select>
                        <span id="voiceLatencyBadge" style="display:none;"></span>
                    </div>

                    <div class="vfx-dock-card">
                        <label style="font-size: 10px; color: #94A3B8;">Avatar Engine:</label>
                        <select id="selectAvatarEngine" class="vfx-dock-select" onchange="onAvatarEngineChange(this.value)">
                            <option value="auto" selected>✨ Auto-Pilot Autonomous Selection</option>
                            <option value="hedra_char3">🔥 Hedra Character-3 API (#1 Trending Dev)</option>
                            <option value="liveportrait_free">🟢 LivePortrait (100% Free Landmark Sync)</option>
                            <option value="client_cyber_canvas">🛡️ Client-Side 3D Cyber Presenter (Zero-Drop)</option>
                        </select>
                        <span id="avatarFpsBadge" style="display:none;"></span>
                    </div>

                    <div class="vfx-dock-card">
                        <label style="font-size: 10px; color: #94A3B8;">B-Roll Scene Engine:</label>
                        <select id="selectBrollEngine" class="vfx-dock-select" onchange="onBrollEngineChange(this.value)">
                            <option value="auto" selected>✨ Auto-Pilot Autonomous Selection</option>
                            <option value="seedance_25">🏆 ByteDance Seedance 2.5 (Leaderboard #1)</option>
                            <option value="kling_30">🔥 Kuaishou Kling AI 3.0 Pro (Viral Physics)</option>
                            <option value="veo_31">⚡ Google Veo 3.1 (Gemini 4K Cinematic Audio)</option>
                            <option value="procedural_3d_webgl">🛡️ Built-in 60 FPS 3D WebGL (Zero-Lag)</option>
                        </select>
                        <span id="brollResBadge" style="display:none;"></span>
                    </div>

                    <div class="vfx-dock-card">
                        <label style="font-size: 10px; color: #94A3B8;">Failover Router:</label>
                        <select id="selectAggregatorEngine" class="vfx-dock-select" onchange="onAggregatorEngineChange(this.value)">
                            <option value="nanopro_auto_cascade" selected>🛡️ NanoPro Autonomous Zero-Stop Cascade</option>
                            <option value="fal_ai_queue">⚡ fal.ai Serverless Unified Queue</option>
                        </select>
                        <span id="gatewayStatusBadge" style="display:none;"></span>
                    </div>
                </div>
            </details>
        </div>

                <!-- ↔️ Complete Horizontal Scroll Navigation Bar (Fast Jump) -->
        <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(10,16,32,0.92); border: 1.5px solid rgba(56,189,248,0.4); border-radius: 12px; padding: 10px 18px; margin-bottom: 16px; backdrop-filter: blur(14px); box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 16px;">↔️</span>
                <span style="font-size: 12px; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;">
                    HORIZONTAL SCROLL DECK ACTIVE (1360px FULL STUDIO)
                </span>
                <span style="font-size: 11px; color: #94A3B8;">&bull; Use scrollbar below or click fast jump buttons:</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <button type="button" class="btn btn-secondary motion-spring-btn" onclick="scrollVfxStudio('left')" style="padding: 5px 12px; font-size: 11px; border-color: #38BDF8; color: #38BDF8; font-weight: 700;">
                    ⬅️ 1. Master Prompt Console
                </button>
                <button type="button" class="btn btn-secondary motion-spring-btn" onclick="scrollVfxStudio('center')" style="padding: 5px 12px; font-size: 11px; border-color: #10B981; color: #10B981; font-weight: 700;">
                    📱 2. 9:16 Smartphone Preview
                </button>
                <button type="button" class="btn btn-secondary motion-spring-btn" onclick="scrollVfxStudio('right')" style="padding: 5px 12px; font-size: 11px; border-color: #C084FC; color: #C084FC; font-weight: 700;">
                    ➡️ 3. 1-Click Video Export
                </button>
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

                <!-- 1-Click Prompt Preset Chips -->
                <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
                    <span class="vfx-quick-chip" onclick="applyQuickPromptPreset('sql_window')">🔥 SQL Window Ranking</span>
                    <span class="vfx-quick-chip" onclick="applyQuickPromptPreset('python_asyncio')">⚡ Python Asyncio</span>
                    <span class="vfx-quick-chip" onclick="applyQuickPromptPreset('snowflake_medallion')">☁️ Snowflake Medallion</span>
                    <span class="vfx-quick-chip" onclick="applyQuickPromptPreset('docker_k8s')">🐳 Docker &amp; K8s</span>
                    <span class="vfx-quick-chip" onclick="applyQuickPromptPreset('rag_vector')">🤖 Agentic RAG Vector</span>
                </div>

                <!-- 🔄 Generation Strategy Pattern Selector (Unified vs Multi-Model Mix) -->
                <div style="background: rgba(11, 19, 43, 0.9); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">
                            🔄 Generation Pattern Strategy
                        </span>
                        <span id="activePatternBadge" style="font-size: 10px; font-weight: 800; color: #10B981; background: rgba(16,185,129,0.15); border: 1px solid #10B981; padding: 2px 8px; border-radius: 6px;">
                            MULTI-MODEL HYBRID
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                        <button type="button" class="sql-pattern-btn active" id="btnPatternHybrid" onclick="setGenerationPattern('hybrid')" style="padding: 8px 10px; font-size: 11px; border-radius: 8px; border: 1px solid #10B981; background: rgba(16,185,129,0.2); color: #34D399; font-weight: 700; cursor: pointer; text-align: left; display: flex; flex-direction: column; gap: 2px;">
                            <span>✨ Multi-Model Hybrid</span>
                            <span style="font-size: 9.5px; opacity: 0.8; font-weight: normal;">Best-of-Breed mixture across scenes</span>
                        </button>
                        <button type="button" class="sql-pattern-btn" id="btnPatternUnified" onclick="setGenerationPattern('unified')" style="padding: 8px 10px; font-size: 11px; border-radius: 8px; border: 1px solid #334155; background: rgba(15,23,42,0.8); color: #94A3B8; font-weight: 700; cursor: pointer; text-align: left; display: flex; flex-direction: column; gap: 2px;">
                            <span>🎯 Unified (Same Engine)</span>
                            <span style="font-size: 9.5px; opacity: 0.8; font-weight: normal;">Single model for entire 60s video</span>
                        </button>
                    </div>
                </div>

                <!-- ⚡ 50+ AI Video Engine Selector Dock -->
                <div style="background: rgba(11, 19, 43, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.35); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #C084FC; text-transform: uppercase;">
                            ⚡ 50+ AI Video Engine Master Dock
                        </span>
                        <span style="font-size: 10px; color: #FBBF24; font-family: monospace;">40 Video + 17 Audio/VFX</span>
                    </div>
                    <select id="selectModernVideoModelMaster" class="studio-input" onchange="onModernModelSelected(this.value)" style="width: 100%; background: #070B16; border: 1px solid #334155; color: #F8FAFC; font-size: 12px; font-weight: 700; border-radius: 8px; padding: 8px; cursor: pointer;">
                        <optgroup label="🟢 100% Free Open-Source (Local Laptop GPU Acceleration)">
                            <option value="wan_21" selected>🟢 Wan 2.1 (Alibaba Open-Source) • 1080p Flagship</option>
                            <option value="ltx_video">⚡ Lightricks LTX-Video • Real-Time GPU Speed</option>
                            <option value="hunyuan_video">🎬 Tencent HunyuanVideo 13B • Cinematic 4K</option>
                            <option value="cogvideox">🧪 CogVideoX (THUDM) • 3D Animation & Shorts</option>
                            <option value="genmo_mochi1">✨ Genmo Mochi 1 • Fluid High-Motion</option>
                            <option value="pollinations_free_2026">🌐 Pollinations Free Video • Unlimited Zero-Card</option>
                            <option value="procedural_3d_webgl">💻 Built-in 60 FPS 3D WebGL / GPU Procedural Engine</option>
                        </optgroup>
                        <optgroup label="🔵 Google Gemini Pro & Veo 3.1 (Direct Integration)">
                            <option value="veo_31">🔵 Google Veo 3.1 & Gemini Pro 4K Engine</option>
                        </optgroup>
                        <optgroup label="🟣 Cinematic Generative AI (Cloud APIs & Fast Queues)">
                            <option value="kling_30">🔥 Kuaishou Kling AI 3.0 Pro • Viral Physics</option>
                            <option value="hailuo_h3">🌪️ MiniMax Hailuo H3 / Video-01</option>
                            <option value="runway_gen45">🎥 Runway Gen-4.5 / Gen-4 Turbo</option>
                            <option value="luma_ray2">💫 Luma Ray-2 Dream Machine</option>
                            <option value="pika_20">🎨 Pika 2.0 (Pikaffects & SFX)</option>
                            <option value="pixverse_v6">🌟 PixVerse v6 • 4K Character Consistency</option>
                            <option value="vidu_ai">⚡ Vidu AI 1.5 • 30s Ultra-Fast</option>
                            <option value="seaart_ai">🎨 SeaArt AI Creative Video</option>
                            <option value="haiper_ai">🖌️ Haiper AI 2.0 • Video Repaint</option>
                            <option value="leonardo_motion">📸 Leonardo AI Motion Studio</option>
                            <option value="kaiber_ai">🎵 Kaiber AI Reactive Video</option>
                            <option value="firefly_video">🛡️ Adobe Firefly Video • Commercial Safe</option>
                            <option value="krea_ai">⚡ Krea AI Real-Time Upscale</option>
                            <option value="morph_studio">🎞️ Morph Studio Storyboard</option>
                            <option value="higgsfield_ai">🏢 Higgsfield AI 35+ Production Hub</option>
                            <option value="dreamina_capcut">🎬 Dreamina / CapCut AI</option>
                            <option value="pollo_ai">🐣 Pollo AI Multi-Model</option>
                            <option value="clipfly_ai">✂️ Clipfly AI Video + Editor</option>
                            <option value="fal_ai_queue">⚡ fal.ai Serverless Unified Queue</option>
                            <option value="akool_video">🎭 AKOOL Studio Transitions</option>
                            <option value="openai_sora">🚀 OpenAI Sora Turbo</option>
                            <option value="seedance_25">🛸 ByteDance Seedance 2.5</option>
                        </optgroup>
                        <optgroup label="🟠 Social Media & Script-to-Video (Reels / Shorts Automation)">
                            <option value="invideo_ai">📱 InVideo AI Full Reels Automation</option>
                            <option value="fliki_ai">🇮🇳 Fliki AI • Regional Marathi/Hindi Voiceover</option>
                            <option value="capcut_ai">✂️ CapCut Web/App Auto AI Captions</option>
                            <option value="veed_io">💬 VEED.io Smart Karaoke Subtitles</option>
                            <option value="pictory_ai">🎙️ Pictory AI Long-to-Short</option>
                            <option value="lumen5_ai">📄 Lumen5 Article-to-Video</option>
                            <option value="steve_ai">🧸 Steve AI 2D/3D Explainers</option>
                            <option value="canva_video">🎨 Canva AI Video Magic</option>
                            <option value="google_vids">📊 Google Vids Storyboard</option>
                            <option value="creatify_ai">📢 Creatify AI Viral Promo</option>
                        </optgroup>
                    </select>
                    <div id="modelSpecsQuickPill" style="font-size: 10.5px; color: #10B981; margin-top: 6px; display: flex; align-items: center; gap: 6px;">
                        <span>● Active:</span> <b style="color: #F8FAFC;" id="modelSpecsNameText">Wan 2.1 (Alibaba Open-Source)</b>
                        <span style="color: #64748B;">• Local Laptop GPU Ready (100% Free)</span>
                    </div>
                </div>

                <!-- Master Prompt Textarea -->
                <textarea class="studio-input" id="sqlShortQuestion" rows="8" placeholder="तुमचा कोणताही मास्टर प्रॉम्प्ट (Master Prompt) इथे टाईप करा:

१. थेट प्रश्न (Question): 'Explain Dense_Rank vs Rank in SQL' किंवा 'Kafka vs RabbitMQ'
२. व्हॉईस स्क्रिप्ट (TTS Script): 'नमस्कार मित्रांनो, आज आपण पाहणार आहोत की...'
३. आर्किटेक्चर (Topic): 'Cloud Data Lakehouse Medallion Architecture with DuckDB'

✨ तुमच्या prompt नुसार निवडलेले Voice, Avatar आणि 4K B-Roll APIs थेट कॉल होऊन 9:16 Shorts व्हिडिओ तयार होईल." style="width: 100%; margin-bottom: 14px; background: #070B16; border: 1.5px solid #1E2D4A; color: #F8FAFC; font-size: 12.5px; font-family: 'Fira Code', monospace; border-radius: 10px; padding: 12px; line-height: 1.6; resize: vertical; box-shadow: inset 0 2px 8px rgba(0,0,0,0.6);"></textarea>

                <!-- Natural Teacher Voice Language Selection with Audio Wave -->
                <div style="background: rgba(11, 19, 43, 0.8); border: 1px solid #1E2D4A; border-radius: 10px; padding: 12px 14px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 14px;">🎙️</span>
                            <span style="font-size: 11px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">Natural Teacher Voice Language</span>
                        </div>
                        <!-- Live Waveform Visualizer -->
                        <div style="display: flex; align-items: center; gap: 4px; height: 16px;">
                            <span class="vfx-wave-bar"></span>
                            <span class="vfx-wave-bar"></span>
                            <span class="vfx-wave-bar"></span>
                            <span class="vfx-wave-bar"></span>
                            <span id="activeVoiceBadge" style="margin-left: 6px; font-size: 11px; color: #10B981; font-weight: 800;">मराठी शिक्षक</span>
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

                <!-- Launch Action Button with Motion.dev & Kokonut UI Shimmer -->
                <button type="button" class="btn btn-primary vfx-laser-btn motion-spring-btn" id="btnGenerateSqlBlueprint" onclick="generateSqlShortBlueprint()" style="width: 100%; padding: 16px; font-weight: 900; font-size: 14px; letter-spacing: 0.5px; background: linear-gradient(135deg, #0284C7, #6366F1, #10B981); border: none; border-radius: 12px; cursor: pointer; color: #FFFFFF; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; box-shadow: 0 6px 25px rgba(2,132,199,0.55);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 20px;">🚀</span>
                        <span style="letter-spacing: 0.5px;">LAUNCH AUTONOMOUS AUTO-PILOT VIDEO (1-CLICK)</span>
                    </div>
                    <span style="font-size: 11px; font-weight: 600; color: #BAE6FD; opacity: 0.9;">
                        ⚡ NanoPro Director Commissions Internet + 31+ APIs on Auto-Pilot
                    </span>
                </button>
                <div id="sqlVideoGenerationStatus" role="status" aria-live="polite" style="margin-top: 8px; min-height: 18px; color: #7DD3FC; font-size: 11.5px; text-align: center; font-weight: 600;"></div>
            </div>

            <!-- COLUMN 2: 9:16 TITANIUM SMARTPHONE PREVIEW -->
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">
                    <span style="font-size: 11.5px; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;">2. 9:16 SMARTPHONE PREVIEW (PROMPT-DRIVEN)</span>
                    <span id="playerTimer" style="font-size: 11px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 0:00</span>
                </div>

                <!-- Futuristic Smartphone Bezel -->
                <div id="phoneBezel" style="width: 340px; height: 604px; background: #000000; border: 4px solid #1E2D4A; border-radius: 38px; box-shadow: 0 25px 60px rgba(0,0,0,0.9), 0 0 30px rgba(56,189,248,0.25); position: relative; overflow: hidden; display: flex; flex-direction: column;">
                    
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

                    <!-- Picture-in-Picture Talking Avatar Window (Hedra, LivePortrait, HeyGen) -->
                    <div id="phoneAvatarPip" style="display:none !important; position:absolute; top:42px; right:12px; width:80px; height:100px; border-radius:12px; border:2px solid #38BDF8; background:#070B16; z-index:15; overflow:hidden; box-shadow:0 8px 20px rgba(0,0,0,0.8);">
                        <img id="phoneAvatarImg" src="" style="width:100%; height:100%; object-fit:cover;" />
                        <div style="position:absolute; bottom:2px; left:0; right:0; text-align:center; font-size:7.5px; background:rgba(0,0,0,0.7); color:#10B981; font-weight:800;">LIP-SYNC</div>
                    </div>

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
                
                <div class="vfx-glow-box" style="padding: 20px; border-color: rgba(16, 185, 129, 0.45); background: radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.12), transparent 70%), #0A0F1D;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 13.5px; font-weight: 900; color: #10B981; display: flex; align-items: center; gap: 6px;">
                            <span>🎬</span> <span>CLICK 9:16 VIDEO EXPORT</span>
                        </span>
                        <span style="font-size: 10px; background: rgba(236,72,153,0.2); color: #F472B6; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(236,72,153,0.4); font-weight: 800;">
                            🛡️ 100% Zero-Watermark
                        </span>
                    </div>

                    <div style="font-size: 11px; color: #94A3B8; margin-bottom: 14px; line-height: 1.55;">
                        Multi-Stage Composite: निवडलेले <b>Voice Engine</b>, <b>Lip-Sync Avatar</b> आणि <b>4K B-Roll Scene</b> एकत्र कम्पोझिट होऊन तुमच्या डिव्हाइसवर 1080×1920 60 FPS व्हिडिओ थेट सेव्ह होतो.
                    </div>

                    <!-- Local Device Hardware Check -->
                    <div style="background:rgba(7,11,22,.72);border:1px solid #1E2D4A;border-radius:8px;padding:10px;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                            <strong style="font-size:11px;color:#BAE6FD;">💻 HARDWARE ACCELERATION</strong>
                            <button type="button" class="btn btn-secondary" onclick="checkSqlVideoDevice()" style="padding:4px 9px;font-size:10px;border-color:#38BDF8;color:#7DD3FC;font-weight:700;">Check GPU &amp; WebGL</button>
                        </div>
                        <div id="sqlVideoDeviceStatus" role="status" aria-live="polite" style="margin-top:6px;color:#94A3B8;font-size:10px;line-height:1.5;">60 FPS WebGL Hardware Compositor Ready. Zero CPU bottleneck.</div>
                    </div>

                    <!-- Export Resolution -->
                    <label for="sqlExportResolution" style="display:flex;align-items:center;justify-content:space-between;gap:10px;background:rgba(7,11,22,.72);border:1px solid #1E2D4A;border-radius:8px;padding:10px;margin-bottom:14px;color:#CBD5E1;font-size:11px;">
                        <span><strong style="color:#BAE6FD;">📺 Export Resolution</strong><br><span style="color:#94A3B8;">Ultra-crisp 9:16 Shorts &amp; Reels format</span></span>
                        <select id="sqlExportResolution" aria-label="Video export resolution" style="background:#0B1120;color:#F8FAFC;border:1px solid #334155;border-radius:6px;padding:7px 9px;font-size:11px;font-weight:700;">
                            <option value="1080">1080p Full HD · 1080×1920 (Fast)</option>
                            <option value="4k">4K UHD · 2160×3840 (Ultra VFX)</option>
                        </select>
                    </label>

                    <!-- Direct Download Button Group -->
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 13px 12px; font-weight: 900; font-size: 12.5px; letter-spacing: 0.3px; background: linear-gradient(135deg, #10B981, #06B6D4); border: none; border-radius: 8px; cursor: pointer; color: #000; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 18px rgba(16,185,129,0.4);">
                            <span style="font-size: 18px; flex-shrink: 0;">📥</span>
                            <span id="exportBtnLabel">DOWNLOAD FULL 9:16 VIDEO (VOICE &amp; B-ROLL SYNCED)</span>
                        </button>

                        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                            <button type="button" class="btn btn-secondary" onclick="downloadVoiceoverMp3()" id="btnDownloadAudioOnly" style="flex: 1 1 90px; padding: 7px 6px; font-size: 10.5px; font-weight: 700; border-color: #10B981; color: #10B981;" title="Download Teacher Audio (.mp3)">
                                🎵 Save Voice (.mp3)
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="downloadCurrentFrameAsPng()" style="flex: 1 1 90px; padding: 7px 6px; font-size: 10.5px; font-weight: 700; border-color: #F59E0B; color: #F59E0B;" title="Save current frame as HD PNG">
                                📸 Save Frame (.png)
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
                                        AI ENGINES ATTRIBUTION &amp; AUDIT LEDGER
                                    </h4>
                                    <div style="font-size: 10.5px; color: #94A3B8;">50+ AI Model Transparency • Full Scene Composition Breakdown</div>
                                </div>
                            </div>
                            <span id="ledgerPatternBadge" style="font-size: 10px; font-weight: 800; color: #10B981; background: rgba(16,185,129,0.15); border: 1px solid #10B981; padding: 3px 10px; border-radius: 6px;">
                                MULTI-MODEL HYBRID (4 AI MODELS)
                            </span>
                        </div>

                        <!-- Scene Breakdown Grid -->
                        <div id="ledgerScenesList" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px;">
                            <!-- Dynamically injected scene attribution cards -->
                        </div>

                        <!-- Hardware & Voice Pipeline Summary -->
                        <div style="background: rgba(7, 11, 22, 0.8); border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">
                            <div>
                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🎙️ Voiceover Engine</div>
                                <div id="ledgerVoiceName" style="font-size: 11.5px; color: #34D399; font-weight: 800; margin-top: 2px;">Edge Neural Marathi</div>
                                <div style="font-size: 9.5px; color: #94A3B8;">Devanagari Teacher Cadence</div>
                            </div>
                            <div>
                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">⚡ Subtitle Engine</div>
                                <div style="font-size: 11.5px; color: #38BDF8; font-weight: 800; margin-top: 2px;">NanoPro Synced Karaoke</div>
                                <div style="font-size: 9.5px; color: #94A3B8;">Word-Level Frame Alignment</div>
                            </div>
                            <div>
                                <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">💻 Master Compositor</div>
                                <div style="font-size: 11.5px; color: #FBBF24; font-weight: 800; margin-top: 2px;">Laptop GPU NVENC FFmpeg</div>
                                <div style="font-size: 9.5px; color: #94A3B8;">1080×1920 60FPS • Zero-Watermark</div>
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

    function onVoiceEngineChange(val) {
        const badge = document.getElementById('voiceLatencyBadge');
        if (badge) {
            badge.innerText = val.includes('free') ? 'Zero-Cost CPU Active' : (val.includes('cartesia') ? '40ms Ultra-Fast' : 'Studio Quality');
        }
    }

    function onAvatarEngineChange(val) {
        const badge = document.getElementById('avatarFpsBadge');
        if (badge) {
            badge.innerText = val.includes('hedra') ? '#1 Trending Dev API' : (val.includes('free') ? 'Free Landmark Sync' : '4K Lip-Sync');
        }
    }

    function onBrollEngineChange(val) {
        const badge = document.getElementById('brollResBadge');
        if (badge) {
            badge.innerText = val.includes('free') ? '100% Free Stream' : (val.includes('seedance') ? 'Leaderboard #1' : '1080p 60FPS');
        }
        const hiddenMod = document.getElementById('selectedModernVideoModel');
        if (hiddenMod) hiddenMod.value = val;
    }

    function onAggregatorEngineChange(val) {
        const badge = document.getElementById('gatewayStatusBadge');
        if (badge) {
            badge.innerText = val.includes('cascade') ? 'Auto-Cascade Armed' : 'Serverless Queue Active';
        }
    }
    </script>
    """
