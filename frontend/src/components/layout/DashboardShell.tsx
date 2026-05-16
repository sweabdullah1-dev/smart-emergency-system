'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { usePathname } from 'next/navigation';
import { LanguageSwitcher } from './LanguageSwitcher';
import { clearAuth, getStoredUser } from '@/lib/api';
import { Activity, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';

export function DashboardShell({ children, role }: { children: React.ReactNode; role?: string }) {
  const t = useTranslations();
  const locale = useLocale();
  const pathname = usePathname();
  const user = getStoredUser();
  const dir = locale === 'ar' ? 'rtl' : 'ltr';

  const links: Record<string, { href: string; label: string }[]> = {
    citizen: [{ href: `/${locale}/citizen`, label: t('nav.citizen') }],
    dispatcher: [
      { href: `/${locale}/dispatcher`, label: t('nav.dispatcher') },
      { href: `/${locale}/analytics`, label: t('nav.analytics') },
    ],
    driver: [{ href: `/${locale}/driver`, label: t('nav.driver') }],
    hospital: [{ href: `/${locale}/hospital`, label: t('nav.hospital') }],
    admin: [
      { href: `/${locale}/dispatcher`, label: t('nav.dispatcher') },
      { href: `/${locale}/analytics`, label: t('nav.analytics') },
    ],
  };

  const navLinks = links[user?.role || role || 'citizen'] || links.citizen;

  return (
    <div dir={dir} className="min-h-screen bg-emergency-dark bg-grid-pattern bg-[length:24px_24px]">
      <header className="sticky top-0 z-50 border-b border-white/5 glass-panel mx-4 mt-4 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="h-6 w-6 text-emergency-red animate-pulse_slow" />
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h1 className="text-sm font-bold text-white md:text-base">{t('app.title')}</h1>
            <p className="text-[10px] text-gray-500 hidden sm:block">{t('app.simulationNotice')}</p>
          </motion.div>
        </div>
        <nav className="flex items-center gap-4">
          {navLinks.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`text-sm ${pathname.startsWith(l.href) ? 'text-emergency-blue' : 'text-gray-400 hover:text-white'}`}
            >
              {l.label}
            </Link>
          ))}
          <LanguageSwitcher />
          <button
            onClick={() => {
              clearAuth();
              window.location.href = `/${locale}/login`;
            }}
            className="text-gray-400 hover:text-emergency-red"
            title={t('nav.logout')}
          >
            <LogOut className="h-4 w-4" />
          </button>
        </nav>
      </header>
      <main className="p-4 md:p-6">{children}</main>
    </div>
  );
}
