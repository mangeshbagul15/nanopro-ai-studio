# Prompt-Driven Cinematic Visuals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace generic orbiting-node scenes with prompt-specific AI imagery and optional AI video motion, synchronized with narration in a complete 9:16 MP4.

**Architecture:** The storyboard model will return a visual prompt and exact native overlays per narration scene. A strict scene-asset pipeline generates a portrait image for each scene, optionally animates it through Runway, and records progress through TaskManager. The browser composites scene assets, accurate overlays, narration, and subtitles; when Runway is unavailable, it moves the same generated image with scene-aware camera motion. If no topic-specific image can be generated, the job fails with a clear error instead of using a stock template.

**Tech Stack:** Python, FastAPI, TaskManager, existing Replicate/Pollinations image providers, existing Runway client, browser Canvas 2D, MediaRecorder, FFmpeg MP4 finalization.

**Spec:** `docs/superpowers/specs/2026-10-19-prompt-driven-cinematic-visuals-design.md`

## Global Constraints

- Generate one prompt-specific portrait keyframe per scene.
- Make at most one short Runway image-to-video request per scene; use an AI-image pan/zoom fallback when unavailable.
- Return an actionable error when topic-specific imagery cannot be generated; never substitute unrelated template imagery.
- Keep the full narration, subtitles, and visual scene timing synchronized.
- Keep preview and exported video at 9:16 and target 45–55 seconds, below 60 seconds where narration permits.
- Render exact code, equations, and labels as native overlays rather than relying on AI-rendered text.
- Keep changes within Universal Tech Video Maker and preserve other Studio sections.

## Review Focus

1. Missing/exhausted image provider returns a visible scene error and never writes a placeholder image — Task 2 tests this.
2. Runway unavailable or over quota continues with the same prompt-specific keyframe — Task 3 tests this.
3. Coding prompts keep code accurate/readable as an overlay while scene imagery remains illustrative — Tasks 1 and 5 test this.
4. A long-running scene job reports progress and terminal failure without returning a partial success — Task 4 tests this.
5. Unrelated prompts cannot share cached visuals and export still includes every narration scene under 60 seconds when duration allows — Tasks 3 and 6 test this.

---

### Task 1: Expand the AI scene contract

**Files:**
- Modify: `app/video_maker/sql_short_engine.py`
- Test: `app/tests/test_sql_short_full_length_export.py`

**Interfaces:**
- Produces each scene's `visual_prompt: str`, `continuity: str`, and `overlay_items: list[dict]` alongside narration, visual description, composition, motion, entities, and relationships.
- Each overlay item has `kind` (`label`, `code`, or `formula`), `content`, and normalized `x`/`y` anchor values from 0 to 1.

- [ ] **Step 1: Write failing tests** named `test_scene_prompt_contains_subject_action_and_visual_continuity` and `test_code_overlay_is_separate_from_generated_image_text`. Assert schema fields, prompt instructions that the shot depict the narrated mechanism, and exact overlay fields.
- [ ] **Step 2: Run** `python app/tests/test_sql_short_full_length_export.py -v`; expect the new contract assertions to fail.
- [ ] **Step 3: Implement** the scene prompt and validation in `generate_short_prompt_async`; request 5–6 scenes, concrete subject/action/camera details, continuity, and native text overlays. Reject missing/empty `visual_prompt` or invalid overlay anchors; keep the one simplified model retry.
- [ ] **Step 4: Re-run** the targeted test file; expect the contract tests to pass.
- [ ] **Step 5: Commit** `feat(video): add cinematic visual prompts to scenes`.

### Task 2: Add strict scene-image generation

**Files:**
- Modify: `app/agents/image_agent.py`
- Test: `app/tests/test_scene_image_generation.py` (create)

