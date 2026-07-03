/* 自訂海報/連結截圖 v2:精準鎖 poster 標籤→link 輸入框底,含填好的連結 */
const { chromium } = require('playwright');
const B = 'http://localhost:8766/MusicalMap/';
const OUT = 'C:/Users/Home/AppData/Local/Temp/claude/C--Users-Home/79bfe7d5-ce91-4131-96a1-9968e0d0425f/scratchpad/shots/';
const POSTER = 'https://cdn-imgix.headout.com/media/images/79059f2bed566c8f56467f3ef7389605-512.png';
const LINK = 'https://wickedthemusical.com';
(async () => {
  const br = await chromium.launch({ channel: 'chrome', headless: true });
  for (const hl of ['zh-hant', 'zh-hans', 'en']) {
    const ctx = await br.newContext({ viewport: { width: 560, height: 1600 }, deviceScaleFactor: 2 });
    const pf = await ctx.newPage();
    await pf.goto(B + 'me-input.html?embed=1&hl=' + hl, { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pf.waitForSelector('#q', { timeout: 20000 });
    await pf.waitForTimeout(1500);
    await pf.fill('#q', 'wicked');
    await pf.waitForTimeout(1500);
    await pf.click('#results > *');
    await pf.waitForTimeout(1200);
    const prod = await pf.$('.pcard[data-g], .pcard[data-c]');
    if (prod) { await prod.click(); await pf.waitForTimeout(1200); }
    const prod2 = await pf.$('.pcard[data-c]');
    if (prod2) { await prod2.click(); await pf.waitForTimeout(1200); }
    const more = await pf.$('#more');
    if (more) { const hid = await pf.evaluate(() => { const l2 = document.getElementById('l2'); return l2 && l2.hidden; }); if (hid) { await more.click(); await pf.waitForTimeout(600); } }
    // 填海報 URL + 連結
    const pin = await pf.$('input[placeholder*="貼上圖片"], input[placeholder*="贴上图片"], input[placeholder*="image URL" i], input[placeholder*="Paste an image" i]');
    const lin = await pf.$('input[placeholder*="售票或節目"], input[placeholder*="售票或节目"], input[placeholder*="programme" i]');
    if (!pin || !lin) { console.log('FIELD MISS', hl, !!pin, !!lin); await pf.screenshot({ path: `${OUT}custom_debug_${hl}.png`, fullPage: true }); await pf.close(); await ctx.close(); continue; }
    await pin.fill(POSTER); await pin.dispatchEvent('input');
    await lin.fill(LINK); await lin.dispatchEvent('input');
    await pf.waitForTimeout(2500);
    // 邊界:poster 欄的「標籤」(往上找最近的 .lbl/label) → link 輸入框底
    const box = await pf.evaluate(() => {
      const pin2 = document.querySelector('input[placeholder*="貼上圖片"], input[placeholder*="贴上图片"], input[placeholder*="Paste an image"]');
      const lin2 = document.querySelector('input[placeholder*="售票或節目"], input[placeholder*="售票或节目"], input[placeholder*="programme"]');
      let lab = pin2; while (lab && lab.previousElementSibling == null) lab = lab.parentElement;
      const labEl = lab ? lab.previousElementSibling : null;
      const top = (labEl || pin2).getBoundingClientRect().top;
      const bot = lin2.getBoundingClientRect().bottom;
      return { top, bot };
    });
    const y = Math.max(0, box.top - 12);
    await pf.screenshot({ path: `${OUT}custom_${hl}.png`, clip: { x: 0, y, width: 560, height: box.bot + 14 - y } });
    console.log('ok', hl, JSON.stringify(box));
    await pf.close(); await ctx.close();
  }
  await br.close();
})();
