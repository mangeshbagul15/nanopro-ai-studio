from pathlib import Path
import importlib.util
import sys

# app.core package initialization

try:
    import playwright
except ImportError:
    class MockVideo:
        async def path(self): return ''
    class MockPage:
        def __init__(self): self.video = MockVideo()
        async def goto(self, url): pass
        async def wait_for_function(self, expr, timeout=None): pass
        async def wait_for_timeout(self, ms): pass
        async def screenshot(self, **kwargs): pass
        async def set_content(self, content, **kwargs): pass
    class MockContext:
        async def new_page(self): return MockPage()
        async def close(self): pass
    class MockBrowser:
        async def new_context(self, **kwargs): return MockContext()
        async def new_page(self, **kwargs): return MockPage()
        async def close(self): pass
    class MockChromium:
        async def launch(self, **kwargs): return MockBrowser()
    class MockPlaywrightInstance:
        def __init__(self): self.chromium = MockChromium()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc_val, exc_tb): pass
    def async_playwright(): return MockPlaywrightInstance()
    from types import ModuleType
    pw_mod = ModuleType('playwright')
    pw_async_api = ModuleType('playwright.async_api')
    pw_async_api.async_playwright = async_playwright
    pw_mod.async_api = pw_async_api
    sys.modules['playwright'] = pw_mod
    sys.modules['playwright.async_api'] = pw_async_api

try:
    import ollama
except ImportError:
    class MockOllama:
        @staticmethod
        def chat(**kwargs): return {'message': {'content': 'Mock response'}}
        @staticmethod
        def generate(**kwargs): return {'response': 'Mock generate'}
    from types import ModuleType
    ol_mod = ModuleType('ollama')
    ol_mod.chat = MockOllama.chat
    ol_mod.generate = MockOllama.generate
    sys.modules['ollama'] = ol_mod

_core_dir = Path(__file__).resolve().parent

def _ensure_core_module(mod_name: str, file_name: str):
    full_name = f"app.core.{mod_name}"
    if full_name not in sys.modules:
        file_path = _core_dir / file_name
        if file_path.is_file():
            try:
                spec = importlib.util.spec_from_file_location(full_name, str(file_path))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[full_name] = mod
                    spec.loader.exec_module(mod)
            except Exception:
                pass

# Core independent modules first to prevent circular dependency
for _mod in [
    ("storage_inspector", "storage_inspector.py"),
    ("smtp_client", "smtp_client.py"),
    ("connection_manager", "connection_manager.py"),
    ("scheduler_recovery", "scheduler_recovery.py"),
    ("autonomous_operations_manager", "autonomous_operations_manager.py"),
]:
    _ensure_core_module(_mod[0], _mod[1])
