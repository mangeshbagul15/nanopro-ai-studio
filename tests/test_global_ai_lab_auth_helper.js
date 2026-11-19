const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const repoRoot = path.resolve(__dirname, "..");
const source = fs.readFileSync(
  path.join(repoRoot, "app", "ui", "global_ai_lab_view.py"),
  "utf8"
);
const helperStart = source.indexOf("window.ailabAuthFetch = function");
const helperEnd = source.indexOf("// The live catalog", helperStart);
assert.ok(helperStart >= 0 && helperEnd > helperStart, "Auth helper must be present");
const helperSource = source.slice(helperStart, helperEnd);

function createContext(token) {
  const calls = [];
  const context = {
    window: {
      location: {
        href: "https://nano.example/global_ai_lab",
        origin: "https://nano.example",
      },
    },
    localStorage: {
      getItem(key) {
        assert.equal(key, "nanopro_session_token");
        return token;
      },
    },
    Headers,
    URL,
    fetch: async (url, options) => {
      calls.push({ url, options });
      return { ok: true };
    },
  };
  vm.runInNewContext(helperSource, context);
  return { context, calls };
}

test("adds NanoPro session token to same-origin API requests", async () => {
  const { context, calls } = createContext("session-123");
  await context.window.ailabAuthFetch("/api/banking/orchestrator/overview", {
    headers: { Accept: "application/json" },
  });

  assert.equal(calls.length, 1);
  assert.equal(calls[0].options.headers.get("X-Session-Token"), "session-123");
  assert.equal(calls[0].options.headers.get("Accept"), "application/json");
  assert.equal(calls[0].options.credentials, "same-origin");
});

test("does not forward the session token to another origin", async () => {
  const { context, calls } = createContext("session-123");
  await context.window.ailabAuthFetch("https://other.example/api", {});

  assert.equal(calls[0].options.headers.has("X-Session-Token"), false);
});
