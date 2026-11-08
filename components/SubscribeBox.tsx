export default function SubscribeBox() {
  return (
    <div
      className="my-12 px-6 py-8 rounded-xl text-center"
      style={{ background: "rgba(232,68,10,0.07)", border: "1px solid rgba(232,68,10,0.15)" }}
    >
      <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--accent)", letterSpacing: "0.1em" }}>
        By Florence
      </p>
      <h3 className="text-xl font-medium mb-2" style={{ color: "var(--foreground)" }}>
        Writing at the intersection of AI and inner life
      </h3>
      <p className="text-sm mb-5" style={{ color: "var(--foreground)", opacity: 0.6 }}>
        New essays on consciousness, technology, and what it means to be human — delivered to your inbox.
      </p>
      <a
        href="https://sproutingplant.substack.com/subscribe"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block px-6 py-2.5 rounded-full text-sm font-medium transition-opacity hover:opacity-80"
        style={{ background: "var(--accent)", color: "#fff" }}
      >
        Subscribe free
      </a>
    </div>
  );
}
