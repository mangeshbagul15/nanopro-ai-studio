import os

gw_path = os.path.join("deploy", "cloudflare_worker_gateway.js")
with open(gw_path, "r", encoding="utf-8") as f:
    content = f.read()

old_bank_rpt_block = """    {
      "id": "bank_rpt",
      "name": "RBI / FIU / ALM / UPI Reports",
      "stage": "REPORT",
      "engine": "reports",
      "schedule": "After L2 star",
      "description": "Builds 44 statutory reports across AML/FIU-IND (21), RBI/ADF/CIMS (10), ALM (7), UPI/Cards (6) with Master Excel & Domain CSV packages in SFTP Outbound.",
      "status": "SUCCESS",
      "rows": 142500,
      "tables": 44,
      "detail": "All 44 regulatory report marts verified (AML: 21, RBI: 10, ALM: 7, UPI: 6) • Master Excel & CSVs published to SFTP Outbound.",
      "paused": false,
      "in_flight": false
    },"""

new_bank_rpt_block = """    {
      "id": "bank_rpt_aml",
      "name": "AML & FIU-IND (21 Reports)",
      "stage": "REPORT",
      "engine": "reports",
      "schedule": "After L2 star",
      "description": "CTR, STR, CCR, NTR, CBWTR, Structuring, PEP, TBML (21 reports) -> NANOPRO_AML_FIU_IND_21_Reports.xlsx in SFTP Outbound.",
      "status": "SUCCESS",
      "rows": 142500,
      "tables": 21,
      "detail": "21 AML & FIU-IND statutory reports verified • NANOPRO_AML_FIU_IND_21_Reports.xlsx published to SFTP Outbound.",
      "paused": false,
      "in_flight": false
    },
    {
      "id": "bank_rpt_rbi",
      "name": "RBI ADF / CIMS (10 Reports)",
      "stage": "REPORT",
      "engine": "reports",
      "schedule": "After L2 star",
      "description": "Form A, Form VIII, CRILC, SMA, PSL, LCR, NSFR (10 reports) -> NANOPRO_RBI_ADF_CIMS_10_Reports.xlsx in SFTP Outbound.",
      "status": "SUCCESS",
      "rows": 142500,
      "tables": 10,
      "detail": "10 RBI ADF/CIMS statutory reports verified • NANOPRO_RBI_ADF_CIMS_10_Reports.xlsx published to SFTP Outbound.",
      "paused": false,
      "in_flight": false
    },
    {
      "id": "bank_rpt_alm",
      "name": "ALM & Liquidity (7 Reports)",
      "stage": "REPORT",
      "engine": "reports",
      "schedule": "After L2 star",
      "description": "Structural Liquidity SLS, IRS Sensitivity, EaR, EVE, NIM (7 reports) -> NANOPRO_ALM_Liquidity_7_Reports.xlsx in SFTP Outbound.",
      "status": "SUCCESS",
      "rows": 142500,
      "tables": 7,
      "detail": "7 ALM liquidity risk reports verified • NANOPRO_ALM_Liquidity_7_Reports.xlsx published to SFTP Outbound.",
      "paused": false,
      "in_flight": false
    },
    {
      "id": "bank_rpt_upi",
      "name": "UPI & Digital (6 Reports)",
      "stage": "REPORT",
      "engine": "reports",
      "schedule": "After L2 star",
      "description": "NPCI Settlement, TD vs BD, ATM Switch, Chargebacks (6 reports) -> NANOPRO_UPI_Digital_Banking_6_Reports.xlsx in SFTP Outbound.",
      "status": "SUCCESS",
      "rows": 142500,
      "tables": 6,
      "detail": "6 UPI & Digital Banking reports verified • NANOPRO_UPI_Digital_Banking_6_Reports.xlsx published to SFTP Outbound.",
      "paused": false,
      "in_flight": false
    },"""

assert old_bank_rpt_block in content, "old_bank_rpt_block not found"
content = content.replace(old_bank_rpt_block, new_bank_rpt_block, 1)

