import { useEffect, useRef } from "react";
// Mapa neural de fundo: neurônios claros à deriva, sinapses disparando e ligações com o núcleo.
const N = 110, D = 190, RATE = { idle: .8, busy: 7, listen: 2.5, speak: 3, mute: .1 };
export default function Background({ level, state = "idle" }) {
  const cv = useRef(), lv = useRef(level), st = useRef(state);
  lv.current = level; st.current = state;
  useEffect(() => {
    const c = cv.current, ctx = c.getContext("2d"), dpr = Math.min(2, devicePixelRatio || 1);
    let W = innerWidth, H = innerHeight;
    const size = () => { W = innerWidth; H = innerHeight; c.width = W * dpr; c.height = H * dpr; };
    size(); addEventListener("resize", size);
    const nodes = Array.from({ length: N }, () => ({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25, f: 0 }));
    const pulses = []; let last = performance.now(), spawn = 0, raf;
    const frame = now => {
      const dt = Math.min(.05, (now - last) / 1000); last = now;
      const lvl = lv.current ? lv.current() : 0, core = document.querySelector(".core")?.getBoundingClientRect();
      const cx = core ? core.left + core.width / 2 : W / 2, cy = core ? core.top + core.height / 2 : H / 2, cr = core ? core.width * .34 : 0;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H); ctx.globalCompositeOperation = "lighter"; ctx.lineWidth = 1;
      for (const n of nodes) { n.x += n.vx; n.y += n.vy; if (n.x < 0 || n.x > W) n.vx *= -1; if (n.y < 0 || n.y > H) n.vy *= -1; n.f *= .94; }
      const edges = [];
      for (let i = 0; i < N; i++) {
        const a = nodes[i]; ctx.beginPath();
        for (let j = i + 1; j < N; j++) { const b = nodes[j], d = Math.hypot(a.x - b.x, a.y - b.y); if (d < D) { edges.push([a.x, a.y, b.x, b.y, i, j]); ctx.strokeStyle = `rgba(56,217,255,${.1 * (1 - d / D)})`; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); } }
        if (cr) { const dx = a.x - cx, dy = a.y - cy, d = Math.hypot(dx, dy); if (d > cr && d < cr * 2.8) {
          const px = cx + dx / d * cr, py = cy + dy / d * cr; edges.push([a.x, a.y, px, py, i, -1]);
          ctx.strokeStyle = `rgba(120,230,255,${.08 + .5 * lvl})`; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(px, py); ctx.stroke(); } }
      }
      spawn += dt * ((RATE[st.current] ?? .8) + lvl * 12);
      while (spawn >= 1 && edges.length) { spawn--; const e = edges[Math.floor(Math.random() * edges.length)]; pulses.push({ e, t: 0, rev: e[5] === -1 ? Math.random() < .5 : Math.random() < .5 }); }
      for (let k = pulses.length - 1; k >= 0; k--) {
        const p = pulses[k]; p.t += dt * 1.4; const [x1, y1, x2, y2, i, j] = p.e, t = p.rev ? 1 - p.t : p.t;
        if (p.t >= 1) { const dest = p.rev ? i : j; if (dest >= 0) nodes[dest].f = 1; pulses.splice(k, 1); continue; }
        ctx.fillStyle = "rgba(200,245,255,.9)"; ctx.beginPath(); ctx.arc(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, 1.8, 0, 6.3); ctx.fill();
      }
      for (const n of nodes) {
        if (n.f > .05) { ctx.fillStyle = `rgba(120,230,255,${.18 * n.f})`; ctx.beginPath(); ctx.arc(n.x, n.y, 7 * n.f + 2, 0, 6.3); ctx.fill(); }
        ctx.fillStyle = `rgba(210,248,255,${.3 + .7 * n.f})`; ctx.beginPath(); ctx.arc(n.x, n.y, 1.2 + n.f * 1.6, 0, 6.3); ctx.fill();
      }
    };
    const loop = now => { frame(now); raf = requestAnimationFrame(loop); };
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) frame(performance.now()); else raf = requestAnimationFrame(loop);
    return () => { cancelAnimationFrame(raf); removeEventListener("resize", size); };
  }, []);
  return <canvas ref={cv} className="bg" aria-hidden="true" />;
}
