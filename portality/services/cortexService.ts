import { supabase } from '../lib/supabase';

// In development, we might fallback to localhost if ENV not set
// In production, this should point to your VPS URL
const CORTEX_URL = import.meta.env.VITE_CORTEX_URL || 'http://localhost:8000';

export interface SynapseResponse {
  status: string;
  thought_process: string;
  response: string;
  action_required: boolean;
}

export const cortexService = {
  /**
   * Sends a thought/request to the Aureon Cortex (Python Backend)
   */
  async process(content: string, context?: any): Promise<SynapseResponse> {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error("User must be authenticated to access Cortex.");
    }

    try {
      const res = await fetch(`${CORTEX_URL}/api/v1/synapse/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Optional: Add Auth Header if we implement JWT validation in Python
        },
        body: JSON.stringify({
          user_id: user.id,
          content,
          context
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
      return false;
    }
  }
};
