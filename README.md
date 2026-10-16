---
title: Mangesh Nano Pro AI Studio
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# MANGESH NANO PRO AI STUDIO v12
**Full Multi-Agent Automation, Video Maker, Model Integration & Animated Digital Office**

Owner: Mangesh Bagul  
Platform: Windows 10 / Windows 11  
Default Workspace Directory: `C:\Mangesh\AI video\AI_manager`  
Local Server: `http://127.0.0.1:8000`

---

## 🚀 Key Functional Upgrades & Working Architecture

### 1. Interactive Center Panels (No Static Placeholders)
Every navigation item in the Left Sidebar switches the central panel to a dedicated, fully-featured workspace:
- **Dashboard**: Manager Agent central prompt box with multi-agent delegation, digital office preview, and deliverables viewer.
- **SQL Video Maker**: Dedicated SQL question input, query editor, video settings, and YouTube metadata generation (title, description, tags, 9:16 thumbnail).
- **Python Video Maker**: Dedicated Python concept prompt, code editor, controlled execution output, animation settings, and metadata generation.
- **Image Maker**: Prompt input, style selector (Modern Tech, YouTube Vertical, Corporate Dark, Cyberpunk), aspect ratio (9:16, 16:9, 1:1), and instant image generation.
- **Coding Agent**: Multi-language support (Python, SQL, JS, HTML/CSS, Bash), Model selector (Qwen 3b/7b, Phi4), and actions: *Generate Code*, *Debug Code*, *Explain Code*, *Generate Unit Tests*. Includes AST syntax validation.
- **Research Agent**: Live topic research, local knowledge retrieval, and model synthesis with structured sections and citation tracking.
- **Telegram AI Agent**: Direct integration with Bot `@mangesh_technews_bot` and Chat ID `1200023268`. One-click *Send Telegram Tech News*, *Check Telegram Bot Connection*, and custom message dispatch with infallible plaintext fallback.
- **Tasks & Reminders**: Add reminders, recurring schedules, pending tasks table, and executive briefing generator. Stored in SQLite.
- **Animated AI Office**: Visual digital office with animated SVG robot characters featuring glowing antenna visors, moving typing arms, and walking transitions across workstations.
- **Backups & Memory**: Real SQLite memory statistics, database file size, search knowledge base, and full `.tar.gz` system backup archive creation.
- **Live Execution Logs**: Real-time log stream from all agents and components with copy and clear tools.
- **Settings**: Dynamic Ollama and API model detection, connection testing, and latency benchmarking.

### 2. Local Audio Browse (Not Built-In Audio Library)
- Both SQL and Python Video Maker workspaces include a **Browse Audio File** button (`<input type="file">`).
- Allows selecting local MP3, WAV, AAC, or M4A audio files from your Windows laptop.
- Duration is anchored strictly to the video length; audio is automatically looped or trimmed via FFmpeg so background audio never alters the final video duration.

### 3. Infallible Telegram Bot Delivery
- Fixed Telegram entity parsing error (`HTTP 400 Bad Request: can't parse entities`).
- Strips any non-whitelisted HTML tags (`<title>`, `<head>`, `<!DOCTYPE>`, etc.).
- Includes automatic fallback to plain-text dispatch with all HTML tags stripped if Telegram API returns any format error.

### 4. Smart Model Prioritization & Timeout Prevention
- Cross-checks installed Ollama models dynamically.
- Prioritizes fast models (`qwen2.5-coder:3b`, `phi4-mini`) over heavy models (`7b`) to prevent timeouts.
- Scales timeout windows based on model parameter size.

---

## 🛠️ Windows Installation & Running Guide

### Quick Start
Double-click `start_studio.bat` or run:
```cmd
cd /d "C:\Mangesh\AI video\AI_manager"
pip install -r requirements.txt
python main.py
```
The server will start at `http://127.0.0.1:8000` and automatically launch Google Chrome.

### Running Automated Verification Tests
```cmd
python -m unittest app/tests/test_suite.py
```
All 10 unit tests pass 100%.

Gemini CLI test
