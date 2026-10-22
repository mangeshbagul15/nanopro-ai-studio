"""
Mangesh Nano Pro AI Studio - Upgraded Workspace Views
Contains:
- Single AI Manager Symbol Component
- AI Manager Conversation & Response Stream (Tables, Charts, Animated Output)
- Animated 3D AI Agent Office (All 305 registered agents, live truthful states)
- Nano Pro Voice Assistant ("Hi NanoPro", wake-word, unified context)
- Task Scheduler & Automation Center (Windows Task Scheduler Alternative)
- News Center (ABP Majha & Aaj Tak, hourly check, dual-language, floating alert)
- Entertainment & Modern Lifestyle Center (Multimedia, Music, Fashion, YouTube)
- Book Reader & Intelligent Learning Assistant (PDF/DOCX/TXT reader, quizzes, Marathi explanations)
"""

AI_MANAGER_SYMBOL_HTML = r"""
<div id="aiManagerSymbolWrapper" class="ai-manager-symbol-container state-ready" onclick="toggleVoiceOrManagerPrompt()" title="AI Manager — Click to Speak or Activate">
    <div class="manager-core-orb" id="managerCoreOrb">
        <div class="orb-inner"></div>
        <div class="orb-ring ring-1"></div>
        <div class="orb-ring ring-2"></div>
        <div class="orb-status-glow" id="orbStatusGlow"></div>
    </div>
    <div class="manager-symbol-label">
        <span class="symbol-name">AI MANAGER</span>
        <span class="symbol-state" id="managerStateText">READY</span>
    </div>
</div>
"""

AI_MANAGER_VIEW_HTML = r"""
<div class="workspace-view active" id="view-ai_manager">
    <!-- Manager Status & Capability Bar -->
    <div class="panel-card" style="margin-bottom:12px; padding:12px 18px;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:50%; background:radial-gradient(circle, #38BDF8 20%, #1E1B4B 90%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 12px rgba(56,189,248,0.4);">
                    &#129302;
                </div>
                <div>
                    <h2 style="margin:0; font-size:15px; color:#F8FAFC;">Central AI Manager &amp; Response Stream</h2>
                    <span style="font-size:11.5px; color:var(--text-muted);">Personal Operating Center • Multilingual (English, मराठी, Hinglish) • Context-Aware Coordination</span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span class="badge" style="background:#0F172A; border:1px solid #38BDF8; color:#38BDF8; font-size:11px; padding:4px 10px;">305 SPECIALISTS ACTIVE</span>
                <button type="button" class="btn btn-secondary" onclick="clearManagerConversation()" style="font-size:11px; padding:4px 10px;">&#128465; Clear Chat</button>
                <button type="button" class="btn btn-secondary" onclick="exportChatTranscript()" style="font-size:11px; padding:4px 10px;">&#128190; Export Chat</button>
                <button type="button" class="btn btn-accent" onclick="switchView('approvals')" style="font-size:11px; padding:4px 10px;">Approval Queue</button>
                <button type="button" class="btn btn-accent" onclick="switchView('vault')" style="font-size:11px; padding:4px 10px;">Credentials Vault</button>
            </div>
        </div>
    </div>

    <!-- Central Conversation Stream Container -->
    <div class="manager-chat-container">
        <!-- Live Message Stream -->
        <div class="chat-stream-box" id="managerChatStreamBox">
            <!-- Initial Welcome Message from Manager -->
            <div class="chat-msg manager">
                <div class="msg-avatar">&#129302;</div>
                <div class="msg-bubble">
                    <strong>Hello Mangesh! I am your Nano Pro AI Manager.</strong><br/>
                    I lead your team of 205 specialist AI agents across Data Engineering (Oracle XE, S3, Snowflake, AWS DMS), Python/SQL Automation, Career Radar, News, Document Reading, and Modern Lifestyle.<br/><br/>
                    You can speak or type naturally in <strong>English</strong>, <strong>मराठी</strong>, or <strong>Hinglish</strong>. How can I assist your operations today?
                    <div class="msg-tools">
                        <button type="button" class="msg-tool-btn" onclick="speakText('Hello Mangesh, I am your Nano Pro AI Manager. How can I assist your operations today?')">&#127908; Read Aloud</button>
                    </div>
                    <div class="msg-meta">
                        <span>Nano Pro Operating Center • Ready</span>
                        <span>Just now</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Follow-up & Recommendation Action Chips -->
        <div class="quick-prompt-chips-bar" id="managerQuickChipsBar">
            <span class="action-chip" onclick="quickFillPrompt('Connect these two tables and show me customer balances.')">&#128452; "Connect tables &amp; show customer balances"</span>
            <span class="action-chip" onclick="quickFillPrompt('Explain this in simple language.')">&#128161; "Explain in simple language"</span>
            <span class="action-chip" onclick="quickFillPrompt('Make a graph.')">&#128202; "Make a graph"</span>
            <span class="action-chip" onclick="quickFillPrompt('Check live news from ABP Majha and Aaj Tak.')">&#128240; "Check live news"</span>
            <span class="action-chip" onclick="quickFillPrompt('Show active automation tasks in Task Scheduler.')">&#9200; "Task Scheduler status"</span>
            <span class="action-chip" onclick="quickFillPrompt('Explain my uploaded book in Marathi.')">&#128218; "Explain book in Marathi"</span>
        </div>

        <!-- Compact Interactive Message Composer -->
        <div class="chat-composer-box">
            <button type="button" class="btn btn-secondary" id="chatAttachBtn" onclick="triggerChatAttachment()" title="Attach CSV, Excel, TXT, or PDF" style="padding:10px 12px;">&#128206;</button>
            <input type="file" id="chatFileInputHidden" style="display:none;" onchange="handleChatFileUpload(event)" />
            <textarea class="chat-composer-input" id="managerChatInput" placeholder="Ask Manager: 'Connect tables and show customer balances', 'Make a graph', or 'Task Scheduler status'..." rows="1" onkeydown="handleChatKeydown(event)"></textarea>
            <button type="button" class="btn btn-secondary" id="chatMicBtn" onclick="toggleVoiceRecording()" title="Voice Input" style="padding:10px 14px;">&#127908;</button>
            <button type="button" class="btn btn-primary" id="chatSendBtn" onclick="sendManagerMessage()" style="padding:10px 18px;">&#9658; Send</button>
            <button type="button" class="btn btn-secondary" id="chatStopBtn" onclick="stopManagerGeneration()" style="display:none; padding:10px 14px; background:#EF4444; color:#FFF;" title="Stop Generation">&#9209; Stop</button>
        </div>
    </div>
</div>
"""

