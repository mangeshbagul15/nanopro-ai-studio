const fs = require('fs');

// Read the gateway script
const code = fs.readFileSync('deploy/cloudflare_worker_gateway.js', 'utf8');

console.log("Checking syntax of deploy/cloudflare_worker_gateway.js...");
try {
  // Check JS syntax with Function constructor or node syntax check
  require('child_process').execSync('node --check deploy/cloudflare_worker_gateway.js');
  console.log("Syntax check PASSED: deploy/cloudflare_worker_gateway.js is 100% valid JavaScript!");
} catch (e) {
  console.error("Syntax error:", e.message);
  process.exit(1);
}
