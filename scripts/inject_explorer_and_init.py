with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add ailabInitExplorer() call in window.initGlobalAILab
old_init = '''    ailabInitGrip();
    ailabHydrateLocalStorage();
    await ailabLoadHistory();
    ailabLoadLiveModels();'''

new_init = '''    ailabInitGrip();
    ailabHydrateLocalStorage();
    await ailabLoadHistory();
    ailabLoadLiveModels();
    ailabInitExplorer();'''

if old_init in text and "ailabInitExplorer();" not in text:
    text = text.replace(old_init, new_init)

# 2. Add complete Explorer JS engine right before window.initGlobalAILab
explorer_engine_js = '''
  // =========================================================================
  // DATA MODELING EXPLORER JAVASCRIPT CONTROLLER (AWS, Snowflake, BigQuery, DuckDB)
  // =========================================================================
  window.AILAB_EXPLORER = {
    isOpen: true,
    catalog: null,
    treeOpen: { "db_duckdb": true, "db_snowflake": true, "db_bigquery": true, "db_aws": true, "sc_duckdb_main": true, "sc_snowflake_CORE_BANKING": true },
    activeTable: null
  };

  window.ailabInitExplorer = function() {
    const grip = $id("ailabExplorerGrip");
    const panel = $id("ailabExplorer");
    if (grip && panel) {
      let isDragging = false;
      let startX = 0, startW = 0;

      grip.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.clientX;
        startW = panel.offsetWidth;
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
      });

      window.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        const newW = Math.max(180, Math.min(500, startW + (e.clientX - startX)));
        panel.style.width = newW + "px";
      });

      window.addEventListener("mouseup", () => {
        if (isDragging) {
          isDragging = false;
          document.body.style.cursor = "";
          document.body.style.userSelect = "";
        }
      });
    }

    ailabLoadExplorer();
  };

  window.ailabToggleExplorer = function() {
    const p = $id("ailabExplorer");
    const btn = $id("ailabToggleExplorer");
    if (!p) return;
    const isHidden = p.classList.toggle("is-hidden");
    AILAB_EXPLORER.isOpen = !isHidden;
    if (btn) btn.classList.toggle("is-active", !isHidden);
  };

  window.ailabLoadExplorer = async function(forceRefresh = false) {
    const tree = $id("ailabExplorerTree");
    if (!tree) return;

    try {
      const res = await fetch("/api/ai/explorer/catalog");
      if (res.ok) {
        const data = await res.json();
        AILAB_EXPLORER.catalog = data.databases || [];
        ailabRenderExplorerTree();
        return;
      }
    } catch (_) {}

    // Fallback static seed catalog
    AILAB_EXPLORER.catalog = [
      {
        id: "duckdb", name: "DuckDB Local Lakehouse", kind: "duckdb", icon: "🦆",
        schemas: [{ name: "main", tables: [
          { name: "ai_conversations", rows: 1420, columns: [{ name: "id", type: "VARCHAR PRIMARY KEY" }, { name: "chat_id", type: "VARCHAR" }, { name: "role", type: "VARCHAR" }, { name: "content", type: "TEXT" }, { name: "created_at", type: "TIMESTAMP" }] },
          { name: "banking_transactions_cdc", rows: 28400, columns: [{ name: "tx_id", type: "BIGINT PRIMARY KEY" }, { name: "account_no", type: "VARCHAR" }, { name: "amount", type: "DECIMAL(18,2)" }, { name: "cdc_operation", type: "VARCHAR" }, { name: "branch_code", type: "VARCHAR" }] },
          { name: "analytics_summary", rows: 365, columns: [{ name: "report_date", type: "DATE PRIMARY KEY" }, { name: "daily_volume", type: "DECIMAL(20,2)" }, { name: "tx_count", type: "INTEGER" }] }
        ]}]
      },
      {
        id: "snowflake", name: "Snowflake Enterprise Warehouse", kind: "snowflake", icon: "❄️",
        schemas: [
          { name: "CORE_BANKING", tables: [
            { name: "TRANSACTIONS_RAW", rows: 1250000, columns: [{ name: "TRANSACTION_ID", type: "VARCHAR(64)" }, { name: "SRC_ACCOUNT", type: "VARCHAR(32)" }, { name: "DEST_ACCOUNT", type: "VARCHAR(32)" }, { name: "AMOUNT_USD", type: "NUMBER(18,4)" }, { name: "STATUS", type: "VARCHAR(16)" }] },
            { name: "ACCOUNTS_DIM", rows: 45000, columns: [{ name: "ACCOUNT_KEY", type: "NUMBER" }, { name: "ACCOUNT_NUMBER", type: "VARCHAR(32)" }, { name: "CUSTOMER_NAME", type: "VARCHAR(128)" }] }
          ]},
          { name: "ANALYTICS", tables: [
            { name: "MONTHLY_METRICS", rows: 120, columns: [{ name: "MONTH_YEAR", type: "VARCHAR(7)" }, { name: "TOTAL_REVENUE", type: "NUMBER(20,2)" }, { name: "FRAUD_RATIO", type: "FLOAT" }] }
          ]}
        ]
      },
      {
        id: "bigquery", name: "Google BigQuery Lakehouse", kind: "bigquery", icon: "☁️",
        schemas: [{ name: "nanopro_analytics", tables: [
          { name: "lakehouse_audit_logs", rows: 840000, columns: [{ name: "event_id", type: "STRING" }, { name: "event_timestamp", type: "TIMESTAMP" }, { name: "actor", type: "STRING" }, { name: "action", type: "STRING" }] },
          { name: "model_inferences_2026", rows: 54000, columns: [{ name: "request_id", type: "STRING" }, { name: "provider", type: "STRING" }, { name: "model_id", type: "STRING" }, { name: "latency_ms", type: "FLOAT64" }] },
          { name: "customer_segments", rows: 8200, columns: [{ name: "customer_id", type: "STRING" }, { name: "rfm_score", type: "INT64" }, { name: "segment_label", type: "STRING" }] }
        ]}]
      },
      {
        id: "aws", name: "AWS Cloud Data Lake (Athena / S3)", kind: "aws", icon: "🟧",
        schemas: [{ name: "aws_athena_curated", tables: [
          { name: "s3_silver_orders", rows: 450000, columns: [{ name: "order_id", type: "string" }, { name: "order_date", type: "date" }, { name: "net_amount", type: "double" }, { name: "s3_partition_dt", type: "string" }] },
          { name: "s3_gold_revenue", rows: 1825, columns: [{ name: "snapshot_date", type: "date" }, { name: "gross_sales", type: "double" }, { name: "discounts", type: "double" }] }
        ]}]
      }
    ];

    ailabRenderExplorerTree();
  };

  window.ailabRenderExplorerTree = function() {
    const tree = $id("ailabExplorerTree");
    if (!tree) return;
    const filter = ($id("ailabExplorerFilter")?.value || "").toLowerCase().trim();
    const dbs = AILAB_EXPLORER.catalog || [];

    if (dbs.length === 0) {
      tree.innerHTML = '<div style="padding:15px;text-align:center;color:#64748B;font-size:12px;">No databases loaded.</div>';
      return;
    }

    let html = "";
    dbs.forEach(db => {
      const dbKey = "db_" + db.id;
      const isOpen = AILAB_EXPLORER.treeOpen[dbKey] !== false;

      let schemasHtml = "";
      (db.schemas || []).forEach(sc => {
        const scKey = "sc_" + db.id + "_" + sc.name;
        const isScOpen = AILAB_EXPLORER.treeOpen[scKey] !== false;

        let tablesHtml = "";
        (sc.tables || []).forEach(tb => {
          if (filter && !tb.name.toLowerCase().includes(filter) && !sc.name.toLowerCase().includes(filter)) {
            return;
          }
          const tbKey = "tb_" + db.id + "_" + sc.name + "_" + tb.name;
          const isTbOpen = !!AILAB_EXPLORER.treeOpen[tbKey];

          let colsHtml = "";
          if (tb.columns && tb.columns.length > 0) {
            colsHtml = `
              <div class="ailab-tree-children ${isTbOpen ? 'is-expanded' : ''}" id="child_${escapeHtml(tbKey)}">
                ${tb.columns.map(c => `
                  <div style="padding:2px 6px 2px 22px;font-size:10.5px;color:#94A3B8;display:flex;justify-content:space-between;font-family:monospace;">
                    <span>• ${escapeHtml(c.name)}</span>
                    <span style="color:#64748B;font-size:9.5px;">${escapeHtml(c.type)}</span>
                  </div>
                `).join("")}
              </div>
            `;
          }

          tablesHtml += `
            <div class="ailab-tree-node">
              <div class="ailab-tree-row" onclick="ailabClickExplorerTable('${escapeHtml(db.id)}', '${escapeHtml(sc.name)}', '${escapeHtml(tb.name)}', '${escapeHtml(tbKey)}')">
                <span class="ailab-tree-arrow ${isTbOpen ? 'is-expanded' : ''}">▶</span>
                <span style="font-size:11px;">📄</span>
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(tb.name)}</span>
                <span class="ailab-tree-badge" style="background:rgba(59,130,246,0.15);color:#93C5FD;">${tb.rows ? tb.rows.toLocaleString() : ''}r</span>
              </div>
              ${colsHtml}
            </div>
          `;
        });

        if (tablesHtml || !filter) {
          schemasHtml += `
            <div class="ailab-tree-node">
              <div class="ailab-tree-row" onclick="ailabToggleTreeNode('${escapeHtml(scKey)}')">
                <span class="ailab-tree-arrow ${isScOpen ? 'is-expanded' : ''}">▶</span>
                <span style="font-size:11px;">📁</span>
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#E2E8F0;">${escapeHtml(sc.name)}</span>
              </div>
              <div class="ailab-tree-children ${isScOpen ? 'is-expanded' : ''}" id="child_${escapeHtml(scKey)}">
                ${tablesHtml || '<div style="padding:4px 15px;color:#64748B;font-size:11px;">No tables.</div>'}
              </div>
            </div>
          `;
        }
      });

      html += `
        <div class="ailab-tree-node" style="margin-bottom:6px;">
          <div class="ailab-tree-row" style="font-weight:700;color:#F8FAFC;" onclick="ailabToggleTreeNode('${escapeHtml(dbKey)}')">
            <span class="ailab-tree-arrow ${isOpen ? 'is-expanded' : ''}">▶</span>
            <span>${db.icon || '🗄️'}</span>
            <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(db.name)}</span>
          </div>
          <div class="ailab-tree-children ${isOpen ? 'is-expanded' : ''}" id="child_${escapeHtml(dbKey)}">
            ${schemasHtml}
          </div>
        </div>
      `;
    });

    tree.innerHTML = html;
  };

  window.ailabToggleTreeNode = function(key) {
    AILAB_EXPLORER.treeOpen[key] = !AILAB_EXPLORER.treeOpen[key];
    const el = $id("child_" + key);
    if (el) el.classList.toggle("is-expanded", AILAB_EXPLORER.treeOpen[key]);
    ailabRenderExplorerTree();
  };

  window.ailabClickExplorerTable = function(dbId, schema, table, tbKey) {
    AILAB_EXPLORER.treeOpen[tbKey] = !AILAB_EXPLORER.treeOpen[tbKey];
    ailabRenderExplorerTree();

    const fullPath = `${dbId}.${schema}.${table}`;
    const input = $id("ailabPromptInput");
    if (input) {
      input.value = `Analyze table \`${fullPath}\` with schema optimization, CDC deduplication, and DuckDB/BigQuery performance.`;
      input.focus();
    }
  };

  window.ailabFilterExplorer = function(val) {
    ailabRenderExplorerTree();
  };
'''

if "window.AILAB_EXPLORER" not in text:
    text = text.replace("window.initGlobalAILab = async function() {", explorer_engine_js + "\n  window.initGlobalAILab = async function() {")

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Injected Explorer JS engine successfully!")
