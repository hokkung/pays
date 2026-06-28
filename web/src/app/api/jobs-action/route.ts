import { NextRequest, NextResponse } from "next/server";
import { api } from "@/lib/api";

export async function GET() {
  const runs = await api.getJobRuns();
  return NextResponse.json(runs);
}

export async function POST(request: NextRequest) {
  const { job_name } = await request.json();
  const result = await api.triggerJob(job_name);
  return NextResponse.json(result);
}
