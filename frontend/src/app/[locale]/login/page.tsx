'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { login } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';
import { toast } from 'sonner';

const DEMOS = [
  { email: 'admin@system.com', password: 'admin123', role: 'dispatcher' },
  { email: 'driver@system.com', password: 'driver123', role: 'driver' },
  { email: 'citizen@system.com', password: 'citizen123', role: 'citizen' },
  { email: 'hospital@system.com', password: 'hospital123', role: 'hospital' },
];

export default function LoginPage() {
  const t = useTranslations('auth');
  const params = useParams();
  const locale = (params?.locale as string) || 'en';
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e?: React.FormEvent, demo?: (typeof DEMOS)[0]) => {
    e?.preventDefault();
    setLoading(true);
    try {
      const creds = demo || { email, password, role: '' };
      const user = await login(creds.email, creds.password);
      toast.success('Logged in');
      const routes: Record<string, string> = {
        citizen: `/${locale}/citizen`,
        dispatcher: `/${locale}/dispatcher`,
        driver: `/${locale}/driver`,
        hospital: `/${locale}/hospital`,
        admin: `/${locale}/dispatcher`,
      };
      router.push(routes[user.role] || `/${locale}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-emergency-dark">
      <div className="absolute top-4 end-4">
        <LanguageSwitcher />
      </div>
      <form onSubmit={handleLogin} className="glass-panel w-full max-w-md p-8 space-y-4">
        <h1 className="text-2xl font-bold text-white">{t('signIn')}</h1>
        <div>
          <label className="text-sm text-gray-400">{t('email')}</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2 text-white"
            required
          />
        </div>
        <div>
          <label className="text-sm text-gray-400">{t('password')}</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg bg-black/40 border border-white/10 px-3 py-2 text-white"
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={loading}>
          {t('signIn')}
        </Button>
        <p className="text-xs text-gray-500 pt-4">{t('demoAccounts')}</p>
        <div className="grid grid-cols-2 gap-2">
          {DEMOS.map((d) => (
            <Button
              key={d.email}
              type="button"
              variant="outline"
              size="sm"
              onClick={() => handleLogin(undefined, d)}
            >
              {t(d.role as 'admin')}
            </Button>
          ))}
        </div>
      </form>
    </div>
  );
}
