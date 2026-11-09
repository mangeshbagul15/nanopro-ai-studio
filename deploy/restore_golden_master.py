"""
NanoPro AI Studio - Golden Master Authentication Gateway Restore Sentinel
==========================================================================
Autonomous recovery tool for NanoPro Manager & Sentinel Workers.
Restores the verified golden baseline of login_gateway.html, alwaysdata_wsgi.py,
auth_manager.py, and cloudflare_worker_gateway.js whenever regressions occur.

Usage:
    python deploy/restore_golden_master.py [--dry-run] [--no-sync]
"""

import os
import sys
import json
import shutil
import hashlib
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def calculate_sha256(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def restore_golden_master(sync_cloud: bool = True, dry_run: bool = False) -> dict:
    # The 2026-11-02 snapshot predates the auth hardening work and still contains
    # master-password / hardcoded-OTP backdoors. Restoring it would reintroduce them.
    return {
        "status": "error",
        "error": "Golden master restore is disabled: the snapshot contains pre-hardening auth backdoors. Use git history for rollback instead."
    }

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    golden_dir = os.path.join(base_dir, 'deploy', 'golden_master')
    manifest_path = os.path.join(golden_dir, 'golden_master_manifest.json')

    if not os.path.exists(manifest_path):
        return {"status": "error", "error": f"Manifest not found at {manifest_path}"}

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print(f"=== Restoring {manifest.get('snapshot_name', 'Golden Master')} ===")
    print(f"Verified Snapshot Date: {manifest.get('created_at_ist')}")

    restored_files = []
    for target_rel, info in manifest.get('components', {}).items():
        src_path = os.path.join(base_dir, info['backup_file'])
        dst_path = os.path.join(base_dir, target_rel)

        if not os.path.exists(src_path):
            print(f"Error: Golden backup source {src_path} is missing!")
            continue

        # Verify backup integrity
        current_hash = calculate_sha256(src_path)
        if current_hash != info['sha256']:
            print(f"Warning: Hash mismatch on golden master {src_path}!")

        if not dry_run:
            shutil.copy2(src_path, dst_path)
            print(f"-> Restored {target_rel} from {os.path.basename(src_path)}")
        else:
            print(f"[DRY-RUN] Would restore {target_rel} from {os.path.basename(src_path)}")

        restored_files.append(target_rel)

    # Autonomous Cloud Sync to Alwaysdata
    cloud_synced = False
    if sync_cloud and not dry_run:
        try:
            import paramiko
            print("\nConnecting to Alwaysdata to deploy golden master...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_user = os.environ.get("ALWAYSDATA_SSH_USER", "mangeshbagul15")
            ssh_password = os.environ.get("ALWAYSDATA_SSH_PASSWORD", "")
            if not ssh_password:
                raise RuntimeError("ALWAYSDATA_SSH_PASSWORD is not set")
            client.connect('ssh-mangeshbagul15.alwaysdata.net', port=22, username=ssh_user, password=ssh_password, timeout=15)

            sftp = client.open_sftp()
            sftp.put(os.path.join(base_dir, 'deploy', 'login_gateway.html'), 'login_gateway.html')
            sftp.put(os.path.join(base_dir, 'deploy', 'alwaysdata_wsgi.py'), 'alwaysdata_wsgi.py')
            sftp.close()

            sync_cmd = """
            cp /home/mangeshbagul15/login_gateway.html /home/mangeshbagul15/home/mangeshbagul15/login_gateway.html
            cp /home/mangeshbagul15/alwaysdata_wsgi.py /home/mangeshbagul15/home/mangeshbagul15/alwaysdata_wsgi.py
            touch /home/mangeshbagul15/alwaysdata_wsgi.py
            """
            client.exec_command(sync_cmd)
            client.close()
            cloud_synced = True
            print("Alwaysdata cloud sync successful!")
        except Exception as ex:
            print(f"Warning: Cloud sync skipped/failed: {ex}")

    # Log recovery state
    try:
        state_file = os.path.join(base_dir, 'data', 'autonomous_sentinel_state.json')
        state = {}
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
        state['last_golden_master_restoration'] = {
            'timestamp': time.time(),
            'date_ist': time.strftime('%Y-%m-%d %H:%M:%S IST', time.localtime()),
            'restored_files': restored_files,
            'cloud_synced': cloud_synced
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

    print("\n[SUCCESS] NanoPro Golden Master Reset & Restoration Complete!")
    return {
        "status": "success",
        "restored_files": restored_files,
        "cloud_synced": cloud_synced,
        "timestamp": time.time()
    }

if __name__ == '__main__':
    args = sys.argv[1:]
    is_dry = '--dry-run' in args
    no_sync = '--no-sync' in args
    res = restore_golden_master(sync_cloud=(not no_sync), dry_run=is_dry)
    sys.exit(0 if res.get('status') == 'success' else 1)
