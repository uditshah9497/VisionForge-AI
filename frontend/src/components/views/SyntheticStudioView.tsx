import React, { useState } from 'react';
import {
  Cpu,
  Sparkles,
  Sliders,
  Eye,
  CheckCircle2,
  AlertOctagon,
  Layers,
  Sun,
  ShieldCheck,
  ChevronRight,
  Maximize2,
  X
} from 'lucide-react';
import { Dataset, SceneItem } from '../../types';
import { api } from '../../services/api';

interface SyntheticStudioViewProps {
  datasets: Dataset[];
  selectedDataset: any;
  onRefresh: () => void;
}

export const SyntheticStudioView: React.FC<SyntheticStudioViewProps> = ({
  datasets,
  selectedDataset,
  onRefresh
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [form, setForm] = useState({
    name: 'Industrial Assembly Test Bench',
    image_count: 5,
    components_per_scene: 6,
    difficulty: 'medium',
    defect_types: ['missing', 'misplaced', 'orientation', 'occlusion'],
    lighting: 'standard_5000k',
    seed: 42
  });

  const [activeScene, setActiveScene] = useState<SceneItem | null>(null);
  const [showBBoxes, setShowBBoxes] = useState(true);

  const handleDefectToggle = (defect: string) => {
    setForm(prev => {
      const exists = prev.defect_types.includes(defect);
      return {
        ...prev,
        defect_types: exists
          ? prev.defect_types.filter(d => d !== defect)
          : [...prev.defect_types, defect]
      };
    });
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    try {
      await api.generateDataset(form);
      onRefresh();
    } catch (err: any) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const scenes: SceneItem[] = selectedDataset?.scenes || [];

  return (
    <div className="space-y-6">
      {/* Studio Header & Configuration Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Parametric Config Panel */}
        <div className="panel-card p-5 lg:col-span-1">
          <div className="flex items-center gap-2 mb-4 text-cyan-400 font-semibold text-sm">
            <Sliders className="w-4 h-4" />
            <span>Parametric Scene Generator</span>
          </div>

          <form onSubmit={handleGenerate} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1">Dataset Name</label>
              <input
                type="text"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-100 outline-none focus:border-cyan-500"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Image Count ({form.image_count})</label>
                <input
                  type="range"
                  min={1}
                  max={20}
                  value={form.image_count}
                  onChange={e => setForm({ ...form, image_count: Number(e.target.value) })}
                  className="w-full accent-cyan-400"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Components/Scene ({form.components_per_scene})</label>
                <input
                  type="range"
                  min={3}
                  max={10}
                  value={form.components_per_scene}
                  onChange={e => setForm({ ...form, components_per_scene: Number(e.target.value) })}
                  className="w-full accent-cyan-400"
                />
              </div>
            </div>

            {/* Difficulty Pills */}
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Difficulty Tier</label>
              <div className="grid grid-cols-3 gap-2">
                {['easy', 'medium', 'hard'].map(d => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setForm({ ...form, difficulty: d })}
                    className={`py-1.5 rounded-lg font-mono capitalize transition-all ${
                      form.difficulty === d
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/50'
                        : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Defect Injections */}
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Injectable Defect Types</label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'missing', label: 'Missing Part' },
                  { id: 'misplaced', label: 'Misplaced (Δx,y)' },
                  { id: 'orientation', label: 'Inverted (180°)' },
                  { id: 'occlusion', label: 'Wire Occlusion' }
                ].map(item => (
                  <label
                    key={item.id}
                    className="flex items-center gap-2 p-2 rounded bg-[#080C14] border border-slate-800 text-slate-300 cursor-pointer hover:border-slate-700"
                  >
                    <input
                      type="checkbox"
                      checked={form.defect_types.includes(item.id)}
                      onChange={() => handleDefectToggle(item.id)}
                      className="rounded accent-cyan-500"
                    />
                    <span>{item.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Lighting Profile */}
            <div>
              <label className="block text-slate-400 font-medium mb-1">Workstation Lighting</label>
              <select
                value={form.lighting}
                onChange={e => setForm({ ...form, lighting: e.target.value })}
                className="w-full bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 outline-none focus:border-cyan-500"
              >
                <option value="standard_5000k">Daylight Standard (5000K Industrial)</option>
                <option value="tungsten_3200k">Warm Tungsten (3200K)</option>
                <option value="low_light">Low Ambient Lux (Stress Test)</option>
                <option value="harsh_shadows">Specular High-Contrast Directional</option>
              </select>
            </div>

            {/* Random Seed */}
            <div>
              <label className="block text-slate-400 font-medium mb-1">Reproducibility Seed</label>
              <input
                type="number"
                value={form.seed}
                onChange={e => setForm({ ...form, seed: Number(e.target.value) })}
                className="w-full bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-100 font-mono outline-none focus:border-cyan-500"
              />
            </div>

            <button
              type="submit"
              disabled={isGenerating}
              className="w-full mt-2 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
            >
              {isGenerating ? 'Synthesizing Benchmark...' : 'Generate Synthetic Dataset'}
            </button>
          </form>
        </div>

        {/* Gallery of Generated Scenes */}
        <div className="panel-card p-5 lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Rendered Workstation Gallery</h3>
                <p className="text-xs text-slate-400">
                  {selectedDataset ? `${selectedDataset.name} (Seed #${selectedDataset.seed})` : 'Select or generate a dataset'}
                </p>
              </div>
              <span className="badge-cyan font-mono">{scenes.length} Scenes Available</span>
            </div>

            {scenes.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {scenes.map(s => (
                  <div
                    key={s.id}
                    onClick={() => setActiveScene(s)}
                    className="group relative rounded-lg overflow-hidden border border-slate-800 bg-slate-950 hover:border-cyan-500/60 transition-all cursor-pointer shadow-md"
                  >
                    <img
                      src={s.image_url}
                      alt={`Scene ${s.scene_number}`}
                      className="w-full h-36 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent flex flex-col justify-end p-2.5">
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <span className="text-cyan-300 font-semibold">Scene #{s.scene_number}</span>
                        <span className="text-slate-400">{s.questions.length} Questions</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-center p-6 border border-dashed border-slate-800 rounded-lg text-slate-500 text-xs">
                <Cpu className="w-8 h-8 text-slate-600 mb-2" />
                <p>No synthetic scenes generated yet.</p>
                <p className="mt-1">Configure parameters on the left to start automated scene generation.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Interactive Scene Inspector Modal */}
      {activeScene && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0B0F19] border border-slate-800 rounded-xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="badge-cyan font-mono">Scene #{activeScene.scene_number}</span>
                <h3 className="font-semibold text-white text-sm">Synthetic Scene Graph & Visual Inspector</h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowBBoxes(!showBBoxes)}
                  className={`px-3 py-1 rounded text-xs font-mono transition-colors border ${
                    showBBoxes
                      ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}
                >
                  {showBBoxes ? 'Bounding Boxes: ON' : 'Bounding Boxes: OFF'}
                </button>
                <button
                  onClick={() => setActiveScene(null)}
                  className="p-1 text-slate-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-4 overflow-y-auto grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Image View with Canvas Overlays */}
              <div className="space-y-3">
                <div className="relative rounded-lg overflow-hidden border border-slate-800 bg-black">
                  <img
                    src={activeScene.image_url}
                    alt="Active Scene Inspection"
                    className="w-full h-auto object-contain"
                  />
                  {showBBoxes && (
                    <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 800 600">
                      {activeScene.scene_graph?.components?.map((c, i) => {
                        const [x1, y1, x2, y2] = c.bbox;
                        const isDef = c.is_defective;
                        const color = isDef ? '#EF4444' : '#06B6D4';
                        return (
                          <g key={i}>
                            <rect
                              x={x1}
                              y={y1}
                              width={x2 - x1}
                              height={y2 - y1}
                              fill="none"
                              stroke={color}
                              strokeWidth={2}
                              strokeDasharray={isDef ? '4,4' : 'none'}
                            />
                            <text
                              x={x1}
                              y={Math.max(12, y1 - 4)}
                              fill={color}
                              fontSize={10}
                              fontFamily="monospace"
                              fontWeight="bold"
                            >
                              {c.name} {isDef ? `[${c.defect_type}]` : ''}
                            </text>
                          </g>
                        );
                      })}
                    </svg>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 px-1 font-mono">
                  <span>Dimensions: 800 x 600 px</span>
                  <span>Seed: #{activeScene.seed}</span>
                  <span>Components: {activeScene.scene_graph?.components?.length || 0}</span>
                </div>
              </div>

              {/* Metadata & Associated Questions */}
              <div className="space-y-4">
                {/* Questions for this scene */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-300 uppercase font-mono mb-2">
                    Associated Ground-Truth Questions
                  </h4>
                  <div className="space-y-2">
                    {activeScene.questions.map((q, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
                        <div className="flex items-center justify-between text-[10px] font-mono mb-1">
                          <span className="text-cyan-400 capitalize">{q.category.replace('_', ' ')}</span>
                          <span className="badge-emerald uppercase text-[9px]">{q.validation_status}</span>
                        </div>
                        <p className="text-slate-200 font-medium mb-1.5">{q.question_text}</p>
                        <div className="flex items-center gap-2 text-[11px] font-mono text-emerald-400">
                          <span className="text-slate-500">Expected:</span>
                          <span className="bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-800/50">
                            {q.expected_answer}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Raw Scene Graph Accordion */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-300 uppercase font-mono mb-2">
                    Scene Graph Metadata (JSON)
                  </h4>
                  <pre className="p-3 rounded-lg bg-black/60 border border-slate-800 text-[10px] font-mono text-cyan-300 h-48 overflow-y-auto">
                    {JSON.stringify(activeScene.scene_graph, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
