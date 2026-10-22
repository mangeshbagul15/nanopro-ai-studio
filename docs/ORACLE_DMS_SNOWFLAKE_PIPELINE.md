# Oracle → AWS DMS → S3 → Snowflake pipeline

NanoPro's Task Scheduler creates three visible jobs: daily ingestion plus report at 10:00 IST, and report-only jobs every 14 days and monthly at 10:00 IST. They start disabled. Enable them only after the following cloud setup and a manual verification run.

## Required cloud setup

1. Configure a real AWS DMS replication instance, Oracle source endpoint, and S3 target endpoint. The DMS task must use full load plus CDC and have valid table mappings. The Oracle host must be reachable from the DMS replication subnet; a laptop LAN address alone is not reachable from AWS.
2. Configure AWS role credentials for the NanoPro runtime (prefer an instance/task role) and `AWS_DEFAULT_REGION`.
3. Set `NANOPRO_DMS_TASK_ARN` to the already-created DMS task ARN. NanoPro can inspect, start, and stop real DMS tasks; it does not create an AWS replication instance or endpoint automatically.
4. Configure the Snowflake connection in NanoPro's credential vault and use a role with only the required stage/table permissions.
5. Set the four SQL statements in the runtime environment:
   - `NANOPRO_SNOWFLAKE_COPY_SQL`: idempotent load of DMS S3 landing files into L0.
   - `NANOPRO_SNOWFLAKE_L1_SQL`: idempotent L0 → L1 transformation.
   - `NANOPRO_SNOWFLAKE_L2_SQL`: idempotent L1 → L2 transformation.
   - `NANOPRO_SNOWFLAKE_REPORT_SQL`: a query for the chosen period. It may use `{report_start}`, `{report_end}`, and `{execution_date}` placeholders. Return at least one paired numeric `LIVE_*` and `T1_*` (or `T_1_*`) column; NanoPro adds computed `DIFF_*` values.

The SQL is schema-specific because the actual Oracle table mappings, S3 file format, Snowflake stage, and L0/L1/L2 definitions are account-specific. Do not paste credentials into SQL, source control, or chat. Configure secrets in Render environment variables / a secret manager and rotate any previously committed credentials.

## Verification and outputs

The daily execution records DMS state, Snowflake L0, L1, L2, report, and email stages in Task Scheduler run history. Fortnightly/monthly jobs query and email reports without re-running DMS/COPY/MERGE. Any failed stage stops subsequent stages and records a failed run. Failure notifications attempt email, Telegram, and WhatsApp Cloud API only when configured; unavailable providers are recorded as not verified.

Reports use Asia/Kolkata dates: daily covers the prior day, fortnightly covers the prior 14 days, and monthly covers the previous calendar month. The CSV includes generation, report, and execution dates, masks common PII-named columns, and computes `LIVE_* - T1_*` differences. Files below 5,000,000 bytes are attached; larger files are omitted from email and only a summary is sent.

Local tests use mocked AWS/Snowflake/email responses. They verify the orchestration contract and do not prove that cloud accounts, network routes, grants, mappings, or delivery credentials are live. A genuine cloud stage-by-stage run is required before enabling the schedules.
