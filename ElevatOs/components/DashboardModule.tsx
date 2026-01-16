import { useEffect, useState } from 'react';
import DataView from './DataView';
import RAGView from './RAGView';
import ConnectionsView from './ConnectionsView';
import NotionView from './NotionView';
import TeamView from './TeamView';
import ClientsView from './ClientsView';
import FlowView from './FlowView';
import { ViewState, UserProfile, Task, Lead, NotionPage, Client, CalendarEvent } from '../types';

interface DashboardModuleProps {
  type: string;
  user?: UserProfile;
  data: {
    tasks: Task[];
    leads: Lead[];
    notionDocs: NotionPage[];
    events: CalendarEvent[];
    clients: Client[];
  };
}

export function DashboardModule({ type, user, data }: DashboardModuleProps) {
  // Routing logic for specialized views
  switch (type) {
    case 'data':
      return <DataView notionDocs={data.notionDocs} />;
    case 'intelligence': // Mapping Stich naming to views
    case 'rag':
      return <RAGView organizationId={user?.organizationId} />;
    case 'integrations':
    case 'connections':
      return <ConnectionsView organizationId={user?.organizationId || ''} />;
    case 'notion':
      return <NotionView clients={data.clients} services={[]} tasks={data.tasks} />;
    case 'team':
      return <TeamView organizationId={user?.organizationId || ''} />;
    case 'agency':
    case 'clients':
      return <ClientsView clients={data.clients} />;
    case 'flow':
      return <FlowView messages={[]} user={user!} />;
    default:
      return (
        <div className="w-full text-center py-20 px-4 animate-in fade-in duration-700">
          <div className="glass-panel max-w-md mx-auto p-12 rounded-[2.5rem] space-y-4">
            <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-6 text-lumina">
              {/* Optional dynamic icon based on type */}
              <div className="w-1.5 h-1.5 rounded-full bg-lumina animate-ping" />
            </div>
            <h2 className="text-2xl font-display font-medium text-white uppercase tracking-widest">
              Work in Progress
            </h2>
            <p className="text-white/40 font-light">
              Módulo <span className="text-white/60 font-medium">"{type.toUpperCase()}"</span> está siendo calibrado por Aureon.
            </p>
          </div>
        </div>
      );
  }
}
