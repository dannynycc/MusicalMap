from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1200,"height":800})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector(".leaflet-marker-icon",timeout=15000)
    pg.evaluate("const s=ALL.find(x=>x.title==='Wicked'&&x.city==='London'); focusShow(s);")
    pg.wait_for_timeout(3000)
    n=pg.locator(".mm-popup .pop-cta.sm").count()
    print("multi ticket links:",n)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_multilink.png")
    b.close()
