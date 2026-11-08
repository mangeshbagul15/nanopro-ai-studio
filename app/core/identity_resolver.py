"""
NanoPro Enterprise Unified Identity & Account Resolver
=====================================================
Provides unified identity resolution across multiple authentication channels:
  1. Direct Credentials (username: 'nanopro')
  2. Google SSO / OAuth (email: 'mangeshbagul15@gmail.com')
  3. WhatsApp OTP (phone: '+918433755448' / '8433755448')
  4. Clerk Zero-Trust Identity (user_id / JWT)

Resolves any identity or login method to the Single Canonical Account:
  - Canonical User ID: 'user_admin_001'
  - Canonical Username: 'nanopro'
  - Primary Email: 'mangeshbagul15@gmail.com'
  - Primary Phone: '+918433755448'
  - Master Role: 'admin'

For regular users, ensures strict tenant isolation (per-user DuckDB & SQLite partitioning).
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple
from app.core.config import SQLITE_DB_PATH
from app.core.logger import log_event

# Canonical Master Admin Identifiers for Mangesh Bagul (Super Admin)
ADMIN_USERNAMES: Set[str] = {"nanopro"}
ADMIN_EMAILS: Set[str] = {
    "mangeshbagul15@gmail.com",
    "nanoproaistudio@gmail.com",
    "nanopro@gmail.com",
    "nanoproai@gmail.com",
}
ADMIN_PHONES: Set[str] = {
    "8433755448",
    "+918433755448",
    "918433755448",
}
ADMIN_USER_ID = "user_admin_001"


def _clean_phone(phone: str) -> str:
    digits = "".join(c for c in (phone or "") if c.isdigit())
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    if digits:
        return f"+{digits}"
    return ""


def is_admin_identity(identifier: str) -> bool:
    """Checks whether the given username, email, phone, or user_id belongs to Super Admin."""
    if not identifier:
        return False
    val = identifier.strip().lower()
    if val in ADMIN_USERNAMES or val == ADMIN_USER_ID.lower():
        return True
    if val in ADMIN_EMAILS:
        return True
    clean_p = _clean_phone(val)
    if clean_p and clean_p in ADMIN_PHONES:
        return True
    return False


def resolve_canonical_username(identifier: str) -> str:
    """
    Given any identifier (username, email, phone, session user_id),
    returns the single canonical username.
    Super Admin always resolves to 'nanopro'.
    """
    if not identifier:
        return "user"
    clean = str(identifier).strip()
    if is_admin_identity(clean):
        return "nanopro"

    # Query local database for linked user
    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=5.0)
        conn.row_factory = sqlite3.Row
        with conn:
            cursor = conn.cursor()
            # 1. Direct username
            cursor.execute("SELECT username FROM users WHERE LOWER(username) = LOWER(?)", (clean,))
            r = cursor.fetchone()
            if r:
                return r["username"]

            # 2. Direct user_id
            cursor.execute("SELECT username FROM users WHERE id = ?", (clean,))
            r = cursor.fetchone()
            if r:
                return r["username"]

            # 3. Direct email
            cursor.execute("SELECT username FROM users WHERE LOWER(email) = LOWER(?)", (clean,))
            r = cursor.fetchone()
            if r:
                return r["username"]

            # 4. Direct phone
            phone_fmt = _clean_phone(clean)
            if phone_fmt:
                cursor.execute("SELECT username FROM users WHERE phone_number = ? OR phone_number LIKE ?", (phone_fmt, f"%{phone_fmt[-10:]}%"))
                r = cursor.fetchone()
                if r:
                    return r["username"]

            # 5. Linked identities
            cursor.execute("SELECT u.username FROM user_linked_identities l JOIN users u ON l.user_id = u.id WHERE LOWER(l.identifier) = LOWER(?)", (clean,))
            r = cursor.fetchone()
            if r:
                return r["username"]
    except Exception:
        pass

    # Clean username fallback
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", clean.lower()).strip("_")
    return sanitized or "user"


IDENTITY_PROVIDER_ALIASES: Dict[str, Tuple[str, ...]] = {
    "google": ("google", "email", "clerk"),
    "email": ("email", "google"),
    "clerk": ("clerk", "google", "email"),
    "whatsapp": ("whatsapp", "phone"),
    "phone": ("phone", "whatsapp"),
    "credentials": ("credentials",),
}


def _identity_key(provider: str, identifier: str) -> str:
    """Normalizes an identifier so the same person matches across login channels."""
    value = (identifier or "").strip()
    if not value:
        return ""
    provider = (provider or "").strip().lower()
    if provider in ("whatsapp", "sms", "phone"):
        return _clean_phone(value) or value
    return value.lower()


def _identifier_variants(identifier: str) -> Set[str]:
    value = (identifier or "").strip()
    variants: Set[str] = {value.lower()} if value else set()
    digits = "".join(c for c in value if c.isdigit())
    if len(digits) >= 6:
        variants.update({digits, f"+{digits}", f"91{digits}"})
        if len(digits) == 10:
            variants.update({f"+91{digits}", f"91{digits}"})
        elif len(digits) == 12 and digits.startswith("91"):
            variants.update({f"+{digits}", digits[2:]})
    return {v for v in variants if v}


def _link_identity_on(
    conn,
    user_id: str,
    provider: str,
    identifier: str,
    verified: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Links an identifier using the caller's connection (same transaction)."""
    key = _identity_key(provider, identifier)
    if not user_id or not key:
        return False
    try:
        row = conn.execute(
            "SELECT user_id FROM user_linked_identities WHERE LOWER(identifier) = LOWER(?)",
            (key,),
        ).fetchone()
        if row and row[0] != user_id:
            return False
        conn.execute(
            "INSERT OR IGNORE INTO user_linked_identities"
            " (id, user_id, provider, identifier, linked_at, is_verified, metadata)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                f"ident_{uuid.uuid4().hex[:16]}",
                user_id,
                (provider or "generic").strip().lower(),
                key,
                time.time(),
                1 if verified else 0,
                json.dumps(metadata or {}),
            ),
        )
        return True
    except Exception as exc:
        log_event(f"Identity link skipped: {exc}", component="IdentityResolver", level="WARNING")
        return False


