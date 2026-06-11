from playwright.sync_api import sync_playwright

OUT = r"D:\ClaudeCode\MusicalMap\preview_wicked.png"

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1400, "height": 880})
    pg.goto("http://localhost:8753/", wait_until="networkidle")
    pg.wait_for_selector(".show-group", timeout=15000)
    pg.wait_for_timeout(1500)
    pg.evaluate(
        """() => {
        const g = [...document.querySelectorAll('.show-group')]
          .find(el => el.querySelector('.title')?.textContent.trim().startsWith('Wicked'));
        if (g) { g.scrollIntoView({block:'center'}); g.querySelector('.show-item').click(); }
    }"""
    )
    pg.wait_for_timeout(3000)  # let fitBounds + tiles settle
    pg.screenshot(path=OUT)
    print("saved", OUT)
    b.close()
