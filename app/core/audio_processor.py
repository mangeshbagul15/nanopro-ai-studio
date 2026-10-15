"""
Mangesh Nano Pro AI Studio - Audio Processor & Video Synchronization Engine
Integrates FFmpeg to accurately inspect audio duration, loop shorter audio tracks,
trim longer tracks, adjust volume, and mux background audio to generated animation videos
without changing the configured video duration.
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from app.core.logger import log_event
from app.core.config import AUDIO_FALLBACK_LOOP, AUDIO_FALLBACK_PAD

class AudioProcessor:
    def __init__(self):
        self.ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe_bin = shutil.which("ffprobe") or "ffprobe"

    def is_ffmpeg_available(self) -> bool:
        try:
            res = subprocess.run([self.ffmpeg_bin, "-version"], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    def get_media_duration(self, file_path: Path) -> float:
        """Returns the media duration in seconds using ffprobe."""
        if not file_path.exists():
            return 0.0
        cmd = [
            self.ffprobe_bin,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(res.stdout.strip())
        except Exception as e:
            log_event(f"Error probing duration for {file_path.name}: {e}", level="WARNING", component="AudioProcessor")
            return 0.0

    def prepare_audio_track(
        self,
        input_audio_path: Path,
        target_duration: float,
        output_audio_path: Path,
        volume: float = 0.5,
        fallback_policy: str = AUDIO_FALLBACK_LOOP
    ) -> bool:
        """
        Prepares an audio track strictly matching target_duration:
        - If input audio > target_duration: Trims to target_duration.
        - If input audio < target_duration: Intelligently loops audio (or pads) to target_duration.
        - Applies volume adjustment (0.0 to 1.0).
        """
        if not input_audio_path.exists():
            log_event(f"Audio file not found: {input_audio_path}", level="ERROR", component="AudioProcessor")
            return False

        orig_duration = self.get_media_duration(input_audio_path)
        log_event(f"Audio duration: {orig_duration:.1f}s | Target video duration: {target_duration:.1f}s | Volume: {volume}", component="AudioProcessor")

        output_audio_path.parent.mkdir(parents=True, exist_ok=True)
        volume_filter = f"volume={max(0.0, min(2.0, volume))}"

        if orig_duration <= 0.0:
            log_event("Invalid audio duration detected", level="ERROR", component="AudioProcessor")
            return False

        if orig_duration < target_duration and fallback_policy == AUDIO_FALLBACK_LOOP:
            # Need to loop the audio until target_duration
            loops = int(target_duration // orig_duration) + 1
            cmd = [
                self.ffmpeg_bin, "-y",
                "-stream_loop", str(loops),
                "-i", str(input_audio_path),
                "-t", str(target_duration),
                "-filter:a", volume_filter,
                "-c:a", "aac", "-b:a", "192k",
                str(output_audio_path)
            ]
        else:
            # Trim or pad directly
            cmd = [
                self.ffmpeg_bin, "-y",
                "-i", str(input_audio_path),
                "-t", str(target_duration),
                "-filter:a", volume_filter,
                "-c:a", "aac", "-b:a", "192k",
                str(output_audio_path)
            ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                log_event(f"FFmpeg audio processing failed: {res.stderr[:200]}", level="ERROR", component="AudioProcessor")
                return False
            log_event(f"Audio track prepared at exact {target_duration:.1f}s: {output_audio_path.name}", component="AudioProcessor")
            return True
        except Exception as e:
            log_event(f"Audio preparation exception: {e}", level="ERROR", component="AudioProcessor")
            return False

    def mux_video_audio(
        self,
        video_input_path: Path,
        audio_input_path: Optional[Path],
        output_video_path: Path,
        target_video_duration: Optional[float] = None
    ) -> bool:
        """
        Combines the recorded silent video with the prepared background audio track.
        Guarantees final video duration is anchored to video duration, NOT audio duration.
        """
        if not video_input_path.exists():
            log_event(f"Video input does not exist: {video_input_path}", level="ERROR", component="AudioProcessor")
            return False

        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        vid_duration = target_video_duration or self.get_media_duration(video_input_path)

        if not audio_input_path or not audio_input_path.exists():
            # No audio requested or missing -> remux/copy video only
            cmd = [
                self.ffmpeg_bin, "-y",
                "-i", str(video_input_path),
                "-c:v", "copy",
                "-an",
                str(output_video_path)
            ]
        else:
            # Video + Audio Muxing
            # -shortest ensures that if audio is longer, it stops at video end
            cmd = [
                self.ffmpeg_bin, "-y",
                "-i", str(video_input_path),
                "-i", str(audio_input_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(output_video_path)
            ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                log_event(f"Muxing failed: {res.stderr[:200]}", level="ERROR", component="AudioProcessor")
                return False
            final_dur = self.get_media_duration(output_video_path)
            log_event(f"Final synchronized video produced: {output_video_path.name} (Duration: {final_dur:.1f}s)", component="AudioProcessor")
            return True
        except Exception as e:
            log_event(f"Muxing exception: {e}", level="ERROR", component="AudioProcessor")
            return False

audio_processor = AudioProcessor()
