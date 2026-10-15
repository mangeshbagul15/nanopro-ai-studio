import os
import zipfile
import sys
import time

src_dir = r"C:\Mangesh\AI video\NanoPro_Made_By_Mangesh_Bagul_AI_v1\Mangesh_Nano_Pro_AI_Studio_v7_FINAL_PRODUCTION"
out_zip = r"C:\Mangesh\AI video\NanoPro_Made_By_Mangesh_Bagul_AI_v1\Mangesh_Nano_Pro_AI_Studio_v7_FINAL_PRODUCTION.zip"

print(f"Starting ZIP generation from: {src_dir}")
t0 = time.time()

exclude_dirs = {"__pycache__", ".git", ".venv", "venv", ".idea", ".vscode", "tmp"}
exclude_extensions = {".pyc", ".pyo"}

count = 0
with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(src_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in exclude_extensions:
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, src_dir)
            z.write(full_path, rel_path)
            count += 1
            if count % 50 == 0:
                print(f"  Zipped {count} files...")

elapsed = time.time() - t0
size_mb = os.path.getsize(out_zip) / (1024 * 1024)
print(f"SUCCESS: Zipped {count} files into {out_zip}")
print(f"Size: {size_mb:.2f} MB | Elapsed: {elapsed:.2f}s")
