// Full play-through with scripted touches: first launch -> tutorial -> every stage -> boss, buying upgrades
// after losses, then save tests (reload, export/import, damaged save). Exit code 0 only if everything passes.
// Usage: node tools/playthrough.mjs [baseUrl] [shotsDir]
import puppeteer from "puppeteer-core";
import { mkdirSync, existsSync, rmSync } from "node:fs";
import os from "node:os";

const base = (process.argv[2] || "http://127.0.0.1:5194/").replace(/\/?$/, "/");
const out = process.argv[3] || "docs/shots/playthrough";
rmSync(out, { recursive: true, force: true }); mkdirSync(out, { recursive: true });
if (os.freemem() / 1048576 < 450 && !process.env.CI) { console.error("low memory, not starting Chrome"); process.exit(2); }
const chrome = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium-browser"].find((p) => existsSync(p));
const browser = await puppeteer.launch({ executablePath: chrome, headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--mute-audio", `--user-data-dir=${process.env.TMPDIR || "/tmp"}/pt-chrome-${Date.now()}`] });
const page = await browser.newPage();
await page.setViewport({ width: 844, height: 390, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
const problems = [], log = (...a) => console.log(...a);
page.on("pageerror", (e) => problems.push("page error: " + e.message));
page.on("console", (m) => { if (m.type() === "error" && !/favicon|404/.test(m.text())) problems.push("console error: " + m.text()); });
page.on("requestfailed", (r) => problems.push("request failed: " + r.url()));
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
let shotN = 0;
const shot = async (name) => { await page.screenshot({ path: `${out}/${String(++shotN).padStart(2, "0")}-${name}.png` }); };
async function tapEl(el) { await el.evaluate((e) => e.scrollIntoView({ block: "nearest" })); const b = await el.boundingBox(); if (!b) throw new Error("element not visible"); await page.touchscreen.tap(b.x + b.width / 2, b.y + b.height / 2); await sl(250); }
async function tapText(sel, text, timeout = 8000, exact = false) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) {
    const els = await page.$$(sel);
    for (const el of els) { const t = (await el.evaluate((e) => e.textContent)).trim(); if (t && (exact ? t === text : t.includes(text)) && await el.boundingBox()) { await tapEl(el); return true; } }
    await sl(200);
  }
  throw new Error(`dead end: no "${text}" button (${sel})`);
}
async function waitFor(sel, timeout = 15000) { const el = await page.waitForSelector(sel, { timeout, visible: true }); return el; }
const G = (f, ...a) => page.evaluate(f, ...a);

let this_shot_rain = false;
async function playStage(id) {
  await waitFor(".hud .weapon", 30000);
  await G(() => { __siegeline.setSpeed(1); __siegeline.autoplay(0.7); });
  // follow any tutorial prompts with real touches (the test player plays between prompts)
  const t0 = Date.now();
  while (Date.now() - t0 < 90000) {
    const tut = await page.$(".tut"); const text = tut ? await tut.evaluate((e) => e.textContent) : "";
    const hasTutor = await G(() => !!(__siegeline.battle && __siegeline.battle.tutor));
    if (!hasTutor) break;
    if (/Ashguard card/.test(text)) { await shot(`${id}-tutorial-send`); await tapEl(await page.$('.ucard[data-id="ashguard"]')); }
    else if (/ballista/.test(text)) {
      await shot(`${id}-tutorial-aim`);
      const b = await (await page.$(".weapon")).boundingBox(); const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
      await page.mouse.move(cx, cy); await page.mouse.down(); await page.mouse.move(cx - 70, cy + 45, { steps: 8 }); await sl(250); await page.mouse.up();
    } else if (/Ember Rain/.test(text)) {
      if (!this_shot_rain) { await shot(`${id}-tutorial-ability`); this_shot_rain = true; }
      await tapEl(await page.$('.abil[data-id="ember_rain"]')); await page.touchscreen.tap(560, 230);
    } else if (/Marshal/.test(text)) { await shot(`${id}-tutorial-hero`); await tapEl(await page.$(".herobtn")); }
    await sl(400);
  }
  // then the test player takes over at high speed
  await G(() => { __siegeline.autoplay(0.7); __siegeline.setSpeed(6); });
  let mid = false;
  const t1 = Date.now();
  while (Date.now() - t1 < 240000) {
    if (!mid && Date.now() - t1 > 6000) { mid = true; await G(() => __siegeline.setSpeed(1)); await sl(500); await shot(`${id}-battle`); await G(() => __siegeline.setSpeed(6)); }
    const res = await page.$(".result"); if (res) break;
    await sl(500);
  }
  await G(() => { __siegeline.autoplay(null); __siegeline.setSpeed(1); });
  await waitFor(".result", 20000); await sl(2600);
  const win = !!(await page.$(".result.win"));
  await shot(`${id}-${win ? "win" : "loss"}`);
  return win;
}

async function buyUpgrades() {
  for (const tab of ["Units", "Keep & Ballista", "Hero & Powers"]) {
    await tapText(".tab", tab);
    for (let i = 0; i < 12; i++) { const b = await page.$(".upbtn.primary"); if (!b) break; await tapEl(b); }
  }
  await shot("armoury-after-buying");
}

try {
  await page.goto(base + "?test=1", { waitUntil: "networkidle0" });
  await G(() => localStorage.clear()); await page.reload({ waitUntil: "networkidle0" });
  await waitFor(".logo"); await shot("title");
  await tapText("button", "Play");
  await waitFor(".map"); await sl(500); await shot("worldmap");
  await tapEl(await page.$(".pin:not(.locked)"));
  await waitFor(".node"); await sl(600); await shot("region");
  const stages = ["r1s1", "r1s2", "r1s3", "r1s4", "r1s5", "r1boss"];
  const results = [];
  for (let i = 0; i < stages.length; i++) {
    const id = stages[i];
    let tries = 0, won = false;
    while (!won && tries < 4) {
      tries++;
      if (!(await page.$(".hud"))) {        // start from the region screen
        if (!(await page.$(".sheet"))) { await sl(600); const nodes = await page.$$(".screen:not(.out) .node"); await tapEl(nodes[i]); }
        await waitFor(".sheet"); await tapText(".sheet button", "Fight");
      }
      won = await playStage(id);
      results.push(`${id} try ${tries}: ${won ? "win" : "loss"}`); log(results.at(-1));
      if (!won) {
        await tapText(".result button", "Upgrade"); await waitFor(".list"); await buyUpgrades();
        await tapEl(await page.$('button[aria-label="Back"]')); await waitFor(".node");
      } else if (i < stages.length - 1) {
        // reload mid-region once (after stage 2) to prove progress survives a restart
        if (id === "r1s2") {
          await page.reload({ waitUntil: "networkidle0" }); await waitFor(".logo");
          const cont = await G(() => [...document.querySelectorAll("button")].some((b) => b.textContent.includes("Continue")));
          if (!cont) problems.push("after reload the title did not offer Continue");
          await tapText("button", "Continue"); await waitFor(".map"); await sl(700);
          const pin = await page.$(".pin:not(.locked)"); if (!pin) throw new Error("dead end: no open region on the map after reload");
          await tapEl(pin); await waitFor(".node"); await sl(700);
          const nodes = await page.$$(".screen:not(.out) .node");
          if (!nodes[i + 1]) throw new Error("dead end: next stage node missing after reload (" + nodes.length + " nodes)");
          await tapEl(nodes[i + 1]);
          await waitFor(".sheet"); await tapText(".sheet button", "Fight");
        } else await tapText(".result button", "Next stage");
        await waitFor(".hud .weapon", 30000);
      }
    }
    if (!won) throw new Error(`could not beat ${id} in 4 tries (with upgrades between)`);
  }
  await tapText(".result button", "Continue"); await waitFor(".map"); await sl(600); await shot("region-cleared-map");
  if (!(await page.$(".announce"))) problems.push("no region-cleared announcement on the map");
  const ga = await page.$(".announce button"); if (ga) await tapEl(ga);
  const D = await G(() => __siegeline.D);
  log(`marks ${D.marks}, stars ${Object.values(D.stages).map((s) => s.stars.filter(Boolean).length).join(",")}, units ${D.unlocked.units.length}`);
  if (D.unlocked.units.length !== 6) problems.push(`expected 6 units unlocked, got ${D.unlocked.units.length}`);

  // ---- save tests
  // export via the settings UI
  await tapEl(await page.$('button[aria-label="Settings"]')); await tapText(".panel button", "Export save");
  const code = await (await waitFor(".panel textarea")).evaluate((e) => e.value);
  if (!/^SGL\d+:/.test(code)) problems.push("export code missing");
  await shot("settings-export");
  // wipe through the UI, then import the code back
  await tapText(".panel button", "Reset progress"); await tapText(".panel button", "Delete my progress"); await waitFor(".logo");
  const wiped = await G(() => __siegeline.D.marks === 0 && Object.keys(__siegeline.D.stages).length === 0);
  if (!wiped) problems.push("reset did not clear progress");
  await sl(800); await tapEl(await page.$('button[aria-label="Settings"]')); await sl(500);
  for (let k = 0; k < 3 && !(await page.$(".panel textarea")); k++) { await tapText(".panel button", "Import save"); await sl(400); }
  await (await waitFor(".panel textarea")).type(code.slice(0, 40)); await page.$eval(".panel textarea", (e, c) => (e.value = c), code);
  await tapText(".panel button", "Import", 8000, true); await waitFor(".map");
  const back = await G(() => __siegeline.D.unlocked.units.length);
  if (back !== 6) problems.push("import did not restore progress");
  // a bad code must be refused politely
  await sl(800); await tapEl(await page.$('button[aria-label="Settings"]')); await sl(500);
  for (let k = 0; k < 3 && !(await page.$(".panel textarea")); k++) { await tapText(".panel button", "Import save"); await sl(400); }
  await page.$eval(".panel textarea", (e) => (e.value = "SGL2:not-a-real-save")); await tapText(".panel button", "Import", 8000, true); await sl(300);
  const toast = await G(() => document.querySelector(".toast")?.textContent || "");
  if (!/valid/.test(toast)) problems.push("bad import code was not refused with a message");
  await shot("bad-import-refused");
  // damaged save: corrupt the main slot, expect the backup to be restored
  await G(() => __siegeline.save());
  await G(() => { __siegeline.save(); localStorage.setItem("siegeline.save", '{"v":2,"sum":"x","data":"{broken'); });
  await page.reload({ waitUntil: "networkidle0" }); await waitFor(".logo"); await sl(400);
  const restored = await G(() => __siegeline.D.unlocked.units.length === 6);
  const msg = await G(() => document.querySelector(".toast")?.textContent || "");
  await shot("damaged-save-restored");
  if (!restored) problems.push("damaged save: backup not restored");
  if (!/Restored/.test(msg)) problems.push("damaged save: no message shown");
  // both slots damaged: fresh start, no crash
  await G(() => { localStorage.setItem("siegeline.save", "garbage"); localStorage.setItem("siegeline.save.bak", "garbage"); });
  await page.reload({ waitUntil: "networkidle0" }); await waitFor(".logo");
  const fresh = await G(() => __siegeline.D.marks === 0);
  if (!fresh) problems.push("both slots damaged: did not start fresh");
  log("save tests done");
  log(results.join("\n"));
} catch (e) {
  problems.push("FAILED: " + e.message);
  await shot("failure").catch(() => {});
}
await browser.close();
if (problems.length) { console.log("PROBLEMS:\n- " + [...new Set(problems)].join("\n- ")); process.exit(1); }
console.log("PLAY-THROUGH PASSED");
