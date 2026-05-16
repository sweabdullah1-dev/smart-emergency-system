const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

type Handler = (data: Record<string, unknown>) => void;

let socket: WebSocket | null = null;
const handlers: Set<Handler> = new Set();

export function connectWebSocket(channel = 'all') {
  if (socket?.readyState === WebSocket.OPEN) return socket;
  socket = new WebSocket(`${WS_URL}/ws/${channel}`);
  socket.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      handlers.forEach((h) => h(data));
    } catch {
      /* ignore */
    }
  };
  socket.onclose = () => {
    setTimeout(() => connectWebSocket(channel), 3000);
  };
  return socket;
}

export function subscribe(handler: Handler) {
  handlers.add(handler);
  return () => handlers.delete(handler);
}

export function playAlertSound() {
  if (typeof window === 'undefined') return;
  try {
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.value = 0.15;
    osc.start();
    setTimeout(() => {
      osc.stop();
      ctx.close();
    }, 400);
  } catch {
    /* fallback silent */
  }
}