old_sftp_section = """    sftp: {
      status: "live",
      landing_prefix: "s3://nanopro-data-lake-765865641438/sftp/inbound/",
      bronze_prefix: "s3://nanopro-data-lake-765865641438/sftp/bronze/",
      glue_database: "nanopro_sftp",
      supported: ["csv", "txt", "tsv", "xlsx", "xls"],
      files: [
        {
          key: "cbs_feed/sample_transactions.csv",
          name: "sample_transactions.csv",
          partner: "cbs_feed",
          size: 1420,
          rows: 4,
          table: "CBS_FEED_SAMPLE_TRANSACTIONS",
          status: "INGESTED",
          ingested_at: new Date().toISOString()
        }
      ],
      tables: [
        {
          table: "CBS_FEED_SAMPLE_TRANSACTIONS",
          source_file: "sample_transactions.csv",
          rows: 4,
          columns: "account_id, txn_type, amount, channel, timestamp",
          ingested_at: new Date().toISOString()
        }
      ]
    },"""

new_sftp_section = """    sftp: {
      status: "live",
      landing_prefix: "s3://nanopro-data-lake-765865641438/sftp/inbound/",
      bronze_prefix: "s3://nanopro-data-lake-765865641438/sftp/bronze/",
      glue_database: "nanopro_sftp",
      supported: ["csv", "txt", "tsv", "xlsx", "xls"],
      files: [
        {
          key: "cbs_feed/sample_transactions.csv",
          name: "sample_transactions.csv",
          partner: "cbs_feed",
          size: 1420,
          rows: 4,
          table: "CBS_FEED_SAMPLE_TRANSACTIONS",
          status: "INGESTED",
          ingested_at: new Date().toISOString()
        },
        {
          key: "upi_settlement/npci_upi_clearing.csv",
          name: "npci_upi_clearing.csv",
          partner: "upi_settlement",
          size: 3280,
          rows: 12,
          table: "UPI_SETTLEMENT_NPCI_CLEARING",
          status: "INGESTED",
          ingested_at: new Date().toISOString()
        },
        {
          key: "inbound_cbs/daily_gl_balances.csv",
          name: "daily_gl_balances.csv",
          partner: "inbound_cbs",
          size: 5120,
          rows: 25,
          table: "CBS_DAILY_GL_BALANCES",
          status: "INGESTED",
          ingested_at: new Date().toISOString()
        }
      ],
      tables: [
        {
          table: "CBS_FEED_SAMPLE_TRANSACTIONS",
          source_file: "sample_transactions.csv",
          rows: 4,
          columns: "account_id, txn_type, amount, channel, timestamp",
          ingested_at: new Date().toISOString()
        },
        {
          table: "UPI_SETTLEMENT_NPCI_CLEARING",
          source_file: "npci_upi_clearing.csv",
          rows: 12,
          columns: "rrn, upi_ref, remitter_vpa, payee_vpa, amount, status, settlement_date",
          ingested_at: new Date().toISOString()
        },
        {
          table: "CBS_DAILY_GL_BALANCES",
          source_file: "daily_gl_balances.csv",
          rows: 25,
          columns: "gl_code, gl_description, branch_code, currency, closing_balance",
          ingested_at: new Date().toISOString()
        }
      ]
    },"""

assert old_sftp_section in content, "old_sftp_section not found"
content = content.replace(old_sftp_section, new_sftp_section, 1)

old_outbound_section = """    sftp_outbound: {
      status: "live",
      prefix: "s3://nanopro-data-lake-765865641438/sftp/outbound/reports/",
      sftp_path: "/sftp/outbound/reports/",
      reports: [
        {
          key: "sftp/outbound/reports/NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx",
          filename: "NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx",
          bytes: 70349,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_AML_FIU_20261119_200425.csv",
          filename: "NANOPRO_AML_FIU_20261119_200425.csv",
          bytes: 56191,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_AML_FIU_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_AML_FIU_20261119_200425.csv"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_RBI_ADF_CIMS_20261119_200425.csv",
          filename: "NANOPRO_RBI_ADF_CIMS_20261119_200425.csv",
          bytes: 5900,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_RBI_ADF_CIMS_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_RBI_ADF_CIMS_20261119_200425.csv"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_ALM_LIQUIDITY_20261119_200425.csv",
          filename: "NANOPRO_ALM_LIQUIDITY_20261119_200425.csv",
          bytes: 2940,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_ALM_LIQUIDITY_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_ALM_LIQUIDITY_20261119_200425.csv"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_UPI_DIGITAL_20261119_200425.csv",
          filename: "NANOPRO_UPI_DIGITAL_20261119_200425.csv",
          bytes: 4146,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_UPI_DIGITAL_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_UPI_DIGITAL_20261119_200425.csv"
        }
      ]
    },"""

