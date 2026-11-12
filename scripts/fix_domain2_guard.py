with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_cond = """      if ((pLower.includes("google") || pLower.includes("search") || pLower.includes("browse") || pLower.includes("screen share") || pLower.includes("side screen") || pLower.includes("cua") || pLower.includes("शोध") || pLower.includes("ब्राउझर") || pLower.includes("web") || pLower.includes("wikipedia") || pLower.includes("open router") || pLower.includes("openrouter")) &&
          (pLower.includes("kara") || pLower.includes("करा") || pLower.includes("open") || pLower.includes("उघडा") || pLower.includes("search") || pLower.includes("शोध") || pLower.includes("share") || pLower.includes("शेअर") || pLower.includes("बघ") || pLower.includes("bagh") || pLower.includes("sanga") || pLower.includes("सांग") || pLower.includes("drive"))) {"""

new_cond = """      const isExplicitCodeTask = /(\\bdef\\b|\\bclass\\b|\\bpython\\b|\\bfastapi\\b|\\bscript\\b|\\bfunction\\b|\\bdebug\\b|\\bbug\\b|पायथन|कोड)/i.test(pLower);
      if (!isExplicitCodeTask &&
          ((pLower.includes("google") || /\\bsearch\\b/.test(pLower) || pLower.includes("browse") || pLower.includes("screen share") || pLower.includes("side screen") || pLower.includes("cua") || pLower.includes("शोध") || pLower.includes("ब्राउझर") || pLower.includes("web") || pLower.includes("wikipedia") || pLower.includes("open router") || pLower.includes("openrouter")) &&
          (pLower.includes("kara") || pLower.includes("करा") || pLower.includes("open") || pLower.includes("उघडा") || /\\bsearch\\b/.test(pLower) || pLower.includes("शोध") || pLower.includes("share") || pLower.includes("शेअर") || pLower.includes("बघ") || pLower.includes("bagh") || pLower.includes("sanga") || pLower.includes("सांग") || pLower.includes("drive")))) {"""

if old_cond in text:
    text = text.replace(old_cond, new_cond)
    with open('deploy/cloudflare_worker_gateway.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated Domain 2 guard in deploy/cloudflare_worker_gateway.js!")
else:
    print("Could not find old_cond in deploy/cloudflare_worker_gateway.js")
    exit(1)
