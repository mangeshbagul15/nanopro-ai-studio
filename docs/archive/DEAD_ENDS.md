# Dead Ends Log

| Iteration | Approach Tried | Why It Failed | Files Touched |
|-----------|---------------|---------------|---------------|
| 1 | Standard `threading.Lock()` in `ProviderCircuitBreaker` | Deadlocks when `get_summary()` calls `get_state()` while holding lock. Must use `threading.RLock()`. | `app/core/model_adapter.py` |
| 1 | Synchronous `urlopen` to `/api/tags` in `list_installed_models()` | Blocks for 1.0s on cold start or when Ollama is offline, breaching 500ms failover SLA. Must guard with `is_available()` cached check. | `app/core/model_adapter.py` |
| 1 | Narrow fatal error list omitting "disconnect" / "remote" | Causes generic socket disconnections to retry across 3 models on Groq instead of instant failover. | `app/core/model_adapter.py` |
| 1 | Synchronous `db.save_task` in `create_job()` | Blocks caller thread for up to 136ms during heavy disk queueing. | `app/core/task_manager.py` |
