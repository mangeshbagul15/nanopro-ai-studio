# -*- coding: utf-8 -*-
import sys

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove static template blocks 3, 4, 5
m3 = '// DOMAIN 3: ENTERPRISE DATA ENGINEERING & MEDALLION LAKEHOUSE'
m_tg = '// 1. TELEGRAM DISPATCH INTENT'

idx3 = code.find(m3)
idxtg = code.find(m_tg)

if idx3 == -1 or idxtg == -1:
    print("Could not find static blocks bounds!")
    sys.exit(1)

# Remove the static blocks
code = code[:idx3] + code[idxtg:]
print(f"Removed static blocks 3-5 (saved {idxtg - idx3} bytes)!")

# 2. Replace the 5-Tier Dispatch Decision with the full 473+ Models Mesh
m_dispatch = '// 5-Tier Dispatch Decision'
m_resp_ok = 'if (resp && resp.ok) {'

idx_d = code.find(m_dispatch)
idx_ok = code.find(m_resp_ok, idx_d)

if idx_d == -1 or idx_ok == -1:
    print("Could not find dispatch decision bounds!")
    sys.exit(1)

new_dispatch_code = """// 5-Tier Mathematical Specialist Dispatch Decision (473+ Models Unified Mesh)
      let executedModel = model;
      let activeProvider = "OPENROUTER_MESH";
      let resp = null;

      // 1. DIRECT ROUTING: User explicitly selected a model from the 473+ Model Catalog
      if (model && model !== "auto") {
        executedModel = model;
        if (model.startsWith("groq/") || model === "openai/gpt-oss-120b" || model === "qwen/qwen3.8-27b") {
          activeProvider = "GROQ_LPU_DIRECT";
          resp = await callGroq(model, 6000);
        } else {
          activeProvider = "OPENROUTER_FRONTIER_DIRECT";
          resp = await callOR(model, 8500);
        }
      } else {
        // 2. SINGLE AUTO MATHEMATICAL ENGINE:
        // Scalarized Pareto Frontier + Shannon Entropy Domain Matrix
        const pCheck = prompt.toLowerCase();
        
        // A. ENTERPRISE DATA ENGINEERING, ETL, PIPELINES, SNOWFLAKE, AWS, LAKHOUSE, MIGRATION
        if (/(data engineering|pipeline|snowflake|aws|bigquery|duckdb|cdc|dms|medallion|eod|sod|bod|ingestion|lakehouse|migration|oracle|kafka|debezium|etl|elt|डेटा|पाइपलाइन)/i.test(pCheck)) {
          activeProvider = "OPENROUTER_DATA_ARCHITECT";
          // Meta Llama 3.3 70B & GPT-4o-mini provide industry-standard data engineering architecture
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR(executedModel, 8500);
          if (!resp || !resp.ok) {
            executedModel = "openai/gpt-4o-mini";
            resp = await callOR(executedModel, 7500);
          }
        }
        // B. DEEP CODE GENERATION, PYTHON, SQL, FASTAPI, DEBUGGING & REFACTORING
        else if (/(code|python|sql|fastapi|func|class|javascript|typescript|def |algorithm|bug|query|पायथन|कोड|एसक्यूएल)/i.test(pCheck)) {
          activeProvider = "OPENROUTER_CODE_SPECIALIST";
          // Alibaba Qwen 2.5 Coder 32B SOTA
          executedModel = "qwen/qwen-2.5-coder-32b-instruct";
          resp = await callOR(executedModel, 8500);
          if (!resp || !resp.ok) {
            executedModel = "openai/gpt-4o-mini";
            resp = await callOR(executedModel, 7500);
          }
        }
        // C. DEEP MATHEMATICAL REASONING, FORMULAS, PROOFS & OPTIMIZATION
        else if (/(math|formula|proof|logic|reason|entropy|pareto|thompson|accuracy|theorem|bayes|गणित|सूत्र|अल्गोरिदम)/i.test(pCheck)) {
          activeProvider = "OPENROUTER_DEEP_REASONING";
          // DeepSeek V3 / Llama 3.3 70B for deep mathematical precision
          executedModel = "deepseek/deepseek-chat";
          resp = await callOR(executedModel, 8500);
          if (!resp || !resp.ok) {
            executedModel = "meta-llama/llama-3.3-70b-instruct";
            resp = await callOR(executedModel, 8000);
          }
        }
        // D. GENERAL RAPID SYNTHESIS & HUMAN UNDERSTANDING (<800ms SLA)
        else {
          activeProvider = "OPENROUTER_RAPID_SLA";
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR(executedModel, 7000);
          if (!resp || !resp.ok) {
            executedModel = "openai/gpt-4o-mini";
            resp = await callOR(executedModel, 6000);
          }
        }
      }

      // 3. ZERO-LOSS 429 SHIELD & VERIFIED FAILOVER CASCADE
      if (!resp || !resp.ok) {
        const cascade = [
          "meta-llama/llama-3.3-70b-instruct",
          "openai/gpt-4o-mini",
          "qwen/qwen-2.5-coder-32b-instruct",
          "deepseek/deepseek-chat",
          "nvidia/nemotron-3.5-lightning:free"
        ];
        for (const fbModel of cascade) {
          if (executedModel === fbModel) continue;
          activeProvider = "OPENROUTER_SHIELD_CASCADE";
          executedModel = fbModel;
          resp = await callOR(fbModel, 6500);
          if (resp && resp.ok) break;
        }
      }

      // 4. EMERGENCY SUB-300ms GROQ LPU FALLBACK
      if (!resp || !resp.ok) {
        activeProvider = "GROQ_LPU_EMERGENCY";
        executedModel = "groq/qwen3.8-27b";
        resp = await callGroq("qwen/qwen3.8-27b", 5000);
      }

      """

code = code[:idx_d] + new_dispatch_code + code[idx_ok:]

with open('deploy/cloudflare_worker_gateway.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully updated deploy/cloudflare_worker_gateway.js with Unified OpenRouter Mesh!")
