import { NextRequest, NextResponse } from "next/server";
import { api } from "@/lib/api";

export async function POST(request: NextRequest) {
  const body = await request.json();
  await api.createAsset(body);
  return NextResponse.json({ ok: true });
}

export async function DELETE(request: NextRequest) {
  const { id } = await request.json();
  await api.deleteAsset(id);
  return NextResponse.json({ ok: true });
}
