import ast
import base64
import io
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "agents" / "image_agent.py"


def load_generate_image(fake_replicate, output_dir):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ImageCreationAgent")
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "generate_image")
    module = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "Dict": dict, "Any": object, "Optional": object, "Path": Path,
        "json": json, "base64": base64,
        "os": __import__("os"), "time": __import__("time"),
        "uuid": uuid,
        "subprocess": __import__("subprocess"), "urllib": __import__("urllib"),
        "log_event": lambda *args, **kwargs: None,
        "db": SimpleNamespace(add_knowledge=lambda *args, **kwargs: None),
        "credentials_vault": SimpleNamespace(get_credential=lambda name: None),
    }
    exec(compile(module, str(SOURCE), "exec"), namespace)
    method_fn = namespace["generate_image"]
    obj = SimpleNamespace(output_dir=Path(output_dir))
    return lambda *args, **kwargs: method_fn(obj, *args, **kwargs)


class SceneImageGenerationTests(unittest.TestCase):
    def test_gemini_image_api_generates_prompt_specific_portrait_keyframe(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(is_available=lambda: False)
            generate = load_generate_image(fake, temp)
            image_bytes = b"\x89PNG\r\n\x1a\n" + b"x" * 1200
            response = {"candidates": [{"content": {"parts": [
                {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(image_bytes).decode("ascii")}}
            ]}}]}
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch.dict("os.environ", {"GEMINI_API_KEY": "AIza-test-image-key", "OPENAI_API_KEY": "", "POLLINATIONS_API_KEY": ""}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(response).encode("utf-8"))) as request:
                result = generate("Solar photons release electrons inside silicon cells", allow_local_fallback=False, preserve_prompt=True)
            self.assertEqual(result["provider"], "gemini-flash-image")
            self.assertTrue(Path(result["file_path"]).is_file())
            api_request = request.call_args.args[0]
            self.assertEqual(api_request.get_header("X-goog-api-key"), "AIza-test-image-key")
            payload = json.loads(api_request.data.decode("utf-8"))
            self.assertEqual(payload["generationConfig"]["imageConfig"]["aspectRatio"], "9:16")
            self.assertIn("silicon cells", payload["contents"][0]["parts"][0]["text"])

    def test_cloudflare_workers_ai_generates_prompt_specific_portrait_keyframe(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(is_available=lambda: False)
            generate = load_generate_image(fake, temp)
            image_bytes = b"\xff\xd8\xff" + b"x" * 1200
            response = {"result": {"image": base64.b64encode(image_bytes).decode("ascii")}}
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch.dict("os.environ", {"CLOUDFLARE_ACCOUNT_ID": "account-test", "CLOUDFLARE_API_TOKEN": "cfut-test", "GEMINI_API_KEY": "", "OPENAI_API_KEY": "", "POLLINATIONS_API_KEY": ""}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(response).encode("utf-8"))) as request:
                result = generate("Solar photons strike silicon cells", allow_local_fallback=False, preserve_prompt=True)
            self.assertEqual(result["provider"], "cloudflare-flux-schnell")
            api_request = request.call_args.args[0]
            self.assertIn("/accounts/account-test/ai/run/@cf/black-forest-labs/flux-1-schnell", api_request.full_url)
            self.assertEqual(api_request.get_header("Authorization"), "Bearer cfut-test")
            self.assertIn("Solar photons strike silicon cells", json.loads(api_request.data.decode("utf-8"))["prompt"])

    def test_pollinations_uses_authenticated_current_generation_endpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(is_available=lambda: False)
            generate = load_generate_image(fake, temp)
            payload = b"\x89PNG\r\n\x1a\n" + b"x" * 1200
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch.dict("os.environ", {"POLLINATIONS_API_KEY": "sk-test-pollen-key", "OPENAI_API_KEY": ""}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(payload)) as request:
                result = generate("A water cycle evaporation scene", allow_local_fallback=False, preserve_prompt=True)
            self.assertEqual(result["provider"], "pollinations-flux")
            self.assertTrue(request.call_args.args[0].full_url.startswith("https://gen.pollinations.ai/image/"))
            self.assertEqual(request.call_args.args[0].get_header("Authorization"), "Bearer sk-test-pollen-key")

    def test_openai_images_is_used_when_replicate_is_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(is_available=lambda: False)
            generate = load_generate_image(fake, temp)
            response = {"data": [{"b64_json": base64.b64encode(b"x" * 1200).decode("ascii")}]}
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-image-key"}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(response).encode("utf-8"))) as request:
                result = generate("A close-up cutaway of silicon cells releasing electrons", allow_local_fallback=False, preserve_prompt=True)
            self.assertEqual(result["provider"], "openai-gpt-image")
            self.assertTrue(Path(result["file_path"]).is_file())
            request_data = json.loads(request.call_args.args[0].data.decode("utf-8"))
            self.assertIn("silicon cells releasing electrons", request_data["prompt"])
            self.assertEqual(request_data["size"], "1024x1536")

    def test_strict_scene_mode_raises_instead_of_creating_placeholder(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(is_available=lambda: False)
            generate = load_generate_image(fake, temp)
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch("urllib.request.urlopen", side_effect=OSError("offline")):
                with self.assertRaisesRegex(RuntimeError, "prompt-specific image") as raised:
                    generate("A solar panel converting sunlight", allow_local_fallback=False)
            self.assertIn("Gemini", str(raised.exception))
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_scene_mode_preserves_visual_prompt(self):
        with tempfile.TemporaryDirectory() as temp:
            prompt = "A close-up cutaway of silicon cells converting photons into electron flow"
            received = []
            fake = SimpleNamespace(
                is_available=lambda: True,
                generate_image=lambda **kwargs: received.append(kwargs) or {"image_url": "https://img.example/solar.png"},
            )
            generate = load_generate_image(fake, temp)
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(b"x" * 1200)):
                generate(prompt, preserve_prompt=True)
            self.assertIn(prompt, received[0]["prompt"])
            self.assertNotIn("artstation", received[0]["prompt"].lower())

    def test_scene_image_returns_provider_url(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(
                is_available=lambda: True,
                generate_image=lambda **kwargs: {"image_url": "https://img.example/scene.png"},
            )
            generate = load_generate_image(fake, temp)
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(b"x" * 1200)):
                result = generate("A solar panel", allow_local_fallback=False, preserve_prompt=True)
            self.assertEqual(result.get("source_url"), "https://img.example/scene.png")

    def test_scene_prompt_forbids_people_and_requests_technical_visuals(self):
        with tempfile.TemporaryDirectory() as temp:
            prompt = "Explain a CI/CD pipeline to a beginner"
            received = []
            fake = SimpleNamespace(
                is_available=lambda: True,
                generate_image=lambda **kwargs: received.append(kwargs) or {"image_url": "https://img.example/ci.png"},
            )
            generate = load_generate_image(fake, temp)
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch("urllib.request.urlopen", return_value=io.BytesIO(b"x" * 1200)):
                generate(prompt, preserve_prompt=True, width=1080, height=1920)
            sent = received[0]["prompt"]
            self.assertIn(prompt, sent)
            self.assertIn("no people", sent.lower())
            self.assertIn("technical motion-graphics", sent.lower())
            self.assertEqual(received[0]["aspect_ratio"], "9:16")

    def test_concurrent_scene_calls_get_distinct_output_files(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(
                is_available=lambda: True,
                generate_image=lambda **kwargs: {"image_url": "https://img.example/scene.png"},
            )
            generate = load_generate_image(fake, temp)
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch("urllib.request.urlopen", side_effect=lambda *args, **kwargs: io.BytesIO(b"x" * 1200)), \
                 patch("time.time", return_value=1700000000):
                first = generate("Scene one")
                second = generate("Scene two")
            self.assertNotEqual(first["filename"], second["filename"])


if __name__ == "__main__":
    unittest.main()
