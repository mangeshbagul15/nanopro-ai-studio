"""
Mangesh Nano Pro AI Studio - Unified Video Creation Engine (SQL & Python Modes)
Integrates SQL Interview Video Maker and Python Animation Video Maker into one unified,
mode-switchable engine with audio controls, thumbnail rendering, and output metadata.
"""

import os
import sys
import re
import json
import time
import uuid
import random
import asyncio
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.core.config import (
    VIDEO_SQL_DIR, VIDEO_PY_DIR, VIDEO_AUDIO_DIR, VIDEO_OUTPUT_DIR,
    IMAGE_OUTPUT_DIR, AUDIO_FALLBACK_LOOP
)
from app.core.logger import log_event
from app.core.task_manager import task_manager
from app.core.audio_processor import audio_processor

# Import SQL and Python specialized cores
import app.video_maker.sql.sql_core as sql_core
import app.video_maker.python.python_core as py_core

class UnifiedVideoMaker:
    def __init__(self):
        self.output_dir = VIDEO_OUTPUT_DIR
        self.audio_dir = VIDEO_AUDIO_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def generate_video_pipeline(
        self,
        job_id: str,
        mode: str,  # 'sql' or 'python'
        question: str,
        query_logic: str,
        enable_audio: bool = False,
        audio_file_path: Optional[str] = None,
        audio_volume: float = 0.5,
        audio_fallback_policy: str = AUDIO_FALLBACK_LOOP,
        output_format: str = "mp4",
        resolution: str = "1080x1920"  # '1080x1920', '1920x1080', '1080x1080'
    ) -> Dict[str, Any]:
        """
        Executes end-to-end video creation:
        1. Parse & validate inputs
        2. Execute AI Model / Code Extraction
        3. Build Animation HTML
        4. Record HTML via Playwright
        5. Process Background Audio & Mux with FFmpeg
        6. Return complete output metadata
        """
        task_manager.update_job_stage(job_id, "learning", progress=15)
        log_event(f"Starting {mode.upper()} Video Generation pipeline for job {job_id}", component="VideoMaker", job_id=job_id)

        clean_q = (question or "").strip()
        clean_ql = (query_logic or "").strip()

        if not clean_q and not clean_ql:
            clean_q = "Explain and animate the solution step-by-step"

        # Step 1: Generate Animation Data
        task_manager.update_job_stage(job_id, "models", progress=30)
        if mode == "sql":
            anim_data = sql_core.generate_animation_data(clean_q, clean_ql)
        else:
            anim_data = py_core.generate_animation_data(clean_q, clean_ql)

        # Step 2: Build Animation HTML
        task_manager.update_job_stage(job_id, "build", progress=55)
        html_file = VIDEO_SQL_DIR / f"anim_{job_id}.html" if mode == "sql" else VIDEO_PY_DIR / f"anim_{job_id}.html"
        
        if mode == "sql":
            html_content = sql_core.create_html_file(anim_data, html_file)
        else:
            py_core.create_html_file(anim_data, html_file)
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()

        # Update job with live preview html
        with task_manager._lock:
            job = task_manager._jobs.get(job_id)
            if job:
                job["html"] = html_content
                job["html_ready"] = True

        # Step 3: Record Animation via Playwright
        task_manager.update_job_stage(job_id, "video", progress=75)
        raw_video_dir = self.output_dir / "raw"
        raw_video_dir.mkdir(parents=True, exist_ok=True)

        raw_video_path = None
        # Check if playwright is available in this environment
        try:
            import playwright
            if platform.system() == "Windows":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            if mode == "sql":
                raw_video_path = asyncio.run(sql_core.record_video(html_file, str(raw_video_dir)))
            else:
                raw_video_path = asyncio.run(py_core.record_video(html_file, str(raw_video_dir)))
        except ImportError:
            log_event("Playwright not installed in environment; producing simulation artifact", level="WARNING", component="VideoMaker", job_id=job_id)
            raw_video_path = str(raw_video_dir / f"simulated_{job_id}.mp4")
            synth_cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"color=c=0x170D2E:s={resolution}:d=10",
                "-vf", f"drawtext=text='@Code_With_Mangesh {mode.upper()} Video':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                raw_video_path
            ]
            subprocess.run(synth_cmd, capture_output=True)

        # Step 4: Audio synchronization & Muxing
        final_video_file = self.output_dir / f"{mode}_tutorial_{job_id}.mp4"
        if raw_video_path and Path(raw_video_path).exists():
            vid_duration = audio_processor.get_media_duration(Path(raw_video_path))
            log_event(f"Recorded video duration: {vid_duration:.1f}s", component="VideoMaker", job_id=job_id)

            if enable_audio and audio_file_path and Path(audio_file_path).exists():
                task_manager.update_job_stage(job_id, "audio_mux", progress=90)
                prep_audio = self.audio_dir / f"sync_{job_id}.aac"
                audio_ok = audio_processor.prepare_audio_track(
                    input_audio_path=Path(audio_file_path),
                    target_duration=vid_duration,
                    output_audio_path=prep_audio,
                    volume=audio_volume,
                    fallback_policy=audio_fallback_policy
                )
                if audio_ok:
                    audio_processor.mux_video_audio(
                        video_input_path=Path(raw_video_path),
                        audio_input_path=prep_audio,
                        output_video_path=final_video_file,
                        target_video_duration=vid_duration
                    )
                else:
                    audio_processor.mux_video_audio(Path(raw_video_path), None, final_video_file)
            else:
                # Video without audio
                audio_processor.mux_video_audio(Path(raw_video_path), None, final_video_file)
        
        result_payload = {
            "mode": mode,
            "question": clean_q,
            "final_video_path": str(final_video_file),
            "html_path": str(html_file),
            "video_duration": audio_processor.get_media_duration(final_video_file),
            "audio_enabled": enable_audio,
            "timestamp": time.time()
        }

        task_manager.set_job_completed(job_id, result_payload)
        return result_payload

    def generate_thumbnail(self, mode: str, question: str, query_logic: str) -> Dict[str, Any]:
        """Unified thumbnail generation for either SQL or Python modes."""
        log_event(f"Generating thumbnail for {mode.upper()} mode...", component="VideoMaker")
        if mode == "sql":
            return sql_core.create_thumbnail(question, query_logic)
        else:
            return py_core.create_thumbnail(question, query_logic)

    def generate_metadata(self, mode: str, question: str, query_logic: str, kind: str) -> str:
        """Unified YouTube title, description, and hashtags generation."""
        if mode == "sql":
            return sql_core.generate_metadata(question, query_logic, kind)
        else:
            return py_core.generate_metadata(question, query_logic, kind)

unified_video_maker = UnifiedVideoMaker()
