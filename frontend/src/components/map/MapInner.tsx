'use client';

import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import type { Ambulance, Emergency, Hospital, TrafficZone } from '@/types';

const icon = (color: string) =>
  L.divIcon({
    className: 'custom-marker',
    html: `<div style="background:${color};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 0 8px ${color}"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

const emergencyIcon = icon('#ef4444');
const ambulanceIcon = icon('#3b82f6');
const hospitalIcon = icon('#22c55e');

function parsePolyline(polyline?: string): [number, number][] {
  if (!polyline) return [];
  try {
    const pts = JSON.parse(polyline) as number[][];
    return pts.map((p) => [p[0], p[1]] as [number, number]);
  } catch {
    return [];
  }
}

export default function MapInner({
  center = [24.7136, 46.6753],
  zoom = 11,
  emergencies = [],
  ambulances = [],
  hospitals = [],
  traffic = [],
  routePolyline,
  height = '400px',
}: {
  center?: [number, number];
  zoom?: number;
  emergencies?: Emergency[];
  ambulances?: Ambulance[];
  hospitals?: Hospital[];
  traffic?: TrafficZone[];
  routePolyline?: string;
  height?: string;
}) {
  useEffect(() => {
    delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
  }, []);

  const route = useMemo(() => parsePolyline(routePolyline), [routePolyline]);
  const trafficColor = (level: string) =>
    level === 'red' ? '#ef4444' : level === 'yellow' ? '#eab308' : '#22c55e';

  return (
    <div style={{ height, width: '100%' }} className="glass-panel overflow-hidden">
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {traffic.map((z) => (
          <Circle
            key={z.id}
            center={[z.center_lat, z.center_lng]}
            radius={z.radius_km * 1000}
            pathOptions={{
              color: trafficColor(z.level),
              fillColor: trafficColor(z.level),
              fillOpacity: 0.15,
            }}
          />
        ))}
        {route.length > 1 && <Polyline positions={route} pathOptions={{ color: '#3b82f6', weight: 4 }} />}
        {emergencies.map((e) => (
          <Marker key={`e-${e.id}`} position={[e.lat, e.lng]} icon={emergencyIcon}>
            <Popup>#{e.id} — {e.severity} — {e.status}</Popup>
          </Marker>
        ))}
        {ambulances.map((a) => (
          <Marker key={`a-${a.id}`} position={[a.lat, a.lng]} icon={ambulanceIcon}>
            <Popup>{a.plate_number} — {a.status}</Popup>
          </Marker>
        ))}
        {hospitals.map((h) => (
          <Marker key={`h-${h.id}`} position={[h.lat, h.lng]} icon={hospitalIcon}>
            <Popup>{h.name} — {h.city}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