new_outbound_section = """    sftp_outbound: {
      status: "live",
      prefix: "s3://nanopro-data-lake-765865641438/sftp/outbound/reports/",
      sftp_path: "/sftp/outbound/reports/",
      reports: [
        {
          key: "sftp/outbound/reports/NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx",
          filename: "NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx",
          bytes: 70349,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_BANKING_REPORTS_EOD_20261119_200425.xlsx"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_AML_FIU_IND_21_Reports_20261119_200425.xlsx",
          filename: "NANOPRO_AML_FIU_IND_21_Reports_20261119_200425.xlsx",
          bytes: 42100,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_AML_FIU_IND_21_Reports_20261119_200425.xlsx",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_AML_FIU_IND_21_Reports_20261119_200425.xlsx"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_RBI_ADF_CIMS_10_Reports_20261119_200425.xlsx",
          filename: "NANOPRO_RBI_ADF_CIMS_10_Reports_20261119_200425.xlsx",
          bytes: 18450,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_RBI_ADF_CIMS_10_Reports_20261119_200425.xlsx",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_RBI_ADF_CIMS_10_Reports_20261119_200425.xlsx"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_ALM_Liquidity_7_Reports_20261119_200425.xlsx",
          filename: "NANOPRO_ALM_Liquidity_7_Reports_20261119_200425.xlsx",
          bytes: 14200,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_ALM_Liquidity_7_Reports_20261119_200425.xlsx",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_ALM_Liquidity_7_Reports_20261119_200425.xlsx"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_UPI_Digital_Banking_6_Reports_20261119_200425.xlsx",
          filename: "NANOPRO_UPI_Digital_Banking_6_Reports_20261119_200425.xlsx",
          bytes: 12900,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_UPI_Digital_Banking_6_Reports_20261119_200425.xlsx",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_UPI_Digital_Banking_6_Reports_20261119_200425.xlsx"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_AML_FIU_20261119_200425.csv",
          filename: "NANOPRO_AML_FIU_20261119_200425.csv",
          bytes: 56191,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_AML_FIU_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_AML_FIU_20261119_200425.csv"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_RBI_ADF_CIMS_20261119_200425.csv",
          filename: "NANOPRO_RBI_ADF_CIMS_20261119_200425.csv",
          bytes: 5900,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_RBI_ADF_CIMS_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_RBI_ADF_CIMS_20261119_200425.csv"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_ALM_LIQUIDITY_20261119_200425.csv",
          filename: "NANOPRO_ALM_LIQUIDITY_20261119_200425.csv",
          bytes: 2940,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_ALM_LIQUIDITY_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_ALM_LIQUIDITY_20261119_200425.csv"
        },
        {
          key: "sftp/outbound/reports/NANOPRO_UPI_DIGITAL_20261119_200425.csv",
          filename: "NANOPRO_UPI_DIGITAL_20261119_200425.csv",
          bytes: 4146,
          modified: new Date().toISOString(),
          sftp_path: "/sftp/outbound/reports/NANOPRO_UPI_DIGITAL_20261119_200425.csv",
          download_url: "/api/banking/orchestrator/report/download?filename=NANOPRO_UPI_DIGITAL_20261119_200425.csv"
        }
      ]
    },"""

assert old_outbound_section in content, "old_outbound_section not found"
content = content.replace(old_outbound_section, new_outbound_section, 1)

with open(gw_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched cloudflare_worker_gateway.js")
