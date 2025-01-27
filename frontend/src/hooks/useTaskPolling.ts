import { useAIStore } from '@/stores/ai.store';
import { useEffect } from 'react';

export function useTaskPolling(taskId?: string, interval = 5000) {
    const { getTaskStatus } = useAIStore();
  
    useEffect(() => {
      if (!taskId) return;
  
      const poll = setInterval(async () => {
        try {
          await getTaskStatus(taskId);
        } catch (error) {
          console.error('Polling error:', error);
          clearInterval(poll);
        }
      }, interval);
  
      return () => clearInterval(poll);
    }, [taskId, interval]);
  }