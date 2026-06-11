from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1100,"height":760})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector(".show-group",timeout=15000); pg.wait_for_timeout(1200)
    pg.evaluate("""()=>{const g=[...document.querySelectorAll('.show-group')].find(e=>e.querySelector('.title')?.textContent.includes('Lion King'));g&&g.querySelector('.show-item').click();}""")
    pg.wait_for_timeout(1500)
    pg.evaluate("()=>{const m=Object.values(window).find(x=>x);}")
    # click first poster pin to open a popup
    pg.evaluate("map.setView([19.44,-99.20],14)"); pg.wait_for_timeout(2500)
    try: pg.eval_on_selector(".poster-pin","el=>el.parentElement.click()"); pg.wait_for_timeout(1200)
    except Exception: pass
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_cta.png"); print("cta")
    b.close()
