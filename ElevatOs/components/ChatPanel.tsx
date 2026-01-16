import { useState, useRef, useEffect } from 'react';
import { X, Send, Mic, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { cortexService } from '../services/cortexService';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thought_trace?: string[];
}

export function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '¡Hola! Soy Aureon, un polímata digital que vive en ElevatOs, un sistema operativo de negocios inteligentes. ¿En qué puedo apoyarte hoy?'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await cortexService.process(userMsg.content);
      
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        thought_trace: response.thought_trace
      };
      
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      console.error("Chat Error:", error);
      const errorMsg: Message = {
         id: (Date.now() + 1).toString(),
         role: 'assistant',
         content: 'Lo siento, mi enlace con el Cortex parece algo inestable en este momento. Por favor, verifica tu conexión a la red y volvamos a intentarlo.'
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />

      {/* Panel */}
      <div 
        className={`fixed top-0 right-0 h-full w-full md:w-[450px] bg-obsidian-dim/95 backdrop-blur-xl border-l border-white/10 shadow-2xl z-50 transform transition-transform duration-300 ease-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
            <div className="flex items-center gap-3">
               <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-amber-400 animate-ping' : 'bg-lumina animate-pulse'}`}></div>
               <span className="font-display font-medium text-white tracking-wide">AUREON CORTEX</span>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-white/60 hover:text-white">
              <X size={20} />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
             {messages.map((msg) => (
               <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                 
                 {/* Avatar */}
                 <div className={`w-8 h-8 rounded-full flex items-center justify-center border flex-shrink-0 ${
                   msg.role === 'assistant' 
                     ? 'bg-lumina/20 border-lumina/30 text-lumina' 
                     : 'bg-white/10 border-white/20 text-white'
                 }`}>
                   <span className="text-xs">{msg.role === 'assistant' ? 'AI' : 'U'}</span>
                 </div>

                 {/* Bubble */}
                 <div className={`flex flex-col max-w-[85%] space-y-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                   <div className={`relative px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                     msg.role === 'user'
                       ? 'bg-lumina/10 border border-lumina/20 text-white rounded-tr-sm'
                       : 'bg-white/5 border border-white/10 text-white/90 rounded-tl-sm'
                   }`}>
                      <div className="prose prose-invert prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0 text-sm">
                        <ReactMarkdown 
                          components={{
                            li: ({node, ...props}) => <li className="list-disc ml-4" {...props} />
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                   </div>
                   
                   {/* Thought Trace (Assistant Only) */}
                   {msg.role === 'assistant' && msg.thought_trace && msg.thought_trace.length > 0 && (
                     <div className="text-[10px] text-white/30 px-2 font-mono">
                       {msg.thought_trace.map((trace, i) => (
                         <div key={i} className="flex items-center gap-1">
                           <span className="w-1 h-1 rounded-full bg-white/20"></span>
                           {trace}
                         </div>
                       ))}
                     </div>
                   )}
                 </div>
               </div>
             ))}
             {isLoading && (
               <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-lumina/20 border border-lumina/30 flex items-center justify-center">
                    <Loader2 size={14} className="animate-spin text-lumina" />
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce"></span>
                  </div>
               </div>
             )}
             <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-white/10 bg-black/40 backdrop-blur-md">
            <div className="relative">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask Aureon..." 
                disabled={isLoading}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-white placeholder-white/30 focus:outline-none focus:border-lumina/50 focus:bg-white/10 transition-all disabled:opacity-50"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                 <button className="p-2 text-white/40 hover:text-lumina transition-colors hidden md:block">
                    <Mic size={18} />
                 </button>
                 <button 
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isLoading}
                  className={`p-2 transition-colors ${
                    inputValue.trim() && !isLoading ? 'text-lumina hover:text-lumina-bright' : 'text-white/20'
                  }`}
                 >
                    <Send size={18} />
                 </button>
              </div>
            </div>
            <div className="text-center mt-2">
               <span className="text-[10px] text-white/20 font-mono">Aureon v2.0 (Cortex) • Secured via Hydra</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
