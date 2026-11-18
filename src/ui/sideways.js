// Sideways view. iPhone home-screen apps ignore the manifest's orientation, so with rotation lock on the screen stays
// portrait. When the screen is taller than wide, the whole game (canvas and menus) is drawn turned 90 degrees, so the
// phone is simply held sideways like any landscape game. Touch positions arrive in screen space and are mapped back
// with toGame(); the notch and home-indicator margins are moved to the matching game sides.
//   mode "auto": the top of the phone goes to the LEFT (turn the phone anticlockwise), the usual way to hold a game
//   mode "flip": the top of the phone goes to the right
//   mode "off":  never turn; a "turn your phone" card shows instead
export const SW = { on: false, flip: false, W: 0, H: 0 };

export function applySideways(mode = "auto") {
  const vw = window.innerWidth, vh = window.innerHeight;
  SW.on = mode !== "off" && vh > vw;
  SW.flip = mode === "flip";
  SW.W = SW.on ? vh : vw; SW.H = SW.on ? vw : vh;      // the game's own width and height in css px
  const root = document.documentElement;
  root.classList.toggle("sideways", SW.on);
  root.classList.toggle("flip", SW.on && SW.flip);
  root.classList.toggle("no-sideways", mode === "off");
  root.style.setProperty("--gw", SW.W + "px"); root.style.setProperty("--gh", SW.H + "px");
  return SW;
}

/** Screen point (clientX, clientY) -> point in the game's own css px. */
export function toGame(cx, cy) {
  if (!SW.on) return [cx, cy];
  return SW.flip ? [SW.W - cy, cx] : [cy, SW.H - cx];
}

/** Centre of an element's on-screen box, in game css px. */
export function centreOf(el) {
  const r = el.getBoundingClientRect();
  return toGame(r.left + r.width / 2, r.top + r.height / 2);
}
