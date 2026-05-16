'use client';

import { useEffect } from 'react';
import { connectWebSocket, subscribe, playAlertSound } from '@/lib/websocket';
import { toast } from 'sonner';

export function useRealtime(onEvent?: (data: Record<string, unknown>) => void) {
  useEffect(() => {
    connectWebSocket('all');
    const unsub = subscribe((data) => {
      onEvent?.(data);
      if (data.type === 'notification' && data.play_sound) {
        playAlertSound();
        toast(data.title as string, { description: data.message as string });
      }
      if (data.type === 'new_emergency') {
        playAlertSound();
        toast('New Emergency', { description: 'A new emergency has been reported.' });
      }
    });
    return unsub;
  }, [onEvent]);
}
