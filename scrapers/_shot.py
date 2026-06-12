from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="msedge",headless=True)
    pg=b.new_page(viewport={"width":1200,"height":800})
    pg.goto("http://localhost:8753/",wait_until="networkidle")
    pg.wait_for_selector(".leaflet-marker-icon",timeout=15000)
    for title,city in [("The Phantom of the Opera","London"),("The Lion King","New York"),("Mamma Mia!","Yokohama")]:
        txt=pg.evaluate(f"""()=>{{const s=ALL.find(x=>x.title.includes('{title.split()[-1]}')&&x.city==='{city}');
            return s?JSON.stringify([s.title,s.start_date,s.end_date]):'none'}}""")
        print(city,txt)
    # render check: open Phantom London popup, read date line
    pg.evaluate("const s=ALL.find(x=>x.city==='London'&&x.group==='phantom of the opera'); focusShow(s);")
    pg.wait_for_timeout(2500)
    body=pg.evaluate("document.querySelector('.mm-popup .pop-body')?.innerText || ''")
    print("POPUP:",body.replace(chr(10),' | ')[:160])
    chk=pg.evaluate("document.body.innerText.includes('常駐演出中')")
    print("any 常駐演出中 left:",chk)
    b.close()
