export default function Navbar() {
  return (
    <header className="navbar glass-panel">
      <a className="brand" href="/" aria-label="ArXiv Podcast home">
        <span className="brand-mark" aria-hidden="true" />
        <span>ArXiv Podcast</span>
      </a>
      <nav aria-label="Primary navigation">
        <a href="#generate">Generate</a>
        <a href="#status">Status</a>
      </nav>
    </header>
  );
}
