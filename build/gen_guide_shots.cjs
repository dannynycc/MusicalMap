/* guide 素材產製 v2:三語 × (map/popup/form/stats/wall) PNG@2x */
const { chromium } = require('playwright');
const fs = require('fs');
const B = 'http://localhost:8766/MusicalMap/';
const OUT = 'C:/Users/Home/AppData/Local/Temp/claude/C--Users-Home/79bfe7d5-ce91-4131-96a1-9968e0d0425f/scratchpad/shots/';
fs.mkdirSync(OUT, { recursive: true });
const LANGS = ['zh-hant', 'zh-hans', 'en'];
(async () => {
  const br = await chromium.launch({ channel: 'chrome', headless: true });
  for (const hl of LANGS) {
    const ctx = await br.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });

    // ---- map(美東視角) ----
    const pg = await ctx.newPage();
    await pg.goto(B + hl + '/', { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pg.waitForFunction(() => document.body.classList.contains('ready') && window.mmMap, { timeout: 30000 });
    await pg.setViewportSize({ width: 1160, height: 790 });   // 360 側欄 + 800 地圖;58 header+~64 filterbar+668
    await pg.evaluate(() => window.mmMap.setView([39.5, -78], 4));
    await pg.waitForTimeout(5000);
    const mb = await pg.evaluate(() => { const r = document.getElementById('map').getBoundingClientRect(); return { x: r.x, y: r.y, h: r.height }; });
    await pg.screenshot({ path: `${OUT}map_${hl}.png`, clip: { x: mb.x, y: mb.y, width: 800, height: Math.min(668, mb.h) } });

    // ---- popup:搜 Wicked → 展開的 group 點第一個 .stop(城市列) ----
    await pg.setViewportSize({ width: 1280, height: 900 });
    await pg.fill('#search', 'Wicked');
    await pg.waitForTimeout(1200);
    const stop = await pg.$('#show-list .show-group .stop') || await pg.$('#show-list .show-item.single') || await pg.$('#show-list .show-item');
    if (stop) await stop.click();
    await pg.waitForSelector('.leaflet-popup .popup', { timeout: 15000 }).catch(()=>{});
    await pg.waitForTimeout(3000);
    const pb = await pg.evaluate(() => { const el = document.querySelector('.leaflet-popup'); if (!el) return null; const r = el.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; });
    if (pb) {
      const cx = pb.x + pb.w / 2, cy = pb.y + pb.h / 2;
      const x = Math.max(0, Math.min(1280 - 664, cx - 332)), y = Math.max(0, Math.min(900 - 382, cy - 191));
      await pg.screenshot({ path: `${OUT}popup_${hl}.png`, clip: { x, y, width: 664, height: 382 } });
    } else { console.log('POPUP MISS', hl); }
    await pg.close();

    // ---- form ----
    const pf = await ctx.newPage();
    await pf.setViewportSize({ width: 560, height: 700 });
    await pf.goto(B + 'me-input.html?embed=1&hl=' + hl, { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pf.waitForSelector('#q', { timeout: 20000 });
    await pf.waitForTimeout(1500);
    await pf.fill('#q', hl === 'en' ? 'phantom' : '歌劇魅影');
    await pf.waitForTimeout(1500);
    await pf.screenshot({ path: `${OUT}form_${hl}.png`, clip: { x: 0, y: 0, width: 560, height: 258 } });
    await pf.close();

    // ---- stats + wall(me.html demo;藏 gate/header/controls/banner,等海報載完) ----
    const pm = await ctx.newPage();
    await pm.setViewportSize({ width: 800, height: 1000 });
    await pm.goto(B + 'me.html?hl=' + hl, { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pm.waitForTimeout(2500);
    await pm.evaluate(() => {
      const kill = ['#mev2gate', 'header', '.demobanner', '.controls'];
      kill.forEach(s => document.querySelectorAll(s).forEach(el => el.style.display = 'none'));
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
    });
    // 等海報牆所有圖載完(最多 12s)
    await pm.waitForFunction(() => {
      const imgs = [...document.querySelectorAll('#wall-poster img')];
      return imgs.length > 0 && imgs.every(i => i.complete && i.naturalWidth > 0);
    }, { timeout: 12000 }).catch(()=>{});
    // 元素截圖(自動捲動),之後 PIL 裁上緣到目標高度
    const wallEl = await pm.$('#wall-poster');
    await wallEl.screenshot({ path: `${OUT}wall_${hl}.png` });
    const statEl = await pm.$('.statgrid');
    await statEl.screenshot({ path: `${OUT}stats_${hl}.png` });
    await pm.close();
    await ctx.close();
    console.log('done', hl);
  }
  await br.close();
})();
