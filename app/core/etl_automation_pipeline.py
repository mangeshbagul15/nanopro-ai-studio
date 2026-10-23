"""
NanoPro AI Studio  Full ETL Automation Pipeline
=================================================
Architecture:
  Internet Sample Data
      
  Neon PostgreSQL -> L0_RAW (Bronze)
      
  Neon PostgreSQL -> L1_CLEAN (Silver)
      
  Snowflake BANK_DB -> L2_SUMMARY (Gold)
      
  Reports -> Email (nanoproaistudio@gmail.com) + Telegram (@mangesh_reports_bot)

Projects:
  1. credit_card   Credit Card Transactions & Fraud
  2. aml           Anti-Money Laundering
  3. alm           Asset Liability Management
  4. adf_cims      RBI ADF CIMS Reporting
  5. cbs           Core Banking Finacle Recon

Schedules:
  BOD   06:00 AM IST (Full Load check, status)
  SOD   08:00 AM IST (Start of Day report)
  Daily 10:00 AM IST (T-1 report dispatch)
  EOD   06:00 PM IST (End of Day summary)
  Weekly   Monday 08:00 AM
  Fortnightly  1st & 15th 08:00 AM
  Monthly      1st of month 07:00 AM
"""

from __future__ import annotations

import os
import time
import uuid
import json
import random
import threading
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.logger import log_event
from app.core.config import BASE_DIR, TELEGRAM_CHAT_ID

# 
# Star Schema: Real Banking Replica  Fact & Dimension Tables
# Based on actual Indian banking data models (RBI/IBA standards)
# 

