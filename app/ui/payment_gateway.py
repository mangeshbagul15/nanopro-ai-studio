"""

NanoPro Payment Gateway — functional Razorpay checkout view (HTML + client JS).

"""


def get_payment_gateway_html() -> str:
    return r'''
<div class="workspace-view" id="view-payment_gateway">
<style>
#view-payment_gateway .pgr-wrap { display:flex; flex-direction:column; gap:14px; }
#view-payment_gateway .pgr-hero { display:flex; justify-content:space-between; align-items:center; gap:14px; flex-wrap:wrap; background:linear-gradient(135deg, rgba(15,23,42,.97), rgba(30,27,75,.9)); border:1px solid #334155; border-radius:14px; padding:18px; }
#view-payment_gateway .pgr-hero h2 { margin:0; font-size:18px; color:#F8FAFC; display:flex; align-items:center; gap:9px; }
#view-payment_gateway .pgr-hero p { margin:4px 0 0; font-size:12px; color:#94A3B8; }
#view-payment_gateway .pgr-badge { font-size:10.5px; font-weight:800; letter-spacing:.4px; padding:4px 9px; border-radius:999px; border:1px solid #334155; color:#94A3B8; background:#0B1120; }
#view-payment_gateway .pgr-badge.live { color:#34D399; border-color:#065F46; background:rgba(6,95,70,.25); }
#view-payment_gateway .pgr-badge.test { color:#FBBF24; border-color:#92400E; background:rgba(146,64,14,.22); }
#view-payment_gateway .pgr-badge.off { color:#F87171; border-color:#7F1D1D; background:rgba(127,29,29,.22); }
#view-payment_gateway .pgr-grid { display:grid; grid-template-columns:minmax(0,1.15fr) minmax(310px,.85fr); gap:14px; align-items:start; }
@media (max-width: 980px) { #view-payment_gateway .pgr-grid { grid-template-columns:1fr; } }
#view-payment_gateway .pgr-card { background:#0F172A; border:1px solid #334155; border-radius:14px; padding:18px; }
#view-payment_gateway .pgr-card h3 { margin:0 0 4px; font-size:15px; color:#F8FAFC; }
#view-payment_gateway .pgr-muted { font-size:12px; color:#94A3B8; line-height:1.55; }
#view-payment_gateway .pgr-row { margin-top:14px; }
#view-payment_gateway .pgr-label { display:block; font-size:10.5px; font-weight:800; letter-spacing:.6px; text-transform:uppercase; color:#94A3B8; margin-bottom:6px; }
#view-payment_gateway .pgr-input-wrap { display:flex; align-items:center; gap:8px; background:#0B1120; border:1px solid #334155; border-radius:10px; padding:0 12px; transition:border-color .15s; }
#view-payment_gateway .pgr-input-wrap:focus-within { border-color:#38BDF8; box-shadow:0 0 0 3px rgba(56,189,248,.12); }
#view-payment_gateway .pgr-input-wrap input { flex:1; background:transparent; border:0; outline:0; color:#F8FAFC; font-size:14px; padding:12px 0; min-width:0; }
#view-payment_gateway .pgr-input-wrap input::placeholder { color:#64748B; }
#view-payment_gateway .pgr-input-wrap.invalid { border-color:#EF4444; }
#view-payment_gateway .pgr-prefix { color:#CBD5E1; font-size:13.5px; font-weight:700; padding-right:8px; border-right:1px solid #334155; }
#view-payment_gateway .pgr-change { background:none; border:0; color:#38BDF8; font-size:11.5px; font-weight:800; cursor:pointer; padding:4px 6px; }
#view-payment_gateway .pgr-error { display:none; font-size:11px; color:#F87171; margin-top:5px; }
#view-payment_gateway .pgr-pay-btn { width:100%; margin-top:18px; padding:14px 16px; border:0; border-radius:11px; background:linear-gradient(135deg,#0EA5E9,#2563EB); color:#FFF; font-size:15px; font-weight:800; cursor:pointer; box-shadow:0 8px 22px rgba(37,99,235,.35); transition:transform .12s, box-shadow .12s, opacity .12s; }
#view-payment_gateway .pgr-pay-btn:hover { transform:translateY(-1px); box-shadow:0 10px 26px rgba(37,99,235,.45); }
#view-payment_gateway .pgr-pay-btn:active { transform:translateY(0); }
#view-payment_gateway .pgr-pay-btn:disabled { opacity:.55; cursor:not-allowed; transform:none; box-shadow:none; }
#view-payment_gateway .pgr-spin { display:inline-block; width:14px; height:14px; border:2px solid rgba(255,255,255,.35); border-top-color:#FFF; border-radius:50%; animation:pgrspin .7s linear infinite; vertical-align:-2px; margin-right:8px; }
@keyframes pgrspin { to { transform:rotate(360deg); } }
#view-payment_gateway .pgr-secure { display:flex; align-items:center; justify-content:center; gap:7px; margin-top:12px; font-size:11px; color:#94A3B8; }
#view-payment_gateway .pgr-flash { display:none; margin-top:12px; padding:10px 12px; border-radius:9px; font-size:12px; line-height:1.5; }
#view-payment_gateway .pgr-flash.err { display:block; background:rgba(127,29,29,.25); border:1px solid #7F1D1D; color:#FCA5A5; }
#view-payment_gateway .pgr-flash.ok { display:block; background:rgba(6,95,70,.25); border:1px solid #065F46; color:#6EE7B7; }
#view-payment_gateway .pgr-flash.info { display:block; background:rgba(30,58,138,.25); border:1px solid #1E40AF; color:#93C5FD; }
#view-payment_gateway .pgr-plan-total { font-size:30px; font-weight:900; color:#F8FAFC; letter-spacing:-.5px; }
#view-payment_gateway .pgr-plan-total small { font-size:12px; font-weight:600; color:#94A3B8; letter-spacing:0; }
#view-payment_gateway .pgr-feature { display:flex; gap:8px; align-items:flex-start; font-size:12px; color:#CBD5E1; margin-top:8px; line-height:1.45; }
#view-payment_gateway .pgr-feature b { color:#38BDF8; font-size:13px; line-height:1.2; }
#view-payment_gateway .pgr-breakdown { border-top:1px dashed #334155; margin-top:14px; padding-top:12px; }
#view-payment_gateway .pgr-line { display:flex; justify-content:space-between; gap:10px; font-size:12.5px; color:#CBD5E1; padding:5px 0; }
#view-payment_gateway .pgr-line.total { border-top:1px solid #334155; margin-top:6px; padding-top:10px; color:#F8FAFC; font-weight:800; font-size:14px; }
#view-payment_gateway .pgr-setup { display:none; border:1px solid #92400E; background:rgba(146,64,14,.14); border-radius:12px; padding:14px; font-size:12px; color:#FCD34D; line-height:1.55; }
#view-payment_gateway .pgr-admin { display:none; }
#view-payment_gateway .pgr-admin-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
@media (max-width: 720px) { #view-payment_gateway .pgr-admin-grid { grid-template-columns:1fr; } }
#view-payment_gateway .pgr-table { width:100%; border-collapse:collapse; margin-top:10px; }
#view-payment_gateway .pgr-table th, #view-payment_gateway .pgr-table td { text-align:left; font-size:11.5px; padding:8px 8px; border-bottom:1px solid #1E293B; color:#CBD5E1; }
#view-payment_gateway .pgr-table th { color:#94A3B8; text-transform:uppercase; letter-spacing:.4px; font-size:10px; }
#view-payment_gateway .pgr-success { display:none; border:1px solid #065F46; background:linear-gradient(135deg, rgba(6,78,59,.55), rgba(15,23,42,.95)); border-radius:14px; padding:18px; }
#view-payment_gateway .pgr-success h3 { color:#6EE7B7; }
#view-payment_gateway .pgr-kv { display:flex; justify-content:space-between; gap:12px; font-size:12px; color:#CBD5E1; padding:5px 0; border-bottom:1px dashed rgba(51,65,85,.7); }
#view-payment_gateway .pgr-kv b { color:#F8FAFC; }
</style>

<div class="pgr-wrap">
    <div class="pgr-hero">
        <div>
            <h2>&#128274; Payment Gateway <span class="pgr-badge" id="pgrGatewayBadge">LOADING</span></h2>
            <p>Secure checkout powered by Razorpay &bull; UPI, cards and net banking &bull; GST invoice ready</p>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <button type="button" class="btn btn-secondary" onclick="pgrRefresh()" style="font-size:11px; padding:7px 12px;">&#8635; Refresh Status</button>
            <button type="button" class="btn btn-secondary" id="pgrAdminToggle" onclick="pgrToggleAdmin()" style="font-size:11px; padding:7px 12px; display:none;">&#128273; Connect Razorpay</button>
        </div>
    </div>

    <div class="pgr-setup" id="pgrSetupBanner"></div>

    <div class="pgr-grid">
        <div class="pgr-card">
            <h3>Almost done</h3>
            <p class="pgr-muted">Add your name and mobile number. Then pay by UPI, card or net banking.</p>

            <div class="pgr-row">
                <label class="pgr-label" for="pgrEmail">Login details will come to</label>
                <div class="pgr-input-wrap" id="pgrEmailWrap">
                    <input type="email" id="pgrEmail" placeholder="you@example.com" autocomplete="email" readonly />
                    <button type="button" class="pgr-change" onclick="pgrEnableEmail()">Change</button>
                </div>
                <div class="pgr-error" id="pgrEmailErr">Enter a valid email address.</div>
            </div>

            <div class="pgr-row">
                <label class="pgr-label" for="pgrName">Your name</label>
                <div class="pgr-input-wrap" id="pgrNameWrap">
                    <input type="text" id="pgrName" placeholder="Name for your invoice" autocomplete="name" maxlength="80" />
                </div>
                <div class="pgr-error" id="pgrNameErr">Enter your full name (at least 2 characters).</div>
            </div>

            <div class="pgr-row">
                <label class="pgr-label" for="pgrMobile">Mobile number</label>
                <div class="pgr-input-wrap" id="pgrMobileWrap">
                    <span class="pgr-prefix">&#127470;&#127475; +91</span>
                    <input type="tel" id="pgrMobile" placeholder="10-digit mobile number" inputmode="numeric" autocomplete="tel-national" maxlength="10" oninput="this.value=this.value.replace(/\D/g,'').slice(0,10)" />
                </div>
                <div class="pgr-error" id="pgrMobileErr">Enter a valid 10-digit Indian mobile number.</div>
            </div>

            <button type="button" class="pgr-pay-btn" id="pgrPayBtn" onclick="pgrPay()">Pay &#8377;352.82</button>
            <div class="pgr-secure">&#128274; Secure payment &bull; <b style="color:#CBD5E1;">Razorpay</b> &bull; Plan starts right after payment</div>
            <div class="pgr-flash" id="pgrFormMsg"></div>
        </div>

        <div class="pgr-card" style="border-color:#1E40AF;">
            <div class="pgr-muted" style="font-size:10.5px; font-weight:800; letter-spacing:.7px; text-transform:uppercase; color:#38BDF8;">You are buying</div>
            <h3 id="pgrPlanName" style="margin-top:6px; font-size:17px;">Ai Awaaz Starter</h3>
            <p class="pgr-muted" id="pgrPlanTagline" style="margin:0;">Pay once. Lifetime access.</p>
            <div style="display:flex; align-items:flex-end; gap:8px; margin-top:14px;">
                <div class="pgr-plan-total" id="pgrPlanTotal">&#8377;352.82</div>
                <small class="pgr-muted" style="margin-bottom:5px;">incl. GST</small>
            </div>
            <div id="pgrPlanFeatures" style="margin-top:10px;"></div>

            <div class="pgr-breakdown">
                <div class="pgr-line"><span>Plan price</span><b id="pgrBasePrice">&#8377;299.00</b></div>
                <div class="pgr-line"><span>GST (<span id="pgrGstRate">18</span>%)</span><b id="pgrGstPrice">&#8377;53.82</b></div>
                <div class="pgr-line total"><span>You pay</span><b id="pgrTotalPrice">&#8377;352.82</b></div>
            </div>
            <p class="pgr-muted" id="pgrPlanNote" style="margin-top:12px; font-size:11px;">1 minute of audio uses about 830 characters. Your limit refills every month, and unused limit does not carry over.</p>
        </div>
    </div>

    <div class="pgr-card pgr-success" id="pgrSuccessCard">
        <h3>&#10003; Payment successful</h3>
        <p class="pgr-muted" id="pgrSuccessMsg">Your plan is active now.</p>
        <div style="margin-top:10px;">
            <div class="pgr-kv"><span>Payment ID</span><b id="pgrSuccessPaymentId">-</b></div>
            <div class="pgr-kv"><span>Order ID</span><b id="pgrSuccessOrderId">-</b></div>
            <div class="pgr-kv"><span>Amount paid</span><b id="pgrSuccessAmount">-</b></div>
            <div class="pgr-kv"><span>Plan</span><b id="pgrSuccessPlan">-</b></div>
            <div class="pgr-kv" style="border-bottom:0;"><span>Monthly quota</span><b id="pgrSuccessQuota">-</b></div>
        </div>
        <button type="button" class="btn btn-secondary" onclick="pgrResetForm()" style="margin-top:12px; font-size:11px; padding:7px 12px;">Buy another plan</button>
    </div>

    <div class="pgr-card pgr-admin" id="pgrAdminPanel">
        <h3>&#128273; Connect Razorpay (Admin)</h3>
        <p class="pgr-muted" style="margin-top:4px;">Keys are stored encrypted in the server vault. For permanent storage across redeploys, also set <b>RAZORPAY_KEY_ID</b> and <b>RAZORPAY_KEY_SECRET</b> in Render &rarr; Environment.</p>
        <div class="pgr-admin-grid" style="margin-top:12px;">
            <div>
                <label class="pgr-label">Key ID</label>
                <div class="pgr-input-wrap"><input type="text" id="pgrKeyId" placeholder="rzp_test_... or rzp_live_..." autocomplete="off" /></div>
            </div>
            <div>
                <label class="pgr-label">Key Secret</label>
                <div class="pgr-input-wrap"><input type="password" id="pgrKeySecret" placeholder="Razorpay key secret" autocomplete="new-password" /></div>
            </div>
        </div>
        <button type="button" class="btn btn-primary" id="pgrSaveKeysBtn" onclick="pgrSaveKeys()" style="margin-top:12px; font-size:12px; padding:9px 14px;">Save &amp; Verify Connection</button>
        <div class="pgr-flash" id="pgrAdminMsg"></div>
    </div>

    <div class="pgr-card pgr-admin" id="pgrHistoryPanel">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
            <h3>&#128203; Recent payments</h3>
            <button type="button" class="btn btn-secondary" onclick="pgrLoadHistory()" style="font-size:10.5px; padding:5px 10px;">Refresh</button>
        </div>
        <div id="pgrHistoryBody" class="pgr-muted" style="margin-top:8px;">Loading…</div>
    </div>
</div>
</div>
'''


