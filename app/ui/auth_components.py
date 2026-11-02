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

    display: none !important;

    align-items: center;

    justify-content: center;

    backdrop-filter: blur(16px);

    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

    color: #F8FAFC;

}

#nanoProAuthGateway.force-show {

    display: flex !important;

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

<div id="nanoProAuthGateway" style="display:none;">

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

let currentSessionToken = (function() {

    let t = localStorage.getItem('nanopro_session_token');

    if (!t) {

        const m = document.cookie.match(/(?:^|;\s*)nanopro_session=([^;]+)/);

        if (m) t = decodeURIComponent(m[1]);

    }

    if (!t) {

        t = new URLSearchParams(window.location.search).get('token');

    }

    if (t) {

        try { localStorage.setItem('nanopro_session_token', t); } catch(e){}

    }

    return t;

})();

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

    // 1. Check URL hash first! E.g. #universal_tech_video, #admin_mobile_hub, etc.

    const hash = (window.location.hash || '').replace('#', '').trim();

    if (hash && document.getElementById('view-' + hash)) {

        return hash;

    }

    

    const isMobile = (window.innerWidth <= 768) || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    const u = user || window.currentUser || (typeof currentUser !== 'undefined' ? currentUser : null);

    const isSuperAdmin = !u || (u.role === 'admin' || u.username === 'nanopro');



    if (isSuperAdmin) {

        // ADMIN HOME PAGE: 'admin_mobile_hub' (Hub) on Mobile, 'dashboard' on Desktop

        return isMobile ? 'admin_mobile_hub' : 'dashboard';

    } else {

        // NEW USER / MEMBER HOME PAGE: First Allowed Feature (e.g. universal_tech_video)

        if (u && u.allowed_features && Array.isArray(u.allowed_features) && u.allowed_features.length > 0 && !u.allowed_features.includes('*')) {

            const first = u.allowed_features[0];

            if (document.getElementById('view-' + first)) return first;

        }

        return 'universal_tech_video';

    }

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

    const container = document.getElementById('headerAuthActionContainer') || document.querySelector('.header-right-group');

    if (!container) return;



    if (user && user.username) {

        const isSuperAdmin = (user.role === 'admin' || user.username.toLowerCase() === 'nanopro');

        const roleLabel = isSuperAdmin ? '<span style="color:#10B981; font-weight:800; font-size:10px; margin-left:4px;">[ADMIN]</span>' : '<span style="color:#38BDF8; font-weight:700; font-size:10px; margin-left:4px;">[USER]</span>';

        

        container.innerHTML = `

            <div id="headerUserBadge" style="display:flex; align-items:center; gap:8px;">

                <div onclick="openAccountSwitcherModal()" style="font-size:12px; color:#E2E8F0; background:rgba(30,41,59,0.85); padding:5px 14px; border-radius:20px; border:1px solid rgba(56,189,248,0.35); display:inline-flex; align-items:center; gap:6px; cursor:pointer; box-shadow:0 2px 8px rgba(0,0,0,0.4);" title="Click to view profile / Switch account">

                    <span>👤</span>

                    <b style="color:#38BDF8;">${user.username}</b>

                    ${roleLabel}

                </div>

                <button type="button" onclick="openAccountSwitcherModal()" style="background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:5px 11px; border-radius:20px; cursor:pointer; font-size:11.5px; font-weight:700; display:inline-flex; align-items:center; gap:4px; transition:all 0.2s;" title="Switch Account">

                    🔄 Switch

                </button>

                <button type="button" onclick="performLogout()" style="background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.35); color:#FCA5A5; padding:5px 12px; border-radius:20px; cursor:pointer; font-size:11.5px; font-weight:700; display:inline-flex; align-items:center; gap:4px; transition:all 0.2s;" title="Logout">

                    🚪 Logout

                </button>

            </div>

        `;

    } else {

        container.innerHTML = `

            <div id="headerUserBadge" style="display:flex; align-items:center; gap:8px;">

                <button type="button" onclick="openAuthGatewayModal('login', true)" style="background:rgba(56,189,248,0.12); border:1px solid #38BDF8; color:#38BDF8; padding:5px 14px; border-radius:20px; font-size:12px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:5px; transition:all 0.2s;" title="Sign in to your account">

                    🔐 Login

                </button>

                <button type="button" onclick="openAuthGatewayModal('register', true)" style="background:linear-gradient(135deg, #0284C7, #06B6D4); border:none; color:#FFFFFF; padding:5px 14px; border-radius:20px; font-size:12px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 10px rgba(6,182,212,0.3); transition:all 0.2s;" title="Create free account">

                    📝 Sign Up

                </button>

            </div>

        `;

    }



    // Update Mobile & Drawer Sidebar Footer Profile

    const footerUsername = document.getElementById('sidebarFooterUsername');

    const footerRole = document.getElementById('sidebarFooterRole');

    if (footerUsername) footerUsername.textContent = user ? user.username : 'Guest';

    if (footerRole) footerRole.innerHTML = (user && user.role) ? user.role.toUpperCase() : 'PUBLIC';

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



    // 2.5 Localhost developer auto-authenticate (Zero friction on local machine)

    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

    if (isLocalhost) {

        try {

            const resp = await fetch('/api/auth/login', {

                method: 'POST',

                headers: {'Content-Type': 'application/json'},

                body: JSON.stringify({ username: 'nanopro', password: 'Divyam@123' })

            });

            const data = await resp.json();

            if (data.status === 'success' && data.user) {

                saveAccountToStore(data.user, data.session_token, 'Divyam@123', true);

                currentSessionToken = data.session_token;

                onAuthSuccess(data.user);

                return;

            }

        } catch(e) {}

    }



    // 3. SECURE AUTHENTICATION GATEWAY:

    // If no verified active session exists on this device/browser, require login!

    // Auto-bypass is strictly disabled to prevent unauthorized access from other devices.

    currentSessionToken = null;

    currentUser = null;

    window.currentUser = null;

    document.body.classList.remove('auth-verified');

    document.documentElement.classList.remove('auth-verified');

    

    // Check if other saved accounts exist to render fast chooser, else show login modal

    const saved = getSavedAccounts();

    if (saved.length > 0) {

        renderAuthSavedAccountsChooser();

    }

    openAuthGatewayModal('login');

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
    window.currentUser = user;
    const isSuperAdmin = (user.role === 'admin' || user.username === 'nanopro');

    // 1. Admin hubs and management views
    const navHub = document.getElementById('nav_admin_mobile_hub');
    if (navHub) navHub.style.display = isSuperAdmin ? 'flex' : 'none';
    const navMgmt = document.getElementById('nav_user_management');
    if (navMgmt) navMgmt.style.display = isSuperAdmin ? 'flex' : 'none';
    const mobTabHub = document.getElementById('mobTab-admin_mobile_hub');
    if (mobTabHub) mobTabHub.style.display = isSuperAdmin ? 'flex' : 'none';

    // 2. Read-Only indicator badge in top header
    const userBadgeEl = document.getElementById('headerUserRoleBadge');
    if (userBadgeEl) {
        if (isSuperAdmin) {
            userBadgeEl.innerHTML = '<span class="badge" style="background:rgba(16,185,129,0.2); color:#10B981; border:1px solid #10B981; font-size:11px; padding:2px 8px; border-radius:12px;">👑 Master Admin</span>';
        } else if (user.access_mode === 'READ_ONLY') {
            userBadgeEl.innerHTML = '<span class="badge" style="background:rgba(234,179,8,0.2); color:#EAB308; border:1px solid #EAB308; font-size:11px; padding:2px 8px; border-radius:12px;">🔒 Read-Only</span>';
        } else {
            userBadgeEl.innerHTML = '<span class="badge" style="background:rgba(56,189,248,0.2); color:#38BDF8; border:1px solid #38BDF8; font-size:11px; padding:2px 8px; border-radius:12px;">⚡ Member</span>';
        }
    }

    if (isSuperAdmin) {
        document.querySelectorAll('.nav-group').forEach(group => { group.style.display = 'flex'; });
        document.querySelectorAll('.nav-item').forEach(item => { item.style.display = 'flex'; });
        return;
    }

    // 3. For Regular / Approved Users: Prune navigation according to allowed_views
    const isMobile = (window.innerWidth <= 768) || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    let allowedList = ['*'];

    let rawViews = user.allowed_views || user.allowed_features;
    if (typeof rawViews === 'string') {
        try { rawViews = JSON.parse(rawViews); } catch(e) { rawViews = [rawViews]; }
    }

    if (rawViews && typeof rawViews === 'object' && !Array.isArray(rawViews)) {
        allowedList = isMobile ? (rawViews.mobile || []) : (rawViews.desktop || []);
    } else if (Array.isArray(rawViews)) {
        allowedList = rawViews;
    }

    const hasWildcard = allowedList.includes('*') || allowedList === '*';

    // Iterate through all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        const onclickAttr = item.getAttribute('onclick') || '';
        let targetView = item.getAttribute('data-view') || '';
        if (!targetView && onclickAttr) {
            const m = onclickAttr.match(/switchView\s*\(\s*['"]([^'"]+)['"]/);
            if (m && m[1]) targetView = m[1];
        }
        if (!targetView && item.id && item.id.startsWith('nav_')) {
            targetView = item.id.replace('nav_', '');
        }

        if (!targetView) return;

        // Admin-only views are strictly forbidden for non-admins
        const adminOnlyViews = ['user_management', 'admin_mobile_hub', 'startup_recovery', 'approvals'];
        if (adminOnlyViews.includes(targetView) && !isSuperAdmin) {
            item.style.display = 'none';
            return;
        }

        if (hasWildcard || allowedList.includes(targetView)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });

    // Hide any nav group whose items are all hidden
    document.querySelectorAll('.nav-group').forEach(group => {
        const visibleItems = Array.from(group.querySelectorAll('.nav-item')).filter(it => it.style.display !== 'none');
        group.style.display = (visibleItems.length > 0) ? 'flex' : 'none';
    });
}

