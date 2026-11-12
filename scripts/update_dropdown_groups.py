import sys

with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

target_block = """      const select = $id("ailabModelSelect");
      if (!select) return;

      const currentVal = AILAB.selectedModel || select.value || "auto";

      const groups = {
        free: [],
        usa: [],
        china: [],
        europe: [],
        india: [],
        global: []
      };

      const models = data.models || [];
      if (models.length > 0) {
        models.forEach(m => {
          if (!m.id || m.id === "auto") return;
          const prov = ailabResolveModelProvenance(m.id);
          const isFree = m.is_free || m.id.includes(":free");
          const displayName = `${prov.flag} ${m.name || prov.clean_name} (${prov.lab_name})`;

          const item = { id: m.id, name: displayName };

          if (isFree) {
            groups.free.push(item);
          } else if (prov.country === "United States" || prov.country === "USA") {
            groups.usa.push(item);
          } else if (prov.country === "China") {
            groups.china.push(item);
          } else if (prov.country === "France" || prov.country === "Germany" || prov.country.includes("Europe")) {
            groups.europe.push(item);
          } else if (prov.country === "India") {
            groups.india.push(item);
          } else {
            groups.global.push(item);
          }
        });

        select.innerHTML = `
          <optgroup label="⚡ High-Tech Mathematical Router">
            <option value="auto">⚡ AUTO Router (Pareto &lt;800ms)</option>
          </optgroup>
          ${groups.free.length > 0 ? `
            <optgroup label="🆓 Unlimited Free Frontier Models (${groups.free.length} Models)">
              ${groups.free.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}
            </optgroup>
          ` : ""}
          ${groups.usa.length > 0 ? `
            <optgroup label="🇺🇸 United States Labs (${groups.usa.length} Models · OpenAI, Anthropic, Google, Meta, xAI, NVIDIA)">
              ${groups.usa.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}
            </optgroup>
          ` : ""}
          ${groups.china.length > 0 ? `
            <optgroup label="🇨🇳 China Frontier Labs (${groups.china.length} Models · DeepSeek, Alibaba Qwen, Moonshot, Baidu)">
              ${groups.china.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}
            </optgroup>
          ` : ""}
          ${groups.europe.length > 0 ? `
            <optgroup label="🇫🇷 Europe Sovereign Labs (${groups.europe.length} Models · Mistral AI, Aleph Alpha)">
              ${groups.europe.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}
            </optgroup>
          ` : ""}
          ${groups.india.length > 0 ? `
            <optgroup label="🇮🇳 India Sovereign Labs (${groups.india.length} Models · Sarvam AI, Krutrim, BharatGen)">
              ${groups.india.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}
            </optgroup>
          ` : ""}
          ${groups.global.length > 0 ? `
            <optgroup label="🌍 Global & Asia Labs (${groups.global.length} Models · UAE Falcon, Sakana Japan, Upstage Korea)">
              ${groups.global.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}
            </optgroup>
          ` : ""}
        `;

        select.value = currentVal;
      }"""