AI_OFFICE_VIEW_HTML = r"""
<div class="workspace-view" id="view-ai_office">
    <div class="panel-card" style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h2>Animated AI Agent Office — Living 3D Workspace</h2>
                <p style="font-size:12px; color:var(--text-muted); margin:0;">
                    Visualizes all 205 registered specialist agents across 13 divisions, active workstations, real task progress, and live data pipeline flows.
                </p>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <input type="text" class="studio-input" id="officeSearchAgentInput" placeholder="Search 205 agents..." oninput="filterOfficeAgents(this.value)" style="width:180px; padding:5px 10px; font-size:11.5px;" />
                <select class="studio-input" id="officePodFilter" onchange="filterOfficePod(this.value)" style="padding:5px 10px; font-size:11.5px;">
                    <option value="all">All 13 Pods (205 Agents)</option>
                    <option value="A">Group A: Core Cognitive &amp; Orchestration (5)</option>
                    <option value="B">Group B: Data Engineering &amp; Pipeline Fabric (20)</option>
                    <option value="C">Group C: Snowflake &amp; Oracle Specialized Engine (20)</option>
                    <option value="D">Group D: Data Quality, Governance &amp; Catalog (15)</option>
                    <option value="E">Group E: AWS Database Migration Service (DMS) (15)</option>
                    <option value="F">Group F: Enterprise Analytics &amp; BI (20)</option>
                    <option value="G">Group G: Autonomous AI/MLOps &amp; Deep Learning (20)</option>
                    <option value="H">Group H: Cyber Defense &amp; Vault Security (15)</option>
                    <option value="I">Group I: SRE &amp; Infrastructure Resiliency (15)</option>
                    <option value="J">Group J: Career Radar &amp; MNC HR Outreach (20)</option>
                    <option value="K">Group K: Communication Center (15)</option>
                    <option value="L">Group L: Automated Schedulers &amp; CRON (15)</option>
                    <option value="M">Group M: Lifestyle &amp; Live News (10)</option>
                </select>
                <button type="button" class="btn btn-secondary" onclick="refreshOfficeLiveState()" style="font-size:11px; padding:5px 10px;">&#128257; Refresh State</button>
            </div>
        </div>
    </div>

    <!-- 3D Office Environment Viewport -->
    <div class="office-3d-viewport">
        <!-- Central Manager Hologram Desk -->
        <div class="manager-central-desk">
            <div class="desk-hologram-core">
                <div class="hologram-avatar">&#129302;</div>
                <div>
                    <div style="font-size:14px; font-weight:800; color:#F8FAFC;">CENTRAL AI MANAGER DESK</div>
                    <div style="font-size:11.5px; color:#38BDF8;">Orchestrating 205 Specialist Agents • Single Intelligent Entry Point</div>
                </div>
            </div>
            <div style="display:flex; gap:12px; align-items:center;">
                <div style="text-align:right;">
                    <div style="font-size:10.5px; color:var(--text-muted); text-transform:uppercase;">Current Office Mode</div>
                    <div style="font-size:12px; font-weight:700; color:#10B981;" id="officeModeText">&#9679; Autonomous Operations Ready</div>
                </div>
                <button type="button" class="btn btn-primary" onclick="switchView('ai_manager')" style="font-size:11px; padding:6px 12px;">Talk to Manager &rarr;</button>
            </div>
        </div>

        <!-- Live Data Flow Animation Container -->
        <div id="officeDataFlowBanner" style="display:none; background:rgba(30,58,138,0.3); border:1px solid #38BDF8; border-radius:6px; padding:8px 12px; margin:14px 0; font-size:11.5px; color:#38BDF8; align-items:center; gap:8px;">
            <span style="animation:pulseListen 1s infinite;">&#9889;</span>
            <span id="officeDataFlowText">Manager Agent &rarr; Snowflake Agent &rarr; Visualization Agent</span>
        </div>

        <!-- Workstations Floor Grid (Populated dynamically from 45 registered agents) -->
        <div class="office-floor-grid" id="officeAgentsGridContainer" style="margin-top:16px;">
            <!-- Rendered dynamically -->
        </div>
    </div>
</div>
"""

