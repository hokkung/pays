import { api } from "@/lib/api";
import { formatTHB, formatPrice, timeAgo } from "@/lib/format";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let assets: Awaited<ReturnType<typeof api.getAssetsWithLatest>> = [];
  let fxRates: Awaited<ReturnType<typeof api.getFxRates>> = { items: [] };
  let news: Awaited<ReturnType<typeof api.getNews>> = { items: [], next_cursor: null };

  try {
    [assets, fxRates, news] = await Promise.all([
      api.getAssetsWithLatest(),
      api.getFxRates(),
      api.getNews({ limit: 5 }),
    ]);
  } catch {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="rounded-xl border border-[var(--danger)] bg-[var(--card)] p-8 text-center">
          <p className="text-[var(--danger)] font-medium">
            Cannot connect to backend
          </p>
          <p className="text-sm text-[var(--muted)] mt-2">
            Make sure the API server is running on port 8000.
          </p>
        </div>
      </div>
    );
  }

  const totalTHB = assets.reduce(
    (sum, a) => sum + (a.price_in_thb ?? 0),
    0,
  );

  const usdThb = fxRates.items.find(
    (r) => r.base_ccy === "USD" && r.quote_ccy === "THB",
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-[var(--muted)] text-sm mt-1">
          Portfolio overview
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-[var(--card-border)] bg-[var(--card)] p-5">
          <p className="text-xs text-[var(--muted)] uppercase tracking-wide">
            Portfolio Value (THB)
          </p>
          <p className="text-3xl font-bold mt-2">
            ฿{formatTHB(totalTHB)}
          </p>
        </div>
        <div className="rounded-xl border border-[var(--card-border)] bg-[var(--card)] p-5">
          <p className="text-xs text-[var(--muted)] uppercase tracking-wide">
            Tracked Assets
          </p>
          <p className="text-3xl font-bold mt-2">{assets.length}</p>
        </div>
        <div className="rounded-xl border border-[var(--card-border)] bg-[var(--card)] p-5">
          <p className="text-xs text-[var(--muted)] uppercase tracking-wide">
            USD / THB
          </p>
          <p className="text-3xl font-bold mt-2">
            {usdThb ? formatTHB(parseFloat(usdThb.rate)) : "-"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Watchlist</h2>
            <Link
              href="/assets"
              className="text-sm text-[var(--accent)] hover:underline"
            >
              View all →
            </Link>
          </div>
          <div className="space-y-2">
            {assets.length === 0 && (
              <p className="text-sm text-[var(--muted)] py-8 text-center">
                No assets yet. Add some in the Assets page.
              </p>
            )}
            {assets.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-3"
              >
                <div>
                  <span className="font-semibold">{a.symbol}</span>
                  <span className="text-[var(--muted)] text-sm ml-2">
                    {a.name}
                  </span>
                </div>
                <div className="text-right">
                  <p className="font-mono text-sm">
                    {a.latest_price !== null
                      ? `$${formatPrice(a.latest_price)}`
                      : "-"}
                  </p>
                  <p className="text-xs text-[var(--muted)]">
                    ฿{formatTHB(a.price_in_thb)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Latest News</h2>
            <Link
              href="/news"
              className="text-sm text-[var(--accent)] hover:underline"
            >
              View all →
            </Link>
          </div>
          <div className="space-y-2">
            {news.items.length === 0 && (
              <p className="text-sm text-[var(--muted)] py-8 text-center">
                No articles yet. Trigger a fetch in Settings.
              </p>
            )}
            {news.items.map((a) => (
              <a
                key={a.id}
                href={a.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-3 hover:border-[var(--accent)] transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-medium line-clamp-2">
                    {a.title}
                  </p>
                  <span className="text-xs text-[var(--muted)] shrink-0">
                    {timeAgo(a.published_at)}
                  </span>
                </div>
                {a.topics.length > 0 && (
                  <div className="flex gap-1.5 mt-2">
                    {a.topics.map((t) => (
                      <span
                        key={t.id}
                        className="text-xs px-2 py-0.5 rounded-full bg-[var(--accent-muted)] text-[var(--accent)]"
                      >
                        {t.name}
                      </span>
                    ))}
                  </div>
                )}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
