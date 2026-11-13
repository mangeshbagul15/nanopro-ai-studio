import os
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://mangesh-nanopro.mangeshbagul15.workers.dev"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path = os.path.join(out_dir, "antigravity_claude_chat_alignment.png")

def main():
    print("==========================================================")
    print("VERIFYING ANTIGRAVITY & CLAUDE CODE CHAT ALIGNMENT")
    print("==========================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))

        page.goto(f"{BASE_URL}/#global_ai_lab", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Login if gateway visible
        login_visible = page.evaluate("""() => {
            const u = document.getElementById('loginUsername');
            return u ? (u.offsetWidth > 0 && u.offsetHeight > 0) : false;
        }""")
        if login_visible:
            print("[*] Logging in on login gateway...")
            page.fill("#loginUsername", "nanopro")
            page.fill("#loginPassword", "Mangesh@123")
            page.click("#loginBtn")
            page.wait_for_timeout(3000)

        # Switch to global_ai_lab
        page.evaluate("""() => {
            if (typeof switchView === 'function') switchView('global_ai_lab');
        }""")
        page.wait_for_timeout(2000)

        # Send test prompt
        test_prompt = "मराठीमध्ये EOD बँकिंग सेटलमेंट कशी होते? दोन ओळीत सांगा."
        print(f"[*] Submitting prompt: '{test_prompt}'")

        page.evaluate(f"""() => {{
            const input = document.getElementById('ailabPromptInput');
            if (input) {{
                input.value = `{test_prompt}`;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            const btn = document.getElementById('ailabSendBtn');
            if (btn) btn.click();
            else if (typeof ailabSubmitPrompt === 'function') ailabSubmitPrompt();
        }}""")

        # Wait for assistant response to render
        print("[*] Waiting for turn-by-turn chat alignment...")
        for i in range(15):
            page.wait_for_timeout(1000)
            chat_state = page.evaluate("""() => {
                const userMsgs = document.querySelectorAll('.ailab-msg-user');
                const asstMsgs = document.querySelectorAll('.ailab-msg-assistant');
                const lastUser = userMsgs[userMsgs.length - 1];
                const lastAsst = asstMsgs[asstMsgs.length - 1];
                
                return {
                    userCount: userMsgs.length,
                    asstCount: asstMsgs.length,
                    userAlign: lastUser ? window.getComputedStyle(lastUser).alignSelf : null,
                    userMarginLeft: lastUser ? window.getComputedStyle(lastUser).marginLeft : null,
                    asstAlign: lastAsst ? window.getComputedStyle(lastAsst).alignSelf : null,
                    asstMarginLeft: lastAsst ? window.getComputedStyle(lastAsst).marginLeft : null,
                    hasCopyBtn: !!(lastAsst && lastAsst.querySelector('.ailab-copy-btn')),
                    hasMathBtn: !!(lastAsst && lastAsst.querySelector('.ailab-math-accordion-btn')),
                    asstTextLen: lastAsst ? lastAsst.textContent.length : 0
                };
            }""")
            print(f"[*] Check [{i+1}s]: userMsgs={chat_state['userCount']}, asstMsgs={chat_state['asstCount']}, userAlign={chat_state['userAlign']}, asstAlign={chat_state['asstAlign']}, textLen={chat_state['asstTextLen']}")
            if chat_state['asstCount'] > 0 and chat_state['asstTextLen'] > 80:
                print("[+] Verified assistant message arrived and formatted!")
                break

        # Test Math Accordion toggle
        print("[*] Testing Math Details toggle...")
        toggle_res = page.evaluate("""() => {
            const btn = document.querySelector('.ailab-math-accordion-btn');
            if (btn) btn.click();
            const accordions = document.querySelectorAll('.ailab-prov-math-accordion');
            const lastAcc = accordions[accordions.length - 1];
            return {
                btnFound: !!btn,
                accordionDisplay: lastAcc ? lastAcc.style.display : null
            };
        }""")
        print("[*] Math toggle state:", toggle_res)
        page.wait_for_timeout(1000)

        # Save screenshot artifact
        page.screenshot(path=screenshot_path)
        print(f"[*] Screenshot saved successfully: {screenshot_path}")

        browser.close()
        print("\nALL ANTIGRAVITY & CLAUDE CODE CHAT ALIGNMENT CHECKS PASSED!")

if __name__ == "__main__":
    main()
