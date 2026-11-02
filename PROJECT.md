# Project: Universal Tech AI Video Maker (9:16 Shorts & Reels) Revamp

## Architecture
- **Workspace UI & Web Route (`main.py`, `app/ui/sql_video_workspace.py`, `app/ui/sql_video_js.py`)**:
  - `@app.get("/workspace/sql-video")`: Serves clean, responsive HTML5 workspace tailored for 9:16 vertical reels and shorts.
  - Clean UI Controls:
    - Topic / prompt input with trending topic suggestion chips.
    - LLM Model Selector: Groq LPU (`openai/gpt-oss-120b`), Mistral (`codestral-latest`), Cohere (`command-r-plus-08-2024`), SambaNova, DeepSeek, OpenRouter.
    - Regional Language & Voice Actor Selectors:
      - Marathi: `mr-IN-AarohiNeural`, `mr-IN-ManoharNeural`
      - Hindi: `hi-IN-MadhurNeural`, `hi-IN-SwaraNeural`
      - English: `en-US-JennyNeural`, `en-US-GuyNeural`, Deepgram Aura (`aura-asteria-en`, `aura-luna-en`)
    - Dynamic Live API Toggles: Pixabay Video (4K/2K B-roll), Unsplash (4K Photos), Giphy (Stickers), Freesound (SFX Transitions), Tavily (Real-Time News).
    - Multi-stage generation progress indicator and 9:16 smartphone preview player.
- **Multi-Model Routing Layer (`app/core/model_adapter.py`)**:
  - `ModelManager`: Orchestrates script generation across providers.
  - `CohereAdapter`: Supports Cohere `command-r-plus-08-2024` with low latency.
  - `SambaNovaAdapter`: Supports SambaNova cloud models with fast fallback.
  - Failover cascade: Groq -> Mistral -> Cohere -> Gemini -> Ollama.
- **Dynamic Live API Providers (`app/video_maker/`)**:
  - `pixabay_video_provider.py`: 4K/2K B-roll search, vertical cropping, CDN clip downloading.
  - `freesound_provider.py`: SFX transition search (`whoosh`, `glitch`, `riser`), audio caching.
  - `deepgram_provider.py`: Aura TTS high-fidelity speech synthesis; Nova-2 STT transcription with word-level float timestamps (`start`, `end`) for animated captions.
  - `giphy_provider.py`: Transparent stickers and viral meme overlays.
  - `tavily_news_search.py`: Real-time news topics search and factual grounding.
  - `unsplash_provider.py`: 4K portrait 9:16 photography.
- **Core Video Generation Engine (`app/video_maker/sql_short_engine.py`, `modern_2026_video_matrix.py`)**:
  - `generate_short_prompt_async`: Assembles scenes, invokes live media APIs, coordinates audio synthesis, word-level caption alignment, and returns authentic generation ledger.
  - Video Compositor & FFmpeg 7.1 Backend: Stitches 1080x1920 (9:16) H.264 video, AAC audio, and animated subtitles.
- **Automated Verification & E2E Test Suite (`app/tests/test_video_maker_pipeline_e2e.py`)**:
  - Python `unittest` harness testing live API connectivity, blueprint generation, and FFmpeg video synthesis with stream aspect ratio and audio verification.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | UI/UX Clutter & Obsolete Elimination | Remove dead `#phoneAvatarPip`, 44 inflated model options, static fake badges, fake modals, and 45 orphan DOM IDs in JS | M1 | R1 Survey |
