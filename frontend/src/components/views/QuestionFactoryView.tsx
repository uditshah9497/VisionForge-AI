import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Code2,
  Tag,
  Search,
  ExternalLink
} from 'lucide-react';
import { QuestionItem } from '../../types';
import { api } from '../../services/api';

export const QuestionFactoryView: React.FC = () => {
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const data = await api.getQuestions({
        category: selectedCategory || undefined,
        difficulty: selectedDifficulty || undefined,
        status: selectedStatus || undefined
      });
      setQuestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, [selectedCategory, selectedDifficulty, selectedStatus]);

  const filtered = questions.filter(q =>
    q.question_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
    q.expected_answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header and Filter Controls */}
      <div className="panel-card p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-cyan-400" />
              <span>Verifiable Question Factory</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Deterministic, template-generated visual reasoning tasks with verifiable reference answers
            </p>
          </div>
          <span className="badge-cyan font-mono">{filtered.length} Questions Displayed</span>
        </div>

        {/* Filters Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
            <input
              type="text"
              placeholder="Search questions or answers..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full bg-[#080C14] border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-slate-200 outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={selectedCategory}
            onChange={e => setSelectedCategory(e.target.value)}
            className="bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 outline-none focus:border-cyan-500"
          >
            <option value="">All Categories (5 Types)</option>
            <option value="identification">Object Identification</option>
            <option value="counting">Object Counting</option>
            <option value="spatial">Spatial Reasoning</option>
            <option value="anomaly_detection">Anomaly Detection</option>
            <option value="relationship">Component Relationship</option>
          </select>

          <select
            value={selectedDifficulty}
            onChange={e => setSelectedDifficulty(e.target.value)}
            className="bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 outline-none focus:border-cyan-500"
          >
            <option value="">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <select
            value={selectedStatus}
            onChange={e => setSelectedStatus(e.target.value)}
            className="bg-[#080C14] border border-slate-800 rounded-lg px-3 py-2 text-slate-200 outline-none focus:border-cyan-500"
          >
            <option value="">All Validation Statuses</option>
            <option value="PASS">PASS (Validated)</option>
            <option value="FAIL">FAIL (Quarantined)</option>
          </select>
        </div>
      </div>

      {/* Questions List */}
      {loading ? (
        <div className="h-64 flex items-center justify-center text-xs text-slate-400 font-mono">
          Loading verified question factory records...
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map(q => (
            <div key={q.id} className="panel-card-hover p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="badge-cyan capitalize font-mono text-[10px]">
                      {q.category.replace('_', ' ')}
                    </span>
                    <span className="badge-slate capitalize font-mono text-[10px]">
                      {q.difficulty}
                    </span>
                  </div>
                  <span
                    className={`font-mono text-[10px] ${
                      q.validation_status === 'PASS' ? 'badge-emerald' : 'badge-rose'
                    }`}
                  >
                    {q.validation_status}
                  </span>
                </div>

                <div className="flex gap-3 mt-3">
                  {q.image_url && (
                    <img
                      src={q.image_url}
                      alt="Thumbnail"
                      className="w-16 h-16 rounded object-cover border border-slate-800 shrink-0"
                    />
                  )}
                  <div>
                    <h3 className="text-sm font-medium text-white leading-snug">
                      {q.question_text}
                    </h3>
                  </div>
                </div>
              </div>

              {/* Ground Truth Separated Display */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500 font-mono">Expected Ground Truth:</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/60 text-emerald-400 font-mono font-bold">
                    {q.expected_answer}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">Type: {q.answer_type}</span>
              </div>

              {/* Derivation Rule Trace */}
              {q.derivation_rule && (
                <div className="mt-2 text-[10px] font-mono text-slate-500 truncate">
                  Rule: {q.derivation_rule}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="panel-card p-12 text-center text-slate-500 text-xs">
          No questions matched your filter criteria.
        </div>
      )}
    </div>
  );
};
