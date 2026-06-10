import { useState } from "react";

export default function Hero({ onSubmit, isSubmitting }) {
  const [arxivId, setArxivId] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = arxivId.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  };

  return (
    <section className="hero glass-panel" id="generate" aria-labelledby="hero-title">
      <p className="eyebrow">Research audio workflow</p>
      <h1 id="hero-title">ArXiv Podcast</h1>
      <p className="hero-copy">
        Convert an eligible arXiv paper into a long-form Host and Expert discussion. The pipeline checks licensing,
        extracts the paper text, writes a technical script, and synthesizes speech with free TTS.
      </p>

      <form className="generate-form" onSubmit={handleSubmit}>
        <label htmlFor="arxiv-id">arXiv ID</label>
        <div className="input-row">
          <input
            id="arxiv-id"
            name="arxiv_id"
            value={arxivId}
            onChange={(event) => setArxivId(event.target.value)}
            placeholder="2401.12345 or arXiv:2401.12345"
            autoComplete="off"
            required
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Generating" : "Generate podcast"}
          </button>
        </div>
      </form>
    </section>
  );
}