**Interfaces:**
- Extend `ImageCreationAgent.generate_image(prompt, style="modern_tech", width=1080, height=1920, allow_local_fallback=True, preserve_prompt=False) -> dict`.
- Successful result includes `file_path`, `filename`, `provider`, and provider `source_url` when available.
- With `allow_local_fallback=False`, raise a descriptive `RuntimeError` if Replicate and Pollinations both fail; never create the current Pillow/FFmpeg text card.
- With `preserve_prompt=True`, do not append generic “ArtStation/8k” phrases; retain the exact model-produced visual brief plus only portrait/quality constraints.

- [ ] **Step 1: Write failing tests** named `test_strict_scene_mode_raises_instead_of_creating_placeholder`, `test_scene_mode_preserves_visual_prompt`, and `test_scene_image_returns_provider_url` using provider fakes.
- [ ] **Step 2: Run** `python app/tests/test_scene_image_generation.py -v`; expect failure because strict mode and provider URL are absent.
- [ ] **Step 3: Implement** the optional arguments without changing existing thumbnail callers; return the public source URL for Replicate/Pollinations and keep the existing local fallback only for callers that permit it.
- [ ] **Step 4: Re-run** the new tests and existing image-agent tests; expect both paths to pass.
- [ ] **Step 5: Commit** `feat(video): add strict prompt-specific image generation`.

### Task 3: Build the per-scene asset pipeline

**Files:**
- Create: `app/video_maker/scene_visual_pipeline.py`
- Test: `app/tests/test_scene_visual_pipeline.py` (create)

**Interfaces:**
- Provide `async def generate_scene_assets(scenes: list[dict], job_id: str, public_base_url: str, progress_callback: Callable[[str, int], None]) -> list[dict]`.
- Return one item per scene: `scene_id`, `image_url`, optional `video_url`, `provider`, `duration`, and `prompt_hash`.
- Write normalized 9:16 assets under `data/assets/video_scenes/` so the existing `/assets` static mount can serve them.

- [ ] **Step 1: Write failing tests** named `test_generates_distinct_cached_keyframes_per_visual_prompt`, `test_runway_failure_keeps_same_scene_image`, and `test_image_failure_stops_without_stock_substitution`. Fake the image and Runway clients; assert prompts hash to separate cache entries and progress callback reports each scene.
- [ ] **Step 2: Run** `python app/tests/test_scene_visual_pipeline.py -v`; expect import/interface failures.
- [ ] **Step 3: Implement** bounded parallel keyframe generation (maximum two concurrent scenes), hash-based cache keys from `visual_prompt` plus provider settings, portrait normalization, optional Runway image-to-video using the public asset URL, and per-scene final-frame duration metadata. Poll Runway tasks through `runway_video.get_task_status`; on Runway errors retain that scene's AI image; on image errors stop with the scene number and prompt title.
- [ ] **Step 4: Re-run** the new tests; expect distinct assets, fallback, and fail-closed behavior to pass.
- [ ] **Step 5: Commit** `feat(video): generate prompt-specific scene assets`.

### Task 4: Add observable asynchronous generation jobs

**Files:**
- Modify: `main.py`
- Test: `app/tests/test_sql_video_generation_jobs.py` (create)

**Interfaces:**
- Add `POST /api/sql_video/generate_prompt_job`, returning `{status: "queued", job_id}`.
- Add `GET /api/sql_video/generation_jobs/{job_id}`, returning `{status, stage, progress, result_data, error_message}` from TaskManager.
- Background execution calls the existing blueprint generator, then `generate_scene_assets`, updates TaskManager stages, and uses `set_job_completed` or `set_job_failed`.
- Preserve the existing synchronous `/api/sql_video/generate_prompt` response for existing callers; both routes must use the same scene-asset pipeline and response schema.

- [ ] **Step 1: Write failing tests** named `test_generation_job_returns_id_and_polls_progress`, `test_generation_job_returns_complete_blueprint_and_assets`, and `test_generation_job_reports_scene_failure`. Assert lifecycle and complete result fields.
- [ ] **Step 2: Run** `python app/tests/test_sql_video_generation_jobs.py -v`; expect new route failures.
- [ ] **Step 3: Implement** the background job routes with unique job ids, explicit storyboard/image/motion/audio/composition stage progress, and terminal result/error payloads.
- [ ] **Step 4: Re-run** the route tests; expect queued, running, completed, and failed states to pass.
- [ ] **Step 5: Commit** `feat(video): track cinematic generation job progress`.