replacement_block = """      const select = $id("ailabModelSelect");
      if (!select) return;

      const currentVal = AILAB.selectedModel || select.value || "auto";

      const groups = {
        krutrim: [],
        poe: [],
        edenai: [],
        requesty: [],
        nvidia: [],
        sambanova: [],
        parasail: [],
        arcee: [],
        cloudflare: [],
        novita: [],
        deepinfra: [],
        mistral: [],
        deepseek: [],
        groq: [],
        hf: [],
        frontier: [],
        free: [],
        other: []
      };

      const models = data.models || [];
      if (models.length > 0) {
        models.forEach(m => {
          if (!m.id || m.id === "auto") return;
          const prov = ailabResolveModelProvenance(m.id);
          const isFree = m.is_free || m.id.includes(":free");
          const displayName = `${prov.flag} ${m.name || prov.clean_name} (${prov.lab_name})`;
          const item = { id: m.id, name: displayName };
          const pfx = (m.id.split("/")[0] || "").toLowerCase();

          if (pfx === "krutrim" || pfx === "ola") {
            groups.krutrim.push(item);
          } else if (pfx === "poe") {
            groups.poe.push(item);
          } else if (pfx === "edenai") {
            groups.edenai.push(item);
          } else if (pfx === "requesty") {
            groups.requesty.push(item);
          } else if (pfx === "nvidia") {
            groups.nvidia.push(item);
          } else if (pfx === "sambanova") {
            groups.sambanova.push(item);
          } else if (pfx === "parasail") {
            groups.parasail.push(item);
          } else if (pfx === "arcee") {
            groups.arcee.push(item);
          } else if (pfx === "cf" || pfx === "@cf") {
            groups.cloudflare.push(item);
          } else if (pfx === "novita") {
            groups.novita.push(item);
          } else if (pfx === "deepinfra") {
            groups.deepinfra.push(item);
          } else if (pfx === "mistral" || pfx === "mistralai") {
            groups.mistral.push(item);
          } else if (pfx === "deepseek") {
            groups.deepseek.push(item);
          } else if (pfx === "groq") {
            groups.groq.push(item);
          } else if (pfx === "hf" || pfx === "huggingface") {
            groups.hf.push(item);
          } else if (["anthropic", "google", "openai", "meta", "meta-llama"].includes(pfx)) {
            groups.frontier.push(item);
          } else if (isFree) {
            groups.free.push(item);
          } else {
            groups.other.push(item);
          }
        });

        const optHtml = [
          `<optgroup label="⚡ High-Tech Mathematical Router"><option value="auto">⚡ AUTO Router (Pareto &lt;800ms)</option></optgroup>`,
          groups.krutrim.length ? `<optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · ${groups.krutrim.length} Models)">${groups.krutrim.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.poe.length ? `<optgroup label="⚡ Poe by Quora (${groups.poe.length} Unified Bot Models)">${groups.poe.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.edenai.length ? `<optgroup label="🌿 Eden AI (${groups.edenai.length} Unified Models · OpenAI, Anthropic, Gemini, Mistral)">${groups.edenai.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.requesty.length ? `<optgroup label="🌐 Requesty AI (${groups.requesty.length} Global Unified Models)">${groups.requesty.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.nvidia.length ? `<optgroup label="🟢 NVIDIA NIM Microservices (${groups.nvidia.length} Models · TensorRT-LLM)">${groups.nvidia.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.sambanova.length ? `<optgroup label="⚡ SambaNova Systems (${groups.sambanova.length} Fast SN40L RDUs)">${groups.sambanova.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.parasail.length ? `<optgroup label="⛵ Parasail GPU Network (${groups.parasail.length} Decentralized Models)">${groups.parasail.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.arcee.length ? `<optgroup label="🏹 Arcee AI (${groups.arcee.length} Domain-Specialized SLMs)">${groups.arcee.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.cloudflare.length ? `<optgroup label="☁️ Cloudflare Workers AI (${groups.cloudflare.length} Edge Models)">${groups.cloudflare.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.novita.length ? `<optgroup label="🚀 Novita AI Multi-Cloud (${groups.novita.length} Models)">${groups.novita.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.deepinfra.length ? `<optgroup label="🧠 DeepInfra High-Throughput (${groups.deepinfra.length} Models)">${groups.deepinfra.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.mistral.length ? `<optgroup label="🇫🇷 Mistral AI Direct (${groups.mistral.length} Models)">${groups.mistral.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.deepseek.length ? `<optgroup label="🇨🇳 DeepSeek Sovereign Direct (${groups.deepseek.length} Models)">${groups.deepseek.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.groq.length ? `<optgroup label="⚡ Groq Ultra-Fast LPUs (${groups.groq.length} Models &lt;300ms SLA)">${groups.groq.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.hf.length ? `<optgroup label="🤗 Hugging Face Serverless Hub (${groups.hf.length} Models)">${groups.hf.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.frontier.length ? `<optgroup label="🇺🇸 Frontier Flagships (${groups.frontier.length} Models · Anthropic, Google, OpenAI, Meta)">${groups.frontier.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.free.length ? `<optgroup label="🆓 Unlimited Free Frontier Models (${groups.free.length} Models)">${groups.free.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.other.length ? `<optgroup label="🌍 Global & Asia Labs (${groups.other.length} Models)">${groups.other.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : ""
        ].filter(Boolean).join("");

        select.innerHTML = optHtml;

        // Ensure currentVal is still selectable even if from large catalog
        if (currentVal && currentVal !== "auto") {
          let opt = Array.from(select.options).find(o => o.value === currentVal);
          if (!opt) {
            const prov = ailabResolveModelProvenance(currentVal);
            opt = document.createElement("option");
            opt.value = currentVal;
            opt.textContent = `${prov.flag} ${prov.clean_name || currentVal} (${prov.lab_name})`;
            select.appendChild(opt);
          }
        }
        select.value = currentVal;
      }"""

if target_block in text:
    text = text.replace(target_block, replacement_block)
    with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESS: Updated dropdown dynamic grouping to match all 19 sovereign provider groups!")
else:
    print("ERROR: target_block not found in app/ui/global_ai_lab_view.py")
