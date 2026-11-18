// Every screen at one phone size, for the part 4 consistency check. With NOTCH=1 the landscape safe areas of a notched
// iPhone are simulated (the game reads them through --sal/--sar/--sab, which normally come from env()).
// Usage: VW=667 VH=375 [NOTCH=1] node tools/screens.mjs OUTDIR [baseUrl]
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";
const [out, base = "http://127.0.0.1:5194/"] = process.argv.slice(2);
const VW = +(process.env.VW || 844), VH = +(process.env.VH || 390), NOTCH = !!process.env.NOTCH;
mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--mute-audio", `--user-data-dir=${process.env.TMPDIR || "/tmp"}/sc-chrome-${Date.now()}`] });
const page = await browser.newPage();
await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
const errs = []; page.on("pageerror", (e) => errs.push(e.message));
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
const notch = () => NOTCH && page.evaluate(() => { const s = document.documentElement.style; s.setProperty("--sal", "47px"); s.setProperty("--sar", "47px"); s.setProperty("--sab", "21px"); });
const shot = async (n) => { await notch(); await sl(350); await page.screenshot({ path: `${out}/${n}.png` }); console.log("shot", n); };
const G = (f, ...a) => page.evaluate(f, ...a);
await page.goto(base + "?test=1&seed=7", { waitUntil: "networkidle0" });
await G(() => localStorage.clear()); await page.reload({ waitUntil: "networkidle0" }); await sl(800);
await shot("01-title");
// mid-region progress: stages 1-6 cleared, so the Tavern, recruits and powers are all there
await G(() => { const D = __siegeline.D; for (const id of ["r1s1", "r1s2", "r1s3", "r1s4", "r1s5", "r1s6"]) D.stages[id] = { stars: [true, true, false], best: 100, clears: 1 }; D.marks = 820; D.tutorials = ["basics", "ability", "hero"]; D.unitLevels.ashguard = 10; __siegeline.save(); });
await page.reload({ waitUntil: "networkidle0" }); await sl(600);
await G(() => __siegeline.worldMap()); await sl(1200); await shot("02-worldmap");
await G(() => __siegeline.regionScreen()); await sl(1500); await shot("03-region");
await G(() => __siegeline.prepScreen("r1s7")); await sl(1200);
await G(() => document.querySelector(".foe.new")?.click()); await shot("04-scouting-loadout");
await G(() => __siegeline.tavern()); await sl(900); await shot("05-tavern");
await G(() => __siegeline.armoury()); await sl(900); await shot("06-quartermaster-skill-choice");
await G(() => __siegeline.openSettings()); await sl(600); await shot("07-settings");
await page.reload({ waitUntil: "networkidle0" }); await sl(500);
await G(() => __siegeline.startBattle("r1s7", ["maulwright", "cinder_runner", "bellringer", "netcaster", "ashguard"]));
await page.waitForSelector(".hud .weapon", { timeout: 30000 }); await G(() => { __siegeline.autoplay(0.7); __siegeline.setSpeed(3); }); await sl(9000);
await G(() => __siegeline.setSpeed(0.0001)); await shot("08-battle");
await G(() => document.querySelector('button[aria-label="Pause"]').click()); await shot("09-pause");
await page.reload({ waitUntil: "networkidle0" }); await sl(500);
await G(() => { __siegeline.D.stages = {}; __siegeline.startBattle("r1s1", ["torchbow"]); });
await page.waitForSelector(".hud .weapon", { timeout: 30000 }); await G(() => { __siegeline.battle.endTutor(true); __siegeline.setSpeed(8); });
await page.waitForSelector(".result", { timeout: 180000 }); await G(() => __siegeline.setSpeed(1)); await sl(3000); await shot("10-defeat-with-trait-tip");
await browser.close();
if (errs.length) { console.log("PAGE ERRORS:\n" + errs.join("\n")); process.exit(1); }
