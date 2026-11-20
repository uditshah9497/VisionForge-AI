import React, { useState, useEffect } from 'react';
import {
  EyeOff,
  Sparkles,
  Zap,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Split,
  Layers,
  HelpCircle
} from 'lucide-react';
import { BlindSpotPair } from '../../types';
import { api } from '../../services/api';

export const BlindSpotView: React.FC = () => {
  const [pairs, setPairs] = useState<BlindSpotPair[]>([]);
  const [loading, setLoading] = useState(false);
  const [activePair, setActivePair] = useState<BlindSpotPair | null>(null);

  const [form, setForm] = useState({
    base_seed: 42,
    perturbation_type: 'component_removed',
    provider: 'demo',
    model_name: 'visionforge-demo-v1'
  });

  const loadPairs = async () => {
    try {
      const data = await api.getBlindSpotPairs();
      setPairs(data);
      if (data.length > 0 && !activePair) {
        setActivePair(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadPairs();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newPair = await api.generateBlindSpot(form);
      setPairs(prev => [newPair, ...prev]);
      setActivePair(newPair);
    } catch (err: any) {
      alert(`Blind spot test generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Feature Explainer Banner */}
      <div className="panel-card p-5 border-amber-500/30 bg-gradient-to-r from-[#14101A] via-[#161224] to-[#0A101D]">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-amber-950 border border-amber-700/50 flex items-center justify-center shrink-0 text-amber-400">
            <EyeOff className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white tracking-tight">
                Visual Blind Spot Discovery: Controlled Adversarial Testing
              </h2>
              <span className="badge-amber font-mono text-[10px]">Delta-Pair Testing</span>
            </div>
            <p className="mt-1 text-xs text-slate-300 leading-relaxed max-w-4xl">
              Frontier vision models often suffer from subtle visual blind spots—failing to perceive minor displacements,
              inverting orientation, or hallucinating component presence due to strong language priors.
              VisionForge synthesizes paired images with exactly ONE controlled property altered while holding all other visual invariants constant,
              exposing reasoning failures in high-precision assembly inspection.
            </p>
          </div>
        </div>
      </div>

      {/* Generator Form and Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Panel */}
        <div className="panel-card p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <span>Generate Adversarial Test Pair</span>
          </h3>

          <form onSubmit={handleGenerate} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Perturbation Type (Controlled Delta)</label>
              <select
                value={form.perturbation_type}
                onChange={e => setForm({ ...form, perturbation_type: e.target.value })}
                className="w-full bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 outline-none focus:border-amber-500"
              >
                <option value="component_removed">Component Removal (Missing Socket)</option>
                <option value="misplaced">Micro-Displacement (Shifted by 45px)</option>
                <option value="orientation_inversion">Orientation Inversion (180° Upside Down)</option>
                <option value="lighting_change">Luminance Drop (Low Ambient Lux 35%)</option>
                <option value="occlusion">Partial Occlusion (Industrial Wire Harness)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Base Random Seed</label>
              <input
                type="number"
                value={form.base_seed}
                onChange={e => setForm({ ...form, base_seed: Number(e.target.value) })}
                className="w-full bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Model Evaluator</label>
              <select
                value={form.model_name}
                onChange={e => setForm({ ...form, model_name: e.target.value })}
                className="w-full bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 outline-none focus:border-amber-500"
              >
                <option value="visionforge-demo-v1">VisionForge Simulator (Demo)</option>
                <option value="gemini-1.5-pro">Google Gemini 1.5 Pro</option>
                <option value="gemini-2.0-flash">Google Gemini 2.0 Flash</option>
                <option value="gpt-4o">OpenAI GPT-4o</option>
                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-black font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50"
            >
              {loading ? 'Synthesizing & Evaluating...' : 'Probe Visual Blind Spot'}
            </button>
          </form>
        </div>

        {/* Existing Test Pairs List */}
        <div className="panel-card p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">Discovered Blind Spot Records</h3>
            <span className="badge-amber font-mono">{pairs.length} Tested Pairs</span>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto">
            {pairs.map(p => (
              <div
                key={p.id}
                onClick={() => setActivePair(p)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all flex items-center justify-between ${
                  activePair?.id === p.id
                    ? 'bg-amber-950/30 border-amber-500/60 text-white'
                    : 'bg-[#080C14] border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-200 capitalize">
                      {p.property_changed.replace('_', ' ')}
                    </span>
                    {p.is_blind_spot ? (
                      <span className="badge-rose text-[10px] font-mono">Blind Spot Anomaly</span>
                    ) : (
                      <span className="badge-emerald text-[10px] font-mono">Perceived Correctly</span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{p.delta_description}</div>
                </div>
                <div className="text-right text-[11px] font-mono text-slate-400">
                  Model: {p.model_name || 'Simulator'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Side-by-Side Adversarial Inspection Panel */}
      {activePair && (
        <div className="panel-card p-6 border-amber-500/40">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-4 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <span className="badge-amber font-mono text-[10px] uppercase">
                  {activePair.property_changed.replace('_', ' ')}
                </span>
                <h3 className="text-sm font-bold text-white">
                  Controlled Difference: {activePair.delta_description}
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Visual Query: <span className="text-slate-200 font-medium">"{activePair.question_text}"</span>
              </p>
            </div>
            {activePair.is_blind_spot ? (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-300 font-mono text-xs font-semibold">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>CONFIRMED VISUAL BLIND SPOT</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800 text-emerald-300 font-mono text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Robust Perception (No Blind Spot)</span>
              </div>
            )}
          </div>

          {/* Side-by-Side Images */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            {/* Image A: Baseline */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-cyan-400 font-semibold">Condition A (Baseline Assembly)</span>
                <span className="text-slate-500">Normal State</span>
              </div>
              <div className="rounded-lg overflow-hidden border border-slate-800 bg-black">
                <img
                  src={activePair.original_image_url}
                  alt="Original Workstation Condition"
                  className="w-full h-auto object-contain"
                />
              </div>
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Ground Truth Answer:</span>
                  <span className="text-emerald-400 font-bold">{activePair.original_expected_answer}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Model Predicted:</span>
                  <span className="text-slate-200 font-bold">{activePair.original_model_answer || 'Pending'}</span>
                </div>
              </div>
            </div>

            {/* Image B: Perturbed */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-amber-400 font-semibold">Condition B (Single Controlled Perturbation)</span>
                <span className="text-rose-400 font-semibold">{activePair.property_changed}</span>
              </div>
              <div className="rounded-lg overflow-hidden border border-amber-500/40 bg-black">
                <img
                  src={activePair.modified_image_url}
                  alt="Perturbed Workstation Condition"
                  className="w-full h-auto object-contain"
                />
              </div>
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Ground Truth Answer:</span>
                  <span className="text-emerald-400 font-bold">{activePair.modified_expected_answer}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Model Predicted:</span>
                  <span className={`font-bold ${
                    activePair.modified_model_answer === activePair.modified_expected_answer
                      ? 'text-emerald-400'
                      : 'text-rose-400'
                  }`}>
                    {activePair.modified_model_answer || 'Pending'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Diagnostic Failure Analysis */}
          {activePair.is_blind_spot && (
            <div className="mt-6 p-4 rounded-lg bg-rose-950/30 border border-rose-900/50 text-xs">
              <div className="font-semibold text-rose-300 flex items-center gap-2 mb-1">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Blind Spot Taxonomy: {activePair.failure_category}</span>
              </div>
              <p className="text-slate-300 leading-relaxed">
                The multimodal model answered <code className="text-rose-300 font-bold">"{activePair.modified_model_answer}"</code> for
                Condition B when the ground truth was <code className="text-emerald-300 font-bold">"{activePair.modified_expected_answer}"</code>.
                This exposes an attention or localization weakness where the model fails to detect the single physical variation.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
