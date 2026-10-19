"""
Mangesh Nano Pro AI Studio - Agent 2: Image Creation Agent
Generates YouTube thumbnails, technical diagrams, educational illustrations,
and saves metadata to the local project store.
"""

import os
import time
import subprocess
import urllib.request
import urllib.parse
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import IMAGE_OUTPUT_DIR
from app.core.logger import log_event
from app.core.database import db

class ImageCreationAgent:
    def __init__(self):
        self.output_dir = IMAGE_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_image(
        self,
        prompt: str,
        style: str = "modern_tech",
        width: int = 1080,
        height: int = 1920,
        allow_local_fallback: bool = True,
        preserve_prompt: bool = False,
    ) -> Dict[str, Any]:
        """
        Generates an image from prompt.
        If an external image service / local Stable Diffusion is configured, calls it.
        Otherwise creates a high-res educational SVG/PNG thumbnail card.
        """
        log_event(f"ImageCreationAgent generating image for: {prompt[:60]}", component="ImageAgent")
        timestamp = int(time.time())
        filename = f"gen_img_{timestamp}_{uuid.uuid4().hex[:10]}.png"
        filepath = self.output_dir / filename

        # 1. Try Replicate Flux.1 / SDXL if configured and credit active
        image_generated = False
        provider_used = "local-canvas"
        source_url = None
        provider_prompt = (
            f"{prompt}, portrait composition, high visual quality"
            if preserve_prompt
            else f"{prompt}, style {style}, 8k sharp, cinematic lighting"
        )
        try:
            from app.core.replicate_engine import replicate_engine
            if replicate_engine.is_available():
                rep_res = replicate_engine.generate_image(
                    prompt=provider_prompt,
                    model="black-forest-labs/flux-schnell"
                )
                img_url = rep_res.get("image_url")
                if img_url:
                    # Download Replicate image to output directory
                    req_rep = urllib.request.Request(img_url, headers={"User-Agent": "NanoProAI/2.0"})
                    with urllib.request.urlopen(req_rep, timeout=15) as r_resp:
                        r_bytes = r_resp.read()
                        if len(r_bytes) > 1000:
                            with open(filepath, "wb") as f:
                                f.write(r_bytes)
                            image_generated = True
                            provider_used = "replicate-flux"
                            source_url = img_url
                            log_event(f"Replicate generated AI image ({len(r_bytes)} bytes) for: {prompt[:40]}", component="ImageAgent")
        except Exception as re_err:
            log_event(f"Replicate skipped/cascading ({re_err}), falling back to Pollinations Flux.", component="ImageAgent")

        # 2. Try Generative AI via Pollinations.ai (Flux.1 / SDXL - Zero-Config, Free Lifetime)
        if not image_generated:
            try:
                enhanced_prompt = (
                    f"{prompt}, portrait composition, high visual quality"
                    if preserve_prompt
                    else f"{prompt}, style {style}, professional 8k sharp, cinematic lighting, trending on artstation"
                )
                encoded_prompt = urllib.parse.quote(enhanced_prompt)
                # Use scaled dimensions for fast generation
                target_w = min(width, 1024)
                target_h = min(height, 1024)
                poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={target_w}&height={target_h}&model=flux&nologo=true&seed={timestamp%100000}"
                req = urllib.request.Request(poll_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NanoProAI/1.0"})
                with urllib.request.urlopen(req, timeout=18) as resp:
                    img_data = resp.read()
                    if len(img_data) > 1000:
                        with open(filepath, "wb") as f:
                            f.write(img_data)
                        image_generated = True
                        provider_used = "pollinations-flux"
                        source_url = poll_url
                        log_event(f"Pollinations.ai generated real AI image ({len(img_data)} bytes) for: {prompt[:40]}", component="ImageAgent")
            except Exception as pe:
                log_event(f"Pollinations.ai skipped or offline ({pe}), using local graphics canvas fallback.", component="ImageAgent")

        # Scene renders must fail closed instead of silently returning a text card.
        if not image_generated and not allow_local_fallback:
            raise RuntimeError(
                "NanoPro could not generate a prompt-specific image. Check the configured image providers and retry."
            )

        # 3. Fallback to local Pillow or FFmpeg canvas if offline (legacy callers only).
        if not image_generated:
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new("RGB", (width, height), color="#170D2E")
                draw = ImageDraw.Draw(img)
                # Background grid/decorations
                draw.rectangle([40, 40, width-40, height-40], outline="#8B2EFF", width=6)
                draw.rectangle([60, 60, width-60, 200], fill="#21143D", outline="#F000D0", width=4)
                # Text placeholder
                draw.text((100, 100), "@Code_With_Mangesh", fill="#FFD900")
                draw.text((100, 280), f"Topic: {prompt[:50]}", fill="#FFFFFF")
                draw.text((100, 360), f"Style: {style.title()}", fill="#D5CEE8")
                img.save(str(filepath))
            except Exception as e:
                # Fallback using ffmpeg color filter
                log_event(f"Pillow unavailable, fallback to ffmpeg render: {e}", component="ImageAgent")
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi", "-i", f"color=c=0x170D2E:s={width}x{height}:d=1",
                    "-vf", f"drawbox=x=40:y=40:w={width-80}:h={height-80}:color=0x8B2EFF@1.0:t=6,drawtext=text='@Code_With_Mangesh':fontsize=54:fontcolor=0xFFD900:x=100:y=120,drawtext=text='{prompt[:40]}':fontsize=42:fontcolor=white:x=100:y=250",
                    "-vframes", "1",
                    str(filepath)
                ]
                subprocess.run(cmd, capture_output=True)

        res_metadata = {
            "prompt": prompt,
            "style": style,
            "dimensions": f"{width}x{height}",
            "file_path": str(filepath),
            "filename": filename,
            "provider": provider_used,
            "source_url": source_url,
            "created_at": time.time()
        }
        
        # Save to database
        db.add_knowledge("generated_images", prompt[:50], json_dump := str(res_metadata), metadata=res_metadata)
        log_event(f"Image saved to: {filepath}", component="ImageAgent")
        return res_metadata

image_creation_agent = ImageCreationAgent()
