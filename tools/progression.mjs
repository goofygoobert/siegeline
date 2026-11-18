// How long does region 1 take? Simulates a player going through the region: the intended crew, retrying losses,
// spending doubloons on upgrades as they come (crew first, then fort and cannon), then replaying for missing stars.
// Prints battles and minutes to clear the region and to 100% (every star), for a few skill levels.
// usage: node tools/progression.mjs [runs=6] [extraMode]   (extraMode=heroic also plays the heroic stages)
import { loadContent } from "./content_node.mjs";
import { createBattle, step, stars as starCount } from "../src/sim/battle.js";
import { makeBot } from "../src/sim/bot.js";
import { upgradeCost } from "../src/sim/stats.js";
import { kit, ROSTER, tideOf } from "./loadouts.mjs";

const C = loadContent(), G = C.game, RUNS = +(process.argv[2] || 6), OVERHEAD = 35;   // seconds per battle spent in menus
const stages = C.stages;
function playOnce(k, D, skill, seed, st = stages[k]) {
  const crew = ROSTER.stages[k].right.slice(0, st.slots || 5);
  const lv = {}; for (const u of crew) lv[u] = D.lv[u] || 1;
  const prog = { unitLevels: lv, keep: D.keep, ballista: D.ballista, energyMax: D.emax, energyRegen: D.ereg, hero: D.hero, abilities: { ember_rain: D.ab, rally: D.ab }, skills: {} };
  const kt = st.tideOf ? kit(7) : kit(k);
  const B = createBattle(C, { ...st, available: crew, ...kt, hero: kt.hero && !st.noCaptain }, prog, seed); const bot = makeBot({ skill });
  while (!B.result && B.t < 900) { bot(B); step(B); B.events.length = 0; }
  const win = B.result === "win";
  return { win, t: B.t, got: win ? [true, B.keep.hp >= B.keep.max * G.stars.keepHp, B.endT - B.heldT <= st.par] : [false, false, false], kills: B.stats.kills };
}
function spend(D, crew) {
  // cheapest useful upgrade first, repeatedly: crew in the current loadout, the fort, the cannon
  for (let guard = 0; guard < 50; guard++) {
    const opts = [];
    for (const u of crew) if ((D.lv[u] || 1) < 10) opts.push([upgradeCost("unit", D.lv[u] || 1, G), () => (D.lv[u] = (D.lv[u] || 1) + 1)]);
    if (D.keep < 10) opts.push([upgradeCost("keep", D.keep, G), () => D.keep++]);
    if (D.ballista < 10) opts.push([upgradeCost("ballista", D.ballista, G), () => D.ballista++]);
    opts.sort((a, b) => a[0] - b[0]);
    if (!opts.length || opts[0][0] > D.marks) return;
    D.marks -= opts[0][0]; opts[0][1]();
  }
}
function journey(skill, seed0, stageList = stages) {
  const D = { marks: 0, lv: {}, keep: 1, ballista: 1, emax: 1, ereg: 1, hero: 1, ab: 1 };
  const rec = stageList.map(() => ({ stars: [false, false, false], clears: 0 }));
  let battles = 0, secs = 0, clearAt = null, seed = seed0;
  const play = (k) => {
    const st = stageList[k], r = playOnce(stages.indexOf(st) >= 0 ? stages.indexOf(st) : k, D, skill, seed++, st); battles++; secs += r.t + OVERHEAD;
    const R = rec[k];
    if (r.win) {
      let ns = 0; for (let i = 0; i < 3; i++) if (r.got[i] && !R.stars[i]) { R.stars[i] = true; ns++; }
      D.marks += (R.clears === 0 ? st.reward : Math.round(st.reward * G.rewards.replayFraction)) + ns * G.rewards.perNewStar; R.clears++;
    } else D.marks += Math.round(Math.min(40, r.kills * 2));
    spend(D, ROSTER.stages[Math.min(k, ROSTER.stages.length - 1)].right);
    return r.win;
  };
  for (let k = 0; k < stageList.length; k++) { let n = 0; while (!play(k) && n++ < 40); }
  clearAt = { battles, mins: secs / 60 };
  for (let pass = 0; pass < 60 && rec.some((r) => r.stars.some((s) => !s)); pass++) for (let k = 0; k < stageList.length; k++) if (rec[k].stars.some((s) => !s)) play(k);
  const full = rec.every((r) => r.stars.every(Boolean));
  const starsAt = { battles, mins: secs / 60, full };
  // Black Tide: every stage again, stronger with its twist, until its crown is won
  let crowns = 0;
  for (let k = 0; k < stages.length; k++) {
    const st = tideOf(stages[k]);
    for (let n = 0; n < 40; n++) {
      const r = playOnce(k, D, skill, seed++, st); battles++; secs += r.t + OVERHEAD;
      if (r.win) { D.marks += st.reward; crowns++; spend(D, ROSTER.stages[k].right); break; }
      D.marks += Math.round(Math.min(40, 10 + r.kills * 2)); spend(D, ROSTER.stages[k].right);
      // between tide attempts a player replays earlier stages for doubloons
      const farm = playOnce(k, D, skill, seed++); battles++; secs += farm.t + OVERHEAD; if (farm.win) D.marks += Math.round(stages[k].reward * G.rewards.replayFraction);
    }
  }
  return { clearAt, starsAt, all: { battles, mins: secs / 60, full: full && crowns === stages.length }, crowns, lv: D.lv, keep: D.keep };
}
for (const [name, skill] of [["sloppy", 0.35], ["average", 0.6], ["sharp", 0.9]]) {
  const rs = Array.from({ length: RUNS }, (_, i) => journey(skill, 1000 + i * 99991));
  const avg = (f) => rs.reduce((a, r) => a + f(r), 0) / rs.length;
  console.log(`${name.padEnd(8)} region clear: ${avg((r) => r.clearAt.battles).toFixed(0)} battles, ${avg((r) => r.clearAt.mins).toFixed(0)} min | all stars: ${avg((r) => r.starsAt.mins).toFixed(0)} min | 100% (stars + ${stages.length} crowns): ${avg((r) => r.all.battles).toFixed(0)} battles, ${(avg((r) => r.all.mins) / 60).toFixed(1)} h (${rs.filter((r) => r.all.full).length}/${RUNS} reached it, crowns avg ${avg((r) => r.crowns).toFixed(1)}) | end levels: crew ~${avg((r) => Object.values(r.lv).reduce((a, b) => a + b, 0) / Math.max(1, Object.keys(r.lv).length)).toFixed(1)}, fort ${avg((r) => r.keep).toFixed(1)}`);
}
