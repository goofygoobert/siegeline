# Performance

Measured with `tools/perf.mjs`: headless Chrome on the Jetson (ARM CPU, **no GPU: canvas drawing is done in software**), with an 844×390 phone viewport at 2× pixel ratio. A phone's Safari draws canvas images on the GPU, so the drawing numbers below are a worst case. The simulation numbers transfer directly.

Headless Chrome also caps animation frames at 15 fps, so frame *rate* can't be measured here. I measure the game's own **work per frame** (simulation + drawing + HUD) against the 16.7 ms budget for 60 fps.

## Targets and results

| Target | Result | Status |
|---|---|---|
| 60 fps in the busiest battle | Normal busy boss fight: **15.4 ms/frame** work (software drawing, before GPU help). Stress test with ~95–99 live objects (unlimited embers, triple spawn rate): **17.6–28 ms avg**, of which the simulation is **0.31 ms**; the rest is software pixel fill. | Simulation and logic well within budget. Drawing should fit on a phone GPU; not verified on a real phone. Adaptive quality kicks in if it doesn't (see below). |
| First load under ~5 s on a phone connection | Simulated good 4G (9 Mbps, 60 ms RTT), cold cache: title screen ready in **0.44 s**, 141 KB. First battle (all region art for it) ready **2.7 s** later, 2.0 MB. | Met |
| No memory growth over 20 minutes | Back-to-back battles at 8× speed (27 simulated minutes): JS heap stays **2.4–3.5 MB**, no upward trend. | Met |
| No pauses when units appear | Entities are reused from a pool (dead slots are recycled), particles and damage numbers use fixed pools of 360 / 48, and atlases and white flash copies are made at load time, not at spawn. Sim cost per frame 0.31 ms even at 95 objects. | Met by design. Worst frames come from drawing, not spawning. |

## Before and after (work per frame, normal busy boss battle, software rendering)

| Change | Avg | p95 | Worst |
|---|---|---|---|
| Before: backgrounds scaled from source every frame, full-screen gradient vignette, additive blend switched per particle | 43.0 ms | 69.1 ms | 173.7 ms |
| After: each background layer pre-scaled once to screen resolution (plain copies per frame), vignette rendered once to a small image, all glowing particles drawn in one additive pass | **15.4 ms** | **19.1 ms** | **21.5 ms** |
| Stress (~98 objects), shadows/glows as pre-rendered images, fewer small damage numbers at reduced quality | 17.6–28.3 ms (run to run) | 32–34 ms | 38–57 ms |

## How the game stays fast
- **Atlases:** each sprite group is 1–3 WebP pages (≤2048²). A frame is one `drawImage` from an atlas, and hit flashes use a pre-tinted white copy of the atlas, so there are no per-frame filters.
- **Off-screen skipping:** entities, projectiles, particles and patches outside the camera are skipped.
- **Pools:** entities, particles (360), damage numbers (48) and one-shot effects (24) are reused, with no per-frame allocation in the hot loop.
- **Fixed-step simulation** at 30 Hz with interpolated drawing, so a slow frame never changes the outcome.
- **Adaptive quality:** if the average frame rate stays under 45 fps for ~1.5 s, effects step down. Level 1 halves particles and drops ambient embers. Level 0 also drops the vignette, castle smoke and small damage numbers, and lowers canvas resolution from 2× to 1.5×.
- **Loading on demand:** the title needs only 141 KB. Battle art loads when you first enter a battle, behind a progress bar. The level-5/10 unit looks (1.5 MB) load only after a unit reaches level 5 or 10, and the boss (600 KB) only for the boss stage. The service worker then caches everything for offline play. It registers 4 s after load so it doesn't compete with the first screen.

## Download size by group (WebP / AAC)
| Group | Size |
|---|---|
| Code (JS + CSS) | 112 KB |
| Title + world map | 168 KB |
| Backgrounds (r1 + night set) | 308 KB |
| Castles + effects | 320 KB |
| Units: base looks | 687 KB |
| Units: level 5 and level 10 looks | 1,545 KB (loaded only when needed) |
| Hero | 192 KB |
| Enemies | 828 KB |
| Boss | 600 KB |
| UI portraits and icons | 28 KB |
| Audio (33 effects + 6 music tracks) | 2,948 KB (each loads when first needed) |
| **Total region 1** | **~7.8 MB** |

## Not yet verified
- Real frame rate on an iPhone (no device here). The play-through recording and the perf probe are both headless.

## Redesign slice (2026-11-17)
- Download: `dist/` 8.6 MB → 9.6 MB (new carved-figure atlas pages `v2`, `v22` = 0.96 MB; old frames of the same two characters still ship until phase 3).
- Frame work, headless software rendering, same machine under load (load average ~4.5), busiest-battle probe: live 28.2 ms avg / 34 ms p95; redesign 29.1 ms avg / 37 ms p95. No meaningful change. One 75 ms hitch seen in the redesign run (live worst 39 ms): not yet traced.
- New per-frame work is small fixed pools (24 decals, 24 sparks, 8 rings). Hit-stop pauses the sim, not the renderer.
- Still not measured on a real iPhone.

## Roll-out (2026-11-17, phase 3)
- Download: `dist/` 13 MB (was 8.6 MB live, 9.6 MB slice). Art atlases 8.4 MB in 24 pages; audio unchanged at 2.9 MB. First battle on a throttled connection: 3.7 MB, 4.1 s. Offline precache 11.8 MB.
- A normal battle loads about 8 atlas pages (3 crew, 3 monsters, Captain, forts/effects); the boss stage adds 6 boss pages. Level 5 and level 10 looks add up to 4 pages each, only when a unit has them. Texture memory on a real iPhone is **not measured** and is the main risk of this pass.
- Frame work, headless software rendering, machine under load (load average 4.7–5.6): 35 ms avg / 43 ms p95 (live build the same hour at load 4.5: 28 ms / 34 ms). Larger sprites cost more in software rendering; on a phone GPU this should not matter, but it is unverified.
- One 260 ms frame per run: the adaptive-quality step-down (it rebuilds the scaled background layers). It fires because the headless run is slow; pages are now decoded and warmed during loading.
