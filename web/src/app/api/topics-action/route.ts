import { NextRequest, NextResponse } from "next/server";
import { api } from "@/lib/api";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const result = await api.createTopic(body);
  return NextResponse.json(result);
}

export async function DELETE(request: NextRequest) {
  const { id } = await request.json();
  await api.deleteTopic(id);
  return NextResponse.json({ ok: true });
}
