import { useEffect, useRef } from "react";
export default function TerminalFeed({ logs }) {
  const end = useRef(); useEffect(() => end.current?.scrollIntoView(), [logs]);
  return (
    <section className="panel feed"><h2>LOGS / TERMINAL FEED</h2>
      <div className="lines">{logs.map((l, i) => <p key={i} className={l.src}><time>{l.t}</time> <b>{l.src}</b> {l.text}</p>)}<div ref={end} /></div>
    </section>);
}
