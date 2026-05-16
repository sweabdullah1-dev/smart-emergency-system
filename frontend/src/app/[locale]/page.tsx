'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Activity, Shield, Truck, Hospital, BarChart3 } from 'lucide-react';

export default function HomePage() {
  const t = useTranslations();
  const params = useParams();
  const locale = (params?.locale as string) || 'en';

  const cards = [
    { href: `/${locale}/login`, icon: Shield, label: t('nav.login'), color: 'text-emergency-blue' },
    { href: `/${locale}/citizen`, icon: Activity, label: t('nav.citizen'), color: 'text-emergency-red' },
    { href: `/${locale}/dispatcher`, icon: BarChart3, label: t('nav.dispatcher'), color: 'text-emergency-blue' },
    { href: `/${locale}/driver`, icon: Truck, label: t('nav.driver'), color: 'text-emergency-blue' },
    { href: `/${locale}/hospital`, icon: Hospital, label: t('nav.hospital'), color: 'text-green-400' },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-emergency-dark bg-grid-pattern bg-[length:32px_32px]">
      <div className="text-center mb-12">
        <Activity className="mx-auto h-16 w-16 text-emergency-red mb-4 animate-pulse" />
        <h1 className="text-3xl md:text-5xl font-bold text-white mb-2">{t('app.title')}</h1>
        <p className="text-gray-400">{t('app.subtitle')}</p>
        <p className="text-xs text-amber-500/80 mt-4 max-w-md mx-auto">{t('app.simulationNotice')}</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-3xl w-full">
        {cards.map((c) => (
          <Link
            key={c.href}
            href={c.href}
            className="glass-panel p-6 hover:border-emergency-blue/40 transition group"
          >
            <c.icon className={`h-8 w-8 ${c.color} mb-3 group-hover:scale-110 transition`} />
            <span className="text-white font-medium">{c.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
