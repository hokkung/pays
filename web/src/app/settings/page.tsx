import { api } from "@/lib/api";
import { SettingsClient } from "@/components/settings-client";

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
  const [topics, jobRuns] = await Promise.all([
    api.getTopics(),
    api.getJobRuns(),
  ]);

  return (
    <SettingsClient initialTopics={topics} initialJobRuns={jobRuns.items} />
  );
}
