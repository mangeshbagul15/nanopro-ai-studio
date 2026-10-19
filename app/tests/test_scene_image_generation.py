import ast
import io
import json
import tempfile
import unittest
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
        "os": __import__("os"), "time": __import__("time"),
        "subprocess": __import__("subprocess"), "urllib": __import__("urllib"),
        "log_event": lambda *args, **kwargs: None,
        "db": SimpleNamespace(add_knowledge=lambda *args, **kwargs: None),
    }
    exec(compile(module, str(SOURCE), "exec"), namespace)
    method_fn = namespace["generate_image"]
    obj = SimpleNamespace(output_dir=Path(output_dir))
    return lambda *args, **kwargs: method_fn(obj, *args, **kwargs)


class SceneImageGenerationTests(unittest.TestCase):
    def test_strict_scene_mode_raises_instead_of_creating_placeholder(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = SimpleNamespace(is_available=lambda: False)
            generate = load_generate_image(fake, temp)
            with patch.dict("sys.modules", {"app.core.replicate_engine": SimpleNamespace(replicate_engine=fake)}), \
                 patch("urllib.request.urlopen", side_effect=OSError("offline")):
                with self.assertRaisesRegex(RuntimeError, "prompt-specific image"):
                    generate("A solar panel converting sunlight", allow_local_fallback=False)
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


if __name__ == "__main__":
    unittest.main()
