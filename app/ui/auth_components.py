"""
Mangesh Nano Pro AI Studio - Enterprise Authentication Gateway & User Management UI Components
Provides cyber-dark login/registration modal, user approval interface, inactivity timers, and audit trail.
"""

def get_auth_injection() -> str:
    return """
<!-- ========================================================================= -->
<!-- NANOPRO ENTERPRISE AUTHENTICATION GATEWAY & USER MANAGEMENT OVERLAY       -->
<!-- ========================================================================= -->
<style>
/* Security Gateway Overlay */
#nanoProAuthGateway {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at 50% 30%, #0F172A 0%, #030712 100%);
    z-index: 9999999;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(16px);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F8FAFC;
}

.auth-card {
    width: 480px;
    max-width: 92vw;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 16px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 40px rgba(56, 189, 248, 0.15);
    overflow: hidden;
    animation: authFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes authFadeIn {
    from { opacity: 0; transform: scale(0.96) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

.auth-header {
    padding: 24px 28px 16px;
    text-align: center;
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.auth-logo-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.3);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    color: #38BDF8;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.auth-title {
    font-size: 22px;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 6px;
    letter-spacing: -0.5px;
}

.auth-subtitle {
    font-size: 13px;
    color: #94A3B8;
    margin: 0;
}

.auth-tabs {
    display: flex;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(10, 15, 29, 0.6);
}

.auth-tab-btn {
    flex: 1;
    padding: 13px 0;
    background: none;
    border: none;
    color: #94A3B8;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
}

.auth-tab-btn.active {
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.05);
}

.auth-tab-btn.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 20%;
    width: 60%;
    height: 2px;
    background: #38BDF8;
    box-shadow: 0 0 10px #38BDF8;
}

.auth-body {
    padding: 24px 28px 28px;
}

.auth-form-group {
    margin-bottom: 16px;
}

.auth-form-group label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: #CBD5E1;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.auth-input {
    width: 100%;
    padding: 11px 14px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #FFFFFF;
    font-size: 14px;
    box-sizing: border-box;
    transition: all 0.2s;
}

.auth-input:focus {
    outline: none;
    border-color: #38BDF8;
    background: rgba(30, 41, 59, 0.9);
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

.pwd-rules-box {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 10px 14px;
    margin-top: 8px;
    font-size: 11.5px;
}

.pwd-rule-item {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #94A3B8;
    margin-bottom: 4px;
}

.pwd-rule-item:last-child { margin-bottom: 0; }
.pwd-rule-item.valid { color: #10B981; }
.pwd-rule-item.valid::before { content: '✔'; font-weight: bold; }
.pwd-rule-item.invalid::before { content: '○'; }

.auth-alert-box {
    padding: 11px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    line-height: 1.4;
    margin-bottom: 16px;
    display: none;
}

.auth-alert-error {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #FCA5A5;
}

.auth-alert-warning {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #FCD34D;
}

.auth-alert-success {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #6EE7B7;
}

.auth-btn-primary {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%);
    border: none;
    border-radius: 8px;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35);
    transition: all 0.2s;
}

.auth-btn-primary:hover {
    background: linear-gradient(135deg, #0369A1 0%, #1D4ED8 100%);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
    transform: translateY(-1px);
}

.auth-btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.auth-footer-hint {
    margin-top: 16px;
    font-size: 11.5px;
    color: #64748B;
    text-align: center;
}

/* User Management Panel Styles */
.user-mgmt-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.mgmt-stat-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 22px;
}

.mgmt-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
}

.mgmt-card-num {
    font-size: 24px;
    font-weight: 800;
    color: #38BDF8;
    margin-top: 4px;
}

.mgmt-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
}

.mgmt-table th {
    background: rgba(30, 41, 59, 0.7);
    color: #94A3B8;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.mgmt-table td {
    padding: 11px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #E2E8F0;
}

.status-badge-active { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid #10B981; padding: 2px 8px; border-radius: 12px; font-size: 11px; }
.status-badge-pending { background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid #F59E0B; padding: 2px 8px; border-radius: 12px; font-size: 11px; }
.status-badge-disabled { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid #EF4444; padding: 2px 8px; border-radius: 12px; font-size: 11px; }

.btn-action-sm {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.15s;
}

.btn-approve { background: #10B981; color: #FFFFFF; }
.btn-approve:hover { background: #059669; }
.btn-disable { background: #EF4444; color: #FFFFFF; }
.btn-disable:hover { background: #DC2626; }
.btn-enable { background: #0284C7; color: #FFFFFF; }
.btn-enable:hover { background: #0369A1; }
</style>

<!-- AUTHENTICATION GATEWAY MODAL OVERLAY -->
<div id="nanoProAuthGateway">
    <div class="auth-card">
        <div class="auth-header">
            <div class="auth-logo-badge">🛡️ Enterprise Security Gateway</div>
            <h1 class="auth-title">MANGESH NANO PRO</h1>
            <p class="auth-subtitle">Intelligent AI & Autonomous Multi-Agent Studio v14</p>
        </div>

        <div class="auth-tabs">
            <button type="button" class="auth-tab-btn active" id="tabBtnLogin" onclick="switchAuthTab('login')">लॉगिन (Sign In)</button>
            <button type="button" class="auth-tab-btn" id="tabBtnRegister" onclick="switchAuthTab('register')">नवीन नोंदणी (Sign Up)</button>
        </div>

        <div class="auth-body">
            <!-- Alert message box -->
            <div id="authAlertBox" class="auth-alert-box"></div>

            <!-- LOGIN FORM -->
            <form id="authLoginForm" onsubmit="handleAuthLogin(event)">
                <div class="auth-form-group">
                    <label>युझरनेम (Username)</label>
                    <input type="text" id="loginUsername" class="auth-input" placeholder="उदा. nanopro" required autocomplete="username" />
                </div>
                <div class="auth-form-group">
                    <label>पासवर्ड (Password)</label>
                    <input type="password" id="loginPassword" class="auth-input" placeholder="••••••••••••" required autocomplete="current-password" />
                </div>
                <button type="submit" id="loginSubmitBtn" class="auth-btn-primary">🔐 सुरक्षित लॉगिन करा (Sign In)</button>
                <div class="auth-footer-hint">
                    Default Master Admin: <b>nanopro</b> | Pass: <b>Divyam@123</b>
                </div>
            </form>

            <!-- REGISTRATION FORM -->
            <form id="authRegisterForm" style="display:none;" onsubmit="handleAuthRegister(event)">
                <div class="auth-form-group">
                    <label>पूर्ण नाव (Full Name)</label>
                    <input type="text" id="regFullName" class="auth-input" placeholder="उदा. Rahul Sharma" required />
                </div>
                <div class="auth-form-group">
                    <label>युझरनेम (Username - 3 to 20 chars)</label>
                    <input type="text" id="regUsername" class="auth-input" placeholder="उदा. rahul_de" required />
                </div>
                <div class="auth-form-group">
                    <label>ईमेल आयडी (Email ID)</label>
                    <input type="email" id="regEmail" class="auth-input" placeholder="उदा. user@company.com" required />
                </div>
                <div class="auth-form-group">
                    <label>पासवर्ड (Password)</label>
                    <input type="password" id="regPassword" class="auth-input" placeholder="••••••••••••" oninput="checkPasswordRules(this.value)" required />
                    
                    <!-- Real-time Security Checklist -->
                    <div class="pwd-rules-box">
                        <div id="ruleLength" class="pwd-rule-item invalid">किमान ८ अक्षरे (8+ Characters)</div>
                        <div id="ruleUpper" class="pwd-rule-item invalid">एक मोठे अक्षर (Uppercase A-Z)</div>
                        <div id="ruleLower" class="pwd-rule-item invalid">एक लहान अक्षर (Lowercase a-z)</div>
                        <div id="ruleNumber" class="pwd-rule-item invalid">एक अंक (Number 0-9)</div>
                        <div id="ruleSpecial" class="pwd-rule-item invalid">एक विशेष चिन्ह (@$!%*?&#)</div>
                    </div>
                </div>
                <button type="submit" id="regSubmitBtn" class="auth-btn-primary">📝 खाते तयार करा (Submit for Approval)</button>
                <div class="auth-footer-hint">
                    सुरक्षा धोरण: नोंदणीनंतर ॲडमिन (nanopro) कडून मंजुरी मिळाल्यावरच खाते सक्रिय होईल.
                </div>
            </form>
        </div>
    </div>
</div>

<!-- ========================================================================= -->
<!-- JAVASCRIPT: AUTHENTICATION, IDLE TIMEOUT & USER MANAGEMENT CONTROLLER     -->
<!-- ========================================================================= -->
<script>
let currentUser = null;
let currentSessionToken = localStorage.getItem('nanopro_session_token');
let idleLogoutTimer = null;
const IDLE_LIMIT_MS = 15 * 60 * 1000; // 15 Minutes for regular users

function switchAuthTab(tab) {
    const alertBox = document.getElementById('authAlertBox');
    if (alertBox) alertBox.style.display = 'none';

    document.getElementById('tabBtnLogin').classList.toggle('active', tab === 'login');
    document.getElementById('tabBtnRegister').classList.toggle('active', tab === 'register');
    document.getElementById('authLoginForm').style.display = (tab === 'login') ? 'block' : 'none';
    document.getElementById('authRegisterForm').style.display = (tab === 'register') ? 'block' : 'none';
}

function checkPasswordRules(pwd) {
    const lengthValid = pwd.length >= 8;
    const upperValid = /[A-Z]/.test(pwd);
    const lowerValid = /[a-z]/.test(pwd);
    const numValid = /[0-9]/.test(pwd);
    const specialValid = /[@$!%*?&#^+=~-]/.test(pwd);

    updateRuleElem('ruleLength', lengthValid);
    updateRuleElem('ruleUpper', upperValid);
    updateRuleElem('ruleLower', lowerValid);
    updateRuleElem('ruleNumber', numValid);
    updateRuleElem('ruleSpecial', specialValid);

    return (lengthValid && upperValid && lowerValid && numValid && specialValid);
}

function updateRuleElem(id, isValid) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'pwd-rule-item ' + (isValid ? 'valid' : 'invalid');
}

function showAuthAlert(msg, type='error') {
    const box = document.getElementById('authAlertBox');
    if (!box) return;
    box.className = 'auth-alert-box auth-alert-' + type;
    box.innerHTML = msg;
    box.style.display = 'block';
}

async function handleAuthLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('loginSubmitBtn');
    btn.disabled = true;
    btn.innerText = 'पडताळणी करत आहे...';

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    try {
        const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, password })
        });
        const data = await resp.json();

        if (data.status === 'success') {
            localStorage.setItem('nanopro_session_token', data.session_token);
            currentSessionToken = data.session_token;
            currentUser = data.user;
            onAuthSuccess(data.user);
        } else {
            showAuthAlert(data.error || 'लॉगिन अयशस्वी!', 'error');
        }
    } catch (err) {
        showAuthAlert('सर्व्हरशी संपर्क होऊ शकला नाही: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = '🔐 सुरक्षित लॉगिन करा (Sign In)';
    }
}

async function handleAuthRegister(e) {
    e.preventDefault();
    const pwd = document.getElementById('regPassword').value;
    if (!checkPasswordRules(pwd)) {
        showAuthAlert('कृपया सर्व पासवर्ड सुरक्षा नियम पूर्ण करा.', 'error');
        return;
    }

    const btn = document.getElementById('regSubmitBtn');
    btn.disabled = true;
    btn.innerText = 'नोंदणी करत आहे...';

    const payload = {
        full_name: document.getElementById('regFullName').value.trim(),
        username: document.getElementById('regUsername').value.trim(),
        email: document.getElementById('regEmail').value.trim(),
        password: pwd
    };

    try {
        const resp = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await resp.json();

        if (data.status === 'success') {
            showAuthAlert('<b>' + data.message + '</b>', 'warning');
            document.getElementById('authRegisterForm').reset();
            setTimeout(() => switchAuthTab('login'), 3500);
        } else {
            showAuthAlert(data.error || 'नोंदणी अयशस्वी!', 'error');
        }
    } catch (err) {
        showAuthAlert('त्रुटी आली: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = '📝 खाते तयार करा (Submit for Approval)';
    }
}

function onAuthSuccess(user) {
    currentUser = user;
    const gateway = document.getElementById('nanoProAuthGateway');
    if (gateway) gateway.style.display = 'none';

    // Show User info in top header
    updateHeaderUserProfile(user);

    // Show User Management menu item if Admin
    const navMgmt = document.getElementById('nav_user_management');
    if (navMgmt) {
        navMgmt.style.display = (user.role === 'admin' || user.username === 'nanopro') ? 'flex' : 'none';
    }

    // Start Inactivity Timer for regular users
    startInactivityTracker(user);
}

function updateHeaderUserProfile(user) {
    let badge = document.getElementById('headerUserBadge');
    if (!badge) {
        const topHeader = document.querySelector('.header-right-group');
        if (topHeader) {
            badge = document.createElement('div');
            badge.id = 'headerUserBadge';
            badge.style.display = 'flex';
            badge.style.alignItems = 'center';
            badge.style.gap = '8px';
            badge.style.marginLeft = '12px';
            topHeader.appendChild(badge);
        }
    }
    if (badge) {
        const roleLabel = (user.role === 'admin') ? '<span style="color:#10B981; font-weight:bold;">[Admin]</span>' : '<span style="color:#38BDF8;">[User]</span>';
        badge.innerHTML = `
            <div style="font-size:12px; color:#E2E8F0; background:rgba(30,41,59,0.7); padding:4px 10px; border-radius:20px; border:1px solid rgba(255,255,255,0.1);">
                👤 <b>${user.username}</b> ${roleLabel}
            </div>
            <button type="button" onclick="performLogout()" style="background:rgba(239,68,68,0.15); border:1px solid #EF4444; color:#FCA5A5; padding:4px 8px; border-radius:6px; cursor:pointer; font-size:11.5px; font-weight:bold;" title="Sign Out">
                Logout 🚪
            </button>
        `;
    }
}

function startInactivityTracker(user) {
    if (user.role === 'admin' || user.username === 'nanopro') {
        // Admin is immune to auto-logout
        return;
    }

    const resetTimer = () => {
        if (idleLogoutTimer) clearTimeout(idleLogoutTimer);
        idleLogoutTimer = setTimeout(triggerAutoLogout, IDLE_LIMIT_MS);
    };

    ['mousemove', 'keydown', 'click', 'scroll'].forEach(evt => {
        window.addEventListener(evt, resetTimer, { passive: true });
    });
    resetTimer();
}

async function triggerAutoLogout() {
    alert('⏱️ सुरक्षा सूचना: १५ मिनिटांच्या निष्क्रियतेमुळे (Inactivity) तुमचे सत्र आपोआप बंद होत आहे.');
    await performLogout(true);
}

async function performLogout(isAuto=false) {
    try {
        if (currentSessionToken) {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_token: currentSessionToken })
            });
        }
    } catch(e){}
    localStorage.removeItem('nanopro_session_token');
    currentSessionToken = null;
    currentUser = null;
    location.reload();
}

// Initial Session Verification on Page Load
document.addEventListener('DOMContentLoaded', async () => {
    if (currentSessionToken) {
        try {
            const resp = await fetch('/api/auth/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_token: currentSessionToken })
            });
            const data = await resp.json();
            if (data.is_valid && data.user) {
                onAuthSuccess(data.user);
                return;
            }
        } catch(e){}
    }
    // If not authenticated, ensure gateway is visible
    const gateway = document.getElementById('nanoProAuthGateway');
    if (gateway) gateway.style.display = 'flex';
});

/* --- ADMIN USER MANAGEMENT APIS --- */
async function loadAdminUsers() {
    try {
        const resp = await fetch('/api/admin/users/list');
        const data = await resp.json();
        const tbody = document.getElementById('adminUsersTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';
        let total = 0, pending = 0, active = 0;

        (data.users || []).forEach(u => {
            total++;
            if (u.status === 'PENDING_APPROVAL') pending++;
            if (u.status === 'ACTIVE') active++;

            const statusClass = (u.status === 'ACTIVE') ? 'status-badge-active' : (u.status === 'PENDING_APPROVAL' ? 'status-badge-pending' : 'status-badge-disabled');
            
            let actionsHtml = '';
            if (u.status === 'PENDING_APPROVAL') {
                actionsHtml = `<button class="btn-action-sm btn-approve" onclick="approveUser('${u.id}')">Approve ✔️</button>`;
            } else if (u.username !== 'nanopro') {
                const nextSt = (u.status === 'ACTIVE') ? 'DISABLED' : 'ACTIVE';
                const btnLabel = (u.status === 'ACTIVE') ? 'Disable 🚫' : 'Enable ✅';
                const btnClass = (u.status === 'ACTIVE') ? 'btn-disable' : 'btn-enable';
                actionsHtml = `<button class="btn-action-sm ${btnClass}" onclick="toggleUserStatus('${u.id}', '${nextSt}')">${btnLabel}</button>`;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${u.username}</b></td>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td><span style="text-transform:uppercase; font-size:11px; font-weight:bold;">${u.role}</span></td>
                <td><span class="${statusClass}">${u.status}</span></td>
                <td>${u.last_login_fmt}</td>
                <td>${u.total_usage_fmt}</td>
                <td>${actionsHtml}</td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('statTotalUsers').innerText = total;
        document.getElementById('statPendingUsers').innerText = pending;
        document.getElementById('statActiveUsers').innerText = active;

        loadAdminAuditLogs();
    } catch (err) {
        console.error('Error loading admin users:', err);
    }
}

async function approveUser(userId) {
    if (!confirm('या युझरला NanoPro वापरण्याची मंजुरी (Approve) द्यायची का?')) return;
    try {
        const resp = await fetch('/api/admin/users/approve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, admin_username: currentUser ? currentUser.username : 'nanopro' })
        });
        const data = await resp.json();
        alert(data.message || 'युझर मंजूर झाला!');
        loadAdminUsers();
    } catch(e) { alert('त्रुटी: ' + e.message); }
}

async function toggleUserStatus(userId, newStatus) {
    try {
        const resp = await fetch('/api/admin/users/toggle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, status: newStatus })
        });
        const data = await resp.json();
        alert(data.message);
        loadAdminUsers();
    } catch(e) { alert('त्रुटी: ' + e.message); }
}

async function triggerTelegramDiagnosticsNow() {
    const btn = document.getElementById('btnTriggerTelegramDiag');
    if (btn) { btn.disabled = true; btn.innerText = 'Telegram ला पाठवत आहे...'; }
    try {
        const resp = await fetch('/api/telegram/send_diagnostics_now', { method: 'POST' });
        const data = await resp.json();
        alert('✅ ३-तासी सिस्टीम आरोग्य अहवाल Telegram ला त्वरित पाठवला गेला आहे!');
    } catch(e) { alert('त्रुटी: ' + e.message); }
    finally {
        if (btn) { btn.disabled = false; btn.innerText = '📱 Send Telegram Health Audit Now'; }
    }
}

async function loadAdminAuditLogs() {
    try {
        const resp = await fetch('/api/admin/audit_logs');
        const data = await resp.json();
        const tbody = document.getElementById('adminAuditLogsBody');
        if (!tbody) return;

        tbody.innerHTML = '';
        (data.logs || []).slice(0, 15).forEach(l => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span style="color:#94A3B8;">${l.time_fmt}</span></td>
                <td><b>${l.username}</b></td>
                <td><span class="badge" style="background:#1E293B; color:#38BDF8;">${l.event_type}</span></td>
                <td>${l.details}</td>
                <td>${l.ip_address}</td>
                <td>${l.duration}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e){}
}
</script>
"""

