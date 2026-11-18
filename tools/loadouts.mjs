// Shared by the tests and balance tools: what the player has on each stage (crew, Captain, powers) when playing in order.
import { readFileSync } from "node:fs";
export const ROSTER = JSON.parse(readFileSync(new URL("../data/design/roster.json", import.meta.url)));
/** Captain and powers unlocked by the time you reach stage index k (Broadside after 1, Captain after 2, Shanty after 4). */
export function kit(k) { return { hero: k >= 2, abilities: [...(k >= 1 ? ["ember_rain"] : []), ...(k >= 4 ? ["rally"] : [])] }; }
/** A stage ready to fight with a given loadout. */
export function withLoadout(st, k, crew) { return { ...st, available: crew, ...kit(k) }; }
export const right = (k) => ROSTER.stages[k].right;
export const wrong = (k) => ROSTER.stages[k].wrongIds;
