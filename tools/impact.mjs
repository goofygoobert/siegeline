// Screenshot the frame just after the first cannonball that hits monsters. Usage: node tools/impact.mjs OUT.png [baseUrl] [delayMs]
import puppeteer from "puppeteer-core";
const [out, base = "http://127.0.0.1:5194/", delay = "90"] = process.argv.slice(2);
const browser = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--mute-audio", `--user-data-dir=${process.env.TMPDIR || "/tmp"}/im-chrome-${Date.now()}`] });
const page = await browser.newPage();
await page.setViewport({ width: 844, height: 390, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
await page.goto(base + "?test=1&seed=7", { waitUntil: "networkidle0" });
await page.evaluate(() => localStorage.clear()); await page.reload({ waitUntil: "networkidle0" });
await page.evaluate(() => { __siegeline.D.tutorials.push("basics", "ability", "hero"); __siegeline.startBattle("r1s1"); });
await page.waitForSelector(".hud .weapon", { timeout: 30000 });
await page.evaluate(() => { const S = __siegeline, b = S.battle; if (b.tutor) b.endTutor(true); S.autoplay(0.9); S.setSpeed(3);
  const c = S.R.consume; S.R.consume = (B) => { for (const e of B.events) if (e.type === "boltHit" && e.hits >= 2 && B.t > 25 && !window.__hit) { window.__hit = 1; S.setSpeed(1); S.R.camTarget = Math.max(0, e.x - S.R.W * 0.5); S.R.camX = Math.max(0, e.x - S.R.W * 0.5); } c(B); }; });
await page.waitForFunction("window.__hit", { timeout: 120000 });
await sl(+delay); await page.evaluate(() => { __siegeline.battle.paused = true; }); await sl(120);
await page.screenshot({ path: out }); console.log("shot", out);
await browser.close();
