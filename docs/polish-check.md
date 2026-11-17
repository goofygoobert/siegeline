# Feel list check (design §8)

Each item was checked in code and in the play-through screenshots or recording on 2026-11-17.

| Touch | In? | Where |
|---|---|---|
| White hit flash on sprites | Yes. Softened to 50% after review. Burn ticks don't flash (that bug made the boss white). | renderer `drawEntity`, atlas white copies |
| Splatter: dark red for Wardens, ash and embers for Hollows | Yes | renderer `dmg`/`die` events |
| Damage numbers that pop and rise | Yes. Hits on the same target within 0.25 s merge into one number; small hits are hidden at reduced quality. | renderer `num` |
| Knockback slide | Yes (maul, brute, boss sweep, bolts) | sim `damage` / `stepEntity` |
| Dust ring and shake on slams | Yes | `slam`, `bossSlam` |
| Ballista aim arc, landing ring, camera follows the landing point | Yes. The camera only moves when the ring would leave the screen. | `drawAim`, `updateAim` |
| Explosion flipbook, smoke, embers, burning patch | Yes | `boltHit` → `fxAt("blast")`, fire patches |
| Shake scaled to hits, "N down!" on multi-kills | Yes | `boltHit` |
| Reload click | Yes | `reloaded` |
| Deaths: collapse and fade, Hollows burst into embers | Yes | `die` |
| Bloater burst: flash, shake, damage to both sides | Yes | `burst` |
| Hero call: gold flash, shake, callout, horn | Yes | `hero` |
| Flare ring, flash, stun stars | Yes | `flare` + stun stars in `drawEntity` |
| Boss entrance: roar, music duck, shake, camera, health bar | Yes | `bossSpawn`, `onBoss` |
| Boss warnings: pulsing red zones, text callouts on a dark plate | Yes. One callout at a time after review 2. | `drawMarks`, `bossWarn` |
| Boss winded window with stars | Yes (added after review 1) | sim `vuln`, renderer stars |
| Phase-two flash and roar | Yes | `bossPhase` |
| Slow motion and flash on the boss kill and the gate's fall | Yes | `bossDead`, `win` |
| "They're rushing!" when the gate drops below half; "The Maw grows angry" after par | Yes | `rush`, `angry` |
| Stars pop in one by one with rising pitch; coins fly to the counter and tick it up | Yes | `results()` |
| Loss: shake, low sting, tip based on what killed you, "so close" line, Upgrade button | Yes | `finish`, `loseTip` |
| Ember store full: gold counter and chime | Yes | `updateHud` |
| UI presses scale down; tap, back, upgrade and locked sounds | Yes | CSS `.btn:active`, `tap()` |
| Reduced motion: no shake, flashes or animations | Yes | settings toggle and the system setting |
| Haptics | No. iPhone Safari has no vibration API. | — |
