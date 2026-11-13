import sys

def update_ui_view():
    path = "app/ui/global_ai_lab_view.py"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    
    old_snip = """      const data = await res.json();
      if (data.chat) {
        AILAB.chats.unshift(data.chat);
        AILAB.activeChatId = data.chat.id;
        AILAB.messages = [];
        localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats));
        ailabRenderSidebar();
        ailabRenderMessages();
        $id("ailabActiveTitle").textContent = data.chat.title;
        $id("ailabPromptInput").focus();
      }"""

    new_snip = """      const data = await res.json();
      const chatObj = data.chat || {
        id: data.chat_id || ("chat_" + Date.now()),
        title: data.title || "New AI Chat Session",
        project_id: projectId || null,
        model: AILAB.selectedModel,
        effort: AILAB.selectedEffort,
        message_count: 0,
        created_at: Date.now() / 1000
      };
      AILAB.chats.unshift(chatObj);
      AILAB.activeChatId = chatObj.id;
      AILAB.messages = [];
      localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats));
      ailabRenderSidebar();
      ailabRenderMessages();
      $id("ailabActiveTitle").textContent = chatObj.title;
      $id("ailabPromptInput").focus();"""

    if old_snip in c:
        c = c.replace(old_snip, new_snip)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Updated app/ui/global_ai_lab_view.py")
    else:
        print("[!] Snippet not found in app/ui/global_ai_lab_view.py")

def update_worker():
    path = "deploy/cloudflare_worker_gateway.js"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    old_snip = """    if (path === "/api/ai/history/chats") {
      if (request.method === "POST" || request.method === "PUT") {
        let b = {}; try { b = await request.json(); } catch (_) {}
        return new Response(JSON.stringify({
          status: "success",
          chat_id: b.id || ("chat_" + Date.now()),
          title: b.title || "New AI Chat","""

    new_snip = """    if (path === "/api/ai/history/chats") {
      if (request.method === "POST" || request.method === "PUT") {
        let b = {}; try { b = await request.json(); } catch (_) {}
        const newChatId = b.id || ("chat_" + Date.now());
        const newTitle = b.title || "New AI Chat";
        return new Response(JSON.stringify({
          status: "success",
          chat_id: newChatId,
          title: newTitle,
          chat: {
            id: newChatId,
            title: newTitle,
            project_id: b.project_id || null,
            model: b.model || "auto",
            effort: b.effort || "default",
            message_count: 0,
            created_at: Date.now() / 1000
          },"""

    if old_snip in c:
        c = c.replace(old_snip, new_snip)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print("[+] Updated deploy/cloudflare_worker_gateway.js")
    else:
        print("[!] Snippet not found in deploy/cloudflare_worker_gateway.js")

if __name__ == "__main__":
    update_ui_view()
    update_worker()
