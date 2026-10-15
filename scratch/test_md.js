function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function createCodeBlockHtml(lang, code, blockId) {
    const safeCode = escapeHtml(code);
    return `<div class="code-block-wrapper" id="${blockId}"><div class="code-header"><span style="font-weight:700; text-transform:uppercase;">${lang}</span><button type="button" class="copy-btn" onclick="copyCodeBlock('${blockId}')">&#128203; Copy Code</button></div><pre class="code-content"><code>${safeCode}</code></pre></div>`;
}

function formatMarkdownChat(text) {
    if (!text) return '';

    const codeBlocks = [];
    const inlineCodes = [];
    const tables = [];

    // 1. Extract multi-line fenced code blocks ```lang ... ```
    let processed = text.replace(/```([a-zA-Z0-9_\-\+]*)\r?\n([\s\S]*?)```/g, (match, lang, code) => {
        const id = 'cb_' + Math.random().toString(36).substring(2, 9);
        const placeholder = `@@@CODEBLOCK_${codeBlocks.length}@@@`;
        const codeLang = lang ? lang.trim() : 'SQL / CODE';
        codeBlocks.push(createCodeBlockHtml(codeLang, code.trim(), id));
        return placeholder;
    });

    // 2. Extract inline code `...`
    processed = processed.replace(/`([^`\r\n]+)`/g, (match, code) => {
        const placeholder = `@@@INLINECODE_${inlineCodes.length}@@@`;
        inlineCodes.push(`<code style="background:#1E293B; color:#38BDF8; padding:2px 6px; border-radius:4px; font-family:monospace; font-size:11.5px;">${escapeHtml(code)}</code>`);
        return placeholder;
    });

    // 3. Extract and parse markdown tables
    processed = processed.replace(/(?:^|\n)((?:\|[^\r\n]+\|\r?\n?){3,})/g, (match, tableText) => {
        const lines = tableText.trim().split(/\r?\n/).filter(l => l.trim().startsWith('|'));
        if (lines.length >= 2) {
            const isSep = /^\|(?:\s*[:-]+[-| :]*)\|$/.test(lines[1].trim());
            if (!isSep && lines.length < 3) return match;

            const parseRow = (line) => {
                const parts = line.split('|');
                if (parts.length > 2) {
                    return parts.slice(1, -1).map(p => p.trim());
                }
                return parts.map(p => p.trim());
            };

            const headerCells = parseRow(lines[0]);
            const headerHtml = headerCells.map(h => `<th style="padding:7px 12px; text-align:left; color:#38BDF8; font-weight:700; border-bottom:1px solid #1E2D4A; white-space:nowrap;">${escapeHtml(h)}</th>`).join('');

            const startIdx = isSep ? 2 : 1;
            let bodyHtml = '';
            for (let i = startIdx; i < lines.length; i++) {
                if (!lines[i].trim()) continue;
                const rowCells = parseRow(lines[i]);
                const rowHtml = rowCells.map(c => `<td style="padding:6px 12px; color:#E2E8F0; border-bottom:1px solid rgba(30,45,74,0.4); white-space:nowrap;">${escapeHtml(c)}</td>`).join('');
                bodyHtml += `<tr style="transition:background 0.15s;" onmouseover="this.style.background='rgba(56,189,248,0.06)'" onmouseout="this.style.background='transparent'">${rowHtml}</tr>`;
            }

            const tableHtml = `<div style="overflow-x:auto; margin:10px 0; border:1px solid #1E2D4A; border-radius:6px; background:#0B132B;"><table style="width:100%; border-collapse:collapse; font-size:11.5px; font-family:monospace;"><thead><tr style="background:#15223E;">${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`;
            const placeholder = `@@@TABLE_${tables.length}@@@`;
            tables.push(tableHtml);
            return '\n' + placeholder + '\n';
        }
        return match;
    });

    // 4. Escape remaining HTML entities for safety
    let html = escapeHtml(processed);

    // 5. Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 6. Italic *text* (Never match underscores inside identifier names like BANK_DB)
    html = html.replace(/(^|[^\*])\*([^\*\n]+)\*([^\*]|$)/g, '$1<em>$2</em>$3');

    // Safe underscore italic only if isolated with whitespace: e.g. " _italic note_ "
    html = html.replace(/(^|\s)_([a-zA-Z0-9\s]{1,60})_(\s|[.,!?;]|$)/g, '$1<em>$2</em>$3');

    // 7. Headings
    html = html.replace(/^### (.*$)/gim, '<h3 style="color:#38BDF8; font-size:13px; margin:10px 0 4px 0; font-weight:700;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="color:#F8FAFC; font-size:14px; margin:12px 0 6px 0; font-weight:800;">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 style="color:#38BDF8; font-size:15px; margin:14px 0 6px 0; font-weight:800;">$1</h1>');

    // 8. Bullet points and lists
    html = html.replace(/^\s*[•\-\*]\s+(.*$)/gim, '<div style="padding-left:14px; margin:3px 0;">&bull; $1</div>');
    html = html.replace(/^\s*(\d+)\.\s+(.*$)/gim, '<div style="padding-left:14px; margin:3px 0;"><strong style="color:#38BDF8;">$1.</strong> $2</div>');

    // 9. Restore placeholders in reverse order
    tables.forEach((t, i) => {
        html = html.replace(`@@@TABLE_${i}@@@`, t);
    });

    inlineCodes.forEach((ic, i) => {
        html = html.replace(`@@@INLINECODE_${i}@@@`, ic);
    });

    codeBlocks.forEach((cb, i) => {
        html = html.replace(`@@@CODEBLOCK_${i}@@@`, cb);
    });

    // 10. Line breaks (preserve existing tags, replace plain \n)
    html = html.replace(/\r?\n/g, '<br>');
    // Clean up excessive <br> before or after block elements
    html = html.replace(/(?:<br>\s*)+(<(?:div|table|pre|h1|h2|h3)[^>]*>)/gi, '$1');
    html = html.replace(/(<\/(?:div|table|pre|h1|h2|h3)>)(?:\s*<br>)+/gi, '$1');

    return html;
}

// TEST CASES
const testCases = [
    {
        name: "Snowflake query with BANK_DB.L0_STAGING.ACCOUNTS",
        input: `### ❄️ Snowflake SQL Query:\n\`\`\`sql\nSELECT * FROM BANK_DB.L0_STAGING.ACCOUNTS LIMIT 5;\n\`\`\``,
        expected: ["BANK_DB.L0_STAGING.ACCOUNTS", "code-block-wrapper", "SELECT * FROM BANK_DB.L0_STAGING.ACCOUNTS LIMIT 5;"],
        forbidden: ["<em>DB", "BANKDB.L0STAGING"]
    },
    {
        name: "Inline code with BANK_DB",
        input: `Check table \`ACCOUNTS\` in \`BANK_DB.L0_STAGING\``,
        expected: ["<code", "BANK_DB.L0_STAGING", "ACCOUNTS"],
        forbidden: ["<em>DB", "BANKDB"]
    },
    {
        name: "Table preview with column names containing underscores",
        input: `| ACCOUNT_ID | CUSTOMER_ID | ACCOUNT_NUMBER | STATUS |\n|---|---|---|---|\n| 101 | 1001 | ACC1001CORP | ACTIVE |`,
        expected: ["<table", "ACCOUNT_ID", "CUSTOMER_ID", "ACCOUNT_NUMBER", "ACC1001CORP"],
        forbidden: ["ACCOUNTID", "CUSTOMERID", "ACCOUNTNUMBER"]
    },
    {
        name: "Plain text with multiple underscored identifiers",
        input: `We connect to BANK_DB and schema L0_STAGING then query MY_ORACLE_XE_LOCAL.`,
        expected: ["BANK_DB", "L0_STAGING", "MY_ORACLE_XE_LOCAL"],
        forbidden: ["<em>DB", "BANKDB", "L0STAGING"]
    }
];

let failed = 0;
testCases.forEach(tc => {
    const out = formatMarkdownChat(tc.input);
    let ok = true;
    for (const exp of tc.expected) {
        if (!out.includes(exp)) {
            console.error(`FAIL: ${tc.name} - Expected to find "${exp}"`);
            ok = false;
        }
    }
    for (const forb of tc.forbidden) {
        if (out.includes(forb)) {
            console.error(`FAIL: ${tc.name} - Found forbidden "${forb}"`);
            ok = false;
        }
    }
    if (ok) {
        console.log(`PASS: ${tc.name}`);
    } else {
        failed++;
        console.error("Output was:\n", out);
    }
});

if (failed > 0) {
    console.error(`\n❌ ${failed} tests failed!`);
    process.exit(1);
} else {
    console.log(`\n🎉 ALL ${testCases.length} TESTS PASSED!`);
}
