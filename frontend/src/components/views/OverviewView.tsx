import React from 'react';
import {
  Image as ImageIcon,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  Swords,
  Target,
  ArrowUpRight,
  Sparkles,
  Zap
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { AnalyticsOverview, Dataset } from '../../types';

interface OverviewViewProps {
  analytics: AnalyticsOverview | null;
  datasets: Dataset[];
  onNavigate: (tab: any) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  analytics,
  datasets,
  onNavigate
}) => {
  const kpis = [
    {
      label: 'Generated Images',
      value: analytics?.total_images_generated ?? 0,
      icon: ImageIcon,
      color: 'text-cyan-400',
      border: 'border-cyan-500/20'
    },
    {
      label: 'Reasoning Questions',
      value: analytics?.total_questions_generated ?? 0,
      icon: HelpCircle,
      color: 'text-blue-400',
      border: 'border-blue-500/20'
    },
    {
      label: 'Validated Tasks',
      value: analytics?.validated_tasks ?? 0,
      sub: `${analytics?.validation_pass_rate ?? 0}% Pass Rate`,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      border: 'border-emerald-500/20'
    },
    {
      label: 'Quarantined Tasks',
      value: analytics?.rejected_tasks ?? 0,
      sub: 'Zero-tolerance gating',
      icon: AlertTriangle,
      color: 'text-amber-400',
      border: 'border-amber-500/20'
    },
    {
      label: 'Evaluation Runs',
      value: analytics?.evaluation_runs_count ?? 0,
      icon: Swords,
      color: 'text-purple-400',
      border: 'border-purple-500/20'
    },
    {
      label: 'Avg Model Accuracy',
      value: `${analytics?.average_model_accuracy ?? 0}%`,
      icon: Target,
      color: 'text-emerald-400',
      border: 'border-emerald-500/20'
    }
  ];

  const categoryChartData = Object.entries(analytics?.category_distribution || {}).map(([name, count]) => ({
    name: name.replace('_', ' '),
    count
  }));

  const accuracyChartData = Object.entries(analytics?.accuracy_by_category || {}).map(([cat, acc]) => ({
    category: cat.replace('_', ' '),
    accuracy: acc
  }));

  const barColors = ['#06B6D4', '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'];

  return (
    <div className="space-y-6">
      {/* Hero Mission Card */}
      <div className="panel-card p-6 bg-gradient-to-r from-[#0C1222] via-[#0E172E] to-[#0A101D] border-cyan-500/30 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-700/50 text-cyan-400 text-xs font-mono mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Industrial Visual Benchmark Pipeline Active</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight leading-snug">
            Automated Synthetic Task Generation & Multimodal Model Evaluation
          </h2>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            VisionForge AI autonomously generates parametric industrial assembly scenes with controlled defect variations,
            formulates verifiable visual reasoning questions, computes deterministic reference ground truth,
            gates quality through 8-stage automated validation, and stress-tests frontier vision models.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('studio')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-xs tracking-wide transition-colors shadow-lg shadow-cyan-500/20"
            >
              <Zap className="w-4 h-4" />
              <span>Launch Synthetic Studio</span>
            </button>
            <button
              onClick={() => onNavigate('arena')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs tracking-wide border border-slate-700 transition-colors"
            >
              <Swords className="w-4 h-4 text-purple-400" />
              <span>Evaluate Multimodal Models</span>
            </button>
            <button
              onClick={() => onNavigate('blind_spot')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs tracking-wide border border-slate-700 transition-colors"
            >
              <ArrowUpRight className="w-4 h-4 text-amber-400" />
              <span>Visual Blind Spot Discovery</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className={`panel-card p-4 border ${kpi.border} flex flex-col justify-between`}>
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-medium">{kpi.label}</span>
                <Icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
              <div className="mt-3">
                <div className="text-2xl font-bold text-white font-mono tracking-tight">{kpi.value}</div>
                {kpi.sub && <div className="text-[11px] text-slate-400 font-mono mt-0.5">{kpi.sub}</div>}
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="panel-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Visual Tasks by Reasoning Category</h3>
              <p className="text-xs text-slate-400">Distribution across 5 core evaluation capabilities</p>
            </div>
            <span className="badge-cyan font-mono">5 Categories</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryChartData}>
                <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#1E293B', borderRadius: 8, fontSize: 12 }}
                  itemStyle={{ color: '#06B6D4' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {categoryChartData.map((_, i) => (
                    <Cell key={i} fill={barColors[i % barColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Accuracy by Capability */}
        <div className="panel-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Multimodal Accuracy by Capability</h3>
              <p className="text-xs text-slate-400">Measured accuracy across evaluated tasks (%)</p>
            </div>
            <span className="badge-emerald font-mono">Live Benchmarks</span>
          </div>
          <div className="h-64">
            {accuracyChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={accuracyChartData} layout="vertical">
                  <XAxis type="number" domain={[0, 100]} stroke="#64748B" fontSize={11} />
                  <YAxis type="category" dataKey="category" stroke="#64748B" fontSize={11} width={120} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#1E293B', borderRadius: 8, fontSize: 12 }}
                    itemStyle={{ color: '#10B981' }}
                  />
                  <Bar dataKey="accuracy" fill="#10B981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                Run an evaluation in Model Arena to populate capability benchmarks
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Active Datasets Table */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Generated Synthetic Benchmarks</h3>
            <p className="text-xs text-slate-400">Parametric datasets available for model evaluation</p>
          </div>
          <button
            onClick={() => onNavigate('studio')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1"
          >
            Create New Dataset <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Dataset Name</th>
                <th className="py-2.5 px-3">Domain</th>
                <th className="py-2.5 px-3">Difficulty</th>
                <th className="py-2.5 px-3">Scenes</th>
                <th className="py-2.5 px-3">Seed</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {datasets.map((d) => (
                <tr key={d.id} className="hover:bg-slate-900/40">
                  <td className="py-3 px-3 font-medium text-white">{d.name}</td>
                  <td className="py-3 px-3 text-slate-400">{d.domain}</td>
                  <td className="py-3 px-3">
                    <span className="badge-slate font-mono capitalize">{d.difficulty}</span>
                  </td>
                  <td className="py-3 px-3 font-mono">{d.num_scenes}</td>
                  <td className="py-3 px-3 font-mono text-cyan-400">#{d.seed}</td>
                  <td className="py-3 px-3">
                    <span className="badge-emerald font-mono uppercase">{d.status}</span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => onNavigate('studio')}
                      className="text-cyan-400 hover:underline"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
