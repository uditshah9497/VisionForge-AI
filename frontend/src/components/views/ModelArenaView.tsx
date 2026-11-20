import React, { useState, useEffect } from 'react';
import {
  Swords,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Coins,
  Bot,
  AlertCircle,
  FileText,
  Sparkles
} from 'lucide-react';
import { Dataset, ModelConfig, EvaluationRun } from '../../types';
import { api } from '../../services/api';

interface ModelArenaViewProps {
  datasets: Dataset[];
  selectedDatasetId: string;
}

export const ModelArenaView: React.FC<ModelArenaViewProps> = ({
  datasets,
  selectedDatasetId
}) => {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('visionforge-demo-v1');
  const [maxQuestions, setMaxQuestions] = useState<number>(10);
  const [isRunning, setIsRunning] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<EvaluationRun | null>(null);
  const [evalHistory, setEvalHistory] = useState<EvaluationRun[]>([]);

  useEffect(() => {
    api.getModels().then(setModels).catch(console.error);
    api.getEvaluations().then(data => {
      setEvalHistory(data);
      if (data.length > 0) {
        api.getEvaluation(data[0].id).then(setEvaluationResult).catch(console.error);
      }
    }).catch(console.error);
  }, []);

  const handleRunEvaluation = async () => {
    if (!selectedDatasetId) {
      alert('Please select an active dataset first.');
      return;
    }
    const modelObj = models.find(m => m.id === selectedModel);
    const provider = modelObj ? modelObj.provider : 'demo';

    setIsRunning(true);
    try {
      const res = await api.runEvaluation({
        dataset_id: selectedDatasetId,
        model_name: selectedModel,
        provider,
        max_questions: maxQuestions
      });
      setEvaluationResult(res);
      // Reload history
      const history = await api.getEvaluations();
      setEvalHistory(history);
    } catch (err: any) {
      alert(`Evaluation error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const currentModelConfig = models.find(m => m.id === selectedModel);

  return (
    <div className="space-y-6">
      {/* Configuration & Launch Panel */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Swords className="w-5 h-5 text-purple-400" />
              <span>Multimodal Model Arena & Benchmarking Suite</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Evaluate frontier vision models across verified manufacturing assembly tasks
            </p>
          </div>
          {currentModelConfig?.is_configured ? (
            <span className="badge-emerald font-mono flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              API Credentials Configured
            </span>
          ) : (
            <span className="badge-amber font-mono">
              Calibrated Simulator Mode
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
          {/* Model Selector */}
          <div className="md:col-span-2">
            <label className="block text-slate-400 font-medium mb-1.5">Select Multimodal Model</label>
            <div className="grid grid-cols-1 gap-2">
              {models.map(m => (
                <div
                  key={m.id}
                  onClick={() => setSelectedModel(m.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                    selectedModel === m.id
                      ? 'bg-purple-950/40 border-purple-500/60 text-white'
                      : 'bg-[#080C14] border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Bot className={`w-4 h-4 ${selectedModel === m.id ? 'text-purple-400' : 'text-slate-500'}`} />
                    <div>
                      <div className="font-semibold">{m.name}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">{m.description}</div>
                    </div>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                    m.is_configured
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      : 'bg-slate-800 text-slate-400'
                  }`}>
                    {m.is_configured ? 'Live API' : 'Calibrated Simulator'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Settings & Trigger */}
          <div className="space-y-4 md:col-span-2 flex flex-col justify-between">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">
                Benchmark Sample Size ({maxQuestions} Tasks)
              </label>
              <input
                type="range"
                min={2}
                max={30}
                value={maxQuestions}
                onChange={e => setMaxQuestions(Number(e.target.value))}
                className="w-full accent-purple-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Evenly samples across Identification, Counting, Spatial Reasoning, and Anomaly Detection.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-300 space-y-1">
              <div className="font-semibold text-white">Evaluation Rules Enforcement:</div>
              <div>• Deterministic answer normalization extracts clean tokens from verbose reasoning.</div>
              <div>• Ground truth is never shared with or altered by the evaluated model.</div>
              <div>• Detailed metrics record latency (ms), token usage, and cost per task.</div>
            </div>

            <button
              onClick={handleRunEvaluation}
              disabled={isRunning}
              className="w-full py-3 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-purple-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{isRunning ? 'Evaluating Multimodal Model...' : `Run Benchmark on ${currentModelConfig?.name || selectedModel}`}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Benchmark Results Display */}
      {evaluationResult && (
        <div className="space-y-6">
          {/* Summary KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="panel-card p-4 border-purple-500/30">
              <div className="text-xs text-slate-400">Benchmark Model</div>
              <div className="text-sm font-bold font-mono text-white mt-1 truncate">
                {evaluationResult.model_name}
              </div>
              <div className="text-[10px] text-purple-400 font-mono mt-0.5">
                Provider: {evaluationResult.model_provider}
              </div>
            </div>

            <div className="panel-card p-4 border-emerald-500/30">
              <div className="text-xs text-slate-400">Overall Accuracy</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                {(evaluationResult.overall_accuracy * 100).toFixed(1)}%
              </div>
              <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                {evaluationResult.total_tasks} Tasks Evaluated
              </div>
            </div>

            <div className="panel-card p-4 border-blue-500/30">
              <div className="text-xs text-slate-400">Mean Latency</div>
              <div className="text-2xl font-bold font-mono text-blue-400 mt-1 flex items-center gap-1">
                <Clock className="w-4 h-4 text-blue-400" />
                <span>{evaluationResult.avg_latency_ms.toFixed(1)} ms</span>
              </div>
              <div className="text-[10px] text-slate-400 font-mono mt-0.5">Real-time inference speed</div>
            </div>

            <div className="panel-card p-4 border-amber-500/30">
              <div className="text-xs text-slate-400">Total Compute Cost</div>
              <div className="text-2xl font-bold font-mono text-amber-400 mt-1 flex items-center gap-1">
                <Coins className="w-4 h-4 text-amber-400" />
                <span>${evaluationResult.total_cost_usd.toFixed(6)}</span>
              </div>
              <div className="text-[10px] text-slate-400 font-mono mt-0.5">USD Estimated</div>
            </div>
          </div>

          {/* Task-by-Task Response Inspector */}
          <div className="panel-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">Itemized Task Evaluations & Normalized Answers</h3>
                <p className="text-xs text-slate-400">
                  Detailed inspection of model output, normalized answer, ground truth, and correctness
                </p>
              </div>
              <span className="badge-purple font-mono">Run ID: {evaluationResult.id}</span>
            </div>

            <div className="space-y-3">
              {evaluationResult.responses?.map((r, i) => (
                <div
                  key={i}
                  className={`p-3.5 rounded-lg border text-xs transition-colors ${
                    r.is_correct
                      ? 'bg-emerald-950/10 border-emerald-900/40'
                      : 'bg-rose-950/10 border-rose-900/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="badge-cyan font-mono text-[10px] capitalize">
                        {r.category.replace('_', ' ')}
                      </span>
                      <span className="badge-slate font-mono text-[10px] capitalize">
                        {r.difficulty}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 font-mono text-[11px]">
                      <span>{r.latency_ms.toFixed(0)} ms</span>
                      {r.is_correct ? (
                        <span className="badge-emerald flex items-center gap-1 text-[10px]">
                          <CheckCircle2 className="w-3 h-3" /> PASS
                        </span>
                      ) : (
                        <span className="badge-rose flex items-center gap-1 text-[10px]">
                          <XCircle className="w-3 h-3" /> FAIL ({r.failure_category || 'incorrect'})
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="text-white font-medium text-xs mb-2">
                    {r.question_text}
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2 pt-2 border-t border-slate-800/60 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-500">Expected Ground Truth:</span>
                      <div className="text-emerald-400 font-bold">{r.expected_answer}</div>
                    </div>
                    <div>
                      <span className="text-slate-500">Normalized Model Output:</span>
                      <div className={`font-bold ${r.is_correct ? 'text-emerald-300' : 'text-rose-400'}`}>
                        {r.normalized_answer || 'Empty/Unparseable'}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-500">Raw Model Response:</span>
                      <div className="text-slate-400 truncate" title={r.model_response}>
                        {r.model_response}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
