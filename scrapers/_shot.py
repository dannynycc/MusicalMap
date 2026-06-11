from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1100,"height":760})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector(".leaflet-marker-icon",timeout=15000)
    t0=time.time()
    pg.evaluate("map.setView([49.836,18.288],13)")
    pg.wait_for_timeout(1500)
    ok=pg.evaluate("""()=>{const e=[...document.querySelectorAll('.poster-pin')];return e.some(x=>x.style.backgroundImage.includes('assets/posters/elisabeth'))}""")
    # measure the asset load directly
    r=pg.evaluate("""async()=>{const t0=performance.now();await fetch('assets/posters/elisabeth-ostrava.jpg').then(r=>r.blob());return Math.round(performance.now()-t0)}""")
    print("marker uses local asset:",ok,"| local fetch ms:",r)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_eli2.png")
    b.close()
