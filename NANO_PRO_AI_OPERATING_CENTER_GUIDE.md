# 🚀 NANO PRO — INTELLIGENT PERSONAL AI OPERATING CENTER
## Comprehensive Architecture & User Operations Manual

---

### 🌟 Executive Overview
**Nano Pro** has been upgraded into a central intelligent personal operating center. It functions as a single intelligent Manager leading a team of **45 specialized AI agents** that understand instructions in **English, Marathi (मराठी), and Hinglish**, coordinate database pipelines, automate Python/SQL workflows, deliver hourly verified news, curate modern multimedia & lifestyle, and guide book reading and deep study.

---

### 1. 💬 AI Manager Conversation & Response Stream
- **Natural, Human-Like Communication**:
  - Understands everyday English, Marathi, Hinglish, and incomplete instructions.
  - Automatically remembers conversational context across turns.
  - Understands conversational follow-ups:
    - `"Connect these two tables and show me customer balances"`
    - `"Explain this in simple language"` / `"सोप्या भाषेत समजाव"`
    - `"Make a graph"` / `"आलेख दाखवा"`
    - `"Compare these"`
    - `"Continue"`
- **Smart Response Modes**:
  - `Quick Answer`: Concise and direct.
  - `Detailed Explanation`: Step-by-step reasoning and breakdowns.
  - `Data Result`: Interactive table with search, sorting, and pagination.
  - `Data Visualization`: Dynamic Canvas charts (Bar, Line, Donut, Pie).
  - `Code Execution`: SQL and Python scripts with execution metrics.
  - `Task Execution`: Pipeline progress and step-by-step execution.
  - `Recommendation`: Follow-up action chips.
- **Interactive Components**:
  - **Sortable & Searchable Tables**: Click any column header to sort ascending/descending; real-time search filter; rows-per-page selector (5, 10, 25); pagination controls; Export to CSV and Export to Excel buttons.
  - **Canvas Charts**: Vector rendering with legend and tooltips; instant toggle between Bar, Line, and Donut views.
  - **KPI Metric Cards**: Real-time summary statistics with percentage changes and trend indicators.
  - **Real-Time Animated Execution Panel**: Step progress (1. Interpret -> 2. Connection Check -> 3. Execute SQL -> 4. Render Table -> 5. Chart & Explain) with query view and elapsed time badge.

---

### 2. 🤖 Single AI Manager Symbol
- **Unified Visual Identity**: A single, prominent symbol representing the AI Manager across the entire interface (in the top header bar and voice station).
- **8 Dynamic Reactive States**:
  1. `READY`: Calm cyan/blue core with breathing orbital ring.
  2. `LISTENING`: Glowing emerald green microphone aura with pulsing ripple.
  3. `THINKING`: Clockwise rotating violet/purple energy orbit.
  4. `PLANNING`: Geometric cobalt expanding diamond lattice.
  5. `DELEGATING`: Outward radiating teal data transmission beams.
  6. `EXECUTING`: Rapidly spinning amber/gold progress ring.
  7. `SPEAKING`: Synchronized magenta audio waveform modulation.
  8. `WAITING`: Warm standby amber breath.
  9. `ERROR`: Alert crimson warning indicator.
- **Click-to-Speak**: Clicking the AI Manager Symbol activates microphone input.

---

### 3. 🏢 Animated 3D AI Agent Office
- **Living 3D Digital Workspace**:
  - **Central Manager Desk**: Floating holographic core with active coordination display.
  - **6 Specialist Workstation Pods** (All 45 Registered Agents):
    - **Group A (Core Orchestration)**: Manager Agent, Task Planning Agent, Task Coordinator, Model Router, Quality Assurance Agent.
    - **Group B (Data Engineering)**: Data Engineer Agent, Data Discovery Agent, Ingestion Agent, Data Quality Agent, Snowflake L0 Bronze Agent, Snowflake L1 Silver Harmonized Agent, Snowflake L2 Gold Curated Agent, Data Pipeline Agent, Data Transformation Agent.
    - **Group C (Snowflake & Oracle)**: Snowflake Admin, Oracle XE Admin, Query Optimizer, CDC Agent, Partitioning Agent, Reverse ETL Agent, Staging Lake Agent, Database Auditor.
    - **Group D (Analytics & ML)**: Data Analyst, ML Feature Engineer, Data Scientist, Statistical Modeler, KPI Reporting Agent.
    - **Group E (Integrations & Comms)**: Email Agent, Telegram Agent, S3 Data Lake Agent, SFTP & Transfer Agent, REST API Connector, Webhook Agent, Notification Dispatcher.
    - **Group F (Security, Governance & Dev)**: Security Officer, Credentials Vault, Code Reviewer, Python Developer, SQL Developer, Test Engineer, Documentation Writer, Backup Manager, Storage Inspector, Recovery Engine, Job Search Assistant.
- **Truthful Status Display**:
  - `Working`, `Planning`, `Waiting for Dependency`, `Standby`, `Completed`, `Failed`, `Paused`.
  - Reflects real backend execution polled from `/api/office/live-state`.
  - Zero fabricated activity: agents rest when no tasks are running.
