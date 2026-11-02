import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

def patch_login_gateway():
    path = os.path.join("deploy", "login_gateway.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate the window.addEventListener('load') block
    old_load_block = """        // Initialize Clerk SDK & Process OAuth Handshakes
        window.addEventListener('load', async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const isGoogleCallback = urlParams.has('clerk_sso') || window.location.hash.includes('clerk') || window.location.href.includes('__clerk_');
            if (isGoogleCallback) {
                showAlert('⚡ Official Google OAuth handshake प्राप्त झाले. पडताळणी सुरू आहे...', 'info');
            }

            if (window.Clerk) {
                try {
                    await window.Clerk.load();

                    // Check 1: User is already signed in
                    if (window.Clerk.user && window.Clerk.session) {
                        await syncClerkSession();
                        return;
                    }

                    // Check 2: Sign-up in progress with missing requirements (intercept email directly, bypass missing fields!)
                    if (window.Clerk.client && window.Clerk.client.signUp) {
                        const su = window.Clerk.client.signUp;
                        const email = su.emailAddress || (su.verifications && su.verifications.externalAccount && su.verifications.externalAccount.emailAddress);
                        if (email) {
                            const name = (su.firstName ? (su.firstName + ' ' + (su.lastName || '')) : '') || 'Google User';
                            await authenticateWithBackendGoogle(email, name);
                            return;
                        }
                    }

                    // Check 3: Sign-in in progress
                    if (window.Clerk.client && window.Clerk.client.signIn && window.Clerk.client.signIn.status === 'complete') {
                        await syncClerkSession();
                        return;
                    }

                    // Check 4: Dynamic listener for authentication state
                    if (window.Clerk.addListener) {
                        window.Clerk.addListener(async (e) => {
                            if (e && (e.user || e.session)) {
                                await syncClerkSession();
                            } else if (e && e.client && e.client.signUp) {
                                const su = e.client.signUp;
                                const email = su.emailAddress || (su.verifications && su.verifications.externalAccount && su.verifications.externalAccount.emailAddress);
                                if (email) {
                                    const name = (su.firstName ? (su.firstName + ' ' + (su.lastName || '')) : '') || 'Google User';
                                    await authenticateWithBackendGoogle(email, name);
                                }
                            }
                        });
                    }
                } catch(e) {
                    console.warn('Clerk initialization note:', e);
                }
            }
        });"""

    new_load_block = """        // Initialize Clerk SDK & Process OAuth Handshakes
        window.addEventListener('load', async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const isLogout = urlParams.has('logout') || sessionStorage.getItem('nanopro_just_logged_out') === '1';

            // 1. IF USER LOGGED OUT: Purge everything, sign out Clerk, and STAY ON LOGIN PAGE (NO AUTO-LOGIN)!
            if (isLogout) {
                sessionStorage.removeItem('nanopro_just_logged_out');
                localStorage.removeItem('nanopro_session_token');
                localStorage.removeItem('nanopro_active_account');
                localStorage.removeItem('nanopro_saved_accounts');
                localStorage.removeItem('nanopro_remember_credentials');
                document.cookie = 'nanopro_session=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
                document.cookie = 'nanopro_session=; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
                showAlert('ℹ️ यशस्वीरीत्या लॉगआउट झाले (Successfully logged out). कृपया लॉगिन करण्यासाठी खालील पर्याय निवडा.', 'info');

                if (window.Clerk) {
                    try {
                        await window.Clerk.load();
                        if (window.Clerk.signOut) {
                            await window.Clerk.signOut();
                        }
                    } catch(ce) {}
                }
                if (window.history && window.history.replaceState) {
                    window.history.replaceState({}, document.title, window.location.pathname);
                }
                return; // STOP! Do not auto-login on logout!
            }

            // 2. ONLY AUTO-COMPLETE IF USER EXPLICITLY CLICKED GOOGLE OAUTH (?clerk_sso=1)
            const isGoogleCallback = urlParams.has('clerk_sso');

            if (isGoogleCallback) {
                showAlert('⚡ Official Google OAuth handshake प्राप्त झाले. पडताळणी सुरू आहे...', 'info');

                if (window.Clerk) {
                    try {
                        await window.Clerk.load();

                        // Check A: User signed in
                        if (window.Clerk.user && window.Clerk.session) {
                            await syncClerkSession();
                            return;
                        }

                        // Check B: Sign-up in progress with missing requirements (intercept email directly, bypass missing fields!)
                        if (window.Clerk.client && window.Clerk.client.signUp) {
                            const su = window.Clerk.client.signUp;
                            const email = su.emailAddress || (su.verifications && su.verifications.externalAccount && su.verifications.externalAccount.emailAddress);
                            if (email) {
                                const name = (su.firstName ? (su.firstName + ' ' + (su.lastName || '')) : '') || 'Google User';
                                await authenticateWithBackendGoogle(email, name);
                                return;
                            }
                        }

                        // Check C: Sign-in complete
                        if (window.Clerk.client && window.Clerk.client.signIn && window.Clerk.client.signIn.status === 'complete') {
                            await syncClerkSession();
                            return;
                        }
                    } catch(e) {
                        console.warn('Clerk OAuth callback error:', e);
                    }
                }
            } else {
                // NORMAL VISIT (NOT A REDIRECT): Load Clerk silently, NEVER auto-login without user click!
                if (window.Clerk) {
                    try {
                        await window.Clerk.load();
                    } catch(e) {}
                }
            }
        });"""

    c_norm = content.replace("\r\n", "\n")
    o_norm = old_load_block.replace("\r\n", "\n")
    n_norm = new_load_block.replace("\r\n", "\n")

    if o_norm in c_norm:
        c_norm = c_norm.replace(o_norm, n_norm, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c_norm)
        print("login_gateway.html patched successfully!")
    else:
        print("ERROR: old_load_block not found in login_gateway.html!")

def patch_complete_dashboard():
    path = os.path.join("deploy", "complete_nanopro_dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update performLogout
    old_logout = """async function performLogout(isAuto=false) {
    try {
        if (currentSessionToken) {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_token: currentSessionToken })
            });
        }
    } catch(e){}
    document.cookie = 'nanopro_session=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
    document.cookie = 'nanopro_session=; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
    localStorage.removeItem('nanopro_session_token');
    localStorage.removeItem('nanopro_saved_accounts');
    localStorage.removeItem('nanopro_remember_credentials');
    localStorage.removeItem('nanopro_active_account');
    sessionStorage.clear();
    currentSessionToken = null;
    currentUser = null;
    window.currentUser = null;
    document.body.classList.remove('auth-verified');
    document.documentElement.classList.remove('auth-verified');
    window.location.replace('/login');
}"""

    new_logout = """async function performLogout(isAuto=false) {
    try {
        if (currentSessionToken) {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_token: currentSessionToken })
            });
        }
    } catch(e){}
    document.cookie = 'nanopro_session=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
    document.cookie = 'nanopro_session=; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
    localStorage.removeItem('nanopro_session_token');
    localStorage.removeItem('nanopro_saved_accounts');
    localStorage.removeItem('nanopro_remember_credentials');
    localStorage.removeItem('nanopro_active_account');
    sessionStorage.clear();
    sessionStorage.setItem('nanopro_just_logged_out', '1');
    try {
        if (window.Clerk && window.Clerk.signOut) {
            await window.Clerk.signOut();
        }
    } catch(ce){}
    currentSessionToken = null;
    currentUser = null;
    window.currentUser = null;
    document.body.classList.remove('auth-verified');
    document.documentElement.classList.remove('auth-verified');
    window.location.replace('/login?logout=1');
}"""

    # 2. Update signOutAllAccounts
    old_signout_all = """function signOutAllAccounts() {

    localStorage.removeItem('nanopro_saved_accounts');

    localStorage.removeItem('nanopro_active_account');

    localStorage.removeItem('nanopro_session_token');

    localStorage.removeItem('nanopro_remember_credentials');

    location.reload();

}"""

    new_signout_all = """async function signOutAllAccounts() {
    localStorage.removeItem('nanopro_saved_accounts');
    localStorage.removeItem('nanopro_active_account');
    localStorage.removeItem('nanopro_session_token');
    localStorage.removeItem('nanopro_remember_credentials');
    document.cookie = 'nanopro_session=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
    document.cookie = 'nanopro_session=; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
    sessionStorage.clear();
    sessionStorage.setItem('nanopro_just_logged_out', '1');
    try {
        if (window.Clerk && window.Clerk.signOut) {
            await window.Clerk.signOut();
        }
    } catch(ce){}
    window.location.replace('/login?logout=1');
}"""

    c_norm = content.replace("\r\n", "\n")
    o_logout_norm = old_logout.replace("\r\n", "\n")
    n_logout_norm = new_logout.replace("\r\n", "\n")

    if o_logout_norm in c_norm:
        c_norm = c_norm.replace(o_logout_norm, n_logout_norm, 1)
        print("performLogout patched in complete_nanopro_dashboard.html!")
    else:
        print("ERROR: old_logout not found in complete_nanopro_dashboard.html!")

    o_so_norm = old_signout_all.replace("\r\n", "\n")
    n_so_norm = new_signout_all.replace("\r\n", "\n")
    if o_so_norm in c_norm:
        c_norm = c_norm.replace(o_so_norm, n_so_norm, 1)
        print("signOutAllAccounts patched in complete_nanopro_dashboard.html!")
    else:
        print("ERROR: old_signout_all not found in complete_nanopro_dashboard.html!")

    with open(path, "w", encoding="utf-8") as f:
        f.write(c_norm)

def patch_alwaysdata_wsgi():
    path = os.path.join("deploy", "alwaysdata_wsgi.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace /login redirect in /logout handlers to include ?logout=1
    content_new = content.replace("Location', '/login')", "Location', '/login?logout=1')")
    content_new = content_new.replace('Location\', "/login")', 'Location\', "/login?logout=1")')
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_new)
    print("alwaysdata_wsgi.py /logout redirects patched!")

def patch_main_py():
    path = "main.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content_new = content.replace('RedirectResponse(url="/login")', 'RedirectResponse(url="/login?logout=1")')
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_new)
    print("main.py /logout redirect patched!")

patch_login_gateway()
patch_complete_dashboard()
patch_alwaysdata_wsgi()
patch_main_py()
print("All patches completed!")
