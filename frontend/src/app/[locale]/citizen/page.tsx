'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { DashboardShell } from '@/components/layout/DashboardShell';
import LiveMap from '@/components/map/LiveMap';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useRealtime } from '@/hooks/useRealtime';
import type { Emergency, Ambulance, Hospital } from '@/types';
import { motion } from 'framer-motion';

export default function CitizenPage() {
  const t = useTranslations('emergency');
  const [lat, setLat] = useState(24.7136);
  const [lng, setLng] = useState(46.6753);
  const [form, setForm] = useState({
    reporter_name: '',
    reporter_phone: '',
    emergency_type: 'cardiac',
    severity: 'high',
    notes: '',
  });
  const [active, setActive] = useState<Emergency | null>(null);
  const [ambulances, setAmbulances] = useState<Ambulance[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);

  const refresh = useCallback(async () => {
    const ems = await api<Emergency[]>('/emergencies');
    const latest = ems.find((e) => !['completed', 'cancelled'].includes(e.status));
    setActive(latest || null);
    const [amb, hosp] = await Promise.all([
      api<Ambulance[]>('/ambulances'),
      api<Hospital[]>('/hospitals'),
    ]);
    setAmbulances(amb);
    setHospitals(hosp);
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [refresh]);

  useRealtime(() => refresh());

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((p) => {
        setLat(p.coords.latitude);
        setLng(p.coords.longitude);
      });
    }
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const em = await api<Emergency>('/emergencies', {
      method: 'POST',
      body: JSON.stringify({ ...form, lat, lng }),
    });
    setActive(em);
    refresh();
  };

  const assignedHospital = hospitals.find((h) => h.id === active?.hospital_id);

  return (
    <DashboardShell role="citizen">
      <div className="grid lg:grid-cols-2 gap-6">
        <motion.form
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onSubmit={submit}
          className="glass-panel p-6 space-y-4"
        >
          <h2 className="text-xl font-bold text-emergency-red">{t('report')}</h2>
          <input
            placeholder={t('fullName')}
            className="w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2"
            value={form.reporter_name}
            onChange={(e) => setForm({ ...form, reporter_name: e.target.value })}
            required
          />
          <input
            placeholder={t('phone')}
            className="w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2"
            value={form.reporter_phone}
            onChange={(e) => setForm({ ...form, reporter_phone: e.target.value })}
            required
          />
          <select
            className="w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2"
            value={form.emergency_type}
            onChange={(e) => setForm({ ...form, emergency_type: e.target.value })}
          >
            {['cardiac', 'trauma', 'respiratory', 'stroke', 'accident', 'fire_related', 'other'].map((k) => (
              <option key={k} value={k}>
                {t(`types.${k}`)}
              </option>
            ))}
          </select>
          <select
            className="w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2"
            value={form.severity}
            onChange={(e) => setForm({ ...form, severity: e.target.value })}
          >
            {['low', 'medium', 'high', 'critical'].map((k) => (
              <option key={k} value={k}>
                {t(`severities.${k}`)}
              </option>
            ))}
          </select>
          <textarea
            placeholder={t('notes')}
            className="w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
          <p className="text-xs text-gray-500">
            GPS: {lat.toFixed(4)}, {lng.toFixed(4)}
          </p>
          <Button type="submit" variant="danger" className="w-full">
            {t('submit')}
          </Button>
        </motion.form>

        <div className="space-y-4">
          {active && (
            <div className="glass-panel p-4 border-l-4 border-emergency-red">
              <h3 className="font-bold text-white">#{active.id} — {t(`statuses.${active.status}`)}</h3>
              <p className="text-sm text-gray-400">
                {t('eta')}: {active.eta_minutes?.toFixed(1) ?? '—'} min
              </p>
              {assignedHospital && (
                <p className="text-sm text-emergency-blue">
                  {t('assignedHospital')}: {assignedHospital.name}
                </p>
              )}
            </div>
          )}
          <LiveMap
            center={[lat, lng]}
            emergencies={active ? [active] : []}
            ambulances={ambulances}
            hospitals={hospitals.slice(0, 30)}
            routePolyline={active?.route_polyline}
            height="450px"
          />
        </div>
      </div>
    </DashboardShell>
  );
}
