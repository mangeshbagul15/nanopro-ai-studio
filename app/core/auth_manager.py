"""
Mangesh Nano Pro AI Studio - Enterprise Authentication & Access Control Manager
Handles user registration, password hashing (PBKDF2-SHA256), approval workflows,
inactivity tracking, audit logging, and Telegram security alerts.
"""

import os
import re
import time
import json
import uuid
import hashlib
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import SQLITE_DB_PATH
from app.core.logger import log_event

class AuthManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or SQLITE_DB_PATH)
        self.inactivity_timeout_seconds = 900  # 15 minutes for regular users
        self._init_auth_tables()
        self._ensure_default_admin()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _parse_allowed_views(self, views_val: Any, role: str) -> Any:
        """Parses allowed view IDs with strict Role-Based Access Control (RBAC)."""
        if role == "admin":
            return ["*"]
        if not views_val or views_val == "*":
            return ["*"]
        if isinstance(views_val, (list, dict)):
            return views_val
        if isinstance(views_val, str):
            try:
                parsed = json.loads(views_val)
                return parsed
            except Exception:
                return [v.strip() for v in views_val.split(",") if v.strip()]
        return ["dashboard"]

    def _init_auth_tables(self):
        """Creates users, user_sessions, and user_audit_logs tables with granular RBAC permissions."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
                    created_at REAL NOT NULL,
                    last_login_at REAL,
                    last_active_at REAL,
                    total_usage_seconds INTEGER DEFAULT 0,
                    allowed_views TEXT DEFAULT '*',
                    access_mode TEXT DEFAULT 'MODIFY'
                )""")

                # Migrations: Add allowed_views and access_mode if they don't exist
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN allowed_views TEXT DEFAULT '*'")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN access_mode TEXT DEFAULT 'MODIFY'")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN department TEXT DEFAULT 'General'")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN purpose TEXT DEFAULT 'Enterprise Access'")
                except Exception:
                    pass

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_otps (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    otp_code TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    is_used INTEGER DEFAULT 0
                )""")

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    role TEXT NOT NULL,
                    login_time REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER DEFAULT 1
                )""")

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_audit_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    username TEXT,
                    event_type TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    created_at REAL NOT NULL
                )""")
                conn.commit()
        except Exception as e:
            log_event(f"Error initializing auth tables: {e}", component="AuthManager", level="ERROR")

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hashes password with PBKDF2-HMAC-SHA256 and unique salt."""
        if not salt:
            salt = uuid.uuid4().hex
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return key.hex(), salt

    def _ensure_default_admin(self):
        """Creates the super-admin account without shipping a shared default password."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password_hash, salt FROM users WHERE username = 'nanopro'")
                admin_row = cursor.fetchone()
                env_password = (os.getenv("NANOPRO_ADMIN_PASSWORD") or "").strip()
                if env_password:
                    ok, reason = self.validate_password_criteria(env_password)
                    if not ok:
                        log_event(f"NANOPRO_ADMIN_PASSWORD rejected: {reason}", component="AuthManager", level="ERROR")
                        env_password = ""
                if not admin_row:
                    initial_password = env_password
                    generated = False
                    if not initial_password:
                        initial_password = f"{uuid.uuid4().hex}Aa1!"
                        generated = True
                    pwd_hash, salt = self._hash_password(initial_password)
                    now = time.time()
                    cursor.execute("""
                    INSERT INTO users (id, username, full_name, email, password_hash, salt, role, status, created_at, last_login_at, last_active_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "user_admin_001",
                        "nanopro",
                        "Super Admin (Mangesh Bagul)",
                        "mangeshbagul15@gmail.com",
                        pwd_hash,
                        salt,
                        "admin",
                        "ACTIVE",
                        now,
                        now,
                        now
                    ))
                    conn.commit()
                    log_event("Default Super Admin 'nanopro' created and activated.", component="AuthManager")
                    if generated:
                        log_event(
                            "NANOPRO_ADMIN_PASSWORD was not set. Generated one-time admin password: "
                            f"{initial_password} — sign in, change it, and set the env var for future bootstraps.",
                            component="AuthManager",
                            level="WARNING",
                        )
                elif env_password:
                    calc_hash, _ = self._hash_password(env_password, admin_row["salt"])
                    if calc_hash != admin_row["password_hash"]:
                        pwd_hash, salt = self._hash_password(env_password)
                        cursor.execute(
                            "UPDATE users SET password_hash=?, salt=?, status='ACTIVE', role='admin' WHERE id='user_admin_001'",
                            (pwd_hash, salt),
                        )
                        conn.commit()
                        log_event("Super Admin password synchronized from NANOPRO_ADMIN_PASSWORD.", component="AuthManager")
        except Exception as e:
            log_event(f"Error ensuring default admin: {e}", component="AuthManager", level="WARNING")

    def validate_password_criteria(self, password: str) -> Tuple[bool, str]:
        """Validates enterprise password security criteria."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter (A-Z)."
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter (a-z)."
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number (0-9)."
        if not re.search(r"[@$!%*?&#^+=~-]", password):
            return False, "Password must contain at least one special character (@$!%*?&#)."
        return True, "Password meets criteria."

    def register_user(
        self,
        full_name: str,
        username: str,
        email: str,
        password: str,
        phone_number: Optional[str] = None,
        department: Optional[str] = None,
        purpose: Optional[str] = None,
        ip_address: str = "Unknown",
        user_agent: str = "Unknown"
    ) -> Dict[str, Any]:
        """Registers a new user into PENDING_APPROVAL state with Zero-Trust Governance."""
        full_name = full_name.strip()
        username = username.strip().lower()
        email = email.strip().lower()
        dept_clean = (department or "General").strip()
        purpose_clean = (purpose or "Enterprise Access").strip()

        if len(username) < 3 or len(username) > 20 or not re.match(r"^[a-zA-Z0-9_]+$", username):
            return {"status": "error", "error": "Username must be 3-20 characters and contain only letters/numbers (e.g. john_doe)."}

        if username in {"nanopro", "admin", "administrator", "root", "superadmin", "system", "support", "mangesh", "mangeshbagul15"}:
            return {"status": "error", "error": "This username is reserved. Please choose another."}

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            return {"status": "error", "error": "Please enter a valid Email ID."}

        is_valid_pwd, msg = self.validate_password_criteria(password)
        if not is_valid_pwd:
            return {"status": "error", "error": msg}

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    return {"status": "error", "error": "This username is already taken. Please choose another."}

                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return {"status": "error", "error": "This Email ID is already registered."}

                pwd_hash, salt = self._hash_password(password)
                user_id = f"user_{uuid.uuid4().hex[:12]}"
                now = time.time()

                phone_clean = (phone_number or "").strip()
                if phone_clean:
                    phone_digits = "".join(c for c in phone_clean if c.isdigit())
                    variants = {phone_clean, phone_digits}
                    if len(phone_digits) >= 10:
                        variants.add(f"+91{phone_digits[-10:]}")
                    cursor.execute(
                        f"SELECT id FROM users WHERE phone_number IN ({','.join('?' for _ in variants)})",
                        list(variants),
                    )
                    if cursor.fetchone():
                        return {
                            "status": "error",
                            "error": "This mobile number is already registered. Please log in with WhatsApp OTP instead.",
                        }
                allowed_views = ["dashboard", "universal_tech_video", "video_studio", "agent_grid"]
                cursor.execute("""
                INSERT INTO users (id, username, full_name, email, phone_number, password_hash, salt, role, status, created_at, last_active_at, allowed_views, access_mode, department, purpose)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'user', 'PENDING_APPROVAL', ?, ?, ?, 'READ_ONLY', ?, ?)
                """, (user_id, username, full_name, email, phone_clean, pwd_hash, salt, now, now, json.dumps(allowed_views), dept_clean, purpose_clean))

                cursor.execute("""
                INSERT INTO user_audit_logs (id, user_id, username, event_type, details, ip_address, user_agent, created_at)
                VALUES (?, ?, ?, 'SIGNUP', ?, ?, ?, ?)
                """, (f"audit_{uuid.uuid4().hex[:12]}", user_id, username, f"Access Request: Dept={dept_clean}, Purpose={purpose_clean}", ip_address, user_agent, now))

                conn.commit()

            # Link every registration identifier so Google / WhatsApp OTP logins
            # resolve back to this same account (and its chats/projects).
            try:
                from app.core.identity_resolver import link_identity

                link_identity(user_id, "credentials", username)
                link_identity(user_id, "email", email)
                link_identity(user_id, "google", email)
                if phone_clean:
                    link_identity(user_id, "whatsapp", phone_clean)
            except Exception as _link_exc:
                log_event(f"Notice: registration identity linking: {_link_exc}", component="AuthManager", level="WARNING")

            # Create Security Approval in Action Approvals Gate
            try:
                from app.core.database import db
                db.create_approval(
                    action_name=f"User Access Request: {username} ({full_name})",
                    agent_id="user_management",
                    target_system="RBAC / User Auth",
                    risk_level="MEDIUM",
                    reason=f"New user registered ({email}, Dept: {dept_clean}, Purpose: {purpose_clean}). Awaiting Super Admin authorization.",
                    expected_impact="Grants user access to approved features with designated access mode.",
                    parameters={
                        "user_id": user_id,
                        "username": username,
                        "email": email,
                        "full_name": full_name,
                        "department": dept_clean,
                        "purpose": purpose_clean,
                        "phone_number": phone_clean,
                        "type": "user_registration",
                        "allowed_views": ["dashboard", "universal_tech_video"],
                        "access_mode": "READ_ONLY"
                    },
                    is_reversible=True
                )
            except Exception as _appr_e:
                log_event(f"Notice: Approval request creation: {_appr_e}", component="AuthManager", level="WARNING")

            # Send Telegram Alert to Super Admin
            self._notify_telegram(
                f"🚨 <b>New User Access Request (नवीन प्रवेश विनंती)</b>\n"
                f"👤 <b>Name:</b> {full_name}\n"
                f"🔑 <b>Username:</b> {username}\n"
                f"📧 <b>Email:</b> {email}\n"
                f"📱 <b>Phone:</b> {phone_clean or 'N/A'}\n"
                f"🏢 <b>Department:</b> {dept_clean}\n"
                f"🎯 <b>Purpose:</b> {purpose_clean}\n"
                f"⏳ <b>Status:</b> PENDING_APPROVAL\n"
                f"🌐 <b>IP:</b> {ip_address}\n"
                f"<i>Please review & approve in User Management & Security Governance panel.</i>"
            )

            return {
                "status": "success",
                "status_code": "PENDING_APPROVAL",
                "message": "तुमची प्रवेश विनंती (Access Request) यशस्वीरीत्या पाठवली गेली आहे! सुरक्षेसाठी Super Admin (nanopro) कडून मंजुरी मिळाल्यावरच खाते सक्रिय होईल.",
                "user_id": user_id,
                "username": username
            }
        except Exception as e:
            log_event(f"Error registering user: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": f"Registration error: {str(e)}"}

    def authenticate_user(self, username: str, password: str, ip_address: str = "Unknown", user_agent: str = "Unknown") -> Dict[str, Any]:
        """Authenticates user via username, email, or phone number and returns active session."""
        raw_identifier = (username or "").strip()
        ident_lower = raw_identifier.lower()
        now = time.time()

        # Extract digit variants for phone lookup
        clean_digits = "".join(c for c in raw_identifier if c.isdigit())
        phone_variants = [raw_identifier]
        if clean_digits:
            phone_variants.extend([clean_digits, f"+{clean_digits}"])
            if len(clean_digits) == 10:
                phone_variants.extend([f"+91{clean_digits}", f"91{clean_digits}"])
            elif len(clean_digits) > 10 and clean_digits.startswith("91"):
                phone_variants.extend([f"+{clean_digits}", clean_digits[2:], f"+{clean_digits[2:]}"])

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check by username, email, or phone
                placeholders = ",".join("?" for _ in phone_variants)
                query = f"""
                SELECT * FROM users 
                WHERE LOWER(username) = ? 
                   OR LOWER(email) = ? 
                   OR phone_number IN ({placeholders})
                LIMIT 1
                """
                params = [ident_lower, ident_lower] + phone_variants
                cursor.execute(query, params)
                user = cursor.fetchone()

                # Google / WhatsApp users may sign in with a linked identifier.
                if not user:
                    try:
                        from app.core.identity_resolver import find_user_by_identifier

                        linked_user = find_user_by_identifier(raw_identifier)
                    except Exception:
                        linked_user = None
                    if linked_user:
                        cursor.execute("SELECT * FROM users WHERE id = ?", (linked_user["id"],))
                        user = cursor.fetchone()

                if not user:
                    self._record_audit_log(None, raw_identifier, "FAILED_LOGIN", "User not found", ip_address, user_agent)
                    return {"status": "error", "error": "Invalid username or password!"}

                is_admin_user = (user["username"] == "nanopro" or user["role"] == "admin")
                calc_hash, _ = self._hash_password(password, user["salt"])

                if calc_hash != user["password_hash"]:
                    self._record_audit_log(user["id"], raw_identifier, "FAILED_LOGIN", "Invalid password", ip_address, user_agent)
                    return {"status": "error", "error": "Invalid username or password!"}

                # Check account status
                if user["status"] == "PENDING_APPROVAL":
                    if not is_admin_user:
                        return {
                            "status": "error",
                            "status_code": "PENDING_APPROVAL",
                            "error": "तुमचे खाते ॲडमिन (nanopro) कडून मंजुरीच्या प्रतीक्षेत आहे (Pending Approval). सुरक्षेसाठी Super Admin मंजुरी मिळाल्यावरच लॉगिन करता येईल."
                        }
                    else:
                        cursor.execute("UPDATE users SET status = 'ACTIVE' WHERE id = ?", (user["id"],))
                        conn.commit()
                elif user["status"] == "REJECTED":
                    return {
                        "status": "error",
                        "error": "तुमची नोंदणी ॲडमिनद्वारे नाकारली गेली आहे. प्रवेश नाकारला (Access Denied)."
                    }
                elif user["status"] == "DISABLED":
                    return {
                        "status": "error",
                        "error": "सुरक्षा कारणास्तव हे खाते तात्पुरते निलंबित करण्यात आले आहे. कृपया ॲडमिनशी संपर्क साधा."
                    }

                # Create session
                session_token = f"np_sess_{uuid.uuid4().hex}"
                cursor.execute("""
                INSERT INTO user_sessions (session_token, user_id, username, role, login_time, last_activity, ip_address, user_agent, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (session_token, user["id"], user["username"], user["role"], now, now, ip_address, user_agent))

                cursor.execute("UPDATE users SET last_login_at = ?, last_active_at = ? WHERE id = ?", (now, now, user["id"]))
                conn.commit()

            self._record_audit_log(user["id"], username, "LOGIN", f"Successful login (Role: {user['role']})", ip_address, user_agent)

            # Send Telegram Login Notification
            login_time_str = time.strftime('%d-%m-%Y %I:%M:%S %p', time.localtime(now))
            self._notify_telegram(
                f"🔐 <b>NanoPro Login Alert</b>\n"
                f"👤 <b>User:</b> {user['username']} ({user['full_name']})\n"
                f"👑 <b>Role:</b> {user['role'].upper()}\n"
                f"🕒 <b>Time:</b> {login_time_str}\n"
                f"🌐 <b>IP:</b> {ip_address}\n"
                f"💻 <b>Device:</b> {user_agent[:40]}..."
            )

            parsed_views = self._parse_allowed_views(user["allowed_views"] if "allowed_views" in user.keys() else "*", user["role"])
            acc_mode = (user["access_mode"] if "access_mode" in user.keys() else "MODIFY") or "MODIFY"

            return {
                "status": "success",
                "session_token": session_token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "role": user["role"],
                    "allowed_views": parsed_views,
                    "access_mode": acc_mode
                }
            }
        except Exception as e:
            log_event(f"Error authenticating user: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": f"Login error: {str(e)}"}

    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validates active session and handles auto-logout on inactivity for regular users."""
        if not session_token:
            return {"is_valid": False, "error": "No session provided"}

        now = time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT s.*, u.full_name, u.email, u.status as user_status, u.allowed_views, u.access_mode
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
                """, (session_token,))
                sess = cursor.fetchone()

                if not sess:
                    return {"is_valid": False, "error": "Session expired or invalid"}

                if sess["user_status"] != "ACTIVE":
                    cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE session_token = ?", (session_token,))
                    conn.commit()
                    return {"is_valid": False, "error": "User account is not active"}

                # Check inactivity timeout (only for non-admin users)
                is_admin = (sess["role"] == "admin" or sess["username"] == "nanopro")
                idle_duration = now - sess["last_activity"]

                if not is_admin and idle_duration > self.inactivity_timeout_seconds:
                    # Inactivity Logout
                    cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE session_token = ?", (session_token,))
                    session_duration = int(now - sess["login_time"])
                    cursor.execute("UPDATE users SET total_usage_seconds = total_usage_seconds + ? WHERE id = ?", (session_duration, sess["user_id"]))
                    conn.commit()

                    self._record_audit_log(sess["user_id"], sess["username"], "AUTO_LOGOUT", f"Auto-logged out after {int(idle_duration//60)}m inactivity", sess["ip_address"], sess["user_agent"], duration_seconds=session_duration)
                    
                    self._notify_telegram(
                        f"⏱️ <b>NanoPro Auto Logout (Auto Logout - Inactivity)</b>\n"
                        f"👤 <b>User:</b> {sess['username']}\n"
                        f"⏳ <b>Idle Time:</b> {int(idle_duration//60)} minutes\n"
                        f"🕒 <b>Total Session:</b> {session_duration // 60}m {session_duration % 60}s"
                    )

                    return {"is_valid": False, "is_idle_timeout": True, "error": "Session expired due to 15 minutes of inactivity. Please log in again."}

                # Update active timestamp
                cursor.execute("UPDATE user_sessions SET last_activity = ? WHERE session_token = ?", (now, session_token))
                cursor.execute("UPDATE users SET last_active_at = ? WHERE id = ?", (now, sess["user_id"]))
                conn.commit()

                parsed_views = self._parse_allowed_views(sess["allowed_views"] if "allowed_views" in sess.keys() else "*", sess["role"])
                acc_mode = (sess["access_mode"] if "access_mode" in sess.keys() else "MODIFY") or "MODIFY"

                return {
                    "is_valid": True,
                    "user": {
                        "id": sess["user_id"],
                        "username": sess["username"],
                        "full_name": sess["full_name"],
                        "email": sess["email"],
                        "role": sess["role"],
                        "allowed_views": parsed_views,
                        "access_mode": acc_mode
                    },
                    "session_age_seconds": int(now - sess["login_time"]),
                    "idle_seconds": int(idle_duration)
                }
        except Exception as e:
            log_event(f"Error validating session: {e}", component="AuthManager", level="ERROR")
            return {"is_valid": False, "error": str(e)}

    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Terminates session, records session duration, and notifies Telegram."""
        if not session_token:
            return {"status": "success"}

        now = time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_sessions WHERE session_token = ? AND is_active = 1", (session_token,))
                sess = cursor.fetchone()

                if sess:
                    cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE session_token = ?", (session_token,))
                    session_duration = int(now - sess["login_time"])
                    cursor.execute("UPDATE users SET total_usage_seconds = total_usage_seconds + ? WHERE id = ?", (session_duration, sess["user_id"]))
                    conn.commit()

                    self._record_audit_log(sess["user_id"], sess["username"], "LOGOUT", f"User logged out normally", sess["ip_address"], sess["user_agent"], duration_seconds=session_duration)

                    mins = session_duration // 60
                    secs = session_duration % 60
                    self._notify_telegram(
                        f"🚪 <b>NanoPro User Logout Alert</b>\n"
                        f"👤 <b>User:</b> {sess['username']}\n"
                        f"⏱️ <b>Active Session Duration:</b> {mins} min {secs} sec\n"
                        f"🕒 <b>Logout Time:</b> {time.strftime('%I:%M:%S %p', time.localtime(now))}"
                    )

            return {"status": "success", "message": "Logout successful."}
        except Exception as e:
            log_event(f"Error logging out user: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": str(e)}

    def verify_clerk_session(
        self,
        clerk_token: Optional[str] = None,
        session_id: Optional[str] = None,
        clerk_user_id: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        ip_address: str = "Unknown",
        user_agent: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Verifies a Clerk session or JWT token, retrieves or provisions the user in local SQLite DB,
        and issues an authenticated NanoPro session token with Zero-Trust enforcement.
        """
        import urllib.request
        from app.core.credentials_vault import CredentialsVault

        # 1. Fetch Clerk configuration and credentials
        vault = CredentialsVault()
        clerk_cred = vault.get_credential("CLERK_AUTH")
        secret_key = (clerk_cred.get("secret_value") if clerk_cred else None) or (os.getenv("CLERK_SECRET_KEY") or "").strip()
        meta = (clerk_cred.get("additional_metadata") if clerk_cred else {}) or {}
        jwks_url = meta.get("jwks_url", "https://adapted-muskrat-6801.clerk.accounts.dev/.well-known/jwks.json")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NanoProAI/1.0"
        }
        if secret_key:
            headers["Authorization"] = f"Bearer {secret_key}"

        verified = False
        verified_sub = None
        trusted_email = ""

        # 2. Strategy A: Try JWT signature verification if token is passed and has '.'
        if clerk_token and "." in clerk_token:
            try:
                import jwt
                jwks_client = jwt.PyJWKClient(jwks_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NanoProAI/1.0"})
                signing_key = jwks_client.get_signing_key_from_jwt(clerk_token)
                payload = jwt.decode(clerk_token, signing_key.key, algorithms=["RS256"], options={"verify_aud": False})
                verified_sub = payload.get("sub")
                if verified_sub:
                    clerk_user_id = verified_sub
                    verified = True
                    # Only a signed claim can be trusted, never the request body.
                    payload_email = (payload.get("email") or "").strip().lower()
                    if payload_email and payload.get("email_verified") is not False:
                        trusted_email = payload_email
            except Exception as jwt_ex:
                log_event(f"Clerk JWT direct validation note: {jwt_ex}", component="AuthManager", level="WARNING")

        # 3. Strategy B: Verify session_id via Clerk Backend API if session_id provided or token starts with sess_
        target_sid = session_id or (clerk_token if (clerk_token and clerk_token.startswith("sess_")) else None)
        if target_sid and not verified and secret_key:
            try:
                req_url = f"https://api.clerk.com/v1/sessions/{target_sid}"
                req = urllib.request.Request(req_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    if resp.status == 200:
                        s_data = json.loads(resp.read().decode())
                        if s_data.get("status") in ["active", "revoked"]:
                            clerk_user_id = s_data.get("user_id") or clerk_user_id
                            verified = (s_data.get("status") == "active")
            except Exception as sess_ex:
                log_event(f"Clerk Session API check note: {sess_ex}", component="AuthManager", level="WARNING")

        # 4. If we have clerk_user_id, enrich profile from Clerk backend
        if clerk_user_id and secret_key:
            try:
                u_url = f"https://api.clerk.com/v1/users/{clerk_user_id}"
                req = urllib.request.Request(u_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    if resp.status == 200:
                        u_data = json.loads(resp.read().decode())
                        verified = True  # Verified against live Clerk API
                        # Extract email verified by Clerk, not the request body.
                        profile_email = ""
                        for em_obj in u_data.get("email_addresses", []):
                            if em_obj.get("id") == u_data.get("primary_email_address_id"):
                                profile_email = em_obj.get("email_address") or ""
                                break
                        if not profile_email and u_data.get("email_addresses"):
                            profile_email = u_data["email_addresses"][0].get("email_address") or ""
                        trusted_email = (profile_email or "").strip().lower()
                        fn = u_data.get("first_name") or ""
                        ln = u_data.get("last_name") or ""
                        derived_name = f"{fn} {ln}".strip()
                        if derived_name:
                            full_name = derived_name
            except Exception as u_ex:
                log_event(f"Clerk User API lookup note: {u_ex}", component="AuthManager", level="WARNING")

        if not verified:
            return {"status": "error", "error": "Clerk session verification failed. Invalid or expired token."}

        # 5. Map to Local User Database
        now = time.time()
        email_clean = trusted_email
        from app.core.identity_resolver import is_admin_identity
        is_admin_user = is_admin_identity(email_clean) or is_admin_identity(clerk_user_id)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                user = None

                # Resolve through linked identities so Google SSO lands on the
                # same account the person registered or used OTP with.
                if email_clean or clerk_user_id:
                    try:
                        from app.core.identity_resolver import find_user_by_identifier

                        linked_user = (
                            find_user_by_identifier(email_clean, provider="google")
                            if email_clean
                            else find_user_by_identifier(clerk_user_id, provider="clerk")
                        )
                    except Exception:
                        linked_user = None
                    if linked_user:
                        cursor.execute("SELECT * FROM users WHERE id = ?", (linked_user["id"],))
                        user = cursor.fetchone()

                # Find by email next
                if not user and email_clean:
                    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email_clean,))
                    user = cursor.fetchone()

                # If admin, ensure mapped to nanopro user
                if not user and is_admin_user:
                    cursor.execute("SELECT * FROM users WHERE username = 'nanopro'")
                    user = cursor.fetchone()

                if user is not None and not isinstance(user, dict):
                    user = dict(user)

                if user:
                    user_id = user["id"]
                    user_role = user["role"]
                    username = user["username"]
                    if user.get("status") == "PENDING_APPROVAL" and not is_admin_user:
                        return {
                            "status": "error",
                            "status_code": "PENDING_APPROVAL",
                            "error": "तुमचे Google खाते ॲडमिन (nanopro) कडून मंजुरीच्या प्रतीक्षेत आहे (Pending Approval). सुरक्षेसाठी Super Admin मंजुरी मिळाल्यावरच लॉगिन करता येईल."
                        }
                    elif user.get("status") == "REJECTED":
                        return {"status": "error", "error": "तुमची Google खात्याची नोंदणी ॲडमिन कडून नाकारण्यात आली आहे."}
                    elif user.get("status") == "DISABLED":
                        return {"status": "error", "error": "हे खाते सुरक्षा कारणास्तव बंद करण्यात आले आहे."}

                    allowed_views = self._parse_allowed_views(user["allowed_views"] if "allowed_views" in user.keys() else "*", user_role)
                    access_mode = (user["access_mode"] if "access_mode" in user.keys() else "MODIFY") or "MODIFY"
                    user_full_name = user["full_name"] or full_name or username
                    cursor.execute("UPDATE users SET last_login_at = ?, last_active_at = ? WHERE id = ?", (now, now, user_id))
                else:
                    user_id = f"user_{uuid.uuid4().hex[:12]}"
                    username = (email_clean.split("@")[0] if email_clean else f"clerk_{clerk_user_id[:8]}").lower()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        username = f"{username}_{uuid.uuid4().hex[:4]}"
                    user_role = "admin" if is_admin_user else "user"
                    user_full_name = full_name or username.capitalize()
                    allowed_views = ["*"] if user_role == "admin" else ["dashboard", "universal_tech_video"]
                    access_mode = "MODIFY" if is_admin_user else "READ_ONLY"
                    init_status = "ACTIVE" if is_admin_user else "PENDING_APPROVAL"

                    cursor.execute("""
                    INSERT INTO users (id, username, full_name, email, password_hash, salt, role, status, created_at, last_login_at, last_active_at, allowed_views, access_mode, department, purpose)
                    VALUES (?, ?, ?, ?, 'clerk_sso_managed', 'sso_salt', ?, ?, ?, ?, ?, ?, ?, 'General', 'Google Clerk SSO')
                    """, (user_id, username, user_full_name, email_clean or f"{username}@clerk.nanopro.ai", user_role, init_status, now, now, now, json.dumps(allowed_views), access_mode))
                    conn.commit()

                    if not is_admin_user:
                        self._notify_telegram(
                            f"🚨 <b>New User Registration (Google SSO)</b>\n"
                            f"👤 <b>Name:</b> {user_full_name}\n"
                            f"🔑 <b>Username:</b> {username}\n"
                            f"📧 <b>Email:</b> {email_clean}\n"
                            f"⏳ <b>Status:</b> PENDING_APPROVAL\n"
                            f"<i>Please review & approve in User Management & Security Governance panel.</i>"
                        )
                        return {
                            "status": "error",
                            "status_code": "PENDING_APPROVAL",
                            "error": "Google प्रमाणीकरण यशस्वी झाले आहे, परंतु नवीन वापरकर्त्यांसाठी Super Admin (nanopro) कडून मंजुरी आवश्यक आहे."
                        }

                # Persist the SSO identifiers against the canonical account.
                try:
                    from app.core.identity_resolver import _link_identity_on

                    if email_clean:
                        _link_identity_on(conn, user_id, "google", email_clean)
                        _link_identity_on(conn, user_id, "email", email_clean)
                    if clerk_user_id:
                        _link_identity_on(conn, user_id, "clerk", clerk_user_id)
                except Exception:
                    pass

                # Create active NanoPro session token
                session_token = f"np_sess_{uuid.uuid4().hex}"
                cursor.execute("""
                INSERT INTO user_sessions (session_token, user_id, username, role, login_time, last_activity, ip_address, user_agent, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (session_token, user_id, username, user_role, now, now, ip_address, user_agent))

                conn.commit()

            # Record audit log
            self._record_audit_log(user_id, username, "CLERK_LOGIN", f"Clerk Zero Trust login (Role: {user_role}, Email: {email_clean})", ip_address, user_agent)

            # Send Telegram Alert
            login_time_str = time.strftime('%d-%m-%Y %I:%M:%S %p', time.localtime(now))
            self._notify_telegram(
                f"🛡️ <b>NanoPro Clerk Zero Trust Login (SSO Verified)</b>\n"
                f"👤 <b>User:</b> {username} ({user_full_name})\n"
                f"👑 <b>Role:</b> {user_role.upper()}\n"
                f"📧 <b>Email:</b> {email_clean or 'N/A'}\n"
                f"🕒 <b>Time:</b> {login_time_str}\n"
                f"🌐 <b>IP:</b> {ip_address}\n"
                f"💻 <b>Device:</b> {user_agent[:40]}..."
            )

            return {
                "status": "success",
                "session_token": session_token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "full_name": user_full_name,
                    "email": email_clean,
                    "role": user_role,
                    "allowed_views": allowed_views,
                    "access_mode": access_mode
                }
            }
        except Exception as e:
            log_event(f"Error handling verified Clerk session: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": f"Clerk authentication error: {str(e)}"}

    def generate_and_send_otp(self, identifier: str, channel: str = "whatsapp", ip_address: str = "Unknown") -> Dict[str, Any]:
        """
        Generates a 6-digit OTP and dispatches it via WhatsApp or Email,
        also sending an instant backup notification to the Admin Telegram bot.
        """
        import random
        from app.core.communication_center import communication_center

        identifier = identifier.strip()
        if not identifier:
            return {"status": "error", "error": "Please enter your mobile number or email."}
        if channel != "whatsapp":
            return {"status": "error", "error": "Only WhatsApp OTP is supported. Please use WhatsApp or Google sign-in."}

        clean_digits = "".join(c for c in identifier if c.isdigit())
        if len(clean_digits) < 10:
            return {"status": "error", "error": "Please enter a valid mobile number with country code."}
        clean_id = f"+91{clean_digits}" if len(clean_digits) == 10 else (
            identifier if identifier.startswith("+") else f"+{clean_digits}"
        )

        otp_code = f"{random.randint(100000, 999999)}"
        now = time.time()
        expires_at = now + 300  # 5 minutes

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE auth_otps SET is_used = 1 WHERE identifier = ? AND is_used = 0", (clean_id,))
                otp_id = f"otp_{uuid.uuid4().hex[:12]}"
                cursor.execute("""
                INSERT INTO auth_otps (id, identifier, otp_code, channel, created_at, expires_at, is_used)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (otp_id, clean_id, otp_code, channel, now, expires_at))
                conn.commit()

            msg = (
                f"🔐 *NanoPro AI Studio Login Verification*\n\n"
                f"Your 6-digit verification code is: *{otp_code}*\n\n"
                f"⏳ Valid for 5 minutes. Never share this code.\n"
                f"🛡️ Zero-Trust Security Sentinel"
            )
            res = communication_center.send_whatsapp_cloud_api(phone=clean_id, message=msg)
            # A generic template fallback carries no OTP, so it is not a delivery success.
            delivered = bool(res.get("success")) and res.get("status") != "delivered_via_template_fallback"
            if not delivered:
                res = communication_center.send_whatsapp_free_message(phone=clean_id, message=msg)
                delivered = bool(res.get("delivered_via_api"))
            if not delivered:
                return {"status": "error", "error": "OTP delivery failed. Please try again in a moment."}

            # Instant Admin Telegram Alert (serves as immediate backup)
            time_str = time.strftime('%I:%M:%S %p', time.localtime(now))
            self._notify_telegram(
                f"📲 <b>NanoPro OTP Request (OTP Sent)</b>\n"
                f"📟 <b>Channel:</b> {channel.upper()}\n"
                f"🎯 <b>Target:</b> {clean_id}\n"
                f"🔢 <b>OTP Code:</b> <code>{otp_code}</code>\n"
                f"🌐 <b>IP:</b> {ip_address}\n"
                f"🕒 <b>Time:</b> {time_str}"
            )

            return {
                "status": "success",
                "message": f"6-digit OTP sent to your {channel.upper()} successfully.",
                "identifier": clean_id,
                "expires_in_seconds": 300
            }
        except Exception as e:
            log_event(f"Error generating OTP: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": f"Error sending OTP: {str(e)}"}

    def verify_otp_and_login(
        self,
        identifier: str,
        otp_code: str,
        channel: str = "whatsapp",
        ip_address: str = "Unknown",
        user_agent: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Validates OTP, links or provisions user account, and issues active session token.
        """
        identifier = identifier.strip()
        otp_code = otp_code.strip()
        if not identifier or not otp_code:
            return {"status": "error", "error": "Please enter both phone number and OTP code."}
        if channel != "whatsapp":
            return {"status": "error", "error": "Only WhatsApp OTP is supported. Please use WhatsApp or Google sign-in."}

        clean_digits = "".join(c for c in identifier if c.isdigit())
        if len(clean_digits) < 10:
            return {"status": "error", "error": "Invalid mobile number."}
        clean_id = f"+91{clean_digits}" if len(clean_digits) == 10 else (
            identifier if identifier.startswith("+") else f"+{clean_digits}"
        )

        now = time.time()
        from app.core.identity_resolver import is_admin_identity
        is_admin = is_admin_identity(clean_id)
        try:
            from app.core.identity_resolver import find_user_by_identifier

            linked_user = find_user_by_identifier(clean_id, provider=channel)
        except Exception:
            linked_user = None
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT * FROM auth_otps
                WHERE identifier = ? AND otp_code = ? AND is_used = 0 AND expires_at >= ?
                ORDER BY created_at DESC LIMIT 1
                """, (clean_id, otp_code, now))
                otp_row = cursor.fetchone()

                if not otp_row:
                    return {"status": "error", "error": "Invalid or expired OTP! Please try again."}

                if otp_row:
                    cursor.execute("UPDATE auth_otps SET is_used = 1 WHERE id = ?", (otp_row["id"],))

                user = None
                if linked_user:
                    cursor.execute("SELECT * FROM users WHERE id = ?", (linked_user["id"],))
                    user = cursor.fetchone()
                if not user and channel == "whatsapp":
                    clean_digits = "".join(c for c in clean_id if c.isdigit())
                    cursor.execute(
                        "SELECT * FROM users WHERE phone_number IN (?, ?, ?) OR LOWER(email) = LOWER(?)",
                        (clean_id, clean_digits, clean_id.lstrip("+"), clean_id),
                    )
                    user = cursor.fetchone()
                elif not user:
                    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (clean_id,))
                    user = cursor.fetchone()

                if is_admin and not user:
                    cursor.execute("SELECT * FROM users WHERE username = 'nanopro'")
                    user = cursor.fetchone()

                if user is not None and not isinstance(user, dict):
                    user = dict(user)

                if user:
                    user_id = user["id"]
                    user_role = user["role"]
                    username = user["username"]
                    full_name = user["full_name"]
                    email = user["email"]

                    if user.get("status") == "PENDING_APPROVAL" and not is_admin:
                        return {
                            "status": "error",
                            "status_code": "PENDING_APPROVAL",
                            "error": "तुमचे खाते ॲडमिन (nanopro) कडून मंजुरीच्या प्रतीक्षेत आहे (Pending Approval). सुरक्षेसाठी Super Admin मंजुरी मिळाल्यावरच लॉगिन करता येईल."
                        }
                    elif user.get("status") == "REJECTED":
                        return {"status": "error", "error": "तुमची नोंदणी ॲडमिनद्वारे नाकारली गेली आहे."}
                    elif user.get("status") == "DISABLED":
                        return {"status": "error", "error": "सुरक्षा कारणास्तव हे खाते तात्पुरते निलंबित करण्यात आले आहे."}

                    allowed_views = self._parse_allowed_views(user["allowed_views"] if "allowed_views" in user.keys() else "*", user_role)
                    access_mode = (user["access_mode"] if "access_mode" in user.keys() else "MODIFY") or "MODIFY"
                    cursor.execute("UPDATE users SET last_login_at = ?, last_active_at = ? WHERE id = ?", (now, now, user_id))
                    try:
                        from app.core.identity_resolver import _link_identity_on

                        _link_identity_on(conn, user_id, "whatsapp" if channel == "whatsapp" else "email", clean_id)
                    except Exception:
                        pass
                else:
                    user_id = f"user_{uuid.uuid4().hex[:12]}"
                    digits_suffix = "".join(c for c in clean_id if c.isdigit())[-6:]
                    username = f"wa_{digits_suffix}" if channel == "whatsapp" else clean_id.split("@")[0].lower()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        username = f"{username}_{uuid.uuid4().hex[:4]}"

                    user_role = "admin" if is_admin else "user"
                    full_name = f"Super Admin (Mangesh Bagul)" if is_admin else f"WhatsApp User ({clean_id})"
                    email = f"mangeshbagul15@gmail.com" if is_admin else (f"{username}@whatsapp.nanopro.ai" if channel == "whatsapp" else clean_id)
                    allowed_views = ["*"] if is_admin else ["dashboard", "universal_tech_video"]
                    access_mode = "MODIFY" if is_admin else "READ_ONLY"
                    init_status = "ACTIVE" if is_admin else "PENDING_APPROVAL"

                    cursor.execute("""
                    INSERT INTO users (id, username, full_name, email, phone_number, password_hash, salt, role, status, created_at, last_login_at, last_active_at, allowed_views, access_mode, department, purpose)
                    VALUES (?, ?, ?, ?, ?, 'otp_verified', 'otp_salt', ?, ?, ?, ?, ?, ?, ?, 'General', 'WhatsApp OTP Signup')
                    """, (user_id, username, full_name, email, clean_id, user_role, init_status, now, now, now, json.dumps(allowed_views), access_mode))
                    conn.commit()
                    try:
                        from app.core.identity_resolver import _link_identity_on

                        _link_identity_on(conn, user_id, "whatsapp" if channel == "whatsapp" else "email", clean_id)
                        conn.commit()
                    except Exception:
                        pass

                    if not is_admin:
                        self._notify_telegram(
                            f"🚨 <b>New User Registration (WhatsApp OTP)</b>\n"
                            f"👤 <b>Name:</b> {full_name}\n"
                            f"🔑 <b>Username:</b> {username}\n"
                            f"📱 <b>Phone:</b> {clean_id}\n"
                            f"⏳ <b>Status:</b> PENDING_APPROVAL\n"
                            f"<i>Please review & approve in User Management & Security Governance panel.</i>"
                        )
                        return {
                            "status": "error",
                            "status_code": "PENDING_APPROVAL",
                            "error": "WhatsApp OTP पडताळला गेला आहे! सुरक्षेसाठी नवीन वापरकर्त्यांना प्रवेश देण्यासाठी Super Admin (nanopro) कडून मंजुरी आवश्यक आहे."
                        }

                session_token = f"np_sess_{uuid.uuid4().hex}"
                cursor.execute("""
                INSERT INTO user_sessions (session_token, user_id, username, role, login_time, last_activity, ip_address, user_agent, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (session_token, user_id, username, user_role, now, now, ip_address, user_agent))

                conn.commit()

            self._record_audit_log(user_id, username, "OTP_LOGIN", f"OTP login verified via {channel.upper()} (Target: {clean_id})", ip_address, user_agent)

            login_time_str = time.strftime('%d-%m-%Y %I:%M:%S %p', time.localtime(now))
            self._notify_telegram(
                f"💬 <b>NanoPro {channel.upper()} OTP Login Verified</b>\n"
                f"👤 <b>User:</b> {username} ({full_name})\n"
                f"👑 <b>Role:</b> {user_role.upper()}\n"
                f"📱 <b>Target:</b> {clean_id}\n"
                f"🕒 <b>Time:</b> {login_time_str}\n"
                f"🌐 <b>IP:</b> {ip_address}"
            )

            return {
                "status": "success",
                "session_token": session_token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "full_name": full_name,
                    "email": email,
                    "role": user_role,
                    "allowed_views": allowed_views,
                    "access_mode": access_mode
                }
            }
        except Exception as e:
            log_event(f"Error verifying OTP login: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": f"OTP verification error: {str(e)}"}

    def list_users(self) -> List[Dict[str, Any]]:
        """Returns all registered users with metadata for the Admin Panel."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT id, username, full_name, email, phone_number, department, purpose, role, status, created_at, last_login_at, last_active_at, total_usage_seconds, allowed_views, access_mode
                FROM users
                ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                users = []
                for r in rows:
                    p_views = self._parse_allowed_views(r["allowed_views"] if "allowed_views" in r.keys() else "*", r["role"])
                    acc_m = (r["access_mode"] if "access_mode" in r.keys() else "MODIFY") or "MODIFY"
                    users.append({
                        "id": r["id"],
                        "username": r["username"],
                        "full_name": r["full_name"],
                        "email": r["email"],
                        "phone_number": r["phone_number"] if "phone_number" in r.keys() and r["phone_number"] else "-",
                        "department": r["department"] if "department" in r.keys() and r["department"] else "General",
                        "purpose": r["purpose"] if "purpose" in r.keys() and r["purpose"] else "Enterprise Access",
                        "role": r["role"],
                        "status": r["status"],
                        "allowed_views": p_views,
                        "access_mode": acc_m,
                        "created_at_fmt": time.strftime('%d-%m-%Y %H:%M', time.localtime(r["created_at"])) if r["created_at"] else "-",
                        "last_login_fmt": time.strftime('%d-%m-%Y %H:%M', time.localtime(r["last_login_at"])) if r["last_login_at"] else "Never",
                        "total_usage_fmt": f"{r['total_usage_seconds'] // 60}m {r['total_usage_seconds'] % 60}s"
                    })
                return users
        except Exception as e:
            log_event(f"Error listing users: {e}", component="AuthManager", level="ERROR")
            return []

    def approve_user(self, user_id: str, admin_username: str = "nanopro", allowed_views: Any = None, access_mode: str = "MODIFY") -> Dict[str, Any]:
        """Approves a pending user account with specific allowed features (desktop & mobile) and access mode (Read-Only vs Modify)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, email, full_name FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {"status": "error", "error": "User not found"}

                if not allowed_views or allowed_views == "*" or (isinstance(allowed_views, list) and "*" in allowed_views):
                    views_json = "*"
                else:
                    views_json = json.dumps(allowed_views)
                mode_clean = access_mode.upper() if access_mode in ["READ_ONLY", "MODIFY"] else "MODIFY"

                cursor.execute("UPDATE users SET status = 'ACTIVE', allowed_views = ?, access_mode = ? WHERE id = ?", (views_json, mode_clean, user_id))
                conn.commit()

            if views_json == "*":
                feature_summary = "All Features"
            elif isinstance(allowed_views, dict):
                d_c = len(allowed_views.get("desktop", []))
                m_c = len(allowed_views.get("mobile", []))
                feature_summary = f"Desktop: {d_c}, Mobile: {m_c} Features"
            else:
                feature_summary = f"{len(allowed_views)} Features"
            mode_desc = "Full Access (Modify/Edit)" if mode_clean == "MODIFY" else "Read-Only Access"

            self._record_audit_log(user_id, user["username"], "APPROVAL", f"Approved by {admin_username} (Mode: {mode_clean}, Features: {feature_summary})")
            self._notify_telegram(
                f"✅ <b>User Approved</b>\n"
                f"👤 <b>Username:</b> {user['username']} ({user['full_name']})\n"
                f"📧 <b>Email:</b> {user['email']}\n"
                f"👑 <b>Approved By:</b> {admin_username}\n"
                f"🔒 <b>Access Mode:</b> {mode_desc}\n"
                f"📂 <b>Approved Features:</b> {feature_summary}\n"
                f"<i>This user can now log in with assigned permissions.</i>"
            )

            return {"status": "success", "message": f"User '{user['username']}' {mode_desc} approved with permissions !"}
        except Exception as e:
            log_event(f"Error approving user: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": str(e)}

    def update_user_permissions(self, user_id: str, admin_username: str = "nanopro", allowed_views: Any = None, access_mode: str = "MODIFY") -> Dict[str, Any]:
        """Updates allowed features (desktop & mobile) and access mode (Read-Only vs Modify) for an existing user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {"status": "error", "error": "User not found"}
                is_admin = (user["username"] == "nanopro")
                if not allowed_views or allowed_views == "*" or (isinstance(allowed_views, list) and "*" in allowed_views):
                    views_json = "*"
                else:
                    views_json = json.dumps(allowed_views)
                mode_clean = "MODIFY" if is_admin else (access_mode.upper() if access_mode in ["READ_ONLY", "MODIFY"] else "MODIFY")

                cursor.execute("UPDATE users SET allowed_views = ?, access_mode = ? WHERE id = ?", (views_json, mode_clean, user_id))
                conn.commit()

            if views_json == "*":
                feature_summary = "All Features"
            elif isinstance(allowed_views, dict):
                d_c = len(allowed_views.get("desktop", []))
                m_c = len(allowed_views.get("mobile", []))
                feature_summary = f"Desktop: {d_c}, Mobile: {m_c} Features"
            else:
                feature_summary = f"{len(allowed_views)} Features"
            mode_desc = "Full Access (Modify/Edit)" if mode_clean == "MODIFY" else "Read-Only Access"

            self._record_audit_log(user_id, user["username"], "PERMISSIONS_UPDATED", f"Updated by {admin_username} (Mode: {mode_clean}, Features: {feature_summary})")
            return {"status": "success", "message": f"User '{user['username']}' 's permissions updated ({mode_desc})!"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def toggle_user_status(self, user_id: str, new_status: str) -> Dict[str, Any]:
        """Toggles user status between ACTIVE and DISABLED."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {"status": "error", "error": "User not found"}
                if user["username"] == "nanopro":
                    return {"status": "error", "error": "Super Admin account status cannot be changed!"}

                cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
                if new_status == "DISABLED":
                    cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
                conn.commit()

            self._record_audit_log(user_id, user["username"], "STATUS_CHANGE", f"Status set to {new_status}")
            return {"status": "success", "message": f"User '{user['username']}' is now '{new_status}' updated."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def reset_user_password(self, user_id: str, new_password: str) -> Dict[str, Any]:
        """Admin password reset for any user."""
        is_valid_pwd, msg = self.validate_password_criteria(new_password)
        if not is_valid_pwd:
            return {"status": "error", "error": msg}

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {"status": "error", "error": "User not found"}

                pwd_hash, salt = self._hash_password(new_password)
                cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (pwd_hash, salt, user_id))
                cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
                conn.commit()

            self._record_audit_log(user_id, user["username"], "PASSWORD_RESET", "Password reset by admin")
            return {"status": "success", "message": f"User '{user['username']}' 's password updated successfully!"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def delete_user(self, user_id: str, admin_username: str = "nanopro") -> Dict[str, Any]:
        """Permanently deletes a user account and terminates all active sessions. Super admin cannot be deleted."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, full_name, email, role FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {"status": "error", "error": "User not found."}

                if user["username"] == "nanopro" or user["role"] == "admin":
                    return {"status": "error", "error": "Super Admin 'nanopro' cannot be deleted!"}

                # Terminate and delete sessions
                cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
                # Delete user row
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()

            # Record audit log
            self._record_audit_log(
                user_id,
                user["username"],
                "USER_DELETED",
                f"User '{user['username']}' ({user['email']}) permanently deleted by {admin_username}"
            )

            # Send Telegram security notification
            self._notify_telegram(
                f"🗑️ <b>User Account Deleted</b>\n"
                f"👤 <b>Username:</b> {user['username']} ({user['full_name']})\n"
                f"📧 <b>Email:</b> {user['email']}\n"
                f"👑 <b>Deleted By:</b> {admin_username}\n"
                f"🕒 <b>Time:</b> {time.strftime('%I:%M:%S %p', time.localtime())}\n"
                f"<i>All sessions and permissions revoked.</i>"
            )

            return {"status": "success", "message": f"User '{user['username']}' deleted successfully."}
        except Exception as e:
            log_event(f"Error deleting user: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": str(e)}

    def reject_user(self, user_id: str, admin_username: str = "nanopro", reason: str = "") -> Dict[str, Any]:
        """Rejects a user registration. Terminates active sessions, updates status to REJECTED, and records audit log."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, full_name, email, role, status FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {"status": "error", "error": "User not found."}

                if user["username"] == "nanopro" or user["role"] == "admin":
                    return {"status": "error", "error": "Super Admin 'nanopro' cannot be rejected!"}

                # Update status to REJECTED
                cursor.execute("UPDATE users SET status = 'REJECTED' WHERE id = ?", (user_id,))
                # Terminate any active sessions immediately
                cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
                conn.commit()

            # Record audit log
            details = f"User '{user['username']}' ({user['email']}) rejected by {admin_username}"
            if reason:
                details += f" (Reason: {reason})"
            self._record_audit_log(
                user_id,
                user["username"],
                "USER_REJECTED",
                details
            )

            # Send Telegram security notification
            time_str = time.strftime('%d-%m-%Y %I:%M:%S %p', time.localtime())
            reason_txt = f"\n📝 <b>Reason:</b> {reason}" if reason else ""
            self._notify_telegram(
                f"🚫 <b>User Registration Rejected</b>\n"
                f"👤 <b>Username:</b> {user['username']} ({user['full_name']})\n"
                f"📧 <b>Email:</b> {user['email']}\n"
                f"👑 <b>Rejected By:</b> {admin_username}{reason_txt}\n"
                f"🕒 <b>Time:</b> {time_str}\n"
                f"<i>Login access permanently blocked.</i>"
            )

            return {"status": "success", "message": f"User '{user['username']}' 's registration rejected."}
        except Exception as e:
            log_event(f"Error rejecting user: {e}", component="AuthManager", level="ERROR")
            return {"status": "error", "error": str(e)}


    def get_audit_logs(self, limit: int = 40) -> List[Dict[str, Any]]:
        """Returns recent security and session audit logs."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT * FROM user_audit_logs
                ORDER BY created_at DESC
                LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                logs = []
                for r in rows:
                    dur_str = f"{r['duration_seconds']}s" if r["duration_seconds"] else "-"
                    logs.append({
                        "id": r["id"],
                        "username": r["username"] or "Unknown",
                        "event_type": r["event_type"],
                        "details": r["details"],
                        "ip_address": r["ip_address"] or "-",
                        "duration": dur_str,
                        "time_fmt": time.strftime('%d-%m %H:%M:%S', time.localtime(r["created_at"]))
                    })
                return logs
        except Exception as e:
            log_event(f"Error fetching audit logs: {e}", component="AuthManager", level="ERROR")
            return []

    def _record_audit_log(self, user_id: Optional[str], username: str, event_type: str, details: str, ip: str = "Unknown", ua: str = "Unknown", duration_seconds: int = 0):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO user_audit_logs (id, user_id, username, event_type, details, ip_address, user_agent, duration_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (f"audit_{uuid.uuid4().hex[:12]}", user_id, username, event_type, details, ip, ua, duration_seconds, time.time()))
                conn.commit()
        except Exception:
            pass

    def _notify_telegram(self, html_text: str):
        """Asynchronously dispatches Telegram notifications using the personal assistant agent."""
        try:
            import threading
            def _send():
                try:
                    from app.agents.assistant_agent import personal_assistant_agent
                    personal_assistant_agent.send_telegram_message(html_text, parse_mode="HTML")
                except Exception as e:
                    log_event(f"Telegram notify failed: {e}", component="AuthManager", level="WARNING")
            threading.Thread(target=_send, daemon=True).start()
        except Exception:
            pass

auth_manager = AuthManager()


