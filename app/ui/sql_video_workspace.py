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
        grid-template-columns: minmax(320px, 1.15fr) 340px minmax(340px, 1.25fr);
        width: 100%;
        max-width: 100%;
        gap: 20px;
        align-items: start;
        box-sizing: border-box;
    }
    @media (max-width: 1220px) {
        .sql-studio-grid {
            grid-template-columns: minmax(300px, 1fr) 340px;
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
        cursor: default;
        overflow: hidden;
        word-break: break-word;
        box-sizing: border-box;
    }
    .agent-node .agent-badge {
        display: inline-block;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 8px;
        padding: 1px 4px;
        border-radius: 3px;
        box-sizing: border-box;
    }
    .agent-node.active {
        border-color: #38BDF8 !important;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(99, 102, 241, 0.2)) !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.5) !important;
        transform: translateY(-2px);
    }
    .agent-node.completed {
        border-color: #10B981 !important;
        background: rgba(16, 185, 129, 0.12) !important;
    }
    .agent-node.training {
        border-color: #A855F7 !important;
        background: rgba(168, 85, 247, 0.15) !important;
        animation: learnPulse 1.4s infinite;
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
                <span class="status-pill" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; font-size: 11px; padding: 4px 10px; border-radius: 20px;">📱 9:16 Vertical Reel (&lt;60s)</span>
                <span class="status-pill" style="background: rgba(139, 92, 246, 0.15); border: 1px solid #8B5CF6; color: #8B5CF6; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🔊 Regional AI Voice Live</span>
                <span class="status-pill" style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #F59E0B; font-size: 11px; padding: 4px 10px; border-radius: 20px;">🤖 Coding Intelligence Models Live</span>
            </div>
        </div>

        <!-- AUTONOMOUS MULTI-AGENT VIDEO PIPELINE (NANOPRO MASTER MANAGER ORCHESTRATION) -->
        <div class="agent-pipeline-container" id="agentPipelineContainer">
            <!-- Pipeline Header & Live Telemetry -->
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; border-bottom: 1px solid rgba(30, 45, 74, 0.8); padding-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">🤖</span>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;">
                            AUTONOMOUS MULTI-AGENT VIDEO PIPELINE (NANOPRO MASTER ORCHESTRATION)
                        </div>
                        <div style="font-size: 11px; color: #94A3B8;">
                            Prompt ➔ Decomposition ➔ Code Architecture ➔ Sandbox Verification ➔ Visual Retouch ➔ Neural Voice ➔ GitHub Learning ➔ 9:16 Deliverable
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                    <span id="pipelineMasterStatusBadge" style="font-size: 10px; background: rgba(16,185,129,0.15); border: 1.5px solid #10B981; color: #10B981; padding: 3px 8px; border-radius: 20px; font-weight: 700; display: flex; align-items: center; gap: 4px; white-space: nowrap;">
                        <span style="width: 7px; height: 7px; background: #10B981; border-radius: 50%; box-shadow: 0 0 8px #10B981; display: inline-block;"></span>
                        <span id="pipelineMasterStatusText">NanoPro Active</span>
                    </span>
                    <span id="pipelineGitHubModelBadge" onclick="openWeightsOptimizerModal()" style="cursor: pointer; font-size: 10px; background: rgba(168,85,247,0.15); border: 1.5px solid #A855F7; color: #C084FC; padding: 3px 8px; border-radius: 20px; font-weight: 700; display: flex; align-items: center; gap: 4px; white-space: nowrap; max-width: 100%;" title="View Live Synaptic Weights & AdamW Loss Convergence">
                        <span>🧠</span>
                        <span id="pipelineGitHubModelText">GitHub Model: Epoch #54 • Loss: 0.0363</span>
                    </span>
                    <button type="button" class="btn btn-secondary pipeline-btn" onclick="triggerModelTraining()" id="btnTrainModelNow" style="border-color: #10B981; color: #10B981; font-weight: 700; display: flex; align-items: center; gap: 4px;" title="Execute Live Backpropagation & Weight Tuning on GitHub Model">
                        <span>🚀</span> <span>Train Model</span>
                    </button>
                    <button type="button" class="btn btn-secondary pipeline-btn" onclick="openWeightsOptimizerModal()" style="border-color: #C084FC; color: #C084FC; font-weight: 700; display: flex; align-items: center; gap: 4px;" title="Open Weights Optimizer & AdamW Tuning Studio">
                        <span>⚡</span> <span>Weights Optimizer</span>
                    </button>
                    <button type="button" class="btn btn-secondary pipeline-btn" onclick="openElevenLabsModal()" style="border-color: #8B5CF6; color: #C4B5FD; font-weight: 700; display: flex; align-items: center; gap: 4px;" title="Open ElevenLabs Humanlike AI Voice Studio">
                        <span>🎙️</span> <span>ElevenLabs Voice</span>
                    </button>
                    <button type="button" class="btn btn-secondary pipeline-btn" onclick="openAgentBrainModal()" style="border-color: #38BDF8; color: #38BDF8; font-weight: 700; display: flex; align-items: center; gap: 4px;" title="View 12 Specialist Agents, Thoughts & Perfectionist Audit">
                        <span>🧠</span> <span>12 Agents Matrix</span>
                    </button>
                    <button type="button" class="btn btn-secondary pipeline-btn" onclick="toggleTelemetry()" style="border-color: #38BDF8; color: #38BDF8; font-weight: 700;" title="Toggle Telemetry Sidebar">
                        ◨ Toggle Sidebar
                    </button>
                </div>
            </div>

            <!-- 8 Interactive Pipeline Nodes & Laser Connectors -->
            <div class="agent-nodes-wrapper">
                <!-- Node 1: Prompt Box -->
                <div class="agent-node active" id="pnode-1" data-step="prompt">
                    <div style="font-size: 16px; margin-bottom: 2px;">📝</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">1. Prompt Box</div>
                    <div style="font-size: 9px; color: #94A3B8;">User Scenario</div>
                    <div class="agent-badge" style="font-size: 8px; color: #38BDF8; background: rgba(56,189,248,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">Input Domain</div>
                </div>

                <div class="agent-connector" id="pconn-1"></div>

                <!-- Node 2: NanoPro Manager -->
                <div class="agent-node" id="pnode-2" data-step="manager">
                    <div style="font-size: 16px; margin-bottom: 2px;">🤖</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">2. NanoPro Agent</div>
                    <div style="font-size: 9px; color: #94A3B8;">Orchestration</div>
                    <div class="agent-badge" style="font-size: 8px; color: #10B981; background: rgba(16,185,129,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">Master Controller</div>
                </div>

                <div class="agent-connector" id="pconn-2"></div>

                <!-- Node 3: Developing (Coding & Architecture) -->
                <div class="agent-node" id="pnode-3" data-step="coding">
                    <div style="font-size: 16px; margin-bottom: 2px;">💻</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">3. Developing</div>
                    <div style="font-size: 9px; color: #94A3B8;">Code &amp; Schema</div>
                    <div class="agent-badge" style="font-size: 8px; color: #F59E0B; background: rgba(245,158,11,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">Groq / Gemini</div>
                </div>

                <div class="agent-connector" id="pconn-3"></div>

                <!-- Node 4: Modification & Verification Sandbox -->
                <div class="agent-node" id="pnode-4" data-step="verification">
                    <div style="font-size: 16px; margin-bottom: 2px;">🧪</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">4. Modification</div>
                    <div style="font-size: 9px; color: #94A3B8;">AST &amp; Logic Check</div>
                    <div class="agent-badge" style="font-size: 8px; color: #06B6D4; background: rgba(6,182,212,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">SQLite AST Sandbox</div>
                </div>

                <div class="agent-connector" id="pconn-4"></div>

                <!-- Node 5: Retouch (Visual Motion & Layout) -->
                <div class="agent-node" id="pnode-5" data-step="retouch">
                    <div style="font-size: 16px; margin-bottom: 2px;">🎨</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">5. Retouch</div>
                    <div style="font-size: 9px; color: #94A3B8;">9:16 Canvas &amp; Neon</div>
                    <div class="agent-badge" style="font-size: 8px; color: #EC4899; background: rgba(236,72,153,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">Runway / Cyber Glass</div>
                </div>

                <div class="agent-connector" id="pconn-5"></div>

                <!-- Node 6: Final Audio & Subtitle -->
                <div class="agent-node" id="pnode-6" data-step="voice" onclick="openElevenLabsModal()" style="cursor: pointer;" title="Configure ElevenLabs Voice AI, Indian Male Tech YouTuber & Regional Voice Models">
                    <div style="font-size: 16px; margin-bottom: 2px;">🎙️</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">6. Voice &amp; Subtitle</div>
                    <div style="font-size: 9px; color: #94A3B8;">Synced Voiceover</div>
                    <div class="agent-badge" style="font-size: 8px; color: #8B5CF6; background: rgba(139,92,246,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">ElevenLabs / Edge</div>
                </div>

                <div class="agent-connector" id="pconn-6"></div>

                <!-- Node 7: GitHub Self-Learning Model -->
                <div class="agent-node" id="pnode-7" data-step="learning" onclick="openWeightsOptimizerModal()" style="cursor: pointer;" title="Open GitHub Continuous Learning & Synaptic Weights Optimizer">
                    <div style="font-size: 16px; margin-bottom: 2px;">🧠</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">7. GitHub Model</div>
                    <div style="font-size: 9px; color: #94A3B8;">Continuous Learning</div>
                    <div class="agent-badge" style="font-size: 8px; color: #A855F7; background: rgba(168,85,247,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">Weights Optimizer</div>
                </div>

                <div class="agent-connector" id="pconn-7"></div>

                <!-- Node 8: Final Result Deliverable -->
                <div class="agent-node" id="pnode-8" data-step="result">
                    <div style="font-size: 16px; margin-bottom: 2px;">🎬</div>
                    <div style="font-size: 11px; font-weight: 700; color: #F8FAFC;">8. Final Result</div>
                    <div style="font-size: 9px; color: #94A3B8;">1-Click 9:16 Video</div>
                    <div class="agent-badge" style="font-size: 8px; color: #10B981; background: rgba(16,185,129,0.15); border-radius: 3px; padding: 1px 4px; margin-top: 4px; display: inline-block;">1080x1920 (&lt;60s)</div>
                </div>
            </div>

            <!-- Live Multi-Agent Execution & Learning Console Ticker -->
            <div style="margin-top: 10px; background: #050811; border: 1px solid #1E293B; border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0;">
                    <span style="font-size: 13px; color: #38BDF8;">⚡</span>
                    <div id="pipelineLiveLogTicker" style="font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; color: #94A3B8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        [NanoPro Manager] Master Orchestrator ready. All 12 specialized AI agents &amp; GitHub self-learning weights active.
                    </div>
                    <span onclick="openAgentBrainModal()" style="font-size: 10px; color: #38BDF8; cursor: pointer; text-decoration: underline; white-space: nowrap;" title="Click to view full agent thoughts and perfectionist audit">[🔍 View 12 Agent Thoughts &amp; Audit]</span>
                </div>
                <div style="display: flex; gap: 6px; flex-shrink: 0;">
                    <span id="pipelineEpochPill" style="font-size: 10px; color: #C084FC; font-family: monospace; background: rgba(168,85,247,0.1); border: 1px solid rgba(168,85,247,0.3); padding: 2px 6px; border-radius: 4px;">Epoch #53</span>
                    <span id="pipelineLossPill" style="font-size: 10px; color: #10B981; font-family: monospace; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); padding: 2px 6px; border-radius: 4px;">Loss: 0.0372</span>
                </div>
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

                <!-- Creation Mode Selector (FAANG Drill, 3D Architecture, Viral 60s Reel, Deep Mentor) -->
                <div style="margin-bottom: 12px; background: rgba(15, 23, 42, 0.8); border: 1px solid #1E2D4A; border-radius: 8px; padding: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 11px; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.5px;">
                            🎯 Creation Mode (व्हिडिओ निर्मिती प्रकार):
                        </span>
                        <span id="activeCreationModeBadge" style="font-size: 10px; color: #10B981; font-weight: 700; background: rgba(16,185,129,0.15); padding: 2px 6px; border-radius: 4px;">
                            🏢 FAANG Interview Drill
                        </span>
                    </div>
                    <input type="hidden" id="sqlShortCreationMode" value="faang_drill" />
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px;">
                        <button type="button" class="sql-mode-btn active" id="btnModeFaang" onclick="setSqlCreationMode('faang_drill')">
                            <span class="btn-check">✓</span> <span>🏢 FAANG Drill (Code/SQL)</span>
                        </button>
                        <button type="button" class="sql-mode-btn" id="btnModeArch" onclick="setSqlCreationMode('architecture_3d')">
                            <span class="btn-check">✓</span> <span>🌐 3D Cloud Architecture</span>
                        </button>
                        <button type="button" class="sql-mode-btn" id="btnModeViral" onclick="setSqlCreationMode('viral_reel')">
                            <span class="btn-check">✓</span> <span>⚡ Viral 60s Tech Reel</span>
                        </button>
                        <button type="button" class="sql-mode-btn" id="btnModeMentor" onclick="setSqlCreationMode('deep_mentor')">
                            <span class="btn-check">✓</span> <span>👨‍🏫 Deep Academic Mentor</span>
                        </button>
                    </div>
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

                <!-- Quick Domain Scenario Preset Chips (1-Click Test Scenarios) -->
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 10px; color: #94A3B8; display: block; margin-bottom: 4px;">⚡ <b>क्लिक करून थेट सुरू करा (Trending 1-Click Tech Prompts):</b></span>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('sql')" style="font-size: 10px; padding: 3px 8px; border-color: #38BDF8; color: #38BDF8; font-weight:600;">
                            ⚡ SQL: DENSE_RANK &amp; Ties
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('snowflake')" style="font-size: 10px; padding: 3px 8px; border-color: #06B6D4; color: #06B6D4; font-weight:600;">
                            ⚡ Snowflake: QUALIFY &amp; Snowpipe
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('python')" style="font-size: 10px; padding: 3px 8px; border-color: #10B981; color: #10B981; font-weight:600;">
                            ⚡ Python: Asyncio Event Loop
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('aws')" style="font-size: 10px; padding: 3px 8px; border-color: #F59E0B; color: #F59E0B; font-weight:600;">
                            ⚡ AWS: S3 to Redshift Data Lake
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('de')" style="font-size: 10px; padding: 3px 8px; border-color: #8B5CF6; color: #8B5CF6; font-weight:600;">
                            ⚡ Data Eng: Medallion Architecture
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('rag')" style="font-size: 10px; padding: 3px 8px; border-color: #EC4899; color: #EC4899; font-weight:600;">
                            ⚡ AI/RAG: Vector Search Embeddings
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('docker')" style="font-size: 10px; padding: 3px 8px; border-color: #38BDF8; color: #38BDF8; font-weight:600;">
                            ⚡ Docker: Multi-Stage Build
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="insertPromptScenario('git')" style="font-size: 10px; padding: 3px 8px; border-color: #10B981; color: #10B981; font-weight:600;">
                            ⚡ Git: Rebase vs Merge
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
                    <div style="font-size: 11px; font-weight: 700; color: #38BDF8; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; display:flex; justify-content:space-between; align-items:center;">
                        <span>🎙️ Voiceover Audio &amp; Subtitle Controls</span>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span id="activeVoiceBadge" style="color:#10B981; font-weight:700;">मराठी शिक्षक</span>
                            <button type="button" class="btn btn-secondary" id="btnOpenElevenLabs" onclick="openElevenLabsModal()" style="font-size: 10px; padding: 2px 8px; border-color: #8B5CF6; color: #C4B5FD; font-weight: 700; display: flex; align-items: center; gap: 4px;" title="ElevenLabs AI Voice Studio">
                                <span>⚡ ElevenLabs AI Studio</span>
                            </button>
                        </div>
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
                        <button type="button" class="sql-avatar-btn active" id="btnBgCyber" onclick="setSqlMotionEngine(false); document.getElementById('sqlCinematicBgSelect').value='cyber_matrix'; this.classList.add('active'); document.getElementById('btnBg3D').classList.remove('active');">
                            <span class="btn-check">✓</span> <span>🌐 Transparent Cyber Glass</span>
                        </button>
                        <button type="button" class="sql-avatar-btn" id="btnBg3D" onclick="setSqlMotionEngine(true); document.getElementById('sqlCinematicBgSelect').value='runway_cloud'; this.classList.add('active'); document.getElementById('btnBgCyber').classList.remove('active');">
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
                        1080x1920 फुल-एचडी रेंडरिंग सोबत नॅचरल AI शिक्षक ऑडिओ इंटिग्रेटेड (&lt;६० से.)! कोपऱ्यातील वॉटरमार्क 100% रिमूव्ह केले जातात.
                    </div>

                    <!-- Direct Download Button Group -->
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 12px 10px; font-weight: 900; font-size: 12px; letter-spacing: 0.3px; background: linear-gradient(135deg, #10B981, #06B6D4); border: none; border-radius: 8px; cursor: pointer; color: #000; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 15px rgba(16,185,129,0.35); white-space: normal; line-height: 1.3; text-align: center; word-break: break-word; box-sizing: border-box;">
                            <span style="font-size: 18px; flex-shrink: 0;">📥</span>
                            <span id="exportBtnLabel">DOWNLOAD 9:16 REEL (&lt;60s) (VOICE SYNCED)</span>
                        </button>

                        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                            <button type="button" class="btn btn-secondary" onclick="exportSqlShortVideo(15)" style="flex: 1 1 90px; padding: 7px 4px; font-size: 10.5px; font-weight: 700; border-color: #38BDF8; color: #38BDF8; white-space: normal; line-height: 1.2; text-align: center; word-break: break-word; min-width: 0;" title="15-sec quick test video with audio">
                                ⚡ Quick 15s
                            </button>
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
                            <div style="color: #10B981; font-weight: 700;">✓ Trial 2: Speech Pacing &amp; Duration Limit</div>
                            <div style="color: #94A3B8; font-size: 10px;">Word count dynamically calibrated (100-120 words), strictly within &lt;60s Shorts window</div>
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

    <!-- GITHUB MODEL CONTINUOUS LEARNING & SYNAPTIC WEIGHTS OPTIMIZER MODAL -->
    <div id="weightsOptimizerModal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(10px); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
        <div style="background: #090E1D; border: 2px solid #A855F7; border-radius: 14px; width: 100%; max-width: 920px; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 50px rgba(0,0,0,0.85), 0 0 35px rgba(168,85,247,0.35);">
            <!-- Modal Header -->
            <div style="background: linear-gradient(135deg, rgba(168,85,247,0.25), rgba(99,102,241,0.25)); border-bottom: 1.5px solid #1E2D4A; padding: 16px 22px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 26px;">🧠</span>
                    <div>
                        <h3 style="margin: 0; font-size: 16px; color: #C084FC; font-weight: 800; letter-spacing: 0.5px;">GITHUB MODEL: CONTINUOUS LEARNING &amp; SYNAPTIC WEIGHTS OPTIMIZER</h3>
                        <div style="font-size: 11px; color: #94A3B8;">AdamW Neural Optimization • Active Reinforcement Tuning • Prompt-Guided Domain Calibration</div>
                    </div>
                </div>
                <button type="button" onclick="closeWeightsOptimizerModal()" style="background: #1E293B; border: 1px solid #334155; color: #F8FAFC; border-radius: 6px; padding: 6px 14px; cursor: pointer; font-size: 13px; font-weight: 700;">✕ Close</button>
            </div>

            <!-- Modal Content (Scrollable) -->
            <div style="padding: 20px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 16px;">
                <!-- Live Telemetry Stats Bar -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                    <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Current Epoch</div>
                        <div id="modalOptimizerEpoch" style="font-size: 18px; font-weight: 800; color: #C084FC; font-family: monospace;">Epoch #54</div>
                    </div>
                    <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Convergence Loss</div>
                        <div id="modalOptimizerLoss" style="font-size: 18px; font-weight: 800; color: #10B981; font-family: monospace;">0.0363</div>
                    </div>
                    <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Knowledge Vectors</div>
                        <div id="modalOptimizerVectors" style="font-size: 18px; font-weight: 800; color: #38BDF8; font-family: monospace;">196 Vectors</div>
                    </div>
                    <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center;">
                        <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Optimizer Engine</div>
                        <div style="font-size: 15px; font-weight: 800; color: #F59E0B;">AdamW (lr=5e-4)</div>
                    </div>
                </div>

                <!-- 6 Dynamic Synaptic Weights Breakdown -->
                <div style="background: rgba(168,85,247,0.06); border: 1.5px solid rgba(168,85,247,0.3); border-radius: 10px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 13px; font-weight: 800; color: #C084FC;">⚡ 6 ACTIVE SYNAPTIC WEIGHTS (DYNAMIC PROMPT STEERING)</span>
                        <span style="font-size: 11px; color: #10B981; background: rgba(16,185,129,0.15); padding: 2px 8px; border-radius: 6px;">Live Model Injected</span>
                    </div>
                    <div id="modalSynapticWeightsList" style="display: flex; flex-direction: column; gap: 10px;">
                        <!-- Weights rows populated dynamically -->
                    </div>
                </div>

                <!-- Multi-Objective Loss Function Ledger -->
                <div style="background: #070B16; border: 1px solid #1E293B; border-radius: 10px; padding: 14px;">
                    <div style="font-size: 12px; font-weight: 700; color: #38BDF8; margin-bottom: 8px;">
                        📐 Multi-Objective Loss Backpropagation: L = w_time · L_time + w_pace · L_pace + w_syntax · L_syntax + w_density · L_density
                    </div>
                    <div style="font-size: 11px; color: #94A3B8; line-height: 1.5;">
                        Whenever you type a prompt or generate a video, this neural model automatically evaluates the output duration, pacing variance from &lt;60s standard, AST syntax validity, and scene density. Gradients are computed with weight decay and momentum vectors (m, v) to guarantee each next video is smarter, tighter, and more engaging than the last.
                    </div>
                </div>

                <!-- Interactive Train Step Action Button -->
                <div style="display: flex; gap: 10px; justify-content: flex-end; align-items: center; border-top: 1px solid #1E2D4A; padding-top: 12px;">
                    <span id="modalTrainStepStatus" style="font-size: 11px; color: #94A3B8; font-family: monospace;"></span>
                    <button type="button" class="btn btn-primary" onclick="runWeightsOptimizationStep()" id="btnModalTrainStep" style="padding: 10px 20px; font-weight: 800; font-size: 12px; background: linear-gradient(135deg, #A855F7, #6366F1); color: #FFF; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(168,85,247,0.4);">
                        <span>⚡ Run AdamW Weight Optimization Step Now</span>
                    </button>
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
    <!-- END 9:16 SQL SHORT & REEL STUDIO UPGRADE -->
    '''
