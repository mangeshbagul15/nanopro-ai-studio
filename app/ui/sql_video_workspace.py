"""
Mangesh Nano Pro AI Studio - 9:16 SQL Short Video Creation Workspace
Dedicated Mobile, Instagram Reels & YouTube Shorts Studio (Max 60 Seconds).
Zero Server Load: Client-Side Canvas & MediaRecorder Video Generation.
"""

def get_sql_video_workspace_html() -> str:
    return r'''
    <!-- 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    <div class="sql-shorts-container" style="margin-bottom: 24px;">
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.15)); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">📱</span>
                    <div>
                        <h2 style="margin: 0; font-size: 18px; color: #38BDF8; font-weight: 800; letter-spacing: 0.5px;">9:16 SQL SHORT VIDEO CREATION WORKSPACE</h2>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">Trending Mobile Reels & Shorts (Max 60s) • Peak Point Viral Hooks • Real Banking Scenarios • Arrow Motion • Zero Server CPU Load</div>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="status-pill" style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #10B981; font-size: 11px; padding: 4px 10px; border-radius: 20px;">⚡ 21/21 APIs Live</span>
                <span class="status-pill" style="background: rgba(236, 72, 153, 0.15); border: 1px solid #EC4899; color: #EC4899; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🛡️ 100% Watermark-Free</span>
                <span class="status-pill" style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #F59E0B; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🇮🇳 ZP व ग्रामीण विद्यार्थी मिशन</span>
                <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; font-size: 11px; padding: 4px 10px; border-radius: 20px;">📱 9:16 Vertical (60s)</span>
                <span class="status-pill" style="background: rgba(139, 92, 246, 0.15); border: 1px solid #8B5CF6; color: #8B5CF6; font-size: 11px; padding: 4px 10px; border-radius: 20px;">💻 0% Server Load</span>
            </div>
        </div>

        <!-- Main Studio Grid (Controls + Phone Preview + Sandbox) -->
        <div style="display: grid; grid-template-columns: minmax(360px, 1.2fr) minmax(340px, 0.9fr) minmax(340px, 1.1fr); gap: 20px; align-items: start;">
            
            <!-- COLUMN 1: AI Prompt Generator & Language Controls -->
            <div class="panel-card" style="margin: 0; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 12px; padding: 18px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <h3 style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 700;">1. SCENARIO &amp; AI PROMPT BLUEPRINT</h3>
                    <span style="font-size: 11px; color: #38BDF8; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 6px;">AI Prompt Engine</span>
                </div>

                <!-- Rural & Banking Presets Dropdown -->
                <label class="input-label" style="font-size: 12px; color: #94A3B8; font-weight: 600;">Scenario Preset (ZP School / Kirana / Bank)</label>
                <select class="studio-input" id="sqlShortPresetSelect" onchange="handleSqlPresetChange(this.value)" style="width: 100%; margin-bottom: 12px; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; border-radius: 6px; padding: 8px 10px;">
                    <option value="zp_school_ranking" selected>🏫 ZP शाळा निकाल: समान गुण असताना २ रा क्रमांक (DENSE_RANK)</option>
                    <option value="kirana_dukan_hisob">🛒 गावचे किराणा दुकान: चालू उधारी व शिल्लक हिशोब (PARTITION BY)</option>
                    <option value="bank_running_total">🏦 HDFC / SBI: Cumulative Running Balance (SUM OVER PARTITION BY)</option>
                    <option value="bank_consecutive_fraud">💳 ICICI / Axis: Fraud Detection - Consecutive Withdrawals (LAG OVER)</option>
                    <option value="bank_salary_rank">📈 Goldman / Morgan: 2nd Highest Salary No Ties (DENSE_RANK)</option>
                    <option value="custom">⚡ Custom Question / Interview Scenario...</option>
                </select>

                <!-- Custom Question Textarea -->
                <label class="input-label" style="font-size: 12px; color: #94A3B8; font-weight: 600;">Interview Question / Business Scenario</label>
                <textarea class="studio-input" id="sqlShortQuestion" rows="3" placeholder="Enter bank level interview question..." style="width: 100%; margin-bottom: 12px; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; font-size: 12px; border-radius: 6px; padding: 8px;"></textarea>

                <!-- Multilingual Controls: Audio Voice & Text Overlays -->
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: #38BDF8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Multilingual Audio &amp; Text Settings</div>
                    
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 11px; color: #94A3B8; display: block; margin-bottom: 4px;">🎙️ Voiceover Audio Language:</span>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" class="btn btn-secondary sql-lang-btn active" id="btnAudioMr" onclick="setSqlAudioLang('mr')" style="flex:1; font-size:11px; padding: 6px 2px;">🇮🇳 मराठी</button>
                            <button type="button" class="btn btn-secondary sql-lang-btn" id="btnAudioHi" onclick="setSqlAudioLang('hi')" style="flex:1; font-size:11px; padding: 6px 2px;">🇮🇳 हिन्दी</button>
                            <button type="button" class="btn btn-secondary sql-lang-btn" id="btnAudioEn" onclick="setSqlAudioLang('en')" style="flex:1; font-size:11px; padding: 6px 2px;">🇬🇧 English</button>
                        </div>
                    </div>

                    <div>
                        <span style="font-size: 11px; color: #94A3B8; display: block; margin-bottom: 4px;">📝 Subtitle / Overlay Text Style:</span>
                        <div style="display: flex; gap: 6px;">
                            <button type="button" class="btn btn-secondary sql-text-btn" id="btnTextEn" onclick="setSqlTextStyle('en')" style="flex:1; font-size:11px; padding: 6px 2px;">English</button>
                            <button type="button" class="btn btn-secondary sql-text-btn active" id="btnTextMinglish" onclick="setSqlTextStyle('minglish')" style="flex:1; font-size:11px; padding: 6px 2px;">Minglish (मराठी)</button>
                            <button type="button" class="btn btn-secondary sql-text-btn" id="btnTextHinglish" onclick="setSqlTextStyle('hinglish')" style="flex:1; font-size:11px; padding: 6px 2px;">Hinglish</button>
                        </div>
                    </div>
                </div>

                <!-- AI Avatar Presenter Selector (HeyGen & D-ID Integration) -->
                <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size: 11px; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.5px;">🧑‍💼 AI Talking Avatar Presenter (HeyGen &amp; D-ID)</span>
                        <span style="font-size: 10px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 6px; border-radius: 4px;">20/20 APIs</span>
                    </div>
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <select class="studio-input" id="sqlAvatarSelect" onchange="setSqlAvatarPresenter(this.value)" style="flex: 1; background: #070B16; border: 1px solid #283C62; color: #F8FAFC; border-radius: 6px; padding: 6px; font-size: 11px;">
                            <option value="none">🚫 No Avatar (Cyber Code Only)</option>
                            <option value="Nadim_public_5" selected>🧑‍💼 Nadim (HeyGen Banker Lead - 4K)</option>
                            <option value="Wayne_20240711">👨‍💼 Wayne (HeyGen Wall St Exec)</option>
                            <option value="Daisy-inskirt-20220818">👩‍💼 Daisy (HeyGen Tech Lead)</option>
                            <option value="did_adam">🧑‍💻 Adam (D-ID Creative Reality)</option>
                            <option value="did_emma">👩‍💼 Emma (D-ID Fintech Anchor)</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button type="button" class="btn btn-secondary" onclick="renderAiAvatarVideo()" id="btnRenderAvatar" style="flex: 1; font-size: 11px; padding: 6px; color: #818CF8; border-color: rgba(99,102,241,0.4);">
                            🎬 Generate AI Avatar Hook Video (HeyGen / D-ID)
                        </button>
                    </div>
                    <div id="avatarRenderStatus" style="font-size: 10px; color: #94A3B8; margin-top: 6px; display: none;"></div>
                </div>

                <!-- Generate Blueprint Button -->
                <button type="button" class="btn btn-primary" id="btnGenerateSqlBlueprint" onclick="generateSqlShortBlueprint()" style="width: 100%; padding: 10px; font-weight: 700; background: linear-gradient(135deg, #0284C7, #6366F1); border: none; border-radius: 6px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span>✨ Generate 60s AI Blueprint &amp; Prompt</span>
                </button>

                <!-- 60-Second Timed Blueprint Breakdown Accordion -->
                <div id="sqlShortBlueprintBox" style="margin-top: 14px; background: #070B16; border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; font-size: 11px; max-height: 260px; overflow-y: auto;">
                    <div style="color: #38BDF8; font-weight: 700; margin-bottom: 6px;">⏱️ 60-SECOND REEL TIMELINE:</div>
                    <div style="color: #EF4444; margin-bottom: 4px;"><b>0:00 - 0:05 [HOOK]:</b> <span id="bpTimelineHook">🚨 ९०% मुलं या HDFC बँक SQL प्रश्नात फेल होतात! क्युम्युलेटिव्ह बॅलन्स कसा काढायचा?</span></div>
                    <div style="color: #F59E0B; margin-bottom: 4px;"><b>0:05 - 0:18 [SCHEMA]:</b> <span id="bpTimelineSchema">Real bank customer transaction records</span></div>
                    <div style="color: #10B981; margin-bottom: 4px;"><b>0:18 - 0:42 [SQL &amp; ARROW]:</b> Animated Typing + Arrow pointing to <code id="bpArrowTarget" style="color:#38BDF8; background:rgba(56,189,248,0.1); padding:2px 4px; border-radius:4px;">PARTITION BY account_no</code></div>
                    <div style="color: #06B6D4; margin-bottom: 4px;"><b>0:42 - 0:54 [SIMULATION]:</b> Real-time output calculation rows highlight</div>
                    <div style="color: #8B5CF6; margin-bottom: 4px;"><b>0:54 - 1:00 [PRO TIP]:</b> Window functions avoid O(N²) subqueries!</div>
                </div>
            </div>

            <!-- COLUMN 2: 9:16 Smartphone Mockup Live Player (Trending UI) -->
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">
                    <span style="font-size: 12px; font-weight: 700; color: #38BDF8;">2. 9:16 SMARTPHONE PREVIEW</span>
                    <span id="playerTimer" style="font-size: 12px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 1:00</span>
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
                        <div style="font-size: 10px; color: #38BDF8; font-weight: 700; text-shadow: 0 1px 3px #000;">SQL 9:16 SHORT</div>
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
                    <input type="range" id="sqlShortScrubber" min="0" max="60" value="0" step="0.5" oninput="seekSqlShortPlayer(this.value)" style="width: 100%; accent-color: #38BDF8; cursor: pointer; margin-bottom: 8px;" />
                    
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

            <!-- COLUMN 3: In-Memory SQL Sandbox & Direct Video Download -->
            <div class="panel-card" style="margin: 0; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 12px; padding: 18px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <h3 style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 700;">3. LIVE SANDBOX &amp; 1-CLICK EXPORT</h3>
                    <span style="font-size: 11px; color: #10B981; background: rgba(16,185,129,0.1); padding: 2px 8px; border-radius: 6px;">SQLite &lt; 2ms</span>
                </div>

                <!-- SQL Query Editor Preview -->
                <label class="input-label" style="font-size: 12px; color: #94A3B8; font-weight: 600;">SQL Code In Video (Animated Neon Typing)</label>
                <textarea class="studio-input code-editor" id="sqlShortCodePreview" rows="7" style="width: 100%; font-family: monospace; font-size: 11px; background: #070B16; border: 1px solid #283C62; color: #38BDF8; margin-bottom: 10px; border-radius: 6px; padding: 8px;"></textarea>

                <!-- Sandbox Run Button -->
                <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                    <button type="button" class="btn btn-secondary" onclick="runInMemorySqlSandbox()" style="flex: 1; padding: 8px; font-size: 12px; font-weight: 600; border-color: #38BDF8; color: #38BDF8;">
                        ▶ Test Query in SQLite (&lt; 2ms)
                    </button>
                    <span id="sandboxLatency" style="font-size: 11px; color: #10B981; align-self: center; font-family: monospace;"></span>
                </div>

                <!-- Sandbox Output Table -->
                <div id="sandboxOutputTable" style="max-height: 140px; overflow-y: auto; background: #070B16; border: 1px solid #1E2D4A; border-radius: 6px; padding: 6px; font-size: 10px; font-family: monospace; color: #E2E8F0; margin-bottom: 16px;">
                    <div style="color: #64748B; text-align: center; padding: 12px;">Click [Test Query] to verify output on real bank rows...</div>
                </div>

                <!-- Direct Download Box (0 Server Load & 100% Zero-Watermark) -->
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 182, 212, 0.1)); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 12px; font-weight: 700; color: #10B981;">🎬 1-CLICK 9:16 VIDEO EXPORT</span>
                        <span style="font-size: 10px; background: rgba(236,72,153,0.2); color: #F472B6; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(236,72,153,0.4);">🛡️ 100% Zero-Watermark</span>
                    </div>
                    <div style="font-size: 11px; color: #94A3B8; margin-bottom: 12px;">Exports crisp 9:16 (1080x1920) WebM/MP4 directly from browser with <b>anti-watermark circular crop</b> and Tiranga educational banner. <b>Server CPU load: 0%</b>.</div>

                    <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 12px; font-weight: 800; background: linear-gradient(135deg, #10B981, #06B6D4); border: none; border-radius: 6px; cursor: pointer; color: #000; display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <span style="font-size: 16px;">📥</span>
                        <span id="exportBtnLabel">DOWNLOAD 9:16 VIDEO (CLEAN &amp; NO WATERMARK)</span>
                    </button>
                    
                    <div id="exportProgressBar" style="display:none; margin-top: 10px;">
                        <div style="height: 6px; width: 100%; background: #1E2D4A; border-radius: 3px; overflow: hidden;">
                            <div id="exportProgressFill" style="height: 100%; width: 0%; background: #10B981; transition: width 0.1s linear;"></div>
                        </div>
                        <div id="exportProgressText" style="font-size: 10px; color: #94A3B8; text-align: center; margin-top: 4px;">Rendering frames in high fidelity...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- END 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    '''