VOICE_ASSISTANT_VIEW_HTML = r"""
<div class="workspace-view" id="view-voice_assistant">
    <div class="panel-card" style="text-align:center; max-width:820px; margin:0 auto;">
        <h2>Nano Pro Voice Operating Station</h2>
        <p style="font-size:12.5px; color:var(--text-muted); max-width:680px; margin:0 auto 16px auto;">
            Speak naturally in <strong>मराठी (Marathi)</strong>, <strong>हिंदी (Hindi)</strong>, or <strong>English</strong>. Say <em>"Hi NanoPro"</em> to activate or click the central AI Manager Symbol below.
        </p>

        <!-- Central AI Manager Voice Symbol -->
        <div style="margin:24px 0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div id="bigVoiceOrb" class="ai-manager-symbol-container state-ready" onclick="toggleVoiceRecording()" style="padding:14px 28px; border-radius:40px; transform:scale(1.2);">
                <div class="manager-core-orb" style="width:36px; height:36px;">
                    <div class="orb-inner" style="width:18px; height:18px;"></div>
                    <div class="orb-ring ring-1" style="width:30px; height:30px;"></div>
                    <div class="orb-ring ring-2" style="width:36px; height:36px;"></div>
                </div>
                <div class="manager-symbol-label">
                    <span class="symbol-name" style="font-size:13px;">AI MANAGER</span>
                    <span class="symbol-state" id="bigVoiceState" style="font-size:10px;">CLICK TO SPEAK</span>
                </div>
            </div>
            <div id="voiceFeedbackText" style="font-size:13px; color:#F8FAFC; margin-top:20px; font-weight:600;">
                Click Symbol or Say "Hi NanoPro" to Begin Speaking
            </div>
        </div>

        <!-- Voice Settings & Privacy Controls -->
        <div style="display:flex; flex-wrap:wrap; gap:12px; justify-content:center; align-items:center; background:#11192E; padding:12px 16px; border-radius:8px; border:1px solid #263354; margin-top:14px;">
            <div>
                <label style="font-size:11px; color:var(--text-muted); display:block; text-align:left;">Language Mode:</label>
                <select id="voiceLanguageSelect" class="studio-input" style="padding:5px 8px; font-size:12px;" onchange="onVoiceLanguageChanged()">
                    <option value="mr-IN" selected>मराठी (Marathi - mr-IN)</option>
                    <option value="hi-IN">हिंदी (Hindi - hi-IN)</option>
                    <option value="en-IN">Indian English (en-IN)</option>
                    <option value="en-US">US English (en-US)</option>
                </select>
            </div>
            <div>
                <label style="font-size:11px; color:var(--text-muted); display:block; text-align:left;">Wake-Word Detection:</label>
                <button type="button" id="btnWakeWordToggle" class="btn btn-secondary" onclick="toggleWakeWordListener()" style="font-size:11px; padding:5px 10px;">
                    &#127908; Wake-Word: DISABLED
                </button>
            </div>
            <div style="display:flex; gap:6px; align-items:flex-end;">
                <button type="button" class="btn btn-secondary" onclick="stopSpeaking()" style="font-size:11px; padding:6px 12px; background:#EF4444; color:#FFF;">&#9209; Stop Speaking</button>
                <button type="button" class="btn btn-secondary" onclick="switchView('ai_manager')" style="font-size:11px; padding:6px 12px;">Open Conversation Stream</button>
            </div>
        </div>

        <!-- Spoken Quick Prompts -->
        <div style="margin-top:16px; display:flex; flex-wrap:wrap; gap:6px; justify-content:center;">
            <span class="action-chip" onclick="simulateVoicePrompt('Connect customer and account tables and show customer balances')">&#128483; "Customer balances dakhva"</span>
            <span class="action-chip" onclick="simulateVoicePrompt('Explain this result in simple language')">&#128483; "Sopya bhashet samjav"</span>
            <span class="action-chip" onclick="simulateVoicePrompt('Make a graph of customer balances')">&#128483; "Make a graph"</span>
            <span class="action-chip" onclick="simulateVoicePrompt('Check live news from ABP Majha and Aaj Tak')">&#128483; "Latest news sang"</span>
        </div>
    </div>
</div>
"""

