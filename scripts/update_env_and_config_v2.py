import sys

# 1. Update .env
with open(".env", "r", encoding="utf-8") as f:
    env_content = f.read()

# Update DEEPSEEK_API_KEY
env_content = env_content.replace(
    "DEEPSEEK_API_KEY=sk-2d5bc8b3419244e6bc17f23b36dd6d66",
    "DEEPSEEK_API_KEY=sk-d633fc52cbe041e2a87372a8c2639615"
)

new_env_additions = """
# === NEW FRONTIER LABS (4,750+ MODELS) ===
ARCEE_API_KEY=rcai-c472ef2f4f2ad7362f6decf31f65c047
PARASAIL_API_KEY=psk-nano6dc5de4t-PtQ50R9kBFZAbECjwk6W
KRUTRIM_API_KEY=JcMcoC72Osu3suH8oVvy-2An4
POE_API_KEY=sk-poe-Q_PHEUPo8oUxy-FGHxCy4y2cMbtJSx5y0hprJLGDXcY
BASETEN_API_KEY_2=b10_opZ4nBmj.wzha2FItX9WeW0bgaQAlSqSXOsV2v0XY
"""

if "ARCEE_API_KEY" not in env_content:
    env_content += new_env_additions

with open(".env", "w", encoding="utf-8") as f:
    f.write(env_content)
print("Updated .env")

# 2. Update .env.example
with open(".env.example", "r", encoding="utf-8") as f:
    example_content = f.read()

example_additions = """
# === NEW FRONTIER LABS (4,750+ MODELS) ===
ARCEE_API_KEY=your_arcee_api_key_here
PARASAIL_API_KEY=your_parasail_api_key_here
KRUTRIM_API_KEY=your_krutrim_api_key_here
POE_API_KEY=your_poe_api_key_here
BASETEN_API_KEY_2=your_baseten_api_key_2_here
"""
if "ARCEE_API_KEY" not in example_content:
    example_content += example_additions

with open(".env.example", "w", encoding="utf-8") as f:
    f.write(example_content)
print("Updated .env.example")

# 3. Update app/core/config.py
with open("app/core/config.py", "r", encoding="utf-8") as f:
    cfg_content = f.read()

cfg_content = cfg_content.replace(
    'DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-2d5bc8b3419244e6bc17f23b36dd6d66").strip()',
    'DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-d633fc52cbe041e2a87372a8c2639615").strip()'
)

cfg_additions = """
# New Sovereign Frontier Labs (4,750+ Models)
ARCEE_API_KEY = os.environ.get("ARCEE_API_KEY", "rcai-c472ef2f4f2ad7362f6decf31f65c047").strip()
PARASAIL_API_KEY = os.environ.get("PARASAIL_API_KEY", "psk-nano6dc5de4t-PtQ50R9kBFZAbECjwk6W").strip()
KRUTRIM_API_KEY = os.environ.get("KRUTRIM_API_KEY", "JcMcoC72Osu3suH8oVvy-2An4").strip()
POE_API_KEY = os.environ.get("POE_API_KEY", "sk-poe-Q_PHEUPo8oUxy-FGHxCy4y2cMbtJSx5y0hprJLGDXcY").strip()
BASETEN_API_KEY_2 = os.environ.get("BASETEN_API_KEY_2", "b10_opZ4nBmj.wzha2FItX9WeW0bgaQAlSqSXOsV2v0XY").strip()
"""

if "ARCEE_API_KEY" not in cfg_content:
    cfg_content += cfg_additions

with open("app/core/config.py", "w", encoding="utf-8") as f:
    f.write(cfg_content)
print("Updated app/core/config.py")
