import { MessageSquare, Mic } from 'lucide-react';

interface AureonWidgetProps {
  onOpenChat: () => void;
}

export function AureonWidget({ onOpenChat }: AureonWidgetProps) {
  return (
    <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-30">
        <div className="glass-panel px-2 py-2 rounded-full flex items-center gap-2 border-lumina/20 shadow-neon">
            
            {/* Status Indicator */}
            <div className="hidden md:flex items-center gap-2 px-3 border-r border-white/10 mr-1">
                <div className="w-2 h-2 rounded-full bg-lumina animate-pulse shadow-[0_0_8px_#00ff33]"></div>
                <span className="font-display text-xs tracking-wide text-white/60">ONLINE</span>
            </div>

            {/* Main Orb / Chat Button */}
            <button 
                onClick={onOpenChat}
                className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-white/70 hover:text-lumina transition-all group relative overflow-hidden"
            >
                <div className="absolute inset-0 bg-lumina/0 group-hover:bg-lumina/10 transition-colors"></div>
                <MessageSquare size={18} />
            </button>

            {/* Voice Button */}
            <button 
                className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-white/70 hover:text-lumina transition-all group relative overflow-hidden"
            >
                <div className="absolute inset-0 bg-lumina/0 group-hover:bg-lumina/10 transition-colors"></div>
                 <Mic size={18} />
            </button>

        </div>
    </div>
  );
}
