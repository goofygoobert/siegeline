// Load game content from data/ in Node (the browser loads the same files via import).
import { readFileSync } from "node:fs";
const root = new URL("../data/", import.meta.url);
const j = (p) => JSON.parse(readFileSync(new URL(p, root), "utf8"));
export function loadContent() {
  const stagesR1 = j("stages/r1.json");
  return { units: j("units.json"), enemies: j("enemies.json"), game: j("game.json"), regions: j("regions.json"),
           stages: stagesR1.stages, tutorials: stagesR1.tutorials };
}
