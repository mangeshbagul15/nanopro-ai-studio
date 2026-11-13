"""Mount banking_orchestrator_routes in main.py."""
path = 'main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'app.include_router(ai_command_router)'
addition = '''app.include_router(ai_command_router)

from app.api.banking_orchestrator_routes import router as banking_orchestrator_router
app.include_router(banking_orchestrator_router)'''

if 'banking_orchestrator_router' in content:
    print("Already mounted.")
elif target in content:
    content = content.replace(target, addition, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Mounted banking_orchestrator_routes in main.py")
else:
    print("FAILED: Target not found.")
