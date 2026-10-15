// Vista previa rápida: node preview.js <carpeta_pieza> <t1,t2,...> -> <carpeta>/pv/ov_<t>.png (solo las cartelas)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
const [dir, ts] = process.argv.slice(2);
(async () => {
  const exe = fs.readdirSync('/opt/pw-browsers').find(d => /^chromium-\d+$/.test(d));
  const b = await chromium.launch({ executablePath: `/opt/pw-browsers/${exe}/chrome-linux/chrome`, args: ['--allow-file-access-from-files'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(__dirname, 'native_overlay.html') + '?p=' + path.relative(__dirname, path.resolve(dir)));
  await pg.waitForFunction('window.__READY__ === true');
  fs.mkdirSync(path.join(dir, 'pv'), { recursive: true });
  for (const t of ts.split(',')) { await pg.evaluate(x => window.renderAt(x), +t);
    await pg.screenshot({ path: path.join(dir, 'pv', `ov_${t}.png`), omitBackground: true }); }
  await b.close();
})();
