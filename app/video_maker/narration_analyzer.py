"""Narration Analyzer Module

This module provides functions to analyse a narration transcript and produce a
structured visual storyboard suitable for the audio-first video generation pipeline.

It integrates directly with ModelManager (Groq / Gemini / Ollama fallback) to
break narration into semantic segments with concepts, objectives, and 3D visual specifications.
"""

from __future__ import annotations

import json
import uuid
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.logger import log_event


def _call_model(prompt: str) -> str:
    """Call language model via model_manager with graceful fallback."""
    try:
        from app.core.model_adapter import model_manager
        res = model_manager.route_and_execute(prompt, task_type="reasoning")
        if isinstance(res, dict):
            return res.get("content") or res.get("text") or str(res)
        return str(res)
    except Exception as e:
        log_event(f"Narration model call error: {e}", level="WARNING", component="NarrationAnalyzer")
        return ""


def _segment_prompt(transcript: str) -> str:
    """Construct prompt for semantic speech-to-visual segmenting."""
    return f"""You are an expert Educational Video Director and 3D Motion Graphics Engineer.
Analyze the following narration transcript and produce a clean JSON array named `segments`.

For each spoken sentence or logical idea, create a segment object with:
- "id": short ID like "seg1", "seg2"
- "text": exact spoken sentence
- "concept": core technical concept (e.g., "ETL Pipeline", "Snowflake Warehousing", "CDC Replication")
- "objective": what the viewer should understand
- "visual_type": one of ["architecture_3d", "diagram", "table", "simulation", "code", "steps", "stat", "takeaway"]
- "visuals":
  - "objects": array of objects to show (e.g., ["Database Cylinder", "Message Queue", "Streaming Spark Job"])
  - "layout": layout style (e.g., "isometric 3d architecture with photon flow")
  - "animation": description of motion graphics (e.g., "packets pulsing from client to gateway")
  - "nodes": optional list of nodes with id, label, type, icon, color for 3D architecture
  - "connections": optional list of connections with from, to, label

Return ONLY the raw JSON array (enclosed in [ ... ]), with NO markdown wrapping, NO backticks, and NO conversational filler.

Narration Transcript:
{transcript}
"""


def _generate_rule_based_fallback(transcript: str) -> List[Dict[str, Any]]:
    """Produce deterministic semantic segments if model is offline."""
    raw_sentences = [s.strip() for s in re.split(r'[.!?\n]+', transcript) if len(s.strip()) > 3]
    if not raw_sentences:
        raw_sentences = [transcript.strip()]

    segments = []
    for idx, sentence in enumerate(raw_sentences, start=1):
        s_lower = sentence.lower()
        if any(w in s_lower for w in ["database", "table", "schema", "sql", "select"]):
            vtype = "table"
        elif any(w in s_lower for w in ["pipeline", "architecture", "flow", "etl", "stream", "cloud"]):
            vtype = "architecture_3d"
        elif any(w in s_lower for w in ["code", "function", "api", "query", "python"]):
            vtype = "code"
        elif any(w in s_lower for w in ["compare", "versus", "difference", "vs"]):
            vtype = "comparison"
        else:
            vtype = "diagram"

        segments.append({
            "id": f"seg{idx}",
            "text": sentence,
            "concept": sentence[:40] + ("..." if len(sentence) > 40 else ""),
            "objective": f"Understand: {sentence[:60]}",
            "visual_type": vtype,
            "visuals": {
                "objects": ["Concept Node", "Data Packet", "Flow Conduit"],
                "layout": "isometric 3d architecture" if vtype == "architecture_3d" else "centered view",
                "animation": "smooth fade-in with pulsing glow",
                "nodes": [
                    {"id": "src", "label": "Source", "type": "database", "color": "#00f3ff"},
                    {"id": "proc", "label": "Processing", "type": "process", "color": "#ffd700"},
                    {"id": "tgt", "label": "Target", "type": "cloud", "color": "#10b981"}
                ],
                "connections": [
                    {"from": "src", "to": "proc", "label": "Extract"},
                    {"from": "proc", "to": "tgt", "label": "Load"}
                ]
            }
        })
    return segments


def analyse_transcript(transcript: str) -> Dict[str, Any]:
    """Analyse a narration transcript and produce a structured storyboard."""
    if not transcript or not transcript.strip():
        raise ValueError("Transcript must be a non-empty string")

    clean_text = transcript.strip()
    segments = []

    prompt = _segment_prompt(clean_text)
    raw_response = _call_model(prompt)

    if raw_response:
        cleaned = re.sub(r"^```(?:json)?", "", raw_response.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                segments = parsed
            elif isinstance(parsed, dict) and "segments" in parsed and isinstance(parsed["segments"], list):
                segments = parsed["segments"]
        except Exception:
            segments = []

    if not segments:
        segments = _generate_rule_based_fallback(clean_text)

    job_id = str(uuid.uuid4())
    storyboard = {
        "job_id": job_id,
        "transcript_length": len(clean_text),
        "total_segments": len(segments),
        "segments": segments,
    }
    return storyboard


def save_storyboard(job_id: str, storyboard: Dict[str, Any], base_dir: Path = Path("./video_maker/jobs")) -> Path:
    """Persist the storyboard JSON to disk."""
    job_dir = base_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    out_path = job_dir / "storyboard.json"
    out_path.write_text(json.dumps(storyboard, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


__all__ = ["analyse_transcript", "save_storyboard"]
