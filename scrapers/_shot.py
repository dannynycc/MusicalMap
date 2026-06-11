from playwright.sync_api import sync_playwright
ok=[]
def chk(n,c): ok.append(c); print(("PASS " if c else "FAIL ")+n)
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1300,"height":820})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector(".leaflet-marker-icon",timeout=15000)
    chk("filters removed", pg.locator("#filters").count()==0)
    # Elisabeth @ Ostrava with image
    pg.evaluate("map.setView([49.836,18.288],13)"); pg.wait_for_timeout(2500)
    has_img=pg.evaluate("""()=>{const e=[...document.querySelectorAll('.poster-pin')];return e.length>0 && e.some(x=>x.style.backgroundImage.includes('ndm.cz'))}""")
    chk("Elisabeth marker with NDM image", has_img)
    pg.locator(".poster-pin").first.click(); pg.wait_for_timeout(1000)
    chk("popup no type tag", pg.locator(".mm-popup .p-tag").count()==0)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_elisabeth.png")
    # hover+click mutual exclusion still good
    pg.evaluate("map.closePopup(); map.setView([31.76,-106.49],12)"); pg.wait_for_timeout(2200)
    pin=pg.locator(".poster-pin").first; pin.hover(); pg.wait_for_timeout(400); pin.click(); pg.wait_for_timeout(800)
    chk("hover->click exclusive", pg.locator(".mm-tip").count()==0 and pg.locator(".mm-popup").count()==1)
    b.close()
print("ALL PASS" if all(ok) else "HAS FAILURES")
