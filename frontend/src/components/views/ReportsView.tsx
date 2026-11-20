import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  FileCode,
  FileSpreadsheet,
  ExternalLink,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import { BenchmarkReport } from '../../types';
import { api } from '../../services/api';

export const ReportsView: React.FC = () => {
  const [reports, setReports] = useState<BenchmarkReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getReports().then(setReports).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="panel-card p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-cyan-400" />
              <span>Certified Benchmark Reports Center</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Download audited evaluation reports in JSON, CSV, and Markdown formats
            </p>
          </div>
          <span className="badge-cyan font-mono">{reports.length} Reports Generated</span>
        </div>
      </div>

      {/* Reports Grid */}
      {reports.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map(rep => {
            const isJson = rep.file_name.endsWith('.json');
            const isCsv = rep.file_name.endsWith('.csv');
            const Icon = isJson ? FileCode : isCsv ? FileSpreadsheet : FileText;
            const downloadUrl = api.getReportDownloadUrl(rep.file_name);

            return (
              <div key={rep.id} className="panel-card-hover p-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="badge-cyan font-mono uppercase text-[10px]">
                      {rep.format}
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      Run: {rep.evaluation_run_id}
                    </span>
                  </div>

                  <div className="flex items-start gap-3 mt-3">
                    <div className="w-9 h-9 rounded bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 text-cyan-400">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-white leading-snug">
                        {rep.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 font-mono mt-1">
                        {rep.file_name}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">
                    {rep.created_at ? new Date(rep.created_at).toLocaleDateString() : 'Recent'}
                  </span>
                  <a
                    href={downloadUrl}
                    download={rep.file_name}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-800/60 text-xs font-mono font-medium transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download</span>
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="panel-card p-12 text-center text-slate-500 text-xs">
          No benchmark reports generated yet. Run an evaluation in Model Arena to automatically generate reports.
        </div>
      )}
    </div>
  );
};
