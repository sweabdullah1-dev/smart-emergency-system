'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { DashboardShell } from '@/components/layout/DashboardShell';
import LiveMap from '@/components/map/LiveMap';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useRealtime } from '@/hooks/useRealtime';
import type { Emergency, Ambulance, Hospital, TrafficZone } from '@/types';

export default function DispatcherPage() {
  const t = useTranslations('dispatcher');
  const [emergencies, setEmergencies] = useState<Emergency[]>([]);
  const [ambulances, setAmbulances] = useState<Ambulance[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [traffic, setTraffic] = useState<TrafficZone[]>([]);
  const [selected, setSelected] = useState<Emergency | null>(null);
  const [soundOn, setSoundOn] = useState(true);

  const refresh = useCallback(async () => {
    const [ems, amb, hosp, tr] = await Promise.all([
      api<Emergency[]>('/emergencies'),
      api<Ambulance[]>('/ambulances'),
      api<Hospital[]>('/hospitals'),
      api<TrafficZone[]>('/traffic'),
    ]);
    setEmergencies(ems);
    setAmbulances(amb);
    setHospitals(hosp);
    setTraffic(tr);
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  useRealtime(() => refresh());

  const assign = async (ambulanceId: number) => {
    if (!selected) return;
    await api(`/emergencies/${selected.id}/assign`, {
      method: 'POST',
      body: JSON.stringify({ ambulance_id: ambulanceId, override: true }),
    });
    refresh();
  };

  const nearby = selected
    ? ambulances
        .map((a) => ({ ...a, dist: Math.hypot(a.lat - selected.lat, a.lng - selected.lng) }))
        .sort((x, y) => x.dist - y.dist)
        .slice(0, 5)
    : [];

  return (
    <DashboardShell role="dispatcher">
      <h2 className="text-2xl font-bold text-white mb-4">{t('title')}</h2>
      <div className="grid xl:grid-cols-3 gap-4">
        <div className="glass-panel p-4 max-h-[500px] overflow-y-auto">
          <div className="flex justify-between mb-3">
            <h3 className="font-semibold text-emergency-red">{t('queue')}</h3>
            <label className="text-xs flex items-center gap-1">
              <input type="checkbox" checked={soundOn} onChange={(e) => setSoundOn(e.target.checked)} />
              {t('soundAlert')}
            </label>
          </div>
          {emergencies.map((e) => (
            <button
              key={e.id}
              onClick={() => setSelected(e)}
              className={`w-full text-start p-3 mb-2 rounded-lg border ${
                selected?.id === e.id ? 'border-emergency-blue bg-emergency-blue/10' : 'border-white/5'
              }`}
            >
              <span className="text-emergency-red font-bold">#{e.id}</span> — {e.severity} — {e.status}
              <br />
              <span className="text-xs text-gray-500">{e.reporter_name}</span>
            </button>
          ))}
        </div>

        <div className="xl:col-span-2 space-y-4">
          <LiveMap
            emergencies={emergencies.filter((e) => e.status !== 'completed')}
            ambulances={ambulances}
            hospitals={hospitals}
            traffic={traffic}
            routePolyline={selected?.route_polyline}
            height="380px"
          />
          {selected && (
            <div className="glass-panel p-4">
              <h3 className="font-semibold mb-2">{t('assign')} — #{selected.id}</h3>
              <div className="flex flex-wrap gap-2">
                {nearby.map((a) => (
                  <Button key={a.id} size="sm" variant="outline" onClick={() => assign(a.id)}>
                    {a.plate_number} ({a.status})
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
