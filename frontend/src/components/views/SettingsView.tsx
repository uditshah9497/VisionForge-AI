import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Key,
  Database,
  Folder,
  Server,
  ShieldCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { ModelConfig } from '../../types';
import { api } from '../../services/api';

export const SettingsView: React.FC = () => {
  const [models, setModels] = useState<ModelConfig[]>([]);

  useEffect(() => {
    api.getModels().then(setModels).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <SettingsIcon className="w-5 h-5 text-cyan-400" />
              <span>Platform Settings & Multimodal Model Providers</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Review API keys configuration, local storage directories, and database status
            </p>
          </div>
          <span className="badge-emerald font-mono flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Backend Active: Port 8000
          </span>
        </div>
      </div>

      {/* Model Providers Status Grid */}
      <div className="panel-card p-5">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Key className="w-4 h-4 text-purple-400" />
          <span>Multimodal Model Provider Configuration Status</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Credentials are read from environment variables (<code className="text-cyan-300">.env</code>).
          When external API keys are omitted, VisionForge runs seamlessly in calibrated Demo Simulator mode.
        </p>

        <div className="space-y-3">
          {models.map(m => (
            <div
              key={m.id}
              className="p-3.5 rounded-lg bg-[#080C14] border border-slate-800 flex items-center justify-between text-xs"
            >
              <div>
                <div className="flex items-center gap-2 font-semibold text-slate-200">
                  <span>{m.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">({m.id})</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">{m.description}</div>
              </div>

              <div>
                {m.is_configured ? (
                  <span className="badge-emerald font-mono flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Configured & Ready</span>
                  </span>
                ) : (
                  <span className="badge-slate font-mono text-slate-400">
                    Not Configured (Using Demo Simulator)
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Storage and System Paths */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="panel-card p-4">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs mb-2">
            <Database className="w-4 h-4" />
            <span>Persistence Engine</span>
          </div>
          <div className="text-xs text-slate-300 space-y-1">
            <div className="flex justify-between font-mono">
              <span className="text-slate-500">Database Engine:</span>
              <span className="text-cyan-300">SQLAlchemy ORM</span>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-slate-500">Active Storage:</span>
              <span className="text-slate-200">SQLite (Dev) / PostgreSQL (Prod)</span>
            </div>
          </div>
        </div>

        <div className="panel-card p-4">
          <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs mb-2">
            <Folder className="w-4 h-4" />
            <span>Artifact Directories</span>
          </div>
          <div className="text-xs text-slate-300 space-y-1">
            <div className="flex justify-between font-mono">
              <span className="text-slate-500">Synthetic Images:</span>
              <span className="text-cyan-300">data/artifacts/</span>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-slate-500">Exported Reports:</span>
              <span className="text-cyan-300">data/reports/</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
