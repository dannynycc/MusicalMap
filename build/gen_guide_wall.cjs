/* 海報牆重拍:寬版(更多欄)+整排邊界裁切(不切半張)+等全部海報載完 */
const { chromium } = require('playwright');
const fs = require('fs');
const B = 'http://localhost:8766/MusicalMap/';
const OUT = 'C:/Users/Home/AppData/Local/Temp/claude/C--Users-Home/79bfe7d5-ce91-4131-96a1-9968e0d0425f/scratchpad/shots/';
(async () => {
  const br = await chromium.launch({ channel: 'chrome', headless: true });
  for (const hl of ['zh-hant', 'zh-hans', 'en']) {
    const ctx = await br.newContext({ viewport: { width: 1440, height: 1900 }, deviceScaleFactor: 2 });
    const pm = await ctx.newPage();
    await pm.goto(B + 'me.html?hl=' + hl, { waitUntil: 'networkidle', timeout: 40000 }).catch(()=>{});
    await pm.waitForTimeout(2500);
    await pm.evaluate(() => {
      ['#mev2gate', 'header', '.demobanner', '.controls'].forEach(s => document.querySelectorAll(s).forEach(el => el.style.display = 'none'));
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
      window.scrollTo(0, 0);
    });
    await pm.waitForFunction(() => {
      const imgs = [...document.querySelectorAll('#wall-poster img')];
      return imgs.length > 8 && imgs.every(i => i.complete && i.naturalWidth > 0);
    }, { timeout: 20000 }).catch(() => console.log('img wait timeout', hl));
    await pm.waitForTimeout(800);
    // 算前兩排的精準邊界:取卡片 offsetTop 的相異值排序
    const m = await pm.evaluate(() => {
      const wall = document.getElementById('wall-poster');
      const r = wall.getBoundingClientRect();
      const kids = [...wall.children].filter(el => el.offsetParent !== null);
      const tops = [...new Set(kids.map(el => Math.round(el.getBoundingClientRect().top)))].sort((a, b) => a - b);
      const cols = kids.filter(el => Math.round(el.getBoundingClientRect().top) === tops[0]).length;
      // 裁到第 2 排底:第2排卡片的 bottom 最大值
      const row2 = kids.filter(el => Math.round(el.getBoundingClientRect().top) === tops[1]);
      const row2bot = Math.max(...row2.map(el => el.getBoundingClientRect().bottom));
      return { x: r.x, y: r.y, w: r.width, h: row2bot - r.y, cols, rows: tops.length };
    });
    console.log(hl, 'cols=' + m.cols, 'rows=' + m.rows, 'crop', Math.round(m.w), '×', Math.round(m.h));
    await pm.screenshot({ path: `${OUT}wall_${hl}.png`, clip: { x: m.x, y: m.y, width: m.w, height: m.h } });
    await pm.close();
    await ctx.close();
  }
  await br.close();
})();
