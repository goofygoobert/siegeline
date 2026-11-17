// Screens for design review at one viewport: Quartermaster (with coins), tutorial start, a win tally.
// Usage: VW=667 VH=375 node tools/uishots.mjs OUTDIR [baseUrl] [prefix]
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";
const [out, base = "http://127.0.0.1:5194/", pre = ""] = process.argv.slice(2);
const VW = +(process.env.VW || 844), VH = +(process.env.VH || 390);
mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--mute-audio", `--user-data-dir=${process.env.TMPDIR || "/tmp"}/ui-chrome-${Date.now()}`] });
const page = await browser.newPage();
await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
const shot = async (n) => { await page.screenshot({ path: `${out}/${pre}${n}.png` }); console.log("shot", n); };
await page.goto(base + "?test=1&seed=7", { waitUntil: "networkidle0" });
await page.evaluate(() => localStorage.clear()); await page.reload({ waitUntil: "networkidle0" });
await page.evaluate(() => { __siegeline.startBattle("r1s1"); });
await page.waitForSelector(".hud .weapon", { timeout: 30000 }); await sl(2200); await shot("tutorial");
await page.evaluate(() => { const b = __siegeline.battle; b.endTutor(true); __siegeline.autoplay(0.7); __siegeline.setSpeed(6); });
await page.waitForSelector(".result", { timeout: 120000 }); await page.evaluate(() => __siegeline.setSpeed(1)); await sl(3200); await shot("win");
await page.evaluate(() => { const D = __siegeline.D; D.marks = 260; D.unitLevels.ashguard = 4; __siegeline.armoury(); });
await sl(1200); await shot("quartermaster");
await browser.close();
