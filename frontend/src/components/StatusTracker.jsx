const statusLabels = {
  queued: "Queued",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
};

export default function StatusTracker({ job, error }) {
  if (!job && !error) {
    return (
      <section className="status-tracker glass-panel muted-panel" id="status" aria-live="polite">
        <h2>Status</h2>
        <p>Submit an arXiv ID to start a podcast generation job.</p>
      </section>
    );
  }

  return (
    <section className="status-tracker glass-panel" id="status" aria-live="polite">
      <div className="section-header">
        <h2>Status</h2>
        {job?.status && <span className={`status-pill status-${job.status}`}>{statusLabels[job.status] || job.status}</span>}
      </div>

      {job?.job_id && <p className="mono-text">Job: {job.job_id}</p>}
      {job?.message && <p>{job.message}</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
