import React from 'react';
import { Database, CheckCircle2, ShieldCheck, ExternalLink } from 'lucide-react';
import { Dataset } from '../../types';

interface NavbarProps {
  currentTabName: string;
  datasets: Dataset[];
  selectedDatasetId: string;
  onSelectDatasetId: (id: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTabName,
  datasets,
  selectedDatasetId,
  onSelectDatasetId
}) => {
  return (
    <header className="h-16 bg-[#090D16] border-b border-slate-800/80 px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-white tracking-tight">
          {currentTabName}
        </h1>
        <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-800 text-xs text-slate-400">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-950/70 border border-emerald-800/40 text-emerald-400 font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            Ground Truth: Deterministic (Zero-LLM)
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Active Dataset Selector */}
        <div className="flex items-center gap-2 bg-[#0F172A] border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
          <Database className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400 font-medium">Active Dataset:</span>
          <select
            value={selectedDatasetId}
            onChange={(e) => onSelectDatasetId(e.target.value)}
            className="bg-transparent text-slate-200 font-medium outline-none cursor-pointer pr-1"
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id} className="bg-slate-900 text-slate-200">
                {d.name} ({d.num_scenes} scenes)
              </option>
            ))}
          </select>
        </div>

        {/* API Docs link */}
        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-cyan-300 bg-slate-900/80 hover:bg-slate-850 border border-slate-800 rounded-lg transition-colors"
        >
          <span>OpenAPI Spec</span>
          <ExternalLink className="w-3 h-3 text-slate-400" />
        </a>
      </div>
    </header>
  );
};
