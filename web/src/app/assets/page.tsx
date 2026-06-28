import { api } from "@/lib/api";
import { AssetsClient } from "@/components/assets-client";

export const dynamic = "force-dynamic";

export default async function AssetsPage() {
  const assets = await api.getAssetsWithLatest();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Assets</h1>
        <p className="text-[var(--muted)] text-sm mt-1">
          Watchlist with latest prices and THB conversion
        </p>
      </div>
      <AssetsClient initialAssets={assets} />
    </div>
  );
}
