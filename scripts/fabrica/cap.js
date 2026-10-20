// Captura HTML -> PNG con Playwright y QA de textos.
// Uso: node cap.js jobs.json   (jobs = [{html, out, w, h, safe:{top,bottom,right,left}}])
// QA: los elementos .t no se pisan entre sí y quedan dentro de la zona segura.
const { chromium } = require('/opt/node22/lib/node_modules/playwright'); const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const exe = fs.readdirSync('/opt/pw-browsers').find(d => /^chromium-\d+$/.test(d));
  const b = await chromium.launch({ executablePath: `/opt/pw-browsers/${exe}/chrome-linux/chrome` });
  const res = [];
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
    await p.goto('file://' + j.html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    const s = j.safe || { top: 0, bottom: 0, right: 0, left: 0 };
    const r = await p.evaluate(() => [...document.querySelectorAll('.t')].map(e => { const b = e.getBoundingClientRect(); return { id: e.id, x0: b.left, y0: b.top, x1: b.right, y1: b.bottom } }));
    const bad = [];
    for (let i = 0; i < r.length; i++) {
      const a = r[i];
      if (a.y0 < s.top || a.y1 > j.h - s.bottom || a.x1 > j.w - s.right || a.x0 < s.left) bad.push('fuera de zona ' + a.id);
      if (s.notchX && a.y1 > s.notchY && a.x1 > s.notchX) bad.push('tapado por los botones de IG ' + a.id);
      for (let k = i + 1; k < r.length; k++) { const c = r[k]; if (a.x0 < c.x1 && c.x0 < a.x1 && a.y0 < c.y1 && c.y0 < a.y1) bad.push('se pisan ' + a.id + '/' + c.id) }
    }
    await p.screenshot({ path: j.out, omitBackground: true }); await p.close();
    res.push({ out: j.out, ok: bad.length === 0, bad });
  }
  await b.close(); console.log(JSON.stringify(res));
})();
