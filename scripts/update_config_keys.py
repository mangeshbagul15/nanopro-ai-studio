with open('app/core/config.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4").strip()'
addition = '''
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "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").strip()
FAL_AI_API_KEY = os.environ.get("FAL_AI_API_KEY", "fal_sk_d1a4032b2a4d4c94ad7cbef5395d439f:ad79f427f9e0d633316032a561ab9999").strip()
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "r8_VSW8CuVp9dP35gBcLCIFIJcNxfzVpuY3jNpQI").strip()
AIMLAPI_KEY = os.environ.get("AIMLAPI_KEY", "d6b5f7f58a5d797e02fd021c231026ea").strip()
AIMLAPI_BACKUP_KEY = os.environ.get("AIMLAPI_BACKUP_KEY", "666612ebe3ae25e4db14bd8da4b654fd").strip()'''

if target in text:
    text = text.replace(target, target + addition)
    with open('app/core/config.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated app/core/config.py!')
else:
    print('Target not found in app/core/config.py')
