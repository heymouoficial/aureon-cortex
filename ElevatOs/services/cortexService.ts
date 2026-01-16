import { supabase } from '../lib/supabase';

// Pointing to VPS IP directly as per deployment
const CORTEX_URL = import.meta.env.VITE_CORTEX_URL || 'http://72.62.171.113:8000';

export interface SynapseResponse {
  answer: string;
  thought_trace: string[];
  actions: any[];
}

export const cortexService = {
  /**
   * Sends a thought/request to the Aureon Cortex (Python Backend)
   */
  async process(message: string, context?: any): Promise<SynapseResponse> {
    // We can optionally pass user context, but let's keep it simple for now
    // const { data: { user } } = await supabase.auth.getUser();
    
    try {
      const res = await fetch(`${CORTEX_URL}/api/v1/synapse/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          context: {
             ...context,
             platform: 'elevatos-web'
          }
        })
      });

      if (!res.ok) {
        throw new Error(`Cortex Error: ${res.statusText}`);
      }

      const data = await res.json();
      return data as SynapseResponse;
    } catch (error) {
      console.error("🧠 Cortex Connection Failed:", error);
      throw error;
    }
  },

  /**
   * Health check to see if Cortex is awake
   */
  async ping(): Promise<boolean> {
    try {
      const res = await fetch(`${CORTEX_URL}/health`);
      return res.ok;
    } catch (e) {
        console.warn("Cortex ping failed", e);
      return false;
    }
  }
};
