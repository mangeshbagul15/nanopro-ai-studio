# Global AI Lab Explorer and Orchestrator Repair

## Goal

Restore authenticated Explorer and Orchestrator API calls, make AWS S3 listing failures actionable, and preserve existing NanoPro data tools.

## Findings

- Cloudflare serves `deploy/complete_nanopro_dashboard.html` as a static asset. The Global AI Lab Python view's protected API calls did not explicitly send `X-Session-Token`.
- `/api/banking/*` requires a validated NanoPro session. The modal converted HTTP 401 into a generic expired-session message without a direct login action.
- The AWS catalog loader is unchanged from the pre-change dashboard. AWS returns an `AccessDenied` for `s3:ListBucket`, so the backend correctly returns an unreachable catalog entry without schemas.
- The old-looking Explorer launcher text existed before the previous reinjection; it launches the current modal. The modal itself is the newer implementation.
- Existing S3 features include lake-key listing, a write probe, bucket hardening, and DuckDB snapshot sync. They must not be removed or duplicated.

## Design

1. Add a same-origin-only session-aware fetch helper that reads the existing `nanopro_session_token` from local storage and sets `X-Session-Token`. Use it for protected Explorer and Orchestrator calls. Keep browser same-origin cookies enabled and leave validation to the backend.
2. Stop Explorer retries on HTTP 401 and show a direct login action. Give the Orchestrator 401 state the same action.
3. Render the real S3 error and configured bucket detail inline when an AWS node is expanded. Show the `s3:ListBucket` hint only for list/access-denied errors.
4. Update the launcher subtitle to list the current DAG, SFTP, Alerts, and Logs tabs.
5. Fix `scripts/reinject_ailab.py` so it does not duplicate the Global AI Lab section marker in the static asset.

## AWS Access Boundary

The configured AWS identity must be granted S3 permissions in AWS; application code cannot change IAM policies. The observed tree error requires `s3:ListBucket` on the configured bucket, and object previews need `s3:GetObject`. Existing write/hardening operations need their corresponding S3 permissions. Scope any full S3 administrator policy to the configured NanoPro bucket unless the account owner explicitly intends account-wide access.

## Verification

- Python source/static-asset contract tests run with `python -m unittest tests.test_global_ai_lab_api_auth -v`.
- Node tests verify same-origin token forwarding and cross-origin token isolation.
- Check Python compilation, Worker syntax, and all extracted dashboard inline scripts.
- Verify authenticated APIs after deployment. S3 objects appear only after the AWS identity's IAM policy allows listing.

## Out of Scope

- Rebuilding the Explorer or replacing existing S3 tools.
- Making protected APIs public or bypassing backend session validation.
- Changing AWS IAM policies or storing AWS credentials in the repository.
