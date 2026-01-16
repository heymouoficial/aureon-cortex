import { useEffect, useState } from 'react';
import { notionService } from '../services/notionService';
import { Project, Integration, KnowledgeItem } from '../types/notion';

interface DashboardModuleProps {
  type: string;
}

export function DashboardModule({ type }: DashboardModuleProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        let result: any[] = [];
        if (type === 'overview') {
            result = await notionService.getOverview();
        } else if (type === 'integrations') {
            result = await notionService.getIntegrations();
        } else if (type === 'data') {
            result = await notionService.getData();
        }
        setData(result);
      } catch (e) {
        console.error("Failed to fetch data", e);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [type]);

  if (loading) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-lumina border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (data.length === 0) {
      if (type === 'intelligence') {
          return (
              <div className="w-full text-center py-12 text-white/40 font-light">
                  <span className="text-xl">Aureon Cortex Analysis...</span>
                  <p className="text-sm mt-2">Voice & Chat Intelligence Active.</p>
              </div>
          )
      }
    return <div className="text-white/50 text-center py-10">No data available for {type}</div>;
  }

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="glass-panel rounded-2xl p-6 overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.map((item) => (
            <div key={item.id} className="bg-white/5 hover:bg-white/10 p-4 rounded-xl border border-white/5 hover:border-lumina/30 transition-all duration-300 group cursor-pointer">
              <div className="flex justify-between items-start mb-2">
                 <span className={`text-xs px-2 py-1 rounded-full border ${getStatusColor(item.status)}`}>
                   {item.status}
                 </span>
                 {item.provider && <span className="text-xs text-white/40">{item.provider}</span>}
              </div>
              <h4 className="text-lg font-display text-white group-hover:text-lumina transition-colors truncate">
                {item.title}
              </h4>
              <div className="mt-4 flex justify-between items-center text-xs text-white/40">
                <span>{item.client || item.category || item.type}</span>
                <span>{item.lastEdited}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getStatusColor(status: string) {
  if (status === 'Active' || status === 'Done' || status === 'In Progress') return 'bg-lumina/10 text-lumina border-lumina/20';
  if (status === 'Error' || status === 'Blocked') return 'bg-red-500/10 text-red-400 border-red-500/20';
  return 'bg-white/5 text-white/50 border-white/10';
}
