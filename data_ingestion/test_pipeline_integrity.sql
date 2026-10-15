-- =========================================================================
-- Automated SQL Test Suite & Assertions for Snowflake ETL Pipeline
-- Database: BANK_DB | Quality Threshold: 100% Pass Rate Required
-- =========================================================================

-- Test 1: Primary Key Uniqueness on RAW_CUSTOMERS
SELECT CUSTOMER_ID, COUNT(*) AS DUPLICATE_COUNT
FROM BANK_DB.L0_STAGING.RAW_CUSTOMERS
GROUP BY CUSTOMER_ID
HAVING COUNT(*) > 1;

-- Test 2: Foreign Key Referential Integrity (All accounts have valid customer)
SELECT a.ACCOUNT_NUMBER, a.CUSTOMER_ID
FROM BANK_DB.L0_STAGING.RAW_ACCOUNTS a
LEFT JOIN BANK_DB.L0_STAGING.RAW_CUSTOMERS c ON a.CUSTOMER_ID = c.CUSTOMER_ID
WHERE c.CUSTOMER_ID IS NULL;

-- Test 3: Non-Negative Account Balance Constraint
SELECT ACCOUNT_NUMBER, BALANCE
FROM BANK_DB.L0_STAGING.RAW_ACCOUNTS
WHERE BALANCE < 0;

-- Test 4: L0-to-L1 Row Count Reconciliation
SELECT 
    (SELECT COUNT(*) FROM BANK_DB.L0_STAGING.RAW_STAGE_TRANSACTIONS) AS L0_SOURCE_COUNT,
    (SELECT COUNT(*) FROM BANK_DB.L1_HARMONIZED.FACT_CLEANSED_TRANSACTIONS) AS L1_TARGET_COUNT;
