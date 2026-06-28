import { api } from "@/lib/api";
import { NewsList } from "@/components/news-list";

export const dynamic = "force-dynamic";

export default async function NewsPage() {
  const [topics, initialNews] = await Promise.all([
    api.getTopics(),
    api.getNews({ limit: 50 }),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">News</h1>
        <p className="text-[var(--muted)] text-sm mt-1">
          {initialNews.items.length} article(s) loaded
        </p>
      </div>
      <NewsList topics={topics} initialData={initialNews} />
    </div>
  );
}
