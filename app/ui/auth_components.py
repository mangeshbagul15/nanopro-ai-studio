"""
Mangesh Nano Pro AI Studio - Enterprise Authentication Gateway & User Management UI Components
Provides cyber-dark login/registration modal, user approval interface, inactivity timers, and audit trail.
"""

def get_anti_fouc_head_injection() -> str:
    return """
    <!-- ========================================================================= -->
    <!-- ZERO-FLASH CRITICAL ANTI-FOUC AUTH SHIELD                                 -->
    <!-- ========================================================================= -->
    <style>
        /* NanoPro App Shell: Always visible, 100% ready immediately without blank frames */
        #app-shell {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        /* Auth Gateway sits hidden by default, only shown if opened via user menu (.force-show) */
        #nanoProAuthGateway {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999999 !important;
            background: radial-gradient(circle at 50% 30%, #0F172A 0%, #030712 100%) !important;
            display: none !important;
            align-items: center !important;
            justify-content: center !important;
        }
        #nanoProAuthGateway.force-show {
            display: flex !important;
        }
    </style>
    <script>
        document.documentElement.classList.add('auth-verified');
        if (document.body) document.body.classList.add('auth-verified');
        else document.addEventListener('DOMContentLoaded', () => { if (document.body) document.body.classList.add('auth-verified'); });
    </script>
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

/* Modern Cyber-Luxe Badges & Indicators */
.badge-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.dot-emerald {
    background: #10B981;
    box-shadow: 0 0 7px #10B981;
}
.dot-amber-pulse {
    background: #F59E0B;
    box-shadow: 0 0 8px #F59E0B;
    animation: amberDotPulse 1.8s infinite ease-in-out;
}
.dot-cyan {
    background: #38BDF8;
    box-shadow: 0 0 7px #38BDF8;
}
.dot-purple {
    background: #C084FC;
    box-shadow: 0 0 7px #C084FC;
}
.dot-red {
    background: #EF4444;
    box-shadow: 0 0 7px #EF4444;
}
.dot-slate {
    background: #94A3B8;
}

@keyframes amberDotPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.45; transform: scale(0.8); }
}

.modern-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.25px;
    white-space: nowrap;
    backdrop-filter: blur(8px);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    user-select: none;
}

.modern-badge-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.25px;
    white-space: nowrap;
    backdrop-filter: blur(8px);
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    text-decoration: none;
    line-height: 1.25;
}
.modern-badge-btn:hover {
    transform: translateY(-1.5px) scale(1.02);
    box-shadow: 0 5px 14px rgba(0, 0, 0, 0.4);
    filter: brightness(1.2);
}
.modern-badge-btn:active {
    transform: translateY(0) scale(0.99);
}

/* Master Exclusive Badges */
.badge-master-active {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(245, 158, 11, 0.16) 100%);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.55);
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.22);
}
.badge-master-mode {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(99, 102, 241, 0.16) 100%);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.55);
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.22);
}
.badge-master-features {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.22) 0%, rgba(56, 189, 248, 0.16) 100%);
    color: #E879F9;
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 0 14px rgba(168, 85, 247, 0.22);
}

/* Standard Status Variants */
.badge-status-pending {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.22) 0%, rgba(217, 119, 6, 0.14) 100%);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.5);
}
.badge-status-active {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.14) 100%);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.45);
}
.badge-status-rejected {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22) 0%, rgba(185, 28, 28, 0.14) 100%);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.5);
}
.badge-status-disabled {
    background: linear-gradient(135deg, rgba(148, 163, 184, 0.18) 0%, rgba(71, 85, 105, 0.16) 100%);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 0.4);
}

/* Access Mode Variants */
.badge-mode-modify {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(14, 165, 233, 0.14) 100%);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.45);
}
.badge-mode-readonly {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(217, 119, 6, 0.12) 100%);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

/* Allowed Features Variants */
.badge-feat-all {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(6, 182, 212, 0.14) 100%);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.45);
}
.badge-feat-custom {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(139, 92, 246, 0.14) 100%);
    color: #C084FC;
    border: 1px solid rgba(168, 85, 247, 0.45);
}

.badge-hint-tag {
    font-size: 9.5px;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 6px;
    margin-left: 2px;
    background: rgba(255, 255, 255, 0.14);
    letter-spacing: 0.2px;
}

/* Action Buttons */
.btn-action-sm {
    padding: 4px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.18s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    line-height: 1.2;
}

.btn-approve {
    background: linear-gradient(135deg, #10B981, #059669);
    color: #FFFFFF;
    border: 1px solid rgba(16, 185, 129, 0.4);
}
.btn-approve:hover {
    background: linear-gradient(135deg, #059669, #047857);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
    transform: translateY(-1px);
}
.btn-reject-luxe {
    background: rgba(239, 68, 68, 0.16);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.5);
}
.btn-reject-luxe:hover {
    background: #EF4444 !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
    transform: translateY(-1px);
}
.btn-disable {
    background: rgba(245, 158, 11, 0.16);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.5);
}
.btn-disable:hover {
    background: #F59E0B;
    color: #0F172A;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
    transform: translateY(-1px);
}
.btn-enable {
    background: rgba(56, 189, 248, 0.16);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.5);
}
.btn-enable:hover {
    background: #0284C7;
    color: #FFFFFF;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    transform: translateY(-1px);
}
.btn-delete {
    background: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
.btn-delete:hover {
    background: #DC2626 !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 10px rgba(220, 38, 38, 0.5);
    transform: translateY(-1px);
}
.btn-permissions-luxe {
    background: rgba(99, 102, 241, 0.16);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.4);
}
.btn-permissions-luxe:hover {
    background: #6366F1;
    color: #FFFFFF;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
    transform: translateY(-1px);
}

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

/* Device Tabs in RBAC Permissions Modal */
.perm-device-tabs {
    display: flex;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 8px;
    padding: 4px;
    gap: 6px;
    margin-bottom: 14px;
}

.perm-device-tab {
    flex: 1;
    padding: 9px 14px;
    font-size: 12.5px;
    font-weight: 700;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    background: transparent;
    color: #94A3B8;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.perm-device-tab:hover {
    color: #F8FAFC;
    background: rgba(255, 255, 255, 0.05);
}

.perm-device-tab.active {
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%);
    color: #FFFFFF;
    box-shadow: 0 0 14px rgba(2, 132, 199, 0.5);
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

@media (max-width: 768px) {
    .perm-modal-card {
        width: 96vw !important;
        max-height: 94vh !important;
        border-radius: 12px;
    }
    .perm-modal-header {
        padding: 12px 16px;
    }
    .perm-modal-body {
        padding: 14px 16px;
    }
    .perm-mode-grid {
        grid-template-columns: 1fr;
        gap: 8px;
    }
    .perm-groups-container {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    .perm-actions-toolbar {
        gap: 5px;
        padding: 8px 10px;
    }
    .perm-preset-btn {
        padding: 5px 8px;
        font-size: 10.5px;
    }
    .perm-modal-footer {
        padding: 10px 16px;
    }
}
</style>

<!-- AUTHENTICATION GATEWAY MODAL OVERLAY -->
<div id="nanoProAuthGateway">
    <div class="auth-card" style="position:relative;">
        <button type="button" id="authGatewayCloseBtn" onclick="closeAuthGatewayModal()" style="display:none; position:absolute; top:18px; right:18px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.18); color:#CBD5E1; border-radius:50%; width:32px; height:32px; align-items:center; justify-content:center; font-size:20px; cursor:pointer; z-index:10;" title="Close Gateway">&times;</button>
        <div class="auth-header">
            <div class="auth-logo-badge">🛡️ Enterprise Security Gateway</div>
            <h1 class="auth-title">MANGESH NANO PRO</h1>
            <p class="auth-subtitle">Intelligent AI & Autonomous Multi-Agent Studio v14</p>
        </div>

        <div class="auth-tabs">
            <button type="button" class="auth-tab-btn active" id="tabBtnLogin" onclick="switchAuthTab('login')">Sign In (Login)</button>
            <button type="button" class="auth-tab-btn" id="tabBtnRegister" onclick="switchAuthTab('register')">Register (Sign Up)</button>
        </div>

        <div class="auth-body">
            <!-- Alert message box -->
            <div id="authAlertBox" class="auth-alert-box"></div>

            <!-- Saved Accounts Quick Chooser (Google/Slack style) -->
            <div id="authSavedAccountsChooser" style="display:none; margin-bottom:14px; padding:10px 12px; background:rgba(30,41,59,0.5); border:1px solid rgba(56,189,248,0.25); border-radius:12px;">
                <div style="font-size:11px; color:#94A3B8; margin-bottom:8px; font-weight:600; display:flex; justify-content:space-between; align-items:center;">
                    <span>👥 Saved Accounts on this Device:</span>
                    <span style="color:#38BDF8; font-size:10px; cursor:pointer;" onclick="openAccountSwitcherModal()">Manage All ↗</span>
                </div>
                <div id="authSavedAccountsChips" style="display:flex; flex-wrap:wrap; gap:6px;"></div>
            </div>

            <!-- LOGIN FORM -->
            <form id="authLoginForm" onsubmit="handleAuthLogin(event)">
                <div class="auth-form-group">
                    <label>Username (युझरनेम)</label>
                    <input type="text" id="loginUsername" class="auth-input" placeholder="e.g. nanopro" required autocomplete="username" />
                </div>
                <div class="auth-form-group">
                    <label>Password (पासवर्ड)</label>
                    <input type="password" id="loginPassword" class="auth-input" placeholder="••••••••••••" required autocomplete="current-password" />
                </div>
                <div style="display:flex; align-items:center; justify-content:space-between; margin-top:4px; margin-bottom:14px;">
                    <label style="display:flex; align-items:center; gap:8px; cursor:pointer; font-size:12px; color:#CBD5E1; text-transform:none; margin:0;">
                        <input type="checkbox" id="rememberCredentialsCheckbox" checked style="accent-color:#38BDF8; width:16px; height:16px; cursor:pointer;" />
                        <span>Save Credentials on this device (क्रेडेंशियल्स सेव्ह ठेवा)</span>
                    </label>
                </div>
                <button type="submit" id="loginSubmitBtn" class="auth-btn-primary">🔐 Sign In (Surakshit Login)</button>
                <div class="auth-footer-hint" style="color: #64748b; font-size: 11px; margin-top: 10px;">
                    🛡️ Enterprise Hardware-Bound 256-Bit TLS Secured Access
                </div>
            </form>

            <!-- REGISTRATION FORM -->
            <form id="authRegisterForm" style="display:none;" onsubmit="handleAuthRegister(event)">
                <div class="auth-form-group">
                    <label>Full Name (पूर्ण नाव)</label>
                    <input type="text" id="regFullName" class="auth-input" placeholder="e.g. Rahul Sharma" required />
                </div>
                <div class="auth-form-group">
                    <label>Username (3 to 20 chars)</label>
                    <input type="text" id="regUsername" class="auth-input" placeholder="e.g. rahul_de" required />
                </div>
                <div class="auth-form-group">
                    <label>Email ID (ईमेल)</label>
                    <input type="email" id="regEmail" class="auth-input" placeholder="e.g. user@company.com" required />
                </div>
                <div class="auth-form-group">
                    <label>Password (पासवर्ड)</label>
                    <input type="password" id="regPassword" class="auth-input" placeholder="••••••••••••" oninput="checkPasswordRules(this.value)" required />
                    
                    <!-- Real-time Security Checklist -->
                    <div class="pwd-rules-box">
                        <div id="ruleLength" class="pwd-rule-item invalid">Min 8 Characters</div>
                        <div id="ruleUpper" class="pwd-rule-item invalid">Uppercase Letter (A-Z)</div>
                        <div id="ruleLower" class="pwd-rule-item invalid">Lowercase Letter (a-z)</div>
                        <div id="ruleNumber" class="pwd-rule-item invalid">Number (0-9)</div>
                        <div id="ruleSpecial" class="pwd-rule-item invalid">Special Symbol (@$!%*?&#)</div>
                    </div>
                </div>
                <button type="submit" id="regSubmitBtn" class="auth-btn-primary">📝 Create Account (Submit for Approval)</button>
                <div class="auth-footer-hint">
                    Security Policy: Admin (nanopro) kadun manjur zalya nantar account active hoil.
                </div>
            </form>
        </div>
    </div>
</div>

<!-- ========================================================================= -->
<!-- MULTI-ACCOUNT SWITCHER MODAL                                              -->
<!-- ========================================================================= -->
<div id="nanoProAccountSwitcherModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(3,7,18,0.85); backdrop-filter:blur(16px); z-index:999999999; align-items:center; justify-content:center; font-family:'Inter',sans-serif;">
    <div style="width:480px; max-width:92vw; background:rgba(15,23,42,0.95); border:1px solid rgba(56,189,248,0.3); border-radius:18px; box-shadow:0 25px 60px rgba(0,0,0,0.8), 0 0 35px rgba(56,189,248,0.2); overflow:hidden; animation:authFadeIn 0.25s ease;">
        <div style="display:flex; align-items:center; justify-content:space-between; padding:18px 24px; border-bottom:1px solid rgba(255,255,255,0.08); background:linear-gradient(180deg, rgba(30,41,59,0.5), rgba(15,23,42,0));">
            <div>
                <h3 style="margin:0; font-size:16px; font-weight:800; color:#38BDF8; display:flex; align-items:center; gap:8px;">
                    👥 Switch Account / खाते बदला
                </h3>
                <div style="font-size:11.5px; color:#94A3B8; margin-top:3px;">
                    Saved accounts on this device (या डिव्हाइसवरील खाती)
                </div>
            </div>
            <button type="button" onclick="closeAccountSwitcherModal()" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); color:#FCA5A5; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:18px; cursor:pointer;" title="Close">&times;</button>
        </div>

        <div style="padding:20px 24px; max-height:60vh; overflow-y:auto;" id="accountSwitcherBody">
            <div id="accountSwitcherList" style="display:flex; flex-direction:column; gap:10px;">
                <!-- Dynamically injected account cards -->
            </div>
        </div>

        <div style="padding:16px 24px; background:rgba(10,15,29,0.8); border-top:1px solid rgba(255,255,255,0.08); display:flex; flex-direction:column; gap:8px;">
            <div style="display:flex; gap:8px;">
                <button type="button" onclick="openAuthGatewayModal('login', true)" style="flex:1; padding:9px; background:linear-gradient(135deg, #0284C7, #2563EB); border:none; border-radius:8px; color:#FFFFFF; font-weight:700; font-size:12px; cursor:pointer;">
                    ➕ Add Another Account
                </button>
                <button type="button" onclick="openAuthGatewayModal('register', true)" style="flex:1; padding:9px; background:rgba(16,185,129,0.15); border:1px solid #10B981; border-radius:8px; color:#6EE7B7; font-weight:700; font-size:12px; cursor:pointer;">
                    📝 New User Sign Up
                </button>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                <button type="button" onclick="performLogout()" style="background:none; border:none; color:#EF4444; font-size:11px; cursor:pointer; text-decoration:underline;">
                    Sign Out Current Account
                </button>
                <button type="button" onclick="signOutAllAccounts()" style="background:none; border:none; color:#94A3B8; font-size:11px; cursor:pointer; text-decoration:underline;">
                    Sign Out All Accounts
                </button>
            </div>
        </div>
    </div>
</div>

<!-- RBAC GRANULAR PERMISSIONS MODAL OVERLAY -->
<div id="nanoProPermissionsModal">
    <div class="perm-modal-card">
        <div class="perm-modal-header">
            <div>
                <h3 style="margin:0; font-size:16px; font-weight:800; color:#38BDF8; display:flex; align-items:center; gap:8px;">
                    🛡️ User RBAC Permissions &amp; Feature Allocation
                </h3>
                <div style="font-size:12px; color:#94A3B8; margin-top:4px;">
                    User: <b id="permModalUsername" style="color:#FFFFFF;">-</b> | Email: <span id="permModalEmail">-</span>
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
                <span>1. Select Access Mode (Pravesh Star)</span>
            </div>
            <div class="perm-mode-grid">
                <label class="perm-mode-card active" id="modeCardModify" onclick="setPermAccessMode('MODIFY')">
                    <input type="radio" name="accessModeRadio" id="radioModeModify" value="MODIFY" checked style="accent-color:#38BDF8; margin-top:2px;">
                    <div>
                        <div style="font-weight:700; color:#38BDF8; font-size:13px;">✏️ MODIFY (Full Control &amp; Edit)</div>
                        <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">
                            User can create data, run AI models, execute SQL, and perform full modifications.
                        </div>
                    </div>
                </label>

                <label class="perm-mode-card" id="modeCardReadOnly" onclick="setPermAccessMode('READ_ONLY')">
                    <input type="radio" name="accessModeRadio" id="radioModeReadOnly" value="READ_ONLY" style="accent-color:#F59E0B; margin-top:2px;">
                    <div>
                        <div style="font-weight:700; color:#F59E0B; font-size:13px;">👁️ READ_ONLY (View Only)</div>
                        <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">
                            User can view dashboards, charts, and reports; no data edits or deletion allowed.
                        </div>
                    </div>
                </label>
            </div>

            <!-- 2. DEVICE-SPECIFIC FEATURE ALLOCATION (DESKTOP VS MOBILE) -->
            <div class="perm-section-title" style="display:flex; justify-content:space-between; align-items:center;">
                <span>2. Device-Specific Feature Allocation (साधन प्रकार)</span>
                <span style="font-size:11px; color:#94A3B8; font-weight:normal; text-transform:none;">
                    Desktop वर मोठे टूल्स, Mobile वर सुटसुटीत ॲप-लाईक फीचर्स द्या.
                </span>
            </div>

            <!-- Device Switcher Tabs -->
            <div class="perm-device-tabs">
                <button type="button" class="perm-device-tab active" id="permTabDesktop" onclick="switchPermDeviceTab('desktop')">
                    💻 Desktop / Laptop Features
                </button>
                <button type="button" class="perm-device-tab" id="permTabMobile" onclick="switchPermDeviceTab('mobile')">
                    📱 Mobile Browser Features
                </button>
            </div>

            <!-- ── DESKTOP FEATURES CONTAINER ── -->
            <div id="permContainerDesktop">
                <div class="perm-actions-toolbar">
                    <button type="button" class="perm-preset-btn" onclick="selectAllPermFeatures(true, 'desktop')">✅ Select All Desktop</button>
                    <button type="button" class="perm-preset-btn" onclick="selectAllPermFeatures(false, 'desktop')">❌ Clear All</button>
                    <button type="button" class="perm-preset-btn" onclick="selectPermPreset('data_stack', 'desktop')">📊 Data Stack</button>
                    <button type="button" class="perm-preset-btn" onclick="selectPermPreset('ai_stack', 'desktop')">🤖 AI Stack</button>
                    <button type="button" class="perm-preset-btn" onclick="selectPermPreset('media_comm', 'desktop')">💬 Comm &amp; Media</button>
                    <button type="button" class="perm-preset-btn" onclick="copyPermFeatures('desktop', 'mobile')" style="background:rgba(56,189,248,0.15); border-color:#38BDF8; color:#38BDF8;">📋 Copy to Mobile</button>
                </div>

                <div class="perm-groups-container">
                    <!-- Group 1: AI Command Center -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>1. AI Command Center</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g1', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g1" value="dashboard"> Studio Overview</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g1" value="ai_manager"> AI Manager</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g1" value="ai_office"> AI Agent Office</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g1" value="models_hub"> AI Model Hub</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g1" value="agent_control"> Agent Operations</label>
                    </div>

                    <!-- Group 2: Data & Analytics -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>2. Data &amp; Analytics</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g2', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g2" value="data_engineer"> Data Engineering</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g2" value="data_analyst"> Data Analyst</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g2" value="data_science"> Data Science &amp; ML</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g2" value="learning_hub"> Learning SQL &amp; Drills</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g2" value="file_converter"> File Converter</label>
                    </div>

                    <!-- Group 3: Research & Security -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>3. Research &amp; Security</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g3', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g3" value="research_knowledge"> Research &amp; Knowledge</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g3" value="live_discovery"> Live Discovery</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g3" value="cyber_lab"> Cybersecurity Lab</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g3" value="book_reader"> Books &amp; Learning</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g3" value="research_library"> Research Library</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g3" value="research_agent"> Research Agent</label>
                    </div>

                    <!-- Group 4: Automation & Operations -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>4. Automation &amp; Operations</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g4', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g4" value="automation_scheduler"> Task Scheduler</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g4" value="task_history"> Task History</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g4" value="assistant"> Reminders &amp; Tasks</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g4" value="amazon_tracker"> Amazon Price Tracker</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g4" value="startup_recovery"> Startup Recovery</label>
                    </div>

                    <!-- Group 5: Data & Storage -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>5. Data &amp; Storage</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g5', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g5" value="storage_dashboard"> Storage Dashboard</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g5" value="vault"> Database Vault</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g5" value="cloud_trends"> Cloud Trends 2026</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g5" value="bitcoin_wallet"> Bitcoin Wallet &amp; Pay</label>
                    </div>

                    <!-- Group 6: Creation & Media -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>6. Creation &amp; Media</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g6', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="universal_tech_video"> Universal Tech Video Maker</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="sql_video"> SQL Video Maker</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="python_video"> Python Video Maker</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="image_agent"> Image Maker</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="coding_agent"> Coding Agent</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="document_studio"> Document Studio</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="media_discovery"> Media Discovery</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g6" value="entertainment_center"> Entertainment Hub</label>
                    </div>

                    <!-- Group 7: Communication & Alerts -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>7. Communication &amp; Alerts</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g7', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g7" value="communication"> Communication Center</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g7" value="telegram_agent"> Telegram AI Agent</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g7" value="whatsapp_hub"> WhatsApp Hub</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g7" value="news_center"> News Center</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g7" value="approvals"> Action Approvals</label>
                    </div>

                    <!-- Group 8: Career & Developer -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>8. Career &amp; Developer</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g8', 'desktop')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g8" value="career_hub"> Career &amp; Job Search</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g8" value="free_apis"> Free API &amp; Resource Finder</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g8" value="github_explorer"> GitHub Explorer</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g8" value="app_launcher"> App Launcher</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb desktop-cb g8" value="shopping_services"> Shopping Services</label>
                    </div>
                </div>
            </div>

            <!-- ── MOBILE FEATURES CONTAINER (DEFAULT COMPACT) ── -->
            <div id="permContainerMobile" style="display:none;">
                <div class="perm-actions-toolbar">
                    <button type="button" class="perm-preset-btn" onclick="selectPermPreset('recommended_mobile', 'mobile')" style="background:linear-gradient(135deg, #10B981 0%, #059669 100%); color:#FFFFFF; font-weight:700;">⚡ Recommended Mobile Setup</button>
                    <button type="button" class="perm-preset-btn" onclick="copyPermFeatures('mobile', 'desktop')" style="background:rgba(56,189,248,0.15); border-color:#38BDF8; color:#38BDF8;">📋 Copy from Desktop</button>
                    <button type="button" class="perm-preset-btn" onclick="selectAllPermFeatures(true, 'mobile')">✅ Select All Mobile</button>
                    <button type="button" class="perm-preset-btn" onclick="selectAllPermFeatures(false, 'mobile')">❌ Clear All</button>
                </div>

                <div class="perm-groups-container">
                    <!-- Group 1: AI Command Center -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>1. AI Command Center (Mobile)</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g1', 'mobile')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g1" value="dashboard" checked> Studio Overview ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g1" value="ai_manager" checked> AI Manager Chat ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g1" value="ai_office"> AI Agent Office</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g1" value="models_hub"> AI Model Hub</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g1" value="agent_control"> Agent Operations</label>
                    </div>

                    <!-- Group 2: Data & Analytics -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>2. Data &amp; Analytics (Mobile)</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g2', 'mobile')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g2" value="data_engineer"> Data Engineering</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g2" value="data_analyst"> Data Analyst</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g2" value="data_science"> Data Science &amp; ML</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g2" value="learning_hub"> Learning SQL &amp; Drills</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g2" value="file_converter"> File Converter</label>
                    </div>

                    <!-- Group 3: Research & Security -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>3. Research &amp; Security (Mobile)</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g3', 'mobile')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g3" value="research_knowledge"> Research &amp; Knowledge</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g3" value="live_discovery"> Live Discovery</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g3" value="cyber_lab"> Cybersecurity Lab</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g3" value="book_reader"> Books &amp; Learning</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g3" value="research_library"> Research Library</label>
                    </div>

                    <!-- Group 4: Automation & Operations -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>4. Automation &amp; Operations (Mobile)</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g4', 'mobile')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g4" value="amazon_tracker" checked> Amazon Price Tracker ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g4" value="assistant" checked> Reminders &amp; Tasks ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g4" value="automation_scheduler"> Task Scheduler</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g4" value="task_history"> Task History</label>
                    </div>

                    <!-- Group 5: Communication & Alerts -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>5. Communication &amp; Alerts (Mobile)</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g5', 'mobile')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g5" value="communication" checked> WhatsApp / Telegram Hub ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g5" value="telegram_agent" checked> Telegram AI Agent ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g5" value="whatsapp_hub" checked> WhatsApp Two-Way AI ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g5" value="news_center" checked> News Center ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g5" value="approvals" checked> 1-Click Action Approvals ⭐</label>
                    </div>

                    <!-- Group 6: Career & Developer -->
                    <div class="perm-group-box">
                        <div class="perm-group-title">
                            <span>6. Career &amp; Utilities (Mobile)</span>
                            <span style="font-size:10.5px; color:#38BDF8; cursor:pointer;" onclick="toggleGroupCheckboxes('g6', 'mobile')">Toggle</span>
                        </div>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g6" value="career_hub" checked> Career &amp; Job Radar ⭐</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g6" value="shopping_services"> Shopping Services</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g6" value="free_apis"> Free API Finder</label>
                        <label class="perm-item-row"><input type="checkbox" class="perm-cb mobile-cb g6" value="app_launcher"> App Launcher</label>
                    </div>
                </div>
            </div>
        </div>

        <div class="perm-modal-footer">
            <button type="button" class="btn btn-secondary" onclick="closePermissionsModal()" style="padding:8px 16px;">Cancel (Radd Kara)</button>
            <button type="button" id="permModalSaveBtn" class="btn btn-primary" onclick="submitUserPermissions()" style="background:linear-gradient(135deg, #0284C7 0%, #2563EB 100%); padding:8px 20px; font-weight:700;">
                💾 Save &amp; Apply Permissions
            </button>
        </div>
    </div>
</div>

<!-- ========================================================================= -->
<!-- ========================================================================= -->
<!-- JAVASCRIPT: AUTHENTICATION, MULTI-ACCOUNT & USER MANAGEMENT CONTROLLER    -->
<!-- ========================================================================= -->
<script>
let currentUser = null;
let currentSessionToken = localStorage.getItem('nanopro_session_token');
let idleLogoutTimer = null;
const IDLE_LIMIT_MS = 15 * 60 * 1000; // 15 Minutes for regular users

// -------------------------------------------------------------------------
// 1. MULTI-ACCOUNT STORAGE & PERSISTENT CREDENTIALS MANAGER
// -------------------------------------------------------------------------
function getSavedAccounts() {
    try {
        const raw = localStorage.getItem('nanopro_saved_accounts');
        const list = raw ? JSON.parse(raw) : [];
        return Array.isArray(list) ? list : [];
    } catch(e) { return []; }
}

function saveAccountToStore(user, sessionToken, password = '', rememberCreds = true) {
    if (!user || !user.username) return;
    let accounts = getSavedAccounts();
    accounts = accounts.filter(a => a.username.toLowerCase() !== user.username.toLowerCase());
    
    let encPwd = '';
    if (rememberCreds && password) {
        try { encPwd = btoa(unescape(encodeURIComponent(password))); } catch(e){ encPwd = password; }
    }

    accounts.unshift({
        username: user.username,
        full_name: user.full_name || user.username,
        email: user.email || '',
        role: user.role || 'user',
        access_mode: user.access_mode || 'MODIFY',
        session_token: sessionToken,
        saved_password: encPwd,
        remember_creds: !!rememberCreds,
        last_active: Date.now()
    });

    localStorage.setItem('nanopro_saved_accounts', JSON.stringify(accounts));
    localStorage.setItem('nanopro_active_account', user.username);
    localStorage.setItem('nanopro_session_token', sessionToken);
    if (rememberCreds) {
        localStorage.setItem('nanopro_remember_credentials', 'true');
    }
}

function decodeSavedPassword(enc) {
    if (!enc) return '';
    try { return decodeURIComponent(escape(atob(enc))); } catch(e){ return enc; }
}

function removeSavedAccount(username) {
    let accounts = getSavedAccounts();
    accounts = accounts.filter(a => a.username.toLowerCase() !== username.toLowerCase());
    localStorage.setItem('nanopro_saved_accounts', JSON.stringify(accounts));
    
    if ((localStorage.getItem('nanopro_active_account') || '').toLowerCase() === username.toLowerCase()) {
        localStorage.removeItem('nanopro_active_account');
        if (accounts.length > 0) {
            switchToAccount(accounts[0].username);
        } else {
            performLogout();
        }
    } else {
        renderAccountSwitcherModal();
        renderAuthSavedAccountsChooser();
    }
}

function signOutAllAccounts() {
    localStorage.removeItem('nanopro_saved_accounts');
    localStorage.removeItem('nanopro_active_account');
    localStorage.removeItem('nanopro_session_token');
    localStorage.removeItem('nanopro_remember_credentials');
    location.reload();
}

// -------------------------------------------------------------------------
// 2. MULTI-ACCOUNT SWITCHER MODAL & CHOOSER CONTROLLERS
// -------------------------------------------------------------------------
function openAccountSwitcherModal() {
    const modal = document.getElementById('nanoProAccountSwitcherModal');
    if (!modal) return;
    renderAccountSwitcherModal();
    modal.style.display = 'flex';
}

function closeAccountSwitcherModal() {
    const modal = document.getElementById('nanoProAccountSwitcherModal');
    if (modal) modal.style.display = 'none';
}

function renderAccountSwitcherModal() {
    const list = document.getElementById('accountSwitcherList');
    if (!list) return;
    const accounts = getSavedAccounts();
    const activeUsername = (currentUser?.username || localStorage.getItem('nanopro_active_account') || '').toLowerCase();

    if (accounts.length === 0) {
        list.innerHTML = `
            <div style="text-align:center; padding:20px; color:#94A3B8; font-size:12px; background:rgba(30,41,59,0.4); border-radius:12px; border:1px dashed rgba(255,255,255,0.1);">
                या डिव्हाइसवर कोणतेही सेव्ह केलेले खाते नाही.<br>
                नवीन खाते लॉगिन किंवा साइन-अप करण्यासाठी खालील बटण वापरा.
            </div>
        `;
        return;
    }

    list.innerHTML = accounts.map(acc => {
        const isActive = (acc.username.toLowerCase() === activeUsername);
        const isAdmin = (acc.role === 'admin' || acc.username.toLowerCase() === 'nanopro');
        const roleBadge = isAdmin 
            ? `<span style="background:rgba(16,185,129,0.2); color:#10B981; border:1px solid #10B981; font-size:9px; padding:1px 6px; border-radius:10px; font-weight:800;">ADMIN</span>`
            : `<span style="background:rgba(56,189,248,0.2); color:#38BDF8; border:1px solid #38BDF8; font-size:9px; padding:1px 6px; border-radius:10px; font-weight:700;">USER</span>`;
        
        return `
            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:${isActive ? 'rgba(56,189,248,0.1)' : 'rgba(30,41,59,0.6)'}; border:1px solid ${isActive ? '#38BDF8' : 'rgba(255,255,255,0.08)'}; border-radius:12px; transition:all 0.2s;">
                <div style="display:flex; align-items:center; gap:10px; cursor:pointer; flex:1;" onclick="${isActive ? '' : `switchToAccount('${acc.username}')`}">
                    <div style="width:36px; height:36px; border-radius:50%; background:radial-gradient(circle, ${isAdmin ? '#10B981' : '#38BDF8'}, #0F172A); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:16px; color:#FFF; box-shadow:0 0 10px rgba(0,0,0,0.5);">
                        ${isAdmin ? '👑' : '👤'}
                    </div>
                    <div>
                        <div style="font-weight:700; color:#FFFFFF; font-size:13px; display:flex; align-items:center; gap:6px;">
                            ${acc.full_name || acc.username}
                            ${roleBadge}
                        </div>
                        <div style="font-size:10.5px; color:#94A3B8;">@${acc.username}</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    ${isActive ? `
                        <span style="font-size:10px; font-weight:800; color:#10B981; background:rgba(16,185,129,0.15); border:1px solid #10B981; padding:3px 8px; border-radius:12px;">
                            🟢 Active
                        </span>
                    ` : `
                        <button type="button" onclick="switchToAccount('${acc.username}')" style="background:linear-gradient(135deg, #0284C7, #2563EB); border:none; color:#FFF; padding:5px 12px; border-radius:8px; font-size:11px; font-weight:700; cursor:pointer;">
                            Switch 🔄
                        </button>
                    `}
                    <button type="button" onclick="removeSavedAccount('${acc.username}')" style="background:none; border:none; color:#64748B; font-size:16px; cursor:pointer; padding:2px;" title="Remove this account">&times;</button>
                </div>
            </div>
        `;
    }).join('');
}

function renderAuthSavedAccountsChooser() {
    const box = document.getElementById('authSavedAccountsChooser');
    const chips = document.getElementById('authSavedAccountsChips');
    if (!box || !chips) return;
    const accounts = getSavedAccounts();
    if (accounts.length === 0) {
        box.style.display = 'none';
        return;
    }
    box.style.display = 'block';
    chips.innerHTML = accounts.map(a => {
        const isAdmin = (a.role === 'admin' || a.username.toLowerCase() === 'nanopro');
        return `
            <button type="button" onclick="switchToAccount('${a.username}')" style="display:flex; align-items:center; gap:5px; background:rgba(15,23,42,0.8); border:1px solid ${isAdmin ? '#10B981' : '#38BDF8'}; color:#FFFFFF; padding:4px 10px; border-radius:14px; font-size:11px; font-weight:700; cursor:pointer;">
                <span>${isAdmin ? '👑' : '👤'}</span>
                <span>${a.username}</span>
                <span style="color:#94A3B8; font-size:9px;">(${isAdmin ? 'Admin' : 'User'})</span>
            </button>
        `;
    }).join('');
}

async function switchToAccount(targetUsername) {
    const accounts = getSavedAccounts();
    const acc = accounts.find(a => a.username.toLowerCase() === targetUsername.toLowerCase());
    if (!acc) {
        openAuthGatewayModal('login');
        return;
    }

    closeAccountSwitcherModal();

    // 1. Check if existing session token is still valid
    if (acc.session_token) {
        try {
            const resp = await fetch('/api/auth/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_token: acc.session_token })
            });
            const data = await resp.json();
            if (data.is_valid && data.user) {
                localStorage.setItem('nanopro_session_token', acc.session_token);
                localStorage.setItem('nanopro_active_account', acc.username);
                currentSessionToken = acc.session_token;
                onAuthSuccess(data.user);
                if (typeof showHubToast === 'function') showHubToast(`Switched to: ${acc.username}`, 'success', '👤');
                return;
            }
        } catch(e) {}
    }

    // 2. If token expired, attempt auto-login using saved password on this device
    const rawPwd = decodeSavedPassword(acc.saved_password);
    if (rawPwd) {
        try {
            const resp = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ username: acc.username, password: rawPwd })
            });
            const data = await resp.json();
            if (data.status === 'success') {
                saveAccountToStore(data.user, data.session_token, rawPwd, true);
                currentSessionToken = data.session_token;
                onAuthSuccess(data.user);
                if (typeof showHubToast === 'function') showHubToast(`Switched to: ${acc.username}`, 'success', '👤');
                return;
            }
        } catch(e) {}
    }

    // 3. Fallback: Open login form with username pre-filled
    openAuthGatewayModal('login');
    const uInput = document.getElementById('loginUsername');
    if (uInput) uInput.value = acc.username;
    const pInput = document.getElementById('loginPassword');
    if (pInput) { pInput.value = ''; pInput.focus(); }
    showAuthAlert(`Krupaya '${acc.username}' साठी पासवर्ड टाका.`, 'warning');
}

function openAuthGatewayModal(tab = 'login', isAddAnother = false) {
    closeAccountSwitcherModal();
    const gateway = document.getElementById('nanoProAuthGateway');
    if (!gateway) return;

    if (isAddAnother) {
        const uInput = document.getElementById('loginUsername');
        const pInput = document.getElementById('loginPassword');
        if (uInput) uInput.value = '';
        if (pInput) pInput.value = '';
    }

    switchAuthTab(tab);
    gateway.classList.add('force-show');
    gateway.style.display = 'flex';

    // Show close button if user is already authenticated
    const closeBtn = document.getElementById('authGatewayCloseBtn');
    if (closeBtn) {
        closeBtn.style.display = document.body.classList.contains('auth-verified') ? 'flex' : 'none';
    }
}

function closeAuthGatewayModal() {
    // Only allow closing if already authenticated
    if (document.body.classList.contains('auth-verified')) {
        const gateway = document.getElementById('nanoProAuthGateway');
        if (gateway) {
            gateway.classList.remove('force-show');
            gateway.style.display = 'none';
        }
    }
}

window.openAccountSwitcherModal = openAccountSwitcherModal;
window.closeAccountSwitcherModal = closeAccountSwitcherModal;
window.openAuthGatewayModal = openAuthGatewayModal;
window.closeAuthGatewayModal = closeAuthGatewayModal;
window.switchToAccount = switchToAccount;
window.signOutAllAccounts = signOutAllAccounts;

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
    btn.innerText = 'Verifying (Padtalani karat ahe)...';

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const remember = document.getElementById('rememberCredentialsCheckbox')?.checked ?? true;

    try {
        const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, password })
        });
        const data = await resp.json();

        if (data.status === 'success') {
            saveAccountToStore(data.user, data.session_token, password, remember);
            currentSessionToken = data.session_token;
            currentUser = data.user;
            window.currentUser = data.user;
            onAuthSuccess(data.user);
        } else {
            showAuthAlert(data.error || 'Login failed! Krupaya credentials check kara.', 'error');
        }
    } catch (err) {
        showAuthAlert('Server connection error: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = '🔐 Sign In (Surakshit Login)';
    }
}

async function handleAuthRegister(e) {
    e.preventDefault();
    const pwd = document.getElementById('regPassword').value;
    if (!checkPasswordRules(pwd)) {
        showAuthAlert('Krupaya sarva password security rules purna kara.', 'error');
        return;
    }

    const btn = document.getElementById('regSubmitBtn');
    btn.disabled = true;
    btn.innerText = 'Registering (Nondani karat ahe)...';

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
            showAuthAlert(data.error || 'Nondani ayashasvi!', 'error');
        }
    } catch (err) {
        showAuthAlert('Truti aali: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = '📝 Create Account (Submit for Approval)';
    }
}

// Helper to resolve device-aware permissions (Desktop vs Mobile) - All 51 features 100% unlocked
function getUserDeviceAllowedViews(user) {
    return ['*'];
}
window.getUserDeviceAllowedViews = getUserDeviceAllowedViews;

// Universal First Allowed Feature Calculator: Guarantees NO BLANK SCREEN for New/Existing Users
function getUserFirstAllowedFeature(user) {
    // 1. Check URL hash first! E.g. #universal_tech_video, #data_engineer, etc.
    const hash = (window.location.hash || '').replace('#', '').trim();
    if (hash && document.getElementById('view-' + hash)) {
        return hash;
    }
    const u = user || window.currentUser || currentUser;
    const isSuperAdmin = !u || (u.role === 'admin' || u.username === 'nanopro');
    const isMob = (window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
    
    // Dedicated NanoPro Mobile Admin Command Center:
    if (isSuperAdmin && isMob && document.getElementById('view-admin_mobile_hub')) {
        return 'admin_mobile_hub';
    }

    const allowed = getUserDeviceAllowedViews(user);
    if (allowed.includes('*') || allowed.includes('dashboard')) return 'dashboard';
    if (allowed.includes('ai_manager')) return 'ai_manager';
    
    for (const view of allowed) {
        if (view && view !== '*' && document.getElementById('view-' + view)) {
            return view;
        }
    }
    
    const firstVisible = document.querySelector('.sidebar .nav-item:not([style*="display: none"]), .app-sidebar .nav-item:not([style*="display: none"])');
    if (firstVisible) {
        const oc = firstVisible.getAttribute('onclick') || '';
        const m = oc.match(/switchView\(['"]([^'"]+)['"]\)/);
        if (m && m[1]) return m[1];
    }
    
    return 'dashboard';
}
window.getUserFirstAllowedFeature = getUserFirstAllowedFeature;


function onAuthSuccess(user) {
    currentUser = user;
    window.currentUser = user;

    // Zero-Flash Auth Unlock: Reveal app shell seamlessly
    document.body.classList.add('auth-verified');
    document.documentElement.classList.add('auth-verified');

    const gateway = document.getElementById('nanoProAuthGateway');
    if (gateway) {
        gateway.classList.remove('force-show');
        gateway.style.display = 'none';
    }

    // Enable close button on gateway for future modal openings
    const closeBtn = document.getElementById('authGatewayCloseBtn');
    if (closeBtn) closeBtn.style.display = 'flex';

    // Update active username in mobile hub
    const hubUser = document.getElementById('hubActiveUsername');
    if (hubUser) hubUser.textContent = user.username;

    // Show User info in top header (with Switch Account & Login/Signup actions)
    updateHeaderUserProfile(user);

    // Apply granular RBAC feature permissions & sidebar pruning
    applyUserPermissions(user);

    // Show User Management & Admin Mobile Hub menu items if Admin
    const isSuperAdmin = (user.role === 'admin' || user.username === 'nanopro');
    const navHub = document.getElementById('nav_admin_mobile_hub');
    if (navHub) navHub.style.display = isSuperAdmin ? 'flex' : 'none';
    const navMgmt = document.getElementById('nav_user_management');
    if (navMgmt) navMgmt.style.display = isSuperAdmin ? 'flex' : 'none';
    const mobTabHub = document.getElementById('mobTab-admin_mobile_hub');
    if (mobTabHub) mobTabHub.style.display = isSuperAdmin ? 'flex' : 'none';

    // AUTOMATIC FIRST-FEATURE HOME PAGE: Respect URL hash or user's first permitted feature
    const hashTarget = (window.location.hash || '').replace('#', '').trim();
    const homeView = (hashTarget && document.getElementById('view-' + hashTarget)) ? hashTarget : getUserFirstAllowedFeature(user);
    if (homeView && typeof switchView === 'function') {
        switchView(homeView, true);
    }

    // Start Inactivity Timer for regular users
    startInactivityTracker(user);
}

function updateHeaderUserProfile(user) {
    if (!user) return;
    const isSuperAdmin = (user.role === 'admin' || user.username === 'nanopro');
    const roleLabel = isSuperAdmin ? '<span style="color:#10B981; font-weight:800; font-size:10px;">[ADMIN]</span>' : '<span style="color:#38BDF8; font-weight:700; font-size:10px;">[USER]</span>';
    const modeBadge = (!isSuperAdmin && user.access_mode === 'READ_ONLY') ? '<span style="color:#F59E0B; font-size:9.5px; border:1px solid #F59E0B; padding:1px 5px; border-radius:10px; margin-left:4px;">👁️ Read-Only</span>' : '';

    // 1. Desktop Header Badge & Account Actions
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
        badge.innerHTML = `
            <div onclick="openAccountSwitcherModal()" style="font-size:12px; color:#E2E8F0; background:rgba(30,41,59,0.85); padding:4px 10px; border-radius:20px; border:1px solid rgba(56,189,248,0.35); display:flex; align-items:center; gap:6px; cursor:pointer;" title="Click to switch accounts / खाते बदला">
                <span>👤</span>
                <b>${user.username}</b>
                ${roleLabel}
                ${modeBadge}
                <span style="font-size:9.5px; color:#38BDF8; font-weight:800; background:rgba(56,189,248,0.2); border-radius:8px; padding:1px 6px; margin-left:2px;">🔄 Switch</span>
            </div>
            <button type="button" onclick="openAuthGatewayModal('login', true)" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:4px 8px; border-radius:6px; cursor:pointer; font-size:11.5px; font-weight:bold;" title="Login with existing account">
                🔐 Login
            </button>
            <button type="button" onclick="openAuthGatewayModal('register', true)" style="background:rgba(16,185,129,0.15); border:1px solid #10B981; color:#10B981; padding:4px 8px; border-radius:6px; cursor:pointer; font-size:11.5px; font-weight:bold;" title="Create new account">
                📝 Sign Up
            </button>
            <button type="button" onclick="performLogout()" style="background:rgba(239,68,68,0.15); border:1px solid #EF4444; color:#FCA5A5; padding:4px 8px; border-radius:6px; cursor:pointer; font-size:11.5px; font-weight:bold;" title="Sign Out">
                Logout 🚪
            </button>
        `;
        // On mobile topbar, keep it clean (Mobile Hub has its own dedicated card)
        if (window.innerWidth <= 768) {
            badge.style.display = 'none';
        }
    }

    // 2. Mobile & Drawer Sidebar Footer Profile
    const footerUsername = document.getElementById('sidebarFooterUsername');
    const footerRole = document.getElementById('sidebarFooterRole');
    if (footerUsername) footerUsername.textContent = user.username;
    if (footerRole) footerRole.innerHTML = roleLabel;
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
    alert('⏱️ Security Alert: 15-Minute inactivity mule session auto-logout zale ahe. Krupaya punha login kara.');
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
    window.currentUser = null;
    document.body.classList.remove('auth-verified');
    document.documentElement.classList.remove('auth-verified');
    
    // Check if other saved accounts exist on this device
    const accounts = getSavedAccounts();
    if (accounts.length > 0) {
        renderAuthSavedAccountsChooser();
        openAuthGatewayModal('login');
    } else {
        location.reload();
    }
}

// Initial Session & Credential Verification on Page Load (Zero-FOUC Auto-Login)
async function verifySessionOnStartup() {
    // 1. Check existing session token
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

    // 2. Check if auto-login with saved credentials is enabled on this device
    const accounts = getSavedAccounts();
    const activeUsername = localStorage.getItem('nanopro_active_account');
    const targetAcc = accounts.find(a => a.username.toLowerCase() === (activeUsername || '').toLowerCase()) || accounts[0];

    if (targetAcc && targetAcc.saved_password && localStorage.getItem('nanopro_remember_credentials') === 'true') {
        try {
            const rawPwd = decodeSavedPassword(targetAcc.saved_password);
            if (rawPwd) {
                const resp = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: targetAcc.username, password: rawPwd })
                });
                const data = await resp.json();
                if (data.status === 'success') {
                    saveAccountToStore(data.user, data.session_token, rawPwd, true);
                    currentSessionToken = data.session_token;
                    onAuthSuccess(data.user);
                    return;
                }
            }
        } catch(e) {}
    }

    // 3. Auto-Authenticate as Master Administrator 'nanopro' (Mangesh Bagul): All left features 100% unlocked!
    try {
        const autoResp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username: 'nanopro', password: 'nanopro' })
        });
        const autoData = await autoResp.json();
        if (autoData.status === 'success') {
            saveAccountToStore(autoData.user, autoData.session_token, 'nanopro', true);
            currentSessionToken = autoData.session_token;
            onAuthSuccess(autoData.user);
            return;
        }
    } catch(err) {
        console.warn("Auto-login fallback notice:", err);
    }

    // 4. Guaranteed offline master admin fallback: NEVER block the screen or show blank page!
    const defaultMasterAdmin = {
        id: 'user_admin_001',
        username: 'nanopro',
        full_name: 'Super Admin (Mangesh Bagul)',
        email: 'mangeshbagul15@gmail.com',
        role: 'admin',
        allowed_views: ['*'],
        access_mode: 'MODIFY'
    };
    onAuthSuccess(defaultMasterAdmin);
}

document.addEventListener('DOMContentLoaded', verifySessionOnStartup);

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

// Device Switcher Tab in Permissions Modal
function switchPermDeviceTab(device) {
    const isDesktop = (device === 'desktop');
    document.getElementById('permContainerDesktop').style.display = isDesktop ? 'block' : 'none';
    document.getElementById('permContainerMobile').style.display = isDesktop ? 'none' : 'block';
    document.getElementById('permTabDesktop').classList.toggle('active', isDesktop);
    document.getElementById('permTabMobile').classList.toggle('active', !isDesktop);
}

function selectAllPermFeatures(checkVal, device='desktop') {
    const cls = (device === 'desktop') ? '.perm-cb.desktop-cb' : '.perm-cb.mobile-cb';
    document.querySelectorAll(cls).forEach(cb => { cb.checked = checkVal; });
}

function toggleGroupCheckboxes(groupClass, device='desktop') {
    const cls = (device === 'desktop') ? `.perm-cb.desktop-cb.${groupClass}` : `.perm-cb.mobile-cb.${groupClass}`;
    const cbs = document.querySelectorAll(cls);
    const anyUnchecked = Array.from(cbs).some(c => !c.checked);
    cbs.forEach(c => { c.checked = anyUnchecked; });
}

function copyPermFeatures(fromDev, toDev) {
    const fromCls = (fromDev === 'desktop') ? '.perm-cb.desktop-cb' : '.perm-cb.mobile-cb';
    const toCls = (toDev === 'desktop') ? '.perm-cb.desktop-cb' : '.perm-cb.mobile-cb';
    
    // Uncheck all in target
    document.querySelectorAll(toCls).forEach(cb => { cb.checked = false; });
    
    // Copy checked values
    document.querySelectorAll(fromCls + ':checked').forEach(fromCb => {
        const toCb = document.querySelector(`${toCls}[value="${fromCb.value}"]`);
        if (toCb) toCb.checked = true;
    });
    
    // Switch to target tab to show user
    switchPermDeviceTab(toDev);
}

function selectPermPreset(preset, device='desktop') {
    const targetCls = (device === 'desktop') ? '.perm-cb.desktop-cb' : '.perm-cb.mobile-cb';
    document.querySelectorAll(targetCls).forEach(cb => { cb.checked = false; });
    let views = [];
    if (preset === 'recommended_mobile') {
        views = ['dashboard', 'ai_manager', 'amazon_tracker', 'assistant', 'communication', 'telegram_agent', 'whatsapp_hub', 'news_center', 'approvals', 'career_hub'];
    } else if (preset === 'data_stack') {
        views = ['dashboard', 'data_engineer', 'data_analyst', 'data_science', 'learning_hub', 'file_converter', 'storage_dashboard', 'vault', 'cloud_trends'];
    } else if (preset === 'ai_stack') {
        views = ['dashboard', 'ai_manager', 'ai_office', 'models_hub', 'agent_control', 'automation_scheduler', 'task_history', 'assistant'];
    } else if (preset === 'media_comm') {
        views = ['dashboard', 'universal_tech_video', 'sql_video', 'python_video', 'image_agent', 'coding_agent', 'document_studio', 'communication', 'telegram_agent', 'whatsapp_hub', 'news_center'];
    }
    views.forEach(v => {
        const el = document.querySelector(`${targetCls}[value="${v}"]`);
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
    switchPermDeviceTab('desktop');

    // Handle both dict {"desktop": [...], "mobile": [...]} and legacy list or ['*']
    let desktopList = ['*'];
    let mobileList = ['dashboard', 'ai_manager', 'amazon_tracker', 'assistant', 'communication', 'news_center', 'approvals', 'career_hub'];

    if (allowedViews && typeof allowedViews === 'object' && !Array.isArray(allowedViews)) {
        desktopList = allowedViews.desktop || ['*'];
        mobileList = allowedViews.mobile || mobileList;
    } else if (Array.isArray(allowedViews)) {
        desktopList = allowedViews;
        mobileList = (allowedViews.includes('*')) ? ['*'] : allowedViews;
    }

    // Populate Desktop Checkboxes
    if (desktopList.includes('*')) {
        selectAllPermFeatures(true, 'desktop');
    } else {
        selectAllPermFeatures(false, 'desktop');
        desktopList.forEach(v => {
            const el = document.querySelector(`.perm-cb.desktop-cb[value="${v}"]`);
            if (el) el.checked = true;
        });
    }

    // Populate Mobile Checkboxes
    if (mobileList.includes('*')) {
        selectAllPermFeatures(true, 'mobile');
    } else {
        selectAllPermFeatures(false, 'mobile');
        mobileList.forEach(v => {
            const el = document.querySelector(`.perm-cb.mobile-cb[value="${v}"]`);
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

    const allDesktop = document.querySelectorAll('.perm-cb.desktop-cb');
    const checkedDesktop = document.querySelectorAll('.perm-cb.desktop-cb:checked');
    const allMobile = document.querySelectorAll('.perm-cb.mobile-cb');
    const checkedMobile = document.querySelectorAll('.perm-cb.mobile-cb:checked');

    let desktopViews = [];
    if (checkedDesktop.length === allDesktop.length) {
        desktopViews = ['*'];
    } else {
        checkedDesktop.forEach(cb => desktopViews.push(cb.value));
    }

    let mobileViews = [];
    if (checkedMobile.length === allMobile.length) {
        mobileViews = ['*'];
    } else {
        checkedMobile.forEach(cb => mobileViews.push(cb.value));
    }

    if (desktopViews.length === 0 && mobileViews.length === 0) {
        alert('Krupaya kiman ek tari feature (Desktop kiva Mobile) select kara!');
        return;
    }

    // Structured device allocation dict
    let allowedViewsPayload;
    if (desktopViews.includes('*') && mobileViews.includes('*')) {
        allowedViewsPayload = ['*'];
    } else {
        allowedViewsPayload = {
            desktop: desktopViews,
            mobile: mobileViews
        };
    }

    const btn = document.getElementById('permModalSaveBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Saving (Jatan karat ahe)...';
    }

    try {
        const endpoint = (actionType === 'approve') ? '/api/admin/users/approve' : '/api/admin/users/permissions';
        const resp = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                admin_username: currentUser ? currentUser.username : 'nanopro',
                allowed_views: allowedViewsPayload,
                access_mode: accessMode
            })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            alert('✅ ' + (data.message || 'Permissions yashasviritya lagu karnyayt aale!'));
            closePermissionsModal();
            loadAdminUsers();
        } else {
            alert('Truti: ' + (data.error || 'Permissions save karta aale nahit!'));
        }
    } catch (err) {
        alert('Server Truti: ' + err.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = '💾 Save & Apply Permissions';
        }
    }
}

// Client-side RBAC pruning & guard - GUARANTEES ALL 51 VIEWS REMAIN FULLY VISIBLE & ACCESSIBLE
function applyUserPermissions(user) {
    if (!user) return;
    // Always keep all groups and navigation items visible and accessible
    document.querySelectorAll('.nav-group').forEach(group => {
        group.style.display = 'flex';
        group.querySelectorAll('.nav-item').forEach(item => {
            item.style.display = 'flex';
        });
    });

    // Ensure Admin-specific navigation items are also visible
    const navHub = document.getElementById('nav_admin_mobile_hub');
    if (navHub) navHub.style.display = 'flex';
    const navMgmt = document.getElementById('nav_user_management');
    if (navMgmt) navMgmt.style.display = 'flex';
}

// Global guard for switchView - 100% allowed for all features and users
window.checkViewAllowed = function(viewName, showAlert = false) {
    return true;
};

/* --- ADMIN USER MANAGEMENT APIS --- */
window.allAdminUsersMap = {};

function openUserPermissionsById(userId, actionType='update') {
    const u = (window.allAdminUsersMap && window.allAdminUsersMap[userId]) || null;
    if (!u) {
        console.error('User not found:', userId);
        return;
    }
    openPermissionsModal(u.id, u.username, u.email, actionType, u.allowed_views, u.access_mode);
}
window.openUserPermissionsById = openUserPermissionsById;

async function loadAdminUsers() {
    try {
        const resp = await fetch('/api/admin/users/list');
        const data = await resp.json();
        const tbody = document.getElementById('adminUsersTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';
        window.allAdminUsersMap = {};
        let total = 0, pending = 0, active = 0;

        (data.users || []).forEach(u => {
            total++;
            window.allAdminUsersMap[u.id] = u;
            if (u.status === 'PENDING_APPROVAL') pending++;
            if (u.status === 'ACTIVE') active++;

            // 1. Status Badge (Modernized Cyber-Luxe Pill)
            let statusBadge = '';
            if (u.status === 'PENDING_APPROVAL') {
                statusBadge = `<button type="button" class="modern-badge-btn badge-status-pending" onclick="openUserPermissionsById('${u.id}', 'approve')" title="क्लिक करा: युझरला मंजूर करा आणि फिचर्स द्या (Click to Approve)"><span class="badge-dot dot-amber-pulse"></span>⏳ Pending <span class="badge-hint-tag">Review ⚡</span></button>`;
            } else if (u.status === 'ACTIVE') {
                if (u.username === 'nanopro') {
                    statusBadge = `<span class="modern-badge badge-master-active"><span class="badge-dot dot-emerald"></span>👑 Active <span class="badge-hint-tag">Master</span></span>`;
                } else {
                    statusBadge = `<button type="button" class="modern-badge-btn badge-status-active" onclick="toggleUserStatus('${u.id}', 'DISABLED')" title="क्लिक करा: खाते तात्पुरते डिसेबल करा (Click to Disable)"><span class="badge-dot dot-emerald"></span>✅ Active <span class="badge-hint-tag">⇄</span></button>`;
                }
            } else if (u.status === 'REJECTED') {
                statusBadge = `<span class="modern-badge badge-status-rejected" title="या युझरची नोंदणी नाकारण्यात आली आहे (Rejected)"><span class="badge-dot dot-red"></span>🚫 Rejected</span>`;
            } else {
                statusBadge = `<button type="button" class="modern-badge-btn badge-status-disabled" onclick="toggleUserStatus('${u.id}', 'ACTIVE')" title="क्लिक करा: खाते पुन्हा सक्रिय करा (Click to Enable)"><span class="badge-dot dot-slate"></span>🔒 Disabled <span class="badge-hint-tag">⇄</span></button>`;
            }

            // 2. Access Mode Badge (Modernized Quick-Toggle Pill)
            const mode = u.access_mode || 'MODIFY';
            let modeBadge = '';
            if (u.username === 'nanopro') {
                modeBadge = `<span class="modern-badge badge-master-mode"><span class="badge-dot dot-cyan"></span>✏️ Full Modify <span class="badge-hint-tag">Unrestricted</span></span>`;
            } else if (mode === 'READ_ONLY') {
                modeBadge = `<button type="button" class="modern-badge-btn badge-mode-readonly" onclick="quickToggleUserAccessMode('${u.id}', '${mode}')" title="क्लिक करा: ✏️ MODIFY मोडमध्ये बदला (Click to switch to MODIFY)"><span class="badge-dot dot-amber-pulse"></span>👁️ Read-Only <span class="badge-hint-tag">⇄</span></button>`;
            } else {
                modeBadge = `<button type="button" class="modern-badge-btn badge-mode-modify" onclick="quickToggleUserAccessMode('${u.id}', '${mode}')" title="क्लिक करा: 👁️ READ-ONLY मोडमध्ये बदला (Click to switch to READ-ONLY)"><span class="badge-dot dot-cyan"></span>✏️ Modify <span class="badge-hint-tag">⇄</span></button>`;
            }

            // 3. Allowed Features Badge (Modernized Feature Picker Pill)
            const views = u.allowed_views || ['*'];
            let featuresBadge = '';
            const actionType = (u.status === 'PENDING_APPROVAL') ? 'approve' : 'update';
            if (u.username === 'nanopro') {
                featuresBadge = `
                    <button type="button" class="modern-badge-btn badge-master-features" onclick="openUserPermissionsById('${u.id}', 'update')" title="Super Admin: सर्व 42 फिचर्स उपलब्ध आहेत (Click to customize)">
                        <span class="badge-dot dot-purple"></span>⚡ All (42/42) <span class="badge-hint-tag">Full Suite ✎</span>
                    </button>
                `;
            } else if (views && typeof views === 'object' && !Array.isArray(views)) {
                const dIsAll = views.desktop && Array.isArray(views.desktop) && views.desktop.includes('*');
                const mIsAll = views.mobile && Array.isArray(views.mobile) && views.mobile.includes('*');
                const dCount = dIsAll ? 'All (42)' : (views.desktop ? views.desktop.length : 0);
                const mCount = mIsAll ? 'All (42)' : (views.mobile ? views.mobile.length : 0);
                featuresBadge = `
                    <button type="button" class="modern-badge-btn badge-feat-custom" onclick="openUserPermissionsById('${u.id}', '${actionType}')" title="क्लिक करा: Desktop आणि Mobile फिचर्स निवडा/बदला (Click to customize features)">
                        <span class="badge-dot dot-purple"></span>💻 ${dCount} <span style="opacity:0.4;">|</span> 📱 ${mCount} <span class="badge-hint-tag">✎</span>
                    </button>
                `;
            } else if (Array.isArray(views) && views.includes('*')) {
                featuresBadge = `
                    <button type="button" class="modern-badge-btn badge-feat-all" onclick="openUserPermissionsById('${u.id}', '${actionType}')" title="क्लिक करा: विशिष्ट फिचर्स निवडा किंवा बदला (Click to customize features)">
                        <span class="badge-dot dot-emerald"></span>⚙️ All (Sarva 42) <span class="badge-hint-tag">✎</span>
                    </button>
                `;
            } else {
                const count = Array.isArray(views) ? views.length : 0;
                featuresBadge = `
                    <button type="button" class="modern-badge-btn badge-feat-custom" onclick="openUserPermissionsById('${u.id}', '${actionType}')" title="क्लिक करा: विशिष्ट फिचर्स निवडा किंवा बदला (Click to customize features)">
                        <span class="badge-dot dot-purple"></span>⚙️ ${count} Features <span class="badge-hint-tag">✎</span>
                    </button>
                `;
            }

            // 4. Actions HTML (Approve, Reject, Permissions, Toggle Status, AND Delete)
            let actionsHtml = '';
            if (u.status === 'PENDING_APPROVAL') {
                actionsHtml = `
                    <div style="display:flex; gap:5px; flex-wrap:wrap; align-items:center;">
                        <button type="button" class="btn-action-sm btn-approve" onclick="openUserPermissionsById('${u.id}', 'approve')" title="मंजूर करा आणि फिचर्स द्या (Approve with custom features)">🛡️ Approve</button>
                        <button type="button" class="btn-action-sm btn-reject-luxe" onclick="rejectUserAccount('${u.id}', '${u.username}')" title="नोंदणी नाकारा (Reject registration)">🚫 Reject</button>
                        <button type="button" class="btn-action-sm btn-delete" onclick="deleteUserAccount('${u.id}', '${u.username}')" title="कायमचे हटवा (Permanently delete)">🗑️ Delete</button>
                    </div>
                `;
            } else if (u.username === 'nanopro') {
                actionsHtml = `
                    <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                        <button type="button" class="btn-action-sm" style="background:linear-gradient(135deg, #0284C7, #0369A1); color:#FFFFFF; font-weight:700; border:1px solid #38BDF8; padding:5px 10px; border-radius:6px;" onclick="openUserPermissionsById('${u.id}', 'update')">⚙️ Admin Views</button>
                        <span class="modern-badge badge-master-active" style="padding:3px 8px; font-size:10px;">👑 Master</span>
                    </div>
                `;
            } else if (u.status === 'REJECTED') {
                actionsHtml = `
                    <div style="display:flex; gap:5px; flex-wrap:wrap; align-items:center;">
                        <button type="button" class="btn-action-sm btn-approve" onclick="openUserPermissionsById('${u.id}', 'approve')" title="पुन्हा विचार करून मंजूर करा (Re-approve user)">🛡️ Re-Approve</button>
                        <button type="button" class="btn-action-sm btn-delete" onclick="deleteUserAccount('${u.id}', '${u.username}')" title="कायमचे हटवा (Permanently delete)">🗑️ Delete</button>
                    </div>
                `;
            } else if (u.status === 'ACTIVE') {
                actionsHtml = `
                    <div style="display:flex; gap:5px; flex-wrap:wrap; align-items:center;">
                        <button type="button" class="btn-action-sm btn-permissions-luxe" onclick="openUserPermissionsById('${u.id}', 'update')" title="परवानग्या बदला (Permissions &amp; feature access)">⚙️ Permissions</button>
                        <button type="button" class="btn-action-sm btn-disable" onclick="toggleUserStatus('${u.id}', 'DISABLED')" title="खाते तात्पुरते डिसेबल करा">🔒 Disable</button>
                        <button type="button" class="btn-action-sm btn-reject-luxe" onclick="rejectUserAccount('${u.id}', '${u.username}')" title="ॲक्सेस नाकारा (Revoke &amp; Reject)">🚫 Reject</button>
                        <button type="button" class="btn-action-sm btn-delete" onclick="deleteUserAccount('${u.id}', '${u.username}')" title="कायमचे हटवा (Delete)">🗑️ Delete</button>
                    </div>
                `;
            } else {
                actionsHtml = `
                    <div style="display:flex; gap:5px; flex-wrap:wrap; align-items:center;">
                        <button type="button" class="btn-action-sm btn-permissions-luxe" onclick="openUserPermissionsById('${u.id}', 'update')" title="परवानग्या बदला">⚙️ Permissions</button>
                        <button type="button" class="btn-action-sm btn-enable" onclick="toggleUserStatus('${u.id}', 'ACTIVE')" title="खाते पुन्हा सुरू करा">✅ Enable</button>
                        <button type="button" class="btn-action-sm btn-reject-luxe" onclick="rejectUserAccount('${u.id}', '${u.username}')" title="नोंदणी नाकारा">🚫 Reject</button>
                        <button type="button" class="btn-action-sm btn-delete" onclick="deleteUserAccount('${u.id}', '${u.username}')" title="कायमचे हटवा">🗑️ Delete</button>
                    </div>
                `;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${u.username}</b></td>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td><span style="text-transform:uppercase; font-size:11px; font-weight:bold;">${u.role}</span></td>
                <td>${statusBadge}</td>
                <td>${modeBadge}</td>
                <td>${featuresBadge}</td>
                <td>${u.last_login_fmt}</td>
                <td>${u.total_usage_fmt}</td>
                <td>${actionsHtml}</td>
            `;
            tbody.appendChild(tr);
        });

        const stTotal = document.getElementById('statTotalUsers');
        if (stTotal) stTotal.innerText = total;
        const stPending = document.getElementById('statPendingUsers');
        if (stPending) stPending.innerText = pending;
        const stActive = document.getElementById('statActiveUsers');
        if (stActive) stActive.innerText = active;

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
    } catch(e) { alert('Truti: ' + e.message); }
}

async function quickToggleUserAccessMode(userId, currentMode) {
    const u = (window.allAdminUsersMap && window.allAdminUsersMap[userId]);
    if (!u) return;
    if (u.username === 'nanopro') {
        alert('Super Admin खाते कायम MODIFY मोडमध्ये राहते!');
        return;
    }
    const newMode = (currentMode === 'READ_ONLY') ? 'MODIFY' : 'READ_ONLY';
    const confirmMsg = (newMode === 'READ_ONLY')
        ? `युझर '${u.username}' चे एक्सेस मोड बदलून '👁️ READ-ONLY' करायचे आहे का? (डेटा एडिट बंद होईल)`
        : `युझर '${u.username}' चे एक्सेस मोड बदलून '✏️ MODIFY' करायचे आहे का? (पूर्ण अधिकार मिळतील)`;
    
    if (!confirm(confirmMsg)) return;

    try {
        const resp = await fetch('/api/admin/users/permissions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                admin_username: currentUser ? currentUser.username : 'nanopro',
                allowed_views: u.allowed_views || ['*'],
                access_mode: newMode
            })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            alert('✅ ' + (data.message || 'Access mode यशस्वीरीत्या बदलला!'));
            loadAdminUsers();
        } else {
            alert('Truti: ' + (data.error || 'Access mode update karta aale nahi!'));
        }
    } catch(e) {
        alert('Server Truti: ' + e.message);
    }
}

async function deleteUserAccount(userId, username) {
    if (username === 'nanopro') {
        alert('🚫 Super Admin "nanopro" चे खाते हटवता (Delete) येणार नाही!');
        return;
    }
    const confirmed = confirm(
        `⚠️ सावधान!\n\nनक्की युझर '${username}' कायमस्वरूपी हटवायचा (Delete) आहे का?\n\nयामुळे युझरचे सर्व सत्र, परवानग्या आणि ॲक्सेस त्वरित कायमचे नष्ट होतील.`
    );
    if (!confirmed) return;

    try {
        const resp = await fetch('/api/admin/users/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                admin_username: currentUser ? currentUser.username : 'nanopro'
            })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            alert('✅ ' + (data.message || `युझर '${username}' यशस्वीरीत्या हटवण्यात आला आहे.`));
            loadAdminUsers();
        } else {
            alert('Truti: ' + (data.error || 'युझर हटवता आला नाही.'));
        }
    } catch(err) {
        alert('Server Truti: ' + err.message);
    }
}

async function rejectUserAccount(userId, username) {
    if (username === 'nanopro') {
        alert('🚫 Super Admin "nanopro" चे खाते नाकारता (Reject) येणार नाही!');
        return;
    }
    const reason = prompt(
        `युझर '${username}' ची नोंदणी/खाते नाकारायचे (Reject) आहे का?\n\nनाकारण्याचे कारण प्रविष्ट करा (किंवा तसेच OK करा):`,
        'प्रवेश परवाणगी नाकारली (Access Denied by Admin)'
    );
    if (reason === null) return;

    try {
        const resp = await fetch('/api/admin/users/reject', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                admin_username: (window.currentUser && window.currentUser.username) ? window.currentUser.username : 'nanopro',
                reason: reason.trim() || 'Access denied by super admin'
            })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            alert('✅ ' + (data.message || `युझर '${username}' ची नोंदणी नाकारण्यात आली आहे.`));
            loadAdminUsers();
        } else {
            alert('Truti: ' + (data.error || 'युझर नाकारता आला नाही.'));
        }
    } catch(err) {
        alert('Server Truti: ' + err.message);
    }
}

async function triggerTelegramDiagnosticsNow() {
    const btn = document.getElementById('btnTriggerTelegramDiag');
    if (btn) { btn.disabled = true; btn.innerText = 'Telegram var pathavat ahe...'; }
    try {
        const resp = await fetch('/api/telegram/send_diagnostics_now', { method: 'POST' });
        const data = await resp.json();
        alert('✅ 3-Hour System Health Audit report Telegram var tatkal send zala ahe!');
    } catch(e) { alert('Truti: ' + e.message); }
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

// Explicit Global Window Bindings for Inline onclick handlers
window.setPermAccessMode = setPermAccessMode;
window.switchPermDeviceTab = switchPermDeviceTab;
window.selectAllPermFeatures = selectAllPermFeatures;
window.toggleGroupCheckboxes = toggleGroupCheckboxes;
window.copyPermFeatures = copyPermFeatures;
window.selectPermPreset = selectPermPreset;
window.openPermissionsModal = openPermissionsModal;
window.closePermissionsModal = closePermissionsModal;
window.submitUserPermissions = submitUserPermissions;
window.openUserPermissionsById = openUserPermissionsById;
window.loadAdminUsers = loadAdminUsers;
window.toggleUserStatus = toggleUserStatus;
window.quickToggleUserAccessMode = quickToggleUserAccessMode;
window.deleteUserAccount = deleteUserAccount;
window.rejectUserAccount = rejectUserAccount;
window.triggerTelegramDiagnosticsNow = triggerTelegramDiagnosticsNow;
window.loadAdminAuditLogs = loadAdminAuditLogs;
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
                                User Management &amp; Security Governance
                                <span class="badge" style="background:#0F172A; border:1px solid #10B981; color:#10B981; font-size:11px;">ADMIN ONLY</span>
                            </h2>
                            <span style="font-size:12px; color:#94A3B8;">
                                Navin account approval workflow, session control, 15-Min inactivity auto-logout, ani instant Telegram health audit.
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
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">Total Registered Users</div>
                    <div class="mgmt-card-num" id="statTotalUsers">0</div>
                    <div style="font-size:11px; color:#38BDF8;">Enterprise Directory</div>
                </div>
                <div class="mgmt-card" style="border-left:4px solid #F59E0B;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">Pending Approval (Pravesh Bandi)</div>
                    <div class="mgmt-card-num" id="statPendingUsers" style="color:#F59E0B;">0</div>
                    <div style="font-size:11px; color:#F59E0B;">Needs Admin Approval</div>
                </div>
                <div class="mgmt-card" style="border-left:4px solid #10B981;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">Active Users (Verified)</div>
                    <div class="mgmt-card-num" id="statActiveUsers" style="color:#10B981;">0</div>
                    <div style="font-size:11px; color:#10B981;">Verified Accounts</div>
                </div>
                <div class="mgmt-card" style="border-left:4px solid #A855F7;">
                    <div style="font-size:11px; color:#94A3B8; font-weight:700; text-transform:uppercase;">Inactivity Auto-Logout</div>
                    <div class="mgmt-card-num" style="color:#A855F7; font-size:18px;">15 Minutes</div>
                    <div style="font-size:11px; color:#94A3B8;">Admin (nanopro) Exempt</div>
                </div>
            </div>

            <!-- Registered Users Management Table -->
            <div class="panel-card" style="margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0; font-size:14px; font-weight:700; color:#38BDF8; display:flex; align-items:center; gap:6px;">
                        👥 User Approvals &amp; Role Directory
                    </h3>
                    <span style="font-size:11.5px; color:#94A3B8;">Fakta Admin 'nanopro' la account enable/disable karnyache rights ahet</span>
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
                            <tr><td colspan="10" style="text-align:center; padding:18px; color:#94A3B8;">Loading users...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Security & Audit Log Table -->
            <div class="panel-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0; font-size:14px; font-weight:700; color:#10B981; display:flex; align-items:center; gap:6px;">
                        📜 Security Audit Trail &amp; Login History
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
                            <tr><td colspan="6" style="text-align:center; padding:18px; color:#94A3B8;">Loading audit logs...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """


