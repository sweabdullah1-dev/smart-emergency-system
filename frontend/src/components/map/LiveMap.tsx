'use client';

import { useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import type { Ambulance, Emergency, Hospital, TrafficZone } from '@/types';

const MapInner = dynamic(() => import('./MapInner'), { ssr: false, loading: () => (
  <div className="glass-panel flex h-[400px] items-center justify-center text-gray-500">Loading map...</div>
)});

interface LiveMapProps {
  center?: [number, number];
  zoom?: number;
  emergencies?: Emergency[];
  ambulances?: Ambulance[];
  hospitals?: Hospital[];
  traffic?: TrafficZone[];
  routePolyline?: string;
  height?: string;
}

export default function LiveMap(props: LiveMapProps) {
  return <MapInner {...props} />;
}
