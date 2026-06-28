"use client";

import { useState, useTransition } from "react";
import type { TopicResponse, JobRunResponse } from "@/lib/types";
import { formatDate } from "@/lib/format";

interface SettingsClientProps {
  initialTopics: TopicResponse[];
  initialJobRuns: JobRunResponse[];
}

export function SettingsClient({
  initialTopics,
  initialJobRuns,
}: SettingsClientProps) {
  const [topics, setTopics] = useState(initialTopics);
  const [jobRuns, setJobRuns] = useState(initialJobRuns);
  const [pending, startTransition] = useTransition();
  const [jobPending, setJobPending] = useState<string | null>(null);
  const [jobResult, setJobResult] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [query, setQuery] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleAddTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !query.trim()) return;
    startTransition(async () => {
      const res = await fetch("/api/topics-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), query: query.trim() }),
      });
      if (res.ok) {
        const topic: TopicResponse = await res.json();
        setTopics((prev) => [...prev, topic]);
        setName("");
        setQuery("");
      }
    });
  };

  const handleDeleteTopic = async (id: number) => {
    startTransition(async () => {
      await fetch("/api/topics-action", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      setTopics((prev) => prev.filter((t) => t.id !== id));
      setDeletingId(null);
    });
  };

  const handleTriggerJob = async (jobName: string) => {
    setJobPending(jobName);
    setJobResult(null);
    try {
      const res = await fetch("/api/jobs-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_name: jobName }),
      });
      const result = await res.json();
      setJobResult(
        `${result.job_name}: ${result.status} (${result.items_processed} items)${
          result.error ? ` - ${result.error}` : ""
        }`,
      );
      const runsRes = await fetch("/api/jobs-action?refresh=true");
      const runsData = await runsRes.json();
      setJobRuns(runsData.items ?? []);
    } finally {
      setJobPending(null);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-[var(--muted)] text-sm mt-1">
          Manage topics and data refresh jobs
        </p>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">Topics</h2>
        <form
          onSubmit={handleAddTopic}
          className="flex gap-2 mb-3"
        >
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name (e.g. Gold)"
            className="flex-1 bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm focus:border-[var(--accent)] outline-none"
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Query (e.g. gold price)"
            className="flex-1 bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm focus:border-[var(--accent)] outline-none"
          />
          <button
            type="submit"
            disabled={pending}
            className="px-4 py-2 text-sm rounded-lg bg-[var(--accent)] text-white hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            Add
          </button>
        </form>

        <div className="space-y-1">
          {topics.length === 0 && (
            <p className="text-sm text-[var(--muted)] py-6 text-center">
              No topics yet.
            </p>
          )}
          {topics.map((t) => (
            <div
              key={t.id}
              className="flex items-center justify-between rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-2"
            >
              <div>
                <span className="text-sm font-medium">{t.name}</span>
                <span className="text-xs text-[var(--muted)] ml-2">{t.query}</span>
              </div>
              {deletingId === t.id ? (
                <div className="flex gap-1">
                  <button
                    onClick={() => handleDeleteTopic(t.id)}
                    disabled={pending}
                    className="text-xs px-2 py-1 rounded bg-[var(--danger)] text-white"
                  >
                    Confirm
                  </button>
                  <button
                    onClick={() => setDeletingId(null)}
                    className="text-xs px-2 py-1 rounded bg-[var(--card-border)]"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setDeletingId(t.id)}
                  className="text-[var(--muted)] hover:text-[var(--danger)] text-sm"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Data Refresh</h2>
        <div className="flex gap-2 mb-3">
          {["fetch_news", "refresh_prices", "refresh_fx"].map((job) => (
            <button
              key={job}
              onClick={() => handleTriggerJob(job)}
              disabled={jobPending !== null}
              className="px-4 py-2 text-sm rounded-lg bg-[var(--card)] border border-[var(--card-border)] hover:border-[var(--accent)] transition-colors disabled:opacity-50"
            >
              {jobPending === job ? "Running..." : job.replace(/_/g, " ")}
            </button>
          ))}
        </div>
        {jobResult && (
          <p className="text-sm text-[var(--muted)] mb-3 font-mono">{jobResult}</p>
        )}

        <h3 className="text-sm font-medium text-[var(--muted)] mb-2">
          Recent Runs
        </h3>
        <div className="space-y-1">
          {jobRuns.length === 0 && (
            <p className="text-sm text-[var(--muted)] py-4">No runs yet.</p>
          )}
          {jobRuns.map((r) => (
            <div
              key={r.id}
              className="flex items-center justify-between rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-2 text-sm"
            >
              <div className="flex items-center gap-3">
                <span
                  className={`w-2 h-2 rounded-full ${
                    r.status === "success"
                      ? "bg-[var(--success)]"
                      : r.status === "failed"
                        ? "bg-[var(--danger)]"
                        : "bg-[var(--warning)]"
                  }`}
                />
                <span className="font-medium">{r.job_name}</span>
                <span className="text-[var(--muted)]">
                  {r.items_processed} items
                </span>
              </div>
              <span className="text-xs text-[var(--muted)]">
                {formatDate(r.started_at)}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
