import { useState, useMemo } from 'react';
import Dashboard from './components/Dashboard';
import { DashboardModule } from './components/DashboardModule';
import { AureonWidget } from './components/AureonWidget';
import { ChatPanel } from './components/ChatPanel';
import Header from './components/Header';
import { UserProfile, ViewState, Task, Lead, NotionPage, Client, CalendarEvent } from './types';

// MOCK DATA (To be replaced by Supabase/Notion hooks later)
const MOCK_USER: UserProfile = {
  id: 'astursadeth',
  name: 'Moshé Quantum',
  role: 'Founder & Architect',
  avatar: 'MQ',
  theme: '#00ff33',
  organizationId: 'MULTIVERSA'
};

function App() {
  const [currentView, setCurrentView] = useState<ViewState>('home');
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Unified State (Centralized for Stich Architecture)
  const tasks: Task[] = [];
  const leads: Lead[] = [];
  const notionDocs: NotionPage[] = [];
  const events: CalendarEvent[] = [];
  const clients: Client[] = [];

  const renderView = () => {
    switch (currentView) {
      case 'home':
        return (
          <Dashboard 
            user={MOCK_USER}
            tasks={tasks}
            leads={leads}
            notionDocs={notionDocs}
            events={events}
            clients={clients}
            onNavigate={(view) => setCurrentView(view)}
          />
        );
      default:
        return (
          <DashboardModule 
            type={currentView as string} 
            user={MOCK_USER}
            data={{
              tasks,
              leads,
              notionDocs,
              events,
              clients
            }}
          />
        );
    }
  };

  return (
    <div className="min-h-screen relative overflow-x-hidden bg-obsidian text-white font-body selection:bg-lumina/30">
      {/* Background Noise & Particles */}
      <div className="bg-noise fixed inset-0 z-0 opacity-10" />
      <div className="fixed inset-0 bg-gradient-to-b from-obsidian-dim/50 to-obsidian -z-10" />
      
      {/* Dynamic Background Blobs */}
      <div className="fixed top-[-10%] left-[-10%] w-[500px] h-[500px] bg-lumina/5 rounded-full blur-[120px] animate-blob" />
      <div className="fixed bottom-[-10%] right-[-10%] w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-[100px] animate-blob delay-700" />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Header user={MOCK_USER} activeView={currentView} />
        
        <main className="flex-1 w-full pt-24 pb-32">
          {renderView()}
        </main>

        <AureonWidget onOpenChat={() => setIsChatOpen(true)} />
        <ChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      </div>
    </div>
  );
}

export default App;
