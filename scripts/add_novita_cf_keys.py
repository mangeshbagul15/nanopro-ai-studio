import os

# 1. Update .env
novita_key = "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E"
cf_token = "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a"
cf_account_id = "ccd6c0bc1765868497170623a66e6ec1"

with open('.env', 'r', encoding='utf-8') as f:
    env_content = f.read()

if "NOVITA_AI_KEY" not in env_content:
    env_content += f"\nNOVITA_AI_KEY = {novita_key}\nCLOUDFLARE_AI_TOKEN = {cf_token}\nCLOUDFLARE_ACCOUNT_ID = {cf_account_id}\n"
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("Updated .env successfully!")

# 2. Update .env.example
with open('.env.example', 'r', encoding='utf-8') as f:
    ex_content = f.read()

if "NOVITA_AI_KEY" not in ex_content:
    ex_content += "\nNOVITA_AI_KEY=your_novita_api_key_here\nCLOUDFLARE_AI_TOKEN=your_cloudflare_ai_token_here\nCLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id_here\n"
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(ex_content)
    print("Updated .env.example successfully!")

# 3. Update app/core/config.py
with open('app/core/config.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

if "NOVITA_AI_KEY" not in cfg:
    cfg = cfg.replace(
        'AIMLAPI_BACKUP_KEY: str = os.getenv("AIMLAPI_BACKUP_KEY", "")',
        'AIMLAPI_BACKUP_KEY: str = os.getenv("AIMLAPI_BACKUP_KEY", "")\n    NOVITA_AI_KEY: str = os.getenv("NOVITA_AI_KEY", "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E")\n    CLOUDFLARE_AI_TOKEN: str = os.getenv("CLOUDFLARE_AI_TOKEN", "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a")\n    CLOUDFLARE_ACCOUNT_ID: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "ccd6c0bc1765868497170623a66e6ec1")'
    )
    with open('app/core/config.py', 'w', encoding='utf-8') as f:
        f.write(cfg)
    print("Updated app/core/config.py successfully!")
