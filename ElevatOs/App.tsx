import { useState } from 'react';
import { DashboardModule } from './components/DashboardModule';
import { AureonWidget } from './components/AureonWidget';
import { ChatPanel } from './components/ChatPanel';

function App() {
  const [active, setActive] = useState("overview");
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="min-h-screen relative overflow-hidden font-body">
      {/* Background Noise & Gradient */}
      <div className="bg-noise" />
      <div className="fixed inset-0 bg-gradient-to-b from-obsidian-dim to-obsidian -z-20" />
      
      {/* Main Container */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen text-center px-4">
        
        {/* Logo / Title */}
        <div className="mb-12 relative group cursor-default">
          <div className="absolute -inset-4 bg-lumina/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000 animate-pulse"></div>
          <h1 className="text-6xl md:text-8xl font-display font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60 relative z-10">
            Elevat<span className="text-lumina text-glow">OS</span>
          </h1>
          <p className="mt-4 text-xl text-white/50 tracking-widest uppercase font-light">
            Business Operating System
          </p>
        </div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl mb-8">
          {['Overview', 'Intelligence', 'Data', 'Integrations'].map((module) => (
            <button
              key={module}
              onClick={() => setActive(module.toLowerCase())}
              className={`glass-panel p-8 rounded-2xl text-left transition-all duration-300 group ${
                active === module.toLowerCase() 
                ? 'border-lumina/50 shadow-[0_0_30px_rgba(0,255,51,0.15)] bg-white/10' 
                : 'hover:bg-white/10 hover:border-white/20'
              }`}
            >
              <h3 className={`text-2xl font-display font-medium mb-2 group-hover:text-lumina transition-colors ${
                active === module.toLowerCase() ? 'text-lumina' : 'text-white'
              }`}>
                {module}
              </h3>
              <p className="text-sm text-white/40 group-hover:text-white/70 transition-colors">
                Access your {module.toLowerCase()} workspace.
              </p>
            </button>
          ))}
        </div>

        {/* Dynamic Dashboard Module */}
        {active && <DashboardModule type={active} />}

        {/* Aureon Widget & Chat Panel */}
        <AureonWidget onOpenChat={() => setIsChatOpen(true)} />
        <ChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

      </div>
    </div>
  );
}

export default App;
