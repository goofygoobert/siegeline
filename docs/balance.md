# Balance

**Method.** `tools/balance.mjs` runs the battle simulation headless at about 3,000–4,500× real time. A scripted test player (`src/sim/bot.js`) uses only a human's inputs: sending cards, aiming the ballista with aim error, using powers and calling the hero. It plays every stage **200 times per cell** across 3 skill levels and 4 upgrade profiles, which is 14,400 battles in about 5 minutes.

**Tuning.** `tools/tune.mjs` bisects a per-stage enemy **power** factor until an average player with no upgrades hits a target win rate (stage 1 ~97% down to the boss ~30%). Power scales enemy health ×p and damage ×p^0.75. The boss has its own factor. Enemy base stats were rescaled once (×1.67 health) so that stage 5 sits at power 1.0.

**Changes made from what the runs showed**
1. First runs: every stage was won 100% even by a sloppy player with no upgrades, and the Keep was never hit. The enemies were far too weak, so I rescaled their base stats and added per-stage power.
2. Many "losses" were stalemates running to the 15-minute cap, a dull stretch for a real player. Added **escalation**: after par time the Maw spawns faster with more elites ("The Maw grows angry"), so every battle reaches a decision.
3. "Modest" upgrades gave 100% everywhere. Softened per-level gains (HP +12% → +8%, damage +9% → +7%, ember flow +1.0 → +0.6/level, store +20 → +15).
4. The reviewer called the boss a grind. Cut her base health 30% and added a **winded** window after each sweep (+50% damage taken for 2.5 s), then re-tuned her power.
5. Starting embers 40 → 55 so the first card is affordable when the tutorial asks. First waves now arrive at 2 s.
6. Par times set to about 110% of the measured average clear time with modest upgrades. Tutorial pauses don't count.

7. **Redesign slice (cannon depth).** Long Tom now knocks monsters back further, a ball that strikes a body directly hits that monster 50% harder (not the boss), and every monster the cannon kills pays back 4 powder ("salvage"). Aim now matters more: the gap between a sloppy and a sharp player is wider than before. All stages were re-tuned with `tools/tune.mjs` to the same target win rates for an average player without upgrades; stage 1, 3 and 4 were then eased a few percent by hand for sloppy first-timers. Boss par moved 215 s → 260 s to match the measured clear time. The boss fight is longer than before for players without upgrades (about 4.5 minutes): still the weakest point of the curve.

**Final results** (after the full region roll-out; win rate; average win time and Keep health for the *average* player; 3-star rate for the average player)

Runs per cell: 100. Skill = bot reaction speed and aim error (sloppy 0.35, average 0.6, sharp 0.9). Profiles: none = all level 1; light = units 2, keep/ballista 2; modest = units 3, keep/ballista 3, ember 2/2, hero 2, powers 2; strong = units 6, keep/ballista 6, ember 4/4, hero 5, powers 5.

| Stage | Upgrades | Sloppy win | Average win | Sharp win | Avg win time (average) | Keep HP left (average) | 3-star rate (average) |
|---|---|---|---|---|---|---|---|
| r1s1 | none | 91% | 100% | 100% | 111 s (par 110) | 100% | 54% |
| r1s1 | light | 100% | 100% | 100% | 103 s (par 110) | 100% | 96% |
| r1s1 | modest | 100% | 100% | 100% | 95 s (par 110) | 100% | 100% |
| r1s1 | strong | 100% | 100% | 100% | 78 s (par 110) | 100% | 100% |
| r1s2 | none | 55% | 79% | 97% | 145 s (par 140) | 99% | 25% |
| r1s2 | light | 91% | 100% | 100% | 135 s (par 140) | 99% | 78% |
| r1s2 | modest | 100% | 100% | 100% | 119 s (par 140) | 99% | 98% |
| r1s2 | strong | 100% | 100% | 100% | 87 s (par 140) | 100% | 100% |
| r1s3 | none | 75% | 92% | 100% | 175 s (par 155) | 99% | 8% |
| r1s3 | light | 100% | 100% | 100% | 158 s (par 155) | 99% | 54% |
| r1s3 | modest | 100% | 100% | 100% | 142 s (par 155) | 100% | 96% |
| r1s3 | strong | 100% | 100% | 100% | 112 s (par 155) | 100% | 100% |
| r1s4 | none | 35% | 74% | 96% | 204 s (par 190) | 100% | 5% |
| r1s4 | light | 95% | 100% | 100% | 183 s (par 190) | 100% | 72% |
| r1s4 | modest | 100% | 100% | 100% | 169 s (par 190) | 100% | 96% |
| r1s4 | strong | 100% | 100% | 100% | 112 s (par 190) | 100% | 100% |
| r1s5 | none | 26% | 59% | 79% | 217 s (par 205) | 99% | 7% |
| r1s5 | light | 77% | 98% | 100% | 202 s (par 205) | 99% | 60% |
| r1s5 | modest | 100% | 100% | 100% | 184 s (par 205) | 99% | 100% |
| r1s5 | strong | 100% | 100% | 100% | 139 s (par 205) | 100% | 100% |
| r1boss | none | 15% | 42% | 54% | 290 s (par 260) | 40% | 1% |
| r1boss | light | 74% | 93% | 98% | 266 s (par 260) | 72% | 28% |
| r1boss | modest | 97% | 99% | 100% | 238 s (par 260) | 84% | 80% |
| r1boss | strong | 100% | 100% | 100% | 149 s (par 260) | 100% | 100% |
