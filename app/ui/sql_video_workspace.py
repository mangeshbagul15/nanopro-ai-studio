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
        overflow-x: auto;
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
        grid-template-columns: 370px 340px 480px;
        min-width: 1210px;
        gap: 20px;
        align-items: start;
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
        font-size: 11px;
        padding: 8px 4px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        font-weight: 600;
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
        font-size: 11px;
        padding: 8px 4px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        font-weight: 600;
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
        font-size: 11px;
        padding: 8px 4px;
        border-radius: 6px;
        cursor: pointer;
        border: 1.5px solid #1E2D4A !important;
        background: #0B1120 !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        font-weight: 600;
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
    .sql-avatar-btn.active .btn-check {
        display: inline-block;
    }

    .btn-check {
        display: none;
        font-weight: 900;
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
                <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; font-size: 11px; padding: 4px 10px; border-radius: 20px;">📱 9:16 Vertical Reel (&lt;60s)</span>
                <span class="status-pill" style="background: rgba(139, 92, 246, 0.15); border: 1px solid #8B5CF6; color: #8B5CF6; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🔊 Regional AI Voice Live</span>
                <span class="status-pill" style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #F59E0B; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🤖 Coding Intelligence Models Live</span>
            </div>
        </div>

        <!-- Horizontal Scroll Guide & Fast Jump Bar -->
        <div style="background: rgba(14, 21, 40, 0.95); border: 1.5px solid #1E2D4A; border-radius: 10px; padding: 10px 16px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
            <div style="font-size: 12px; color: #38BDF8; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">↔️</span>
                <span><b>HORIZONTAL SCROLL BAR ACTIVE:</b> तिन्ही स्तंभ (Columns) एका रेषेत पाहण्यासाठी खालील आडवा बार वापरा किंवा थेट जा:</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <button type="button" class="btn btn-secondary" onclick="document.querySelector('.sql-shorts-container').scrollTo({left: 0, behavior: 'smooth'});" style="font-size: 11px; padding: 5px 12px; font-weight: 700; border-color: #38BDF8; color: #38BDF8;">
                    ⬅️ 1. Scenario (डावे)
                </button>
                <button type="button" class="btn btn-secondary" onclick="document.querySelector('.sql-shorts-container').scrollTo({left: 360, behavior: 'smooth'});" style="font-size: 11px; padding: 5px 12px; font-weight: 700; border-color: #F59E0B; color: #F59E0B;">
                    📱 2. Preview (मध्यम)
                </button>
                <button type="button" class="btn btn-primary" onclick="document.querySelector('.sql-shorts-container').scrollTo({left: 780, behavior: 'smooth'});" style="font-size: 11px; padding: 5px 14px; background: linear-gradient(135deg, #10B981, #06B6D4); color: #000; font-weight: 900; box-shadow: 0 0 12px rgba(16,185,129,0.35);">
                    ➡️ 3. 1-Click Export (उजवे)
                </button>
            </div>
        </div>

        <!-- Main Studio Grid (Controls + Phone Preview + Sandbox) -->
        <div class="sql-studio-grid" id="sqlStudioMainGrid">
            
            <!-- COLUMN 1: AI Prompt Generator & Language Controls -->
            <div class="panel-card" style="margin: 0; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 12px; padding: 18px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <h3 style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 700;">1. MASTER PROMPT &amp; TECH SCENARIO INPUT</h3>
                    <span style="font-size: 11px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 8px; border-radius: 6px; font-weight: 700;">⚡ Universal AI Studio</span>
                </div>

                <!-- Master Prompt Input Textarea -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <label class="input-label" style="font-size: 12px; color: #38BDF8; font-weight: 700; margin: 0;">
                        📝 Tech Concept / Prompt Input:
                    </label>
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary" onclick="clearMasterPrompt()" style="font-size: 10px; padding: 4px 10px; border-color: #EF4444; color: #EF4444; font-weight: 700;" title="Clear prompt input">
                            🧹 Clear Prompt
                        </button>
                    </div>
                </div>

                <textarea class="studio-input" id="sqlShortQuestion" rows="8" placeholder="तुमचा मास्टर प्रॉम्प्ट (Master Prompt), टेक प्रश्न, कोडिंग किंवा संकल्पना इथे प्रविष्ट करा...

उदा. ट्रेंडिंग विषय:
- SQL / Snowflake: Find the latest transaction per customer using ROW_NUMBER() and QUALIFY in Snowflake.
- Python: Advanced FastAPI async background task queue with Redis &amp; Upstash.
- AWS / Data Engineering: S3 to Snowflake Auto-Ingest Snowpipe real-time architecture.
- AI &amp; RAG: Vector search, chunking &amp; semantic retrieval pipeline using LangChain.
- Cloud &amp; Docker: Multi-stage Docker build &amp; Kubernetes deployment best practices.
- Git: Interactive Rebase vs Merge conflict resolution workflow.
- Theory / Architecture: Grey/navy blue transparent glass tiles, laser connecting arrows, step-by-step animations...

✨ कोडिंग मॉडेल्स (Groq LPU / Gemini Flash) आणि व्हिडिओ इंजिन स्वतः हा प्रॉम्प्ट वाचून व्हिडिओची रचना, ॲनिमेशन आणि ऑडिओ 100% डायनॅमिकली तयार करेल!" style="width: 100%; margin-bottom: 12px; background: #070B16; border: 1.5px solid #283C62; color: #F8FAFC; font-size: 12px; font-family: monospace; border-radius: 8px; padding: 10px; line-height: 1.5; resize: vertical;"></textarea>

                <!-- Multilingual Controls: Audio Voice & Text Overlays -->
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: #38BDF8; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; display:flex; justify-content:space-between;">
                        <span>🎙️ Voiceover Audio &amp; Subtitle Controls</span>
                        <span id="activeVoiceBadge" style="color:#10B981; font-weight:700;">मराठी शिक्षक</span>
                    </div>
                    
                    <!-- Voiceover Language Selector Buttons -->
                    <div style="margin-bottom: 12px;">
                        <span style="font-size: 11px; color: #94A3B8; display: block; margin-bottom: 6px;">🗣️ Natural Teacher Voice Language:</span>
                        <div style="display: flex; gap: 6px;">
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

                    <!-- Subtitle / Overlay Text Style Selector Buttons -->
                    <div>
                        <span style="font-size: 11px; color: #94A3B8; display: block; margin-bottom: 6px;">📝 Subtitle / Code Explanation Style:</span>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" class="sql-text-btn" id="btnTextEn" onclick="setSqlTextStyle('en')">
                                <span class="btn-check">✓</span> <span>English</span>
                            </button>
                            <button type="button" class="sql-text-btn active" id="btnTextMinglish" onclick="setSqlTextStyle('minglish')">
                                <span class="btn-check">✓</span> <span>Minglish (मराठी)</span>
                            </button>
                            <button type="button" class="sql-text-btn" id="btnTextHinglish" onclick="setSqlTextStyle('hinglish')">
                                <span class="btn-check">✓</span> <span>Hinglish</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- AI Talking Avatar Presenter Controls (HeyGen & D-ID Integration) -->
                <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size: 11px; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.5px;">🧑‍💼 AI Talking Avatar Presenter</span>
                        <span style="font-size: 10px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 6px; border-radius: 4px;">Auto-Failover Live</span>
                    </div>

                    <!-- Toggle Avatar ON / OFF -->
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <button type="button" class="sql-avatar-btn active" id="btnAvatarToggleOn" onclick="toggleSqlAvatar(true)">
                            <span class="btn-check">✓</span> <span>🧑‍💼 AI Avatar ON</span>
                        </button>
                        <button type="button" class="sql-avatar-btn" id="btnAvatarToggleOff" onclick="toggleSqlAvatar(false)">
                            <span class="btn-check">✓</span> <span>🚫 Code Only (Full Screen)</span>
                        </button>
                    </div>

                    <!-- Dynamic Avatar Configuration (Zero Hardcoded Dropdowns) -->
                    <input type="hidden" id="sqlAvatarSelect" value="Nadim_public_5" />
                    <div style="font-size: 11px; color: #94A3B8; margin-bottom: 8px; line-height: 1.4;">
                        Presenter &amp; character model chosen dynamically based on prompt scenario (Autonomous Failover: HeyGen 4K ➔ D-ID Creative ➔ Cyber Canvas).
                    </div>

                    <!-- Generate Avatar Button -->
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary" onclick="renderAiAvatarVideo()" id="btnRenderAvatar" style="flex: 1; font-size: 11px; padding: 8px; color: #C7D2FE; border-color: rgba(99,102,241,0.5); font-weight:700;">
                            🎬 Generate AI Avatar Hook Video (HeyGen / D-ID)
                        </button>
                    </div>
                    <div id="avatarRenderStatus" style="font-size: 10px; color: #94A3B8; margin-top: 6px; display: none;"></div>
                </div>

                <!-- 3D Cinematic Motion Background (Runway Gen-4 & Luma Dream Machine) -->
                <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size: 11px; font-weight: 700; color: #C084FC; text-transform: uppercase; letter-spacing: 0.5px;">🎥 3D Motion Background (Runway &amp; Luma)</span>
                        <span style="font-size: 10px; color: #38BDF8; background: rgba(56,189,248,0.15); padding: 2px 6px; border-radius: 4px;">Dynamic Motion</span>
                    </div>
                    <!-- Dynamic Background Selector Buttons (Zero Dropdowns) -->
                    <input type="hidden" id="sqlCinematicBgSelect" value="cyber_matrix" />
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <button type="button" class="sql-avatar-btn active" id="btnBgCyber" onclick="document.getElementById('sqlCinematicBgSelect').value='cyber_matrix'; this.classList.add('active'); document.getElementById('btnBg3D').classList.remove('active');">
                            <span class="btn-check">✓</span> <span>🌐 Transparent Cyber Glass</span>
                        </button>
                        <button type="button" class="sql-avatar-btn" id="btnBg3D" onclick="document.getElementById('sqlCinematicBgSelect').value='runway_cloud'; this.classList.add('active'); document.getElementById('btnBgCyber').classList.remove('active');">
                            <span class="btn-check">✓</span> <span>🎥 3D AI Motion Engine</span>
                        </button>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary" onclick="renderCinematicBackgroundVideo()" id="btnRenderCinematicBg" style="flex: 1; font-size: 11px; padding: 6px; color: #C084FC; border-color: rgba(168,85,247,0.4);">
                            🚀 Generate 9:16 Cinematic Video (Runway / Luma)
                        </button>
                    </div>
                    <div id="cinematicBgRenderStatus" style="font-size: 10px; color: #94A3B8; margin-top: 6px; display: none;"></div>
                </div>

                <!-- Generate AI Blueprint Button -->
                <button type="button" class="btn btn-primary" id="btnGenerateSqlBlueprint" onclick="generateSqlShortBlueprint()" style="width: 100%; padding: 12px; font-weight: 800; font-size: 13px; background: linear-gradient(135deg, #0284C7, #6366F1); border: none; border-radius: 8px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 15px rgba(2,132,199,0.35);">
                    <span>✨ Generate AI Teacher Video &amp; Voice from Prompt</span>
                </button>


            </div>

            <!-- COLUMN 2: 9:16 Smartphone Mockup Live Player (Trending UI) -->
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">
                    <span style="font-size: 12px; font-weight: 700; color: #38BDF8;">2. 9:16 SMARTPHONE PREVIEW (PROMPT-DRIVEN)</span>
                    <span id="playerTimer" style="font-size: 12px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 0:58</span>
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
                    <input type="range" id="sqlShortScrubber" min="0" max="58" value="0" step="0.5" oninput="seekSqlShortPlayer(this.value)" style="width: 100%; accent-color: #38BDF8; cursor: pointer; margin-bottom: 8px;" />
                    
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
                        1080x1920 फुल-एचडी रेंडरिंग सोबत नॅचरल AI शिक्षक ऑडिओ इंटिग्रेटेड (&lt;६० से.)! कोपऱ्यातील वॉटरमार्क 100% रिमूव्ह केले जातात.
                    </div>

                    <!-- Direct Download Button Group -->
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 14px; font-weight: 900; font-size: 13px; letter-spacing: 0.5px; background: linear-gradient(135deg, #10B981, #06B6D4); border: none; border-radius: 8px; cursor: pointer; color: #000; display: flex; align-items: center; justify-content: center; gap: 10px; box-shadow: 0 4px 15px rgba(16,185,129,0.35);">
                            <span style="font-size: 18px;">📥</span>
                            <span id="exportBtnLabel">DOWNLOAD 9:16 SHORT / REEL (&lt;60s) (WITH SYNCHRONIZED VOICE)</span>
                        </button>

                        <div style="display: flex; gap: 8px;">
                            <button type="button" class="btn btn-secondary" onclick="exportSqlShortVideo(15)" style="flex: 1; padding: 8px 6px; font-size: 11px; font-weight: 700; border-color: #38BDF8; color: #38BDF8;" title="15-sec quick test video with audio">
                                ⚡ Quick 15s Test
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="downloadVoiceoverMp3()" id="btnDownloadAudioOnly" style="flex: 1; padding: 8px 6px; font-size: 11px; font-weight: 700; border-color: #10B981; color: #10B981;" title="Download Teacher Audio (MP3)">
                                🎵 Save Voice (MP3)
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="downloadCurrentFrameAsPng()" style="flex: 1; padding: 8px 6px; font-size: 11px; font-weight: 700; border-color: #F59E0B; color: #F59E0B;" title="Save current frame as HD PNG">
                                📸 Save Frame (PNG)
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
                            <span id="exportFrameStats">🎞️ फ्रेम: 0 / 1800</span>
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
        </div>
    </div>
    <!-- END 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    '''
