import { NextRequest, NextResponse } from "next/server";
import { api } from "@/lib/api";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const topic = searchParams.get("topic") ?? undefined;
  const cursor = searchParams.get("cursor") ?? undefined;
  const limit = searchParams.get("limit") ?? undefined;

  const data = await api.getNews({
    topic,
    cursor: cursor ?? undefined,
    limit: limit ? parseInt(limit, 10) : undefined,
  });

  return NextResponse.json(data);
}
