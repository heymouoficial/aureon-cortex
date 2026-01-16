export interface NotionPage {
  id: string;
  title: string;
  url: string;
  lastEdited: string;
  cover?: string | null;
  icon?: string | null;
}

export interface Project extends NotionPage {
  status: 'In Progress' | 'Done' | 'Blocked' | 'Backlog';
  priority: 'High' | 'Medium' | 'Low';
  client?: string;
}

export interface Integration extends NotionPage {
  status: 'Active' | 'Inactive' | 'Error';
  type: 'API' | 'Webhook' | 'Bot';
  provider: 'OpenAI' | 'Google' | 'Supabase' | 'Vercel' | 'Other';
}

export interface KnowledgeItem extends NotionPage {
  tags: string[];
  category: 'Procedure' | 'Policy' | 'Technical' | 'General';
}

export interface NotionDatabase {
  overview: Project[];
  integrations: Integration[];
  data: KnowledgeItem[];
}
