// Shared by the tests and balance tools: what the player has on each stage (crew, Captain, powers) when playing in order.
import { readFileSync } from "node:fs";
export const ROSTER = JSON.parse(readFileSync(new URL("../data/design/roster.json", import.meta.url)));
/** Captain and powers unlocked by the time you reach stage index k (Broadside after 1, Captain after 2, Shanty after 4). */
export function kit(k) { return { hero: k >= 2, abilities: [...(k >= 1 ? ["ember_rain"] : []), ...(k >= 4 ? ["rally"] : [])] }; }
/** A stage ready to fight with a given loadout. */
export function withLoadout(st, k, crew) { return { ...st, available: crew, ...kit(k) }; }
export const right = (k) => ROSTER.stages[k].right;
export const wrong = (k) => ROSTER.stages[k].wrongIds;
/** The Black Tide version of a stage: stronger, with its twist; "noCaptain" and "fewerPlaces" are applied here. */
export function tideOf(st) {
  const t = st.tide, mods = t.mods;
  return { ...st, power: st.power * t.power, bossPower: st.bossPower ? st.bossPower * t.power : undefined, mods, reward: t.reward, tideOf: st.id,
    slots: (st.slots || 5) - (mods.includes("fewerPlaces") ? 1 : 0), noCaptain: mods.includes("noCaptain") };
}