def link_identity(
    user_id: str,
    provider: str,
    identifier: str,
    verified: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Links a verified login identifier to a user without stealing another account's link."""
    key = _identity_key(provider, identifier)
    if not user_id or not key:
        return False
    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=10.0)
        try:
            with conn:
                return _link_identity_on(conn, user_id, provider, identifier, verified, metadata)
        finally:
            conn.close()
    except Exception as exc:
        log_event(f"Identity link failed: {exc}", component="IdentityResolver", level="WARNING")
        return False


def find_user_by_identifier(identifier: str, provider: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Finds the canonical account owning a username, email, phone or linked identity.
    Used by username/password, Google, WhatsApp OTP and Clerk logins so every
    channel resolves to the same user and therefore the same chats/projects.
    """
    value = (identifier or "").strip()
    if not value:
        return None
    variants = _identifier_variants(value)
    if not variants:
        return None
    placeholders = ",".join("?" for _ in variants)
    providers = IDENTITY_PROVIDER_ALIASES.get((provider or "").strip().lower())
    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=5.0)
        conn.row_factory = sqlite3.Row
        try:
            if providers:
                p_ph = ",".join("?" for _ in providers)
                row = conn.execute(
                    f"SELECT u.id, u.username, u.role, u.status, u.full_name, u.email, u.phone_number"
                    f" FROM user_linked_identities l JOIN users u ON u.id = l.user_id"
                    f" WHERE LOWER(l.identifier) IN ({placeholders}) AND l.provider IN ({p_ph})"
                    f" ORDER BY l.is_verified DESC LIMIT 1",
                    [v.lower() for v in variants] + list(providers),
                ).fetchone()
                if row:
                    return dict(row)
            row = conn.execute(
                f"SELECT u.id, u.username, u.role, u.status, u.full_name, u.email, u.phone_number"
                f" FROM user_linked_identities l JOIN users u ON u.id = l.user_id"
                f" WHERE LOWER(l.identifier) IN ({placeholders})"
                f" ORDER BY l.is_verified DESC LIMIT 1",
                [v.lower() for v in variants],
            ).fetchone()
            if row:
                return dict(row)
            row = conn.execute(
                f"SELECT id, username, role, status, full_name, email, phone_number FROM users"
                f" WHERE LOWER(username) IN ({placeholders}) OR LOWER(email) IN ({placeholders})"
                f" OR phone_number IN ({placeholders}) OR id IN ({placeholders}) LIMIT 1",
                [v.lower() for v in variants] * 4,
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception:
        return None


def get_canonical_admin_profile() -> Dict[str, Any]:
    """Returns the standardized, complete master admin profile."""
    return {
        "id": ADMIN_USER_ID,
        "username": "nanopro",
        "full_name": "Super Admin (Mangesh Bagul)",
        "email": "mangeshbagul15@gmail.com",
        "phone_number": "+918433755448",
        "role": "admin",
        "status": "ACTIVE",
        "allowed_views": ["*"],
        "access_mode": "MODIFY",
        "linked_accounts": {
            "credentials": "nanopro",
            "google": "mangeshbagul15@gmail.com",
            "whatsapp": "+918433755448",
            "clerk": "user_3LXaKF9W8QkWYxswsB1gmVNGGbK",
        },
    }


def init_identity_tables() -> None:
    """Initializes the user_linked_identities table and seeds admin accounts."""
    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=10.0)
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_linked_identities (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                identifier TEXT NOT NULL,
                linked_at REAL NOT NULL,
                is_verified INTEGER DEFAULT 1,
                metadata TEXT DEFAULT '{}',
                UNIQUE(provider, identifier)
            )""")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_linked_identities_user ON user_linked_identities(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_linked_identities_lookup ON user_linked_identities(provider, identifier)")

            # Seed Admin identities for Mangesh Bagul
            now = time.time()
            admin_identities = [
                ("ident_adm_cred", ADMIN_USER_ID, "credentials", "nanopro"),
                ("ident_adm_email", ADMIN_USER_ID, "email", "mangeshbagul15@gmail.com"),
                ("ident_adm_google", ADMIN_USER_ID, "google", "mangeshbagul15@gmail.com"),
                ("ident_adm_wa1", ADMIN_USER_ID, "whatsapp", "+918433755448"),
                ("ident_adm_wa2", ADMIN_USER_ID, "whatsapp", "8433755448"),
                ("ident_adm_clerk", ADMIN_USER_ID, "clerk", "user_3LXaKF9W8QkWYxswsB1gmVNGGbK"),
            ]
            for i_id, u_id, prov, ident in admin_identities:
                cursor.execute("""
                INSERT OR IGNORE INTO user_linked_identities (id, user_id, provider, identifier, linked_at, is_verified)
                VALUES (?, ?, ?, ?, ?, 1)
                """, (i_id, u_id, prov, ident, now))

            # Ensure nanopro in users table has full data
            cursor.execute("""
            UPDATE users SET 
                email = 'mangeshbagul15@gmail.com',
                phone_number = '+918433755448',
                role = 'admin',
                status = 'ACTIVE'
            WHERE username = 'nanopro' OR id = ?
            """, (ADMIN_USER_ID,))
            conn.commit()
    except Exception as exc:
        log_event(f"Error initializing identity tables: {exc}", component="IdentityResolver", level="ERROR")


# Run schema init at import
init_identity_tables()
