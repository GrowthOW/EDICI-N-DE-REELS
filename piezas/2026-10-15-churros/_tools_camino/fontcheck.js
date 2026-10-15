const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const exe = fs.readdirSync('/opt/pw-browsers').find(d => /^chromium-\d+$/.test(d));
  const b = await chromium.launch({ executablePath: `/opt/pw-browsers/${exe}/chrome-linux/chrome`, args: ['--allow-file-access-from-files'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(__dirname, 'native_overlay.html') + '?p=' + process.argv[2]);
  await pg.waitForFunction('window.__READY__ === true');
  console.log(await pg.evaluate(() => [document.fonts.check('700 64px Body'), [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight)]));
  await b.close();
})();
