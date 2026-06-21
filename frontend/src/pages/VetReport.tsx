import React from 'react';
import { FileText, Download, Mail, Calendar } from 'lucide-react';

const VetReport: React.FC = () => {
  const reports = [
    { id: 1, pet: 'Luna', date: 'June 5, 2026', type: 'Anomaly Follow-up' },
    { id: 2, pet: 'Luna', date: 'May 30, 2026', type: 'Monthly Summary' },
    { id: 3, pet: 'Cooper', date: 'May 15, 2026', type: 'Monthly Summary' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Vet Reports</h2>
        <p className="text-slate-500">Generate and share detailed health insights for your veterinarian</p>
      </div>

      <div className="bg-gradient-to-br from-violet-600 to-indigo-700 rounded-3xl p-8 text-white">
        <div className="max-w-lg">
          <h3 className="text-2xl font-bold mb-4">Need a new report?</h3>
          <p className="opacity-90 mb-8">Select a pet and date range to generate a comprehensive health PDF including activity trends, sleep quality, and any detected anomalies.</p>
          <button className="bg-white text-violet-600 px-6 py-3 rounded-xl font-bold hover:bg-violet-50 transition-colors">
            Generate Report
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Recent Reports</h3>
        <div className="grid grid-cols-1 gap-4">
          {reports.map((report) => (
            <div 
              key={report.id}
              className="bg-white border border-slate-200 rounded-2xl p-4 flex items-center justify-between group hover:border-violet-300 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 group-hover:bg-violet-50 group-hover:text-violet-600 transition-colors">
                  <FileText size={24} />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800">{report.pet} - {report.type}</h4>
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <Calendar size={14} />
                    {report.date}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2 text-slate-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all" title="Download PDF">
                  <Download size={20} />
                </button>
                <button className="p-2 text-slate-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all" title="Email to Vet">
                  <Mail size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VetReport;
