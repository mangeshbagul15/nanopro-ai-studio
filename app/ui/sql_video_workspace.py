# -*- coding: utf-8 -*-

"""Responsive workspace for prompt-led technical lessons and 9:16 video export."""



def get_sql_video_workspace_html() -> str:

 return """

 <style>

 /* =========================================================================

 ↔️ FULL VIEW HORIZONTAL SCROLLBAR & TECH CONTAINER

 ========================================================================= */

 .vfx-horizontal-scroll-container {

 width: 100%;

 max-width: 100%;

 overflow-x: auto !important;

 overflow-y: visible;

 padding-bottom: 24px;

 box-sizing: border-box;

 scroll-behavior: smooth;

 }

 .vfx-horizontal-scroll-container::-webkit-scrollbar {

 height: 12px;

 background: #070B16;

 border-radius: 8px;

 }

 .vfx-horizontal-scroll-container::-webkit-scrollbar-track {

 background: rgba(15, 23, 42, 0.9);

 border: 1px solid rgba(56, 189, 248, 0.3);

 border-radius: 8px;

 }

 .vfx-horizontal-scroll-container::-webkit-scrollbar-thumb {

 background: linear-gradient(90deg, #0284C7, #38BDF8, #10B981);

 border-radius: 8px;

 border: 2px solid #070B16;

 box-shadow: 0 0 14px rgba(56, 189, 248, 0.6);

 }

 .vfx-horizontal-scroll-container::-webkit-scrollbar-thumb:hover {

 background: linear-gradient(90deg, #38BDF8, #818CF8, #34D399);

 }



 .vfx-video-root {

 font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

 color: #F8FAFC;

 width: 100%;

 max-width: 1440px;

 margin: 0 auto;

 box-sizing: border-box;

 }



 /* =========================================================================

 KOKONUT UI, BLACKLIST UI & MOTION.DEV MODERN STYLING

 ========================================================================= */

 :root {

 --spring-smooth: cubic-bezier(0.16, 1, 0.3, 1);

 --spring-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

 --kokonut-glow: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.25), transparent 70%);

 --blacklist-dark: #050811;

 --blacklist-card: rgba(10, 16, 32, 0.88);

 --blacklist-border: rgba(56, 189, 248, 0.28);

 }



 /* Kokonut UI Frosted Glass Card with Hover Sheen */

 .kokonut-card {

 background: var(--blacklist-card);

 border: 1.5px solid var(--blacklist-border);

 border-radius: 16px;

 backdrop-filter: blur(20px);

 -webkit-backdrop-filter: blur(20px);

 box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);

 position: relative;

 overflow: hidden;

 transition: all 0.35s var(--motion-smooth);

 }

 .kokonut-card:hover {

 border-color: rgba(56, 189, 248, 0.65);

 box-shadow: 0 16px 48px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.25);

 transform: translateY(-2px);

 }



 /* Kokonut UI Shimmering Conic Glow Sheen */

 .kokonut-card::after {

 content: '';

 position: absolute;

 top: 0; left: 0; right: 0;

 height: 2px;

 background: linear-gradient(90deg, transparent, #38BDF8, #10B981, #8B5CF6, transparent);

 opacity: 0.8;

 }



 /* Kokonut UI Pill Badge with Pulsing Neon Dot */

 .kokonut-badge {

 display: inline-flex;

 align-items: center;

 gap: 6px;

 padding: 3px 10px;

 border-radius: 9999px;

 font-size: 10.5px;

 font-weight: 700;

 letter-spacing: 0.3px;

 background: rgba(15, 23, 42, 0.85);

 border: 1px solid rgba(56, 189, 248, 0.3);

 color: #F8FAFC;

 }

 .kokonut-pulse-dot {

 width: 6px;

 height: 6px;

 border-radius: 50%;

 background: #10B981;

 box-shadow: 0 0 8px #10B981;

 animation: kokonutDotPulse 2s infinite ease-in-out;

 }

 @keyframes kokonutDotPulse {

 0%, 100% { opacity: 1; transform: scale(1); }

 50% { opacity: 0.35; transform: scale(0.85); }

 }



 /* Blacklist UI Cyber Dark HUD Container */

 .blacklist-hud {

 background: var(--blacklist-dark);

 border: 1.5px solid #1E293B;

 border-radius: 12px;

 font-family: 'JetBrains Mono', 'Fira Code', monospace;

 position: relative;

 }

 .blacklist-tag {

 font-family: 'JetBrains Mono', 'Fira Code', monospace;

 font-size: 10px;

 font-weight: 800;

 letter-spacing: 0.5px;

 color: #38BDF8;

 }



 /* Motion.dev Tactile Spring Button Feedback */

 .motion-spring-btn {

 transition: transform 0.2s var(--spring-bounce), box-shadow 0.2s var(--spring-smooth);

 cursor: pointer;

 }

 .motion-spring-btn:hover {

 transform: translateY(-2px) scale(1.01);

 box-shadow: 0 8px 24px rgba(56, 189, 248, 0.35);

 }

 .motion-spring-btn:active {

 transform: translateY(1px) scale(0.97);

 }



 /* Anime.js Kinetic Typography Highlights */

 .kinetic-subtitle-glow {

 text-shadow: 0 0 16px rgba(56, 189, 248, 0.8), 0 2px 4px rgba(0, 0, 0, 0.9);

 }



 /* 2026 VFX Holographic Cyber Studio Styling */

 .vfx-video-root {

 font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

 color: #F8FAFC;

 }



 .vfx-glow-box {

 background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(7, 11, 22, 0.98));

 border: 1px solid rgba(56, 189, 248, 0.35);

 border-radius: 14px;

 box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.12);

 backdrop-filter: blur(12px);

 transition: border-color 0.3s ease, box-shadow 0.3s ease;

 }

 .vfx-glow-box:hover {

 border-color: rgba(56, 189, 248, 0.65);

 box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8), 0 0 35px rgba(56, 189, 248, 0.2);

 }



 .vfx-dock-grid {

 display: grid;

 grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));

 gap: 12px;

 margin-bottom: 18px;

 }



 .vfx-dock-card {

 background: rgba(11, 19, 43, 0.85);

 border: 1.5px solid #1E2D4A;

 border-radius: 10px;

 padding: 12px 14px;

 transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

 display: flex;

 flex-direction: column;

 justify-content: space-between;

 position: relative;

 overflow: hidden;

 }

 .vfx-dock-card::before {

 content: '';

 position: absolute;

 top: 0;

 left: 0;

 right: 0;

 height: 2px;

 background: linear-gradient(90deg, transparent, #38BDF8, transparent);

 opacity: 0;

 transition: opacity 0.3s ease;

 }

 .vfx-dock-card:hover {

 border-color: #38BDF8;

 transform: translateY(-2px);

 box-shadow: 0 8px 25px rgba(56, 189, 248, 0.2);

 }

 .vfx-dock-card:hover::before {

 opacity: 1;

 }



 .vfx-dock-title {

 font-size: 11px;

 font-weight: 800;

 letter-spacing: 0.5px;

 text-transform: uppercase;

 display: flex;

 align-items: center;

 gap: 6px;

 margin-bottom: 8px;

 }



 .vfx-dock-select {

 width: 100%;

 background: #070B16;

 border: 1px solid #283C62;

 color: #F8FAFC;

 font-size: 11.5px;

 font-weight: 700;

 border-radius: 6px;

 padding: 7px 10px;

 outline: none;

 transition: border-color 0.2s ease;

 cursor: pointer;

 }

 .vfx-dock-select:focus {

 border-color: #38BDF8;

 box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);

 }



 .vfx-quick-chip {

 font-size: 10px;

 padding: 4px 10px;

 border-radius: 20px;

 background: rgba(15, 23, 42, 0.8);

 border: 1px solid #1E2D4A;

 color: #94A3B8;

 cursor: pointer;

 transition: all 0.2s ease;

 display: inline-flex;

 align-items: center;

 gap: 4px;

 white-space: nowrap;

 }

 .vfx-quick-chip:hover {

 background: rgba(56, 189, 248, 0.15);

 border-color: #38BDF8;

 color: #38BDF8;

 transform: scale(1.03);

 }



 /* Studio Main 3-Column Grid */

 .vfx-studio-grid {

 display: grid;

 grid-template-columns: 1.15fr 360px 1fr;

 gap: 20px;

 align-items: start;

 }



 @media (max-width: 1200px) {

 .vfx-studio-grid {

 grid-template-columns: 1fr 360px;

 }

 }

 @media (max-width: 900px) {

 .vfx-studio-grid {

 grid-template-columns: 1fr;

 }

 }



 /* Audio wave animation: ONLY active when playing */

 @keyframes wavePulse {

 0%, 100% { height: 4px; opacity: 0.4; }

 50% { height: 16px; opacity: 1; }

 }

 .vfx-wave-bar {

 width: 3px;

 height: 4px;

 background: #10B981;

 border-radius: 2px;

 transition: height 0.2s ease;

 }

 .vfx-wave-bar:nth-child(2) { background: #38BDF8; }

 .vfx-wave-bar:nth-child(3) { background: #8B5CF6; }

 .vfx-wave-bar:nth-child(4) { background: #EC4899; }

 .vfx-wave-bar.playing,

 .vfx-wave-bar.active,

 .is-playing .vfx-wave-bar {

 animation: wavePulse 1.2s ease-in-out infinite;

 }

 .vfx-wave-bar.playing:nth-child(2),

 .vfx-wave-bar.active:nth-child(2),

 .is-playing .vfx-wave-bar:nth-child(2) { animation-delay: 0.2s; }

 .vfx-wave-bar.playing:nth-child(3),

 .vfx-wave-bar.active:nth-child(3),

 .is-playing .vfx-wave-bar:nth-child(3) { animation-delay: 0.4s; }

 .vfx-wave-bar.playing:nth-child(4),

 .vfx-wave-bar.active:nth-child(4),

 .is-playing .vfx-wave-bar:nth-child(4) { animation-delay: 0.6s; }



 /* Language Buttons */

 .sql-lang-btn {

 font-size: 11px;

 padding: 8px 14px;

 border-radius: 8px;

 cursor: pointer;

 border: 1.5px solid #1E2D4A;

 background: #070B16;

 color: #94A3B8;

 transition: all 0.2s ease;

 display: flex;

 align-items: center;

 gap: 6px;

 font-weight: 700;

 flex: 1;

 justify-content: center;

 }

 .sql-lang-btn:hover {

 border-color: #38BDF8;

 color: #F8FAFC;

 }

 .sql-lang-btn.active {

 background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25));

 border: 2px solid #38BDF8;

 color: #38BDF8;

 box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);

 }

 .sql-lang-btn .btn-check { display: none; font-weight: 900; }

 .sql-lang-btn.active .btn-check { display: inline-block; }



 /* Pulse Laser Button */

 @keyframes laserPulse {

 0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.5), inset 0 0 15px rgba(99, 102, 241, 0.5); }

 50% { box-shadow: 0 0 25px rgba(56, 189, 248, 0.8), inset 0 0 25px rgba(16, 185, 129, 0.6); }

 100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.5), inset 0 0 15px rgba(99, 102, 241, 0.5); }

 }

 .vfx-laser-btn {

 animation: laserPulse 2.5s infinite;

 }



 /* Quick Topic Chips */

 .vfx-chips-dock {

 display: flex;

 flex-wrap: wrap;

 gap: 6px;

 margin-bottom: 10px;

 }

 .vfx-quick-chip {

 font-size: 11px;

 font-weight: 600;

 padding: 5px 12px;

 border-radius: 20px;

 background: rgba(15, 23, 42, 0.85);

 border: 1px solid #1E2D4A;

 color: #94A3B8;

 cursor: pointer;

 transition: all 0.2s var(--spring-smooth);

 display: inline-flex;

 align-items: center;

 gap: 5px;

 white-space: nowrap;

 }

 .vfx-quick-chip:hover {

 background: rgba(56, 189, 248, 0.15);

 border-color: #38BDF8;

 color: #38BDF8;

 transform: translateY(-1px);

 }



 /* Live Media Provider Toggles */

 .vfx-provider-grid {

 display: grid;

 grid-template-columns: 1fr 1fr;

 gap: 8px;

 }

 .provider-toggle-card {

 display: flex;

 align-items: center;

 gap: 8px;

 font-size: 11px;

 font-weight: 700;

 color: #CBD5E1;

 cursor: pointer;

 background: rgba(15, 23, 42, 0.7);

 padding: 8px 10px;

 border-radius: 8px;

 border: 1px solid #1E2D4A;

 transition: all 0.2s ease;

 user-select: none;

 }

 .provider-toggle-card:hover {

 border-color: #38BDF8;

 color: #F8FAFC;

 }

 .provider-toggle-card input[type="checkbox"] {

 width: 15px;

 height: 15px;

 accent-color: #10B981;

 cursor: pointer;

 }



 /* 5-Step Pipeline Progress */

 .vfx-pipeline-tracker {

 display: flex;

 flex-direction: column;

 gap: 6px;

 background: rgba(11, 19, 43, 0.95);

 border: 1.5px solid rgba(56, 189, 248, 0.35);

 border-radius: 10px;

 padding: 12px 14px;

 margin-top: 10px;

 }

 .pipeline-step-row {

 display: flex;

 align-items: center;

 gap: 10px;

 font-size: 11.5px;

 color: #94A3B8;

 transition: color 0.2s ease;

 }

 .pipeline-step-row.active {

 color: #38BDF8;

 font-weight: 700;

 }

 .pipeline-step-row.completed {

 color: #10B981;

 font-weight: 600;

 }

 .pipeline-step-icon {

 width: 18px;

 height: 18px;

 display: flex;

 align-items: center;

 justify-content: center;

 font-size: 12px;

 }

 #vfxHorizontalScrollContainer {
 overflow-x: hidden !important;
 padding: 18px clamp(12px, 2.4vw, 36px) 36px;
 background:
 radial-gradient(ellipse at 10% 0%, rgba(201, 239, 112, 0.09), transparent 34rem),
 radial-gradient(ellipse at 92% 18%, rgba(255, 120, 95, 0.06), transparent 28rem),
 #101411;
 scrollbar-width: thin;
 scrollbar-color: #68764e #171d18;
 }

 .vfx-video-root {
 max-width: 1540px;
 color: #eef1e6;
 font-family: "Avenir Next", "Segoe UI", sans-serif !important;
 }

 .studio-masthead {
 display: flex;
 align-items: center;
 justify-content: space-between;
 gap: 20px;
 margin: 0 0 18px;
 padding: 20px 24px;
 border: 1px solid #394239;
 border-left: 4px solid #c9ef70;
 border-radius: 14px;
 background: linear-gradient(110deg, #1a201b 0%, #171b18 62%, #20251e 100%);
 box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
 }

 .studio-brand {
 display: flex;
 align-items: center;
 gap: 16px;
 min-width: 0;
 }

 .studio-mark {
 display: grid;
 width: 48px;
 height: 48px;
 flex: 0 0 48px;
 place-items: center;
 border: 1px solid rgba(201, 239, 112, 0.45);
 border-radius: 12px;
 background: rgba(201, 239, 112, 0.1);
 color: #c9ef70;
 font: 800 17px "Avenir Next", "Segoe UI", sans-serif;
 letter-spacing: -0.08em;
 }

 .studio-hero-kicker {
 margin-bottom: 4px;
 color: #c9ef70;
 font: 700 10px "SFMono-Regular", Consolas, monospace;
 letter-spacing: 0.14em;
 text-transform: uppercase;
 }

 .studio-header-title {
 margin: 0;
 color: #f3f1e8;
 font: 600 clamp(21px, 2.2vw, 30px)/1.12 Georgia, "Times New Roman", serif;
 letter-spacing: -0.035em;
 }

 .studio-header-copy {
 margin-top: 6px;
 color: #a9b0a4;
 font-size: 12px;
 line-height: 1.5;
 }

 .studio-header-status {
 display: flex;
 flex-wrap: wrap;
 justify-content: flex-end;
 gap: 8px;
 }

 .studio-header-status .kokonut-badge {
 padding: 7px 10px;
 border: 1px solid #465044 !important;
 border-radius: 999px;
 background: #20271f !important;
 color: #dce5d2 !important;
 font-size: 10px;
 letter-spacing: 0.04em;
 }

 .vfx-studio-grid {
 grid-template-columns: minmax(0, 1.13fr) minmax(300px, 0.78fr) minmax(245px, 0.66fr);
 gap: 16px;
 align-items: start;
 }

 #sqlStudioMainGrid > .vfx-glow-box:first-child,
 #exportCardContainer .vfx-glow-box {
 border: 1px solid #394239 !important;
 border-radius: 14px;
 background: #181d19 !important;
 box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2) !important;
 backdrop-filter: none;
 }

 #sqlStudioMainGrid > .vfx-glow-box:first-child:hover,
 #exportCardContainer .vfx-glow-box:hover {
 transform: none;
 border-color: #59664d !important;
 box-shadow: 0 18px 44px rgba(0, 0, 0, 0.28) !important;
 }

 #sqlShortQuestion {
 min-height: 150px;
 border: 1px solid #465044 !important;
 border-radius: 10px !important;
 background: #111612 !important;
 color: #f0f2e9 !important;
 font: 13px/1.65 "SFMono-Regular", Consolas, monospace !important;
 box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.18) !important;
 }

 #sqlShortQuestion:focus,
 .vfx-video-root select:focus,
 .vfx-video-root button:focus-visible,
 .vfx-video-root input:focus-visible {
 outline: 2px solid #c9ef70;
 outline-offset: 2px;
 }

 #sqlStudioMainGrid > section[aria-labelledby] > div[style*="background"] {
 border-color: #394239 !important;
 background: #1d241e !important;
 }

 #sqlStudioMainGrid > section[aria-labelledby] [style*="color: #38BDF8"],
 #sqlStudioMainGrid > section[aria-labelledby] [style*="color: #10B981"] {
 color: #c9ef70 !important;
 }

 #sqlStudioMainGrid > section[aria-labelledby] select,
 #sqlExportResolution,
 #sqlShortSpeed {
 border-color: #465044 !important;
 background: #111612 !important;
 color: #eef1e6 !important;
 }

 #activePatternBadge,
 #modelLatencyBadge,
 #modelSpecsQuickPill,
 #modelSpecsNameText,
 #sqlVideoGenerationStatus {
 color: #c9ef70 !important;
 }

 .vfx-quick-chip {
 border-color: #3b4439;
 background: #202720;
 color: #d1d7ca;
 }

 .vfx-quick-chip:hover {
 border-color: #c9ef70;
 background: rgba(201, 239, 112, 0.1);
 color: #dfff9b;
 }

 .sql-lang-btn {
 border-color: #3b4439;
 background: #141a15;
 color: #b6beb1;
 }

 .sql-lang-btn.active {
 border-color: #c9ef70;
 background: rgba(201, 239, 112, 0.11);
 color: #dfff9b;
 box-shadow: inset 0 0 0 1px rgba(201, 239, 112, 0.18);
 }

 .provider-toggle-card {
 border-color: #394239;
 background: #202720;
 color: #d4d9ce;
 }

 .provider-toggle-card input[type="checkbox"] {
 accent-color: #c9ef70;
 }

 #btnGenerateSqlBlueprint,
 #btnDownloadShortVideo {
 border: 1px solid #d5f687 !important;
 border-radius: 10px !important;
 background: #c9ef70 !important;
 box-shadow: none !important;
 color: #172012 !important;
 letter-spacing: 0.03em;
 }

 #btnGenerateSqlBlueprint:hover,
 #btnDownloadShortVideo:hover {
 background: #d9ff85 !important;
 box-shadow: 0 8px 26px rgba(201, 239, 112, 0.16) !important;
 }

 #btnServerReelFast {
 border-color: #66503e !important;
 background: #241e19 !important;
 color: #f3bc79 !important;
 }

 #sqlStudioMainGrid > .studio-preview-column {
 align-items: stretch !important;
 min-width: 0;
 padding: 8px 4px;
 }

 #phoneBezel {
 width: min(100%, 336px) !important;
 height: auto !important;
 aspect-ratio: 9 / 16;
 border: 1px solid #58634c !important;
 border-radius: 24px !important;
 background: #080b08 !important;
 box-shadow: 0 24px 62px rgba(0, 0, 0, 0.5), 0 0 0 6px rgba(30, 37, 29, 0.72) !important;
 }

 #sqlStudioMainGrid > .studio-preview-column > div,
 #sqlStudioMainGrid > .studio-preview-column > .studio-player-controls {
 width: min(100%, 336px) !important;
 max-width: 336px !important;
 align-self: center;
 }

 #sqlShortScrubber {
 accent-color: #c9ef70 !important;
 }

 #exportCardContainer {
 min-width: 0;
 }

 #exportCardContainer .vfx-glow-box {
 border-color: #59664d !important;
 }

 #aiAttributionLedgerContainer {
 border: 1px solid #394239 !important;
 border-radius: 12px;
 background: #141a15 !important;
 box-shadow: none !important;
 }

 #exportCardContainer .vfx-glow-box > div:first-child > span:first-child {
 color: #c9ef70 !important;
 }

 .vfx-pipeline-tracker {
 border: 1px solid #394239;
 border-radius: 10px;
 background: #121713;
 }

 .pipeline-step-row.active {
 color: #dfff9b;
 }

 .pipeline-step-row.completed {
 color: #a8d87a;
 }

 .vfx-video-root button,
 .vfx-video-root select,
 .vfx-video-root input,
 .vfx-video-root textarea {
 font-family: inherit;
 }

 @media (max-width: 1400px) {
 .vfx-studio-grid {
 grid-template-columns: minmax(0, 1fr) minmax(300px, 0.78fr);
 }

 #exportCardContainer {
 grid-column: 1 / -1;
 display: grid !important;
 grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
 align-items: start;
 }
 }

 @media (max-width: 760px) {
 #vfxHorizontalScrollContainer {
 padding: 12px 10px 24px;
 }

 .studio-masthead {
 align-items: flex-start;
 flex-direction: column;
 padding: 17px;
 }

 .studio-header-status {
 justify-content: flex-start;
 }

 .vfx-studio-grid {
 grid-template-columns: minmax(0, 1fr);
 gap: 12px;
 }

 #exportCardContainer {
 grid-column: auto;
 display: flex !important;
 }

 #sqlStudioMainGrid > .studio-preview-column {
 padding: 4px 0;
 }

 #sqlStudioMainGrid > .vfx-glow-box:first-child {
 padding: 16px !important;
 }
 }

 @media (prefers-reduced-motion: reduce) {
 .vfx-video-root *,
 .vfx-video-root *::before,
 .vfx-video-root *::after {
 animation-duration: 0.01ms !important;
 animation-iteration-count: 1 !important;
 scroll-behavior: auto !important;
 transition-duration: 0.01ms !important;
 }
 }

 </style>

 <style>
 .vfx-horizontal-scroll-container {
 overflow-x: hidden !important;
 overflow-y: visible;
 padding: clamp(12px, 2.2vw, 32px);
 scrollbar-width: none;
 background:
 radial-gradient(ellipse at 12% 0%, rgba(245, 158, 11, 0.08), transparent 34rem),
 radial-gradient(ellipse at 88% 28%, rgba(34, 211, 238, 0.07), transparent 38rem);
 }

 .vfx-horizontal-scroll-container::-webkit-scrollbar { display: none; }

 .vfx-video-root {
 max-width: 1440px;
 color: #F4F1E8;
 font-family: "Avenir Next", "Segoe UI", sans-serif !important;
 }

 .studio-masthead {
 position: relative;
 overflow: hidden;
 margin-bottom: 22px;
 padding: clamp(22px, 3vw, 38px);
 border: 1px solid rgba(148, 163, 184, 0.18);
 border-left: 4px solid #F4B942;
 border-radius: 20px;
 background:
 linear-gradient(112deg, rgba(14, 24, 40, 0.98), rgba(11, 17, 29, 0.96) 68%),
 #0D1522;
 box-shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
 }

 .studio-masthead::after {
 position: absolute;
 right: -56px;
 bottom: -136px;
 width: 340px;
 height: 260px;
 border: 1px solid rgba(34, 211, 238, 0.12);
 border-radius: 50%;
 box-shadow: 0 0 0 26px rgba(34, 211, 238, 0.025), 0 0 0 54px rgba(34, 211, 238, 0.02);
 content: "";
 pointer-events: none;
 }

 .studio-brand { position: relative; z-index: 1; }
 .studio-mark {
 border-color: rgba(244, 185, 66, 0.45);
 background: rgba(244, 185, 66, 0.11);
 color: #FFD06A;
 }
 .studio-hero-kicker {
 color: #FFD06A;
 letter-spacing: 0.18em;
 }
 .studio-header-title {
 color: #FFF9ED;
 font: 600 clamp(26px, 3.2vw, 42px)/1.08 Georgia, "Times New Roman", serif;
 letter-spacing: -0.045em;
 }
 .studio-header-copy {
 color: #A7B3C4;
 font-size: 13px;
 }
 .studio-header-status { position: relative; z-index: 1; }
 .studio-header-status .kokonut-badge {
 border-color: rgba(148, 163, 184, 0.2) !important;
 background: rgba(15, 23, 42, 0.72) !important;
 color: #D7E1EC !important;
 backdrop-filter: blur(8px);
 }

 .vfx-studio-grid {
 grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
 gap: clamp(14px, 2vw, 24px);
 align-items: start;
 }

 #sqlStudioMainGrid > .vfx-glow-box:first-child,
 #exportCardContainer .vfx-glow-box {
 border: 1px solid rgba(148, 163, 184, 0.17) !important;
 border-radius: 18px;
 background: linear-gradient(145deg, #121C2B, #0E1724) !important;
 box-shadow: 0 18px 48px rgba(0, 0, 0, 0.25) !important;
 backdrop-filter: none;
 }

 #sqlStudioMainGrid > .vfx-glow-box:first-child:hover,
 #exportCardContainer .vfx-glow-box:hover {
 transform: none;
 border-color: rgba(34, 211, 238, 0.3) !important;
 }

 #sqlStudioMainGrid > section[aria-labelledby] > div:first-child {
 margin-bottom: 20px !important;
 }
 #studioBriefHeading {
 color: #F9F5EC !important;
 font: 600 24px/1.1 Georgia, "Times New Roman", serif !important;
 letter-spacing: -0.03em;
 }
 #sqlStudioMainGrid > section[aria-labelledby] > div:first-child > span:last-child {
 border-color: rgba(34, 211, 238, 0.24) !important;
 background: rgba(34, 211, 238, 0.08) !important;
 color: #67E8F9 !important;
 letter-spacing: 0.12em;
 }

 #sqlShortQuestion {
 min-height: 230px;
 margin: 0 0 18px !important;
 padding: 18px 19px !important;
 border: 1px solid rgba(148, 163, 184, 0.28) !important;
 border-radius: 14px !important;
 background: #0A111C !important;
 color: #F7F2E9 !important;
 font: 500 15px/1.75 "Avenir Next", "Segoe UI", sans-serif !important;
 box-shadow: inset 0 1px 10px rgba(0, 0, 0, 0.22) !important;
 resize: vertical;
 }
 #sqlShortQuestion::placeholder { color: #8492A5; opacity: 1; }
 #sqlShortQuestion:focus,
 .vfx-video-root button:focus-visible {
 outline: 2px solid #F4B942;
 outline-offset: 3px;
 }

 #sqlStudioMainGrid > section[aria-labelledby] > div[style*="background"] {
 border-color: rgba(148, 163, 184, 0.14) !important;
 border-radius: 15px !important;
 background: rgba(7, 14, 24, 0.72) !important;
 }
 #sqlStudioMainGrid > section[aria-labelledby] [style*="color: #38BDF8"] { color: #67E8F9 !important; }
 #sqlStudioMainGrid > section[aria-labelledby] [style*="color: #10B981"] { color: #C5E66B !important; }

 .sql-lang-btn {
 min-height: 46px;
 flex: 1 1 0;
 justify-content: center;
 border: 1px solid rgba(148, 163, 184, 0.22);
 border-radius: 11px;
 background: rgba(13, 22, 35, 0.88);
 color: #B5C0CF;
 font-size: 12px;
 font-weight: 700;
 transition: border-color 160ms ease, background 160ms ease, color 160ms ease, transform 160ms ease;
 }
 .sql-lang-btn:hover { transform: translateY(-1px); border-color: rgba(244, 185, 66, 0.55); }
 .sql-lang-btn.active {
 border-color: #F4B942;
 background: rgba(244, 185, 66, 0.12);
 color: #FFE2A0;
 box-shadow: inset 0 0 0 1px rgba(244, 185, 66, 0.14);
 }
 .sql-lang-btn .btn-check { display: inline-block; }
 #activeVoiceBadge { color: #8FE8ED !important; font-size: 11px !important; }

 #btnGenerateSqlBlueprint,
 #btnDownloadShortVideo {
 min-height: 54px;
 border: 1px solid #FFD06A !important;
 border-radius: 13px !important;
 background: linear-gradient(105deg, #F4B942, #FFD36F) !important;
 box-shadow: 0 10px 28px rgba(244, 185, 66, 0.17) !important;
 color: #1D1A12 !important;
 font-size: 14px !important;
 letter-spacing: 0.025em;
 }
 #btnGenerateSqlBlueprint:hover,
 #btnDownloadShortVideo:hover {
 background: #FFE09A !important;
 box-shadow: 0 12px 32px rgba(244, 185, 66, 0.25) !important;
 transform: translateY(-1px);
 }
 #btnGenerateSqlBlueprint:disabled,
 #btnDownloadShortVideo:disabled { cursor: progress; opacity: 0.7; transform: none; }
 #sqlVideoGenerationStatus { color: #9BAABD !important; font-size: 12px !important; }

 .studio-preview-column {
 grid-column: 2;
 grid-row: 1;
 align-items: center !important;
 min-width: 0;
 padding: 0 0 8px;
 }
 #sqlStudioMainGrid > .studio-preview-column > div:first-child {
 max-width: 390px !important;
 color: #E8EEF6;
 }
 #phoneBezel {
 width: min(100%, 390px) !important;
 height: auto !important;
 aspect-ratio: 9 / 16;
 border: 1px solid rgba(148, 163, 184, 0.34) !important;
 border-radius: 25px !important;
 background: #070B12 !important;
 box-shadow: 0 28px 80px rgba(0, 0, 0, 0.48), 0 0 0 5px rgba(148, 163, 184, 0.06) !important;
 }
 #sqlStudioMainGrid > .studio-preview-column > div,
 #sqlStudioMainGrid > .studio-preview-column > .studio-player-controls {
 width: min(100%, 390px) !important;
 max-width: 390px !important;
 align-self: center;
 }
 .studio-player-controls {
 border: 1px solid rgba(148, 163, 184, 0.17) !important;
 border-radius: 13px !important;
 background: #111B29 !important;
 }
 #sqlShortScrubber { accent-color: #F4B942 !important; }
 #playerTimer { color: #C5E66B !important; }

 #exportCardContainer {
 grid-column: 1 / -1;
 min-width: 0;
 display: block !important;
 }
 #exportCardContainer .vfx-glow-box {
 border-color: rgba(148, 163, 184, 0.17) !important;
 padding: clamp(16px, 2vw, 24px) !important;
 }
 #exportCardContainer .vfx-glow-box > div:first-child > span:first-child { color: #67E8F9 !important; }
 #exportCardContainer .vfx-glow-box > div:first-child > span:first-child span:last-child { color: #67E8F9 !important; }
 #aiAttributionLedgerContainer {
 border: 1px solid rgba(148, 163, 184, 0.16) !important;
 border-radius: 15px !important;
 background: #0C1420 !important;
 box-shadow: none !important;
 }
 #ledgerScenesList > div {
 border-color: rgba(148, 163, 184, 0.16) !important;
 border-radius: 12px !important;
 background: #111B29 !important;
 }
 .vfx-pipeline-tracker {
 border: 1px solid rgba(148, 163, 184, 0.16);
 border-radius: 12px;
 background: #0D1724;
 }
 .pipeline-step-row.active { color: #FFE2A0; }
 .pipeline-step-row.completed { color: #C5E66B; }

 @media (max-width: 900px) {
 .vfx-studio-grid { grid-template-columns: minmax(0, 1fr) minmax(280px, 0.9fr); }
 }
 @media (max-width: 720px) {
 .vfx-horizontal-scroll-container { padding: 12px 10px 24px; }
 .studio-masthead { align-items: flex-start; flex-direction: column; padding: 20px; }
 .studio-header-status { justify-content: flex-start; }
 .vfx-studio-grid { grid-template-columns: minmax(0, 1fr); gap: 14px; }
 .studio-preview-column { grid-column: 1; grid-row: auto; }
 #exportCardContainer { grid-column: 1; }
 #sqlStudioMainGrid > .vfx-glow-box:first-child { padding: 18px !important; }
 #sqlShortQuestion { min-height: 190px; }
 .sql-lang-btn { min-height: 44px; padding: 8px 4px; font-size: 11px; }
 #phoneBezel { width: min(100%, 360px) !important; }
 }
 </style>



 <!-- Hidden Native Audio Player for Voiceover Sync -->

 <audio id="sqlVoiceAudio" preload="auto" crossorigin="anonymous" style="display:none;"></audio>



 <!-- Cleaned State Inputs -->

 <input type="hidden" id="sqlShortCreationMode" value="dynamic_ai" />

 <input type="hidden" id="selectedModernVideoModel" value="openai/gpt-oss-120b" />

 <input type="hidden" id="selectedVoiceActor" value="mr-IN-AarohiNeural" />



 <!-- 🎬 Anime.js Animation Engine & Motion Physics CDN with Offline Fallback -->

 <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>

 <script>

 if (typeof anime === 'undefined') {

 window.anime = function(opts) {

 if (opts && typeof opts.complete === 'function') setTimeout(opts.complete, opts.duration || 300);

 return { pause: function(){}, play: function(){}, restart: function(){} };

 };

 window.anime.stagger = function(val) { return function(el, i) { return i * (val || 100); }; };

 }

 </script>



 <div class="vfx-horizontal-scroll-container" id="vfxHorizontalScrollContainer">

 <div class="vfx-video-root" style="margin-bottom: 28px;">



 <header class="studio-masthead">

 <div class="studio-brand">

 <div class="studio-mark" aria-hidden="true">N/</div>

 <div class="studio-hero-copy">

 <div class="studio-hero-kicker">NanoPro / Reel studio</div>

 <h2 class="studio-header-title">
 Make your next idea click.

 </h2>

 <div class="studio-header-copy">
 One prompt. One natural voice. A short that actually teaches.

 </div>

 </div>

 </div>

 <div class="studio-header-status">

 <span id="badgeActiveApis" class="kokonut-badge" style="color: #10B981; border-color: rgba(16,185,129,0.4); background: rgba(16,185,129,0.15);">

 <span class="kokonut-pulse-dot"></span> STORY · VOICE · MOTION

 </span>

 <span class="kokonut-badge" style="color: #38BDF8; border-color: rgba(56,189,248,0.4); background: rgba(56,189,248,0.15);">

 📱 9:16 VERTICAL FORMAT

 </span>

 </div>

 </header>



 <!-- =========================================================================

 MAIN STUDIO 3-COLUMN WORKSPACE

 ========================================================================= -->

 <div class="vfx-studio-grid" id="sqlStudioMainGrid">

 

 <!-- Prompt and language are the only lesson settings. -->

 <section class="vfx-glow-box" aria-labelledby="studioBriefHeading" style="padding: 20px;">

 <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">

 <div style="display: flex; align-items: center; gap: 8px;">

 <span style="font-size: 19px;">✍️</span>
 <h3 id="studioBriefHeading" style="margin: 0; font-size: 14px; color: #F8FAFC; font-weight: 800;">Your idea becomes a Reel</h3>

 </div>

 <span style="font-size: 10.5px; color: #38BDF8; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 8px; border-radius: 6px; font-weight: 700;">

 AI VIDEO STUDIO

 </span>

 </div>







 <input type="hidden" id="activePatternBadge" value="AUTO FALLBACK" />
 <select id="selectModernVideoModelMaster" hidden aria-hidden="true">
 <option value="gemini-3.5-flash-lite" selected>Automatic storyboard model</option>
 </select>

 <label for="sqlShortQuestion" style="display: block; margin: 0 0 9px; color: #E5EDF6; font-size: 13px; font-weight: 750;">
 What should this Reel teach?
 </label>
 <textarea class="studio-input" id="sqlShortQuestion" rows="9" aria-describedby="lessonPromptHelp" placeholder="Describe the idea, a real-life example, and what the viewer should understand.&#10;&#10;Example: A banking app request fails when Maya’s access token expires. Show how a refresh token gets a new access token, then retries the request successfully. Explain it simply in the selected language." style="width: 100%; margin-bottom: 8px; background: #070B16; border: 1.5px solid #1E2D4A; color: #F8FAFC; font-size: 14px; border-radius: 10px; padding: 12px; line-height: 1.65; resize: vertical;"></textarea>
 <div id="lessonPromptHelp" style="margin: 0 0 18px; color: #9AAABD; font-size: 11px; line-height: 1.55;">
 A specific situation makes a better story. Lessons have no fixed duration limit; longer exports take more time and device memory. This studio currently renders Canvas motion graphics, not AI-generated video clips.
 </div>



 <!-- Language is the only narration control; the matching voice is selected automatically. -->

 <div style="background: rgba(11, 19, 43, 0.85); border: 1px solid #1E2D4A; border-radius: 10px; padding: 14px; margin-bottom: 16px;">

 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">

 <div style="display: flex; align-items: center; gap: 8px;">

 <span style="font-size: 14px;">🎙️</span>

 <span style="font-size: 12px; font-weight: 800; color: #38BDF8; text-transform: uppercase;">Choose narration language</span>

 </div>

 </div>

 

 <!-- 3 Regional Language Buttons -->

 <div style="display: flex; gap: 8px; margin-bottom: 10px;">

 <button type="button" class="sql-lang-btn active" id="btnAudioMr" aria-pressed="true" onclick="onWorkspaceLanguageSelect('mr')">

 <span class="btn-check">✓</span> <span>🇮🇳 Marathi (Marathi)</span>

 </button>

 <button type="button" class="sql-lang-btn" id="btnAudioHi" aria-pressed="false" onclick="onWorkspaceLanguageSelect('hi')">

 <span class="btn-check">✓</span> <span>🇮🇳 Hindi ( )</span>

 </button>

 <button type="button" class="sql-lang-btn" id="btnAudioEn" aria-pressed="false" onclick="onWorkspaceLanguageSelect('en')">

 <span class="btn-check">✓</span> <span>🇬🇧 English (English)</span>

 </button>

 </div>



 <div style="color: #9AAABD; font-size: 11px;">Voice is automatically matched to your language · <span id="activeVoiceBadge">Marathi </span></div>
 <select id="selectVoiceActor" hidden aria-hidden="true">
 <option value="mr-IN-AarohiNeural" selected>Marathi neural teacher</option>
 </select>

 </div>


 <!-- Launch Action Button -->

 <button type="button" class="btn btn-primary vfx-laser-btn motion-spring-btn" id="btnGenerateSqlBlueprint" style="width: 100%; padding: 14px; font-weight: 900; font-size: 14px; letter-spacing: 0.5px; background: linear-gradient(135deg, #0284C7, #6366F1, #10B981); border: none; border-radius: 10px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 6px 25px rgba(2,132,199,0.55);">

 <span style="font-size: 19px;">✦</span>

 <span>Create my Reel</span>

 </button>
 <script>
 (function() {
   function attachReelBtn() {
     var btn = document.getElementById('btnGenerateSqlBlueprint');
     if (!btn) return;
     btn.onclick = function() {
       if (typeof window.generateSqlShortBlueprint === 'function') {
         window.generateSqlShortBlueprint();
       } else if (typeof generateSqlShortBlueprint === 'function') {
         generateSqlShortBlueprint();
       } else {
         var st = document.getElementById('sqlVideoGenerationStatus');
         if (st) st.textContent = 'Loading AI engine... please wait 2 seconds and try again.';
         setTimeout(function() {
           if (typeof window.generateSqlShortBlueprint === 'function') {
             window.generateSqlShortBlueprint();
           }
         }, 2000);
       }
     };
   }
   if (document.readyState === 'loading') {
     document.addEventListener('DOMContentLoaded', attachReelBtn);
   } else {
     attachReelBtn();
   }
 })();
 </script>

 <div id="sqlVideoGenerationStatus" role="status" aria-live="polite" style="margin-top: 8px; min-height: 18px; color: #7DD3FC; font-size: 11.5px; text-align: center; font-weight: 600;"></div>



 <!-- 📊 Live 5-Step Generation Pipeline Progress Indicator -->

 <div id="genPipelineSteps" class="vfx-pipeline-tracker" style="display: none;">

 <div style="font-size: 11px; font-weight: 800; color: #38BDF8; margin-bottom: 4px; text-transform: uppercase; display: flex; justify-content: space-between;">

 <span>🚀 Generation Pipeline Progress</span>

 <span id="pipelineOverallPercent" style="font-family: monospace; color: #10B981;">0%</span>

 </div>

 <div class="pipeline-step-row" id="stepLlm">

 <span class="pipeline-step-icon" id="stepIconLlm">⏳</span>

 <span>1. Writing your short story</span>

 </div>

 <div class="pipeline-step-row" id="stepVoice">

 <span class="pipeline-step-icon" id="stepIconVoice">⏳</span>

 <span>2. Making the narration</span>

 </div>

 <div class="pipeline-step-row" id="stepMedia">

 <span class="pipeline-step-icon" id="stepIconMedia">⏳</span>

 <span>3. Drawing voice-matched scenes</span>

 </div>

 <div class="pipeline-step-row" id="stepSfx">

 <span class="pipeline-step-icon" id="stepIconSfx">⏳</span>

 <span>4. Timing captions and motion</span>

 </div>

 <div class="pipeline-step-row" id="stepRender">

 <span class="pipeline-step-icon" id="stepIconRender">⏳</span>

 <span>5. Ready to preview and export</span>

 </div>

 </div>

 </section>



 <!-- COLUMN 2: 9:16 TITANIUM SMARTPHONE PREVIEW -->

 <section class="studio-preview-column" aria-label="Video preview and playback controls" style="display: flex; flex-direction: column; align-items: center;">

 <div style="margin-bottom: 10px; display: flex; justify-content: space-between; width: 100%; max-width: 340px; align-items: center;">

 <span style="font-size: 12px; font-weight: 800; color: #38BDF8; letter-spacing: 0.5px;">📱 9:16 SMARTPHONE PREVIEW</span>

 <span id="playerTimer" style="font-size: 11px; font-family: monospace; color: #10B981; background: #070B16; padding: 2px 8px; border-radius: 4px; border: 1px solid #1E2D4A;">0:00 / 0:00</span>

 </div>



 <!-- Futuristic Smartphone Bezel -->

 <div id="phoneBezel" style="width: 340px; height: 604px; aspect-ratio: 9 / 16; background: #000000; border: 4px solid #1E2D4A; border-radius: 38px; box-shadow: 0 25px 60px rgba(0,0,0,0.9), 0 0 30px rgba(56,189,248,0.25); position: relative; overflow: hidden; display: flex; flex-direction: column;">

 

 <!-- Dynamic Island Notch -->

 <div style="height: 30px; width: 100%; display: flex; justify-content: center; align-items: center; position: absolute; top: 0; left: 0; z-index: 20; pointer-events: none;">

 <div style="width: 90px; height: 18px; background: #0A0F1D; border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.3); display: flex; align-items: center; justify-content: space-between; padding: 0 8px;">

 <div style="width: 6px; height: 6px; background: #10B981; border-radius: 50%; box-shadow: 0 0 6px #10B981;"></div>

 <div style="font-size: 8px; color: #38BDF8; font-weight: 800; font-family: monospace;">NANOPRO</div>

 <div style="width: 5px; height: 5px; background: #0284C7; border-radius: 50%;"></div>

 </div>

 </div>



 <!-- Video Layer (Generative AI Video Stream: Kling, Luma, Runway, Seedance, Pollinations) -->

 <video id="sqlShortRealVideo" playsinline loop muted autoplay style="display:none; position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; z-index:1; border-radius:34px;"></video>

 

 <!-- 60 FPS Canvas Viewport (1080x1920 logical, scaled via CSS, Overlay on Video) -->

 <canvas id="sqlShortCanvas" width="1080" height="1920" style="position:relative; z-index:2; width: 100%; height: 100%; background: transparent; object-fit: contain;"></canvas>



 <!-- Bottom Audio Wave Indicator -->

 <div id="canvasAudioWave" style="position: absolute; bottom: 10px; left: 16px; right: 16px; height: 20px; display: flex; align-items: center; justify-content: space-between; z-index: 10; pointer-events: none;">

 <div style="font-size: 10px; color: #38BDF8; font-weight: 800; text-shadow: 0 1px 4px #000;">@Code_With_Mangesh</div>

 <div style="display: flex; gap: 3px; align-items: center;">

 <span class="vfx-wave-bar"></span>

 <span class="vfx-wave-bar"></span>

 <span class="vfx-wave-bar"></span>

 <span class="vfx-wave-bar"></span>

 </div>

 </div>

 </div>



 <!-- Player Transport Controls -->

 <div class="studio-player-controls" style="width: 100%; max-width: 340px; margin-top: 12px; background: #0E1528; border: 1px solid #1E2D4A; border-radius: 10px; padding: 10px;">

 <!-- Timeline Scrubber -->

 <input type="range" id="sqlShortScrubber" min="0" max="0" value="0" step="0.1" oninput="seekSqlShortPlayer(this.value)" style="width: 100%; accent-color: #38BDF8; cursor: pointer; margin-bottom: 8px;" />

 

 <div style="display: flex; justify-content: space-between; align-items: center;">

 <div style="display: flex; gap: 6px;">

 <button type="button" class="btn btn-secondary" id="btnPlayPause" onclick="toggleSqlShortPlay()" style="padding: 4px 10px; font-size: 11.5px; font-weight: 700;">▶ Play</button>

 <button type="button" class="btn btn-secondary" onclick="restartSqlShortPlay()" style="padding: 4px 10px; font-size: 11.5px; font-weight: 700;">🔄 Replay</button>

 </div>

 <div style="font-size: 11px; color: #94A3B8;">

 </div>

 </div>

 </div>

 </section>



 <!-- COLUMN 3: 1-CLICK 9:16 VIDEO EXPORT STATION -->

 <div id="exportCardContainer" style="display: flex; flex-direction: column; gap: 16px;">

 

 <div class="vfx-glow-box" style="padding: 16px; border-color: rgba(16, 185, 129, 0.45); background: #0A0F1D;">

 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">

 <span style="font-size: 13px; font-weight: 900; color: #10B981; display: flex; align-items: center; gap: 6px;">

 <span>🎬</span> <span>1-CLICK 9:16 VIDEO EXPORT</span>

 </span>

 <span style="font-size: 11px; color: #A7B3C4;">1080 × 1920 · MP4</span>

 </div>



 <!-- Direct Download Button Group -->

 <div style="display: flex; flex-direction: column; gap: 8px;">

 <button type="button" class="btn btn-primary" id="btnDownloadShortVideo" onclick="exportSqlShortVideo()" style="width: 100%; padding: 13px; font-weight: 900; font-size: 13.5px; background: linear-gradient(135deg, #0284C7, #10B981); border: none; border-radius: 8px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 20px rgba(2,132,199,0.5);">

 <span style="font-size: 18px;">📥</span>

 <span id="exportBtnLabel">RENDER ON THIS DEVICE · 1080×1920</span>

 </button>

 <div style="font-size:10px;color:#94A3B8;line-height:1.5;">
 Final rendering happens in your browser, so NanoPro’s server stays free for other work.
 </div>
 <select id="sqlExportResolution" hidden aria-hidden="true">
 <option value="1080" selected>1080 × 1920</option>
 </select>

 </div>



 <!-- Progress Bar & Remaining Time Stats -->

 <div id="exportProgressBarContainer" style="display:none; background: #0B1120; border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; margin-top: 14px;">

 <div style="display: flex; justify-content: space-between; font-size: 11px; color: #38BDF8; font-weight: 700; margin-bottom: 6px;">

 <span id="exportStageDesc">⏳ 60 FPS Compositor is...</span>

 <span id="exportPercentNum" style="font-family: monospace; font-size: 13px; color: #10B981;">0%</span>

 </div>

 <div style="height: 12px; width: 100%; background: #1E2D4A; border-radius: 6px; overflow: hidden; margin-bottom: 8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.6);">

 <div id="exportProgressFill" style="height: 100%; width: 0%; background: linear-gradient(90deg, #0284C7, #38BDF8, #10B981); transition: width 0.1s linear; border-radius: 6px;"></div>

 </div>

 <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94A3B8; font-family: monospace;">

 <span id="exportEstTime" style="color: #F59E0B; font-weight: 700;">⏱️ : is...</span>

 <span id="exportFrameStats">🎞️ : 0 / narration duration</span>

 </div>

 </div>



 <!-- 🧬 AI ENGINES & COMPONENT ATTRIBUTION LEDGER (Post-Generation Report Card) -->

 <div id="aiAttributionLedgerContainer" style="display:none; background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 70%), #0A0F1D; border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 12px; padding: 18px; margin-top: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.6);">

 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">

 <div style="display: flex; align-items: center; gap: 10px;">

 <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #0284C7, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 16px;">

 🧬

 </div>

 <div>

 <h4 style="margin: 0; font-size: 13px; color: #38BDF8; font-weight: 800; letter-spacing: 0.5px;">

 GENERATION REPORT

 </h4>

 <div style="font-size: 10.5px; color: #94A3B8;">Models, voice, rendering and optional assets actually used</div>

 </div>

 </div>

 <span id="ledgerPatternBadge" style="font-size: 10px; font-weight: 800; color: #10B981; background: rgba(16,185,129,0.15); border: 1px solid #10B981; padding: 3px 10px; border-radius: 6px;">

 WAITING FOR REPORT

 </span>

 </div>



 <!-- Scene Breakdown Grid -->

 <div id="ledgerScenesList" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px;">

 <!-- Dynamically injected scene attribution cards -->

 </div>



 <!-- Hardware & Voice Pipeline Summary -->

 <div style="background: rgba(7, 11, 22, 0.8); border: 1px solid #1E2D4A; border-radius: 8px; padding: 12px; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">

 <div>

 <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🧠 Reasoning LLM</div>

 <div id="ledgerScriptModel" style="font-size: 11.5px; color: #38BDF8; font-weight: 800; margin-top: 2px;">Not generated yet</div>
 <div id="ledgerScriptSpeed" style="font-size: 9.5px; color: #94A3B8;">Storyboard source appears after generation</div>

 </div>

 <div>

 <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🎙️ Voiceover Actor</div>

 <div id="ledgerVoiceName" style="font-size: 11.5px; color: #34D399; font-weight: 800; margin-top: 2px;">Selected voice appears after generation</div>
 <div id="ledgerVoiceDuration" style="font-size: 9.5px; color: #94A3B8;">Voice provider not reported</div>

 </div>

 <div>

 <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">🎬 B-Roll &amp; Visuals</div>

 <div id="ledgerBrollInfo" style="font-size: 11.5px; color: #FBBF24; font-weight: 800; margin-top: 2px;">Optional providers not requested</div>
 <div id="ledgerVisualStats" style="font-size: 9.5px; color: #94A3B8;">Browser Canvas compositor</div>

 </div>

 <div>

 <div style="font-size: 10px; color: #64748B; text-transform: uppercase; font-weight: 700;">⏱️ Total Generation Time</div>

 <div id="ledgerElapsedTime" style="font-size: 11.5px; color: #A78BFA; font-weight: 800; margin-top: 2px;">Shown after generation</div>

 <div style="font-size: 9.5px; color: #94A3B8;">Real-Time End-to-End Pipeline</div>

 </div>

 </div>

 </div>



 <!-- Celebration & Video Ready Card -->

 <div id="videoReadyCelebration" style="display:none; background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(6,182,212,0.25)); border: 2px solid #10B981; border-radius: 8px; padding: 14px; text-align: center; margin-top: 14px;">

 <div style="font-size: 26px;">🎉 🏆 🎬</div>

 <div style="font-size: 14px; font-weight: 800; color: #10B981; margin-top: 4px;"> !</div>

 <div id="videoReadyQuality" style="font-size: 11px; color: #CBD5E1; margin: 4px 0 10px;">Watermark-free • 9:16 • 1080×1920 60FPS</div>

 <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">

 <a id="btnDownloadAgain" href="#" class="btn btn-primary" style="font-size: 11px; padding: 7px 14px; background: linear-gradient(135deg, #10B981, #06B6D4); color: #000; font-weight: 800; border-radius: 6px; text-decoration: none;">

 <span>📥 </span>

 </a>

 <button type="button" class="btn btn-secondary" onclick="restartSqlShortPlay()" style="font-size: 11px; padding: 7px 14px; border-color: #38BDF8; color: #38BDF8; font-weight: 700;">

 <span>▶ on </span>

 </button>

 </div>

 </div>

 </div>



 </div>



 </div>



 </div>

 </div> <!-- Close vfxHorizontalScrollContainer -->



 <!-- Interactive Helper Functions for Prompt Chips and Model Docks -->

 <script>

 // 2. Language & Dynamic Voice Actor Sync

 const WORKSPACE_VOICE_MAP = {

 mr: [

 { value: 'mr-IN-AarohiNeural', label: 'Edge-TTS: mr-IN-AarohiNeural (Female - Clear Educator)', default: true },

 { value: 'mr-IN-ManoharNeural', label: 'Edge-TTS: mr-IN-ManoharNeural (Male - Formal Tech)' }

 ],

 hi: [

 { value: 'hi-IN-MadhurNeural', label: 'Edge-TTS: hi-IN-MadhurNeural (Male - Professional Teacher)', default: true },

 { value: 'hi-IN-SwaraNeural', label: 'Edge-TTS: hi-IN-SwaraNeural (Female - Conversational)' }

 ],

 en: [

 { value: 'en-US-JennyNeural', label: 'Edge-TTS: en-US-JennyNeural (Female - Studio Tech)', default: true },

 { value: 'en-US-GuyNeural', label: 'Edge-TTS: en-US-GuyNeural (Male - Tech Educator)' },

 { value: 'aura-asteria-en', label: 'Deepgram Aura: aura-asteria-en (Female - Human Conversational)' },

 { value: 'aura-luna-en', label: 'Deepgram Aura: aura-luna-en (Female - Natural Calm)' }

 ]

 };



 function updateVoiceActorDropdown(lang) {

 const select = document.getElementById('selectVoiceActor');

 if (!select) return;

 const actors = WORKSPACE_VOICE_MAP[lang] || WORKSPACE_VOICE_MAP.mr;

 select.innerHTML = '';

 actors.forEach(actor => {

 const opt = document.createElement('option');

 opt.value = actor.value;

 opt.textContent = actor.label;

 if (actor.default) opt.selected = true;

 select.appendChild(opt);

 });

 const hiddenVoice = document.getElementById('selectedVoiceActor');

 if (hiddenVoice && select.value) hiddenVoice.value = select.value;

 }



 function onWorkspaceLanguageSelect(lang) {

 window.sqlShortRequestedLang = lang;
 document.querySelectorAll('.sql-lang-btn').forEach(button => {
 const selected = button.id === 'btnAudio' + lang.charAt(0).toUpperCase() + lang.slice(1);
 button.classList.toggle('active', selected);
 button.setAttribute('aria-pressed', String(selected));
 });
 updateVoiceActorDropdown(lang);
 const badge = document.getElementById('activeVoiceBadge');
 if (badge) badge.textContent = lang === 'mr' ? 'Marathi ' : (lang === 'hi' ? ' ' : 'English teacher');
 }



 function onVoiceActorSelected(val) {

 const hiddenVoice = document.getElementById('selectedVoiceActor');

 if (hiddenVoice) hiddenVoice.value = val;

 }



 // 4. Reactive Waveform State Helper

 function setAudioWaveformPlaying(isPlaying) {

 const bars = document.querySelectorAll('.vfx-wave-bar');

 bars.forEach(b => {

 if (isPlaying) b.classList.add('playing');

 else b.classList.remove('playing');

 });

 const visualizer = document.getElementById('audioWaveformVisualizer');

 if (visualizer) {

 if (isPlaying) visualizer.classList.add('is-playing');

 else visualizer.classList.remove('is-playing');

 }

 }

 </script>

 """
