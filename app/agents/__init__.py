import sys
import importlib.util
from pathlib import Path

_agents_dir = Path(__file__).resolve().parent

def _ensure_module(mod_name: str, file_name: str):
    full_name = f"app.agents.{mod_name}"
    if full_name not in sys.modules:
        file_path = _agents_dir / file_name
        if file_path.is_file():
            try:
                spec = importlib.util.spec_from_file_location(full_name, str(file_path))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[full_name] = mod
                    setattr(sys.modules[__name__], mod_name, mod)
                    spec.loader.exec_module(mod)
            except Exception as e:
                import traceback
                traceback.print_exc()

_ensure_module("extended_intents", "extended_intents.py")
_ensure_module("agent_registry", "agent_registry.py")
_ensure_module("discovery_engine", "discovery_engine.py")
_ensure_module("voice_assistant", "voice_assistant.py")
_ensure_module("price_tracker_agent", "price_tracker_agent.py")
_ensure_module("career_agent", "career_agent.py")
_ensure_module("learning_agent", "learning_agent.py")
_ensure_module("planning_agent", "planning_agent.py")
_ensure_module("telegram_router", "telegram_router.py")
_ensure_module("discovery_scheduler", "discovery_scheduler.py")
_ensure_module("cloud_trends_agent", "cloud_trends_agent.py")