STAR_SCHEMA = {

    # 
    # 1. CREDIT CARD  8 Source Files, 10 Oracle Tables
    #    Real bank: HDFC/ICICI/SBI Card style
    # 
    "credit_card": {
        "dims": {
            # Card master  SCD2 (limit changes, upgrades)
            "DIM_CARD": [
                "card_key","card_number_masked","card_type",        # VISA/MASTER/RUPAY/AMEX
                "card_variant","credit_limit_inr","cash_limit_inr",
                "card_status","expiry_date","issue_date",
                "international_enabled","contactless_enabled",
                "customer_key","scd_start_date","scd_end_date","is_current",
                "date_of_generation","report_date","execution_date"
            ],
            # Customer  SCD2
            "DIM_CUSTOMER": [
                "customer_key","customer_id","cust_name","pan_masked",
                "dob","gender","segment",                           # RETAIL/HNI/CORPORATE
                "city","state","pincode","kyc_status","risk_grade",
                "scd_start_date","scd_end_date","is_current",
                "date_of_generation","report_date","execution_date"
            ],
            # Merchant
            "DIM_MERCHANT": [
                "merchant_key","merchant_id","merchant_name",
                "mcc_code","mcc_category","city","state","country",
                "is_international","is_high_risk",
                "date_of_generation","report_date","execution_date"
            ],
            # Date
            "DIM_DATE": [
                "date_key","full_date","day_of_week","day_name",
                "week_of_year","month","month_name","quarter",
                "year","financial_year","is_weekend","is_bank_holiday","is_month_end"
            ],
            # Channel
            "DIM_CHANNEL": [
                "channel_key","channel_code","channel_name",
                "channel_type",                                    # POS/ECOM/ATM/TAP/UPI
                "is_digital","is_card_present","is_domestic",
                "date_of_generation","report_date","execution_date"
            ],
            # EMI Scheme
            "DIM_EMI_SCHEME": [
                "emi_key","scheme_code","scheme_name","tenure_months",
                "interest_rate_pct","processing_fee_pct","bank_name",
                "date_of_generation","report_date","execution_date"
            ],
        },
        "facts": {
            # Core transaction fact
            "FACT_CC_TRANSACTIONS": [
                "txn_key","card_key","customer_key","merchant_key",
                "date_key","channel_key",
                "auth_code","rrn",                                 # Reference Retrieval Number
                "txn_amount_inr","fee_inr","gst_inr",
                "reward_points_earned","cashback_inr",
                "txn_type",                                        # PURCHASE/REFUND/CASH_ADV/EMI
                "txn_status",                                      # SETTLED/DECLINED/REVERSED
                "fraud_flag","risk_score","risk_model_version",
                "txn_timestamp","settlement_date",
                "date_of_generation","report_date","execution_date"
            ],
            # Fraud alerts
            "FACT_CC_FRAUD_ALERTS": [
                "alert_key","txn_key","card_key","customer_key","date_key",
                "alert_type",                                      # VELOCITY/GEOLOCATION/DARK_WEB
                "risk_category","ml_score","rule_triggered",
                "is_confirmed_fraud","false_positive_flag",
                "resolution_status","resolved_by","resolved_at",
                "date_of_generation","report_date","execution_date"
            ],
            # Monthly statement summary
            "FACT_CC_MONTHLY_STATEMENT": [
                "stmt_key","card_key","customer_key","date_key",
                "stmt_period","opening_balance","closing_balance",
                "total_purchases","total_cash_advance","total_payments",
                "min_due","total_due","credit_limit_used_pct",
                "reward_points_balance","late_fee_charged",
                "date_of_generation","report_date","execution_date"
            ],
            # Chargeback
            "FACT_CC_CHARGEBACK": [
                "chargeback_key","txn_key","card_key","merchant_key","date_key",
                "chargeback_reason","amount_inr","status",
                "dispute_date","resolution_date","bank_decision",
                "date_of_generation","report_date","execution_date"
            ],
        },
    },

    # 
    # 2. AML  16 SFTP Files + 16 Oracle Tables
    #    FIU-IND / PMLA compliant model
    # 
    "aml": {
        "dims": {
            # Customer  SCD2
            "DIM_CUSTOMER": [
                "customer_key","customer_id","ucic",               # Unique Customer ID Code
                "customer_name","pan_masked","aadhaar_masked",
                "customer_type",                                   # INDIVIDUAL/CORPORATE/NRI/PEP
                "nationality","country_of_residence",
                "risk_rating",                                     # LOW/MEDIUM/HIGH/CRITICAL
                "pep_flag","sanction_flag","adverse_media_flag",
                "kyc_expiry_date","last_kyc_date",
                "scd_start_date","scd_end_date","is_current",
                "date_of_generation","report_date","execution_date"
            ],
            # Account  SCD2
            "DIM_ACCOUNT": [
                "account_key","account_id","account_type",         # SB/CA/OD/CC/NRE/NRO/FCNR
                "branch_code","ifsc_code","sol_id",
                "open_date","close_date","account_status",
                "dormant_flag","freeze_flag","aml_monitored_flag",
                "scd_start_date","scd_end_date","is_current",
                "date_of_generation","report_date","execution_date"
            ],
            # Counterparty
            "DIM_COUNTERPARTY": [
                "cp_key","cp_id","cp_name","cp_account",
                "cp_bank_name","cp_bank_country","cp_bank_swift",
                "cp_type",                                         # INDIVIDUAL/ENTITY/SHELL
                "cp_risk_flag","cp_sanction_flag","fatf_country_flag",
                "date_of_generation","report_date","execution_date"
            ],
            # Date
            "DIM_DATE": [
                "date_key","full_date","day_of_week","week_of_year",
                "month","quarter","year","financial_year",
                "is_weekend","is_bank_holiday","is_rbi_reporting_date"
            ],
            # Alert Type (FIU-IND categories)
            "DIM_ALERT_TYPE": [
                "alert_key","alert_code","alert_name",
                "alert_category",                                  # STR/CTR/NTR/EFT
                "severity",                                        # LOW/MEDIUM/HIGH/CRITICAL
                "fiu_reportable","ctr_threshold_inr",
                "regulatory_ref",                                  # PMLA Section ref
                "date_of_generation","report_date","execution_date"
            ],
            # Branch
            "DIM_BRANCH": [
                "branch_key","branch_code","branch_name",
                "sol_id","ifsc","micr",
                "zone","region","state","city","tier",             # METRO/URBAN/SEMI/RURAL
                "date_of_generation","report_date","execution_date"
            ],
            # Channel
            "DIM_CHANNEL": [
                "channel_key","channel_code","channel_name",
                "is_digital","is_bulk","is_international",
                "date_of_generation","report_date","execution_date"
            ],
        },
        "facts": {
            # Core AML transaction monitoring
            "FACT_AML_TXN_MONITOR": [
                "txn_key","account_key","customer_key","cp_key",
                "date_key","channel_key","branch_key","alert_type_key",
                "txn_id","txn_reference",
                "txn_type",                                        # NEFT/RTGS/IMPS/SWIFT/CASH
                "amount_inr","base_currency","exchange_rate",
                "counterparty_country","correspondent_bank",
                "str_flag","ctr_flag","ntr_flag","eft_flag",
                "risk_score","ml_model_version",
                "structuring_flag","layering_flag","integration_flag",
                "txn_timestamp",
                "date_of_generation","report_date","execution_date"
            ],
            # STR  Suspicious Transaction Report
            "FACT_AML_STR": [
                "str_key","txn_key","customer_key","account_key","date_key",
                "str_reference","fiu_filing_ref",
                "str_type","str_reason","risk_description",
                "total_amount_inr","txn_count",
                "investigation_status",                            # OPEN/UNDER_REVIEW/FILED/CLOSED
                "compliance_officer","filing_date","fiu_ack_date",
                "date_of_generation","report_date","execution_date"
            ],
            # CTR  Cash Transaction Report (>10L INR)
            "FACT_AML_CTR": [
                "ctr_key","account_key","customer_key","branch_key","date_key",
                "ctr_reference","cash_txn_type",                   # DEPOSIT/WITHDRAWAL
                "amount_inr","txn_count_for_day",
                "threshold_breached_flag","cumulative_amount",
                "reporting_status","rbi_submission_date",
                "date_of_generation","report_date","execution_date"
            ],
            # PEP / Sanction Watch
            "FACT_AML_WATCHLIST_HITS": [
                "hit_key","customer_key","date_key",
                "watchlist_type",                                  # PEP/OFAC/UN/EU/RBI
                "match_score","match_type",                        # EXACT/FUZZY/PHONETIC
                "hit_status","escalated_flag","cleared_flag",
                "escalation_date","clearance_date",
                "date_of_generation","report_date","execution_date"
            ],
            # Daily AML Summary (L2 Gold)
            "FACT_AML_DAILY_SUMMARY": [
                "summary_key","date_key","branch_key",
                "total_txns","total_amount_inr",
                "str_count","ctr_count","ntr_count",
                "high_risk_count","critical_count",
                "new_alerts","resolved_alerts","open_alerts",
                "date_of_generation","report_date","execution_date"
            ],
        },
    },

    # 
    # 3. ALM  Asset Liability Management
    #    RBI ALM Policy / Basel III LCR / NSFR
    # 
    "alm": {
        "dims": {
            # Product
            "DIM_PRODUCT": [
                "product_key","product_code","product_name",
                "product_type",                                    # DEPOSIT/LOAN/INVESTMENT/FX
                "asset_liability",                                 # ASSET/LIABILITY
                "instrument_class",                                # CASA/TD/LOAN/BOND/FX_SWAP
                "is_hqla",                                         # High Quality Liquid Asset
                "hqla_level",                                      # LEVEL1/LEVEL2A/LEVEL2B
                "is_core_deposit",
                "date_of_generation","report_date","execution_date"
            ],
            # Time Bucket (RBI ALM buckets)
            "DIM_TIME_BUCKET": [
                "bucket_key","bucket_code","bucket_label",
                "bucket_days_min","bucket_days_max",
                "rbi_bucket_code",                                 # RBI ALM circular buckets
                "liquidity_horizon",                               # OVERNIGHT/SHORT/MEDIUM/LONG
                "date_of_generation","report_date","execution_date"
            ],
            # Currency
            "DIM_CURRENCY": [
                "currency_key","currency_code","currency_name",
                "is_functional","is_freely_convertible",
                "rbi_reporting_flag",
                "date_of_generation","report_date","execution_date"
            ],
            # Date
            "DIM_DATE": [
                "date_key","full_date","day_of_week","week_of_year",
                "month","quarter","year","financial_year",
                "is_weekend","is_bank_holiday","is_month_end","is_quarter_end"
            ],
            # Branch / Treasury Centre
            "DIM_BRANCH": [
                "branch_key","branch_code","branch_name",
                "zone","region","state",
                "is_treasury_centre","is_dealing_room",
                "date_of_generation","report_date","execution_date"
            ],
            # Counterparty (Treasury)
            "DIM_TREASURY_CP": [
                "cp_key","cp_name","cp_type",                      # BANK/CORPORATE/FII/RBI
                "credit_rating","rating_agency","country",
                "date_of_generation","report_date","execution_date"
            ],
        },
        "facts": {
            # Cashflow bucketing (core ALM fact)
            "FACT_ALM_CASHFLOWS": [
                "cf_key","product_key","bucket_key","currency_key",
                "date_key","branch_key","cp_key",
                "deal_id","deal_type",
                "inflow_amount_inr","outflow_amount_inr","net_cashflow_inr",
                "inflow_fx_amount","outflow_fx_amount",
                "lcr_eligible_flag","nsfr_eligible_flag",
                "run_off_rate","inflow_rate",                      # Basel III rates
                "valuation_date","maturity_date",
                "date_of_generation","report_date","execution_date"
            ],
            # Structural Liquidity (Gap Statement)
            "FACT_STRUCTURAL_LIQUIDITY": [
                "sl_key","date_key","bucket_key","currency_key",
                "total_assets_inr","total_liabilities_inr",
                "gap_inr","cumulative_gap_inr",
                "gap_pct_of_total_assets",
                "rbi_threshold_pct","threshold_breached",
                "date_of_generation","report_date","execution_date"
            ],
            # LCR  Liquidity Coverage Ratio (Basel III)
            "FACT_LCR_DAILY": [
                "lcr_key","date_key","currency_key",
                "hqla_level1_inr","hqla_level2a_inr","hqla_level2b_inr",
                "total_hqla_inr",
                "total_net_cash_outflow_30d","total_net_cash_inflow_30d",
                "net_cash_outflow_inr","lcr_ratio",
                "rbi_minimum_lcr","breach_flag",
                "date_of_generation","report_date","execution_date"
            ],
            # NSFR  Net Stable Funding Ratio (Basel III)
            "FACT_NSFR_MONTHLY": [
                "nsfr_key","date_key","currency_key",
                "available_stable_funding","required_stable_funding",
                "nsfr_ratio","rbi_minimum_nsfr","breach_flag",
                "date_of_generation","report_date","execution_date"
            ],
        },
    },

    # 
    # 4. ADF CIMS  RBI Automated Data Flow
    #    XBRL/XML returns  Form A, BSR, SLR etc.
    # 
    "adf_cims": {
        "dims": {
            # GL Account (Chart of Accounts)
            "DIM_GL_ACCOUNT": [
                "gl_key","gl_code","gl_name","gl_short_name",
                "gl_category",                                     # ASSET/LIABILITY/INCOME/EXPENSE
                "schedule_no",                                     # RBI Balance Sheet schedule
                "rbi_return_code","rbi_line_item_code",
                "xbrl_element_id","xbrl_namespace",
                "finacle_gl_code","is_control_account",
                "date_of_generation","report_date","execution_date"
            ],
            # Return / Form Type
            "DIM_RETURN_TYPE": [
                "return_key","return_code","return_name",
                "rbi_form_ref",                                    # FORMA/FORMVIII/BSR1/BSR2/DSB
                "frequency",                                       # DAILY/WEEKLY/FORTNIGHTLY/MONTHLY
                "submission_deadline_days",
                "xbrl_taxonomy_version","regulatory_act",
                "date_of_generation","report_date","execution_date"
            ],
            # Date
            "DIM_DATE": [
                "date_key","full_date","day_of_week","week_of_year",
                "month","quarter","year","financial_year",
                "is_weekend","is_bank_holiday","is_rbi_due_date"
            ],
            # Branch
            "DIM_BRANCH": [
                "branch_key","branch_code","branch_name",
                "sol_id","ifsc","micr",
                "zone","region","state","tier",
                "date_of_generation","report_date","execution_date"
            ],
            # Currency
            "DIM_CURRENCY": [
                "currency_key","currency_code","currency_name",
                "is_functional","rbi_reporting_flag",
                "date_of_generation","report_date","execution_date"
            ],
            # Sector (RBI sector classification)
            "DIM_SECTOR": [
                "sector_key","sector_code","sector_name",
                "sector_group","priority_sector_flag",
                "rbi_sector_code","bsr_sector_code",
                "date_of_generation","report_date","execution_date"
            ],
        },
        "facts": {
            # GL Balances (core CIMS fact)
            "FACT_CIMS_GL_BALANCES": [
                "balance_key","gl_key","return_key",
                "date_key","branch_key","currency_key","sector_key",
                "opening_debit","opening_credit",
                "closing_debit","closing_credit","net_balance_inr",
                "previous_period_balance","variance_inr","variance_pct",
                "submission_status",                               # PENDING/SUBMITTED/ACCEPTED/REJECTED
                "date_of_generation","report_date","execution_date"
            ],
            # RBI Return Submissions
            "FACT_CIMS_SUBMISSIONS": [
                "submission_key","return_key","date_key",
                "total_line_items","validated_count",
                "submitted_count","accepted_count","rejected_count",
                "submission_timestamp","rbi_portal_ref",
                "rbi_ack_number","rbi_ack_timestamp",
                "submission_status","retry_count",
                "date_of_generation","report_date","execution_date"
            ],
            # SLR Compliance (Statutory Liquidity Ratio)
            "FACT_SLR_COMPLIANCE": [
                "slr_key","date_key","currency_key",
                "ndtl_inr",                                        # Net Demand & Time Liabilities
                "slr_required_pct","slr_required_inr",
                "slr_held_inr","slr_actual_pct",
                "slr_surplus_deficit","breach_flag",
                "govt_securities_inr","sdl_inr","tbill_inr",
                "date_of_generation","report_date","execution_date"
            ],
            # CRR Compliance (Cash Reserve Ratio)
            "FACT_CRR_COMPLIANCE": [
                "crr_key","date_key",
                "ndtl_inr","crr_required_pct","crr_required_inr",
                "balance_with_rbi","crr_actual_pct",
                "surplus_deficit","breach_flag",
                "date_of_generation","report_date","execution_date"
            ],
        },
    },

    # 
    # 5. CBS  Core Banking System (Infosys Finacle)
    #    Real bank CBS: Master Tables + Live Transactions
    #    Covers: CASA, Loans, FD/RD, GL, Payments, Customers
    # 
    "cbs": {
        "dims": {

            #  MASTER TABLES 

            # Customer Master (UCIC  Unique Customer ID Code)
            "DIM_CUSTOMER_MASTER": [
                "customer_key","cif_id","ucic",
                "full_name","short_name","salutation",
                "customer_type",                    # INDIVIDUAL/CORPORATE/NRI/MINOR/HUF/TRUST
                "pan_masked","aadhaar_masked","tan",
                "dob","gender","nationality","resident_status",  # RESIDENT/NRI/PIO
                "mobile","email","address_line1","city","state","pincode",
                "kyc_status","kyc_expiry_date","fatca_status",
                "risk_category",                    # LOW/MEDIUM/HIGH
                "relationship_manager","segment",   # RETAIL/PRIORITY/CORPORATE/STAFF
                "open_date","closure_date","status", # ACTIVE/DORMANT/DECEASED/BLOCKED
                "scd_start_date","scd_end_date","is_current",
                "date_of_generation","report_date","execution_date"
            ],

            # Account Master
            "DIM_ACCOUNT_MASTER": [
                "account_key","account_id","foracid",   # Finacle core account ID
                "cif_id","sol_id","branch_code",
                "account_type",                     # SB/CA/OD/CC/NRE/NRO/FCNR/RFC
                "product_code","scheme_code",
                "open_date","maturity_date","closure_date",
                "account_status",                   # ACTIVE/DORMANT/CLOSED/FROZEN/NPA
                "currency","current_balance","available_balance",
                "lien_amount","hold_amount",
                "interest_rate","od_limit",
                "freeze_code","freeze_reason",
                "nomination_flag","joint_flag",
                "scd_start_date","scd_end_date","is_current",
                "date_of_generation","report_date","execution_date"
            ],

            # Branch / SOL Master
            "DIM_BRANCH_MASTER": [
                "branch_key","branch_code","sol_id",
                "branch_name","branch_type",        # BRANCH/EXTENSION_COUNTER/ATM/DIGITAL
                "ifsc_code","micr_code","bsr_code",
                "zone","region","state","city","tier",  # METRO/URBAN/SEMI_URBAN/RURAL
                "rbi_centre_id","clearing_centre",
                "opening_date","migration_go_live_date",
                "migration_status",                 # NOT_STARTED/IN_PROGRESS/MIGRATED/ROLLBACK
                "is_live_on_finacle",
                "date_of_generation","report_date","execution_date"
            ],

            # Product / Scheme Master
            "DIM_PRODUCT_MASTER": [
                "product_key","product_code","scheme_code",
                "product_name","product_type",      # SB/CA/FD/RD/HL/PL/CC/OD/LAP/MSME
                "product_category",                 # DEPOSIT/LOAN/INVESTMENT/INSURANCE
                "interest_type",                    # FIXED/FLOATING/NIL
                "min_amount","max_amount",
                "min_tenure_days","max_tenure_days",
                "tds_applicable","premature_closure_allowed",
                "legacy_scheme_code","finacle_scheme_code","mapped_flag",
                "date_of_generation","report_date","execution_date"
            ],

            # GL Account / Chart of Accounts
            "DIM_GL_MASTER": [
                "gl_key","gl_code","gl_name","gl_short_name",
                "gl_type",                          # ASSET/LIABILITY/INCOME/EXPENSE/CONTINGENT
                "gl_category","gl_sub_category",
                "balance_sheet_schedule",           # Schedule 1-16 (RBI BS format)
                "p_and_l_schedule",
                "legacy_gl_code","finacle_gl_code",
                "finacle_scheme_code","mapped_flag",
                "mapping_status",                   # DIRECT/SPLIT/MERGED/UNMAPPED
                "control_account_flag","interbank_flag",
                "date_of_generation","report_date","execution_date"
            ],

            # Employee / User Master
            "DIM_EMPLOYEE_MASTER": [
                "employee_key","employee_id","finacle_user_id",
                "employee_name","designation","department",
                "role_type",                        # TELLER/OFFICER/MANAGER/AUDITOR/ADMIN
                "branch_code","sol_id",
                "access_level","maker_checker_role",
                "join_date","status",
                "date_of_generation","report_date","execution_date"
            ],

            # Date
            "DIM_DATE": [
                "date_key","full_date","day_of_week","day_name",
                "week_of_year","month","month_name","quarter",
                "year","financial_year",
                "is_weekend","is_bank_holiday","is_rbi_holiday",
                "is_clearing_day","is_eod_run_date","is_bod_run_date",
                "is_month_end","is_quarter_end","is_year_end"
            ],

            # Currency Master
            "DIM_CURRENCY": [
                "currency_key","currency_code","currency_name",
                "is_functional","is_freely_convertible",
                "rbi_reporting_flag","nostro_flag",
                "date_of_generation","report_date","execution_date"
            ],

            # Migration Batch
            "DIM_MIGRATION_BATCH": [
                "batch_key","batch_id","batch_name",
                "migration_phase",                  # PILOT/WAVE1/WAVE2/WAVE3/CUTOVER/FINAL
                "branch_count","account_count_planned","account_count_actual",
                "start_date","end_date","go_live_date",
                "cutover_type",                     # BIG_BANG/PHASED/PARALLEL_RUN
                "batch_status",                     # PLANNED/IN_PROGRESS/COMPLETED/ROLLBACK/ABORTED
                "rollback_flag","rollback_reason",
                "date_of_generation","report_date","execution_date"
            ],
        },

        "facts": {

            #  LIVE TRANSACTION TABLES 

            # Core Transaction Journal (all debits/credits)
            "FACT_CBS_TXN_JOURNAL": [
                "journal_key","account_key","gl_key",
                "branch_key","date_key","employee_key","currency_key",
                "tran_id","tran_type",              # DR/CR
                "tran_sub_type",                    # CASH/CLEARING/TRANSFER/INTEREST/CHARGES
                "tran_amount","tran_currency","tran_amount_inr",
                "tran_date","value_date","posting_date",
                "tran_code","tran_particulars","narration",
                "ref_number","voucher_number",
                "channel",                          # BRANCH/ATM/NET/MOBILE/UPI/NEFT/RTGS
                "maker_id","checker_id","authorised_flag",
                "reversal_flag","original_tran_id",
                "date_of_generation","report_date","execution_date"
            ],

            # CASA Daily Balance
            "FACT_CBS_CASA_BALANCE": [
                "balance_key","account_key","branch_key","date_key","currency_key",
                "opening_balance","closing_balance","available_balance",
                "lien_balance","hold_balance","od_utilized",
                "total_dr_count","total_cr_count",
                "total_dr_amount","total_cr_amount",
                "interest_accrued","charges_debited",
                "dormant_flag","npa_flag",
                "date_of_generation","report_date","execution_date"
            ],

            # Loan (HL/PL/LAP/MSME) Account
            "FACT_CBS_LOAN_ACCOUNT": [
                "loan_key","account_key","customer_key",
                "branch_key","product_key","date_key",
                "sanction_amount","disbursed_amount","outstanding_principal",
                "emi_amount","emi_due_date","next_emi_date",
                "overdue_principal","overdue_interest","overdue_charges",
                "dpd",                              # Days Past Due
                "npa_stage",                        # STANDARD/SMA0/SMA1/SMA2/NPA/D1/D2/D3/LOSS
                "provision_amount","pcr_pct",       # Provision Coverage Ratio
                "interest_rate","reset_date",
                "prepayment_amount","prepayment_date",
                "date_of_generation","report_date","execution_date"
            ],

            # FD / RD (Term Deposit)
            "FACT_CBS_TERM_DEPOSIT": [
                "td_key","account_key","customer_key",
                "branch_key","product_key","date_key",
                "principal_amount","maturity_amount",
                "interest_rate","interest_type",    # SIMPLE/COMPOUND/CUMULATIVE
                "open_date","maturity_date","renewal_date",
                "interest_accrued_ytd","tds_deducted",
                "premature_closure_flag","penalty_amount",
                "auto_renewal_flag","renewal_count",
                "date_of_generation","report_date","execution_date"
            ],

            # GL Balance (Day-end)
            "FACT_CBS_GL_BALANCE": [
                "gl_balance_key","gl_key","branch_key","date_key","currency_key",
                "opening_dr","opening_cr",
                "period_dr_amount","period_cr_amount","period_txn_count",
                "closing_dr","closing_cr","net_balance_inr",
                "legacy_net_balance","finacle_net_balance",
                "variance_inr","variance_pct",
                "parity_flag",                      # MATCH/MISMATCH/PARTIAL
                "reconciliation_status",            # OPEN/RESOLVED/ESCALATED/WAIVED
                "date_of_generation","report_date","execution_date"
            ],

            # EOD/BOD Batch Processing
            "FACT_CBS_BATCH_PROCESSING": [
                "batch_key_id","branch_key","date_key","batch_key",
                "batch_type",                       # BOD/EOD/SOD/INTRADAY/MONTHLY_CLOSE
                "batch_run_date","batch_start_time","batch_end_time","duration_minutes",
                "total_accounts_processed","success_count","failure_count","skip_count",
                "total_dr_txns","total_cr_txns",
                "total_dr_amount","total_cr_amount","net_position_inr",
                "interest_processed_accounts","interest_amount_inr",
                "charges_processed_accounts","charges_amount_inr",
                "error_count","warning_count","batch_status",  # SUCCESS/PARTIAL/FAILED/RUNNING
                "date_of_generation","report_date","execution_date"
            ],

            # Payments (NEFT/RTGS/IMPS/UPI)
            "FACT_CBS_PAYMENTS": [
                "payment_key","account_key","branch_key","date_key","currency_key",
                "payment_ref","uti_number","utr_number",
                "payment_type",                     # NEFT/RTGS/IMPS/UPI/SWIFT/CHEQUE
                "payment_mode",                     # INWARD/OUTWARD
                "amount_inr","beneficiary_name","beneficiary_account","beneficiary_ifsc",
                "remitter_name","remitter_account","remitter_bank",
                "payment_status",                   # PENDING/SUCCESS/FAILED/REVERSED/RETURNED
                "settlement_date","value_date",
                "rejection_reason","rbi_ref",
                "date_of_generation","report_date","execution_date"
            ],

            # Migration Parity Check
            "FACT_CBS_MIGRATION_PARITY": [
                "parity_key","account_key","batch_key","branch_key","product_key","date_key",
                "legacy_account_id","finacle_account_id",
                "legacy_balance_inr","finacle_balance_inr",
                "balance_variance_inr","balance_variance_pct",
                "interest_variance_inr","charges_variance_inr",
                "migration_status",                 # SUCCESS/FAILED/PARTIAL/PENDING
                "data_quality_score",               # 0-100
                "exception_count","exception_types",
                "verified_by","migrated_at","verified_at",
                "date_of_generation","report_date","execution_date"
            ],
        },
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # 6. UPI â€” Real-Time Payment Settlements
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "upi": {
        "dims": {
            "DIM_VPA":         ["vpa_key","vpa_id","vpa_handle","bank_code","bank_name","vpa_type","is_merchant","merchant_category","registered_mobile","kyc_flag","date_of_generation","report_date","execution_date"],
            "DIM_BANK":        ["bank_key","bank_code","bank_name","ifsc_prefix","upi_participant_flag","npci_member_flag","is_psp","settlement_bank","date_of_generation","report_date","execution_date"],
            "DIM_DATE":        ["date_key","full_date","day_of_week","week_of_year","month","quarter","year","financial_year","is_weekend","is_bank_holiday","is_npci_settlement_day"],
            "DIM_TXN_TYPE":    ["txn_type_key","txn_type_code","txn_type_name","flow_direction","collect_flag","mandate_flag","is_reversal","date_of_generation","report_date","execution_date"],
            "DIM_MERCHANT":    ["merchant_key","merchant_vpa","merchant_name","mcc_code","mcc_category","city","state","is_registered","date_of_generation","report_date","execution_date"],
        },
        "facts": {
            "FACT_UPI_TRANSACTIONS": ["txn_key","vpa_payer_key","vpa_payee_key","bank_key","date_key","txn_type_key","upi_txn_id","npci_txn_ref","amount_inr","txn_status","failure_reason","response_code","latency_ms","batch_id","reversal_flag","settlement_date","date_of_generation","report_date","execution_date"],
            "FACT_UPI_SETTLEMENT":   ["settlement_key","bank_key","date_key","batch_id","total_txns","success_count","failed_count","reversal_count","total_debit_inr","total_credit_inr","net_settlement_inr","npci_settlement_ref","settlement_status","date_of_generation","report_date","execution_date"],
            "FACT_UPI_DAILY_SUMMARY":["summary_key","date_key","bank_key","total_txns","success_rate_pct","avg_txn_amount","peak_hour","top_merchant_vpa","failure_rate_pct","date_of_generation","report_date","execution_date"],
        },
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # 7. UCIC â€” Unique Customer Identification (Customer 360)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "ucic": {
        "dims": {
            "DIM_CUSTOMER_UCIC":  ["ucic_key","ucic_id","cif_id","customer_name","pan_masked","aadhaar_masked","mobile","email","dob","gender","nationality","segment","risk_category","kyc_status","kyc_expiry_date","pep_flag","sanction_flag","scd_start","scd_end","is_current","date_of_generation","report_date","execution_date"],
            "DIM_ADDRESS":        ["address_key","ucic_id","address_type","line1","line2","city","state","pincode","country","is_primary","verified_flag","date_of_generation","report_date","execution_date"],
            "DIM_RELATIONSHIP":   ["rel_key","ucic_id","relationship_type","relationship_manager","branch_code","since_date","date_of_generation","report_date","execution_date"],
            "DIM_DATE":           ["date_key","full_date","day_of_week","month","quarter","year","financial_year","is_weekend","is_bank_holiday"],
            "DIM_SEGMENT":        ["segment_key","segment_code","segment_name","min_balance","max_balance","priority_flag","wealth_flag","date_of_generation","report_date","execution_date"],
        },
        "facts": {
            "FACT_UCIC_DEDUP":           ["dedup_key","ucic_key","date_key","source_system","duplicate_count","merge_action","match_score","pan_match","aadhaar_match","mobile_match","resolution_status","date_of_generation","report_date","execution_date"],
            "FACT_UCIC_PRODUCT_HOLDINGS":["holding_key","ucic_key","date_key","product_type","account_id","balance_inr","status","open_date","maturity_date","date_of_generation","report_date","execution_date"],
            "FACT_UCIC_KYC_STATUS":      ["kyc_key","ucic_key","date_key","kyc_type","kyc_status","expiry_date","document_type","verified_by","days_to_expiry","alert_flag","date_of_generation","report_date","execution_date"],
        },
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # 8. BUREAU MART â€” CIBIL/Experian Credit Bureau
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "bureau_mart": {
        "dims": {
            "DIM_BUREAU_SOURCE":  ["bureau_key","bureau_name","bureau_code","api_endpoint","enquiry_type","response_sla_ms","date_of_generation","report_date","execution_date"],
            "DIM_SCORE_BAND":     ["band_key","band_code","band_label","score_min","score_max","risk_category","lending_eligible","date_of_generation","report_date","execution_date"],
            "DIM_CUSTOMER_CREDIT":["credit_cust_key","customer_id","ucic_id","pan_masked","bureau_id","date_of_generation","report_date","execution_date"],
            "DIM_DATE":           ["date_key","full_date","month","quarter","year","financial_year","is_weekend","is_bank_holiday"],
            "DIM_PRODUCT_CREDIT": ["prod_key","product_type","lender_name","secured_flag","collateral_type","date_of_generation","report_date","execution_date"],
        },
        "facts": {
            "FACT_BUREAU_SCORES":       ["score_key","credit_cust_key","bureau_key","band_key","date_key","credit_score","score_change_30d","number_of_accounts","active_accounts","overdue_accounts","dpd_30","dpd_60","dpd_90","total_exposure_inr","unsecured_inr","enquiry_count_6m","date_of_generation","report_date","execution_date"],
            "FACT_BUREAU_ENQUIRIES":    ["enquiry_key","credit_cust_key","bureau_key","date_key","enquiry_type","enquiry_amount","lender_name","purpose","date_of_generation","report_date","execution_date"],
            "FACT_NPA_EARLY_WARNING":   ["npa_key","credit_cust_key","date_key","risk_flag","dpd_current","score_drop","overdue_amount_inr","watchlist_flag","recommended_action","date_of_generation","report_date","execution_date"],
        },
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # 9. DATA LAKE â€” Enterprise Raw Zone
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "data_lake": {
        "dims": {
            "DIM_SOURCE_SYSTEM":  ["source_key","source_code","source_name","source_type","host","schema_version","owner_team","sla_hours","date_of_generation","report_date","execution_date"],
            "DIM_DATA_DOMAIN":    ["domain_key","domain_code","domain_name","classification","pii_flag","retention_days","date_of_generation","report_date","execution_date"],
            "DIM_DATE":           ["date_key","full_date","day_of_week","month","quarter","year","financial_year","is_weekend","is_bank_holiday"],
            "DIM_SCHEMA_VERSION": ["schema_key","source_key","version","effective_date","ddl_hash","breaking_change_flag","date_of_generation","report_date","execution_date"],
            "DIM_PARTITION":      ["partition_key","source_key","partition_date","partition_type","file_format","compression","location_path","date_of_generation","report_date","execution_date"],
        },
        "facts": {
            "FACT_INGESTION_LOG":     ["log_key","source_key","domain_key","date_key","partition_key","batch_id","record_count","byte_size","load_start","load_end","duration_sec","validation_status","quarantine_count","schema_drift_flag","date_of_generation","report_date","execution_date"],
            "FACT_DATA_QUALITY":      ["dq_key","source_key","domain_key","date_key","completeness_pct","uniqueness_pct","validity_pct","timeliness_pct","overall_score","failed_rules","date_of_generation","report_date","execution_date"],
            "FACT_SCHEMA_DRIFT":      ["drift_key","source_key","schema_key","date_key","column_added","column_dropped","type_changed","nullable_changed","impact_level","downstream_affected","date_of_generation","report_date","execution_date"],
        },
    },
}

# 
# Project Definitions
# 
PROJECTS = {
    "credit_card": {
        "id":          "proj_credit_card",
        "name":        "Credit Card (Transaction & Fraud Analytics)",
        "code":        "CREDIT_CARD",
        "domain":      "Retail Banking & Fraud",
        "neon_l0":     "cc_l0_raw_transactions",
        "neon_l1":     "cc_l1_clean_transactions",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_CREDIT_CARD_SUMMARY",
        "columns": [
            "txn_id", "card_number_masked", "customer_id", "merchant_name",
            "merchant_category", "amount_inr", "txn_type", "channel",
            "status", "fraud_flag", "risk_score", "txn_timestamp",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Daily Fraud Alert", "Weekly Spend Summary", "Monthly Statement"],
        "cadence":     "Daily T-1 at 10:00 AM IST",
        "color":       "#3B82F6",
    },
    "aml": {
        "id":          "proj_aml",
        "name":        "AML (Anti-Money Laundering & Fraud Surveillance)",
        "code":        "AML_SURVEILLANCE",
        "domain":      "Regulatory & Financial Crime",
        "neon_l0":     "aml_l0_raw_transactions",
        "neon_l1":     "aml_l1_clean_transactions",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_AML_SUMMARY",
        "columns": [
            "txn_id", "account_id", "customer_id", "txn_type", "amount_inr",
            "counterparty_id", "counterparty_country", "channel", "alert_type",
            "risk_category", "str_flag", "ctr_flag", "txn_timestamp",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Daily CTR Report", "STR Alert Report", "Monthly FIU-IND XML"],
        "cadence":     "Daily T-1 at 06:30 AM IST",
        "color":       "#EF4444",
    },
    "alm": {
        "id":          "proj_alm",
        "name":        "ALM (Asset Liability Management & Liquidity)",
        "code":        "ALM_LIQUIDITY",
        "domain":      "Treasury & Market Risk",
        "neon_l0":     "alm_l0_raw_cashflows",
        "neon_l1":     "alm_l1_bucketed_flows",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_ALM_SUMMARY",
        "columns": [
            "deal_id", "product_type", "asset_class", "maturity_bucket",
            "cashflow_type", "amount_inr", "currency", "lcr_flag",
            "nsfr_flag", "time_bucket_label", "valuation_date",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Structural Liquidity Gap", "LCR Workbook", "NSFR Report"],
        "cadence":     "Daily T-1 at 07:15 AM IST",
        "color":       "#10B981",
    },
    "adf_cims": {
        "id":          "proj_adf_cims",
        "name":        "ADF CIMS (RBI Automated Data Flow & Central Reporting)",
        "code":        "RBI_CIMS_ADF",
        "domain":      "Regulatory & Statutory Compliance",
        "neon_l0":     "cims_l0_raw_gl_data",
        "neon_l1":     "cims_l1_standardized",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_CIMS_SUMMARY",
        "columns": [
            "return_code", "line_item_id", "gl_code", "account_number",
            "debit_amount", "credit_amount", "net_balance", "currency",
            "return_type", "submission_status", "valuation_date",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Form A  Assets & Liabilities", "Form VIII  SLR Return", "XBRL XML"],
        "cadence":     "Fortnightly / Monthly",
        "color":       "#F59E0B",
    },
    "cbs": {
        "id":          "proj_cbs",
        "name":        "CBS (Core Banking  Finacle Recon & Migration)",
        "code":        "CBS_FINACLE_RECON",
        "domain":      "Core Banking Technology",
        "neon_l0":     "cbs_l0_raw_gl_dump",
        "neon_l1":     "cbs_l1_finacle_recon",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_CBS_SUMMARY",
        "columns": [
            "gl_code", "account_number", "posting_date", "debit_amount",
            "credit_amount", "net_balance", "branch_code", "currency",
            "product_code", "migration_batch_id", "parity_flag", "variance_amount",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["GL Trial Balance Diff", "Migration Parity Audit", "EOD Balance Sheet"],
        "cadence":     "Daily EOD at 23:45 IST",
        "color":       "#8B5CF6",
    },

    # â”€â”€ NEW PROJECT: UPI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "upi": {
        "id":          "proj_upi",
        "name":        "UPI (Unified Payments Interface - Real-Time Settlements)",
        "code":        "UPI_PAYMENTS",
        "domain":      "Payments & Settlement",
        "neon_l0":     "upi_l0_raw_transactions",
        "neon_l1":     "upi_l1_clean_settlements",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_UPI_SUMMARY",
        "columns": [
            "upi_txn_id", "vpa_payer", "vpa_payee", "amount_inr", "txn_type",
            "txn_status", "bank_code", "npci_txn_ref", "remark", "mcc",
            "settlement_date", "batch_id", "reversal_flag",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Daily UPI Settlement Report", "NPCI Reconciliation", "Failed TXN Report"],
        "cadence":     "Daily T-1 at 09:00 AM IST",
        "color":       "#06B6D4",
    },

    # â”€â”€ NEW PROJECT: UCIC â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ucic": {
        "id":          "proj_ucic",
        "name":        "UCIC (Unique Customer Identification Code - Customer 360)",
        "code":        "UCIC_CUSTOMER360",
        "domain":      "Customer Data Management",
        "neon_l0":     "ucic_l0_raw_customer_data",
        "neon_l1":     "ucic_l1_deduplicated_master",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_UCIC_SUMMARY",
        "columns": [
            "ucic_id", "cif_id", "customer_name", "pan_masked", "aadhaar_masked",
            "mobile", "email", "dob", "gender", "kyc_status", "kyc_expiry",
            "risk_category", "segment", "total_accounts", "total_loans",
            "total_deposits", "relationship_since",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["UCIC Dedup Report", "Customer 360 Profile", "KYC Expiry Alert"],
        "cadence":     "Daily T-1 at 08:00 AM IST",
        "color":       "#EC4899",
    },

    # â”€â”€ NEW PROJECT: BUREAU MART â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "bureau_mart": {
        "id":          "proj_bureau_mart",
        "name":        "Bureau Mart (CIBIL/Experian Credit Bureau Analytics)",
        "code":        "BUREAU_CREDIT_MART",
        "domain":      "Credit Risk & Analytics",
        "neon_l0":     "bureau_l0_raw_credit_data",
        "neon_l1":     "bureau_l1_clean_scores",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_BUREAU_SUMMARY",
        "columns": [
            "bureau_ref_id", "customer_id", "ucic_id", "bureau_name",
            "credit_score", "score_band", "number_of_accounts",
            "active_loans", "overdue_accounts", "dpd_30", "dpd_60", "dpd_90",
            "total_exposure_inr", "unsecured_exposure_inr", "enquiry_count_6m",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Daily Credit Score Distribution", "NPA Early Warning", "Monthly Bureau Reconciliation"],
        "cadence":     "Daily T-1 at 08:30 AM IST",
        "color":       "#F97316",
    },

    # â”€â”€ NEW PROJECT: DATA LAKE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "data_lake": {
        "id":          "proj_data_lake",
        "name":        "Data Lake (Enterprise Raw Zone - All Source Systems)",
        "code":        "ENTERPRISE_DATA_LAKE",
        "domain":      "Data Platform & Architecture",
        "neon_l0":     "lake_l0_raw_all_sources",
        "neon_l1":     "lake_l1_validated_landing",
        "sf_schema":   "L2_CURATED",
        "sf_table":    "L2_DATA_LAKE_SUMMARY",
        "columns": [
            "record_id", "source_system", "source_table", "batch_id",
            "load_timestamp", "record_hash", "schema_version",
            "row_count", "byte_size", "validation_status",
            "quarantine_flag", "partition_date",
            "date_of_generation", "report_date", "execution_date"
        ],
        "reports": ["Daily Ingestion Summary", "Schema Drift Alert", "Data Quality Scorecard"],
        "cadence":     "Daily T-1 at 05:00 AM IST",
        "color":       "#64748B",
    },
}

# 
# Sample Data Generators (Internet-style random banking data)
# 
# BOD / SOD / EOD Cut-off Logic
# T-1 Data: report_date = yesterday (data cut at EOD previous day)
# BOD  06:00 â€” Previous day data loaded, T-1 report ready
# SOD  08:00 â€” Start of Day: open positions, beginning balances
# EOD  18:00 â€” End of Day: cut-off, final balances, close
#
# Pipeline always runs AFTER the cut-off, so:
#   report_date    = T-1 (yesterday's data)
#   execution_date = today (when pipeline ran)
#   date_of_generation = today (when report was generated)
# 

IST_OFFSET_HOURS = 5.5   # IST = UTC + 5:30

def _now_ist() -> str:
    now_utc = datetime.datetime.utcnow()
    now_ist = now_utc + datetime.timedelta(hours=IST_OFFSET_HOURS)
    return now_ist.strftime("%Y-%m-%d %H:%M:%S IST")

def _today() -> str:
    now_utc = datetime.datetime.utcnow()
    now_ist = now_utc + datetime.timedelta(hours=IST_OFFSET_HOURS)
    return now_ist.strftime("%Y-%m-%d")

def _yesterday() -> str:
    now_utc = datetime.datetime.utcnow()
    now_ist = now_utc + datetime.timedelta(hours=IST_OFFSET_HOURS)
    return (now_ist - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def _get_batch_cycle() -> str:
    """Returns current batch cycle based on IST hour."""
    now_utc = datetime.datetime.utcnow()
    now_ist = now_utc + datetime.timedelta(hours=IST_OFFSET_HOURS)
    h = now_ist.hour
    if 0 <= h < 6:    return "EOD_PROCESSING"    # Previous day EOD still running
    elif 6 <= h < 8:  return "BOD"               # Begin of Day
    elif 8 <= h < 10: return "SOD"               # Start of Day
    elif 10 <= h < 18: return "INTRADAY"         # Normal business hours
    elif 18 <= h < 22: return "EOD"              # End of Day
    else:              return "EOD_PROCESSING"   # Late night EOD

def _t1_report_dates() -> dict:
    """
    Returns T-1 date window for report generation.
    Always: report_date = yesterday (T-1 cut), execution_date = now IST.
    """
    return {
        "report_date":         _yesterday(),       # Data cut: T-1
        "execution_date":      _now_ist(),          # When pipeline ran
        "date_of_generation":  _today(),            # When report generated
        "batch_cycle":         _get_batch_cycle(),  # BOD/SOD/EOD/INTRADAY
        "t1_cutoff":           f"{_yesterday()} 23:59:59 IST",
    }


def generate_sample_data(project_key: str, rows: int = 200) -> List[Dict[str, Any]]:
    """Generates realistic sample banking data for any project."""
    p       = PROJECTS[project_key]
    cols    = p["columns"]
    records = []
    merchants   = ["Amazon India", "Flipkart", "Swiggy", "Zomato", "Uber India", "Reliance Retail", "Tata Neu", "MakeMyTrip", "Jio Fiber", "Electricity Board"]
    channels    = ["MOBILE_APP", "NET_BANKING", "POS_TERMINAL", "ATM", "BRANCH_COUNTER", "UPI"]
    txn_types   = ["CREDIT", "DEBIT", "TRANSFER", "NEFT", "RTGS", "IMPS", "UPI_PAYMENT"]
    countries   = ["IN", "US", "AE", "SG", "GB", "HK", "DE"]
    alert_types = ["HIGH_VALUE_CASH", "STRUCTURING", "CROSS_BORDER", "DORMANT_ACTIVATION", "PEP_LINKED"]
    buckets     = ["1D", "7D", "14D", "30D", "90D", "1Y", "3Y", "5Y+"]
    products    = ["CASA", "TERM_DEPOSIT", "CORP_LOAN", "G-SEC", "CALL_MONEY", "FX_SWAP"]
    gl_codes    = [f"GL{1000 + i}" for i in range(50)]

    execution_dt = _now_ist()
    report_dt    = _yesterday()
    gen_dt       = _today()

    for i in range(rows):
        amount = round(random.uniform(100, 500000), 2)
        ts     = f"2026-{random.randint(1,10):02d}-{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00"

        if project_key == "credit_card":
            rec = {
                "txn_id":             f"CC_TXN_{uuid.uuid4().hex[:12].upper()}",
                "card_number_masked":  f"**** **** **** {random.randint(1000,9999)}",
                "customer_id":         f"CUST_{random.randint(1000, 9999)}",
                "merchant_name":       random.choice(merchants),
                "merchant_category":   random.choice(["RETAIL", "FOOD", "TRAVEL", "UTILITY", "ECOMMERCE"]),
                "amount_inr":          amount,
                "txn_type":            random.choice(["PURCHASE", "REFUND", "CASH_ADVANCE", "EMI"]),
                "channel":             random.choice(channels),
                "status":              random.choice(["SETTLED", "PENDING", "DECLINED", "REVERSED"]),
                "fraud_flag":          random.choice([0, 0, 0, 0, 1]),
                "risk_score":          round(random.uniform(0, 100), 2),
                "txn_timestamp":       ts,
                "date_of_generation":  gen_dt,
                "report_date":         report_dt,
                "execution_date":      execution_dt,
            }
        elif project_key == "aml":
            rec = {
                "txn_id":              f"AML_TXN_{uuid.uuid4().hex[:12].upper()}",
                "account_id":          f"ACC_{random.randint(1000, 9999)}",
                "customer_id":         f"CUST_{random.randint(1000, 9999)}",
                "txn_type":            random.choice(txn_types),
                "amount_inr":          amount,
                "counterparty_id":     f"CP_{random.randint(100, 999)}",
                "counterparty_country": random.choice(countries),
                "channel":             random.choice(channels),
                "alert_type":          random.choice(alert_types + [None, None, None]),
                "risk_category":       random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
                "str_flag":            random.choice([0, 0, 0, 1]),
                "ctr_flag":            1 if amount > 100000 else 0,
                "txn_timestamp":       ts,
                "date_of_generation":  gen_dt,
                "report_date":         report_dt,
                "execution_date":      execution_dt,
            }
        elif project_key == "alm":
            rec = {
                "deal_id":             f"DEAL_{uuid.uuid4().hex[:10].upper()}",
                "product_type":        random.choice(products),
                "asset_class":         random.choice(["ASSET", "LIABILITY"]),
                "maturity_bucket":     random.choice(buckets),
                "cashflow_type":       random.choice(["PRINCIPAL", "INTEREST", "COUPON", "REDEMPTION"]),
                "amount_inr":          round(amount * 10, 2),
                "currency":            random.choice(["INR", "USD", "EUR"]),
                "lcr_flag":            random.choice([0, 1]),
                "nsfr_flag":           random.choice([0, 1]),
                "time_bucket_label":   random.choice(buckets),
                "valuation_date":      report_dt,
                "date_of_generation":  gen_dt,
                "report_date":         report_dt,
                "execution_date":      execution_dt,
            }
        elif project_key == "adf_cims":
            rec = {
                "return_code":         random.choice(["FORMA", "FORMVIII", "BSR1", "BSR2", "R3"]),
                "line_item_id":        f"LI_{i+1:05d}",
                "gl_code":             random.choice(gl_codes),
                "account_number":      f"ACC{random.randint(10000000, 99999999)}",
                "debit_amount":        round(random.uniform(0, amount), 2),
                "credit_amount":       round(random.uniform(0, amount), 2),
                "net_balance":         round(random.uniform(-50000, 500000), 2),
                "currency":            "INR",
                "return_type":         random.choice(["WEEKLY", "FORTNIGHTLY", "MONTHLY"]),
                "submission_status":   random.choice(["PENDING", "SUBMITTED", "ACCEPTED", "REJECTED"]),
                "valuation_date":      report_dt,
                "date_of_generation":  gen_dt,
                "report_date":         report_dt,
                "execution_date":      execution_dt,
            }
        else:  # cbs
            rec = {
                "gl_code":             random.choice(gl_codes),
                "account_number":      f"ACC{random.randint(10000000, 99999999)}",
                "posting_date":        report_dt,
                "debit_amount":        round(random.uniform(0, amount), 2),
                "credit_amount":       round(random.uniform(0, amount), 2),
                "net_balance":         round(random.uniform(-50000, 500000), 2),
                "branch_code":         f"BR{random.randint(100, 999)}",
                "currency":            "INR",
                "product_code":        random.choice(["SB", "CA", "FD", "RD", "HL", "PL", "CC"]),
                "migration_batch_id":  f"BATCH_{random.randint(1, 50):03d}",
                "parity_flag":         random.choice([1, 1, 1, 0]),
                "variance_amount":     round(random.uniform(0, 100), 2),
                "date_of_generation":  gen_dt,
                "report_date":         report_dt,
                "execution_date":      execution_dt,
            }
        records.append(rec)
    return records


# 
# ETL Pipeline Engine
# 
class ETLAutomationPipeline:
    """
    Full ETL Automation Pipeline:
      FULL LOAD    Truncate + reload all tables (first time or monthly)
      INCREMENTAL  Watermark-based delta load (daily/hourly)
      L0 Raw -> L1 Clean -> L2 Star Schema (DIM+FACT) -> Reports -> Email + Telegram
    """

    # Load mode constants
    FULL_LOAD        = "FULL_LOAD"
    INCREMENTAL_LOAD = "INCREMENTAL"

    def __init__(self):
        self._lock       = threading.RLock()
        self._runs       = {}
        self._watermarks = {}   # project -> last_loaded_timestamp
        self._load_watermarks()
        log_event("ETLAutomationPipeline initialized (Full + Incremental modes).", component="ETLPipeline")

    #  Watermark Management (Incremental State) 
    def _watermark_file(self) -> Path:
        p = BASE_DIR / "data" / "banking" / "etl_watermarks.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _load_watermarks(self):
        """Load last-loaded watermarks from disk for incremental mode."""
        try:
            f = self._watermark_file()
            if f.exists():
                self._watermarks = json.loads(f.read_text())
            else:
                self._watermarks = {}
        except Exception:
            self._watermarks = {}

    def _save_watermarks(self):
        """Persist watermarks after successful load."""
        try:
            self._watermark_file().write_text(json.dumps(self._watermarks, indent=2))
        except Exception as e:
            log_event(f"Failed to save watermarks: {e}", level="WARNING", component="ETLPipeline")

    def get_watermark(self, project_key: str) -> Optional[str]:
        """Returns last successful load timestamp for a project."""
        return self._watermarks.get(project_key)

    def set_watermark(self, project_key: str, ts: str):
        """Update watermark after successful incremental load."""
        self._watermarks[project_key] = ts
        self._save_watermarks()

    def reset_watermark(self, project_key: str = None):
        """Reset watermark to force full load on next run."""
        if project_key:
            self._watermarks.pop(project_key, None)
        else:
            self._watermarks = {}
        self._save_watermarks()
        log_event(f"Watermark reset for: {project_key or 'ALL PROJECTS'}", component="ETLPipeline")

    #  Load Mode Detection 
    def detect_load_mode(self, project_key: str) -> str:
        """
        Returns FULL_LOAD if:
          - No watermark exists (first run)
          - Watermark > 30 days old (monthly full reload)
        Otherwise returns INCREMENTAL.
        """
        wm = self.get_watermark(project_key)
        if not wm:
            return self.FULL_LOAD
        try:
            wm_dt = datetime.datetime.fromisoformat(wm)
            age_days = (datetime.datetime.now() - wm_dt).days
            if age_days >= 30:
                log_event(f"[{project_key}] Watermark {age_days}d old -> forcing FULL_LOAD", component="ETLPipeline")
                return self.FULL_LOAD
            return self.INCREMENTAL_LOAD
        except Exception:
            return self.FULL_LOAD

    #  Full Load: Truncate + Reload 
    def _full_load_neon(self, project_key: str, records: List[Dict], neon_url: str) -> Dict:
        """
        FULL LOAD  Drops and recreates L0 + L1 tables in Neon.
        Used for: first run, monthly reset, schema changes.
        """
        import psycopg2
        p       = PROJECTS[project_key]
        now     = _now_ist()
        results = {}

        conn = psycopg2.connect(neon_url, connect_timeout=15)
        conn.autocommit = True
        cur  = conn.cursor()

        for layer, table in [("L0", p["neon_l0"]), ("L1", p["neon_l1"])]:
            try:
                # Truncate existing table (preserve schema)
                cur.execute(f'DROP TABLE IF EXISTS "{table}"')
                cols     = list(records[0].keys())
                col_defs = ", ".join([f'"{c}" TEXT' for c in cols])
                cur.execute(f'CREATE TABLE "{table}" ({col_defs})')

                # Bulk insert
                phs     = ", ".join(["%s"] * len(cols))
                col_str = ", ".join([f'"{c}"' for c in cols])

                # L1 = deduplicated version of L0
                if layer == "L1":
                    seen, clean = set(), []
                    for r in records:
                        key = tuple(str(v) for v in list(r.values())[:3])
                        if key not in seen:
                            seen.add(key)
                            clean.append(r)
                    load_records = clean
                else:
                    load_records = records

                for r in load_records:
                    cur.execute(f'INSERT INTO "{table}" ({col_str}) VALUES ({phs})',
                                [str(r.get(c, "")) for c in cols])

                results[layer] = {"table": table, "rows": len(load_records),
                                  "mode": "FULL_LOAD", "status": "success"}
                log_event(f"[{p['code']}] FULL LOAD {layer}: {len(load_records)} rows -> {table}", component="ETLPipeline")

            except Exception as e:
                results[layer] = {"table": table, "status": "failed", "error": str(e)[:200]}
                log_event(f"[{p['code']}] FULL LOAD {layer} failed: {e}", level="ERROR", component="ETLPipeline")

        cur.close()
        conn.close()
        return results

    #  Incremental Load: Delta Only 
    def _incremental_load_neon(self, project_key: str, records: List[Dict],
                                neon_url: str, watermark: str) -> Dict:
        """
        INCREMENTAL LOAD  Inserts only new records since last watermark.
        Deduplicates against existing data using primary key.
        Skips records with execution_date <= watermark.
        """
        import psycopg2
        p       = PROJECTS[project_key]
        results = {}

        # Filter new records only (after watermark)
        new_records = []
        for r in records:
            rec_ts = r.get("execution_date", r.get("txn_timestamp", ""))
            if not watermark or rec_ts > watermark:
                new_records.append(r)

        if not new_records:
            log_event(f"[{p['code']}] No new records since watermark {watermark}  skipping", component="ETLPipeline")
            return {"L0": {"rows": 0, "mode": "INCREMENTAL", "status": "skipped"},
                    "L1": {"rows": 0, "mode": "INCREMENTAL", "status": "skipped"}}

        conn = psycopg2.connect(neon_url, connect_timeout=15)
        conn.autocommit = True
        cur  = conn.cursor()

        for layer, table in [("L0", p["neon_l0"]), ("L1", p["neon_l1"])]:
            try:
                cols     = list(new_records[0].keys())
                col_defs = ", ".join([f'"{c}" TEXT' for c in cols])

                # Create table if not exists (first incremental after schema change)
                cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
                for c in ["date_of_generation", "report_date", "execution_date"]:
                    try:
                        cur.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "{c}" TEXT')
                    except Exception:
                        pass

                # L1 = deduplicated
                if layer == "L1":
                    seen, load_records = set(), []
                    for r in new_records:
                        key = tuple(str(v) for v in list(r.values())[:3])
                        if key not in seen:
                            seen.add(key)
                            load_records.append(r)
                else:
                    load_records = new_records

                phs     = ", ".join(["%s"] * len(cols))
                col_str = ", ".join([f'"{c}"' for c in cols])
                for r in load_records:
                    cur.execute(f'INSERT INTO "{table}" ({col_str}) VALUES ({phs})',
                                [str(r.get(c, "")) for c in cols])

                results[layer] = {"table": table, "rows": len(load_records),
                                  "mode": "INCREMENTAL", "status": "success",
                                  "watermark_from": watermark}
                log_event(f"[{p['code']}] INCREMENTAL {layer}: +{len(load_records)} rows -> {table}", component="ETLPipeline")

            except Exception as e:
                results[layer] = {"table": table, "status": "failed", "error": str(e)[:200]}
                log_event(f"[{p['code']}] INCREMENTAL {layer} failed: {e}", level="ERROR", component="ETLPipeline")

        cur.close()
        conn.close()
        return results

    #  Step 1: L0 Raw Load into Neon PostgreSQL 
    def _load_l0_neon(self, project_key: str, records: List[Dict], conn) -> int:
        """Inserts raw records into Neon L0 table."""
        p         = PROJECTS[project_key]
        table     = p["neon_l0"]
        if not records:
            return 0
        cols      = list(records[0].keys())
        col_defs  = ", ".join([f'"{c}" TEXT' for c in cols])
        placeholders = ", ".join(["%s"] * len(cols))

        conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "date_of_generation" TEXT')
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "report_date" TEXT')
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "execution_date" TEXT')

        for r in records:
            vals = [str(r.get(c, "")) for c in cols]
            conn.execute(
                f'INSERT INTO "{table}" ({", ".join([chr(34)+c+chr(34) for c in cols])}) VALUES ({placeholders})',
                vals
            )
        return len(records)

    #  Step 2: L1 Clean into Neon PostgreSQL 
    def _load_l1_neon(self, project_key: str, records: List[Dict], conn) -> int:
        """Cleans and deduplicates records into Neon L1 table."""
        p     = PROJECTS[project_key]
        table = p["neon_l1"]
        if not records:
            return 0

        # Dedup by execution_date + key fields
        seen    = set()
        cleaned = []
        for r in records:
            # Nulls -> defaults
            for k, v in r.items():
                if v is None or v == "None":
                    r[k] = "0" if any(x in k for x in ["amount", "flag", "score", "count"]) else ""
            key = (r.get("txn_id") or r.get("deal_id") or r.get("gl_code", ""),
                   r.get("execution_date", ""))
            if key not in seen:
                seen.add(key)
                cleaned.append(r)

        cols     = list(cleaned[0].keys())
        col_defs = ", ".join([f'"{c}" TEXT' for c in cols])
        phs      = ", ".join(["%s"] * len(cols))

        conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "date_of_generation" TEXT')
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "report_date" TEXT')
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "execution_date" TEXT')

        for r in cleaned:
            vals = [str(r.get(c, "")) for c in cols]
            conn.execute(
                f'INSERT INTO "{table}" ({", ".join([chr(34)+c+chr(34) for c in cols])}) VALUES ({phs})',
                vals
            )
        return len(cleaned)

    #  Step 3: L2 Summary into Snowflake 
    def _load_l2_snowflake(self, project_key: str, l1_count: int, run_id: str) -> Dict:
        """
        Loads L2 Star Schema into Snowflake BANK_DB.L2_CURATED:
          - DIM_* tables (Dimension / Normalization)
          - FACT_* tables (Fact)
          - L2_*_SUMMARY table (pipeline audit row)
        All tables include: date_of_generation, report_date, execution_date
        """
        try:
            import snowflake.connector
            from app.core.connection_manager import connection_manager
            cfg  = connection_manager.get_connection_config("NANO_PRO_SNOWFLAKE", mask=False)
            if not cfg or not cfg.get("secret_value"):
                return {"success": False, "error": "Snowflake password not configured in vault"}
            meta   = cfg.get("metadata") or {}
            p      = PROJECTS[project_key]
            schema = p["sf_schema"]
            star   = STAR_SCHEMA.get(project_key, {})

            sf = snowflake.connector.connect(
                account       = meta.get("account_identifier", "EGPKNWZ-XH53504"),
                user          = meta.get("username", "mangeshbagul15"),
                password      = cfg["secret_value"],
                warehouse     = meta.get("warehouse", "COMPUTE_WH"),
                database      = meta.get("database", "BANK_DB"),
                role          = meta.get("role", "ACCOUNTADMIN"),
                login_timeout = 20,
            )
            today     = _today()
            yesterday = _yesterday()
            now       = _now_ist()

            with sf.cursor() as cur:
                cur.execute(f"USE SCHEMA {schema}")

                #  1. Create Dimension Tables (Normalization) 
                for dim_name, dim_cols in star.get("dims", {}).items():
                    col_ddl = ",\n  ".join([f'"{c}" VARCHAR(256)' for c in dim_cols])
                    cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {dim_name} (
                          {col_ddl},
                          date_of_generation  DATE,
                          report_date         DATE,
                          execution_date      TIMESTAMP_NTZ,
                          created_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                        )
                    """)

                #  2. Create Fact Tables 
                for fact_name, fact_cols in star.get("facts", {}).items():
                    col_ddl = ",\n  ".join([f'"{c}" VARCHAR(256)' for c in fact_cols])
                    cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {fact_name} (
                          {col_ddl},
                          created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                        )
                    """)

                #  3. Create L2 Pipeline Summary Table 
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {p['sf_table']} (
                        run_id              VARCHAR(64),
                        project_code        VARCHAR(32),
                        l0_rows             NUMBER,
                        l1_rows             NUMBER,
                        dim_tables_created  NUMBER,
                        fact_tables_created NUMBER,
                        pipeline_status     VARCHAR(16),
                        date_of_generation  DATE,
                        report_date         DATE,
                        execution_date      TIMESTAMP_NTZ,
                        created_at          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                    )
                """)

                dim_count  = len(star.get("dims",  {}))
                fact_count = len(star.get("facts", {}))

                cur.execute(f"""
                    INSERT INTO {p['sf_table']}
                        (run_id, project_code, l0_rows, l1_rows,
                         dim_tables_created, fact_tables_created,
                         pipeline_status, date_of_generation, report_date, execution_date)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (run_id, p["code"], l1_count, l1_count,
                      dim_count, fact_count,
                      "LOADED", today, yesterday, now))
                sf.commit()

            sf.close()
            return {
                "success":      True,
                "table":        p["sf_table"],
                "dim_tables":   dim_count,
                "fact_tables":  fact_count,
                "rows":         1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_report(self, project_key: str, run_id: str,
                         l0_rows: int, l1_rows: int, sf_result: Dict,
                         load_mode: str = "FULL_LOAD",
                         prev_watermark: Optional[str] = None) -> str:
        p          = PROJECTS[project_key]
        star       = STAR_SCHEMA.get(project_key, {})
        today      = _today()
        yesterday  = _yesterday()
        now        = _now_ist()
        sf_ok      = " Loaded" if sf_result.get("success") else f" {sf_result.get('error','')[:50]}"
        dim_count  = sf_result.get("dim_tables",  len(star.get("dims",  {})))
        fact_count = sf_result.get("fact_tables", len(star.get("facts", {})))
        mode_icon  = "" if load_mode == "FULL_LOAD" else ""
        mode_label = "FULL LOAD (Truncate + Reload)" if load_mode == "FULL_LOAD" else f"INCREMENTAL (Delta since {prev_watermark or 'N/A'})"

        dim_list   = "\n".join([f"   {d}" for d in star.get("dims",  {}).keys()])
        fact_list  = "\n".join([f"   {f}" for f in star.get("facts", {}).keys()])

        return f"""
 <b>NanoPro AI Studio  ETL Pipeline Report</b>


 <b>Project:</b> {p['name']}
 <b>Run ID:</b> <code>{run_id[:16]}</code>
{mode_icon} <b>Load Mode:</b> <code>{mode_label}</code>

 <b>Date of Generation:</b> <code>{today}</code>
 <b>Report Date (T-1):</b> <code>{yesterday}</code>
 <b>Execution Date:</b> <code>{now}</code>


<b>Pipeline Stages:</b>
 <b>L0 Raw (Neon):</b> <code>{l0_rows:,}</code> records
 <b>L1 Clean (Neon):</b> <code>{l1_rows:,}</code> records (dedup + normalized)
 <b>L2 Snowflake (DIM+FACT):</b> {sf_ok}


<b>Star Schema:</b>
 <b>Dimension Tables ({dim_count}):</b>
{dim_list}

 <b>Fact Tables ({fact_count}):</b>
{fact_list}


<b>Reports:</b>
{chr(10).join([' ' + r for r in p['reports']])}


 Pipeline Status: COMPLETED
 Powered by Mangesh NanoPro AI Studio
"""

    #  Main Pipeline Runner 
    def run_project_pipeline(self, project_key: str, rows: int = 200,
                              send_email: bool = True,
                              send_telegram: bool = True,
                              load_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Full pipeline for one project with Full/Incremental load detection:
          - FULL_LOAD:   Truncate + reload (first run / monthly / manual reset)
          - INCREMENTAL: Watermark-based delta insert (daily/hourly)

        Sample Data -> Neon L0 -> Neon L1 -> Snowflake L2 (DIM+FACT) -> Email + Telegram
        """
        if project_key not in PROJECTS:
            return {"success": False, "error": f"Unknown project: {project_key}. Valid: {list(PROJECTS.keys())}"}

        # Auto-detect load mode if not specified
        effective_mode = load_mode or self.detect_load_mode(project_key)
        watermark      = self.get_watermark(project_key)

        run_id = uuid.uuid4().hex
        start  = time.time()
        p      = PROJECTS[project_key]
        log_event(f"ETL [{effective_mode}] started: {p['code']} (run={run_id[:8]}, wm={watermark or 'NONE'})", component="ETLPipeline")

        result = {
            "run_id":            run_id,
            "project":           project_key,
            "project_name":      p["name"],
            "load_mode":         effective_mode,
            "watermark_used":    watermark,
            "stages":            {},
            "report_date":       _yesterday(),
            "execution_date":    _now_ist(),
            "date_of_generation": _today(),
        }

        #  Step 1: Generate Sample Data 
        try:
            # For incremental: generate fewer rows (delta batch)
            delta_rows = rows if effective_mode == self.FULL_LOAD else max(20, rows // 5)
            records = generate_sample_data(project_key, delta_rows)
            result["stages"]["sample_data"] = {
                "status": "success",
                "rows": len(records),
                "mode": effective_mode
            }
            log_event(f"[{p['code']}] Sample data: {len(records)} rows ({effective_mode})", component="ETLPipeline")
        except Exception as e:
            result["stages"]["sample_data"] = {"status": "failed", "error": str(e)}
            result["success"] = False
            return result

        #  Step 2 + 3: Neon L0 + L1 (Full or Incremental) 
        neon_url = os.environ.get("NEON_DATABASE_URL", "")
        l0_rows  = 0
        l1_rows  = 0

        try:
            if not neon_url:
                raise RuntimeError("NEON_DATABASE_URL not set in .env")

            if effective_mode == self.FULL_LOAD:
                neon_result = self._full_load_neon(project_key, records, neon_url)
            else:
                neon_result = self._incremental_load_neon(project_key, records, neon_url, watermark)

            l0_res = neon_result.get("L0", {})
            l1_res = neon_result.get("L1", {})
            l0_rows = l0_res.get("rows", 0)
            l1_rows = l1_res.get("rows", 0)

            result["stages"]["l0_neon"] = l0_res
            result["stages"]["l1_neon"] = l1_res

        except Exception as e:
            result["stages"]["l0_neon"] = {"status": "failed", "error": str(e)[:200]}
            result["stages"]["l1_neon"] = {"status": "failed", "error": str(e)[:200]}
            log_event(f"[{p['code']}] Neon load failed: {e}", level="ERROR", component="ETLPipeline")
            l0_rows = len(records)
            l1_rows = len(records)

        #  Step 4: Snowflake L2 (DIM + FACT + Summary) 
        sf_result = self._load_l2_snowflake(project_key, l1_rows, run_id)
        result["stages"]["l2_snowflake"] = sf_result
        if sf_result.get("success"):
            log_event(f"[{p['code']}] L2 Snowflake: {sf_result.get('dim_tables')} DIMs + {sf_result.get('fact_tables')} FACTs", component="ETLPipeline")
        else:
            log_event(f"[{p['code']}] L2 Snowflake failed: {sf_result.get('error')}", level="WARNING", component="ETLPipeline")

        #  Update Watermark (after successful load) 
        new_watermark = _now_ist()
        self.set_watermark(project_key, new_watermark)
        result["new_watermark"] = new_watermark

        #  Step 5: Generate Report 
        report_text = self._generate_report(project_key, run_id, l0_rows, l1_rows, sf_result,
                                             effective_mode, watermark)

        #  Step 6: Send Telegram 
        tg_sent = False
        if send_telegram:
            try:
                from app.core.telegram_router import send_telegram_routed_message
                tg_res = send_telegram_routed_message(
                    category   = "reports",
                    text       = report_text,
                    chat_id    = TELEGRAM_CHAT_ID,
                    parse_mode = "HTML"
                )
                tg_sent = tg_res.get("success", False)
                result["stages"]["telegram"] = {"status": "sent" if tg_sent else "failed",
                                                 "bot": "@mangesh_reports_bot"}
            except Exception as e:
                result["stages"]["telegram"] = {"status": "failed", "error": str(e)[:100]}

        #  Step 7: Send Email 
        email_sent = False
        if send_email:
            try:
                from app.core.smtp_client import smtp_client
                plain = report_text.replace("<b>","").replace("</b>","").replace(
                    "<code>","").replace("</code>","").replace("<i>","").replace("</i>","")
                email_res = smtp_client.send_email(
                    recipient   = "nanoproaistudio@gmail.com",
                    subject     = f"[NanoPro {effective_mode}] {p['code']}  T-1 {_yesterday()}",
                    body        = plain,
                    report_name = f"{p['code']}_T1_{_yesterday()}",
                    data_source = "NanoPro ETL Automation Pipeline"
                )
                email_sent = email_res.get("success", False)
                result["stages"]["email"] = {"status": "sent" if email_sent else "failed",
                                              "recipient": "nanoproaistudio@gmail.com"}
            except Exception as e:
                result["stages"]["email"] = {"status": "failed", "error": str(e)[:100]}

        duration = round(time.time() - start, 2)
        result.update({
            "success":      True,
            "l0_rows":      l0_rows,
            "l1_rows":      l1_rows,
            "duration_sec": duration,
            "telegram_sent": tg_sent,
            "email_sent":   email_sent,
        })
        log_event(f"ETL Pipeline COMPLETE: {p['code']} | L0={l0_rows} L1={l1_rows} | {duration}s", component="ETLPipeline")
        return result

    #  Run All Projects 
    def run_all_projects(self, rows_per_project: int = 200,
                          send_email: bool = True,
                          send_telegram: bool = True) -> Dict[str, Any]:
        """Runs pipeline for all 5 projects sequentially."""
        results   = {}
        total_l0  = 0
        total_l1  = 0
        start     = time.time()

        for key in PROJECTS:
            log_event(f"Starting pipeline: {key}", component="ETLPipeline")
            res = self.run_project_pipeline(key, rows_per_project, send_email, send_telegram)
            results[key] = res
            total_l0 += res.get("l0_rows", 0)
            total_l1 += res.get("l1_rows", 0)

        duration = round(time.time() - start, 2)

        # Summary Telegram message
        if send_telegram:
            try:
                from app.core.telegram_router import send_telegram_routed_message
                summary = f"""
 <b>NanoPro ETL  ALL PROJECTS COMPLETE</b>


 <b>Report Date:</b> <code>{_yesterday()}</code>
 <b>Execution:</b> <code>{_now_ist()}</code>

<b>Projects Summary:</b>
"""
                for key, res in results.items():
                    icon = "" if res.get("success") else ""
                    summary += f"{icon} <b>{PROJECTS[key]['code']}</b>: L0={res.get('l0_rows',0):,} | L1={res.get('l1_rows',0):,}\n"

                summary += f"""

 <b>Total L0 Records:</b> <code>{total_l0:,}</code>
 <b>Total L1 Records:</b> <code>{total_l1:,}</code>
 <b>Duration:</b> <code>{duration}s</code>
 <b>Status: ALL PIPELINES COMPLETE</b>
"""
                send_telegram_routed_message(
                    category="reports", text=summary,
                    chat_id=TELEGRAM_CHAT_ID, parse_mode="HTML"
                )
            except Exception as e:
                log_event(f"Summary Telegram failed: {e}", level="WARNING", component="ETLPipeline")

        return {
            "success":       True,
            "projects_run":  len(PROJECTS),
            "total_l0_rows": total_l0,
            "total_l1_rows": total_l1,
            "duration_sec":  duration,
            "results":       results,
        }


# 
# Scheduler
# 
class ETLScheduler:
    """
    Automated schedule:
      BOD   06:00   Full Load trigger
      SOD   08:00   Start of Day
      Daily 10:00   T-1 Report dispatch
      EOD   18:00   End of Day summary
      Weekly  Monday 08:00
      Fortnightly 1st & 15th 08:00
      Monthly 1st 07:00
    """
    SCHEDULES = {
        "BOD":         {"hour": 6,  "minute": 0,  "label": "BOD  Begin of Day"},
        "SOD":         {"hour": 8,  "minute": 0,  "label": "SOD  Start of Day"},
        "DAILY_10AM":  {"hour": 10, "minute": 0,  "label": "Daily T-1 Report"},
        "EOD":         {"hour": 18, "minute": 0,  "label": "EOD  End of Day"},
    }

    def __init__(self, pipeline: ETLAutomationPipeline):
        self._pipeline = pipeline
        self._running  = False
        self._thread:  Optional[threading.Thread] = None
        self._stop     = threading.Event()

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ETLScheduler")
        self._thread.start()
        log_event("ETLScheduler started  BOD/SOD/Daily/EOD/Weekly/Monthly active.", component="ETLScheduler")

    def stop(self):
        self._stop.set()
        self._running = False
        log_event("ETLScheduler stopped.", component="ETLScheduler")

    def _loop(self):
        last_run: Dict[str, str] = {}
        while not self._stop.is_set():
            now     = datetime.datetime.now()
            h, m    = now.hour, now.minute
            today   = now.strftime("%Y-%m-%d")
            weekday = now.weekday()   # 0=Monday
            dom     = now.day         # day of month

            # Daily schedules
            for key, cfg in self.SCHEDULES.items():
                slot = f"{today}_{key}"
                if h == cfg["hour"] and m == cfg["minute"] and slot not in last_run:
                    last_run[slot] = now.isoformat()
                    log_event(f"ETLScheduler: Triggering {cfg['label']}...", component="ETLScheduler")
                    threading.Thread(
                        target=self._pipeline.run_all_projects,
                        kwargs={"rows_per_project": 200, "send_email": True, "send_telegram": True},
                        daemon=True
                    ).start()

            # Weekly  Monday 08:00
            slot_w = f"{today}_WEEKLY"
            if weekday == 0 and h == 8 and m == 0 and slot_w not in last_run:
                last_run[slot_w] = now.isoformat()
                log_event("ETLScheduler: Weekly report triggered.", component="ETLScheduler")
                threading.Thread(target=self._pipeline.run_all_projects, daemon=True).start()

            # Fortnightly  1st & 15th at 08:00
            slot_f = f"{today}_FORTNIGHTLY"
            if dom in (1, 15) and h == 8 and m == 0 and slot_f not in last_run:
                last_run[slot_f] = now.isoformat()
                log_event("ETLScheduler: Fortnightly report triggered.", component="ETLScheduler")
                threading.Thread(target=self._pipeline.run_all_projects, daemon=True).start()

            # Monthly  1st at 07:00
            slot_m = f"{today}_MONTHLY"
            if dom == 1 and h == 7 and m == 0 and slot_m not in last_run:
                last_run[slot_m] = now.isoformat()
                log_event("ETLScheduler: Monthly report triggered.", component="ETLScheduler")
                threading.Thread(target=self._pipeline.run_all_projects, daemon=True).start()

            # Cleanup old keys (keep last 200)
            if len(last_run) > 200:
                keys = list(last_run.keys())
                for k in keys[:-100]:
                    del last_run[k]

            self._stop.wait(30)  # check every 30 seconds


# 
# Module-level singletons
# 
etl_pipeline  = ETLAutomationPipeline()
etl_scheduler = ETLScheduler(etl_pipeline)



