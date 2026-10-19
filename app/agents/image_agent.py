"""
Mangesh Nano Pro AI Studio - Agent 2: Image Creation Agent
Generates YouTube thumbnails, technical diagrams, educational illustrations,
and saves metadata to the local project store.
"""

import os
import time
import json
import base64
import subprocess
import urllib.request
import urllib.parse
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import IMAGE_OUTPUT_DIR
from app.core.logger import log_event
from app.core.database import db
from app.core.database import credentials_vault

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
        # Scene keyframes fill the whole 9:16 frame, so they must read as technical
        # motion graphics for the narrated mechanism, never as stock photos of people.
        # The model-authored visual prompt is always kept verbatim and first.
        scene_directives = (
            "Render this as a vertical 9:16 technical motion-graphics frame for a short tech explainer: "
            "stylised 3D isometric illustration or abstract diagram of the exact mechanism described, "
            "clearly separated component shapes, glowing data-flow lines, clean interface panels, "
            "deep navy background, dramatic rim lighting, crisp detail, "
            "balanced empty space in the top and bottom thirds for captions. "
            "Strictly no people, no human figures, no presenter, no faces, no hands, no silhouettes, "
            "no text, no letters, no captions, no watermark, no logo."
        )
        provider_prompt = (
            f"{prompt}. {scene_directives}"
            if preserve_prompt
            else f"{prompt}, style {style}, 8k sharp, cinematic lighting"
        )
        # Ask image models for a native 9:16 frame. Generating square and cropping
        # to portrait later slices away roughly 44% of the composed artwork.
        requested_ratio = "9:16" if height >= width else "16:9"
        try:
            from app.core.replicate_engine import replicate_engine
            if replicate_engine.is_available():
                # FLUX 1.1 Pro carries noticeably more photographic detail than the
                # fast Schnell variant; fall back when the better model is unavailable.
                for replicate_model in ("black-forest-labs/flux-1.1-pro", "black-forest-labs/flux-schnell"):
                    try:
                        rep_res = replicate_engine.generate_image(
                            prompt=provider_prompt,
                            model=replicate_model,
                            aspect_ratio=requested_ratio,
                        )
                    except Exception as model_error:
                        log_event(
                            f"Replicate [{replicate_model}] failed ({type(model_error).__name__}); trying next image model.",
                            level="WARNING",
                            component="ImageAgent",
                        )
                        continue
                    img_url = (rep_res or {}).get("image_url")
                    if not img_url:
                        continue
                    # Download Replicate image to output directory
                    req_rep = urllib.request.Request(img_url, headers={"User-Agent": "NanoProAI/2.0"})
                    with urllib.request.urlopen(req_rep, timeout=15) as r_resp:
                        r_bytes = r_resp.read()
                    if len(r_bytes) > 1000:
                        with open(filepath, "wb") as f:
                            f.write(r_bytes)
                        image_generated = True
                        provider_used = "replicate-flux-schnell" if "schnell" in replicate_model else "replicate-flux-pro"
                        source_url = img_url
                        log_event(f"Replicate [{replicate_model}] generated AI image ({len(r_bytes)} bytes) for: {prompt[:40]}", component="ImageAgent")
                        break
        except Exception as re_err:
            log_event(f"Replicate image provider failed ({type(re_err).__name__}); trying configured image providers.", component="ImageAgent")

        # 2. Gemini image generation. Reuse the configured Google key and explicitly
        # request a portrait image so scene assets are born in the Shorts/Reels ratio.
        if not image_generated:
            try:
                gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
                if not gemini_key:
                    for credential_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI", "GOOGLE"):
                        credential = credentials_vault.get_credential(credential_name)
                        value = (credential or {}).get("secret_value", "")
                        if value and not value.startswith("••"):
                            gemini_key = value
                            break
                if gemini_key:
                    for model_name in ("gemini-3.1-flash-image", "gemini-2.5-flash-image"):
                        # 1K portrait output already matches the 1080x1920 render target.
                        # Asking for 2K doubled peak RAM here and got the 512 MB Render
                        # container restarted mid-render, which surfaced in the browser
                        # as "Unexpected end of JSON input".
                        payload = {
                            "contents": [{"parts": [{"text": provider_prompt}]}],
                            "generationConfig": {
                                "responseModalities": ["IMAGE"],
                                "imageConfig": {
                                    "aspectRatio": requested_ratio,
                                    "imageSize": "1K",
                                },
                            },
                        }
                        request = urllib.request.Request(
                            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
                            data=json.dumps(payload).encode("utf-8"),
                            headers={
                                "x-goog-api-key": gemini_key,
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            },
                        )
                        try:
                            with urllib.request.urlopen(request, timeout=90) as response:
                                response_data = json.loads(response.read().decode("utf-8"))
                        except Exception as model_error:
                            status_code = getattr(model_error, "code", None)
                            status_label = getattr(model_error, "reason", "")
                            provider_status = f"HTTP {status_code}" if status_code else type(model_error).__name__
                            if status_label:
                                provider_status += f" {str(status_label)[:80]}"
                            log_event(f"Gemini image model {model_name} failed ({provider_status}); trying fallback model if available.", level="WARNING", component="ImageAgent")
                            continue
                        parts = (((response_data.get("candidates") or [{}])[0]).get("content") or {}).get("parts") or []
                        inline_image = next((part.get("inlineData") or part.get("inline_data") for part in parts if part.get("inlineData") or part.get("inline_data")), None)
                        encoded_image = (inline_image or {}).get("data")
                        if encoded_image:
                            image_bytes = base64.b64decode(encoded_image, validate=True)
                            if len(image_bytes) > 1000:
                                filepath.write_bytes(image_bytes)
                                image_generated = True
                                provider_used = "gemini-flash-image"
                                log_event(f"Gemini generated prompt-specific portrait image ({len(image_bytes)} bytes).", component="ImageAgent")
                                break
            except Exception as gemini_error:
                log_event(f"Gemini image provider failed ({type(gemini_error).__name__}); trying OpenAI if configured.", level="WARNING", component="ImageAgent")

        # 3. OpenAI image generation. Render deployments commonly configure OpenAI
        # for narration/storyboards; reuse that server-side key for prompt-specific art.
        if not image_generated:
            try:
                openai_key = os.getenv("OPENAI_API_KEY", "")
                if not openai_key:
                    for credential_name in ("OPENAI_API_KEY", "OPENAI_API", "OPENAI"):
                        credential = credentials_vault.get_credential(credential_name)
                        value = (credential or {}).get("secret_value", "")
                        if value and not value.startswith("••"):
                            openai_key = value
                            break
                if openai_key:
                    target_size = "1024x1536" if height >= width else "1536x1024"
                    payload = {
                        "model": "gpt-image-1",
                        "prompt": provider_prompt,
                        "size": target_size,
                        "quality": "medium",
                        "n": 1,
                    }
                    request = urllib.request.Request(
                        "https://api.openai.com/v1/images/generations",
                        data=json.dumps(payload).encode("utf-8"),
                        headers={
                            "Authorization": f"Bearer {openai_key}",
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        },
                    )
                    with urllib.request.urlopen(request, timeout=90) as response:
                        response_data = json.loads(response.read().decode("utf-8"))
                    encoded_image = ((response_data.get("data") or [{}])[0]).get("b64_json")
                    if encoded_image:
                        image_bytes = base64.b64decode(encoded_image, validate=True)
                        if len(image_bytes) > 1000:
                            filepath.write_bytes(image_bytes)
                            image_generated = True
                            provider_used = "openai-gpt-image"
                            log_event(f"OpenAI generated prompt-specific image ({len(image_bytes)} bytes).", component="ImageAgent")
            except Exception as openai_error:
                status_code = getattr(openai_error, "code", None)
                provider_status = f"HTTP {status_code}" if status_code else type(openai_error).__name__
                log_event(f"OpenAI image provider failed ({provider_status}); trying Pollinations if configured.", level="WARNING", component="ImageAgent")

        # 4. Cloudflare Workers AI FLUX provides an independent prompt-specific fallback.
        if not image_generated:
            try:
                cloudflare_account = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
                cloudflare_token = os.getenv("CLOUDFLARE_API_TOKEN", "") or os.getenv("CLOUDFLARE_WORKERS_AI_TOKEN", "")
                if not cloudflare_token:
                    for credential_name in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_WORKERS_AI_TOKEN", "CLOUDFLARE"):
                        credential = credentials_vault.get_credential(credential_name)
                        value = (credential or {}).get("secret_value", "")
                        if value and not value.startswith("••"):
                            cloudflare_token = value
                            break
                if cloudflare_account and cloudflare_token:
                    cloudflare_payload = json.dumps({"prompt": provider_prompt}).encode("utf-8")
                    cloudflare_request = urllib.request.Request(
                        f"https://api.cloudflare.com/client/v4/accounts/{cloudflare_account}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                        data=cloudflare_payload,
                        headers={
                            "Authorization": f"Bearer {cloudflare_token}",
                            "Content-Type": "application/json",
                            "Accept": "image/*, application/json",
                        },
                    )
                    with urllib.request.urlopen(cloudflare_request, timeout=90) as response:
                        response_body = response.read()
                        content_type = response.headers.get("Content-Type", "") if hasattr(response, "headers") else ""
                    if "json" in content_type.lower() or response_body.lstrip().startswith(b"{"):
                        parsed = json.loads(response_body.decode("utf-8"))
                        encoded_image = (parsed.get("result") or {}).get("image")
                        image_bytes = base64.b64decode(encoded_image, validate=True) if encoded_image else b""
                    else:
                        image_bytes = response_body
                    if len(image_bytes) > 1000 and image_bytes.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"RIFF")):
                        filepath.write_bytes(image_bytes)
                        image_generated = True
                        provider_used = "cloudflare-flux-schnell"
                        source_url = "https://api.cloudflare.com/client/v4"
                        log_event(f"Cloudflare Workers AI generated prompt-specific image ({len(image_bytes)} bytes).", component="ImageAgent")
            except Exception as cloudflare_error:
                status_code = getattr(cloudflare_error, "code", None)
                provider_status = f"HTTP {status_code}" if status_code else type(cloudflare_error).__name__
                log_event(f"Cloudflare Workers AI image provider failed ({provider_status}); trying Pollinations if configured.", level="WARNING", component="ImageAgent")

        # 5. Current Pollinations API requires an API key; resolve it from env/vault.
        if not image_generated:
            try:
                poll_key = os.getenv("POLLINATIONS_API_KEY", "")
                if not poll_key:
                    for credential_name in ("POLLINATIONS_API_KEY", "POLLINATIONS_API", "POLLINATIONS"):
                        credential = credentials_vault.get_credential(credential_name)
                        value = (credential or {}).get("secret_value", "")
                        if value and not value.startswith("••"):
                            poll_key = value
                            break
                if poll_key:
                    enhanced_prompt = provider_prompt
                    encoded_prompt = urllib.parse.quote(enhanced_prompt, safe="")
                    target_w = min(width, 1024)
                    target_h = min(height, 1536)
                    poll_url = f"https://gen.pollinations.ai/image/{encoded_prompt}?width={target_w}&height={target_h}&model=black-forest-labs/flux.1-schnell"
                    request = urllib.request.Request(poll_url, headers={"Authorization": f"Bearer {poll_key}", "Accept": "image/*"})
                    with urllib.request.urlopen(request, timeout=90) as response:
                        img_data = response.read()
                    valid_image = (
                        img_data.startswith(b"\x89PNG\r\n\x1a\n")
                        or img_data.startswith(b"\xff\xd8\xff")
                        or (img_data.startswith(b"RIFF") and img_data[8:12] == b"WEBP")
                        or img_data.startswith((b"GIF87a", b"GIF89a"))
                    )
                    if len(img_data) > 1000 and valid_image:
                        filepath.write_bytes(img_data)
                        image_generated = True
                        provider_used = "pollinations-flux"
                        source_url = "https://gen.pollinations.ai"
                        log_event(f"Pollinations generated prompt-specific image ({len(img_data)} bytes).", component="ImageAgent")
            except Exception as pe:
                log_event(f"Pollinations image provider failed ({type(pe).__name__}).", level="WARNING", component="ImageAgent")

        # Scene renders must fail closed instead of silently returning a text card.
        if not image_generated and not allow_local_fallback:
            raise RuntimeError(
                "NanoPro could not generate a prompt-specific image. Configure a valid Replicate, Gemini, OpenAI, Cloudflare Workers AI, or Pollinations image API key with image-generation access and retry."
            )

        # 6. Fallback to local Pillow or FFmpeg canvas if offline (legacy callers only).
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
