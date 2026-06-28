"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import type { AssetWithLatestResponse, AssetType } from "@/lib/types";
import { formatTHB, formatPrice, formatDate } from "@/lib/format";

interface AssetsClientProps {
  initialAssets: AssetWithLatestResponse[];
}

const assetTypes: AssetType[] = ["stock", "etf", "gold", "bond"];

const typeColors: Record<string, string> = {
  stock: "text-green-400",
  etf: "text-blue-400",
  gold: "text-yellow-400",
  bond: "text-purple-400",
};

export function AssetsClient({ initialAssets }: AssetsClientProps) {
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [pending, startTransition] = useTransition();

  const [symbol, setSymbol] = useState("");
  const [name, setName] = useState("");
  const [assetType, setAssetType] = useState<AssetType>("stock");
  const [currency, setCurrency] = useState("USD");

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol.trim() || !name.trim()) return;
    startTransition(async () => {
      await fetch("/api/assets-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: symbol.trim().toUpperCase(),
          name: name.trim(),
          asset_type: assetType,
          currency: currency.trim().toUpperCase() || "USD",
        }),
      });
      setSymbol("");
      setName("");
      setAssetType("stock");
      setCurrency("USD");
      setShowForm(false);
      router.refresh();
    });
  };

  const handleDelete = async (id: number) => {
    startTransition(async () => {
      await fetch("/api/assets-action", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      setDeletingId(null);
      router.refresh();
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-[var(--muted)]">{initialAssets.length} asset(s)</p>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-1.5 text-sm rounded-lg bg-[var(--accent)] text-white hover:opacity-90 transition-opacity"
        >
          {showForm ? "Cancel" : "+ Add Asset"}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleAdd}
          className="rounded-xl border border-[var(--card-border)] bg-[var(--card)] p-4 space-y-3"
        >
          <div className="grid grid-cols-2 gap-3">
            <input
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="Symbol (e.g. AAPL)"
              className="bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm focus:border-[var(--accent)] outline-none"
            />
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Name (e.g. Apple Inc.)"
              className="bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm focus:border-[var(--accent)] outline-none"
            />
            <select
              value={assetType}
              onChange={(e) => setAssetType(e.target.value as AssetType)}
              className="bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm focus:border-[var(--accent)] outline-none"
            >
              {assetTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <input
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              placeholder="Currency"
              maxLength={3}
              className="bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm focus:border-[var(--accent)] outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={pending}
            className="px-4 py-2 text-sm rounded-lg bg-[var(--accent)] text-white hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {pending ? "Adding..." : "Add"}
          </button>
        </form>
      )}

      <div className="space-y-2">
        {initialAssets.length === 0 && (
          <p className="text-sm text-[var(--muted)] py-12 text-center">
            No assets yet. Click &quot;Add Asset&quot; to start tracking.
          </p>
        )}
        {initialAssets.map((a) => (
          <div
            key={a.id}
            className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`font-mono font-bold ${typeColors[a.asset_type]}`}>
                  {a.symbol}
                </span>
                <div>
                  <p className="text-sm">{a.name}</p>
                  <p className="text-xs text-[var(--muted)]">
                    {a.asset_type} · {a.currency}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="font-mono text-sm">
                    {a.latest_price !== null
                      ? `$${formatPrice(a.latest_price)}`
                      : "-"}
                  </p>
                  <p className="text-xs text-[var(--muted)]">
                    ฿{formatTHB(a.price_in_thb)}
                  </p>
                  {a.latest_price_as_of && (
                    <p className="text-xs text-[var(--muted)]">
                      {formatDate(a.latest_price_as_of)}
                    </p>
                  )}
                </div>
                {deletingId === a.id ? (
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleDelete(a.id)}
                      disabled={pending}
                      className="text-xs px-2 py-1 rounded bg-[var(--danger)] text-white hover:opacity-90"
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
                    onClick={() => setDeletingId(a.id)}
                    className="text-[var(--muted)] hover:text-[var(--danger)] text-sm"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
