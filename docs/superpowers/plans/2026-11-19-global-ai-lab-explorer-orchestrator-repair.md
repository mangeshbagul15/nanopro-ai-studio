# Global AI Lab Explorer and Orchestrator Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore protected Explorer and Orchestrator requests and clearly surface AWS S3 access errors without rebuilding existing functionality.

**Architecture:** Add a same-origin-only fetch helper to the generated Global AI Lab view and use it for protected APIs. Keep the backend as the authority for session validation, preserve existing S3 utilities, and regenerate the Cloudflare static asset from the Python view.

**Tech Stack:** Python, embedded JavaScript, FastAPI, Cloudflare Workers, `unittest`, Node.js.

---

### Task 1: Add regression coverage

**Files:**
- Create: `tests/test_global_ai_lab_api_auth.py`
- Create: `tests/test_global_ai_lab_auth_helper.js`

- [x] **Step 1: Add source/static contract tests**

The Python tests read `app/ui/global_ai_lab_view.py` and `deploy/complete_nanopro_dashboard.html` directly, avoiding app bootstrap side effects. They verify the auth helper and call sites, login actions, actionable `s3:ListBucket` errors, updated launcher wording, and exactly one Global AI Lab section marker.

- [x] **Step 2: Add runtime tests for the JavaScript helper**

Use Node's built-in `node:test` and `vm` modules to run the helper with mocked `window`, `localStorage`, and `fetch`; assert same-origin requests receive `X-Session-Token` and other origins do not.

### Task 2: Implement protected request handling and AWS diagnostics

**Files:**
- Modify: `app/ui/global_ai_lab_view.py`

- [x] **Step 1: Add the same-origin helper**

```javascript
window.ailabAuthFetch = function(url, options = {}) {
  const headers = new Headers(options.headers || {});
  let token = "";
  try {
    token = localStorage.getItem("nanopro_session_token") || "";
  } catch (_) {}
  if (token && new URL(url, window.location.href).origin === window.location.origin) {
    headers.set("X-Session-Token", token);
  }
  return fetch(url, {
    ...options,
    headers,
    credentials: options.credentials || "same-origin"
  });
};
```

- [x] **Step 2: Use it for Explorer requests**

Use `ailabAuthFetch` for `/api/ai/explorer/catalog`, `/table`, `/schema`, rename/delete, and column operations. On catalog HTTP 401, stop retrying and display `/login_gateway.html`. When an expanded S3 catalog entry contains a `ListObjectsV2`/`AccessDenied` error, show the escaped backend error, bucket detail, and `s3:ListBucket` hint.

- [x] **Step 3: Use it for Orchestrator requests**

Use `ailabAuthFetch` for overview, DAG run/pause/rollback, schedule, report build, SFTP upload/process/sample/rollback, alert config/test, and logs. Make the overview 401 message link to `/login_gateway.html`.

### Task 3: Regenerate the static view safely

**Files:**
- Modify: `scripts/reinject_ailab.py`
- Regenerate: `deploy/complete_nanopro_dashboard.html`
- Modify: `app/ui/global_ai_lab_view.py`

- [x] **Step 1: Align the launcher subtitle**

Use `DAGs • SFTP • Alerts • Logs`, retaining the existing launch action and modal.

- [x] **Step 2: Prevent duplicate section markers**

Use the generated `fresh_html` directly as the replacement because it already begins with the Global AI Lab marker:

```python
replacement = f"{fresh_html}\n\n        "
```

- [x] **Step 3: Regenerate and verify**

Run: `python scripts/reinject_ailab.py`

Expected: `Successfully replaced in deploy/complete_nanopro_dashboard.html!` and one Global AI Lab section marker.

### Task 4: Validate and complete

**Files:**
- Validate: `app/ui/global_ai_lab_view.py`
- Validate: `deploy/complete_nanopro_dashboard.html`
- Preserve: `/api/de_modern/lake/keys`, `/api/aws/s3_probe`, `/api/aws/s3_harden`, DuckDB-to-S3 sync

- [x] **Step 1: Run regression tests**

Run: `python -m unittest tests.test_global_ai_lab_api_auth -v`

Expected: all tests pass.

- [x] **Step 2: Run helper behavior tests**

Run: `node --test tests/test_global_ai_lab_auth_helper.js`

Expected: two tests pass.

- [x] **Step 3: Run syntax validation**

Run: `python -m py_compile app/ui/global_ai_lab_view.py` and `node --check deploy/cloudflare_worker_gateway.js`.

Extract each inline script from `deploy/complete_nanopro_dashboard.html` into `%TEMP%\nanopro_inline_js_check\block_N.js` and run `node --check` on each script.

- [ ] **Step 4: Commit, push, and deploy**

Commit the source view, generated asset, reinjection fix, and tests. Push the repair branch and deploy the Cloudflare Worker asset. Do not use any exposed Cloudflare API token.

- [ ] **Step 5: Verify live state**

Verify the login actions, updated launcher, and authenticated Orchestrator. Verify live AWS objects only after the AWS identity is granted `s3:ListBucket` (and `s3:GetObject` for previews) on the configured bucket.
