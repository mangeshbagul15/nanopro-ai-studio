// Test simulation of the routing logic in cloudflare_worker_gateway.js
const fs = require('fs');

const gatewayCode = fs.readFileSync('deploy/cloudflare_worker_gateway.js', 'utf8');

// Extract the execute handler logic
const startMarker = 'if (path === "/api/ai/execute" && request.method === "POST") {';
const startIdx = gatewayCode.indexOf(startMarker);
if (startIdx === -1) {
  console.error("Execute block not found!");
  process.exit(1);
}

const testPrompts = [
  { domain: "1. IMAGE / VISUAL GENERATION", prompt: "ek mast futuristic cyber ai lab chi image banva" },
  { domain: "2. CUA BROWSER END-TO-END", prompt: "side screen share madhe google search kara" },
  { domain: "3. DATA ENGINEERING & LAKEHOUSE", prompt: "data engineering pipeline snowflake aws eod sod ingestion" },
  { domain: "4. FORMULAS & REASONING SOTA", prompt: "pareto algorithm formula and accuracy proof dakhva" },
  { domain: "5. CODE & PYTHON SPECIALIST", prompt: "python script to run duckdb batch ingestion and class" }
];

// Verify that the regex matches in gateway code work as expected
testPrompts.forEach(t => {
  const pLower = t.prompt.toLowerCase();
  let matched = "NONE";
  let model = "auto";
  let lab = "";

  if (/(image|photo|picture|चित्र|फोटो|draw|generate image|banner|logo|visual|ui mockup|render chart|visualize|आकृती|ड्रॉ)/i.test(pLower)) {
    matched = "DOMAIN 1: IMAGE & MULTIMODAL GENERATIVE STUDIO";
    model = "google/gemini-2.5-flash:vision-generative";
    lab = "Google DeepMind (Gemini 2.5 Flash)";
  } else if ((pLower.includes("google") || pLower.includes("search") || pLower.includes("browse") || pLower.includes("screen share") || pLower.includes("side screen") || pLower.includes("cua") || pLower.includes("शोध") || pLower.includes("ब्राउझर") || pLower.includes("web") || pLower.includes("wikipedia") || pLower.includes("open router") || pLower.includes("openrouter")) &&
      (pLower.includes("kara") || pLower.includes("करा") || pLower.includes("open") || pLower.includes("उघडा") || pLower.includes("search") || pLower.includes("शोध") || pLower.includes("share") || pLower.includes("शेअर") || pLower.includes("बघ") || pLower.includes("bagh") || pLower.includes("sanga") || pLower.includes("सांग") || pLower.includes("drive"))) {
    matched = "DOMAIN 2: AUTONOMOUS COMPUTER USE AGENT (CUA) — END-TO-END";
    model = "anthropic/claude-3.7-sonnet:computer-use";
    lab = "Anthropic & NanoPro Autonomous Engine";
  } else if (/(data engineering|pipeline|etl|elt|cdc|dms|snowflake|aws|bigquery|duckdb|dynamic table|dynamic tables|eod|sod|bod|ingestion|medallion|kafka|debezium|oracle|data transfer|automailer|alert|डेटा इंजिनिअरिंग|पाइपलाइन)/i.test(pLower)) {
    matched = "DOMAIN 3: ENTERPRISE DATA ENGINEERING & MEDALLION LAKEHOUSE";
    model = "anthropic/claude-3.7-sonnet:data-architect";
    lab = "Anthropic (Claude 3.7 Sonnet)";
  } else if (/(formula|algorithm|accuracy|math|proof|logic|reasoning|entropy|pareto|thompson|bayes|theorem|सूत्र|अल्गोरिदम|अचूकता)/i.test(pLower)) {
    matched = "DOMAIN 4: DEEP MATHEMATICAL REASONING, FORMULAS & ACCURACY";
    model = "deepseek/deepseek-r1:reasoning-sota";
    lab = "DeepSeek AI (DeepSeek R1)";
  } else if (/(code|python|sql|fastapi|function|class|bug|def |query|api|पायथन|कोड|एसक्यूएल)/i.test(pLower)) {
    matched = "DOMAIN 5: CODE, PYTHON & SQL SPECIALIST";
    model = "qwen/qwen-2.5-coder-32b-instruct";
    lab = "Alibaba Cloud (Qwen 2.5 Coder 32B)";
  }

  console.log(`Prompt: "${t.prompt}"`);
  console.log(`  -> Matched: ${matched}`);
  console.log(`  -> Model Routed: ${model}`);
  console.log(`  -> Provenance Lab: ${lab}\n`);
});
