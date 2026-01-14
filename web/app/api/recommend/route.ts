import { NextResponse } from 'next/server';
import { getRecommendations } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const context = searchParams.get('context') || 'personal_use';
  const free_tier = searchParams.get('free_tier') === 'true';
  const collaboration = searchParams.get('collaboration') === 'true';
  const offline_mode = searchParams.get('offline_mode') === 'true';
  const api_available = searchParams.get('api_available') === 'true';

  try {
    const recommendations = await getRecommendations({
      context,
      free_tier: searchParams.has('free_tier') ? free_tier : undefined,
      collaboration: searchParams.has('collaboration') ? collaboration : undefined,
      offline_mode: searchParams.has('offline_mode') ? offline_mode : undefined,
      api_available: searchParams.has('api_available') ? api_available : undefined,
    });

    return NextResponse.json(recommendations);
  } catch (error) {
    console.error('Error getting recommendations:', error);
    return NextResponse.json(
      { error: 'Failed to get recommendations' },
      { status: 500 }
    );
  }
}
