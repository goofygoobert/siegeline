// Phone-sized screenshots of every screen + a scripted battle, using the system Chrome.
// Usage: node tools/shots.mjs [baseUrl] [outDir]   (default http://127.0.0.1:5194/  docs/shots)
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";
import os from "node:os";

const base = process.argv[2] || "http://127.0.0.1:5194/";
const out = process.argv[3] || "docs/shots";
const VW = +(process.env.VW || 844), VH = +(process.env.VH || 390);
mkdirSync(out, { recursive: true });
const free = os.freemem() / 1048576;
if (free < 500) { console.error(`only ${free.toFixed(0)} MB free; not starting Chrome`); process.exit(2); }

const browser = await puppeteer.launch({
  executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--mute-audio", `--user-data-dir=${process.env.TMPDIR || "/tmp"}/shots-chrome-${Date.now()}`, "--js-flags=--max-old-space-size=256"],
});
const page = await browser.newPage();
await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
const errors = [];
page.on("pageerror", (e) => { errors.push("pageerror: " + e.message); console.log("PAGEERROR", e.message); });
page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
const shot = async (name) => { await new Promise((r) => setTimeout(r, 450)); await page.screenshot({ path: `${out}/${name}.png` }); console.log("shot", name); };
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
const G = (expr) => page.evaluate(expr);

await page.goto(base, { waitUntil: "networkidle0" });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: "networkidle0" });
await shot("01-title");
await G("__siegeline.worldMap()"); await sl(600); await shot("02-worldmap");
await G("__siegeline.regionScreen()"); await sl(700); await shot("03-region-sheet");
await G("__siegeline.armoury()"); await sl(500); await shot("04-armoury");
await G("__siegeline.openSettings()"); await sl(300); await shot("05-settings");
// battle: stage 1 with tutorial
await G("__siegeline.startBattle('r1s1')"); await sl(2500); await shot("06-battle-tutorial");
// follow the tutorial: tap the first card, then aim the ballista by dragging
const card = await page.$(".ucard"); if (card) { const b = await card.boundingBox(); await page.touchscreen.tap(b.x + b.width / 2, b.y + b.height / 2); }
await sl(4500);
const w = await page.$(".weapon"); if (w) {
  const b = await w.boundingBox(); const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
  await page.mouse.move(cx, cy); await page.mouse.down(); await page.mouse.move(cx - 60, cy + 40, { steps: 6 }); await sl(300); await shot("07-aiming"); await page.mouse.up();
}
// let the bot play to see a busy battle
await G(`(() => { const S = __siegeline; const b = S.battle; if (!b) return; b.tutor && b.endTutor(true);
  const sendAll = setInterval(() => { const bt = S.battle; if (!bt) return clearInterval(sendAll); for (const c of bt.B.cards) if (bt.B.energy >= c.stats.cost && c.cd <= 0) { bt.send(c.id, bt.cardEls[0]); break; } }, 700); })()`);
await sl(16000); await shot("08-battle-busy");
await sl(14000); await shot("09-battle-later");
console.log(errors.length ? "ERRORS:\n" + errors.join("\n") : "no page errors");
await browser.close();