TASK_SCHEDULER_VIEW_HTML = r"""
<div class="workspace-view" id="view-automation_scheduler">
    <!-- Header with Quick Action -->
    <div class="panel-card" style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h2>Task Scheduler &amp; Automation Center</h2>
                <p style="font-size:12px; color:var(--text-muted); margin:0;">
                    Windows Task Scheduler Alternative — Create, schedule, monitor, pause, and execute Python scripts, SQL queries, Batch files (.bat), and PowerShell jobs.
                </p>
            </div>
            <div style="display:flex; gap:8px;">
                <button type="button" class="btn btn-primary" onclick="openTaskCreationModal()">+ Create New Task</button>
                <button type="button" class="btn btn-secondary" onclick="refreshSchedulerDashboard()">&#128257; Refresh</button>
            </div>
        </div>
    </div>

    <!-- Health Metrics Bar -->
    <div class="scheduler-metrics-bar" id="schedMetricsBar">
        <div class="metric-box-sched">
            <div style="font-size:10.5px; color:var(--text-muted); font-weight:700;">TOTAL TASKS</div>
            <div style="font-size:20px; font-weight:800; color:#38BDF8;" id="schedStatTotal">-</div>
        </div>
        <div class="metric-box-sched">
            <div style="font-size:10.5px; color:var(--text-muted); font-weight:700;">ENABLED / ACTIVE</div>
            <div style="font-size:20px; font-weight:800; color:#10B981;" id="schedStatEnabled">-</div>
        </div>
        <div class="metric-box-sched">
            <div style="font-size:10.5px; color:var(--text-muted); font-weight:700;">PAUSED</div>
            <div style="font-size:20px; font-weight:800; color:#F59E0B;" id="schedStatPaused">-</div>
        </div>
        <div class="metric-box-sched">
            <div style="font-size:10.5px; color:var(--text-muted); font-weight:700;">RUNNING NOW</div>
            <div style="font-size:20px; font-weight:800; color:#EC4899;" id="schedStatRunning">0</div>
        </div>
        <div class="metric-box-sched">
            <div style="font-size:10.5px; color:var(--text-muted); font-weight:700;">SUCCESSFUL RUNS</div>
            <div style="font-size:20px; font-weight:800; color:#10B981;" id="schedStatSuccess">-</div>
        </div>
        <div class="metric-box-sched">
            <div style="font-size:10.5px; color:var(--text-muted); font-weight:700;">FAILED RUNS</div>
            <div style="font-size:20px; font-weight:800; color:#EF4444;" id="schedStatFailed">0</div>
        </div>
    </div>

    <!-- Task Creation & Configuration Card -->
    <div class="panel-card" id="taskCreationCard" style="display:none; margin-bottom:14px; border-color:#38BDF8;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h3 style="margin:0; font-size:14px; color:#F8FAFC;" id="schedFormTitle">Create New Scheduled Automation Task</h3>
            <button type="button" class="btn btn-secondary" onclick="closeTaskCreationModal()" style="font-size:11px; padding:2px 8px;">✕ Close</button>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div>
                <label class="input-label">Task Name *</label>
                <input type="text" class="studio-input" id="schedFormName" placeholder="e.g. Daily Snowflake Bank Reconciliation" />
            </div>
            <div>
                <label class="input-label">Task Type *</label>
                <select class="studio-input" id="schedFormType" onchange="onTaskTypeChange(this.value)">
                    <option value="python">Python Script (.py)</option>
                    <option value="sql">SQL Query / Script (.sql)</option>
                    <option value="bat">Windows Batch Script (.bat)</option>
                    <option value="powershell">PowerShell Script (.ps1)</option>
                    <option value="scheduled_job">Studio App Maintenance Job</option>
                </select>
            </div>
        </div>

        <div style="margin-top:10px;">
            <label class="input-label">Description</label>
            <input type="text" class="studio-input" id="schedFormDesc" placeholder="e.g. Automated daily check of transaction staging buffer" />
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:10px;">
            <div>
                <label class="input-label">Schedule Frequency *</label>
                <select class="studio-input" id="schedFormScheduleType">
                    <option value="daily">Daily at Fixed Time</option>
                    <option value="hourly">Hourly</option>
                    <option value="minutes">Every X Minutes</option>
                    <option value="weekly">Weekly on Selected Day</option>
                    <option value="fortnightly">Every 14 Days</option>
                    <option value="monthly">Monthly</option>
                    <option value="once">Run Once</option>
                    <option value="cron">Custom Cron Expression</option>
                </select>
            </div>
            <div>
                <label class="input-label">Recurrence Parameter (e.g. 08:00, 15, MON@09:00, or Cron)</label>
                <input type="text" class="studio-input" id="schedFormRecurrence" placeholder="08:00" />
            </div>
        </div>

        <div id="schedSqlDbRow" style="margin-top:10px; display:none;">
            <label class="input-label">Target Database Connection</label>
            <select class="studio-input" id="schedFormDbConn">
                <option value="NANO_PRO_SNOWFLAKE">NANO_PRO_SNOWFLAKE (BANK_DB.L0_STAGING)</option>
                <option value="MY_ORACLE_XE_REMOTE">MY_ORACLE_XE_REMOTE (192.168.31.240/XEPDB1)</option>
                <option value="STUDIO_MEMORY_DB">STUDIO_MEMORY_DB (SQLite Internal Ledger)</option>
            </select>
        </div>

        <div style="margin-top:10px;">
            <label class="input-label">Script / Query Code or Local File Path</label>
            <textarea class="studio-input" id="schedFormContent" rows="4" placeholder="Enter Python script, SQL query, or Batch commands here..."></textarea>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:14px;">
            <button type="button" class="btn btn-secondary" onclick="closeTaskCreationModal()">Cancel</button>
            <button type="button" class="btn btn-primary" onclick="submitTaskCreationForm()">Save &amp; Schedule Task</button>
        </div>
    </div>

    <!-- Persistent Scheduled Tasks Table -->
    <div class="panel-card" style="margin-bottom:14px;">
        <h3 style="font-size:13.5px; color:#F8FAFC; margin-bottom:10px;">Configured Tasks List</h3>
        <div class="table-scroll-area">
            <table class="studio-data-table" id="schedTasksTable">
                <thead>
                    <tr>
                        <th>Task Name</th>
                        <th>Type</th>
                        <th>Schedule</th>
                        <th>Next Run</th>
                        <th>Last Run</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="schedTasksTbody">
                    <tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:20px;">Loading tasks...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Execution Run History -->
    <div class="panel-card">
        <h3 style="font-size:13.5px; color:#F8FAFC; margin-bottom:10px;">Recent Execution Logs &amp; Runs</h3>
        <div class="table-scroll-area">
            <table class="studio-data-table" id="schedRunsTable">
                <thead>
                    <tr>
                        <th>Run ID</th>
                        <th>Task Name</th>
                        <th>Trigger</th>
                        <th>Start Time</th>
                        <th>Duration</th>
                        <th>Exit Code</th>
                        <th>Status</th>
                        <th>Output</th>
                    </tr>
                </thead>
                <tbody id="schedRunsTbody">
                    <tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:20px;">Loading history...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

NEWS_CENTER_VIEW_HTML = r"""
<div class="workspace-view" id="view-news_center">
    <!-- Header with Hourly Check Countdown -->
    <div class="panel-card" style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h2>News Center — ABP Majha &amp; Aaj Tak</h2>
                <p style="font-size:12px; color:var(--text-muted); margin:0;">
                    Automated hourly updates from authorized feeds. Canonical deduplication, Marathi and English summaries.
                </p>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
                <span style="font-size:11.5px; color:#10B981; font-weight:700;" id="newsHourlyStatus">&#9679; Hourly Monitor Active</span>
                <button type="button" class="btn btn-primary" onclick="refreshNewsFeed()" style="font-size:11.5px; padding:6px 12px;">&#128257; Refresh News Now</button>
            </div>
        </div>
    </div>

    <!-- Category Filter Tabs -->
    <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px;">
        <button type="button" class="action-chip active" onclick="filterNewsCategory('All', this)">All News</button>
        <button type="button" class="action-chip" onclick="filterNewsCategory('Maharashtra', this)">🚩 Maharashtra</button>
        <button type="button" class="action-chip" onclick="filterNewsCategory('India', this)">🇮🇳 India</button>
        <button type="button" class="action-chip" onclick="filterNewsCategory('Politics', this)">🗳️ Politics</button>
        <button type="button" class="action-chip" onclick="filterNewsCategory('Business', this)">💼 Business &amp; Markets</button>
        <button type="button" class="action-chip" onclick="filterNewsCategory('Technology', this)">🤖 Technology &amp; AI</button>
        <button type="button" class="action-chip" onclick="filterNewsCategory('Sports', this)">🏏 Sports</button>
    </div>

    <!-- News Grid Container -->
    <div class="news-cards-grid" id="newsArticlesGrid">
        <!-- Rendered dynamically -->
    </div>

    <!-- Floating Non-Blocking News Notification Banner -->
    <div class="floating-news-alert-banner" id="floatingNewsBanner">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:11px; font-weight:800; color:#EF4444; text-transform:uppercase;">🚨 BREAKING NEWS ALERT</span>
            <button type="button" onclick="dismissFloatingNews()" style="background:none; border:none; color:#94A3B8; cursor:pointer; font-size:13px;">✕</button>
        </div>
        <div style="font-size:13px; font-weight:700; color:#F8FAFC; margin-bottom:6px;" id="floatingNewsTitle">Title</div>
        <div style="font-size:11.5px; color:#CBD5E1; line-height:1.4; margin-bottom:10px;" id="floatingNewsSummary">Summary</div>
        <div style="display:flex; gap:8px;">
            <button type="button" class="btn btn-primary" onclick="readFloatingNewsAloud()" style="font-size:10.5px; padding:4px 8px;">&#127908; Read Aloud</button>
            <button type="button" class="btn btn-secondary" onclick="openFloatingNewsInCenter()" style="font-size:10.5px; padding:4px 8px;">View Details</button>
            <button type="button" class="btn btn-secondary" onclick="dismissFloatingNews()" style="font-size:10.5px; padding:4px 8px;">Dismiss</button>
        </div>
    </div>
