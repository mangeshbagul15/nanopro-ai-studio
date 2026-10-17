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

    <!-- 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    <div class="sql-shorts-container" style="margin-bottom: 24px;">
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.15)); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 26px;">🚀</span>
                    <div>
                        <h2 style="margin: 0; font-size: 18px; color: #38BDF8; font-weight: 800; letter-spacing: 0.5px;">FAANG &amp; TOP MNC SQL INTERVIEW PREPARATION STUDIO</h2>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">Standard Interview Questions • Step-by-Step Code Typing • Dynamic Arrow Motion • 100% Zero-Watermark • Natural Human Regional Voice</div>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="status-pill" style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #10B981; font-size: 11px; padding: 4px 10px; border-radius: 20px;">⚡ 22/22 APIs Live (Runway + Luma + HeyGen + D-ID)</span>
                <span class="status-pill" style="background: rgba(236, 72, 153, 0.15); border: 1px solid #EC4899; color: #EC4899; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🛡️ 100% Watermark-Free</span>
                <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; font-size: 11px; padding: 4px 10px; border-radius: 20px;">📱 9:16 Vertical Reel (60s)</span>
                <span class="status-pill" style="background: rgba(139, 92, 246, 0.15); border: 1px solid #8B5CF6; color: #8B5CF6; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🔊 Natural Human Audio Live</span>
                <span class="status-pill" style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #F59E0B; font-size: 11px; padding: 4px 10px; border-radius: 20px;">💻 0% Server CPU Load</span>
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
                    <h3 style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 700;">1. TOP MNC INTERVIEW SCENARIOS</h3>
                    <span style="font-size: 11px; color: #38BDF8; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 6px;">FAANG &amp; MNC Standard</span>
                </div>

                <!-- Standard SQL Interview Presets Dropdown -->
                <label class="input-label" style="font-size: 12px; color: #94A3B8; font-weight: 600;">Technical Interview Drill (Select Question)</label>
                <select class="studio-input" id="sqlShortPresetSelect" onchange="handleSqlPresetChange(this.value)" style="width: 100%; margin-bottom: 12px; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; border-radius: 6px; padding: 8px 10px; font-size: 12px;">
                    <option value="sql_q1_second_highest_salary" selected>⭐ Q1: EMPLOYEES — 2nd Highest Salary (Subquery Method)</option>
                    <option value="faang_dense_rank_ties">🏢 Amazon / Google: 2nd Highest Salary With Ties (DENSE_RANK)</option>
                    <option value="goldman_running_balance">🏦 Goldman Sachs / HDFC: Cumulative Running Balance (SUM OVER)</option>
                    <option value="uber_consecutive_active_days">🚗 Uber / Swiggy: Consecutive Active Days (Gaps &amp; Islands)</option>
                    <option value="netflix_top_n_per_category">🎬 Netflix / Spotify: Top 2 Titles Per Category (PARTITION BY)</option>
                    <option value="meta_reciprocal_friends">🌐 Meta / LinkedIn: Mutual Reciprocal Connections (Self-Join)</option>
                    <option value="amazon_churn_zero_orders">📦 Amazon / Flipkart: Customers with ZERO Orders (Anti-Join)</option>
                    <option value="stripe_consecutive_fraud">💳 Stripe / PayPal: Consecutive High-Value Withdrawals (LAG)</option>
                    <option value="zomato_mom_growth">📈 Swiggy / Zomato: Month-over-Month Growth % (LAG Window)</option>
                    <option value="custom">⚡ Custom Interview Scenario / Live Question...</option>
                </select>

                <!-- Interview Question Textarea -->
                <label class="input-label" style="font-size: 12px; color: #94A3B8; font-weight: 600;">Question Understanding &amp; Problem Statement</label>
                <textarea class="studio-input" id="sqlShortQuestion" rows="3" placeholder="Enter standard SQL interview question..." style="width: 100%; margin-bottom: 12px; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; font-size: 12px; border-radius: 6px; padding: 8px;"></textarea>

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

                    <!-- Avatar Presenter Dropdown -->
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <select class="studio-input" id="sqlAvatarSelect" onchange="setSqlAvatarPresenter(this.value)" style="flex: 1; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; border-radius: 6px; padding: 6px; font-size: 11px;">
                            <option value="Nadim_public_5" selected>🧑‍💼 Nadim (HeyGen Banker Lead - 4K)</option>
                            <option value="Wayne_20240711">👨‍💼 Wayne (HeyGen Wall St Exec)</option>
                            <option value="Daisy-inskirt-20220818">👩‍💼 Daisy (HeyGen Tech Lead)</option>
                            <option value="did_adam">🧑‍💻 Adam (D-ID Creative Reality)</option>
                            <option value="did_emma">👩‍💼 Emma (D-ID Fintech Anchor)</option>
                        </select>
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
                        <span style="font-size: 10px; color: #38BDF8; background: rgba(56,189,248,0.15); padding: 2px 6px; border-radius: 4px;">Runway Gen-4</span>
                    </div>
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <select class="studio-input" id="sqlCinematicBgSelect" style="flex: 1; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; border-radius: 6px; padding: 6px; font-size: 11px;">
                            <option value="cyber_matrix" selected>🌐 Cyber Grid &amp; Neon Data Stream (Fast Canvas)</option>
                            <option value="runway_fintech">🏦 Runway Gen-4: High-Tech Global Banking Server Room</option>
                            <option value="runway_cloud">☁️ Runway Gen-4: Modern Cloud Data Warehouse &amp; Analytics</option>
                            <option value="luma_dataflow">✨ Luma Dream Machine: 3D Golden SQL Particles</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary" onclick="renderCinematicBackgroundVideo()" id="btnRenderCinematicBg" style="flex: 1; font-size: 11px; padding: 6px; color: #C084FC; border-color: rgba(168,85,247,0.4);">
                            🚀 Generate 9:16 Cinematic Video (Runway / Luma)
                        </button>
                    </div>
                    <div id="cinematicBgRenderStatus" style="font-size: 10px; color: #94A3B8; margin-top: 6px; display: none;"></div>
                </div>

                <!-- Generate AI Blueprint Button -->
                <button type="button" class="btn btn-primary" id="btnGenerateSqlBlueprint" onclick="generateSqlShortBlueprint()" style="width: 100%; padding: 10px; font-weight: 700; background: linear-gradient(135deg, #0284C7, #6366F1); border: none; border-radius: 6px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span>✨ Generate 85s AI Teacher Blueprint &amp; Prompt</span>
                </button>

                <!-- 85-Second Master Storyboard Breakdown Accordion -->
                <div id="sqlShortBlueprintBox" style="margin-top: 14px; background: #070B16; border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; font-size: 11px; max-height: 250px; overflow-y: auto;">
                    <div style="color: #38BDF8; font-weight: 700; margin-bottom: 6px;">⏱️ 85-SECOND AI TEACHER STORYBOARD (7 SCENES):</div>
                    <div style="color: #38BDF8; margin-bottom: 4px;"><b>0:00 - 0:08 [1. INTRO]:</b> <span id="bpTimelineHook">Question Intro &amp; EMPLOYEES Table (Empty SQL Editor)</span></div>
                    <div style="color: #F59E0B; margin-bottom: 4px;"><b>0:08 - 0:20 [2. UNDERSTAND]:</b> <span id="bpTimelineSchema">Salary Inspection &amp; Duplicate 80k Tie Trap</span></div>
                    <div style="color: #A855F7; margin-bottom: 4px;"><b>0:20 - 0:32 [3. LOGIC]:</b> Strategy Flowchart (Max ➔ Exclude ➔ Max Remaining ➔ 70k)</div>
                    <div style="color: #10B981; margin-bottom: 4px;"><b>0:32 - 0:44 [4. INNER SQL]:</b> Typewriter Inner Query: <code style="color:#38BDF8;">SELECT MAX(SALARY)</code> (80k)</div>
                    <div style="color: #EC4899; margin-bottom: 4px;"><b>0:44 - 0:58 [5. FILTER]:</b> <code style="color:#F59E0B;">WHERE SALARY &lt; (...)</code> + Row Evaluation Table</div>
                    <div style="color: #06B6D4; margin-bottom: 4px;"><b>0:58 - 1:12 [6. RESULT]:</b> Outer MAX Execution ➔ Output = 70000 (Neha)</div>
                    <div style="color: #F43F5E; margin-bottom: 4px;"><b>1:12 - 1:25 [7. TIP &amp; BRAND]:</b> FAANG Interview Tip &amp; @Code_With_Mangesh</div>
                </div>
            </div>

            <!-- COLUMN 2: 9:16 Smartphone Mockup Live Player (Trending UI) -->
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">
                    <span style="font-size: 12px; font-weight: 700; color: #38BDF8;">2. 9:16 SMARTPHONE PREVIEW</span>
                    <span id="playerTimer" style="font-size: 12px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 1:25</span>
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
                    <input type="range" id="sqlShortScrubber" min="0" max="85" value="0" step="0.5" oninput="seekSqlShortPlayer(this.value)" style="width: 100%; accent-color: #38BDF8; cursor: pointer; margin-bottom: 8px;" />
                    
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

            <!-- COLUMN 3: 1-CLICK EXPORT, LIVE STAGE MONITOR & SQL SANDBOX -->
            <div id="exportCardContainer" style="display: flex; flex-direction: column; gap: 16px;">
                
                <!-- 1. PRIMARY EXPORT & LIVE STAGE MONITOR CARD -->
                <div class="panel-card" style="margin: 0; background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(6, 182, 212, 0.12)); border: 1.5px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 13px; font-weight: 800; color: #10B981; display: flex; align-items: center; gap: 6px;">
                            <span>🎬</span> <span>1-CLICK 9:16 VIDEO EXPORT</span>
                        </span>
                        <span style="font-size: 10px; background: rgba(236,72,153,0.2); color: #F472B6; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(236,72,153,0.4); font-weight: 700;">🛡️ 100% Zero-Watermark</span>
                    </div>
                    <div style="font-size: 11px; color: #94A3B8; margin-bottom: 12px;">
                        1080x1920 फुल-एचडी रेंडरिंग सोबत <b>८५-सेकंद नॅचरल AI शिक्षक ऑडिओ</b> इंटिग्रेटेड! कोपऱ्यातील वॉटरमार्क 100% रिमूव्ह केले जातात.
                    </div>

                    <!-- Direct Download Button Group -->
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo(85)" style="width: 100%; padding: 14px; font-weight: 900; font-size: 13px; letter-spacing: 0.5px; background: linear-gradient(135deg, #10B981, #06B6D4); border: none; border-radius: 8px; cursor: pointer; color: #000; display: flex; align-items: center; justify-content: center; gap: 10px; box-shadow: 0 4px 15px rgba(16,185,129,0.35);">
                            <span style="font-size: 18px;">📥</span>
                            <span id="exportBtnLabel">DOWNLOAD 85s AI TEACHER VIDEO (WITH SYNCHRONIZED VOICE)</span>
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

                    <!-- Live 7-Stage Tracker & Real-Time Countdown Monitor -->
                    <div id="exportLiveStageBox" style="margin-top: 14px; background: #070B16; border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 11px; font-weight: 700; color: #38BDF8; text-transform: uppercase;">📊 7-SCENE MASTER TRACKER:</span>
                            <span id="exportLiveBadge" style="font-size: 10px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 6px; border-radius: 4px; font-weight: 700;">तयार आहे (Ready)</span>
                        </div>
                        
                        <!-- 7 Stages Grid -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px;" id="exportStagePills">
                            <div class="stage-pill" id="stagePill1"><span>1️⃣</span> <span>प्रश्न ओळख (0-8s)</span></div>
                            <div class="stage-pill" id="stagePill2"><span>2️⃣</span> <span>डुप्लिकेट समज (8-20s)</span></div>
                            <div class="stage-pill" id="stagePill3"><span>3️⃣</span> <span>लॉजिक फ्लो (20-32s)</span></div>
                            <div class="stage-pill" id="stagePill4"><span>4️⃣</span> <span>इनर सबक्वेरी (32-44s)</span></div>
                            <div class="stage-pill" id="stagePill5"><span>5️⃣</span> <span>रो फिल्टर (44-58s)</span></div>
                            <div class="stage-pill" id="stagePill6"><span>6️⃣</span> <span>निकाल 70,000 (58-72s)</span></div>
                            <div class="stage-pill" id="stagePill7" style="grid-column: span 2;"><span>7️⃣</span> <span>💡 प्रो-टिप व @Code_With_Mangesh (72-85s)</span></div>
                        </div>
                        
                        <!-- Progress Bar & Remaining Time Stats -->
                        <div id="exportProgressBarContainer" style="display:none; background: #0B1120; border: 1px solid #1E2D4A; border-radius: 6px; padding: 10px; margin-top: 8px;">
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
                        <div id="videoReadyCelebration" style="display:none; background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(6,182,212,0.25)); border: 2px solid #10B981; border-radius: 8px; padding: 14px; text-align: center; margin-top: 10px; animation: popIn 0.3s ease-out;">
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

                <!-- 2. IN-MEMORY SQLITE SANDBOX (< 2ms) -->
                <div class="panel-card" style="margin: 0; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 12px; padding: 16px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <h3 style="margin: 0; font-size: 13px; color: #F8FAFC; font-weight: 700;">2. LIVE SQLITE SANDBOX &amp; CODE</h3>
                        <span style="font-size: 10px; color: #10B981; background: rgba(16,185,129,0.1); padding: 2px 6px; border-radius: 4px; font-family: monospace;">SQLite &lt; 2ms</span>
                    </div>

                    <!-- SQL Query Editor Preview -->
                    <label class="input-label" style="font-size: 11px; color: #94A3B8; font-weight: 600;">व्हिडिओमधील SQL कोड (Live Code Preview):</label>
                    <textarea class="studio-input code-editor" id="sqlShortCodePreview" rows="5" style="width: 100%; font-family: monospace; font-size: 11px; background: #070B16; border: 1px solid #283C62; color: #38BDF8; margin-bottom: 8px; border-radius: 6px; padding: 8px;"></textarea>

                    <!-- Sandbox Run Button -->
                    <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                        <button type="button" class="btn btn-secondary" onclick="runInMemorySqlSandbox()" style="flex: 1; padding: 7px; font-size: 11px; font-weight: 700; border-color: #38BDF8; color: #38BDF8;">
                            ▶ Test Query in SQLite (&lt; 2ms)
                        </button>
                        <span id="sandboxLatency" style="font-size: 11px; color: #10B981; align-self: center; font-family: monospace;"></span>
                    </div>

                    <!-- Sandbox Output Table -->
                    <div id="sandboxOutputTable" style="max-height: 120px; overflow-y: auto; background: #070B16; border: 1px solid #1E2D4A; border-radius: 6px; padding: 6px; font-size: 10px; font-family: monospace; color: #E2E8F0;">
                        <div style="color: #64748B; text-align: center; padding: 8px;">[Test Query] दाबा आणि रिअल डेटाबेस निकाल पाहा...</div>
                    </div>
                </div>

                <!-- 3. टेक्निकल इंटरव्ह्यू संकल्पना व मार्गदर्शन (Technical Concept Breakdown Card) -->
                <div class="panel-card" style="margin: 0; background: rgba(15, 23, 42, 0.6); border: 1px solid #1E2D4A; border-radius: 12px; padding: 14px; font-size: 11px;">
                    <div style="font-size: 12px; font-weight: 700; color: #F59E0B; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                        <span>🎓</span> <span>टेक्निकल इंटरव्ह्यू मार्गदर्शन (Step-by-Step Concept Mastery)</span>
                    </div>
                    <div id="studentConceptHelp" style="color: #CBD5E1; line-height: 1.6;">
                        • <b>प्रश्न समजून घ्या (Question Understanding):</b> समान पगार असताना २ रा सर्वाधिक पगार कसा काढायचा? सामान्य RANK() मुळे २ रा नंबर गाळला जातो, पण DENSE_RANK() अचूक २ रा नंबर देते.<br>
                        • <b>कस कोड लिहायचा (How to Write):</b> WITH RankedSalaries AS (SELECT ..., DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk) SELECT * WHERE rnk = 2;<br>
                        • <b>महत्त्वाची क्लॉज (Critical Clause):</b> DENSE_RANK() OVER (ORDER BY salary DESC)<br>
                        • <b>इंटरव्ह्यूअर प्रो-टिप:</b> प्रॉडक्शन डेटाबेसमध्ये LIMIT 1 OFFSET 1 कधीही वापरू नका!
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- END 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    '''
