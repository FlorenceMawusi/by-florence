function InstagramIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
      <circle cx="12" cy="12" r="4"/>
      <circle cx="17.5" cy="6.5" r="0.5" fill="currentColor" stroke="none"/>
    </svg>
  );
}

function FacebookIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
    </svg>
  );
}

function SubstackIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M22.539 8.242H1.46V5.406h21.08v2.836zM1.46 10.812V24L12 17.11 22.54 24V10.812H1.46zM22.54 0H1.46v2.836h21.08V0z"/>
    </svg>
  );
}

export default function Footer() {
  return (
    <footer className="border-t mt-16" style={{ borderColor: "rgba(26,16,8,0.12)" }}>
      <div className="max-w-3xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span className="text-sm" style={{ color: "var(--foreground)", opacity: 0.5 }}>
          © {new Date().getFullYear()} Florence. All rights reserved.
        </span>
        <div className="flex items-center gap-5">
          <a href="https://www.instagram.com/spro.utingplant/" target="_blank" rel="noopener noreferrer" aria-label="Instagram" className="hover:opacity-70 transition-opacity" style={{ color: "var(--foreground)" }}>
            <InstagramIcon />
          </a>
          <a href="https://www.facebook.com/profile.php?id=61591159505096" target="_blank" rel="noopener noreferrer" aria-label="Facebook" className="hover:opacity-70 transition-opacity" style={{ color: "var(--foreground)" }}>
            <FacebookIcon />
          </a>
          <a href="https://sproutingplant.substack.com" target="_blank" rel="noopener noreferrer" aria-label="Substack" className="hover:opacity-70 transition-opacity" style={{ color: "var(--accent)" }}>
            <SubstackIcon />
          </a>
        </div>
      </div>
    </footer>
  );
}
