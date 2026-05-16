'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { DashboardShell } from '@/components/layout/DashboardShell';
import { api } from '@/lib/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#eab308', '#a855f7', '#ec4899'];

interface AnalyticsData {
  total_emergencies: number;
  completed: number;
  active: number;
  avg_response_time_minutes: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  hospital_load: { name: string; city: string; load_percent: number }[];
  hotspots: { lat: number; lng: number; weight: number }[];
}

export default function AnalyticsPage() {
  const t = useTranslations('analytics');
  const [data, setData] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    api<AnalyticsData>('/analytics').then(setData).catch(console.error);
  }, []);

  const typeData = data
    ? Object.entries(data.by_type).map(([name, value]) => ({ name, value }))
    : [];
  const severityData = data
    ? Object.entries(data.by_severity).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <DashboardShell role="dispatcher">
      <h2 className="text-2xl font-bold text-white mb-6">{t('title')}</h2>
      {!data ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              { label: t('totalEmergencies'), value: data.total_emergencies },
              { label: t('active'), value: data.active },
              { label: t('avgResponse'), value: `${data.avg_response_time_minutes} min` },
              { label: 'Completed', value: data.completed },
            ].map((s) => (
              <div key={s.label} className="glass-panel p-4">
                <p className="text-xs text-gray-500">{s.label}</p>
                <p className="text-2xl font-bold text-white">{s.value}</p>
              </div>
            ))}
          </div>
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="glass-panel p-4 h-72">
              <h3 className="text-sm text-gray-400 mb-2">{t('byType')}</h3>
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={typeData}>
                  <XAxis dataKey="name" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ background: '#12121a', border: '1px solid #333' }} />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="glass-panel p-4 h-72">
              <h3 className="text-sm text-gray-400 mb-2">{t('bySeverity')}</h3>
              <ResponsiveContainer width="100%" height="90%">
                <PieChart>
                  <Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                    {severityData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#12121a', border: '1px solid #333' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="glass-panel p-4 lg:col-span-2">
              <h3 className="text-sm text-gray-400 mb-2">{t('hospitalLoad')}</h3>
              <div className="grid md:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
                {data.hospital_load.map((h) => (
                  <div key={h.name} className="flex items-center gap-2 text-sm">
                    <span className="text-gray-400 w-48 truncate">{h.name}</span>
                    <div className="flex-1 h-2 bg-black/40 rounded">
                      <div
                        className="h-full bg-emergency-red rounded"
                        style={{ width: `${Math.min(h.load_percent, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs w-10">{h.load_percent}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </DashboardShell>
  );
}
