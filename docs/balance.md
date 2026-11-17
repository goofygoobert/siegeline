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

**Final results** (win rate; average win time and Keep health for the *average* player; 3-star rate for the average player)

Runs per cell: 100. Skill = bot reaction speed and aim error (sloppy 0.35, average 0.6, sharp 0.9). Profiles: none = all level 1; light = units 2, keep/ballista 2; modest = units 3, keep/ballista 3, ember 2/2, hero 2, powers 2; strong = units 6, keep/ballista 6, ember 4/4, hero 5, powers 5.

| Stage | Upgrades | Sloppy win | Average win | Sharp win | Avg win time (average) | Keep HP left (average) | 3-star rate (average) |
|---|---|---|---|---|---|---|---|
| r1s1 | none | 92% | 100% | 100% | 110 s (par 110) | 100% | 61% |
| r1s1 | light | 100% | 100% | 100% | 103 s (par 110) | 100% | 98% |
| r1s1 | modest | 100% | 100% | 100% | 95 s (par 110) | 100% | 100% |
| r1s1 | strong | 100% | 100% | 100% | 78 s (par 110) | 100% | 100% |
| r1s2 | none | 55% | 83% | 93% | 145 s (par 140) | 99% | 25% |
| r1s2 | light | 98% | 100% | 99% | 136 s (par 140) | 99% | 77% |
| r1s2 | modest | 100% | 100% | 100% | 119 s (par 140) | 99% | 100% |
| r1s2 | strong | 100% | 100% | 100% | 86 s (par 140) | 100% | 100% |
| r1s3 | none | 68% | 90% | 97% | 177 s (par 155) | 99% | 7% |
| r1s3 | light | 99% | 99% | 100% | 159 s (par 155) | 99% | 47% |
| r1s3 | modest | 100% | 100% | 100% | 143 s (par 155) | 100% | 98% |
| r1s3 | strong | 100% | 100% | 100% | 113 s (par 155) | 100% | 100% |
| r1s4 | none | 41% | 83% | 96% | 203 s (par 190) | 100% | 12% |
| r1s4 | light | 96% | 100% | 100% | 182 s (par 190) | 100% | 75% |
| r1s4 | modest | 99% | 100% | 100% | 168 s (par 190) | 100% | 99% |
| r1s4 | strong | 100% | 100% | 100% | 112 s (par 190) | 100% | 100% |
| r1s5 | none | 38% | 64% | 89% | 219 s (par 205) | 99% | 8% |
| r1s5 | light | 76% | 97% | 100% | 204 s (par 205) | 99% | 53% |
| r1s5 | modest | 99% | 100% | 100% | 184 s (par 205) | 100% | 100% |
| r1s5 | strong | 100% | 100% | 100% | 138 s (par 205) | 100% | 100% |
| r1boss | none | 14% | 35% | 59% | 292 s (par 260) | 38% | 1% |
| r1boss | light | 67% | 90% | 97% | 266 s (par 260) | 69% | 26% |
| r1boss | modest | 99% | 100% | 100% | 239 s (par 260) | 85% | 83% |
| r1boss | strong | 100% | 100% | 100% | 150 s (par 260) | 100% | 100% |
