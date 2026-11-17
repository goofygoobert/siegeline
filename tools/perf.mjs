// Performance probe: first load on a throttled phone connection, frame times in the busiest battle,
// worst-frame hitches, and JS heap over a long session. Usage: node tools/perf.mjs [baseUrl] [label]
import puppeteer from "puppeteer-core";
import os from "node:os";
const base = (process.argv[2] || "http://127.0.0.1:5194/").replace(/\/?$/, "/");
const label = process.argv[3] || "run";
if (os.freemem() / 1048576 < 450) { console.error("low memory, not starting Chrome"); process.exit(2); }
const browser = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--mute-audio", "--enable-precise-memory-info", "--user-data-dir=" + (process.env.TMPDIR || "/tmp") + "/perf-chrome-" + Date.now()] });
const page = await browser.newPage();
await page.setViewport({ width: 844, height: 390, deviceScaleFactor: 2, isMobile: true, hasTouch: true, isLandscape: true });
const cdp = await page.createCDPSession();
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
const out = { label };

// 1) first load: "good 4G" (9 Mbps down, 1.5 up, 60 ms RTT), cold cache
await cdp.send("Network.enable");
await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 60, downloadThroughput: 9e6 / 8, uploadThroughput: 1.5e6 / 8 });
await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
let bytes = 0; cdp.on("Network.loadingFinished", (e) => (bytes += e.encodedDataLength));
const t0 = Date.now();
await page.goto(base + "?test=1", { waitUntil: "domcontentloaded" });
await page.waitForSelector(".logo", { visible: true });
await page.waitForFunction(() => { const b = document.querySelector(".bgimg"); return b && b.style.backgroundImage.includes("url"); }, { timeout: 30000 });
out.firstLoadMs = Date.now() - t0; out.firstLoadKB = Math.round(bytes / 1024);
// time to enter the first battle from the title (battle assets over the same connection)
bytes = 0; const t1 = Date.now();
await page.evaluate(() => __siegeline.startBattle("r1s1"));
await page.waitForSelector(".hud .weapon", { visible: true, timeout: 60000 });
out.firstBattleLoadMs = Date.now() - t1; out.firstBattleKB = Math.round(bytes / 1024);
await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
await cdp.send("Network.setCacheDisabled", { cacheDisabled: false });

// 2) busiest battle: boss stage, everything unlocked and levelled, bot playing, late in the fight
await page.evaluate(() => {
  const D = __siegeline.D; D.unlocked.units = ["ashguard", "torchbow", "cinder_runner", "maulwright", "bellringer", "lamplighter"];
  D.unlocked.hero = true; D.unlocked.abilities = ["ember_rain", "rally"]; for (const u of D.unlocked.units) D.unitLevels[u] = 6;
});
await page.evaluate(() => __siegeline.startBattle("r1boss"));
await page.waitForSelector(".hud .weapon", { visible: true, timeout: 60000 });
await page.evaluate(() => { __siegeline.autoplay(0.8); __siegeline.setSpeed(3);
  // stress: unlimited embers and no card cooldowns, so the field fills far beyond normal play
  window.__stress = setInterval(() => { const b = __siegeline.battle; if (!b) return; const B = b.B; B.energyMax = 2000; B.energy = 2000; for (const c of B.cards) c.cd = 0; if (B.loop) B.loop.timer = Math.min(B.loop.timer, 0.4); }, 300); });
await sl(12000);                                   // let both armies fill the field
await page.evaluate(() => __siegeline.setSpeed(1));
const sample = await page.evaluate(() => new Promise((res) => {
  const ft = []; let last = performance.now(); const end = last + 15000; let maxEnts = 0;
  function f(now) { ft.push(now - last); last = now; const B = __siegeline.battle && __siegeline.battle.B; if (B) maxEnts = Math.max(maxEnts, B.ents.filter((e) => e.alive).length + B.projs.filter((p) => p.alive).length);
    if (now < end) requestAnimationFrame(f); else res({ ft, maxEnts, q: __siegeline.R.quality, work: (__siegeline.battle && __siegeline.battle.work || []).slice(), sim: (__siegeline.battle && __siegeline.battle.simWork || []).slice() }); }
  requestAnimationFrame(f);
}));
const ft = sample.ft.slice(5).sort((a, b) => a - b);
out.busy = { frames: ft.length, avgFps: +(1000 / (ft.reduce((a, b) => a + b, 0) / ft.length)).toFixed(1),
  p50ms: +ft[Math.floor(ft.length * 0.5)].toFixed(1), p95ms: +ft[Math.floor(ft.length * 0.95)].toFixed(1), worstMs: +ft.at(-1).toFixed(1),
  over33ms: ft.filter((x) => x > 33.4).length, liveObjects: sample.maxEnts, qualityLevel: sample.q };
const wk = sample.work.sort((a, b) => a - b);
const sm = sample.sim; out.busy.simPerFrameAvgMs = sm.length ? +(sm.reduce((a, b) => a + b, 0) / sm.length).toFixed(2) : null;
out.busy.workPerFrame = wk.length ? { avgMs: +(wk.reduce((a, b) => a + b, 0) / wk.length).toFixed(2), p95Ms: +wk[Math.floor(wk.length * 0.95)].toFixed(2), worstMs: +wk.at(-1).toFixed(2) } : null;

// 3) memory over a long session: replay battles back to back at high speed, sample the heap
console.log(JSON.stringify(out, null, 1)); if (process.argv[4] === "quick") { await browser.close(); process.exit(0); }
const heap = [];
const t2 = Date.now();
await page.evaluate(() => { __siegeline.setSpeed(8); });
while (Date.now() - t2 < 240000) {
  const m = await page.evaluate(() => { const B = __siegeline.battle; if (!B) __siegeline.startBattle(["r1s3", "r1s5", "r1boss"][Math.floor(Math.random() * 3)]); return performance.memory ? performance.memory.usedJSHeapSize : 0; });
  heap.push(Math.round(m / 1048576 * 10) / 10);
  const res = await page.$(".result"); if (res) await page.evaluate(() => __siegeline.startBattle(["r1s3", "r1s5", "r1boss"][Math.floor(Math.random() * 3)]));
  await sl(10000);
}
const simMinutes = await page.evaluate(() => __siegeline.D.playTime / 60);
out.memory = { samplesMB: heap, first: heap[1], last: heap.at(-1), max: Math.max(...heap), simulatedMinutes: +simMinutes.toFixed(1) };
console.log(JSON.stringify(out, null, 1));
await browser.close();
