import { supabase } from '../lib/supabase';
import { Project, Integration, KnowledgeItem, NotionDatabase } from '../types/notion';

class NotionService {
  
  /**
   * Mock Data for Development/Showcase
   */
  private mockData: NotionDatabase = {
    overview: [
      { id: '1', title: 'Website Redesign', url: '#', lastEdited: '2025-01-15', status: 'In Progress', priority: 'High', client: 'Acme Corp' },
      { id: '2', title: 'Q1 Marketing Strategy', url: '#', lastEdited: '2025-01-14', status: 'Backlog', priority: 'Medium', client: 'Globex' },
      { id: '3', title: 'Mobile App Launch', url: '#', lastEdited: '2025-01-12', status: 'Done', priority: 'High', client: 'Soylent Corp' },
    ],
    integrations: [
      { id: '1', title: 'Gemini Pro', url: '#', lastEdited: '2025-01-16', status: 'Active', type: 'API', provider: 'Google' },
      { id: '2', title: 'Supabase DB', url: '#', lastEdited: '2025-01-16', status: 'Active', type: 'API', provider: 'Supabase' },
      { id: '3', title: 'Vercel Deployment', url: '#', lastEdited: '2025-01-15', status: 'Active', type: 'Webhook', provider: 'Vercel' },
    ],
    data: [
      { id: '1', title: 'Standard Operating Procedures', url: '#', lastEdited: '2025-01-10', tags: ['Core', 'Ops'], category: 'Procedure' },
      { id: '2', title: 'Brand Guidelines 2025', url: '#', lastEdited: '2025-01-05', tags: ['Design', 'Brand'], category: 'Policy' },
      { id: '3', title: 'API Documentation', url: '#', lastEdited: '2025-01-15', tags: ['Dev', 'Tech'], category: 'Technical' },
    ]
  };

  /**
   * Fetch Overview (Projects)
   */
  async getOverview(): Promise<Project[]> {
    // TODO: Implement real Supabase/Edge Function call
    // const { data, error } = await supabase.functions.invoke('notion-api', { body: { action: 'get_overview' } });
    return new Promise((resolve) => {
      setTimeout(() => resolve(this.mockData.overview), 800);
    });
  }

  /**
   * Fetch Integrations
   */
  async getIntegrations(): Promise<Integration[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve(this.mockData.integrations), 600);
    });
  }

  /**
   * Fetch Knowledge Base (Data)
   */
  async getData(): Promise<KnowledgeItem[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve(this.mockData.data), 1000);
    });
  }
}

export const notionService = new NotionService();
