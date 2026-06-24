import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-medium mb-6" style={{ color: "var(--foreground)" }}>
        About
      </h1>
      <div className="text-base leading-relaxed flex flex-col gap-4" style={{ color: "var(--foreground)", opacity: 0.8 }}>
        <p>
          I'm Florence — a writer exploring the space where artificial intelligence and spiritual growth meet.
        </p>
        <p>
          This site is a free, open version of my{" "}
          <a href="https://sproutingplant.substack.com" target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)" }}>
            Substack newsletter
          </a>
          . No sign-in required. Just reading.
        </p>
      </div>

      <div className="mt-10 flex flex-col gap-3">
        <h2 className="text-sm font-medium" style={{ color: "var(--foreground)", opacity: 0.5 }}>Find me elsewhere</h2>
        <div className="flex gap-5 text-sm">
          <a href="https://sproutingplant.substack.com" target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)" }}>
            Substack ↗
          </a>
          <a href="https://www.instagram.com/spro.utingplant/" target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)" }}>
            Instagram ↗
          </a>
          <a href="https://www.facebook.com/profile.php?id=61591159505096" target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)" }}>
            Facebook ↗
          </a>
        </div>
      </div>
    </div>
  );
}
