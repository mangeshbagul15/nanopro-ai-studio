# Prompt-Driven Cinematic Visuals — Design

**Date:** 2026-10-19
**Status:** Awaiting user review
**Scope:** Universal Tech Video Maker (`#universal_tech_video`)

## Problem

The current video path produces topic-related narration and scene metadata, but the active canvas renderer reduces the scene to a title, description, a small set of generic geometric nodes, and connector lines. Scene descriptions are not rendered as the actual visual action. As a result, unrelated topics share the same visual grammar and can look like two orbiting objects even when the narration is accurate.

## User outcome

A student should be able to understand a prompt-specific concept by watching its visuals while hearing the narration. A solar-panel scene should depict a panel, light, semiconductor layers, electron movement, and electrical output as the narration explains them. A coding scene should show the actual code or runtime behavior described by the prompt. There should be no fixed topic storyboard or generic orbital-node substitute.

The output remains vertical 9:16, narration-synchronized, and targeted below 60 seconds.

## Design

### 1. Build a scene plan from meaning

The language model continues to parse the user's prompt and narration, and now produces a visual brief for each narration beat. Each brief contains:

- the concept being taught and the narration sentence it supports;
- a concrete visual prompt for the scene's environment, objects, action, and camera framing;
- a separate accurate overlay payload for labels, equations, or code, so image models do not need to draw readable text;
- a continuity description for recurring objects and visual style;
- the scene's narration timing and transition intent.

The model must choose visuals from the actual subject and explain invisible processes using clear educational cutaways or diagrams grounded in the prompt. It must not invent unrelated characters, planets, or metaphors.

### 2. Generate prompt-specific scene imagery

For each scene, generate one portrait keyframe with the existing image-generation integration. Keep generated imagery free of text; render accurate labels and code as native overlays from the model's structured payload.

When the existing Runway integration and credits are available, submit the scene keyframe for a short image-to-video motion pass. Store the resulting same-origin scene asset for browser playback/export. If video generation is unavailable, animate the generated keyframe with scene-aware camera movement and transitions. This still uses the prompt-specific scene image; it does not revert to generic circles or nodes.

If neither scene image generation nor retrieval succeeds, return a clear generation error with retry guidance. Do not emit an unrelated template video.

### 3. Composite scenes with narration

The client uses each scene asset as the visual layer for its narration interval and adds synchronized subtitles plus accurate labels/code overlays. Use scene durations derived from the synthesized audio. Video clips may end before the scene narration; hold their final frame with a subtle camera move until the next scene. Keep the complete output 9:16 and aim for a 45–55-second narration, never intentionally truncating speech.

### 4. Keep generation observable

The UI shows separate progress for storyboard, scene imagery, optional motion generation, audio, and final composition. Provider failures are visible and identify which scene needs retry. Cache generated scene assets by a hash of the prompt, language, visual brief, and provider settings to avoid regenerating unchanged scenes.

## Data flow

1. User prompt and language enter the storyboard endpoint.
2. The model returns validated narration and one visual brief per scene.
3. The backend generates or retrieves portrait keyframes; optional Runway jobs animate them.
4. Same-origin asset URLs and per-scene durations are returned to the video UI.
5. The UI composites those assets with timed narration, subtitles, and exact text/code overlays.
6. The existing MP4 finalization route returns the final 9:16 video download.

## Failure behavior

- Invalid storyboard JSON: retry once with a simplified schema, then show an actionable error.
- Image generation failure for a scene: retry that scene once; if it still fails, stop generation and identify the scene. Do not substitute a stock visual.
- Runway unavailable, rate limited, or out of credits: keep the generated scene image and apply cinematic camera movement; continue without Runway.
- Audio or MP4 composition failure: show the failing stage and preserve generated assets for retry.

## Cost and latency

A typical video uses one image-generation call per scene and up to one short image-to-video call per scene. This can cost more and take longer than the current canvas-only renderer. Use existing configured providers, bounded per-scene retries, status polling, and content-addressed caching. Never silently fan out to unrelated providers or reuse a different prompt's assets.

## Acceptance checks

- A solar-panel prompt produces visible solar hardware, sunlight, energy conversion, and electrical output in the corresponding narration beats; it must not produce planets or generic node orbits.
- A coding prompt shows the requested language/code or runtime behavior accurately, with readable code rendered as native text.
- Two unrelated prompts produce clearly different scene assets and scene actions.
- Narration, subtitles, and scene timing remain synchronized; tested output targets under 60 seconds.
- Output and preview are 9:16, and Generate ultimately downloads the complete MP4.
- Runway-disabled generation still uses prompt-specific AI imagery and understandable camera motion.
- If imagery cannot be produced, the UI reports an actionable error instead of a generic clip.

## Scope boundaries

This design changes the Universal Tech Video Maker's scene generation and rendering pipeline only. It does not change other Studio sections, database integrations, or SQL learning features outside this video workflow. It does not introduce hard-coded topic templates.
