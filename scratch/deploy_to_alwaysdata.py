import paramiko
import os
from pathlib import Path

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting to Alwaysdata SSH...")
client.connect('ssh-mangeshbagul15.alwaysdata.net', port=22, username='mangeshbagul15', password='Divyam@123', timeout=15)
print("Connected!")

sftp = client.open_sftp()

files_to_upload = [
    (Path("deploy/alwaysdata_wsgi.py"), "alwaysdata_wsgi.py"),
    (Path("deploy/cloud_studio.html"), "cloud_studio.html"),
    (Path("deploy/complete_nanopro_dashboard.html"), "complete_nanopro_dashboard.html"),
    (Path("deploy/login_gateway.html"), "login_gateway.html")
]

for local_path, remote_name in files_to_upload:
    if local_path.exists():
        size_mb = local_path.stat().st_size / (1024 * 1024)
        print(f"Uploading {local_path} ({size_mb:.2f} MB) to {remote_name}...")
        sftp.put(str(local_path), remote_name)
        print(f"-> {remote_name} uploaded successfully!")
    else:
        print(f"Warning: {local_path} not found!")

sftp.close()

sync_cmd = """
cp /home/mangeshbagul15/alwaysdata_wsgi.py /home/mangeshbagul15/home/mangeshbagul15/alwaysdata_wsgi.py
cp /home/mangeshbagul15/cloud_studio.html /home/mangeshbagul15/home/mangeshbagul15/cloud_studio.html
cp /home/mangeshbagul15/complete_nanopro_dashboard.html /home/mangeshbagul15/home/mangeshbagul15/complete_nanopro_dashboard.html
cp /home/mangeshbagul15/login_gateway.html /home/mangeshbagul15/home/mangeshbagul15/login_gateway.html
killall -HUP uwsgi || true
ls -lh /home/mangeshbagul15/alwaysdata_wsgi.py /home/mangeshbagul15/cloud_studio.html /home/mangeshbagul15/complete_nanopro_dashboard.html
"""
stdin, stdout, stderr = client.exec_command(sync_cmd)
print("Remote status:")
print(stdout.read().decode())

client.close()
print("Alwaysdata upload and sync complete!")
