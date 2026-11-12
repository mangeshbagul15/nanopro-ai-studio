with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = 'if (path === "/api/ai/execute" && request.method === "POST") {'
start_idx = text.find(start_marker)
end_marker = 'if (path === "/api/approvals/list") {'
end_idx = text.find(end_marker, start_idx)

print(f"Execute block from {start_idx} to {end_idx} (Length: {end_idx - start_idx})")
print("\nFirst 400 chars:")
print(text[start_idx:start_idx+400].encode('ascii', 'backslashreplace').decode('ascii'))
print("\nLast 400 chars:")
print(text[end_idx-400:end_idx].encode('ascii', 'backslashreplace').decode('ascii'))
