// List the atlas json files that exist, so the game never probes for missing pages.
import { readdirSync, writeFileSync } from "node:fs";
const names = readdirSync("public/assets").filter((f) => f.endsWith(".json") && !["worldmap.json", "atlases.json"].includes(f)).map((f) => f.slice(0, -5)).sort();
writeFileSync("public/assets/atlases.json", JSON.stringify(names));
console.log("atlases:", names.join(", "));
