import { NextResponse } from 'next/server';
import { getRankings, getAllRankings } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const context = searchParams.get('context');

  try {
    if (context) {
      const rankings = await getRankings(context);
      return NextResponse.json(rankings);
    }

    const allRankings = await getAllRankings();
    return NextResponse.json(allRankings);
  } catch (error) {
    console.error('Error fetching rankings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch rankings' },
      { status: 500 }
    );
  }
}
