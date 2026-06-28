"use client";

import { useState, useCallback } from "react";
import type { ArticleListResponse, TopicResponse } from "@/lib/types";
import { timeAgo } from "@/lib/format";

interface NewsListProps {
  topics: TopicResponse[];
  initialData: ArticleListResponse;
}

export function NewsList({ topics, initialData }: NewsListProps) {
  const [data, setData] = useState(initialData);
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const loadMore = useCallback(async () => {
    if (!data.next_cursor) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({
        cursor: data.next_cursor,
        limit: "50",
      });
      if (selectedTopic) params.set("topic", selectedTopic);
      const res = await fetch(
        `/api/news-proxy?${params}`,
      );
      const next: ArticleListResponse = await res.json();
      setData((prev) => ({
        items: [...prev.items, ...next.items],
        next_cursor: next.next_cursor,
      }));
    } finally {
      setLoading(false);
    }
  }, [data.next_cursor, selectedTopic]);

  const filterTopic = useCallback(async (topic: string) => {
    setSelectedTopic(topic);
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (topic) params.set("topic", topic);
      const res = await fetch(`/api/news-proxy?${params}`);
      const next: ArticleListResponse = await res.json();
      setData(next);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => filterTopic("")}
          className={`px-3 py-1 text-sm rounded-full transition-colors ${
            !selectedTopic
              ? "bg-[var(--accent)] text-white"
              : "bg-[var(--card)] text-[var(--muted)] hover:text-[var(--foreground)]"
          }`}
        >
          All
        </button>
        {topics.map((t) => (
          <button
            key={t.id}
            onClick={() => filterTopic(t.name)}
            className={`px-3 py-1 text-sm rounded-full transition-colors ${
              selectedTopic === t.name
                ? "bg-[var(--accent)] text-white"
                : "bg-[var(--card)] text-[var(--muted)] hover:text-[var(--foreground)]"
            }`}
          >
            {t.name}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {data.items.length === 0 && (
          <p className="text-sm text-[var(--muted)] py-12 text-center">
            No articles found.
          </p>
        )}
        {data.items.map((a) => (
          <a
            key={a.id}
            href={a.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`block rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-3 hover:border-[var(--accent)] transition-colors ${
              a.is_read ? "opacity-50" : ""
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium line-clamp-2">{a.title}</p>
                {a.summary && (
                  <p className="text-xs text-[var(--muted)] mt-1 line-clamp-1">
                    {a.summary.replace(/<[^>]+>/g, "")}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-2">
                  {a.topics.map((t) => (
                    <span
                      key={t.id}
                      className="text-xs px-2 py-0.5 rounded-full bg-[var(--accent-muted)] text-[var(--accent)]"
                    >
                      {t.name}
                    </span>
                  ))}
                  <span className="text-xs text-[var(--muted)]">
                    {a.source}
                  </span>
                </div>
              </div>
              <span className="text-xs text-[var(--muted)] shrink-0">
                {timeAgo(a.published_at)}
              </span>
            </div>
          </a>
        ))}
      </div>

      {data.next_cursor && (
        <button
          onClick={loadMore}
          disabled={loading}
          className="w-full py-2 text-sm text-[var(--accent)] hover:bg-[var(--card)] rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? "Loading..." : "Load more"}
        </button>
      )}
    </div>
  );
}
