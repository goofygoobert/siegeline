// Build the counter table and stage table in docs/design/strategy.md from data, and run the design checks.
// Source today: data/design/roster.json (design data). Part 3 moves the same fields into data/units.json / enemies.json.
// Usage: node tools/gen_counters.mjs        exit code 1 if a design check fails.
import { readFileSync, writeFileSync } from "node:fs";
const R = JSON.parse(readFileSync("data/design/roster.json", "utf8"));
const cell = (c, e) => {
  const s = e.traits.some((t) => c.strong.includes(t)), w = e.traits.some((t) => c.weak.includes(t));
  return s && !w ? "strong" : w && !s ? "weak" : "even";
};
const mark = { strong: "**+**", even: "·", weak: "−" };
const table = (crew, foes) => {
  const L = ["| Crew \\ Enemy | " + foes.map((e) => e.name).join(" | ") + " |", "|---|" + foes.map(() => ":-:").join("|") + "|"];
  for (const c of crew) L.push(`| **${c.name}** | ` + foes.map((e) => mark[cell(c, e)]).join(" | ") + " |");
  return L.join("\n");
};
const r1c = R.crew.filter((c) => c.region === 1), r1e = R.enemies.filter((e) => e.region === 1);
const problems = [];
// checks
for (const [id, t] of Object.entries(R.traits)) {
  if (id === "plain") continue;
  const ans = R.crew.filter((c) => c.strong.includes(id));
  if (ans.length < 2) problems.push(`trait ${t.name} has ${ans.length} answer(s), needs 2+`);
}
for (const id of new Set(r1e.flatMap((e) => e.traits))) {
  if (id === "plain") continue;
  const ans = r1c.filter((c) => c.strong.includes(id));
  if (ans.length < 2) problems.push(`region 1 trait ${id} has ${ans.length} region-1 answer(s), needs 2+`);
}
for (const c of R.crew) {
  if (c.weak.length < 2) problems.push(`${c.name} has fewer than 2 weaknesses`);
  if (c.strong.some((t) => c.weak.includes(t))) problems.push(`${c.name} is both strong and weak to one trait`);
  const share = R.enemies.filter((e) => cell(c, e) === "strong").length / R.enemies.length;
  if (share > 0.5) problems.push(`${c.name} is strong against ${(share * 100).toFixed(0)}% of enemies (max 50%)`);
  if (share === 0) problems.push(`${c.name} is strong against nothing`);
}
for (const s of R.stages) {
  for (const id of s.right) if (!R.crew.find((c) => c.id === id && c.region === 1)) problems.push(`stage ${s.n}: ${id} is not a region 1 crew member`);
  if (s.right.length > s.slots) problems.push(`stage ${s.n}: intended loadout larger than the slots`);
}
const used = new Set(R.stages.flatMap((s) => s.right));
// crew bought in the Tavern are optional by design (no stage needs a purchase), so only free crew must appear in an
// intended loadout. "Nobody is a must-pick" is measured on play, not on this list: tools/strategy_proof.mjs checks every
// crew member is in 10-90% of winning loadouts.
for (const c of r1c) if (!used.has(c.id) && (c.recruit || {}).how !== "buy") problems.push(`${c.name} is in no intended loadout in region 1`);
const nm = (id) => (R.crew.find((c) => c.id === id) || R.enemies.find((e) => e.id === id) || { name: id }).name;
const stageTable = ["| # | Stage | Slots | New idea, taught by playing | You'll face | A right loadout | A sensible wrong one |", "|---|---|:-:|---|---|---|---|",
  ...R.stages.map((s) => `| ${s.n} | ${s.name} | ${s.slots} | ${s.teaches} | ${s.foes.map(nm).join(", ")} | ${s.right.map(nm).join(", ")} | ${s.wrong} |`)].join("\n");
const traitTable = ["| Trait | Icon | Read it from the silhouette | Rule | Answers (from the data) |", "|---|---|---|---|---|",
  ...Object.entries(R.traits).filter(([id]) => id !== "plain").map(([id, t]) => `| **${t.name}** | ${t.icon} | ${t.read} | ${t.rule} | ${R.crew.filter((c) => c.strong.includes(id)).map((c) => c.name).join(", ")} |`)].join("\n");
const crewTable = ["| Crew | From | Job | Weakness |", "|---|:-:|---|---|", ...R.crew.map((c) => `| **${c.name}** | R${c.region} | ${c.job} | ${c.weakness} |`)].join("\n");
const out = { COUNTERS_R1: table(r1c, r1e), COUNTERS_ALL: table(R.crew, R.enemies), STAGES: stageTable, TRAITS: traitTable, CREW: crewTable,
  CHECKS: problems.length ? problems.map((p) => "- FAIL: " + p).join("\n") : `- All design checks pass: every trait has 2+ answers (and 2+ inside region 1 for region 1 traits), every crew member has 2+ weaknesses, nobody is strong against more than half the enemies, every free region 1 crew member is in at least one intended loadout (Tavern crew are optional; must-picks are checked on play by tools/strategy_proof.mjs).` };
let md = readFileSync("docs/design/strategy.md", "utf8");
for (const [k, v] of Object.entries(out)) {
  const a = `<!-- GEN:${k} -->`, b = `<!-- /GEN:${k} -->`; const i = md.indexOf(a), j = md.indexOf(b);
  if (i < 0 || j < 0) { console.error("marker missing", k); process.exit(1); }
  md = md.slice(0, i + a.length) + "\n" + v + "\n" + md.slice(j);
}
writeFileSync("docs/design/strategy.md", md);
console.log(problems.length ? "DESIGN CHECKS FAILED:\n" + problems.join("\n") : "strategy tables written, design checks pass");
process.exit(problems.length ? 1 : 0);
