// Record short phone-sized clips of real play (title -> map -> battle -> boss) for review. Needs ffmpeg.
// Usage: node tools/record.mjs [baseUrl] [outDir]
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";
const base = (process.argv[2] || "http://127.0.0.1:5194/").replace(/\/?$/, "/");
const out = process.argv[3] || "docs/media";
mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--mute-audio", "--user-data-dir=" + (process.env.TMPDIR || "/tmp") + "/rec-chrome-" + Date.now()] });
const page = await browser.newPage();
await page.setViewport({ width: 844, height: 390, deviceScaleFactor: 1, isMobile: true, hasTouch: true, isLandscape: true });
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
await page.goto(base + "?test=1", { waitUntil: "networkidle0" });
await page.evaluate(() => localStorage.clear()); await page.reload({ waitUntil: "networkidle0" });
const rec = await page.screencast({ path: `${out}/playthrough.webm` });
await sl(1500);
await page.evaluate(() => __siegeline.worldMap()); await sl(1800);
await page.evaluate(() => __siegeline.regionScreen()); await sl(1800);
await page.evaluate(() => __siegeline.startBattle("r1s3")); await page.waitForSelector(".hud .weapon", { visible: true });
await page.evaluate(() => { const D = __siegeline.D; D.unlocked.units = ["ashguard", "torchbow", "cinder_runner", "maulwright"]; });
await page.evaluate(() => { __siegeline.battle.tutor = null; __siegeline.autoplay(0.75); __siegeline.setSpeed(1.5); });
// a real aimed ballista shot partway through
await sl(9000);
const w = await page.$(".weapon"); const b = await w.boundingBox(); const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
await page.mouse.move(cx, cy); await page.mouse.down(); await page.mouse.move(cx - 55, cy + 35, { steps: 10 }); await sl(700); await page.mouse.up();
await sl(14000);
await page.evaluate(() => { __siegeline.autoplay(null); __siegeline.battle && __siegeline.battle.quit(); });
// boss fight
await page.evaluate(() => { const D = __siegeline.D; D.unlocked.units = ["ashguard", "torchbow", "cinder_runner", "maulwright", "bellringer", "lamplighter"]; D.unlocked.hero = true; D.unlocked.abilities = ["ember_rain", "rally"]; for (const u of D.unlocked.units) D.unitLevels[u] = 4; });
await page.evaluate(() => __siegeline.startBattle("r1boss")); await page.waitForSelector(".hud .weapon", { visible: true });
await page.evaluate(() => { __siegeline.autoplay(0.8); __siegeline.setSpeed(1.5); });
await sl(30000);
await page.evaluate(() => __siegeline.setSpeed(4));
await page.waitForSelector(".result", { timeout: 45000 }).catch(() => {});
await page.evaluate(() => __siegeline.setSpeed(1)); await sl(5000);
await rec.stop();
await browser.close();
console.log("recorded", `${out}/playthrough.webm`);