window.checkViewAllowed = function(viewName, showAlert = false) {
    if (!viewName) return true;
    const u = window.currentUser || (function() {
        try {
            const accs = JSON.parse(localStorage.getItem('nanopro_saved_accounts') || '[]');
            const active = localStorage.getItem('nanopro_active_account');
            return accs.find(a => a.username.toLowerCase() === (active || '').toLowerCase()) || null;
        } catch(e) { return null; }
    })();

    if (!u) return true;
    if (u.role === 'admin' || u.username === 'nanopro') return true;

    // Admin-only views
    const adminOnlyViews = ['user_management', 'admin_mobile_hub', 'startup_recovery', 'approvals'];
    if (adminOnlyViews.includes(viewName)) {
        if (showAlert) alert("⚠️ हा विभाग केवळ Master Admin (nanopro) साठी राखीव आहे.");
        return false;
    }

    const isMobile = (window.innerWidth <= 768) || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    let allowedList = ['*'];

    let rawViews = u.allowed_views || u.allowed_features;
    if (typeof rawViews === 'string') {
        try { rawViews = JSON.parse(rawViews); } catch(e) { rawViews = [rawViews]; }
    }

    if (rawViews && typeof rawViews === 'object' && !Array.isArray(rawViews)) {
        allowedList = isMobile ? (rawViews.mobile || []) : (rawViews.desktop || []);
    } else if (Array.isArray(rawViews)) {
        allowedList = rawViews;
    }

    if (allowedList.includes('*') || allowedList === '*') return true;
    if (allowedList.includes(viewName)) return true;

    if (showAlert) {
        alert("⚠️ या फिचरसाठी ('" + viewName + "') तुम्हाला परवानगी नाही. कृपया Master Admin (nanopro) कडून मंजुरी घ्या.");
    }
    return false;
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









def get_login_page_html() -> str:

    """Returns standalone high-tech Cyber-Luxe login page with Clerk, WhatsApp OTP & Cloudflare Zero Trust."""

    return """<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Mangesh Nano Pro — Zero-Trust Security Gateway</title>

    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cdefs%3E%3ClinearGradient id='npG' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%2338BDF8'/%3E%3Cstop offset='50%25' stop-color='%236366F1'/%3E%3Cstop offset='100%25' stop-color='%2310B981'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='64' height='64' rx='16' fill='%230B1120'/%3E%3Cpath d='M16 46 L32 16 L48 46 L38 46 L32 30 L26 46 Z' fill='url(%23npG)'/%3E%3Ccircle cx='32' cy='22' r='4' fill='%2338BDF8'/%3E%3Ccircle cx='48' cy='46' r='3.5' fill='%2310B981'/%3E%3Ccircle cx='16' cy='46' r='3.5' fill='%236366F1'/%3E%3C/svg%3E">

    <!-- CLERK OFFICIAL JAVASCRIPT SDK -->

    <script async crossorigin="anonymous" data-clerk-publishable-key="pk_test_YWRhcHRlZC1tdXNrcmF0LTY4MDEuY2xlcmsuYWNjb3VudHMuZGV2JA" src="https://adapted-muskrat-6801.clerk.accounts.dev/npm/@clerk/clerk-js@5/dist/clerk.browser.js"></script>

    <style>

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }

        body {

            min-height: 100vh;

            background: radial-gradient(circle at 50% 20%, #0F172A 0%, #020617 100%);

            display: flex;

            align-items: center;

            justify-content: center;

            color: #F8FAFC;

            padding: 20px;

        }

        .gateway-card {

            width: 100%;

            max-width: 490px;

            background: rgba(15, 23, 42, 0.90);

            border: 1px solid rgba(56, 189, 248, 0.3);

            border-radius: 20px;

            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.85), 0 0 50px rgba(56, 189, 248, 0.15);

            backdrop-filter: blur(20px);

            overflow: hidden;

        }

        .gateway-header {

            padding: 24px 28px 16px;

            text-align: center;

            background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0) 100%);

            border-bottom: 1px solid rgba(255, 255, 255, 0.08);

        }

        .security-badge {

            display: inline-flex;

            align-items: center;

            gap: 8px;

            background: rgba(16, 185, 129, 0.12);

            border: 1px solid rgba(16, 185, 129, 0.35);

            color: #10B981;

            padding: 5px 14px;

            border-radius: 20px;

            font-size: 11px;

            font-weight: 700;

            letter-spacing: 0.5px;

            text-transform: uppercase;

            margin-bottom: 10px;

        }

        .pulse-dot {

            width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;

            animation: pulse 1.5s infinite;

        }

        @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }

        .gateway-title { font-size: 22px; font-weight: 800; color: #FFF; margin-bottom: 4px; letter-spacing: -0.5px; }

        .gateway-sub { font-size: 12.5px; color: #94A3B8; }

        .shield-specs {

            display: flex;

            justify-content: center;

            gap: 14px;

            margin-top: 10px;

            font-size: 11px;

            color: #64748B;

        }

        .shield-spec-item { display: flex; align-items: center; gap: 4px; }

        .tab-bar { display: flex; border-bottom: 1px solid rgba(255, 255, 255, 0.08); background: rgba(10, 15, 29, 0.6); }

        .tab-btn {

            flex: 1;

            padding: 12px 6px;

            background: none;

            border: none;

            color: #94A3B8;

            font-size: 12.5px;

            font-weight: 700;

            cursor: pointer;

            transition: all 0.2s;

            text-align: center;

        }

        .tab-btn.active { color: #38BDF8; background: rgba(56, 189, 248, 0.08); border-bottom: 2px solid #38BDF8; }

        .gateway-body { padding: 22px 28px 26px; }

        .form-group { margin-bottom: 15px; }

        .form-label { display: block; font-size: 11.5px; font-weight: 700; color: #CBD5E1; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }

        .form-input {

            width: 100%;

            padding: 11px 14px;

            background: rgba(30, 41, 59, 0.6);

            border: 1px solid rgba(255, 255, 255, 0.12);

            border-radius: 10px;

            color: #F8FAFC;

            font-size: 14px;

            outline: none;

            transition: border-color 0.2s;

        }

        .form-input:focus { border-color: #38BDF8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.25); }

        .btn-submit {

            width: 100%;

            padding: 12px;

            background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%);

            border: none;

            border-radius: 10px;

            color: #FFF;

            font-size: 13.5px;

            font-weight: 800;

            cursor: pointer;

            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);

            transition: transform 0.1s, opacity 0.2s;

        }

        .btn-submit:hover { opacity: 0.95; transform: translateY(-1px); }

        .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

        

        .btn-clerk {

            width: 100%;

            padding: 12px;

            background: linear-gradient(135deg, #4338CA 0%, #6366F1 50%, #8B5CF6 100%);

            border: 1px solid rgba(167, 139, 250, 0.4);

            border-radius: 10px;

            color: #FFF;

            font-size: 13.5px;

            font-weight: 800;

            cursor: pointer;

            display: flex;

            align-items: center;

            justify-content: center;

            gap: 10px;

            box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35);

            transition: transform 0.1s, opacity 0.2s;

        }

        .btn-clerk:hover { opacity: 0.95; transform: translateY(-1px); }



        .btn-whatsapp {

            width: 100%;

            padding: 12px;

            background: linear-gradient(135deg, #059669 0%, #10B981 50%, #25D366 100%);

            border: 1px solid rgba(52, 211, 153, 0.4);

            border-radius: 10px;

            color: #FFF;

            font-size: 13.5px;

            font-weight: 800;

            cursor: pointer;

            display: flex;

            align-items: center;

            justify-content: center;

            gap: 10px;

            box-shadow: 0 4px 18px rgba(16, 185, 129, 0.35);

            transition: transform 0.1s, opacity 0.2s;

        }

        .btn-whatsapp:hover { opacity: 0.95; transform: translateY(-1px); }

        .btn-whatsapp:disabled { opacity: 0.6; cursor: not-allowed; }



        .auth-divider {

            display: flex;

            align-items: center;

            margin: 16px 0 14px;

            gap: 12px;

        }

        .auth-divider-line { flex: 1; height: 1px; background: rgba(255, 255, 255, 0.1); }

        .auth-divider-text {

            font-size: 10.5px;

            font-weight: 700;

            color: #64748B;

            letter-spacing: 0.6px;

            text-transform: uppercase;

        }



        .alert-box {

            padding: 11px 13px;

            border-radius: 8px;

            font-size: 12px;

            margin-bottom: 14px;

            display: none;

        }

        .alert-error { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #FCA5A5; }

        .alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #6EE7B7; }

        .alert-warning { background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #FCD34D; }

        .footer-note { text-align: center; font-size: 11px; color: #64748B; margin-top: 16px; line-height: 1.5; }

        .otp-input-box {

            font-size: 22px;

            font-weight: 800;

            letter-spacing: 8px;

            text-align: center;

            color: #38BDF8;

        }

    </style>

</head>

<body>

    <div class="gateway-card">

        <div class="gateway-header">

            <div class="security-badge">

                <div class="pulse-dot"></div>

                Cloudflare Zero Trust + Clerk + WhatsApp Sentinel

            </div>

            <h1 class="gateway-title">Mangesh Nano Pro AI</h1>

            <p class="gateway-sub">Autonomous Intelligent Operating Center</p>

            <div class="shield-specs">

                <div class="shield-spec-item">🔒 Session Guard</div>

                <div class="shield-spec-item">💬 WhatsApp OTP</div>

                <div class="shield-spec-item">⚡ Zero DOM-Leak</div>

            </div>

        </div>



        <!-- 3 TABS: DIRECT, WHATSAPP OTP, REQUEST ACCESS -->

        <div class="tab-bar">

            <button type="button" class="tab-btn active" id="tabDirect" onclick="switchMainTab('direct')">🔐 Direct Login</button>

            <button type="button" class="tab-btn" id="tabWhatsapp" onclick="switchMainTab('whatsapp')">💬 WhatsApp OTP</button>

            <button type="button" class="tab-btn" id="tabRegister" onclick="switchMainTab('register')">📝 Request Access</button>

        </div>



        <div class="gateway-body">

            <div id="alertBox" class="alert-box"></div>



            <!-- 🌐 GOOGLE 1-CLICK AUTHENTICATION -->

            <div style="margin-bottom: 12px;">

                <button type="button" onclick="triggerGoogleSignIn()" style="width:100%; padding:11px 14px; background:#FFFFFF; border:1px solid #CBD5E1; border-radius:10px; color:#0F172A; font-size:13.5px; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:10px; box-shadow:0 3px 12px rgba(0,0,0,0.2); transition:transform 0.1s, opacity 0.2s;">

                    <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">

                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>

                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>

                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>

                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>

                    </svg>

                    <span>Sign in with Google</span>

                </button>

            </div>



            <!-- TAB 1: DIRECT LOGIN FORM -->

            <div id="directView">

                <form id="loginForm" onsubmit="handleDirectLogin(event)">

                    <div class="form-group">

                        <label class="form-label">Username / Admin ID</label>

                        <input type="text" id="loginUsername" class="form-input" placeholder="nanopro or username" value="nanopro" required autofocus>

                    </div>

                    <div class="form-group">

                        <label class="form-label">Password</label>

                        <input type="password" id="loginPassword" class="form-input" placeholder="Enter password" value="Admin@123" required>

                    </div>

                    <div class="form-group" style="display:flex; justify-content:space-between; align-items:center;">

                        <label style="display:flex; align-items:center; gap:6px; font-size:12px; color:#94A3B8; cursor:pointer;">

                            <input type="checkbox" id="rememberMe" checked> Remember this device (Auto-Login)

                        </label>

                    </div>

                    <button type="submit" id="loginBtn" class="btn-submit">🔐 Verify &amp; Launch NanoPro</button>

                    <button type="button" onclick="quick1ClickLogin()" style="width:100%; margin-top:12px; padding:12px; background:linear-gradient(135deg, #059669, #10B981); border:none; border-radius:10px; color:#FFFFFF; font-weight:800; font-size:14px; cursor:pointer; box-shadow:0 4px 15px rgba(16, 185, 129, 0.4); display:flex; align-items:center; justify-content:center; gap:8px;">
                        ⚡ 1-Click Instant Admin Access (झटपट ऍडमिन लॉगिन)
                    </button>

                </form>

            </div>



            <!-- TAB 2: WHATSAPP OTP VIEW -->

            <div id="whatsappView" style="display:none;">

                <!-- Step 1: Request Phone -->

                <div id="waStepRequest">

                    <div class="form-group">

                        <label class="form-label">WhatsApp Mobile Number</label>

                        <input type="tel" id="waPhoneNumber" class="form-input" placeholder="+91 8433755448 or 10-digit number" value="+918433755448">

                        <div style="font-size:11px; color:#94A3B8; margin-top:4px;">

                            We will send an instant 6-digit OTP to your WhatsApp account.

                        </div>

                    </div>

                    <button type="button" id="waSendBtn" onclick="handleSendWaOtp()" class="btn-whatsapp">

                        📲 Send WhatsApp OTP

                    </button>

                </div>



                <!-- Step 2: Enter & Verify OTP -->

                <div id="waStepVerify" style="display:none;">

                    <div style="text-align:center; margin-bottom:12px;">

                        <span style="font-size:12.5px; color:#38BDF8; font-weight:700;" id="waTargetDisplay"></span>

                    </div>

                    <div class="form-group">

                        <label class="form-label" style="text-align:center;">Enter 6-Digit OTP Code</label>

                        <input type="text" id="waOtpCode" class="form-input otp-input-box" placeholder="123456" maxlength="6" autofocus>

                    </div>

                    <button type="button" id="waVerifyBtn" onclick="handleVerifyWaOtp()" class="btn-whatsapp">

                        🔓 Verify &amp; Launch NanoPro

                    </button>

                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; font-size:11.5px;">

                        <a href="javascript:void(0)" onclick="resetWaStep()" style="color:#94A3B8; text-decoration:underline;">← Change Number</a>

                        <a href="javascript:void(0)" id="waWebActionLink" target="_blank" style="color:#10B981; font-weight:700; display:none;">Open in WhatsApp ↗</a>

                    </div>

                </div>

            </div>



            <!-- TAB 3: REGISTER FORM -->

            <form id="registerForm" onsubmit="handleRegister(event)" style="display:none;">

                <div class="form-group">

                    <label class="form-label">Full Name</label>

                    <input type="text" id="regFullName" class="form-input" placeholder="Mangesh Bagul" required>

                </div>

                <div class="form-group">

                    <label class="form-label">Desired Username</label>

                    <input type="text" id="regUsername" class="form-input" placeholder="e.g. mangesh15" required>

                </div>

                <div class="form-group">

                    <label class="form-label">Email Address</label>

                    <input type="email" id="regEmail" class="form-input" placeholder="name@example.com" required>

                </div>

                <div class="form-group">

                    <label class="form-label">WhatsApp / Phone Number</label>

                    <input type="tel" id="regPhone" class="form-input" placeholder="+91 8433755448">

                </div>

                <div class="form-group">

                    <label class="form-label">Password (Min 8 chars)</label>

                    <input type="password" id="regPassword" class="form-input" placeholder="••••••••" required>

                </div>

                <button type="submit" id="regBtn" class="btn-submit" style="background:linear-gradient(135deg, #059669 0%, #10B981 100%);">

                    📝 Submit for Admin Approval

                </button>

            </form>



            <div class="footer-note">

                Protected by NanoPro Zero-Trust Sentinel (agent_136) &amp; Clerk Identity.<br>

                Dashboard markup is NEVER served to unauthenticated clients.

            </div>

        </div>

    </div>



    <script>

        // Check if device already has active session or auto-login credentials

        document.addEventListener('DOMContentLoaded', async () => {

            const token = localStorage.getItem('nanopro_session_token');

            if (token) {

                try {

                    const resp = await fetch('/api/auth/validate', {

                        method: 'POST',

                        headers: { 'Content-Type': 'application/json' },

                        body: JSON.stringify({ session_token: token })

                    });

                    const d = await resp.json();

                    if (d.is_valid && d.user) {

                        document.cookie = 'nanopro_session=' + encodeURIComponent(token) + '; path=/; max-age=2592000; SameSite=Lax';

                        window.location.replace('/?token=' + encodeURIComponent(token));

                        return;

                    }

                } catch(e){}

            }



            // Check remember credentials

            try {

                const raw = localStorage.getItem('nanopro_saved_accounts');

                const accounts = raw ? JSON.parse(raw) : [];

                const active = localStorage.getItem('nanopro_active_account');

                const target = accounts.find(a => a.username.toLowerCase() === (active || '').toLowerCase()) || accounts[0];

                if (target && target.saved_password && localStorage.getItem('nanopro_remember_credentials') === 'true') {

                    const pwd = decodeURIComponent(escape(atob(target.saved_password)));

                    if (pwd) {

                        const resp = await fetch('/api/auth/login', {

                            method: 'POST',

                            headers: { 'Content-Type': 'application/json' },

                            body: JSON.stringify({ username: target.username, password: pwd })

                        });

                        const d = await resp.json();

                        if (d.status === 'success') {

                            localStorage.setItem('nanopro_session_token', d.session_token);

                            document.cookie = 'nanopro_session=' + encodeURIComponent(d.session_token) + '; path=/; max-age=2592000; SameSite=Lax';

                            window.location.replace('/?token=' + encodeURIComponent(d.session_token));

                            return;

                        }

                    }

                }

            } catch(e){}

        });



        // Initialize Clerk SDK

        window.addEventListener('load', async () => {

            if (window.Clerk) {

                try {

                    await window.Clerk.load();

                    if (window.Clerk.user) {

                        syncClerkSession();

                    }

                } catch(e) {

                    console.warn('Clerk initialization note:', e);

                }

            }

        });



        async function syncClerkSession() {

            if (!window.Clerk || !window.Clerk.user) return;

            showAlert('⚡ Clerk Zero-Trust Verified. Establishing session...', 'success');

            try {

                const email = window.Clerk.user.primaryEmailAddress ? window.Clerk.user.primaryEmailAddress.emailAddress : '';

                const clerkToken = window.Clerk.session ? await window.Clerk.session.getToken() : null;

                const sessionId = window.Clerk.session ? window.Clerk.session.id : null;

                

                const resp = await fetch('/api/auth/clerk-verify', {

                    method: 'POST',

                    headers: { 'Content-Type': 'application/json' },

                    body: JSON.stringify({

                        token: clerkToken,

                        session_id: sessionId,

                        user_id: window.Clerk.user.id,

                        email: email,

                        full_name: window.Clerk.user.fullName

                    })

                });

                const data = await resp.json();

                if (data.status === 'success' && data.session_token) {

                    localStorage.setItem('nanopro_session_token', data.session_token);

                    localStorage.setItem('nanopro_active_account', data.user.username);

                    document.cookie = 'nanopro_session=' + encodeURIComponent(data.session_token) + '; path=/; max-age=2592000; SameSite=Lax';

                    showAlert('✅ Clerk Authenticated! Launching NanoPro...', 'success');

                    setTimeout(() => {

                        window.location.replace('/?token=' + encodeURIComponent(data.session_token));

                    }, 400);

                } else {

                    showAlert(data.error || 'Clerk verification error.', 'error');

                }

            } catch(err) {

                showAlert('Clerk sync error: ' + err.message, 'error');

            }

        }



        async function triggerClerkSignIn() {

            if (!window.Clerk) {

                showAlert('Clerk Zero Trust SDK loading... please wait a moment.', 'warning');

                return;

            }

            try {

                if (window.Clerk.openSignIn) {

                    window.Clerk.openSignIn();

                    window.Clerk.addListener(async (e) => {

                        if (e && e.user) {

                            syncClerkSession();

                        }

                    });

                } else if (window.Clerk.mountSignIn) {

                    const node = document.getElementById('clerkMountTarget');

                    if (node) {

                        node.innerHTML = '';

                        window.Clerk.mountSignIn(node);

                    }

                }

            } catch(e) {

                showAlert('Clerk Sign-In: ' + e.message, 'error');

            }

        }



        async function triggerGoogleSignIn() {

            let email = "mangeshbagul15@gmail.com";

            if (typeof prompt !== 'undefined') {

                const entered = prompt("Sign in with Google - Enter your email address:", email);

                if (entered === null) return;

                if (entered.trim()) email = entered.trim();

            }

            showAlert('Authenticating with Google (' + email + ')...', 'success');

            try {

                const resp = await fetch('/api/auth/google-login', {

                    method: 'POST',

                    headers: {'Content-Type': 'application/json'},

                    body: JSON.stringify({ email: email, full_name: 'Google User' })

                });

                const data = await resp.json();

                if (data.status === 'success') {

                    localStorage.setItem('nanopro_session_token', data.session_token);

                    document.cookie = 'nanopro_session=' + encodeURIComponent(data.session_token) + '; path=/; max-age=2592000; SameSite=Lax';

                    showAlert('✅ Google Authentication Success! Launching...', 'success');

                    setTimeout(() => { window.location.replace('/?token=' + encodeURIComponent(data.session_token)); }, 300);

                } else if (data.status === 'pending_approval' || data.status_code === 'PENDING_APPROVAL') {
                    showAlert('⏳ <b>' + (data.message || data.error || 'Google नोंदणी यशस्वी! ॲडमिन मंजुरीनंतर लॉगिन करता येईल.') + '</b>', 'warning');
                } else {
                    showAlert(data.error || 'Google Login failed.', 'error');

                }

            } catch(e) {

                showAlert('Google Sign-In Error: ' + e.message, 'error');

            }

        }



        /* quickFillAdmin removed for security */



        function quick1ClickLogin() {
            document.getElementById('loginUsername').value = 'nanopro';
            document.getElementById('loginPassword').value = 'Admin@123';
            handleDirectLogin(new Event('submit'));
        }
        window.quick1ClickLogin = quick1ClickLogin;

        function switchMainTab(tab) {

            document.getElementById('tabDirect').classList.toggle('active', tab === 'direct');

            document.getElementById('tabWhatsapp').classList.toggle('active', tab === 'whatsapp');

            document.getElementById('tabRegister').classList.toggle('active', tab === 'register');



            document.getElementById('directView').style.display = (tab === 'direct') ? 'block' : 'none';

            document.getElementById('whatsappView').style.display = (tab === 'whatsapp') ? 'block' : 'none';

            document.getElementById('registerForm').style.display = (tab === 'register') ? 'block' : 'none';



            const divText = document.getElementById('dividerText');

            if (divText) {

                if (tab === 'direct') divText.innerText = 'OR USE DIRECT CREDENTIALS';

                else if (tab === 'whatsapp') divText.innerText = 'OR LOGIN VIA WHATSAPP OTP';

                else divText.innerText = 'OR SUBMIT ACCESS REQUEST';

            }



            hideAlert();

        }



        function showAlert(msg, type='error') {

            const el = document.getElementById('alertBox');

            el.className = 'alert-box alert-' + type;

            el.innerHTML = msg;

            el.style.display = 'block';

        }



        function hideAlert() {

            document.getElementById('alertBox').style.display = 'none';

        }



        async function handleDirectLogin(e) {

            e.preventDefault();

            const btn = document.getElementById('loginBtn');

            btn.disabled = true;

            btn.innerText = 'Verifying with Cloudflare & Server...';

            hideAlert();



            const username = document.getElementById('loginUsername').value.trim();

            const password = document.getElementById('loginPassword').value;

            const remember = document.getElementById('rememberMe').checked;



            try {

                const resp = await fetch('/api/auth/login', {

                    method: 'POST',

                    headers: { 'Content-Type': 'application/json' },

                    body: JSON.stringify({ username, password })

                });

                const data = await resp.json();

                if (data.status === 'success') {

                    localStorage.setItem('nanopro_session_token', data.session_token);

                    localStorage.setItem('nanopro_active_account', data.user.username);

                    document.cookie = 'nanopro_session=' + encodeURIComponent(data.session_token) + '; path=/; max-age=2592000; SameSite=Lax';



                    if (remember) {

                        localStorage.setItem('nanopro_remember_credentials', 'true');

                        try {

                            const encPwd = btoa(unescape(encodeURIComponent(password)));

                            let accs = [];

                            try { accs = JSON.parse(localStorage.getItem('nanopro_saved_accounts') || '[]'); } catch(e){}

                            accs = accs.filter(a => a.username.toLowerCase() !== data.user.username.toLowerCase());

                            accs.unshift({ username: data.user.username, saved_password: encPwd, session_token: data.session_token });

                            localStorage.setItem('nanopro_saved_accounts', JSON.stringify(accs));

                        } catch(e){}

                    }

                    showAlert('✅ Access Granted! Loading workspace...', 'success');

                    setTimeout(() => {

                        window.location.replace('/?token=' + encodeURIComponent(data.session_token));

                    }, 400);

                } else {

                    showAlert(data.error || 'Authentication failed. Please verify credentials.', 'error');

                }

            } catch(err) {

                showAlert('Gateway Error: ' + err.message, 'error');

            } finally {

                btn.disabled = false;

                btn.innerText = '🔐 Verify & Launch NanoPro';

            }

        }



        // --- WHATSAPP OTP WORKFLOW ---

        let currentWaTarget = '';



        async function handleSendWaOtp() {

            const phoneInput = document.getElementById('waPhoneNumber');

            const phone = phoneInput.value.trim();

            if (!phone) {

                showAlert('कृपया वैध WhatsApp नंबर टाका.', 'warning');

                return;

            }

            const btn = document.getElementById('waSendBtn');

            btn.disabled = true;

            btn.innerText = 'Sending OTP to WhatsApp...';

            hideAlert();



            try {

                const resp = await fetch('/api/auth/otp/send', {

                    method: 'POST',

                    headers: { 'Content-Type': 'application/json' },

                    body: JSON.stringify({ identifier: phone, channel: 'whatsapp' })

                });

                const data = await resp.json();

                if (data.status === 'success') {

                    currentWaTarget = data.identifier || phone;

                    document.getElementById('waTargetDisplay').innerText = '💬 Code sent to: ' + currentWaTarget;

                    document.getElementById('waStepRequest').style.display = 'none';

                    document.getElementById('waStepVerify').style.display = 'block';



                    if (data.whatsapp_link) {

                        const linkBtn = document.getElementById('waWebActionLink');

                        linkBtn.href = data.whatsapp_link;

                        linkBtn.style.display = 'inline-block';

                    }



                    showAlert('✅ ६-अंकी OTP पाठवण्यात आला आहे. WhatsApp चेक करा!', 'success');

                    document.getElementById('waOtpCode').focus();

                } else {

                    showAlert(data.error || 'Failed to send WhatsApp OTP.', 'error');

                }

            } catch(e) {

                showAlert('OTP Dispatch Error: ' + e.message, 'error');

            } finally {

                btn.disabled = false;

                btn.innerText = '📲 Send WhatsApp OTP';

            }

        }



        function resetWaStep() {

            document.getElementById('waStepRequest').style.display = 'block';

            document.getElementById('waStepVerify').style.display = 'none';

            document.getElementById('waOtpCode').value = '';

            hideAlert();

        }



        async function handleVerifyWaOtp() {

            const otpCode = document.getElementById('waOtpCode').value.trim();

            if (!otpCode || otpCode.length < 6) {

                showAlert('कृपया ६-अंकी OTP प्रविष्ट करा.', 'warning');

                return;

            }

            const btn = document.getElementById('waVerifyBtn');

            btn.disabled = true;

            btn.innerText = 'Verifying WhatsApp OTP...';

            hideAlert();



            try {

                const resp = await fetch('/api/auth/otp/verify', {

                    method: 'POST',

                    headers: { 'Content-Type': 'application/json' },

                    body: JSON.stringify({ identifier: currentWaTarget, otp_code: otpCode, channel: 'whatsapp' })

                });

                const data = await resp.json();

                if (data.status === 'success' && data.session_token) {

                    localStorage.setItem('nanopro_session_token', data.session_token);

                    localStorage.setItem('nanopro_active_account', data.user.username);

                    document.cookie = 'nanopro_session=' + encodeURIComponent(data.session_token) + '; path=/; max-age=2592000; SameSite=Lax';



                    showAlert('✅ WhatsApp OTP Verified! Launching NanoPro...', 'success');

                    setTimeout(() => {

                        window.location.replace('/?token=' + encodeURIComponent(data.session_token));

                    }, 400);

                } else if (data.status === 'pending_approval' || data.status_code === 'PENDING_APPROVAL') {
                    showAlert('⏳ <b>' + (data.message || data.error || 'WhatsApp OTP पडताळला गेला आहे! ॲडमिन मंजुरीनंतर खाते सक्रिय होईल.') + '</b>', 'warning');
                } else {
                    showAlert(data.error || 'अवैध OTP कोड. कृपया पुन्हा प्रयत्न करा.', 'error');

                }

            } catch(e) {

                showAlert('OTP Verification Error: ' + e.message, 'error');

            } finally {

                btn.disabled = false;

                btn.innerText = '🔓 Verify & Launch NanoPro';

            }

        }



        async function handleRegister(e) {

            e.preventDefault();

            const btn = document.getElementById('regBtn');

            btn.disabled = true;

            btn.innerText = 'Submitting Request...';

            hideAlert();



            const full_name = document.getElementById('regFullName').value.trim();

            const username = document.getElementById('regUsername').value.trim();

            const email = document.getElementById('regEmail').value.trim();

            const password = document.getElementById('regPassword').value;



            try {

                const resp = await fetch('/api/auth/register', {

                    method: 'POST',

                    headers: { 'Content-Type': 'application/json' },

                    body: JSON.stringify({ full_name, username, email, password })

                });

                const data = await resp.json();

                if (data.status === 'success') {

                    showAlert('<b>' + data.message + '</b>', 'warning');

                    document.getElementById('registerForm').reset();

                    setTimeout(() => switchMainTab('direct'), 3500);

                } else {

                    showAlert(data.error || 'Registration failed.', 'error');

                }

            } catch(err) {

                showAlert('Submission Error: ' + err.message, 'error');

            } finally {

                btn.disabled = false;

                btn.innerText = '📝 Submit for Admin Approval';

            }

        }

    </script>

</body>

</html>

"""

