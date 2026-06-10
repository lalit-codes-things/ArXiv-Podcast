import { useCallback, useEffect, useRef, useState } from "react";
import GalaxyBackground from "./components/GalaxyBackground.jsx";
import Hero from "./components/Hero.jsx";
import Navbar from "./components/Navbar.jsx";
import PodcastResult from "./components/PodcastResult.jsx";
import StatusTracker from "./components/StatusTracker.jsx";

const POLL_INTERVAL_MS = 2000;

export default function App() {
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const pollHandle = useRef(null);

  const stopPolling = useCallback(() => {
    if (pollHandle.current) {
      clearInterval(pollHandle.current);
      pollHandle.current = null;
    }
  }, []);

  const loadStatus = useCallback(
    async (jobId) => {
      const response = await fetch(`/api/status/${jobId}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not read job status.");
      }
      setJob(data);
      if (data.status === "completed" || data.status === "failed") {
        stopPolling();
        setIsSubmitting(false);
      }
      if (data.status === "failed") {
        setError(data.error || "The podcast generation job failed.");
      }
    },
    [stopPolling],
  );

  const startGeneration = async (arxivId) => {
    stopPolling();
    setError("");
    setJob(null);
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ arxiv_id: arxivId }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not create a generation job.");
      }
      setJob({ job_id: data.job_id, status: data.status, message: "Job queued" });
      await loadStatus(data.job_id);
      pollHandle.current = setInterval(() => {
        loadStatus(data.job_id).catch((statusError) => {
          stopPolling();
          setIsSubmitting(false);
          setError(statusError.message);
        });
      }, POLL_INTERVAL_MS);
    } catch (requestError) {
      setIsSubmitting(false);
      setError(requestError.message);
    }
  };

  useEffect(() => stopPolling, [stopPolling]);

  return (
    <>
      <GalaxyBackground />

      <Navbar />

      <main className="app-main">
        <Hero onSubmit={startGeneration} isSubmitting={isSubmitting} />

        <StatusTracker job={job} error={error} />

        <PodcastResult job={job} />
      </main>
    </>
  );
}
