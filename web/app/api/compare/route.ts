import { NextResponse } from 'next/server';
import { getFeatureComparison } from '@/lib/db';

export async function GET() {
  try {
    const comparison = await getFeatureComparison();
    return NextResponse.json(comparison);
  } catch (error) {
    console.error('Error fetching comparison:', error);
    return NextResponse.json(
      { error: 'Failed to fetch comparison' },
      { status: 500 }
    );
  }
}
