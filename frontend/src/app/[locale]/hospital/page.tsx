'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { DashboardShell } from '@/components/layout/DashboardShell';
import LiveMap from '@/components/map/LiveMap';
import { api } from '@/lib/api';
import { useRealtime } from '@/hooks/useRealtime';
import type { Emergency, Ambulance, Hospital } from '@/types';

export default function HospitalPage() {
  const t = useTranslations('hospital');
  const [queue, setQueue] = useState<Emergency[]>([]);
  const [ambulances, setAmbulances] = useState<Ambulance[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);

  const refresh = useCallback(async () => {
    const ems = await api<Emergency[]>('/emergencies');
    const incoming = ems.filter((e) =>
      ['transporting', 'picked_up', 'arrived_hospital', 'assigned'].includes(e.status)
    );
    setQueue(incoming);
    setAmbulances(await api<Ambulance[]>('/ambulances'));
    setHospitals(await api<Hospital[]>('/hospitals'));
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  useRealtime(() => refresh());

  return (
    <DashboardShell role="hospital">
      <h2 className="text-2xl font-bold text-white mb-4">{t('title')}</h2>
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="glass-panel p-4">
          <h3 className="font-semibold text-green-400 mb-3">{t('incoming')}</h3>
          {queue.length === 0 ? (
            <p className="text-gray-500 text-sm">No incoming cases</p>
          ) : (
            queue.map((e) => (
              <div key={e.id} className="p-3 mb-2 rounded-lg border border-white/10">
                <p className="font-bold text-white">#{e.id} — {e.emergency_type}</p>
                <p className="text-sm text-gray-400">
                  {t('ambulanceEta')}: {e.eta_minutes?.toFixed(1) ?? '—'} min
                </p>
                <p className="text-xs text-emergency-blue">{e.status}</p>
              </div>
            ))
          )}
        </div>
        <LiveMap
          emergencies={queue}
          ambulances={ambulances}
          hospitals={hospitals.slice(0, 20)}
          height="450px"
        />
      </div>
    </DashboardShell>
  );
}
