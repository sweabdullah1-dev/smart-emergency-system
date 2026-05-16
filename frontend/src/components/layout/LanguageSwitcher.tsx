'use client';

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = (newLocale: string) => {
    const segments = pathname.split('/');
    segments[1] = newLocale;
    localStorage.setItem('seps_locale', newLocale);
    router.push(segments.join('/'));
  };

  return (
    <div className="flex gap-1 rounded-lg border border-white/10 p-1">
      {(['en', 'ar'] as const).map((l) => (
        <button
          key={l}
          onClick={() => switchLocale(l)}
          className={`rounded px-3 py-1 text-xs font-medium transition ${
            locale === l ? 'bg-emergency-blue text-white' : 'text-gray-400 hover:text-white'
          }`}
        >
          {l === 'en' ? 'EN' : 'عربي'}
        </button>
      ))}
    </div>
  );
}