- **Live Data Flow Beams**: Visual energy beams travel from Manager Desk to specialist workstations during actual task execution.

---

### 4. 🎤 Nano Pro Voice Assistant ("Hi NanoPro")
- **One-Tap & Wake-Word Activation**:
  - Click the AI Manager Symbol or say *"Hi NanoPro"*.
  - Speech Recognition via Web Speech API with multilingual support (`mr-IN` Marathi, `hi-IN` Hindi, `en-IN` Indian English, `en-US` US English).
  - Speech Synthesis (TTS) reading responses, tables, and book chapters aloud.
- **Interruption Controls**: Say *"Stop"* or click *Stop Speaking* to halt audio immediately.
- **Unified Context**: Voice interactions automatically post to the Manager Conversation Stream and share the exact same conversational memory.

---

### 5. ⏰ Task Scheduler & Automation Center (Windows Task Scheduler Alternative)
- **Supported Task Types**:
  - Python scripts (`.py` files or inline scripts).
  - SQL queries (`.sql` scripts or queries against Snowflake, Oracle XE, or SQLite).
  - Windows Batch files (`.bat`).
  - Windows PowerShell scripts (`.ps1`).
  - Studio Application Jobs (ETL pipelines, backups, health checks).
- **Recurrence Options**:
  - Run Once.
  - Every X Minutes.
  - Hourly.
  - Daily (at HH:MM).
  - Weekly (on selected weekday at HH:MM).
  - Monthly.
  - Custom Cron expression.
- **Full Lifecycle Controls**:
  - Create, Edit, Run Now, Pause, Resume, Enable/Disable, Duplicate, Delete, View Logs.
- **Execution Tracking**:
  - Captures stdout, stderr, process return exit code, and execution duration.
  - Survives application restarts: schedules restored automatically from SQLite `studio_memory.db`.

---

### 6. 📰 News Center — ABP Majha & Aaj Tak
- **Automated Hourly Ingestion**:
  - Ingests verified feeds from **ABP Majha** (Marathi) and **Aaj Tak** (National/Hindi).
  - Canonical URL & publication timestamp deduplication to prevent duplicate alerts.
- **Dual-Language Summaries**:
  - Marathi summary (`summary_mr`) and English summary (`summary_en`) for every story.
- **Categories**:
  - Maharashtra, India, Politics, Business & Markets, Technology & AI, Sports, Breaking News.
- **Floating Alert Banner**:
  - Subtle non-blocking popup in bottom-right corner when Breaking or High-priority news arrives.
  - Actions: *Read Aloud*, *View Story*, *Dismiss*.

---

### 7. 🎬 Entertainment & Modern Lifestyle Center
- **Categories**:
  - Bollywood, Hollywood, Tollywood & South Indian Cinema, Web Series, YouTube, Music Station, Modern Fashion, Lifestyle & Workspaces.
- **Visual Discovery Cards**:
  - Smooth image zoom on hover, metadata tags (IMDb rating, runtime, cast, views).
  - Favorite star toggle.
  - *"Ask AI Manager"* button on each card to get instant explanation or analysis.
  - Embedded YouTube player and Music audio station.

---

### 8. 📚 Book Reader & Intelligent Learning Assistant
- **Document Ingestion**:
  - Supports **PDF** (via `pypdf`), **DOCX** (via `python-docx`), **TXT**, **MD**, or local file paths.
  - Automatic chapter boundary detection and page chunking.
- **Reading View**:
  - Table of Contents sidebar with clickable chapters.
  - Font size controls (`A-` / `A+`).
  - Reading progress bar and chapter progress indicator.
  - Text-to-Speech audio reader for chapters.
- **Intelligent Learning Assistant**:
  - *"Explain this book in simple language"*
  - *"Summarize Chapter X"*
  - *"Explain concept with examples"*
  - *"Create a 7-day study plan"*
  - *"Quiz me on this chapter"* (interactive multiple-choice questions)
  - *"Explain this in Marathi"* (मराठी स्पष्टीकरण)
  - *"Generate a visual conceptual architecture diagram"* (Mermaid / SVG flowchart)

---

### 9. 🔐 Pre-Configured Enterprise Connections
All 4 enterprise connections are active and verified:
1. **NANO_PRO_SNOWFLAKE**: `mangeshbagul15` on `BANK_DB.L0_STAGING` (AWS AP-Southeast-7).
2. **MY_ORACLE_XE_REMOTE**: `SYSTEM` on `192.168.31.240:1521/XEPDB1`.
3. **GMAIL_SMTP**: `mangeshbagul15@gmail.com` via STARTTLS port 587.
4. **AWS_S3_DATA_LAKE & BEDROCK**: `mangesh-studio` in `ap-southeast-2` with `s3://nanopro-data-lake`.
5. **AUTOMATED CROSS-SYSTEM PIPELINE**: Oracle XE ➔ AWS S3 / Staging ➔ Snowflake Data Warehouse.

---

### 10. ⚡ Launch Instructions
```bash
# Windows:
run_studio.bat
# or PowerShell:
./run_studio.ps1

# Direct Python:
python main.py
```
Open your browser to: **http://127.0.0.1:8000**
