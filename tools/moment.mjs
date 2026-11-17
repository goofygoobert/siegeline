// Screenshot one repeatable battle moment: fixed seed, test player, paused at a given battle time.
// Usage: node tools/moment.mjs OUT.png [baseUrl] [stageId] [time s] [seed]     env VW/VH for the viewport
import puppeteer from "puppeteer-core";
import os from "node:os";
const [out, base = "http://127.0.0.1:5194/", stage = "r1s1", T = "40", seed = "7"] = process.argv.slice(2);
const VW = +(process.env.VW || 844), VH = +(process.env.VH || 390);
if (os.freemem() / 1048576 < 450) { console.error("low memory"); process.exit(2); }
const browser = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--mute-audio", `--user-data-dir=${process.env.TMPDIR || "/tmp"}/mo-chrome-${Date.now()}`] });
const page = await browser.newPage();
await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
await page.goto(base + "?test=1&seed=" + seed, { waitUntil: "networkidle0" });
await page.evaluate(() => localStorage.clear()); await page.reload({ waitUntil: "networkidle0" });
await page.evaluate((id) => { const S = __siegeline; S.D.tutorials.push("basics", "ability", "hero"); S.startBattle(id); }, stage);
await page.waitForSelector(".hud .weapon", { timeout: 30000 });
await page.evaluate(() => { const b = __siegeline.battle; if (b.tutor) b.endTutorial ? b.endTutorial(true) : (b.tutor = null); __siegeline.autoplay(0.7); __siegeline.setSpeed(6); });
const t0 = Date.now();
while (Date.now() - t0 < 120000) {
  const t = await page.evaluate(() => __siegeline.battle.B.t);
  if (t >= +T - 1.2) break; await sl(60);
}
await page.evaluate(() => __siegeline.setSpeed(1));
while ((await page.evaluate(() => __siegeline.battle.B.t)) < +T) await sl(30);
await page.evaluate(() => { __siegeline.battle.paused = true; });
await sl(200); await page.screenshot({ path: out });
console.log("shot", out, await page.evaluate(() => __siegeline.battle.B.t.toFixed(2)));
await browser.close();
