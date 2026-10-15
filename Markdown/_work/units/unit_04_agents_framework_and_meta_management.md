# Unit 04: AI Agents Framework & Meta-Management

## Purpose and Responsibility
Defines the enterprise multi-agent meta-orchestration tier:
- `SpecializedAgent` and `AgentRegistry` (45 agents across 6 groups with granular state machines: `Idle`, `Assigned`, `Running`, `Waiting for Dependency`, `Waiting for Approval`, `Retrying`, `Failed`, `Completed`).
- `ManagerAgent` (JARVIS-inspired coordinator handling intent parsing, credential capture, risk evaluation, multi-step pipeline plans).
- `PersonalAssistantAgent` & Specialist agents (`DataEngineerAgent`, `DataAnalystAgent`, `FileConverterAgent`, `MonitoringAgent`).
- `extended_intents.py` (Amazon tracking, job searching, interview practice, planning).
- `telegram_router.py` (Telegram bot authentication whitelist and command dispatch).
- `voice_assistant.py` (Speech commands, Marathi/Hindi/English locale detection, TTS text normalization).

## Files Read
- `app/agents/agent_registry.py`: Registry for 45 specialized agents, permissions, telemetry [Tier 1]
- `app/agents/manager_agent.py`: Central JARVIS orchestrator, intent classifier, credentials auto-detector [Tier 1]
- `app/agents/assistant_agent.py`: Personal assistant, data engineer, analyst, file converter, monitor [Tier 1]
- `app/agents/extended_intents.py`: Modular intent router for careers, prices, learning, planning [Tier 1]
- `app/agents/telegram_router.py`: Bot command handler with access control whitelist [Tier 1]
- `app/agents/voice_assistant.py`: Trilingual voice engine (Marathi, Hindi, English) with TTS preparation [Tier 1]

## Key Classes / Functions
- `AgentRegistry` (`agent_registry.py:131`): [Verified] Holds map of 45 instantiated agents categorized into Groups A through F.
- `SpecializedAgent` (`agent_registry.py:26`): [Verified] Encapsulates state machine, task metrics, durations, permitted tools.
- `ManagerAgent.detect_and_store_credentials()` (`manager_agent.py:37`): [Verified] Scans prompts for passwords, usernames, ports, hostnames, and securely persists them directly into `CredentialsVault`.
- `ManagerAgent.classify_intent()` (`manager_agent.py:86`): [Verified] Assesses operational risk (`LOW`, `MEDIUM`, `HIGH`) and routes prompts to corresponding specialized agents.
- `PersonalAssistantAgent._clean_telegram_text()` (`assistant_agent.py:74`): [Verified] Filters HTML tags down to strict Telegram Bot API whitelist (`b`, `i`, `u`, `s`, `code`, `pre`, `blockquote`, `a`).
- `route_telegram_command()` (`telegram_router.py:13`): [Verified] Enforces chat ID authorization whitelist and handles `/today`, `/tasks`, `/prices`, `/jobs`, `/errors`, `/report`.
- `VoiceAssistant.clean_text_for_speech()` (`voice_assistant.py:22`): [Verified] Cleans markdown syntax, URLs, and code blocks for speech synthesis.

## Dependencies IN & OUT
- **Dependencies IN**: `main.py` API endpoints (`/api/manager/chat`, `/api/voice/interact`, `/api/telegram/*`), UI dashboard.
- **Dependencies OUT**:
  - Internal: `app.core.database`, `app.core.logger`, `app.core.model_adapter`, `app.core.task_manager`, `app.video_maker.unified_video_maker`, `app.agents.price_tracker_agent`, `app.agents.career_agent`, `app.agents.learning_agent`, `app.agents.planning_agent`.
  - External: `urllib.request`, `re`, `xml.etree.ElementTree`, `pandas` (optional).

## Data Touched
- SQLite tables: `credentials`, `tasks`, `approvals`, `conversations`, `project_knowledge`, `reminders`, `communication_logs`.

## Config and Env Variables Used
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_BOT_USERNAME`
- `REMINDERS_CHECK_INTERVAL`

## Error Handling, Retries, Logging, Idempotency
- Telegram dispatch catches `HTTPError`, automatically sanitizes payload, and re-dispatches as plain text fallback to guarantee delivery.
- Chat history maintains conversational multi-turn session persistence in SQLite `conversations` table.
- Agent state transitions are logged with precise timestamps and durations.

## Observed Issues
- **U-UNIT04-01** | Category: Security / Telegram Auth | Severity: Medium | Location: `app/agents/telegram_router.py:14`
  - Evidence: Hardcoded user ID string `"1200023268"` in `authorized_ids = {str(assistant.telegram_chat_id), "1200023268"}`.
  - Fix: Rely solely on configured `assistant.telegram_chat_id` and vault `allowed_user_ids` rather than hardcoded string literal.
- **U-UNIT04-02** | Category: Architecture / Coupling | Severity: Medium | Location: `app/agents/extended_intents.py:8,30,45,60,70`
  - Evidence: In-function deferred imports (`from app.agents.price_tracker_agent import amazon_price_tracker`, `from app.agents.career_agent import career_agent`, etc.) indicate circular import fragility between manager, assistant, and specialist agents.
  - Fix: Decouple agent initialization using dependency injection or central service locator.

## Open Questions
- None.
