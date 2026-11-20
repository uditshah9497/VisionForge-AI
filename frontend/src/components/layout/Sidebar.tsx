import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  HelpCircle,
  CheckCircle2,
  ShieldAlert,
  Swords,
  EyeOff,
  BarChart3,
  FileText,
  Settings,
  Sparkles
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'studio'
  | 'questions'
  | 'ground_truth'
  | 'validation'
  | 'arena'
  | 'blind_spot'
  | 'analytics'
  | 'reports'
  | 'settings';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  datasetCount?: number;
  evalCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  datasetCount = 1,
  evalCount = 1
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'studio', label: 'Synthetic Studio', icon: Cpu, badge: datasetCount ? `${datasetCount} sets` : undefined },
    { id: 'questions', label: 'Question Factory', icon: HelpCircle },
    { id: 'ground_truth', label: 'Ground Truth', icon: CheckCircle2 },
    { id: 'validation', label: 'Validation Center', icon: ShieldAlert },
    { id: 'arena', label: 'Model Arena', icon: Swords, badge: 'Live' },
    { id: 'blind_spot', label: 'Blind Spot Discovery', icon: EyeOff, highlight: true },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#090D16] border-r border-slate-800/80 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-5 border-b border-slate-800/80 gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold tracking-tight text-white flex items-center gap-1.5 text-base">
              VisionForge <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/50 font-mono">AI</span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono tracking-wide">
              Visual Benchmark Factory
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase font-mono">
            Pipeline Modules
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id as NavTab)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-950/80 to-blue-950/50 text-cyan-300 border border-cyan-800/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive ? 'text-cyan-400' : 'text-slate-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                      item.badge === 'Live'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/50'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
                {item.highlight && !item.badge && (
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Industrial Domain Footer Banner */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="p-3 rounded-lg bg-[#0F172A] border border-slate-800 text-xs">
          <div className="flex items-center gap-2 font-medium text-slate-200 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Domain Active
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Industrial Manufacturing Quality Inspection Workstations
          </p>
        </div>
      </div>
    </aside>
  );
};
