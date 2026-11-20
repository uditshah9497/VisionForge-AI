import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  Zap,
  Clock,
  Coins,
  ShieldCheck
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LineChart,
  Line,
  CartesianGrid
} from 'recharts';
import { AnalyticsOverview, EvaluationRun } from '../../types';
import { api } from '../../services/api';

interface AnalyticsViewProps {
  analytics: AnalyticsOverview | null;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ analytics }) => {
  const [evalRuns, setEvalRuns] = useState<EvaluationRun[]>([]);

  useEffect(() => {
    api.getEvaluations().then(setEvalRuns).catch(console.error);
  }, []);

  const categoryData = Object.entries(analytics?.accuracy_by_category || {}).map(([cat, acc]) => ({
    category: cat.replace('_', ' '),
    accuracy: acc
  }));

  const latencyCostData = evalRuns.map(r => ({
    name: r.model_name.replace('visionforge-', '').replace('-20241022', ''),
    latency: r.avg_latency_ms,
    accuracy: r.overall_accuracy * 100
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-400" />
              <span>Multi-Dimensional Benchmark Analytics</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparative model metrics, accuracy curves across visual conditions, latency, and cost
            </p>
          </div>
          <span className="badge-cyan font-mono">Aggregated Records</span>
        </div>
      </div>

      {/* Visual Capability Comparison Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Capability Accuracy */}
        <div className="panel-card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">Accuracy by Visual Capability</h3>
          <p className="text-xs text-slate-400 mb-4">Performance across manufacturing quality tasks</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <XAxis dataKey="category" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#1E293B', borderRadius: 8, fontSize: 12 }}
                  itemStyle={{ color: '#06B6D4' }}
                />
                <Bar dataKey="accuracy" fill="#06B6D4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Latency vs Accuracy */}
        <div className="panel-card p-5">
          <h3 className="text-sm font-semibold text-white mb-1">Inference Latency vs Benchmark Accuracy</h3>
          <p className="text-xs text-slate-400 mb-4">Evaluating accuracy yield against compute latency (ms)</p>
          <div className="h-64">
            {latencyCostData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={latencyCostData}>
                  <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#1E293B', borderRadius: 8, fontSize: 12 }}
                  />
                  <Bar dataKey="latency" name="Latency (ms)" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="accuracy" name="Accuracy (%)" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                Run evaluations to display latency vs accuracy scatter
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Historical Evaluation Runs Matrix */}
      <div className="panel-card p-5">
        <h3 className="text-sm font-semibold text-white mb-1">Benchmark Run Comparison Matrix</h3>
        <p className="text-xs text-slate-400 mb-4">Side-by-side metrics across all recorded evaluation runs</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Run ID</th>
                <th className="py-2.5 px-3">Model Name</th>
                <th className="py-2.5 px-3">Provider</th>
                <th className="py-2.5 px-3">Tasks</th>
                <th className="py-2.5 px-3">Accuracy</th>
                <th className="py-2.5 px-3">Mean Latency</th>
                <th className="py-2.5 px-3">Total Cost</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
              {evalRuns.map(r => (
                <tr key={r.id} className="hover:bg-slate-900/40">
                  <td className="py-3 px-3 text-cyan-400">{r.id}</td>
                  <td className="py-3 px-3 font-sans font-medium text-white">{r.model_name}</td>
                  <td className="py-3 px-3">
                    <span className="badge-slate capitalize">{r.model_provider}</span>
                  </td>
                  <td className="py-3 px-3">{r.total_tasks}</td>
                  <td className="py-3 px-3 text-emerald-400 font-bold">
                    {(r.overall_accuracy * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3">{r.avg_latency_ms.toFixed(1)} ms</td>
                  <td className="py-3 px-3 text-amber-400">${r.total_cost_usd.toFixed(6)}</td>
                  <td className="py-3 px-3 text-slate-500 font-sans">{r.started_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
