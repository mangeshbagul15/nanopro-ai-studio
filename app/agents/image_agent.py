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
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import IMAGE_OUTPUT_DIR
from app.core.logger import log_event
from app.core.database import db

class ImageCreationAgent:
    def __init__(self):
        self.output_dir = IMAGE_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_image(self, prompt: str, style: str = "modern_tech", width: int = 1080, height: int = 1920) -> Dict[str, Any]:
        """
        Generates an image from prompt.
        If an external image service / local Stable Diffusion is configured, calls it.
        Otherwise creates a high-res educational SVG/PNG thumbnail card.
        """
        log_event(f"ImageCreationAgent generating image for: {prompt[:60]}", component="ImageAgent")
        timestamp = int(time.time())
        filename = f"gen_img_{timestamp}.png"
        filepath = self.output_dir / filename

        # 1. Try Generative AI via Pollinations.ai (Zero-Config, Free Lifetime, FLUX/SD)
        pollinations_success = False
        try:
            enhanced_prompt = f"{prompt}, style {style}, professional 8k sharp, cinematic lighting, trending on artstation"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            # Use 512x512 or scaled dimensions for fast generation
            target_w = min(width, 1024)
            target_h = min(height, 1024)
            poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={target_w}&height={target_h}&model=flux&nologo=true&seed={timestamp%100000}"
            req = urllib.request.Request(poll_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NanoProAI/1.0"})
            with urllib.request.urlopen(req, timeout=18) as resp:
                img_data = resp.read()
                if len(img_data) > 1000:
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    pollinations_success = True
                    log_event(f"Pollinations.ai generated real AI image ({len(img_data)} bytes) for: {prompt[:40]}", component="ImageAgent")
        except Exception as pe:
            log_event(f"Pollinations.ai skipped or offline ({pe}), using local graphics canvas fallback.", component="ImageAgent")

        # 2. Fallback to local Pillow or FFmpeg canvas if offline
        if not pollinations_success:
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
            "created_at": time.time()
        }
        
        # Save to database
        db.add_knowledge("generated_images", prompt[:50], json_dump := str(res_metadata), metadata=res_metadata)
        log_event(f"Image saved to: {filepath}", component="ImageAgent")
        return res_metadata

image_creation_agent = ImageCreationAgent()
