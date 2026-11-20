import React from 'react';
import {
  CheckCircle2,
  ShieldCheck,
  Binary,
  Layers,
  Compass,
  Maximize,
  Cpu
} from 'lucide-react';
import { Dataset, SceneItem } from '../../types';

interface GroundTruthViewProps {
  selectedDataset: any;
}

export const GroundTruthView: React.FC<GroundTruthViewProps> = ({ selectedDataset }) => {
  const scenes: SceneItem[] = selectedDataset?.scenes || [];
  const firstScene: SceneItem | undefined = scenes[0];

  return (
    <div className="space-y-6">
      {/* Ground Truth Independence Banner */}
      <div className="panel-card p-5 border-emerald-500/30 bg-gradient-to-r from-[#0B1516] via-[#0D1822] to-[#0A101D]">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-emerald-950 border border-emerald-700/50 flex items-center justify-center shrink-0 text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Deterministic Ground-Truth & Zero-LLM Verification Principle
            </h2>
            <p className="mt-1 text-xs text-slate-300 leading-relaxed max-w-4xl">
              VisionForge AI never uses foundation models (Gemini, GPT-4o, Claude) to calculate or verify reference answers.
              Every ground-truth answer is mathematically derived by pure functional logic over the parametric scene graph
              (exact bounding boxes, CAD coordinates, rotation matrices, and physical occlusion ratios).
              This guarantees zero circular evaluation bias and 100% auditability.
            </p>
          </div>
        </div>
      </div>

      {/* Rules Engine Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="panel-card p-4">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs mb-2">
            <Binary className="w-4 h-4" />
            <span>Counting Derivations</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Deducted via functional filter:
            <code className="block mt-1 p-2 rounded bg-slate-950 font-mono text-[11px] text-cyan-300">
              count(type=X and visibility_score &gt;= 0.30)
            </code>
            Excludes occluded components beyond the human-discernible threshold.
          </p>
        </div>

        <div className="panel-card p-4">
          <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs mb-2">
            <Compass className="w-4 h-4" />
            <span>Spatial Reasoner</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Determined by centroid Cartesian delta vectors:
            <code className="block mt-1 p-2 rounded bg-slate-950 font-mono text-[11px] text-blue-300">
              dx = bx - ax; dy = by - ay;
            </code>
            Cardinal alignments (left_of, right_of, above, below) calculated deterministically.
          </p>
        </div>

        <div className="panel-card p-4">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs mb-2">
            <Cpu className="w-4 h-4" />
            <span>Defect State Extraction</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Evaluated by comparison against reference assembly nest:
            <code className="block mt-1 p-2 rounded bg-slate-950 font-mono text-[11px] text-amber-300">
              is_defective = (pos != expected_pos)
            </code>
            Flags missing sockets, displaced coordinates, and rotated fasteners.
          </p>
        </div>
      </div>

      {/* Sample Scene Inspection */}
      {firstScene ? (
        <div className="panel-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Live Scene Graph Audit - Scene #{firstScene.scene_number}
              </h3>
              <p className="text-xs text-slate-400">
                Component coordinates, bounding boxes, and ground-truth metadata
              </p>
            </div>
            <span className="badge-cyan font-mono">Seed #{firstScene.seed}</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Component Name</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Center (X, Y)</th>
                  <th className="py-2.5 px-3">Bounding Box [x1, y1, x2, y2]</th>
                  <th className="py-2.5 px-3">Rotation</th>
                  <th className="py-2.5 px-3">Visibility</th>
                  <th className="py-2.5 px-3">Defect State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                {firstScene.scene_graph?.components?.map((c, i) => (
                  <tr key={i} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-3 font-sans font-medium text-white">{c.name}</td>
                    <td className="py-2.5 px-3 text-cyan-400">{c.type}</td>
                    <td className="py-2.5 px-3 text-slate-400">({c.center.x}, {c.center.y})</td>
                    <td className="py-2.5 px-3 text-slate-400">[{c.bbox.join(', ')}]</td>
                    <td className="py-2.5 px-3">{c.rotation_deg}°</td>
                    <td className="py-2.5 px-3 text-emerald-400">{c.visibility_score * 100}%</td>
                    <td className="py-2.5 px-3">
                      {c.is_defective ? (
                        <span className="badge-rose uppercase text-[10px]">
                          {c.defect_type || 'Defective'}
                        </span>
                      ) : (
                        <span className="badge-emerald uppercase text-[10px]">Normal</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="panel-card p-8 text-center text-slate-500 text-xs">
          No scenes loaded. Please generate or select a dataset.
        </div>
      )}
    </div>
  );
};
