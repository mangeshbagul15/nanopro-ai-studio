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

/* Permissions Modal Overlay */
#nanoProPermissionsModal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(3, 7, 18, 0.88);
    z-index: 99999999;
    display: none;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(14px);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F8FAFC;
}

.perm-modal-card {
    width: 860px;
    max-width: 95vw;
    max-height: 92vh;
    background: #0F172A;
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 16px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 35px rgba(56, 189, 248, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: authFadeIn 0.25s ease-out;
}

.perm-modal-header {
    padding: 18px 24px;
    background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.perm-modal-body {
    padding: 20px 24px;
    overflow-y: auto;
    flex: 1;
}

.perm-section-title {
    font-size: 13px;
    font-weight: 700;
    color: #38BDF8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.perm-mode-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}

.perm-mode-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 14px 16px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.perm-mode-card:hover {
    border-color: #38BDF8;
    background: rgba(30, 41, 59, 0.9);
}

.perm-mode-card.active {
    border-color: #38BDF8;
    background: rgba(56, 189, 248, 0.12);
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
}

.perm-actions-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
    background: rgba(30, 41, 59, 0.45);
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.perm-preset-btn {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #E2E8F0;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
}

.perm-preset-btn:hover {
    background: #38BDF8;
    color: #0F172A;
    border-color: #38BDF8;
}

.perm-groups-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.perm-group-box {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    padding: 12px 14px;
}

.perm-group-title {
    font-size: 12px;
    font-weight: 700;
    color: #CBD5E1;
    margin-bottom: 8px;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.perm-item-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
    font-size: 12px;
    color: #94A3B8;
    cursor: pointer;
}

.perm-item-row:hover {
    color: #F8FAFC;
}

.perm-item-row input[type="checkbox"] {
    accent-color: #38BDF8;
    cursor: pointer;
    width: 15px;
    height: 15px;
}

.perm-modal-footer {
    padding: 14px 24px;
    background: #0B1120;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}
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

<!-- RBAC GRANULAR PERMISSIONS MODAL OVERLAY -->
<div id="nanoProPermissionsModal">
    <div class="perm-modal-card">
        <div class="perm-modal-header">
            <div>
                <h3 style="margin:0; font-size:16px; font-weight:800; color:#38BDF8; display:flex; align-items:center; gap:8px;">
                    🛡️ युझर प्रवेश अधिकार &amp; फिचर्स वाटप (User RBAC Permissions)
                </h3>
                <div style="font-size:12px; color:#94A3B8; margin-top:4px;">
                    युझर: <b id="permModalUsername" style="color:#FFFFFF;">-</b> | ईमेल: <span id="permModalEmail">-</span>
                </div>
            </div>
            <button type="button" onclick="closePermissionsModal()" style="background:none; border:none; color:#94A3B8; font-size:22px; cursor:pointer;" title="Close">&times;</button>
        </div>

        <div class="perm-modal-body">
            <!-- Hidden context fields -->
            <input type="hidden" id="permModalUserId" value="" />
            <input type="hidden" id="permModalActionType" value="update" />

            <!-- 1. ACCESS LEVEL SELECTION -->
            <div class="perm-section-title">
                <span>1. प्रवेश स्तर निवडा (Access Mode)</span>
            </div>
            <div class="perm-mode-grid">
                <label class="perm-mode-card active" id="modeCardModify" onclick="setPermAccessMode('MODIFY')">
                    <input type="radio" name="accessModeRadio" id="radioModeModify" value="MODIFY" checked style="accent-color:#38BDF8; margin-top:2px;">
                    <div>
                        <div style="font-weight:700; color:#38BDF8; font-size:13px;">✏️ MODIFY (पूर्ण अधिकार)</div>
                        <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">
                            युझरला सर्व डेटा तयार करणे, मॉडेल्स चालवणे, SQL रन करणे आणि एडिट करण्याचे पूर्ण अधिकार राहतील.
                        </div>
                    </div>
                </label>

                <label class="perm-mode-card" id="modeCardReadOnly" onclick="setPermAccessMode('READ_ONLY')">
                    <input type="radio" name="accessModeRadio" id="radioModeReadOnly" value="READ_ONLY" style="accent-color:#F59E0B; margin-top:2px;">
                    <div>
                        <div style="font-weight:700; color:#F59E0B; font-size:13px;">👁️ READ_ONLY (फक्त वाचन)</div>
                        <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">
                            युझर फक्त डॅशबोर्ड, चार्ट्स, रिपोर्ट्स आणि डेटा वाचू शकेल; कोणताही नवीन बदल किंवा डेटा डिलीट करता येणार नाही.
                        </div>
                    </div>
                </label>
            </div>

            <!-- 2. FEATURE SELECTION TOOLBAR -->
            <div class="perm-section-title">
                <span>2. डाव्या बाजूच्या फिचर्सची निवड (Left-Sidebar Navigation Features)</span>
            </div>
            <div class="perm-actions-toolbar">
                <button type="button" class="perm-preset-btn" onclick="selectAllPermFeatures(true)">✅ सर्व निवडा (Select All)</button>
                <button type="button" class="perm-preset-btn" onclick="selectAllPermFeatures(false)">❌ सर्व हटवा (Deselect All)</button>
                <button type="button" class="perm-preset-btn" onclick="selectPermPreset('data_stack')">📊 Data Stack Only</button>
                <button type="button" class="perm-preset-btn" onclick="selectPermPreset('ai_stack')">🤖 AI &amp; Automation Only</button>
                <button type="button" class="perm-preset-btn" onclick="selectPermPreset('media_comm')">💬 Comm &amp; Media</button>
            </div>

            <!-- 3. FEATURE CHECKBOXES (8 USER-ACCESSIBLE CATEGORIES) -->
            <div class="perm-groups-container">
                <!-- Group 1: AI Command Center -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>1. AI Command Center</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g1')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g1" value="dashboard"> Studio Overview</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g1" value="ai_manager"> AI Manager</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g1" value="ai_office"> AI Agent Office</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g1" value="models_hub"> AI Model Hub</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g1" value="agent_control"> Agent Operations</label>
                </div>

                <!-- Group 2: Data & Analytics -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>2. Data &amp; Analytics</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g2')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g2" value="data_engineer"> Data Engineering</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g2" value="data_analyst"> Data Analyst</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g2" value="data_science"> Data Science &amp; ML</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g2" value="learning_hub"> Learning SQL &amp; Drills</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g2" value="file_converter"> File Converter</label>
                </div>

                <!-- Group 3: Research & Security -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>3. Research &amp; Security</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g3')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g3" value="research_knowledge"> Research &amp; Knowledge</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g3" value="live_discovery"> Live Discovery</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g3" value="cyber_lab"> Cybersecurity Lab</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g3" value="book_reader"> Books &amp; Learning</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g3" value="research_library"> Research Library</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g3" value="research_agent"> Research Agent</label>
                </div>

                <!-- Group 4: Automation & Operations -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>4. Automation &amp; Operations</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g4')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g4" value="automation_scheduler"> Task Scheduler</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g4" value="task_history"> Task History</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g4" value="assistant"> Reminders &amp; Tasks</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g4" value="amazon_tracker"> Amazon Price Tracker</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g4" value="startup_recovery"> Startup Recovery</label>
                </div>

                <!-- Group 5: Data & Storage -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>5. Data &amp; Storage</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g5')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g5" value="storage_dashboard"> Storage Dashboard</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g5" value="vault"> Database Vault</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g5" value="cloud_trends"> Cloud Trends 2026</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g5" value="bitcoin_wallet"> Bitcoin Wallet &amp; Pay</label>
                </div>

                <!-- Group 6: Creation & Media -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>6. Creation &amp; Media</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g6')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="sql_video"> SQL Video Maker</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="python_video"> Python Video Maker</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="image_agent"> Image Maker</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="coding_agent"> Coding Agent</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="document_studio"> Document Studio</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="media_discovery"> Media Discovery</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g6" value="entertainment_center"> Entertainment Hub</label>
                </div>

                <!-- Group 7: Communication & Alerts -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>7. Communication &amp; Alerts</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g7')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g7" value="communication"> Communication Center</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g7" value="telegram_agent"> Telegram AI Agent</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g7" value="whatsapp_hub"> WhatsApp Hub</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g7" value="news_center"> News Center</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g7" value="approvals"> Action Approvals</label>
                </div>

                <!-- Group 8: Career & Developer -->
                <div class="perm-group-box">
                    <div class="perm-group-title">
                        <span>8. Career &amp; Developer</span>
                        <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g8')">Toggle</span>
                    </div>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g8" value="career_hub"> Career &amp; Job Search</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g8" value="free_apis"> Free API Finder</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g8" value="github_explorer"> GitHub Explorer</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g8" value="app_launcher"> App Launcher</label>
                    <label class="perm-item-row"><input type="checkbox" class="perm-cb g8" value="shopping_services"> Shopping Services</label>
                </div>
            </div>
        </div>

        <div class="perm-modal-footer">
            <button type="button" class="btn btn-secondary" onclick="closePermissionsModal()" style="padding:8px 16px;">रद्द करा (Cancel)</button>
            <button type="button" id="permModalSaveBtn" class="btn btn-primary" onclick="submitUserPermissions()" style="background:linear-gradient(135deg, #0284C7 0%, #2563EB 100%); padding:8px 20px; font-weight:700;">
                💾 अधिकार लागू करा (Save &amp; Apply)
            </button>
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

    // Apply granular RBAC feature permissions & sidebar pruning
    applyUserPermissions(user);

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
        const isSuperAdmin = (user.role === 'admin' || user.username === 'nanopro');
        const roleLabel = isSuperAdmin ? '<span style="color:#10B981; font-weight:bold;">[Admin]</span>' : '<span style="color:#38BDF8;">[User]</span>';
        const modeBadge = (!isSuperAdmin && user.access_mode === 'READ_ONLY') ? '<span style="color:#F59E0B; font-size:10px; border:1px solid #F59E0B; padding:1px 5px; border-radius:10px; margin-left:4px;">👁️ Read-Only</span>' : '';
        badge.innerHTML = `
            <div style="font-size:12px; color:#E2E8F0; background:rgba(30,41,59,0.7); padding:4px 10px; border-radius:20px; border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center;">
                👤 <b style="margin-left:4px;">${user.username}</b> ${roleLabel} ${modeBadge}
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

/* ========================================================================= */
/* RBAC PERMISSION CONTROLLERS & GRANULAR ACCESS FUNCTIONS                   */
/* ========================================================================= */
function setPermAccessMode(mode) {
    const radioMod = document.getElementById('radioModeModify');
    const radioRO = document.getElementById('radioModeReadOnly');
    if (radioMod) radioMod.checked = (mode === 'MODIFY');
    if (radioRO) radioRO.checked = (mode === 'READ_ONLY');
    const cardMod = document.getElementById('modeCardModify');
    const cardRO = document.getElementById('modeCardReadOnly');
    if (cardMod) cardMod.classList.toggle('active', mode === 'MODIFY');
    if (cardRO) cardRO.classList.toggle('active', mode === 'READ_ONLY');
}

function selectAllPermFeatures(checkVal) {
    document.querySelectorAll('.perm-cb').forEach(cb => { cb.checked = checkVal; });
}

function toggleGroupCheckboxes(groupClass) {
    const cbs = document.querySelectorAll('.perm-cb.' + groupClass);
    const anyUnchecked = Array.from(cbs).some(c => !c.checked);
    cbs.forEach(c => { c.checked = anyUnchecked; });
}

function selectPermPreset(preset) {
    selectAllPermFeatures(false);
    let views = [];
    if (preset === 'data_stack') {
        views = ['dashboard', 'data_engineer', 'data_analyst', 'data_science', 'learning_hub', 'file_converter', 'storage_dashboard', 'vault', 'cloud_trends'];
    } else if (preset === 'ai_stack') {
        views = ['dashboard', 'ai_manager', 'ai_office', 'models_hub', 'agent_control', 'automation_scheduler', 'task_history', 'assistant'];
    } else if (preset === 'media_comm') {
        views = ['dashboard', 'sql_video', 'python_video', 'image_agent', 'coding_agent', 'document_studio', 'communication', 'telegram_agent', 'whatsapp_hub', 'news_center'];
    }
    views.forEach(v => {
        const el = document.querySelector(`.perm-cb[value="${v}"]`);
        if (el) el.checked = true;
    });
}

function openPermissionsModal(userId, username, email, actionType='update', allowedViews=['*'], accessMode='MODIFY') {
    const uidEl = document.getElementById('permModalUserId');
    const atEl = document.getElementById('permModalActionType');
    const unEl = document.getElementById('permModalUsername');
    const emEl = document.getElementById('permModalEmail');
    if (uidEl) uidEl.value = userId;
    if (atEl) atEl.value = actionType;
    if (unEl) unEl.innerText = username;
    if (emEl) emEl.innerText = email || '-';
    
    setPermAccessMode(accessMode || 'MODIFY');

    if (!allowedViews || allowedViews.includes('*')) {
        selectAllPermFeatures(true);
    } else {
        selectAllPermFeatures(false);
        allowedViews.forEach(v => {
            const el = document.querySelector(`.perm-cb[value="${v}"]`);
            if (el) el.checked = true;
        });
    }

    const modal = document.getElementById('nanoProPermissionsModal');
    if (modal) modal.style.display = 'flex';
}

function closePermissionsModal() {
    const modal = document.getElementById('nanoProPermissionsModal');
    if (modal) modal.style.display = 'none';
}

async function submitUserPermissions() {
    const userId = document.getElementById('permModalUserId').value;
    const actionType = document.getElementById('permModalActionType').value;
    const radioChecked = document.querySelector('input[name="accessModeRadio"]:checked');
    const accessMode = radioChecked ? radioChecked.value : 'MODIFY';

    const allCheckboxes = document.querySelectorAll('.perm-cb');
    const checkedCheckboxes = document.querySelectorAll('.perm-cb:checked');

    let allowedViews = [];
    if (checkedCheckboxes.length === allCheckboxes.length) {
        allowedViews = ['*'];
    } else {
        checkedCheckboxes.forEach(cb => allowedViews.push(cb.value));
    }

    if (allowedViews.length === 0) {
        alert('कृपया किमान एक तरी फिचर निवडा!');
        return;
    }

    const btn = document.getElementById('permModalSaveBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'जतन करत आहे...';
    }

    try {
        const endpoint = (actionType === 'approve') ? '/api/admin/users/approve' : '/api/admin/users/permissions';
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                admin_username: currentUser ? currentUser.username : 'nanopro',
                allowed_views: allowedViews,
                access_mode: accessMode
            })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            alert('✅ ' + (data.message || 'अधिकार यशस्वीरीत्या लागू करण्यात आले!'));
            closePermissionsModal();
            loadAdminUsers();
        } else {
            alert('त्रुटी: ' + (data.error || 'अधिकार जतन करता आले नाहीत!'));
        }
    } catch (err) {
        alert('सर्व्हर त्रुटी: ' + err.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = '💾 अधिकार लागू करा (Save & Apply)';
        }
    }
}

// Client-side RBAC pruning & guard
function applyUserPermissions(user) {
    if (!user) return;
    const isSuperAdmin = (user.role === 'admin' || user.username === 'nanopro');
    const allowed = user.allowed_views || ['*'];
    const hasAll = isSuperAdmin || allowed.includes('*');

    // Filter sidebar navigation items
    document.querySelectorAll('.nav-group').forEach(group => {
        let visibleCount = 0;
        const isSystemGroup = (group.id === 'navGroup-system-mgmt');

        group.querySelectorAll('.nav-item').forEach(item => {
            const oc = item.getAttribute('onclick') || '';
            const match = oc.match(/switchView\(['"]([^'"]+)['"]\)/);
            if (match) {
                const v = match[1];
                if (v === 'user_management') {
                    item.style.display = isSuperAdmin ? 'flex' : 'none';
                    if (isSuperAdmin) visibleCount++;
                    return;
                }
                if (hasAll || allowed.includes(v)) {
                    item.style.display = 'flex';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            }
        });

        // If no items are visible in this group (and not super admin), hide the group
        if (!hasAll && visibleCount === 0) {
            group.style.display = 'none';
        } else {
            group.style.display = 'block';
        }
    });

    // Handle access mode banner
    const mode = user.access_mode || 'MODIFY';
    let banner = document.getElementById('nanoProReadOnlyBanner');
    if (mode === 'READ_ONLY' && !isSuperAdmin) {
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'nanoProReadOnlyBanner';
            banner.style.cssText = 'background:linear-gradient(90deg, rgba(245,158,11,0.25) 0%, rgba(239,68,68,0.2) 100%); border-bottom:1px solid rgba(245,158,11,0.5); color:#FCD34D; font-size:12px; font-weight:700; padding:6px 16px; display:flex; align-items:center; justify-content:space-between; position:fixed; top:0; left:0; width:100%; z-index:99999; backdrop-filter:blur(8px);';
            banner.innerHTML = `
                <div style="display:flex; align-items:center; gap:8px;">
                    <span>👁️ <b>फक्त वाचन मोड (Read-Only Mode):</b> तुमचे खाते व्ह्यू-ओन्ली मोडमध्ये आहे. तुम्ही डेटा पाहू शकता, नवीन बदल किंवा एडिट करू शकत नाही.</span>
                </div>
                <span style="font-size:11px; background:rgba(0,0,0,0.4); border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:4px;">RBAC Enforced</span>
            `;
            document.body.appendChild(banner);
        } else {
            banner.style.display = 'flex';
        }
    } else if (banner) {
        banner.style.display = 'none';
    }

    // Switch view if current active view is unauthorized
    if (!hasAll && typeof currentActiveView !== 'undefined' && currentActiveView && !allowed.includes(currentActiveView)) {
        const firstAllowed = allowed[0] || 'dashboard';
        if (typeof switchView === 'function') {
            switchView(firstAllowed);
        }
    }
}

// Global guard for switchView
window.checkViewAllowed = function(viewName) {
    if (!currentUser) return true;
    if (currentUser.role === 'admin' || currentUser.username === 'nanopro') return true;
    const allowed = currentUser.allowed_views || ['*'];
    if (allowed.includes('*') || allowed.includes(viewName)) return true;
    
    alert(`🚫 प्रवेश नाकारला (Access Denied): तुम्हाला '${viewName}' या फिचरचे अधिकार नाहीत.\nकृपया Admin 'nanopro' शी संपर्क साधा.`);
    return false;
};

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
            
            const mode = u.access_mode || 'MODIFY';
            const modeBadge = (mode === 'READ_ONLY') 
                ? '<span style="background:rgba(245,158,11,0.15); color:#F59E0B; border:1px solid #F59E0B; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">👁️ READ-ONLY</span>' 
                : '<span style="background:rgba(56,189,248,0.15); color:#38BDF8; border:1px solid #38BDF8; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">✏️ MODIFY</span>';

            const views = u.allowed_views || ['*'];
            const featuresBadge = (views.includes('*'))
                ? '<span style="background:rgba(16,185,129,0.15); color:#10B981; border:1px solid #10B981; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">All (सर्व ४२)</span>'
                : `<span style="background:rgba(168,85,247,0.15); color:#C084FC; border:1px solid #A855F7; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">${views.length} Features</span>`;

            let actionsHtml = '';
            const viewsJson = JSON.stringify(views).replace(/"/g, '&quot;');
            if (u.status === 'PENDING_APPROVAL') {
                actionsHtml = `<button class="btn-action-sm btn-approve" onclick="openPermissionsModal('${u.id}', '${u.username}', '${u.email}', 'approve', ${viewsJson}, '${mode}')">🛡️ मंजूर करा (Approve)</button>`;
            } else if (u.username !== 'nanopro') {
                const nextSt = (u.status === 'ACTIVE') ? 'DISABLED' : 'ACTIVE';
                const btnLabel = (u.status === 'ACTIVE') ? 'Disable 🚫' : 'Enable ✅';
                const btnClass = (u.status === 'ACTIVE') ? 'btn-disable' : 'btn-enable';
                actionsHtml = `
                    <button class="btn-action-sm" style="background:#6366F1; color:#FFFFFF; margin-right:4px;" onclick="openPermissionsModal('${u.id}', '${u.username}', '${u.email}', 'update', ${viewsJson}, '${mode}')">⚙️ अधिकार</button>
                    <button class="btn-action-sm ${btnClass}" onclick="toggleUserStatus('${u.id}', '${nextSt}')">${btnLabel}</button>
                `;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${u.username}</b></td>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td><span style="text-transform:uppercase; font-size:11px; font-weight:bold;">${u.role}</span></td>
                <td><span class="${statusClass}">${u.status}</span></td>
                <td>${modeBadge}</td>
                <td>${featuresBadge}</td>
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
                                <th>Access Mode</th>
                                <th>Allowed Features</th>
                                <th>Last Login</th>
                                <th>Total Usage</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="adminUsersTableBody">
                            <tr><td colspan="10" style="text-align:center; padding:18px; color:#94A3B8;">युझर्स लोड होत आहेत...</td></tr>
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