</div>
"""

ENTERTAINMENT_VIEW_HTML = r"""
<div class="workspace-view" id="view-entertainment_center">
    <div class="panel-card" style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h2>Entertainment &amp; Modern Lifestyle Center</h2>
                <p style="font-size:12px; color:var(--text-muted); margin:0;">
                    Explore cinema (Bollywood, Hollywood, Tollywood), trending web series, music discovery, tech videos, executive fashion, and productivity setups.
                </p>
            </div>
            <div style="display:flex; gap:8px;">
                <input type="text" class="studio-input" id="entSearchInput" placeholder="Search entertainment..." oninput="filterEntertainmentSearch(this.value)" style="width:200px; padding:5px 10px; font-size:11.5px;" />
            </div>
        </div>
    </div>

    <!-- Category Pills Bar -->
    <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:14px;">
        <button type="button" class="action-chip active" onclick="filterEntertainmentCategory('All', this)">All</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Bollywood', this)">🎬 Bollywood</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Hollywood', this)">🍿 Hollywood</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Tollywood', this)">🔥 Tollywood &amp; South</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Web Series', this)">📺 Web Series</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('YouTube', this)">▶️ YouTube</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Music', this)">🎵 Music Station</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Fashion', this)">👔 Modern Fashion</button>
        <button type="button" class="action-chip" onclick="filterEntertainmentCategory('Lifestyle', this)">✨ Lifestyle &amp; Setup</button>
    </div>

    <!-- Entertainment Discovery Grid -->
    <div class="ent-discovery-grid" id="entertainmentGrid">
        <!-- Rendered dynamically -->
    </div>
</div>
"""

BOOK_READER_VIEW_HTML = r"""
<div class="workspace-view" id="view-book_reader">
    <!-- Header with Book Ingestion Controls -->
    <div class="panel-card" style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h2>Book Reader &amp; Intelligent Learning Assistant</h2>
                <p style="font-size:12px; color:var(--text-muted); margin:0;">
                    Import PDF, DOCX, TXT, or local file paths. Read chapters, ask questions, generate study plans, interactive quizzes, and Marathi explanations.
                </p>
            </div>
            <div style="display:flex; gap:8px;">
                <button type="button" class="btn btn-primary" onclick="triggerBookUpload()">+ Upload Book (PDF/DOCX/TXT)</button>
                <input type="file" id="bookUploadInputHidden" style="display:none;" onchange="handleBookFileUpload(event)" accept=".pdf,.docx,.txt,.md" />
                <button type="button" class="btn btn-secondary" onclick="openBookPathImportModal()">Import Local File Path</button>
            </div>
        </div>
    </div>

    <!-- Active Book Reader Workspace -->
    <div class="reader-workspace">
        <!-- Left: Table of Contents & Chapter List -->
        <div class="reader-toc-panel">
            <div style="font-size:12px; font-weight:800; color:#38BDF8; margin-bottom:8px; text-transform:uppercase;">
                &#128218; Table of Contents
            </div>
            <div style="font-size:13px; font-weight:700; color:#F8FAFC; margin-bottom:4px;" id="readerActiveBookTitle">Loading book...</div>
            <div style="font-size:11px; color:var(--text-muted); margin-bottom:12px;" id="readerActiveBookAuthor">Author</div>

            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-size:10.5px; color:var(--text-sub); margin-bottom:4px;">
                    <span>Reading Progress</span>
                    <span id="readerProgressPct">0%</span>
                </div>
                <div class="agent-progress-track">
                    <div class="agent-progress-fill" id="readerProgressBar" style="width:0%;"></div>
                </div>
            </div>

            <div id="readerChaptersList" style="flex:1; overflow-y:auto;">
                <!-- Chapters loaded dynamically -->
            </div>
        </div>

        <!-- Right: Chapter Content & AI Learning Assistant -->
        <div class="reader-content-panel">
            <!-- Reader Bar Controls -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #263354; padding-bottom:10px; margin-bottom:12px;">
                <div style="font-size:14px; font-weight:700; color:#F8FAFC;" id="readerCurrentChapterTitle">Chapter 1</div>
                <div style="display:flex; gap:6px; align-items:center;">
                    <button type="button" class="btn btn-secondary" onclick="adjustReaderFontSize(-1)" style="font-size:11px; padding:3px 8px;">A-</button>
                    <button type="button" class="btn btn-secondary" onclick="adjustReaderFontSize(1)" style="font-size:11px; padding:3px 8px;">A+</button>
                    <button type="button" class="btn btn-primary" onclick="readCurrentChapterAloud()" style="font-size:11px; padding:4px 10px;">&#127908; Read Aloud</button>
                </div>
            </div>

            <!-- Chapter Text Area -->
            <div class="reader-text-area" id="readerTextArea">
                Select a chapter from the left to begin reading...
            </div>

            <!-- Intelligent Learning Actions Bar -->
            <div style="margin-top:14px; padding-top:12px; border-top:1px solid #263354;">
                <div style="font-size:11.5px; font-weight:700; color:#38BDF8; margin-bottom:6px;">
                    &#129302; Intelligent Learning Assistant:
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px;">
                    <button type="button" class="action-chip" onclick="askBookAI('Explain this book in simple language')">&#128161; Explain in Simple Terms</button>
                    <button type="button" class="action-chip" onclick="askBookAI('Summarize this chapter')">&#128221; Summarize Chapter</button>
                    <button type="button" class="action-chip" onclick="askBookAI('Create a study plan from this book')">&#128197; 7-Day Study Plan</button>
                    <button type="button" class="action-chip" onclick="askBookAI('Quiz me on this chapter')">&#10067; Quiz Me</button>
                    <button type="button" class="action-chip" onclick="askBookAI('Explain this in Marathi')">&#127470;&#127475; मराठीत स्पष्ट करा</button>
                    <button type="button" class="action-chip" onclick="askBookAI('Generate a visual conceptual architecture diagram')">&#128202; Visual Concept Diagram</button>
                </div>
                <div id="readerAIExplanationBox" style="display:none; background:#0B1120; border:1px solid #263354; border-radius:8px; padding:12px; font-size:12.5px; color:#E2E8F0; line-height:1.6; max-height:220px; overflow-y:auto;"></div>
            </div>
        </div>
    </div>
