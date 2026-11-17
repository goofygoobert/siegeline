// Regenerate the data tables inside docs/design.md (between the GENERATED markers) from data/.
import { readFileSync, writeFileSync } from "node:fs";
import { loadContent } from "./content_node.mjs";
const C = loadContent();
const row = (a) => "| " + a.join(" | ") + " |";
const L = [];
L.push("### All player units (Lantern Wardens)", "", row(["#", "Unit", "Role", "Region", "Cost", "Cooldown s", "HP", "DMG", "Atk every s", "Range", "Speed", "Special", "Countered by", "Level 5 look", "Level 10 look"]), row(Array(15).fill("---")));
C.units.units.forEach((u, i) => L.push(row([i + 1, u.name, u.role, "r" + u.region, u.cost, u.cooldown, u.hp, u.dmg, u.rate, u.range, u.speed, Object.keys(u.traits).join(", ") || "-", u.counter, u.tiers["5"], u.tiers["10"]])));
L.push("", `Levels 1–10: +${C.units.levels.hpPerLevel * 100}% HP and +${C.units.levels.dmgPerLevel * 100}% damage per level; new look and perk at levels ${C.units.levels.tierLevels.join(" and ")}.`, "");
L.push("### All enemies", "", row(["Enemy", "Faction", "Region", "HP", "DMG", "Atk every s", "Range", "Speed", "Behaviour"]), row(Array(9).fill("---")));
for (const e of C.enemies.enemies) L.push(row([e.name + (e.boss ? " (boss)" : e.miniboss ? " (mini-boss)" : ""), e.faction, "r" + (e.region || 1), e.hp, e.dmg, e.rate, e.range, e.speed, e.desc]));
L.push("", `Elite versions: HP x${C.enemies.elite.hpMul}, damage x${C.enemies.elite.dmgMul}, speed x${C.enemies.elite.speedMul}, ember glow and 12% larger.`, "");
L.push("### Region 1 stages", "", row(["Stage", "Name", "Enemy gate HP", "Enemy power", "Par time", "First-clear marks", "Unlocks", "Scripted waves"]), row(Array(8).fill("---")));
for (const s of C.stages) L.push(row([s.id, s.name, s.winOn === "boss" ? "sealed (defeat the boss)" : s.enemyCastleHp, "x" + (s.power || 1) + (s.bossPower ? ", boss x" + s.bossPower : ""), s.par + " s", s.reward, s.unlocks.join(", ") || "-", s.waves.map((w) => `${w.t}s ${w.n}x ${w.id}${w.elite ? " (elite)" : ""}`).join("; ")]));
const md = readFileSync("docs/design.md", "utf8");
const a = md.indexOf("<!-- GENERATED -->"), b = md.indexOf("<!-- /GENERATED -->");
writeFileSync("docs/design.md", md.slice(0, a + 18) + "\n" + L.join("\n") + "\n" + md.slice(b));
console.log("tables regenerated");
