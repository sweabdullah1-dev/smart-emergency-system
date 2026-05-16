const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('seps_token');
}

export function setToken(token: string) {
  localStorage.setItem('seps_token', token);
}

export function clearAuth() {
  localStorage.removeItem('seps_token');
  localStorage.removeItem('seps_user');
}

export function getStoredUser(): { id: number; email: string; role: string; full_name: string } | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem('seps_user');
  return raw ? JSON.parse(raw) : null;
}

export function setStoredUser(user: object) {
  localStorage.setItem('seps_user', JSON.stringify(user));
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_URL}/api${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export async function login(email: string, password: string) {
  const data = await api<{ access_token: string }>('/auth/login/json', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  const user = await api<{ id: number; email: string; role: string; full_name: string }>('/auth/me');
  setStoredUser(user);
  return user;
}