</div>
"""

CLOUD_TRENDS_VIEW_HTML = r"""
<div class="workspace-view" id="view-cloud_trends">
    <div class="panel-card" style="margin-bottom:14px; background:linear-gradient(135deg, rgba(14,21,40,0.95) 0%, rgba(26,35,66,0.9) 100%); border:1px solid #263354;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:44px; height:44px; border-radius:50%; background:radial-gradient(circle, #38BDF8 20%, #1E1B4B 90%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 16px rgba(56,189,248,0.5); font-size:22px;">
                    &#9729;
                </div>
                <div>
                    <h2 style="margin:0; font-size:16px; color:#F8FAFC; display:flex; align-items:center; gap:8px;">
                        Snowflake vs AWS — Top 10 Upcoming / Latest Trends (October 2026)
                        <span class="badge" style="background:#0F172A; border:1px solid #38BDF8; color:#38BDF8; font-size:11px;">OCTOBER 2026 ED.</span>
                    </h2>
                    <span style="font-size:12px; color:#94A3B8;">
                        Data Engineering Career &amp; Lakehouse Production Blueprints • Dual-Language (English &amp; मराठी) • Cortex AI &amp; Bedrock AgentCore
                    </span>
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <button type="button" class="btn btn-primary" onclick="runCloudBenchmarkSimulation()" style="font-size:11px; padding:6px 12px;">&#9889; Run Architecture Benchmark</button>
                <button type="button" class="btn btn-secondary" onclick="exportCloudTrendsCSV()" style="font-size:11px; padding:6px 12px;">&#128190; Export Matrix CSV</button>
                <button type="button" class="btn btn-accent" onclick="switchCloudTrendTab('roadmap'); showCareerRoadmap('mr');" style="font-size:11px; padding:6px 12px;">&#127470;&#127475; मराठी करिअर मार्गदर्शन</button>
            </div>
        </div>
    </div>

    <!-- Quick Navigation Tabs & Search -->
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px;">
        <div style="display:flex; gap:8px; flex-wrap:wrap;" id="cloudTrendTabs">
            <button type="button" class="btn btn-primary" id="btnTabAllTrends" onclick="switchCloudTrendTab('all')">All 20 Trends</button>
            <button type="button" class="btn btn-secondary" id="btnTabSnowflake" onclick="switchCloudTrendTab('snowflake')">❄️ Snowflake Top 10</button>
            <button type="button" class="btn btn-secondary" id="btnTabAWS" onclick="switchCloudTrendTab('aws')">🔶 AWS Top 10</button>
            <button type="button" class="btn btn-secondary" id="btnTabMatrix" onclick="switchCloudTrendTab('matrix')">📊 Comparison Matrix</button>
            <button type="button" class="btn btn-secondary" id="btnTabRoadmap" onclick="switchCloudTrendTab('roadmap')">🎯 2026 DE Career Roadmap</button>
        </div>
        <div style="min-width:280px; max-width:400px; flex:1;">
            <input type="text" class="studio-input" id="cloudTrendSearch" placeholder="Search trends (e.g. Cortex, Iceberg v3, S3 Tables)..." oninput="filterCloudTrends()" style="margin:0; font-size:12px; padding:7px 12px;">
        </div>
    </div>

    <!-- Code / DDL Generator Interactive Output Modal/Card -->
    <div id="cloudCodeViewerPanel" style="display:none; margin-bottom:14px; background:#070B16; border:1px solid #38BDF8; border-radius:10px; padding:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-size:13px; font-weight:700; color:#38BDF8; display:flex; align-items:center; gap:8px;">
                &#128187; <span id="cloudCodeTitle">Generated DDL / Code</span>
            </div>
            <div style="display:flex; gap:8px;">
                <button type="button" class="btn btn-secondary" onclick="copyGeneratedCloudCode()" style="font-size:11px; padding:3px 10px;">📋 Copy Code</button>
                <button type="button" class="btn btn-secondary" onclick="closeCloudCodeViewer()" style="font-size:11px; padding:3px 8px;">✕ Close</button>
            </div>
        </div>
        <div style="font-size:11.5px; color:#94A3B8; margin-bottom:8px;" id="cloudCodeDesc"></div>
        <pre id="cloudCodeBlock" style="background:#030712; border:1px solid #263354; border-radius:6px; padding:12px; color:#A7F3D0; font-family:'Courier New', monospace; font-size:12px; overflow-x:auto; max-height:260px;"></pre>
    </div>

    <!-- Main Trends Dual-Column Grid -->
    <div id="cloudTrendsDualGrid" style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
        <!-- Left Column: Snowflake Top 10 -->
        <div class="panel-card" style="padding:16px; background:#0E1528;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; border-bottom:1px solid #263354; padding-bottom:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:22px;">❄️</span>
                    <div>
                        <h3 style="margin:0; font-size:15px; color:#38BDF8;">Snowflake — Top 10 Innovations</h3>
                        <span style="font-size:11.5px; color:#94A3B8;">Cortex AI Suite, Openflow CDC &amp; Dynamic Tables</span>
                    </div>
                </div>
                <span class="badge" style="background:#0B1120; border:1px solid #38BDF8; color:#38BDF8; font-size:11px;">10 FEATURES</span>
            </div>
            <div id="snowflakeTrendsList" style="display:flex; flex-direction:column; gap:12px;">
                <!-- Dynamically loaded -->
            </div>
        </div>

        <!-- Right Column: AWS Top 10 -->
        <div class="panel-card" style="padding:16px; background:#0E1528;">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; border-bottom:1px solid #263354; padding-bottom:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:22px;">🔶</span>
                    <div>
                        <h3 style="margin:0; font-size:15px; color:#F59E0B;">AWS — Top 10 Innovations</h3>
                        <span style="font-size:11.5px; color:#94A3B8;">Bedrock AgentCore, S3 Tables &amp; Apache Iceberg v3</span>
                    </div>
                </div>
                <span class="badge" style="background:#0B1120; border:1px solid #F59E0B; color:#F59E0B; font-size:11px;">10 FEATURES</span>
            </div>
            <div id="awsTrendsList" style="display:flex; flex-direction:column; gap:12px;">
                <!-- Dynamically loaded -->
            </div>
        </div>
    </div>

    <!-- Comparison Matrix Section (Toggled) -->
    <div id="cloudTrendsMatrixSection" style="display:none; margin-top:14px;" class="panel-card">
        <h3 style="margin-bottom:12px; font-size:15px; color:#F8FAFC;">Architectural Comparison Matrix (Head-to-Head 2026)</h3>
        <div class="table-container" style="overflow-x:auto;">
            <table class="studio-table" id="cloudMatrixTable" style="width:100%; font-size:12px;">
                <thead>
                    <tr>
                        <th>Domain / Pillar</th>
                        <th>Snowflake 2026</th>
                        <th>AWS 2026</th>
                        <th>Data Engineering Impact</th>
                        <th>Enterprise Strength</th>
                    </tr>
                </thead>
                <tbody id="cloudMatrixTableBody">
                    <!-- Loaded dynamically -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- 2026 Career Roadmap Section (Toggled) -->
    <div id="cloudTrendsRoadmapSection" style="display:none; margin-top:14px;" class="panel-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <h3 style="margin:0; font-size:15px; color:#10B981;" id="roadmapHeadline">Data Engineer Career Roadmap 2026</h3>
            <div style="display:flex; gap:6px;">
                <button type="button" class="btn btn-secondary" onclick="showCareerRoadmap('en')" style="font-size:11px; padding:3px 8px;">English</button>
                <button type="button" class="btn btn-secondary" onclick="showCareerRoadmap('mr')" style="font-size:11px; padding:3px 8px;">मराठी</button>
            </div>
        </div>
        <div id="roadmapContentBox" style="font-size:12.5px; line-height:1.7; color:#E2E8F0;">
            <!-- Loaded dynamically -->
        </div>
    </div>
</div>
"""
