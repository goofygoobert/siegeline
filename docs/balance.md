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

**Final results** (win rate; average win time and Keep health for the *average* player; 3-star rate for the average player)

Runs per cell: 200. Skill = bot reaction speed and aim error (sloppy 0.35, average 0.6, sharp 0.9). Profiles: none = all level 1; light = units 2, keep/ballista 2; modest = units 3, keep/ballista 3, ember 2/2, hero 2, powers 2; strong = units 6, keep/ballista 6, ember 4/4, hero 5, powers 5.
| Stage | Upgrades | Sloppy win | Average win | Sharp win | Avg win time (average) | Keep HP left (average) | 3-star rate (average) |
|---|---|---|---|---|---|---|---|
| r1s1 | none | 93% | 100% | 100% | 111 s (par 110) | 100% | 49% |
| r1s1 | light | 100% | 100% | 100% | 103 s (par 110) | 100% | 99% |
| r1s1 | modest | 100% | 100% | 100% | 97 s (par 110) | 100% | 100% |
| r1s1 | strong | 100% | 100% | 100% | 79 s (par 110) | 100% | 100% |
| r1s2 | none | 70% | 85% | 95% | 144 s (par 140) | 99% | 33% |
| r1s2 | light | 99% | 99% | 100% | 135 s (par 140) | 99% | 72% |
| r1s2 | modest | 100% | 100% | 100% | 122 s (par 140) | 99% | 96% |
| r1s2 | strong | 100% | 100% | 100% | 86 s (par 140) | 100% | 100% |
| r1s3 | none | 65% | 93% | 100% | 175 s (par 155) | 99% | 16% |
| r1s3 | light | 99% | 100% | 100% | 152 s (par 155) | 99% | 78% |
| r1s3 | modest | 100% | 100% | 100% | 139 s (par 155) | 99% | 100% |
| r1s3 | strong | 100% | 100% | 100% | 112 s (par 155) | 100% | 100% |
| r1s4 | none | 47% | 80% | 95% | 201 s (par 190) | 100% | 18% |
| r1s4 | light | 96% | 100% | 100% | 175 s (par 190) | 100% | 86% |
| r1s4 | modest | 100% | 100% | 100% | 168 s (par 190) | 100% | 92% |
| r1s4 | strong | 100% | 100% | 100% | 109 s (par 190) | 100% | 100% |
| r1s5 | none | 34% | 57% | 64% | 216 s (par 205) | 99% | 16% |
| r1s5 | light | 91% | 100% | 100% | 194 s (par 205) | 100% | 70% |
| r1s5 | modest | 100% | 100% | 100% | 183 s (par 205) | 99% | 97% |
| r1s5 | strong | 100% | 100% | 100% | 136 s (par 205) | 100% | 100% |
| r1boss | none | 16% | 39% | 63% | 252 s (par 240) | 39% | 3% |
| r1boss | light | 85% | 96% | 99% | 234 s (par 240) | 74% | 55% |
| r1boss | modest | 100% | 100% | 100% | 203 s (par 240) | 92% | 97% |
| r1boss | strong | 100% | 100% | 100% | 121 s (par 240) | 100% | 100% |

**Reading it**
- **No upgrades, average player:** stage 1 100%, 2 85%, 3 93%, 4 80%, 5 57%, boss 39%. Early stages are winnable cold and later ones push you toward the Armoury. Nothing is impossible: a sharp player beats the boss cold 63% of the time.
- **Light upgrades** (units level 2, Keep/ballista 2, about 600 marks, roughly what the first clears pay): 96–100% on every stage. This is the intended path.
- **Nothing trivial at first contact:** a sloppy player with no upgrades wins the boss 16% and stage 5 34%.
- **Stars give replay value:** the time star needs either upgrades or sharp play (3-star rates of 3–49% with no upgrades, 55–99% with light).
- **Caveat:** the bot plays very consistently, so its win rate jumps once its army passes a threshold, which makes the curve between "none" and "light" look steeper than a person will feel. Its decisions are reasonable but it doesn't deliberately exploit boss windows or save up embers for heavies the way a good player does.
