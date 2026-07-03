/* stats(完整 statgrid 元素) + form(裁在第一筆結果底部) 三語重拍 */
const { chromium } = require('playwright');
const B = 'http://localhost:8766/MusicalMap/';
const OUT = 'C:/Users/Home/AppData/Local/Temp/claude/C--Users-Home/79bfe7d5-ce91-4131-96a1-9968e0d0425f/scratchpad/shots/';
(async () => {
  const br = await chromium.launch({ channel: 'chrome', headless: true });
  for (const hl of ['zh-hant', 'zh-hans', 'en']) {
    const ctx = await br.newContext({ viewport: { width: 1300, height: 2400 }, deviceScaleFactor: 2 });   // >1100:統計卡 4+3 一排(v1.26.1 版型)

    // stats:拍完整 .statgrid 元素(不裁)
    const pm = await ctx.newPage();
    await pm.goto(B + 'me.html?hl=' + hl, { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pm.waitForTimeout(2500);
    await pm.evaluate(() => {
      ['#mev2gate', 'header', '.demobanner', '.controls'].forEach(s => document.querySelectorAll(s).forEach(el => el.style.display = 'none'));
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
    });
    await pm.waitForTimeout(1500);   // Chart.js 畫完
    const statEl = await pm.$('.statgrid');
    await statEl.screenshot({ path: `${OUT}stats_${hl}.png` });
    await pm.close();

    // form:裁到第一筆結果底部+12px
    const pf = await ctx.newPage();
    await pf.setViewportSize({ width: 560, height: 900 });
    await pf.goto(B + 'me-input.html?embed=1&hl=' + hl, { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pf.waitForSelector('#q', { timeout: 20000 });
    await pf.waitForTimeout(1500);
    await pf.fill('#q', hl === 'en' ? 'phantom' : '歌劇魅影');
    await pf.waitForTimeout(1800);
    const fb = await pf.evaluate(() => {
      const rows = document.querySelectorAll('#results > *');
      const first = rows[0];
      const bot = first ? first.getBoundingClientRect().bottom : 258;
      return Math.ceil(bot + 12);
    });
    await pf.screenshot({ path: `${OUT}form_${hl}.png`, clip: { x: 0, y: 0, width: 560, height: fb } });
    await pf.close();
    await ctx.close();
    console.log('done', hl);
  }
  await br.close();
})();
