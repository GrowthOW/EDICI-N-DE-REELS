// Renderiza piezas HTML a PNG con Chromium (texto real, nunca imagen).
//   node render.js still  <pagina.html> <w> <h> <salida_dir> <estados.json>
//       estados.json = [{"id": "s1", ...params}] -> salida_dir/<id>.png (params en location.hash)
//   node render.js frames <pagina.html> <w> <h> <salida_dir> <fps>
//       la página expone window.TOTAL y window.renderAt(t) -> salida_dir/f_00000.png, transparente
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
const [mode, page_, w, h, out, extra] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
(async () => {
  const exe = fs.readdirSync('/opt/pw-browsers').find(d => /^chromium-\d+$/.test(d));
  const browser = await chromium.launch({ executablePath: `/opt/pw-browsers/${exe}/chrome-linux/chrome`,
    args: ['--force-color-profile=srgb', '--disable-lcd-text', '--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  const url = 'file://' + path.resolve(page_);
  if (mode === 'still') {
    const states = JSON.parse(fs.readFileSync(extra, 'utf8'));
    for (const s of states) {
      await page.goto(url + '#' + encodeURIComponent(JSON.stringify(s)));
      await page.reload();
      await page.waitForFunction('window.__READY__ === true', null, { timeout: 30000 });
      const warn = await page.evaluate(() => window.__WARN__ || null);
      if (warn) console.log('AVISO', s.id, warn);
      await page.screenshot({ path: path.join(out, s.id + '.png'), omitBackground: true });
      console.log('ok', s.id);
    }
  } else {
    await page.goto(url);
    await page.waitForFunction('window.__READY__ === true', null, { timeout: 30000 });
    const fps = +extra, total = await page.evaluate('window.TOTAL');
    const n = Math.round(total * fps);
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => window.renderAt(t), i / fps);
      await page.screenshot({ path: path.join(out, `f_${String(i).padStart(5, '0')}.png`), omitBackground: true });
      if (i % 50 === 0) console.log('frame', i, '/', n);
    }
  }
  await browser.close();
})();
