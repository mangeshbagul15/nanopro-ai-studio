"""
Mangesh Nano Pro AI Studio - Credentials Vault Module
Direct module interface for CredentialsVault, AES-256-GCM encryption/decryption,
and resilient multi-key self-healing storage.
"""

from app.core.database import (
    credentials_vault,
    CredentialsVault,
    encrypt_value,
    decrypt_value,
    mask_credential,
    _resolve_vault_master_key
)

__all__ = [
    "credentials_vault",
    "CredentialsVault",
    "encrypt_value",
    "decrypt_value",
    "mask_credential",
    "_resolve_vault_master_key"
]
