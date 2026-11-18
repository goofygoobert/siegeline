// Validate every data file against its schema plus cross-references. Fails the build on any problem.
import Ajv from "ajv";
import { loadContent } from "./content_node.mjs";
import { readFileSync } from "node:fs";
const C = loadContent();
const ajv = new Ajv({ allErrors: true });
const num = { type: "number", minimum: 0 };
const schemas = {
  unit: { type: "object", required: ["id", "name", "role", "region", "cost", "cooldown", "hp", "dmg", "rate", "range", "speed", "size", "traits", "counter", "tiers"],
    properties: { id: { type: "string", pattern: "^[a-z_]+$" }, cost: num, cooldown: num, hp: { type: "number", exclusiveMinimum: 0 }, dmg: num, rate: { type: "number", exclusiveMinimum: 0 }, range: num, speed: num, size: { type: "number", exclusiveMinimum: 0 },
      tiers: { type: "object", required: ["5", "10"] }, traits: { type: "object" } } },
  enemy: { type: "object", required: ["id", "name", "faction", "hp", "dmg", "rate", "range", "speed", "size", "traits", "bounty"],
    properties: { id: { type: "string", pattern: "^[a-z_]+$" }, faction: { enum: ["hollow", "tithe", "mawborn"] }, hp: { type: "number", exclusiveMinimum: 0 }, bounty: { type: "number", minimum: 0 } } },
  stage: { type: "object", required: ["id", "name", "region", "bg", "enemyCastleHp", "par", "reward", "unlocks", "waves"],
    properties: { waves: { type: "array", items: { type: "object", required: ["t", "id", "n", "gap"], properties: { t: num, n: { type: "integer", minimum: 1 }, gap: num } } },
      loop: { type: "object", required: ["start", "every", "pool", "min"] }, par: { type: "number", minimum: 30 }, reward: num } },
};
const v = Object.fromEntries(Object.entries(schemas).map(([k, s]) => [k, ajv.compile(s)]));
let errs = [];
const check = (kind, obj) => { if (!v[kind](obj)) errs.push(`${kind} ${obj.id}: ${ajv.errorsText(v[kind].errors)}`); };
C.units.units.forEach((u) => check("unit", u));
C.enemies.enemies.forEach((e) => check("enemy", e));
C.stages.forEach((s) => check("stage", s));
const uid = new Set(C.units.units.map((u) => u.id)), eid = new Set(C.enemies.enemies.map((e) => e.id));
if (uid.size !== C.units.units.length) errs.push("duplicate unit id");
if (C.units.units.length < 20) errs.push("expected ~20 units for the full game");
for (const s of C.stages) {
  for (const w of s.waves) if (!eid.has(w.id)) errs.push(`${s.id}: unknown enemy ${w.id}`);
  for (const [id] of (s.loop ? s.loop.pool : [])) if (!eid.has(id)) errs.push(`${s.id}: unknown loop enemy ${id}`);
  for (const u of s.unlocks) if (!uid.has(u) && u !== "hero" && !C.game.abilities[u]) errs.push(`${s.id}: unknown unlock ${u}`);
  for (const u of s.available || []) if (!uid.has(u)) errs.push(`${s.id}: unknown unit ${u}`);
  if (s.boss && !eid.has(s.boss)) errs.push(`${s.id}: unknown boss`);
  if (s.tutorial && !C.tutorials[s.tutorial]) errs.push(`${s.id}: unknown tutorial`);
}
const r1 = C.regions.regions.find((r) => r.id === "r1");
for (const id of r1.stages) if (!C.stages.find((s) => s.id === id)) errs.push(`r1 lists missing stage ${id}`);
const totalStages = C.regions.regions.reduce((n, r) => n + (r.stages ? r.stages.length : r.stageCount || 0), 0);
if (totalStages < 55 || totalStages > 65) errs.push(`full game should plan ~60 stages, has ${totalStages}`);
if (errs.length) { console.error("DATA ERRORS:\n  " + errs.join("\n  ")); process.exit(1); }
console.log(`data ok: ${C.units.units.length} units, ${C.enemies.enemies.length} enemies, ${C.stages.length} stages in r1, ${totalStages} planned`);
