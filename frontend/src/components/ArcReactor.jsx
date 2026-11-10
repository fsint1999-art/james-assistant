import { useEffect, useRef } from "react";
// Núcleo: rede 3D de partículas (esfera) que pulsa, gira e se aglomera conforme o estado.
const N = 700, K = 3;
const MODE = {
  idle:   { amp: .10, spd: .25, att: .15, glow: .6, pul: 0 },
  busy:   { amp: .30, spd: 1.2, att: .7,  glow: 1,  pul: 0 },
  listen: { amp: .18, spd: .55, att: .4,  glow: .85, pul: 0 },
  speak:  { amp: .22, spd: .8,  att: .55, glow: .95, pul: .045 },
  mute:   { amp: .03, spd: .06, att: 0,   glow: .2,  pul: 0 },
};
function build() {
  const p = [], g = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < N; i++) { const y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), a = g * i; p.push([Math.cos(a) * r, y, Math.sin(a) * r]); }
  const nb = p.map((a, i) => p.map((b, j) => [j, (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2])
    .filter(x => x[0] !== i).sort((x, y) => x[1] - y[1]).slice(0, K).map(x => x[0]));
  return { p, nb };
}
const ALPHA = [.08, .18, .34, .6];

export default function ArcReactor({ state = "idle", level }) {
  const cv = useRef(), st = useRef(state), net = useRef(null);
  st.current = state; const lv = useRef(level); lv.current = level;
  useEffect(() => {
    net.current ||= build();
    const { p, nb } = net.current, c = cv.current, ctx = c.getContext("2d");
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const size = () => { c.width = c.clientWidth * dpr; c.height = c.clientHeight * dpr; };
    size(); window.addEventListener("resize", size);
    const cur = { ...MODE.idle }, xs = new Float32Array(N), ys = new Float32Array(N), zs = new Float32Array(N), br = new Float32Array(N);
    const S = { v: 0 }; let t = 0, last = performance.now(), raf;
    const frame = now => {
      const dt = Math.min(.05, (now - last) / 1000); last = now;
      const tg = MODE[st.current] || MODE.idle; for (const k in tg) cur[k] += (tg[k] - cur[k]) * .05;
      t += dt * (.3 + cur.spd);
      const W = c.width, H = c.height, R = Math.min(W, H) * .34;
      const A = [0, 1, 2].map(k => { const a = t * (.5 + k * .23) + k * 2.1, b = t * (.37 + k * .19) + k; return [Math.cos(a) * Math.cos(b), Math.sin(b), Math.sin(a) * Math.cos(b)]; });
      const sl = (S.v += ((lv.current ? lv.current() : 0) - S.v) * .4), pulse = 1 + sl * .07, ry = t * .25, cy = Math.cos(ry), sy = Math.sin(ry), cx = Math.cos(.35), sx = Math.sin(.35);
      for (let i = 0; i < N; i++) {
        const u = p[i], w = Math.sin(u[0] * 3.1 + t * 1.3) * Math.cos(u[1] * 2.7 - t * .9) + .5 * Math.sin(u[2] * 3.7 + t * 1.1);
        let pull = 0; for (const a of A) pull += Math.exp(-((u[0] - a[0]) ** 2 + (u[1] - a[1]) ** 2 + (u[2] - a[2]) ** 2) * 5);
        pull = Math.min(1, pull * cur.att * 1.6);
        const r = (1 + cur.amp * w - pull * .35 + sl * .22 * Math.sin(u[1] * 8 - t * 14)) * pulse, x0 = u[0] * r, y0 = u[1] * r, z0 = u[2] * r;
        const x1 = x0 * cy + z0 * sy, z1 = -x0 * sy + z0 * cy, y2 = y0 * cx - z1 * sx, z2 = y0 * sx + z1 * cx, f = 2.8 / (2.8 - z2);
        xs[i] = W / 2 + x1 * f * R; ys[i] = H / 2 + y2 * f * R; zs[i] = z2; br[i] = pull;
      }
      ctx.clearRect(0, 0, W, H); ctx.globalCompositeOperation = "lighter"; ctx.lineWidth = dpr * .8;
      const paths = [0, 1, 2, 3].map(() => new Path2D());
      for (let i = 0; i < N; i++) for (const j of nb[i]) {
        const a = (.12 + .5 * ((zs[i] + zs[j] + 2) / 4) + .6 * (br[i] + br[j]) / 2) * cur.glow, b = Math.min(3, Math.floor(a * 4));
        paths[b].moveTo(xs[i], ys[i]); paths[b].lineTo(xs[j], ys[j]);
      }
      paths.forEach((pa, b) => { ctx.strokeStyle = `rgba(56,217,255,${ALPHA[b] * Math.max(.3, cur.glow)})`; ctx.stroke(pa); });
      for (const gold of [false, true]) {
        ctx.fillStyle = gold ? `rgba(232,180,74,${.9 * cur.glow})` : `rgba(150,235,255,${.8 * cur.glow})`;
        for (let i = 0; i < N; i++) if ((br[i] >= .5) === gold) { const s = dpr * (1 + (zs[i] + 1) * .8 + br[i] * 1.5); ctx.fillRect(xs[i], ys[i], s, s); }
      }
    };
    const loop = now => { frame(now); raf = requestAnimationFrame(loop); };
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) frame(performance.now()); else raf = requestAnimationFrame(loop);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", size); };
  }, []);
  return <canvas ref={cv} className="core" role="img" aria-label={`Núcleo do JAMES: ${state}`} />;
}