def get_user_management_view_html() -> str:
    """Returns the Admin-only User Management and Security Governance Workspace View."""
    return """
        <!-- VIEW: USER MANAGEMENT & SECURITY GOVERNANCE (ADMIN ONLY) -->
        <div class="workspace-view" id="view-user_management">
            <!-- Header Hero Panel -->
            <div class="panel-card" style="margin-bottom:16px; background:linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.9) 100%); border:1px solid #38BDF8;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div style="display:flex; align-items:center; gap:14px;">
                        <div style="width:48px; height:48px; border-radius:50%; background:radial-gradient(circle, #38BDF8 20%, #1E40AF 90%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 16px rgba(56,189,248,0.4); font-size:24px;">
                            🛡️
                        </div>
                        <div>
                            <h2 style="margin:0; font-size:17px; color:#F8FAFC; display:flex; align-items:center; gap:8px;">
                                युझर व्यवस्थापन &amp; सुरक्षा प्रशासन (User Management &amp; Security Control)
                                <span class="badge" style="background:#0F172A; border:1px solid #10B981; color:#10B981; font-size:11px;">ADMIN ONLY</span>
                            </h2>
                            <span style="font-size:12px; color:#94A3B8;">
                                नवीन खात्यांना मंजुरी (Approval Workflow), सत्र नियंत्रण, 15-Min Inactivity Auto-Logout, आणि तात्काळ 3-Hour Telegram हेल्थ ऑडिट
                            </span>
                        </div>
                    </div>
                    <div style="display:flex; gap:8px; flex-wrap:wrap;">
                        <button type="button" id="btnTriggerTelegramDiag" class="btn btn-primary" onclick="triggerTelegramDiagnosticsNow()" style="background:#0284C7; font-weight:700; font-size:11.5px; padding:7px 14px;">
                            📱 Send Telegram Health Audit Now
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="loadAdminUsers()" style="font-size:11.5px; padding:7px 14px;">
                            🔄 Refresh Users
                        </button>
                    </div>
                </div>
            </div>

            <!-- KPI Grid -->
            <div class="mgmt-stat-cards">
                <div class="mgmt-card" style="border-left:4px solid #38BDF8;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">एकूण नोंदणीकृत (Total Users)</div>
                    <div class="mgmt-card-num" id="statTotalUsers">0</div>
                    <div style="font-size:11px; color:#38BDF8;">Enterprise Directory</div>
                </div>
                <div class="mgmt-card" style="border-left:4px solid #F59E0B;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">मंजुरी प्रलंबित (Pending Approval)</div>
                    <div class="mgmt-card-num" id="statPendingUsers" style="color:#F59E0B;">0</div>
                    <div style="font-size:11px; color:#F59E0B;">प्रवेश बंदी (Needs Approval)</div>
                </div>
                <div class="mgmt-card" style="border-left:4px solid #10B981;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">सक्रिय खाती (Active Users)</div>
                    <div class="mgmt-card-num" id="statActiveUsers" style="color:#10B981;">0</div>
                    <div style="font-size:11px; color:#10B981;">Verified Accounts</div>
                </div>
                <div class="mgmt-card" style="border-left:4px solid #A855F7;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">ऑटो-लॉगआउट धोरण (Inactivity Rule)</div>
                    <div class="mgmt-card-num" style="color:#A855F7; font-size:18px;">15 Minutes</div>
                    <div style="font-size:11px; color:#94A3B8;">Admin (nanopro) Exempt</div>
                </div>
            </div>

            <!-- Registered Users Management Table -->
            <div class="panel-card" style="margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0; font-size:14px; font-weight:700; color:#38BDF8; display:flex; align-items:center; gap:6px;">
                        👥 नोंदणीकृत युझर्स &amp; मंजुरी यादी (User Approval &amp; Role Management)
                    </h3>
                    <span style="font-size:11.5px; color:#94A3B8;">फक्त Admin 'nanopro' ला खाती चालू/बंद करण्याचे अधिकार आहेत</span>
                </div>
                <div style="overflow-x:auto;">
                    <table class="mgmt-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Full Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Last Login</th>
                                <th>Total Usage</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="adminUsersTableBody">
                            <tr><td colspan="8" style="text-align:center; padding:18px; color:#94A3B8;">युझर्स लोड होत आहेत...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Security & Audit Log Table -->
            <div class="panel-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0; font-size:14px; font-weight:700; color:#10B981; display:flex; align-items:center; gap:6px;">
                        📜 सुरक्षा ऑडिट ट्रेल &amp; लॉगिन हिस्ट्री (Real-Time Security &amp; Audit Logs)
                    </h3>
                    <button type="button" class="btn btn-secondary" onclick="loadAdminAuditLogs()" style="font-size:10.5px; padding:4px 8px;">Refresh Logs</button>
                </div>
                <div style="overflow-x:auto;">
                    <table class="mgmt-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>User</th>
                                <th>Event</th>
                                <th>Details</th>
                                <th>IP Address</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody id="adminAuditLogsBody">
                            <tr><td colspan="6" style="text-align:center; padding:18px; color:#94A3B8;">ऑडिट लॉग लोड होत आहेत...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """

