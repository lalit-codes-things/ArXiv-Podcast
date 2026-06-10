export default function PodcastResult({ job }) {
  if (job?.status !== "completed" || !job.result) {
    return null;
  }

  const { audio_url: audioUrl, waveform_url: waveformUrl, metadata, summary } = job.result;

  return (
    <section className="podcast-result glass-panel" aria-labelledby="result-title">
      <div className="section-header">
        <h2 id="result-title">Podcast ready</h2>
        <a className="download-link" href={audioUrl} download>
          Download MP3
        </a>
      </div>

      <p className="paper-title">{metadata?.title || "Generated arXiv podcast"}</p>
      <audio controls src={audioUrl} />
      <img src={waveformUrl} alt="Waveform for the generated ArXiv Podcast episode" />

      {summary && (
        <details>
          <summary>Paper summary used for the script</summary>
          <pre>{summary}</pre>
        </details>
      )}
    </section>
  );
}
