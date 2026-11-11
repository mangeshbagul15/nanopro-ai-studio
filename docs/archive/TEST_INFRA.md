# Universal Tech AI Video Maker — E2E Test Infrastructure & Test Suite Documentation

## 1. Test Architecture Overview

The Universal Tech AI Video Maker End-to-End (E2E) Test Suite (`app/tests/test_e2e_video_maker.py`) is an opaque-box, requirement-driven verification harness designed to thoroughly test 9:16 vertical video creation, live media API integrations, UI workspace responsiveness, audio synchronization, and video rendering pipelines across all 4 standard test tiers.

All test cases are derived strictly from user requirements in `ORIGINAL_REQUEST.md` and the 15-feature inventory in `PROJECT.md`.

```
+----------------------------------------------------------------------------------------------------+
|                      Universal Tech AI Video Maker (9:16 Shorts & Reels) Test Architecture          |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 1: Feature Coverage (F1 - F15)                                                        |   |
|   | - F1: UI/UX Clutter & Obsolete Elimination   - F9: Deepgram Nova-2 Word Captions           |   |
|   | - F2: Responsive 9:16 Workspace Controls     - F10: Deepgram Aura & Edge-TTS Multi-Voice   |   |
|   | - F3: Multi-Stage Progress & Authentic Ledger- F11: Giphy Viral Stickers Overlay Wiring    |   |
|   | - F4: Model Adapter Cohere & SambaNova       - F12: Automated Live API Test Suite          |   |
|   | - F5: Tavily Real-Time Context Wiring        - F13: End-to-End 9:16 Video Synthesis Test   |   |
|   | - F6: Pixabay 9:16 B-Roll Clip Wiring        - F14: Comprehensive E2E Test Suite (Tiers 1-4|   |
|   | - F7: Unsplash Portrait Photography Wiring   - F15: Adversarial Coverage Hardening (Tier 5)|   |
|   | - F8: Freesound SFX Transitions Wiring                                                     |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 2: Boundary & Corner Cases                                                            |   |
|   | - Empty and Whitespace Prompts               - HTTP 401/403/404/429/500/502/504 Handling   |   |
|   | - Ultra-Long Prompts (>2,500 chars)          - Network Timeouts & Connection Drops         |   |
|   | - Unknown / Invalid Model Fallback           - 0-Byte and Corrupted Audio Duration Probing |   |
|   | - Zero Search Results from Media APIs        - SQLite In-Memory Sandbox Syntax Errors      |   |
|   | - Unsupported Language Fallback              - Non-Existent Generation Job ID Lookups      |   |
|   | - Missing or Empty API Key Degradation       - FFmpeg Video Cropping on Missing Files      |   |
|   | - Pixabay Per-Page Boundary Clamping (3-200) - Audio Track Duration Calibration & Loops   |   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 3: Cross-Feature Combinations (Pairwise Feature Interactions)                         |   |
|   | - Marathi Edge-TTS + Pixabay Video B-Roll + Freesound SFX                                  |   |
|   | - English Deepgram Aura TTS + Unsplash Portrait Photo + Giphy Sticker                      |   |
|   | - Hindi Edge-TTS + Tavily News Real-Time Grounding + Nova-2 Word Captions                  |   |
|   | - Groq / Mistral Script Generation + Pixabay Video + Giphy Meme Overlay                    |   |
|   | - Async Job Queue -> Stage Progress Polling -> Final Multi-Asset Blueprint                 |   |
|   | - Deepgram Aura TTS Failure -> Edge-TTS Automatic Cascade with Preserved Media             |   |
|   | - Tavily Grounded Script -> Unsplash 4K Portrait -> Freesound Whoosh Transition           |   |
|   | - SQLite Sandbox Execution -> Real-Time Blueprint Stage Synchronization                    |   |
|   | - Dynamic Multi-Scene Stage Boundary Calibration against Audio Header Durations            |   |
|   | - Full 5-Provider Media Pack Active Concurrently (Pixabay, Unsplash, Giphy, Freesound, TV)|   |
|   +--------------------------------------------------------------------------------------------+   |
|                                                                                                    |
|   +--------------------------------------------------------------------------------------------+   |
|   | Tier 4: Real-World Application Scenarios (Full Vertical Reels Production)                  |   |
|   | - Tech News Reel: 2026 AI Breakthroughs (Tavily, Pixabay, Nova-2 Captions, 9:16 Vertical)  |   |
|   | - SQL Tutorial Short: Banking DENSE_RANK() (Sandbox DB, Animated Code, Marathi Voice, SFX)|   |
|   | - AI Coding Hack Reel: FastAPI Background Tasks (Python Code, Giphy Sticker, Deepgram Aura)|   |
|   | - Motivational Quote Reel: Daily Dev Wisdom (Unsplash 4K Portrait, Hindi Voice, Ambience) |   |
|   | - End-to-End Generation Job HTTP Lifecycle: POST queued -> Polled -> Completed Blueprint   |   |
|   | - Full MP4 Video Synthesis & Stream Verification: 1080x1920 (9:16), H.264, AAC Audio      |   |
|   +--------------------------------------------------------------------------------------------+   |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Test Execution Harness & Environment

- **Framework:** Python standard library `unittest` and `unittest.IsolatedAsyncioTestCase` for asynchronous coroutines.
- **Python Version:** Python 3.11+.
- **Video Rendering Backend:** FFmpeg 7.1 (`imageio_ffmpeg` binary `ffmpeg-win-x86_64-v7.1.exe` or system `ffmpeg`).
- **Isolation Policy:** 
  - Each test sets up and tears down temporary files in isolated directories (`tempfile.TemporaryDirectory`).
  - Unit and boundary tests cleanly mock remote network I/O (`requests.get`, `requests.post`) to ensure fast, deterministic, quota-free execution.
  - Video rendering integration tests synthesize real video files on the fly and verify streams with FFmpeg.

---

## 3. Test Runner Commands

### Run Full Test Suite
```bash
python -m unittest app/tests/test_e2e_video_maker.py
```

### Run Specific Test Tiers
```bash
# Run Tier 1 (Feature Coverage)
python -m unittest app.tests.test_e2e_video_maker.TestTier1_F1_UI_ClutterElimination app.tests.test_e2e_video_maker.TestTier1_F2_WorkspaceControls app.tests.test_e2e_video_maker.TestTier1_F3_ProgressAndLedger app.tests.test_e2e_video_maker.TestTier1_F4_ModelAdapters app.tests.test_e2e_video_maker.TestTier1_F5_TavilyNewsSearch app.tests.test_e2e_video_maker.TestTier1_F6_PixabayVideoProvider app.tests.test_e2e_video_maker.TestTier1_F7_UnsplashProvider app.tests.test_e2e_video_maker.TestTier1_F8_FreesoundProvider app.tests.test_e2e_video_maker.TestTier1_F9_DeepgramWordCaptions app.tests.test_e2e_video_maker.TestTier1_F10_DeepgramAuraAndEdgeTTS app.tests.test_e2e_video_maker.TestTier1_F11_GiphyProvider app.tests.test_e2e_video_maker.TestTier1_F12_AutomatedLiveApiContracts app.tests.test_e2e_video_maker.TestTier1_F13_EndToEndVideoSynthesis app.tests.test_e2e_video_maker.TestTier1_F14_ComprehensiveHarness app.tests.test_e2e_video_maker.TestTier1_F15_AdversarialResilience

# Run Tier 2 (Boundary & Corner Cases)
python -m unittest app.tests.test_e2e_video_maker.TestTier2_BoundaryAndCornerCases

# Run Tier 3 (Cross-Feature Combinations)
python -m unittest app.tests.test_e2e_video_maker.TestTier3_CrossFeatureCombinations

# Run Tier 4 (Real-World Application Scenarios)
python -m unittest app.tests.test_e2e_video_maker.TestTier4_RealWorldApplicationScenarios
```

---

## 4. Quality Gates & Acceptance Verification

1. **Aspect Ratio Verification:** Output video stream must be strictly vertical 9:16 (1080x1920) H.264 video.
2. **Audio Synchronization:** Stage boundaries must be calibrated to audio duration measured via MPEG audio frame headers.
3. **Authentic Asset Ledger:** Generated blueprints must contain authentic asset attribution ledgers identifying active engines and providers.
4. **UI Workspace Integrity:** Obsolete and dead controls (`#phoneAvatarPip`, orphan DOM IDs, hardcoded fake badges) must remain eliminated.
5. **Fault Resilience:** Pipeline must withstand remote API network timeouts and rate limits with clean fallback and zero unhandled server crashes.