### Task 5: Composite generated scene assets in the player

**Files:**
- Modify: `app/ui/sql_video_js.py`
- Modify: `app/ui/sql_video_workspace.py`
- Test: `app/tests/test_sql_short_full_length_export.py`

**Interfaces:**
- Client polls the job API and displays returned `stage`/`progress` until completion or failure.
- Add `loadPromptSceneAssets(scene_assets) -> Promise<void>` and store loaded image/video elements by `scene_id` in `sqlShortState`.
- `renderPromptDrivenVisual` draws the active AI image/video as the full scene background; image-only scenes receive subtle camera motion. Render `overlay_items` from model data as native canvas text/code. Generic node-orbit rendering must not run when a scene asset exists.

- [ ] **Step 1: Write failing tests** named `test_generate_ui_polls_scene_job_progress`, `test_scene_renderer_uses_ai_assets_and_native_overlays`, and `test_asset_scene_skips_generic_orbit_nodes`. Assert 9:16 sizing and final MP4 export remain wired.
- [ ] **Step 2: Run** `python app/tests/test_sql_short_full_length_export.py -v`; expect the new player assertions to fail.
- [ ] **Step 3: Implement** job polling, honest stage labels, image/video preload, audio-time-based per-scene seeking, image camera movement, code/label overlays, and accessible errors; keep Canvas `captureStream` and complete MP4 download.
- [ ] **Step 4: Run** the test file and extract the JavaScript from `get_sql_video_js()` for `node --check`; expect both checks to pass.
- [ ] **Step 5: Commit** `feat(video): render scene assets with synced narration`.

### Task 6: Verify prompt differences and final export

**Files:**
- Test: `app/tests/test_scene_visual_pipeline.py`
- Test: `app/tests/test_sql_short_full_length_export.py`

- [ ] **Step 1: Add integration-style tests** named `test_solar_and_coding_prompts_produce_different_scene_assets` and `test_generated_scene_assets_cover_the_complete_narration_timeline`. Use fake providers and assert different scene prompts/hashes, 9:16 assets, no placeholder shapes, and timeline coverage through audio end.
- [ ] **Step 2: Run** `python app/tests/test_scene_visual_pipeline.py -v` and `python app/tests/test_sql_short_full_length_export.py -v`; expect all tests to pass.
- [ ] **Step 3: Run** `python -m py_compile main.py app/agents/image_agent.py app/video_maker/sql_short_engine.py app/video_maker/scene_visual_pipeline.py`; expect exit code 0.
- [ ] **Step 4: Review** `git diff --check` and confirm no unrelated files or secrets were added.
- [ ] **Step 5: Test** Solar panel and a coding prompt on Render, verify AI-authored different scene assets, complete audio sync, 9:16 playback, and final MP4 download; record duration and any provider fallback.
- [ ] **Step 6: Commit** `test(video): verify prompt-specific cinematic exports`.

## Self-review

- **Spec coverage:** Scene semantics/continuity and native overlays are covered in Tasks 1 and 5; AI imagery, optional Runway motion, cache, and provider failures in Tasks 2–3; observable progress and errors in Task 4; 9:16, full narration, under-60 target, final MP4, and Solar/coding examples in Tasks 5–6.
- **Task boundaries:** Each backend, provider, orchestration, API, browser, and end-to-end layer has its own test deliverable and commit.
- **Cross-task interfaces:** Scene fields flow from Task 1 to Task 3 and Task 5; `scene_assets` flow from Task 3 through Task 4 to Task 5; TaskManager progress is polled through the exact route fields in Task 4.
- **Execution constraint:** Runway public URLs are valid only when the app host is reachable by Runway; local/loopback generation skips Runway and uses the generated image path. Render image URLs must remain same-origin and publicly readable for Canvas export.
