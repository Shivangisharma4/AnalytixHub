import { NextResponse } from 'next/server';
import { getAllServicesWithFeatures, getServiceWithFeatures } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name');

  try {
    if (name) {
      const service = await getServiceWithFeatures(name);
      if (!service) {
        return NextResponse.json({ error: 'Service not found' }, { status: 404 });
      }
      return NextResponse.json(service);
    }

    const services = await getAllServicesWithFeatures();
    return NextResponse.json(services);
  } catch (error) {
    console.error('Error fetching services:', error);
    return NextResponse.json(
      { error: 'Failed to fetch services' },
      { status: 500 }
    );
  }
}