| F2 | Responsive 9:16 Workspace Controls | Clean controls for Topic, quick chips, LLM selector, Language, Voice Actor, and 5 Media Provider toggles | M1 | R1 Survey |
| F3 | Multi-Stage Progress & Authentic Ledger | Live 5-step progress visualization and authentic asset ledger replacing fake 99.8% scores | M1 | R1 Survey |
| F4 | Model Adapter Cohere & SambaNova | Implement `CohereAdapter` and `SambaNovaAdapter` in `model_adapter.py` with fast failover | M2 | R2 Survey |
| F5 | Tavily Real-Time Context Wiring | Wire `tavily_news_search.py` into `sql_short_engine.py` for factual script grounding | M2 | R2 Survey |
| F6 | Pixabay 9:16 B-Roll Clip Wiring | Dynamically query and attach Pixabay video clips per scene in `sql_short_engine.py` | M2 | R2 Survey |
| F7 | Unsplash Portrait Photography Wiring | Dynamically query and attach Unsplash 9:16 photos per scene in `sql_short_engine.py` | M2 | R2 Survey |
| F8 | Freesound SFX Transitions Wiring | Dynamically query and attach Freesound SFX (`whoosh`, `glitch`) between scenes | M2 | R2 Survey |
| F9 | Deepgram Nova-2 Word-Level Captions | Transcribe audio via Nova-2 STT to generate word-level timestamps (`start`, `end`) for animated captions | M2 | R2 Survey |
| F10 | Deepgram Aura & Edge-TTS Multi-Voice | Support Marathi (`mr-IN-AarohiNeural`), Hindi (`hi-IN-MadhurNeural`), and English (`aura-asteria-en`, `en-US-JennyNeural`) | M2 | R2 Survey |
| F11 | Giphy Viral Stickers Overlay Wiring | Dynamically query and attach Giphy transparent stickers to scene blueprints | M2 | R2 Survey |
| F12 | Automated Live API Test Suite | Automated tests for all 8 live APIs verifying HTTP 200 responses and payloads | M3 | R3 Survey |
| F13 | End-to-End 9:16 Video Synthesis Test | Complete E2E test rendering a 9:16 MP4 clip with FFmpeg, probing DAR 9:16, 1080x1920, and AAC audio | M3 | R3 Survey |
| F14 | Comprehensive E2E Test Suite (Tiers 1-4) | Opaque-box test suite covering Tiers 1-4 across all features | E2E Track | Project Pattern |
| F15 | Adversarial Coverage Hardening (Tier 5) | White-box stress testing, boundary fault injection, and coverage audit | M4 | Project Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | UI/UX Revamp & Clutter Elimination | F1, F2, F3: Clean up `sql_video_workspace.py` and `sql_video_js.py`, remove obsolete dead elements, implement functional 9:16 controls and authentic generation ledger | none | DONE |
| M2 | Dynamic Live API Pipeline Integration | F4, F5, F6, F7, F8, F9, F10, F11: Implement `CohereAdapter`/`SambaNovaAdapter`, wire Pixabay, Freesound, Deepgram Aura/Nova-2, Giphy, Tavily, Unsplash, Edge-TTS into `sql_short_engine.py` | none | DONE |
| M3 | Automated Verification & E2E Video Pipeline Test | F12, F13: Implement `app/tests/test_video_maker_pipeline_e2e.py` covering live APIs, blueprint generation, and FFmpeg 9:16 video synthesis & stream probing | M1, M2 | IN_PROGRESS |
| M4 | Final Milestone: 100% E2E Test Pass & Hardening | Phase 1: Pass 100% E2E tests (Tiers 1-4); Phase 2: Tier 5 adversarial coverage hardening & forensic audit signoff | M3, TEST_READY | PLANNED |
| E2E | E2E Testing Track | F14: Build requirement-driven opaque-box test suite (Tiers 1-4), generate `TEST_INFRA.md`, publish `TEST_READY.md` | none | DONE |

## Interface Contracts
### Workspace UI ↔ Backend Generation API
- Route: `POST /api/sql_video/generate_prompt_job`
  - Request JSON:
    ```json
    {
      "prompt": "Top 3 AI tools in 2026",
      "model": "openai/gpt-oss-120b",
      "language": "en",
      "voice": "mr-IN-AarohiNeural",
      "providers": {
        "pixabay": true,
        "unsplash": true,
        "giphy": true,
        "freesound": true,
        "tavily": true
      }
    }
    ```
  - Response JSON (HTTP 202):
    ```json
    { "status": "queued", "job_id": "<uuid>" }
    ```
- Route: `GET /api/sql_video/generation_jobs/{job_id}`
  - Response JSON (HTTP 200):
    ```json
    {
      "job_id": "<uuid>",
      "status": "completed",
      "stage": "complete",
      "progress": 100,
      "result_data": {
        "blueprint": { ... },
        "audio_url": "/static/...",
        "word_timestamps": [ { "word": "Top", "start": 0.08, "end": 0.24 } ],
        "attribution_ledger": { ... }
      }
    }
    ```

### Video Engine ↔ Live Media Providers
- `pixabay_video_provider.search_pixabay_videos(query: str, per_page: int = 5) -> List[Dict[str, Any]]`
- `unsplash_provider.search_unsplash_photos(query: str, count: int = 5, orientation: str = "portrait") -> List[Dict[str, Any]]`
- `freesound_provider.search_sound_effects(query: str, count: int = 3) -> List[Dict[str, Any]]`
- `deepgram_provider.generate_deepgram_speech(text: str, output_path: str, voice: str = "aura-asteria-en") -> bool`
- `deepgram_provider.transcribe_audio_with_timestamps(audio_path: str) -> Optional[List[Dict[str, Any]]]`
- `giphy_provider.search_giphy_stickers(query: str, limit: int = 5) -> List[Dict[str, Any]]`
- `tavily_news_search.search_trending_topic(topic: str, max_results: int = 3) -> List[Dict[str, Any]]`

## Code Layout
- `app/ui/sql_video_workspace.py`: Workspace HTML layout for `/workspace/sql-video`.
- `app/ui/sql_video_js.py` & `app/video_maker/sql_video_js.py`: Client-side UI logic, 60fps canvas player, MediaRecorder export.
- `app/core/model_adapter.py`: `ModelManager`, `CohereAdapter`, `SambaNovaAdapter`, `GroqAdapter`, `MistralAdapter`.
- `app/video_maker/sql_short_engine.py`: Core short video synthesis engine, prompt generation, audio creation, asset aggregation.
- `app/video_maker/modern_2026_video_matrix.py`: Visual pipeline matrix and layout definitions.
- `app/video_maker/pixabay_video_provider.py`: Pixabay Video API client.
- `app/video_maker/freesound_provider.py`: Freesound SFX API client.
- `app/video_maker/deepgram_provider.py`: Deepgram Aura TTS and Nova-2 STT client.
- `app/video_maker/giphy_provider.py`: Giphy stickers and memes client.
- `app/video_maker/tavily_news_search.py`: Tavily real-time news search client.
- `app/video_maker/unsplash_provider.py`: Unsplash 4K photography client.
- `app/tests/test_video_maker_pipeline_e2e.py`: Automated end-to-end test suite.
