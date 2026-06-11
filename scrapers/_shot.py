from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1300,"height":820})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector("#timebar",timeout=15000); pg.wait_for_timeout(2500)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_timebar.png"); print("today")
    # drag slider to +61 days (Aug 12)
    pg.evaluate("els.tRange.value=61; els.tRange.dispatchEvent(new Event('input'))")
    pg.wait_for_timeout(2000)
    pg.evaluate("map.setView([39,-96],4)")
    pg.wait_for_timeout(2500)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_future.png"); print("future")
    b.close()