def get_payment_gateway_js() -> str:
    return r'''
<script>
window.pgrState = window.pgrState || { config: null, plan: null, order: null, initialised: false, busy: false };

function pgrEl(id) { return document.getElementById(id); }

function pgrShow(el, show) { if (el) el.style.display = show ? 'block' : 'none'; }

function pgrMsg(text, kind) {
    const el = pgrEl('pgrFormMsg');
    if (!el) return;
    el.className = 'pgr-flash' + (kind ? ' ' + kind : '');
    el.innerHTML = text || '';
}

function pgrAdminMsg(text, kind) {
    const el = pgrEl('pgrAdminMsg');
    if (!el) return;
    el.className = 'pgr-flash' + (kind ? ' ' + kind : '');
    el.innerHTML = text || '';
}

function pgrIsAdmin() {
    const u = window.currentUser || null;
    return !!u && (u.role === 'admin' || u.username === 'nanopro');
}

function pgrSessionToken() {
    try { return localStorage.getItem('nanopro_session_token') || ''; } catch (e) { return ''; }
}

async function pgrApi(url, options) {
    const opts = Object.assign({ headers: {} }, options || {});
    opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    const token = pgrSessionToken();
    if (token) opts.headers['X-Session-Token'] = token;
    const response = await fetch(url, opts);
    let data = {};
    try { data = await response.json(); } catch (e) { data = { status: 'error', message: 'Invalid server response.' }; }
    data._http = response.status;
    return data;
}

function pgrMoney(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function pgrEscape(text) {
    return String(text == null ? '' : text).replace(/[&<>"']/g, function (ch) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
}

function pgrDateFormat(ts) {
    if (!ts) return '-';
    try { return new Date(Number(ts) * 1000).toLocaleString('en-IN'); } catch (e) { return '-'; }
}

function pgrPrefillUser() {
    const u = window.currentUser || null;
    if (!u) return;
    const email = pgrEl('pgrEmail');
    if (email && !email.value) email.value = u.email || '';
    const name = pgrEl('pgrName');
    if (name && !name.value) name.value = u.full_name || u.name || '';
}

function pgrEnableEmail() {
    const email = pgrEl('pgrEmail');
    if (!email) return;
    email.readOnly = false;
    email.focus();
    email.select();
}

function pgrRenderPlan(plan) {
    if (!plan) return;
    window.pgrState.plan = plan;
    if (pgrEl('pgrPlanName')) pgrEl('pgrPlanName').textContent = plan.name;
    if (pgrEl('pgrPlanTagline')) pgrEl('pgrPlanTagline').textContent = plan.tagline;
    if (pgrEl('pgrPlanTotal')) pgrEl('pgrPlanTotal').textContent = plan.total_display;
    if (pgrEl('pgrBasePrice')) pgrEl('pgrBasePrice').textContent = plan.base_price_display;
    if (pgrEl('pgrGstPrice')) pgrEl('pgrGstPrice').textContent = plan.gst_display;
    if (pgrEl('pgrTotalPrice')) pgrEl('pgrTotalPrice').textContent = plan.total_display;
    if (pgrEl('pgrGstRate')) pgrEl('pgrGstRate').textContent = String(Math.round(plan.gst_rate * 100));
    if (pgrEl('pgrPlanNote')) {
        pgrEl('pgrPlanNote').textContent = '1 minute of audio uses about ' + plan.chars_per_minute +
            ' characters. Your limit refills every month, and unused limit does not carry over.';
    }
    const payBtn = pgrEl('pgrPayBtn');
    if (payBtn && !window.pgrState.busy) payBtn.innerHTML = 'Pay ' + plan.total_display;
    const featureBox = pgrEl('pgrPlanFeatures');
    if (featureBox) {
        featureBox.innerHTML = (plan.features || []).map(function (f) {
            return '<div class="pgr-feature"><b>&#10003;</b><span>' + pgrEscape(f) + '</span></div>';
        }).join('');
    }
}

function pgrRenderConfig(cfg) {
    window.pgrState.config = cfg;
    const badge = pgrEl('pgrGatewayBadge');
    const banner = pgrEl('pgrSetupBanner');
    const adminToggle = pgrEl('pgrAdminToggle');
    const payBtn = pgrEl('pgrPayBtn');
    const plan = (cfg.plans && cfg.plans[0]) || window.pgrState.plan;
    if (plan) pgrRenderPlan(plan);

    if (badge) {
        badge.className = 'pgr-badge ' + (cfg.configured ? (cfg.mode === 'live' ? 'live' : 'test') : 'off');
        badge.textContent = cfg.configured ? (cfg.mode === 'live' ? 'LIVE' : 'TEST MODE') : 'NOT CONNECTED';
    }
    if (payBtn) payBtn.disabled = !cfg.configured || window.pgrState.busy;
    if (adminToggle) adminToggle.style.display = pgrIsAdmin() ? 'inline-block' : 'none';

    if (banner) {
        if (cfg.configured) {
            pgrShow(banner, false);
        } else {
            banner.innerHTML = '&#9888; Razorpay is not connected. ' +
                (pgrIsAdmin()
                    ? 'Use <b>Connect Razorpay</b> above to paste your Key ID and Key Secret, or set the env vars on the server.'
                    : 'Ask the studio admin to connect the gateway.') +
                ' Until then the Pay button stays locked.';
            pgrShow(banner, true);
        }
    }
    if (cfg.configured) {
        pgrShow(pgrEl('pgrAdminPanel'), false);
        pgrShow(pgrEl('pgrHistoryPanel'), false);
    }
}

async function pgrRefresh() {
    try {
        const cfg = await pgrApi('/api/payments/config', { method: 'GET' });
        if (cfg.status === 'success') pgrRenderConfig(cfg);
        else pgrMsg(cfg.message || 'Could not load payment configuration.', 'err');
    } catch (e) {
        pgrMsg('Network error while loading payment configuration.', 'err');
    }
}

async function initPaymentGateway() {
    pgrPrefillUser();
    if (!pgrIsAdmin()) {
        pgrShow(pgrEl('pgrAdminToggle'), false);
        pgrShow(pgrEl('pgrAdminPanel'), false);
        pgrShow(pgrEl('pgrHistoryPanel'), false);
    } else {
        pgrShow(pgrEl('pgrAdminToggle'), true);
    }
    await pgrRefresh();
    window.pgrState.initialised = true;
}

function pgrToggleAdmin() {
    if (!pgrIsAdmin()) return;
    const panel = pgrEl('pgrAdminPanel');
    const history = pgrEl('pgrHistoryPanel');
    const open = panel && panel.style.display !== 'block';
    pgrShow(panel, open);
    pgrShow(history, open);
    if (open) {
        pgrPrefillUser();
        pgrLoadHistory();
    }
}

function pgrFieldError(field, show) {
    const wrap = pgrEl('pgr' + field + 'Wrap');
    const err = pgrEl('pgr' + field + 'Err');
    if (wrap) wrap.classList.toggle('invalid', !!show);
    if (err) err.style.display = show ? 'block' : 'none';
}

function pgrValidateForm() {
    const name = (pgrEl('pgrName').value || '').trim();
    const email = (pgrEl('pgrEmail').value || '').trim();
    const mobile = (pgrEl('pgrMobile').value || '').replace(/\D/g, '');
    let ok = true;
    const nameOk = name.length >= 2;
    const emailOk = /^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$/.test(email);
    const mobileOk = /^[6-9]\d{9}$/.test(mobile);
    pgrFieldError('Name', !nameOk);
    pgrFieldError('Email', !emailOk);
    pgrFieldError('Mobile', !mobileOk);
    if (!nameOk || !emailOk || !mobileOk) {
        ok = false;
        pgrMsg('Please fix the highlighted fields before paying.', 'err');
        const firstBad = !nameOk ? pgrEl('pgrName') : (!emailOk ? pgrEl('pgrEmail') : pgrEl('pgrMobile'));
        if (firstBad) firstBad.focus();
    }
    return ok ? { name: name, email: email, mobile: mobile } : null;
}

function pgrLoadRazorpay() {
    return new Promise(function (resolve, reject) {
        if (window.Razorpay) return resolve(true);
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        script.onload = function () { resolve(!!window.Razorpay); };
        script.onerror = function () { reject(new Error('Could not load Razorpay Checkout.')); };
        document.head.appendChild(script);
    });
}

function pgrSetBusy(busy, label) {
    window.pgrState.busy = busy;
    const btn = pgrEl('pgrPayBtn');
    if (!btn) return;
    btn.disabled = busy;
    if (busy) {
        btn.innerHTML = '<span class="pgr-spin"></span>' + (label || 'Opening secure checkout…');
    } else {
        const plan = window.pgrState.plan;
        btn.innerHTML = 'Pay ' + (plan ? plan.total_display : '');
        const cfg = window.pgrState.config;
        btn.disabled = !cfg || !cfg.configured;
    }
}

async function pgrPay() {
    if (window.pgrState.busy) return;
    const cfg = window.pgrState.config;
    if (!cfg || !cfg.configured) {
        pgrMsg('Razorpay is not connected yet. ' + (pgrIsAdmin() ? 'Open “Connect Razorpay” and paste your keys.' : 'Please contact the studio admin.'), 'err');
        if (pgrIsAdmin()) pgrToggleAdmin();
        return;
    }
    const customer = pgrValidateForm();
    if (!customer) return;
    pgrMsg('');
    pgrSetBusy(true, 'Creating secure order…');
    try {
        const data = await pgrApi('/api/payments/razorpay/order', {
            method: 'POST',
            body: JSON.stringify({
                plan_id: (window.pgrState.plan && window.pgrState.plan.id) || 'ai_awaaz_starter',
                name: customer.name,
                email: customer.email,
                mobile: customer.mobile
            })
        });
        if (data.status !== 'success') {
            pgrSetBusy(false);
            if (data.code === 'gateway_not_configured') {
                await pgrRefresh();
                if (pgrIsAdmin()) pgrToggleAdmin();
            }
            pgrMsg(pgrEscape(data.message || 'Could not create the payment order.'), 'err');
            return;
        }
        window.pgrState.order = data;
        pgrSetBusy(true, 'Opening secure checkout…');
        await pgrLoadRazorpay();
        pgrOpenCheckout(data);
    } catch (e) {
        pgrSetBusy(false);
        pgrMsg(pgrEscape(e.message || 'Payment could not start.'), 'err');
    }
}

function pgrOpenCheckout(order) {
    const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: order.checkout.name,
        description: order.checkout.description,
        order_id: order.order_id,
        prefill: order.checkout.prefill,
        notes: order.checkout.notes,
        theme: { color: '#38BDF8' },
        modal: {
            ondismiss: function () {
                pgrSetBusy(false);
                pgrMsg('Payment cancelled. Your order is saved and you can retry anytime.', 'info');
            }
        },
        handler: function (response) {
            pgrVerifyPayment(response);
        }
    };
    const rzp = new window.Razorpay(options);
    rzp.on('payment.failed', function (response) {
        pgrSetBusy(false);
        const desc = (response && response.error && response.error.description) || 'Payment failed at the gateway.';
        pgrMsg(pgrEscape(desc), 'err');
    });
    rzp.open();
    pgrSetBusy(false);
    pgrMsg('Complete the payment in the Razorpay window. This page will update automatically.', 'info');
}

async function pgrVerifyPayment(response) {
    pgrSetBusy(true, 'Verifying payment…');
    pgrMsg('Verifying your payment with Razorpay…', 'info');
    try {
        const data = await pgrApi('/api/payments/razorpay/verify', {
            method: 'POST',
            body: JSON.stringify({
                order_id: response.razorpay_order_id,
                payment_id: response.razorpay_payment_id,
                signature: response.razorpay_signature
            })
        });
        pgrSetBusy(false);
        if (data.status === 'success') {
            pgrShowSuccess(data);
            pgrLoadHistory();
        } else {
            pgrMsg(pgrEscape(data.message || 'Payment verification failed.'), 'err');
        }
    } catch (e) {
        pgrSetBusy(false);
        pgrMsg('Payment may have succeeded but verification could not complete. Refresh the page or check Recent payments.', 'err');
    }
}

function pgrShowSuccess(data) {
    pgrShow(pgrEl('pgrSuccessCard'), true);
    pgrEl('pgrSuccessPaymentId').textContent = data.payment_id || '-';
    pgrEl('pgrSuccessOrderId').textContent = data.order_id || '-';
    pgrEl('pgrSuccessAmount').textContent = data.amount_display || '-';
    const plan = data.plan || window.pgrState.plan || {};
    pgrEl('pgrSuccessPlan').textContent = plan.name || '-';
    pgrEl('pgrSuccessQuota').textContent = plan.monthly_characters
        ? (Number(plan.monthly_characters).toLocaleString('en-IN') + ' characters / month')
        : '-';
    pgrEl('pgrSuccessMsg').textContent = data.already_verified
        ? 'This payment was already verified. Your plan is active.'
        : 'Payment captured and verified. Your plan is active from now.';
    pgrMsg('');
    pgrEl('pgrSuccessCard').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function pgrResetForm() {
    pgrShow(pgrEl('pgrSuccessCard'), false);
    pgrEl('pgrMobile').value = '';
    pgrEl('pgrMobile').focus();
    pgrMsg('');
}

async function pgrSaveKeys() {
    const keyId = (pgrEl('pgrKeyId').value || '').trim();
    const keySecret = (pgrEl('pgrKeySecret').value || '').trim();
    if (!/^rzp_(test|live)_[A-Za-z0-9]{6,}$/.test(keyId)) {
        pgrAdminMsg('Key ID must start with rzp_test_ or rzp_live_.', 'err');
        return;
    }
    if (keySecret.length < 12) {
        pgrAdminMsg('Paste the full Razorpay Key Secret.', 'err');
        return;
    }
    const btn = pgrEl('pgrSaveKeysBtn');
    btn.disabled = true;
    btn.textContent = 'Verifying…';
    try {
        const data = await pgrApi('/api/payments/config/save', {
            method: 'POST',
            body: JSON.stringify({ key_id: keyId, key_secret: keySecret })
        });
        if (data.status === 'success') {
            pgrAdminMsg('Razorpay connected in ' + (data.mode || '').toUpperCase() + ' mode. You can accept payments now.', 'ok');
            pgrEl('pgrKeySecret').value = '';
            pgrRenderConfig(data);
        } else {
            pgrAdminMsg(pgrEscape(data.message || 'Could not save keys.'), 'err');
        }
    } catch (e) {
        pgrAdminMsg('Network error while saving keys.', 'err');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Save & Verify Connection';
    }
}

async function pgrLoadHistory() {
    if (!pgrIsAdmin()) return;
    const body = pgrEl('pgrHistoryBody');
    if (!body) return;
    body.textContent = 'Loading…';
    try {
        const data = await pgrApi('/api/payments/history?limit=8', { method: 'GET' });
        if (data.status !== 'success') {
            body.textContent = data.message || 'Could not load payments.';
            return;
        }
        if (!data.payments || !data.payments.length) {
            body.textContent = 'No payments yet. The first completed checkout will appear here.';
            return;
        }
        let html = '<table class="pgr-table"><thead><tr><th>Date</th><th>Customer</th><th>Amount</th><th>Status</th><th>Order</th></tr></thead><tbody>';
        data.payments.forEach(function (p) {
            const statusClass = p.status === 'paid' ? 'color:#34D399;' : 'color:#FBBF24;';
            html += '<tr><td>' + pgrEscape(pgrDateFormat(p.created_at)) + '</td><td>' +
                pgrEscape(p.customer_name || '-') + '<br><span style="font-size:10px;color:#64748B;">' +
                pgrEscape(p.customer_email || '') + '</span></td><td>' + pgrEscape(p.amount_display) +
                '</td><td style="' + statusClass + 'font-weight:700;">' + pgrEscape(p.status.toUpperCase()) +
                '</td><td style="font-family:monospace;font-size:10px;">' + pgrEscape(p.order_id) + '</td></tr>';
        });
        html += '</tbody></table>';
        body.innerHTML = html;
    } catch (e) {
        body.textContent = 'Network error while loading payments.';
    }
}

window.initPaymentGateway = initPaymentGateway;
window.pgrRefresh = pgrRefresh;
window.pgrPay = pgrPay;
window.pgrToggleAdmin = pgrToggleAdmin;
window.pgrSaveKeys = pgrSaveKeys;
window.pgrLoadHistory = pgrLoadHistory;
window.pgrEnableEmail = pgrEnableEmail;
window.pgrResetForm = pgrResetForm;
</script>
'''
