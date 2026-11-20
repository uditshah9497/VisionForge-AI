import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileCheck,
  RefreshCw,
  Search
} from 'lucide-react';
import { ValidationSummary } from '../../types';
import { api } from '../../services/api';

export const ValidationCenterView: React.FC = () => {
  const [summary, setSummary] = useState<ValidationSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSummary = async () => {
    setLoading(true);
    try {
      const data = await api.getValidationSummary();
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const checksList = [
    { name: 'Image Decodability & Health', desc: 'Validates non-corrupt PNG headers, RGB channels, and file size', weight: 'Critical' },
    { name: 'Canvas & Bounding Box Area', desc: 'Guarantees strictly positive pixel area within canvas [0,0,800,600]', weight: 'Critical' },
    { name: 'Visual Evidence Sufficiency', desc: 'Verifies min pixel area (>100px) and visibility score (>=0.25)', weight: 'High' },
    { name: 'Answer Determinism & Type Match', desc: 'Enforces strictly parseable, deterministic reference ground truth', weight: 'Critical' },
    { name: 'Question Clarity & Template Resolution', desc: 'Rejects unpopulated template variables and ambiguous phrasing', weight: 'High' },
    { name: 'Cross-Scene Task Deduplication', desc: 'Filters duplicate question texts targeting identical scene coords', weight: 'Medium' }
  ];

  return (
    <div className="space-y-6">
      {/* Header and Summary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="panel-card p-4 border-cyan-500/20">
          <div className="text-xs text-slate-400 font-medium">Total Tasks Evaluated</div>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            {summary?.total_evaluated ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-0.5">Automated Multi-Factor</div>
        </div>

        <div className="panel-card p-4 border-emerald-500/20">
          <div className="text-xs text-slate-400 font-medium">Validated & Certified Tasks</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {summary?.passed_count ?? 0}
          </div>
          <div className="text-[11px] text-emerald-500 font-mono mt-0.5">Approved for Arena</div>
        </div>

        <div className="panel-card p-4 border-rose-500/20">
          <div className="text-xs text-slate-400 font-medium">Quarantined / Rejected</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">
            {summary?.failed_count ?? 0}
          </div>
          <div className="text-[11px] text-rose-400 font-mono mt-0.5">Zero-Tolerance Gated</div>
        </div>

        <div className="panel-card p-4 border-blue-500/20">
          <div className="text-xs text-slate-400 font-medium">Validation Pass Rate</div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
            {summary?.pass_rate ?? 0}%
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-0.5">Quality Assurance Standard</div>
        </div>
      </div>

      {/* 8-Stage Automated Rules Verification Suite */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-cyan-400" />
              <span>Automated Task Validation Engine Specifications</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Every synthetic visual task must satisfy all 6 multi-factor gates prior to benchmark qualification
            </p>
          </div>
          <button
            onClick={loadSummary}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Re-verify</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {checksList.map((chk, i) => (
            <div key={i} className="p-3.5 rounded-lg bg-[#080C14] border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="font-semibold text-slate-200">{chk.name}</span>
                  <span className={`text-[10px] font-mono ${
                    chk.weight === 'Critical' ? 'text-rose-400' : 'text-cyan-400'
                  }`}>
                    [{chk.weight}]
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{chk.desc}</p>
              </div>
              <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center gap-1.5 text-[11px] font-mono text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Automated Enforcement: Active</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quarantined Tasks Audit Log */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Quarantined & Rejected Tasks Isolation Store</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Tasks rejected by the validation engine with failure diagnostic codes
            </p>
          </div>
          <span className="badge-amber font-mono">
            {summary?.quarantined_rejected_tasks?.length || 0} Quarantined
          </span>
        </div>

        {summary?.quarantined_rejected_tasks && summary.quarantined_rejected_tasks.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Question ID</th>
                  <th className="py-2.5 px-3">Scene ID</th>
                  <th className="py-2.5 px-3">Validation Score</th>
                  <th className="py-2.5 px-3">Diagnostic Rejection Reason</th>
                  <th className="py-2.5 px-3">Quarantined At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                {summary.quarantined_rejected_tasks.map((rej, i) => (
                  <tr key={i} className="hover:bg-slate-900/40">
                    <td className="py-3 px-3 text-cyan-400">{rej.question_id}</td>
                    <td className="py-3 px-3 text-slate-400">{rej.scene_id}</td>
                    <td className="py-3 px-3 text-rose-400 font-bold">{rej.score * 100}%</td>
                    <td className="py-3 px-3 text-amber-300 font-sans max-w-md">{rej.rejection_reason}</td>
                    <td className="py-3 px-3 text-slate-500">{rej.validated_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center border border-dashed border-slate-800 rounded-lg text-slate-500 text-xs">
            <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-2" />
            <p className="font-medium text-slate-300">All generated tasks in current benchmark satisfied validation.</p>
            <p className="mt-1">Zero quarantined tasks. All visual evidence checks passed.</p>
          </div>
        )}
      </div>
    </div>
  );
};
