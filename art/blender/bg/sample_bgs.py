from kit import *
import sys
# One wide sample backdrop per world, stacked vertically in one image (top: A, middle: B, bottom: C).
reset()
W, H = 40.0, 10.0
def world(theme, zoff):
    if theme == "A":   # Ashen Marches: ember dusk, ruined towers, ash dunes
        gradient_plane(W, H, (0.16, 0.07, 0.10), (0.85, 0.36, 0.12), (W / 2, 60, zoff + H / 2))
        prop_obj([("cone", (1.4, 1.4, 0.1), (0, 0, 0))], 30, 58, zoff + 6.5, (1.0, 0.75, 0.4), face=True)
        ridge(0, W, zoff + 3.0, 3.0, (0.32, 0.12, 0.11), 50, seed=2, step=2.0)
        ridge(0, W, zoff + 2.0, 2.0, (0.2, 0.09, 0.09), 40, seed=5, step=1.4)
        for i, x in enumerate((4, 13, 26, 35)):
            prop_obj([("box", (0.9, 0.9, 3.5 + i % 2), (0, 0, 1.6)), ("box", (1.2, 1.2, 0.4), (0, 0, 3.6 + i % 2))], x, 35, zoff + 1.5, (0.14, 0.06, 0.07))
        for x in (8, 20, 31):
            prop_obj([("cone", (0.12, 0.05, 2.4), (0, 0, 1.2)), ("box", (1.2, 0.1, 0.1), (0.3, 0, 1.9))], x, 30, zoff + 1.0, (0.09, 0.05, 0.05), rot=0.2)
        ridge(0, W, zoff + 1.0, 0.5, (0.11, 0.07, 0.08), 20, seed=9, step=1.0)
        for i in range(60):
            r = random.Random(i)
            prop_obj([("box", (0.06, 0.06, 0.06), (0, 0, 0))], r.uniform(0, W), 15, zoff + r.uniform(1.5, 9), (1.0, 0.55, 0.15))
    elif theme == "B":  # Saltreach: cold fog sea cliffs, lighthouse, masts
        gradient_plane(W, H, (0.35, 0.45, 0.52), (0.75, 0.8, 0.78), (W / 2, 60, zoff + H / 2))
        ridge(0, W, zoff + 1.0, 0.3, (0.42, 0.55, 0.6), 52, seed=3, step=0.8)
        ridge(0, 14, zoff + 2.5, 3.5, (0.32, 0.4, 0.45), 45, seed=4, step=1.5, jag=0.2)
        ridge(26, W, zoff + 2.0, 4.0, (0.3, 0.38, 0.42), 45, seed=6, step=1.5, jag=0.2)
        prop_obj([("cone", (0.6, 0.4, 3.0), (0, 0, 1.5)), ("box", (0.7, 0.7, 0.5), (0, 0, 3.2))], 34, 40, zoff + 5.8, (0.22, 0.27, 0.3))
        prop_obj([("box", (0.4, 0.4, 0.3), (0, 0, 0))], 34, 39, zoff + 9.1, (1.0, 0.9, 0.5))
        for x in (17, 21):
            prop_obj([("box", (0.12, 0.12, 4.0), (0, 0, 2)), ("box", (1.8, 0.1, 0.1), (0, 0, 3.2)), ("box", (3.5, 1, 0.8), (0, 0, 0.3))], x, 42, zoff + 0.8, (0.2, 0.24, 0.26))
        ridge(0, W, zoff + 1.2, 0.4, (0.25, 0.3, 0.3), 20, seed=8, step=1.0)
        gradient_plane(W, 2.5, (0.8, 0.85, 0.85), (0.8, 0.85, 0.85), (W / 2, 18, zoff + 1.6))
    else:               # Glasswind: blazing desert, glass spires, sun
        gradient_plane(W, H, (0.35, 0.6, 0.85), (0.98, 0.88, 0.65), (W / 2, 60, zoff + H / 2))
        prop_obj([("cone", (1.8, 1.8, 0.1), (0, 0, 0))], 9, 58, zoff + 7.5, (1.0, 0.97, 0.8), face=True)
        ridge(0, W, zoff + 2.0, 1.5, (0.92, 0.7, 0.45), 50, seed=1, step=3.0, jag=0.1)
        for x, h in ((6, 4.5), (15, 6.5), (24, 3.5), (33, 5.5)):
            prop_obj([("cone", (0.5, 0.0, h), (0, 0, h / 2)), ("cone", (0.3, 0.0, h * 0.6), (0.7, 0, h * 0.3))], x, 40, zoff + 1.5, (0.55, 0.85, 0.9))
        ridge(0, W, zoff + 1.2, 1.0, (0.85, 0.58, 0.32), 30, seed=7, step=2.5, jag=0.1)
        ridge(0, W, zoff + 0.8, 0.4, (0.7, 0.45, 0.25), 20, seed=11, step=1.5, jag=0.1)
THEME = "A"
world(THEME, 0)
bg_camera(W, H, 40, H / 2)
