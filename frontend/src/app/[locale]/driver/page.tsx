'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { DashboardShell } from '@/components/layout/DashboardShell';
import LiveMap from '@/components/map/LiveMap';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useRealtime } from '@/hooks/useRealtime';
import { playAlertSound } from '@/lib/websocket';
import type { Emergency, Ambulance } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';

export default function DriverPage() {
  const t = useTranslations('driver');
  const [assignment, setAssignment] = useState<Emergency | null>(null);
  const [ambulances, setAmbulances] = useState<Ambulance[]>([]);
  const [showPopup, setShowPopup] = useState(false);

  const refresh = useCallback(async () => {
    const ems = await api<Emergency[]>('/emergencies');
    const active = ems.find((e) =>
      ['assigned', 'accepted', 'en_route', 'on_scene', 'picked_up', 'transporting'].includes(e.status)
    );
    setAssignment(active || null);
    setAmbulances(await api<Ambulance[]>('/ambulances'));
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  useRealtime((data) => {
    if (data.type === 'emergency_assigned' || data.type === 'notification') {
      playAlertSound();
      setShowPopup(true);
      refresh();
    }
    if (data.type === 'ambulance_position') refresh();
  });

  const accept = async () => {
    if (!assignment) return;
    await api(`/emergencies/${assignment.id}/accept`, { method: 'POST' });
    setShowPopup(false);
    refresh();
  };

  const setStatus = async (status: string) => {
    if (!assignment) return;
    await api(`/emergencies/${assignment.id}/status/${status}`, { method: 'POST' });
    refresh();
  };

  return (
    <DashboardShell role="driver">
      <h2 className="text-2xl font-bold text-white mb-4">{t('title')}</h2>

      <AnimatePresence>
        {showPopup && assignment && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          >
            <div className="glass-panel p-8 max-w-md border-2 border-emergency-red animate-pulse">
              <h3 className="text-xl font-bold text-emergency-red mb-4">{t('newAssignment')}</h3>
              <p className="text-white mb-4">Emergency #{assignment.id} — {assignment.severity}</p>
              <div className="flex gap-2">
                <Button variant="danger" onClick={accept}>
                  {t('accept')}
                </Button>
                <Button variant="ghost" onClick={() => setShowPopup(false)}>
                  Later
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {assignment ? (
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="glass-panel p-4 space-y-3">
            <p className="text-lg font-bold text-white">#{assignment.id}</p>
            <p className="text-gray-400">ETA: {assignment.eta_minutes?.toFixed(1)} min</p>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => setStatus('en_route')}>{t('onTheWay')}</Button>
              <Button onClick={() => setStatus('on_scene')}>{t('arrived')}</Button>
              <Button onClick={() => setStatus('picked_up')}>{t('pickedUp')}</Button>
              <Button variant="danger" onClick={() => setStatus('completed')}>
                {t('completed')}
              </Button>
            </div>
          </div>
          <LiveMap
            center={[assignment.lat, assignment.lng]}
            emergencies={[assignment]}
            ambulances={ambulances}
            routePolyline={assignment.route_polyline}
            height="400px"
          />
        </div>
      ) : (
        <p className="text-gray-500">No active assignment. Waiting for dispatch...</p>
      )}
    </DashboardShell>
  );
}
