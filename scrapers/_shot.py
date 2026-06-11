from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1300, "height": 820})
    pg.goto("http://localhost:8753/", wait_until="networkidle")
    pg.wait_for_selector(".leaflet-marker-icon", timeout=15000)
    pg.evaluate("map.setView([30, -30], 2)")
    pg.wait_for_timeout(3000)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_world.png")
    print("saved world")

    # Phantom SF tour popup: check name (no 'The') + full poster
    pg.evaluate("map.setView([37.78, -122.41], 13)")
    pg.wait_for_timeout(2500)
    try:
        pg.eval_on_selector(".poster-pin", "el => el.parentElement.click()")
        pg.wait_for_timeout(1200)
    except Exception:
        pass
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_popup.png")
    print("saved popup")
    b.close()
