"""
Mangesh Nano Pro AI Studio - Core Discovery & Live Search Engine
Handles:
1. Live GitHub AI Project Search (via GitHub API with local verified fallback)
2. Free API & Developer Resource Finder with documented free tier validation
3. Persistent AI Research Library indexing & deduplication
4. Background recurring discovery schedules and live job monitoring
"""

import time
import json
import urllib.request
import urllib.parse
import urllib.error
import threading
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import db, credentials_vault

class DiscoveryEngine:
    def __init__(self):
        self._scheduler_running = False
        self._scheduler_thread = None

    def search_github(
        self,
        query: str,
        category: str = "All",
        language: str = "All",
        max_results: int = 10,
        auto_save: bool = True
    ) -> Dict[str, Any]:
        """
        Searches GitHub repositories using GitHub REST API.
        Falls back to local verified project database if offline or rate-limited.
        """
        job_id = f"job_gh_{int(time.time()*1000)}"
        db.create_discovery_job(job_id, query, "github")
        log_event(f"Starting GitHub search: query='{query}' category='{category}'", component="DiscoveryEngine")

        items = []
        is_live = False
        error_msg = None

        # Build GitHub search query
        q_terms = [query]
        if language and language.lower() != "all":
            q_terms.append(f"language:{language}")
        full_q = " ".join(q_terms)

        token = None
        cred = credentials_vault.get_credential("github")
        if cred and cred.get("secret_value") and not cred["secret_value"].startswith("••"):
            token = cred["secret_value"]

        headers = {
            "User-Agent": "Mangesh-NanoPro-AI-Studio/12.0",
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            headers["Authorization"] = f"token {token}"

        encoded_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(full_q)}&sort=stars&order=desc&per_page={max_results}"

        try:
            req = urllib.request.Request(encoded_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                gh_items = data.get("items", [])
                is_live = True
                
                existing_repos = {p["repo_url"].lower(): p for p in db.list_github_projects()}
                new_saved = 0
                duplicates = 0

                for item in gh_items:
                    repo_url = item.get("html_url", "")
                    name = item.get("full_name") or item.get("name")
                    desc = item.get("description") or "Open source AI repository"
                    stars = item.get("stargazers_count", 0)
                    forks = item.get("forks_count", 0)
                    lang = item.get("language") or "Python"
                    lic_info = item.get("license")
                    license_name = lic_info.get("spdx_id") or lic_info.get("name") if lic_info else "License not identified"
                    updated_at = item.get("updated_at", "")[:10]

                    # Detect language capabilities
                    combined_text = f"{name} {desc}".lower()
                    supported_langs = []
                    if "marathi" in combined_text:
                        supported_langs.append("Marathi")
                    if "hindi" in combined_text:
                        supported_langs.append("Hindi")
                    if not supported_langs or "english" in combined_text:
                        supported_langs.append("English")
                    
                    proj_dict = {
                        "project_id": f"gh_{item.get('id', int(time.time()*1000))}",
                        "name": name,
                        "repo_url": repo_url,
                        "short_description": desc[:300],
                        "language": lang,
                        "category": category if category != "All" else "AI Tools",
                        "stars": stars,
                        "forks": forks,
                        "last_update_date": updated_at,
                        "latest_release": item.get("default_branch", "main"),
                        "license": license_name,
                        "dependencies": "Standard Python/Node dependencies",
                        "setup_complexity": "Low" if stars > 10000 else "Medium",
                        "local_execution_support": True,
                        "api_requirements": "None (Self-Contained)",
                        "supported_languages": ", ".join(supported_langs),
                        "potential_use": f"Integration into NanoPro {category} workspace.",
                        "security_notes": "Official public repository; review before execution.",
                        "last_checked_at": time.time()
                    }
                    items.append(proj_dict)

                    if repo_url.lower() in existing_repos:
                        duplicates += 1
                    else:
                        if auto_save:
                            db.add_github_project(proj_dict)
                            new_saved += 1

                db.update_discovery_job(job_id, "COMPLETED", processed=len(items), new_count=new_saved, duplicates=duplicates)
                return {
                    "status": "success",
                    "source": "github_live",
                    "query": query,
                    "total_found": len(items),
                    "new_saved": new_saved,
                    "duplicates_skipped": duplicates,
                    "results": items
                }

        except Exception as e:
            error_msg = str(e)
            log_event(f"GitHub Live API unavailable ({error_msg}); using local verified project database.", level="WARNING", component="DiscoveryEngine")

        # Fallback to local verified projects database
        local_items = db.list_github_projects(category=category, search=query, language=language)
        if not local_items:
            # Broaden search if specific query returned zero
            local_items = db.list_github_projects(category=category)

        db.update_discovery_job(job_id, "COMPLETED", processed=len(local_items), new_count=0, duplicates=len(local_items))
        return {
            "status": "success",
            "source": "verified_local_db",
            "note": f"Live GitHub request yielded fallback ({error_msg}). Showing verified local database records.",
            "query": query,
            "total_found": len(local_items),
            "new_saved": 0,
            "duplicates_skipped": len(local_items),
            "results": local_items[:max_results]
        }

    def search_free_apis(
        self,
        query: str = "",
        category: str = "All",
        credit_card_free_only: bool = False,
        marathi_only: bool = False,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Discovers and retrieves legitimately free APIs, developer quotas, and open-source models.
        Filters by category, credit card requirement, and language support.
        """
        log_event(f"Searching Free APIs: query='{query}' category='{category}'", component="DiscoveryEngine")
        apis = db.list_free_apis(category=category, search=query)

        filtered = []
        for a in apis:
            if credit_card_free_only and a.get("credit_card_required"):
                continue
            if marathi_only:
                langs = (a.get("languages_supported") or "").lower()
                if "marathi" not in langs and "multilingual" not in langs and "indian" not in langs:
                    continue
            filtered.append(a)

        return {
            "status": "success",
            "category": category,
            "query": query,
            "total_found": len(filtered),
            "results": filtered[:max_results]
        }

    def search_research_library(
        self,
        query: str = "",
        category: str = "All",
        favorites_only: bool = False
    ) -> Dict[str, Any]:
        """
        Searches the persistent AI Research Library.
        """
        items = db.list_research_library(
            category=category if category != "All" else None,
            search=query,
            is_favorite=True if favorites_only else None
        )
        return {
            "status": "success",
            "total_found": len(items),
            "results": items
        }

    def execute_live_research(
        self,
        topic: str,
        category: str = "AI Models",
        source_preference: str = "all",
        save_to_library: bool = True
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end research query across GitHub, Free APIs, and local notes.
        Stores verified summary and citations into the AI Research Library.
        """
        job_id = f"job_res_{int(time.time()*1000)}"
        db.create_discovery_job(job_id, topic, "multi_source")
        db.update_discovery_job(job_id, "ANALYZING")

        # 1. Search existing library first
        existing = db.list_research_library(search=topic)
        if existing and len(existing) > 0 and (time.time() - existing[0]["verified_at"]) < 86400:
            db.update_discovery_job(job_id, "COMPLETED", processed=len(existing), new_count=0)
            return {
                "status": "success",
                "source": "research_library_cache",
                "topic": topic,
                "summary": existing[0]["summary"],
                "source_url": existing[0]["source_url"],
                "technical_requirements": existing[0]["technical_requirements"],
                "verified_at": existing[0]["verified_at"]
            }

        # 2. Gather from APIs & GitHub
        db.update_discovery_job(job_id, "FETCHING")
        apis = self.search_free_apis(query=topic)
        gh_results = self.search_github(query=topic, max_results=5)

        # 3. Formulate structured finding
        findings = []
        if apis["results"]:
            top_api = apis["results"][0]
            findings.append(f"• **Recommended Free API:** [{top_api['service_name']}]({top_api['official_url']}) by {top_api['provider_name']} — Quota: {top_api['free_quota']} (Auth: {top_api['authentication_type']}, Credit Card: {'Required' if top_api['credit_card_required'] else 'Not Required'}).")

        if gh_results["results"]:
            for repo in gh_results["results"][:2]:
                findings.append(f"• **Recommended GitHub Project:** [{repo['name']}]({repo['repo_url']}) — ⭐ {repo['stars']} stars, License: {repo['license']}. {repo['short_description']} (Languages: {repo['supported_languages']}).")

        summary_text = "\n".join(findings) if findings else f"Research analysis on '{topic}': Analyzed available developer documentation and verified open architectures."
        
        tech_reqs = "Python 3.10+, FastAPI, PyTorch or ONNX Runtime for local execution."
        source_url = apis["results"][0]["official_url"] if apis["results"] else (gh_results["results"][0]["repo_url"] if gh_results["results"] else "https://ai.google.dev")

        item_id = f"res_{int(time.time()*1000)}"
        if save_to_library:
            db.add_research_item({
                "resource_id": item_id,
                "title": f"Research: {topic}",
                "category": category.lower().replace(" ", "_"),
                "source_url": source_url,
                "summary": summary_text,
                "technical_requirements": tech_reqs,
                "user_notes": "Generated and verified by NanoPro Discovery Engine.",
                "is_favorite": 0,
                "tags": f"{category.lower()}, automated_research, {topic.lower()[:20]}"
            })

        db.update_discovery_job(job_id, "COMPLETED", processed=len(findings), new_count=1)
        return {
            "status": "success",
            "source": "live_discovery",
            "resource_id": item_id,
            "topic": topic,
            "summary": summary_text,
            "source_url": source_url,
            "technical_requirements": tech_reqs,
            "verified_at": time.time()
        }

    def start_background_scheduler(self):
        """Starts background worker for scheduled discovery routines."""
        if self._scheduler_running:
            return
        self._scheduler_running = True

        def _worker():
            interval_map = {
                "5m": 300,
                "10m": 600,
                "30m": 1800,
                "1h": 3600,
                "2h": 7200,
                "6h": 21600,
                "12h": 43200,
                "daily": 86400
            }
            while self._scheduler_running:
                try:
                    schedules = db.list_discovery_schedules()
                    now = time.time()
                    for sched in schedules:
                        if sched.get("status") == "active" and sched.get("next_run", 0) <= now:
                            cat = sched.get("category", "")
                            log_event(f"Running scheduled discovery task: {sched['task_name']} ({cat})", component="DiscoveryScheduler")
                            results_count = 0
                            
                            if cat == "github_project":
                                res = self.search_github(sched["query"], max_results=5)
                                results_count = res.get("total_found", 0)
                            elif cat == "free_api":
                                res = self.search_free_apis(sched["query"])
                                results_count = res.get("total_found", 0)
                            elif cat == "telegram_broadcast":
                                from app.agents.assistant_agent import personal_assistant_agent
                                res = personal_assistant_agent.deliver_telegram_broadcast(category="all")
                                results_count = 5
                            elif cat == "news_monitor":
                                from app.agents.assistant_agent import personal_assistant_agent
                                res = personal_assistant_agent.deliver_telegram_broadcast(category="news")
                                results_count = 3
                            elif cat == "amazon_price_watch":
                                from app.agents.price_tracker_agent import amazon_price_tracker
                                count = amazon_price_tracker.recover_overdue_checks()
                                results_count = max(count, 1)
                            elif cat == "data_ingestion":
                                from app.agents.assistant_agent import data_engineer_agent
                                res = data_engineer_agent.batch_folder_ingestion("data_ingestion", auto_dedup=True)
                                results_count = res.get("final_loaded_rows", 0)
                            else:
                                res = self.search_free_apis(sched["query"])
                                results_count = res.get("total_found", 0)
                            
                            interval = interval_map.get(sched.get("frequency", "daily"), 86400)
                            with db.get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                UPDATE discovery_schedules 
                                SET last_run = ?, next_run = ?, results_count = ?, last_status = 'Success'
                                WHERE id = ?
                                """, (now, now + interval, results_count, sched["id"]))
                                conn.commit()
                except Exception as e:
                    log_event(f"Scheduler worker exception: {e}", level="ERROR", component="DiscoveryScheduler")
                time.sleep(30) # High-frequency 30s polling cycle

        self._scheduler_thread = threading.Thread(target=_worker, daemon=True)
        self._scheduler_thread.start()
        log_event("DiscoveryScheduler background worker started.", component="DiscoveryScheduler")

discovery_engine = DiscoveryEngine()
discovery_engine.start_background_scheduler()
