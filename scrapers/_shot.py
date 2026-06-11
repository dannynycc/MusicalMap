from playwright.sync_api import sync_playwright
ok=[]
def chk(name,cond): ok.append((name,cond)); print(("PASS " if cond else "FAIL ")+name)
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1300,"height":820})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector(".leaflet-marker-icon",timeout=15000)

    # U1: hover marker -> small card appears
    pg.evaluate("map.setView([31.76,-106.49],12)"); pg.wait_for_timeout(2200)
    pin=pg.locator(".poster-pin").first
    pin.hover(); pg.wait_for_timeout(500)
    chk("U1 hover shows small card", pg.locator(".mm-tip").count()==1)

    # U2: click same marker -> big card opens, small card disappears
    pin.click(); pg.wait_for_timeout(900)
    chk("U2 click: big card open", pg.locator(".mm-popup").count()==1)
    chk("U2 click: small card GONE", pg.locator(".mm-tip").count()==0)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_u2.png")

    # U3: low-zoom click -> popup suppressed during flight, opens after
    pg.evaluate("map.closePopup(); map.setView([39,-96],4)"); pg.wait_for_timeout(1800)
    pg.locator(".poster-pin").first.click(); pg.wait_for_timeout(250)
    mid=pg.locator(".mm-popup").count()
    pg.wait_for_timeout(3000)
    chk("U3 no popup mid-fly", mid==0)
    chk("U3 popup after fly + zoomed", pg.locator(".mm-popup").count()==1 and pg.evaluate("map.getZoom()")>=9)

    # U4: sidebar hover on clustered marker -> no orphan small card
    pg.evaluate("map.closePopup(); map.setView([20,0],2)"); pg.wait_for_timeout(1500)
    pg.evaluate("""()=>{const it=[...document.querySelectorAll('.show-item')].find(e=>e.textContent.includes('Aladdin'));it&&it.dispatchEvent(new MouseEvent('mouseenter',{bubbles:true}))}""")
    pg.wait_for_timeout(400)
    chk("U4 clustered hover: no orphan card", pg.locator(".mm-tip").count()==0)

    # U5: expand a group, drag slider -> stays expanded
    pg.evaluate("""()=>{const g=[...document.querySelectorAll('.show-group')].find(e=>e.querySelector('.title')?.textContent.trim().startsWith('Wicked'));g.querySelector('.show-item').click()}""")
    pg.wait_for_timeout(700)
    pg.evaluate("els.tRange.value=45; els.tRange.dispatchEvent(new Event('input'))")
    pg.wait_for_timeout(800)
    chk("U5 group stays open after slider", pg.evaluate("""()=>{const g=[...document.querySelectorAll('.show-group')].find(e=>e.querySelector('.title')?.textContent.trim().startsWith('Wicked'));return g?.classList.contains('open')}"""))

    # U6: tour filter -> global, not US-only
    pg.evaluate("els.tRange.value=0; els.tRange.dispatchEvent(new Event('input'))"); pg.wait_for_timeout(600)
    pg.evaluate("""()=>{document.querySelector('input[data-filter=resident]').click()}"""); pg.wait_for_timeout(700)
    cnt=pg.locator("#count").text_content()
    au=pg.evaluate("""()=>[...document.querySelectorAll('.show-item .meta')].some(e=>/Pyrmont|Sydney|Dublin|Auckland|Zürich|Haymarket|Burswood/.test(e.textContent))""")
    chk("U6 tours include non-US (AU/IE/NZ/CH)", au)
    pg.screenshot(path=r"D:\ClaudeCode\MusicalMap\preview_tours.png")
    print("tour count label:",cnt)
    b.close()
print("ALL PASS" if all(c for _,c in ok) else "HAS FAILURES")
