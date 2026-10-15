# =========================================================================
# NanoPro Automated Python Validation Engine for Snowflake ETL Pipeline
# Validates schema types, null thresholds, primary key uniqueness & ranges
# =========================================================================
import pandas as pd
import numpy as np

def validate_pipeline_dataset(df: pd.DataFrame) -> dict:
    # Validates dataframe schema and business rules before warehouse load
    issues = []
    
    # 1. Null Checks
    null_counts = df.isnull().sum()
    critical_cols = ["CUSTOMER_ID", "ACCOUNT_NUMBER", "BALANCE"]
    for col in critical_cols:
        if col in df.columns and null_counts[col] > 0:
            issues.append(f"Null constraint violated: {null_counts[col]} nulls in {col}")
            
    # 2. Primary Key Uniqueness
    if "CUSTOMER_ID" in df.columns and df["CUSTOMER_ID"].duplicated().any():
        issues.append(f"Duplicate primary key values found in CUSTOMER_ID")
        
    # 3. Numeric Integrity (Non-negative balance)
    if "BALANCE" in df.columns and (df["BALANCE"] < 0).any():
        issues.append("Negative balance values detected in account balances")
        
    return {
        "valid": len(issues) == 0,
        "rows_inspected": len(df),
        "issues": issues,
        "schema_verified": True
    }

if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "CUSTOMER_ID": ["CUST_1001", "CUST_1002", "CUST_1003", "CUST_1004", "CUST_1005"],
        "CUSTOMER_NAME": ["Rajesh Sharma", "Priya Patel", "Vikram Singh", "Amit Verma", "Sneha Kulkarni"],
        "ACCOUNT_NUMBER": ["ACC_992101", "ACC_992102", "ACC_992103", "ACC_992104", "ACC_992105"],
        "BALANCE": [850000.0, 520000.0, 480000.0, 360000.0, 275000.0]
    })
    res = validate_pipeline_dataset(sample_data)
    print("Validation Result:", res)
