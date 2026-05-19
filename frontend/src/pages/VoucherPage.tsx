import React, { useState, useRef, useMemo } from 'react';
import axios from 'axios';
import { 
  Download, 
  UploadCloud, 
  AlertCircle, 
  FileCheck, 
  Loader2, 
  Sparkles, 
  AlertTriangle, 
  FileUp, 
  ChevronDown, 
  ChevronUp, 
  Lightbulb, 
  Wrench,
  ArrowRight,
  Database,
  Search,
  CheckCircle2
} from 'lucide-react';
import Chatbot from '../components/Chatbot';

interface VoucherPageProps {
  title: string;
  description: string;
  type: 'bank' | 'sales' | 'purchase' | 'debit-note' | 'credit-note';
}

interface ValidationError {
  row: number;
  field: string;
  current_value: string;
  error: string;
  expected_format: string;
  suggested_fix: string | null;
  solution_steps: string[];
  can_auto_fix: boolean;
  is_critical: boolean;
}

const VoucherPage = ({ title, description, type }: VoucherPageProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Response data state
  const [previewData, setPreviewData] = useState<any>(null);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [expandedErrors, setExpandedErrors] = useState<Record<number, boolean>>({});
  const [autoFixed, setAutoFixed] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 25;
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDownloadSample = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/templates/${type}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_template.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      console.error('Failed to download template', err);
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error' || !err.response) {
        alert('Backend server is not running on port 8000');
      } else {
        alert('Failed to download template');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      resetState();
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsHovering(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      resetState();
    }
  };

  const resetState = () => {
    setPreviewData(null);
    setErrors([]);
    setColumns([]);
    setAutoFixed(false);
    setExpandedErrors({});
    setCurrentPage(1);
  };

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setAutoFixed(false);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const url = `${apiUrl}/api/${type}/upload?use_ai=${useAI}`;
      const response = await axios.post(url, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setPreviewData(response.data);
      setColumns(response.data.columns || []);
      setErrors(response.data.errors || []);
    } catch (err: any) {
      console.error(err);
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error' || !err.response) {
        alert('Backend server is not running on port 8000');
      } else {
        alert('Error processing file: ' + (err.response?.data?.detail?.message || err.response?.data?.detail || err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateXML = async () => {
    if (!file) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const url = `${apiUrl}/api/${type}/generate-xml?use_ai=${useAI}&auto_fixed=${autoFixed}`;
      const response = await axios.post(url, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob',
      });
      
      const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `${type}_voucher.xml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      console.error(err);
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error' || !err.response) {
        alert('Backend server is not running on port 8000');
      } else if (err.response?.data) {
        try {
          const text = await err.response.data.text();
          const detail = JSON.parse(text).detail;
          alert(detail.message || "Validation errors found.");
        } catch(e) {
          alert('Error generating XML');
        }
      } else {
        alert('Error generating XML: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleError = (index: number) => {
    setExpandedErrors(prev => ({ ...prev, [index]: !prev[index] }));
  };

  const handleAutoFix = () => {
    setAutoFixed(true);
    
    // Update preview data to visually correct the table
    if (previewData && previewData.cleaned_data) {
      const updatedPreview = previewData.preview.map((row: any, i: number) => {
        const cleanedRow = previewData.cleaned_data[i];
        if (!cleanedRow) return row;
        
        const newRow = { ...row };
        if (previewData.mapping) {
          Object.entries(previewData.mapping).forEach(([canonical, origCol]) => {
            if (origCol && typeof origCol === 'string' && cleanedRow[canonical] !== undefined && cleanedRow[canonical] !== null) {
              newRow[origCol] = cleanedRow[canonical];
            }
          });
        }
        return newRow;
      });
      
      setPreviewData({ ...previewData, preview: updatedPreview });
    }
  };

  const criticalErrors = useMemo(() => errors.filter(e => e.is_critical), [errors]);
  const fixableErrors = useMemo(() => errors.filter(e => e.can_auto_fix), [errors]);
  
  const displayErrors = autoFixed ? criticalErrors : errors;
  const canGenerateXML = previewData && criticalErrors.length === 0 && (autoFixed || fixableErrors.length === 0);

  const handleChatAction = (action: string) => {
    console.log("Chatbot triggered action:", action);
    if (action === 'AUTO_FIX') {
      if (fixableErrors.length > 0 && !autoFixed) handleAutoFix();
    } else if (action === 'GENERATE_XML') {
      if (canGenerateXML) handleGenerateXML();
    } else if (action === 'REVALIDATE') {
      if (file) handleProcess();
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto min-h-screen animate-fade-in">
      {/* Page Header */}
      <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-blue-400 font-bold uppercase tracking-[0.2em] text-[10px]">
             <Database className="w-3 h-3" /> Dashboard / {type}
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">
            {title}
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl font-medium">
            {description}
          </p>
        </div>
        <button 
          onClick={handleDownloadSample}
          className="btn-secondary flex items-center gap-2 h-fit"
        >
          <Download className="w-4 h-4" /> Download Sample Template
        </button>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
        {/* Left Column: Upload Controls (4 cols) */}
        <div className="xl:col-span-4 space-y-6">
          <div className="glass-card p-8 border-white/10 relative overflow-hidden flex flex-col h-full">
            {/* Background Glow */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl"></div>
            
            <div className="flex items-center gap-3 mb-8">
               <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">1</div>
               <h2 className="text-xl font-bold text-white">Source Configuration</h2>
            </div>
            
            {/* Upload Zone */}
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsHovering(true); }}
              onDragLeave={() => setIsHovering(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative group border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-500 overflow-hidden ${
                isHovering 
                  ? 'border-blue-500 bg-blue-500/5 translate-y-[-4px]' 
                  : 'border-white/10 hover:border-white/20 hover:bg-white/5'
              }`}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept=".xlsx,.xls,.csv" 
                className="hidden" 
              />
              
              {/* Animated Icon Container */}
              <div className={`mx-auto w-20 h-20 mb-6 rounded-2xl bg-white/5 flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:bg-blue-500/10 ${file ? 'text-green-400' : 'text-blue-400'}`}>
                {file ? <FileCheck className="w-10 h-10" /> : <UploadCloud className="w-10 h-10 animate-float" />}
              </div>
              
              <div className="space-y-2">
                <p className="text-white font-bold text-lg">
                  {file ? file.name : "Drop Excel file here"}
                </p>
                <p className="text-slate-400 text-sm font-medium">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : "or click to browse locally"}
                </p>
              </div>

              {/* Hover Indicator */}
              <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-cyan-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-500"></div>
            </div>

            {/* AI Toggle */}
            <div className="mt-8 p-6 rounded-2xl bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent border border-white/5 backdrop-blur-sm">
              <label className="flex items-center justify-between cursor-pointer group">
                <div className="flex gap-4 items-center">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">AI Smart Mapping</span>
                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Detect ambiguous headers</span>
                  </div>
                </div>
                <div className="relative">
                  <input 
                    type="checkbox" 
                    checked={useAI} 
                    onChange={(e) => setUseAI(e.target.checked)} 
                    className="sr-only peer"
                  />
                  <div className="w-12 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-slate-400 after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600 after:shadow-lg peer-checked:after:bg-white"></div>
                </div>
              </label>
            </div>

            <div className="mt-auto pt-8">
              <button
                onClick={handleProcess}
                disabled={!file || loading}
                className="btn-primary w-full flex justify-center items-center gap-3 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <ArrowRight className="w-6 h-6" />}
                {loading ? 'Processing Data...' : 'Analyze Data Source'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Preview & Errors (8 cols) */}
        <div className="xl:col-span-8 space-y-6">
          <div className="glass-card p-8 border-white/10 min-h-[600px] flex flex-col relative overflow-hidden">
             {/* Background Glow */}
             <div className="absolute bottom-0 right-0 -mb-20 -mr-20 w-64 h-64 bg-cyan-500/5 rounded-full blur-[100px]"></div>

            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                 <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-sm">2</div>
                 <h2 className="text-xl font-bold text-white">Validation Engine</h2>
              </div>
              {previewData && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                   <Search className="w-3 h-3" /> Real-time Diagnostics
                </div>
              )}
            </div>
            
            {previewData ? (
              <div className="flex-1 flex flex-col h-full space-y-8">
                
                {/* Stats Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-5 rounded-2xl bg-white/5 border-l-4 border-blue-500 shadow-sm hover:bg-white/10 transition-colors">
                    <span className="text-[10px] font-bold text-slate-500 block uppercase tracking-[0.2em] mb-1">Total Entries</span>
                    <span className="text-3xl font-black text-white">{previewData.total_rows}</span>
                  </div>
                  <div className="p-5 rounded-2xl bg-white/5 border-l-4 border-green-500 shadow-sm hover:bg-white/10 transition-colors">
                    <span className="text-[10px] font-bold text-slate-500 block uppercase tracking-[0.2em] mb-1">Processed</span>
                    <span className="text-3xl font-black text-green-400">{previewData.total_rows - criticalErrors.length}</span>
                  </div>
                  <div className={`p-5 rounded-2xl bg-white/5 border-l-4 shadow-sm hover:bg-white/10 transition-colors ${criticalErrors.length > 0 ? 'border-red-500' : 'border-slate-700 opacity-50'}`}>
                    <span className="text-[10px] font-bold text-slate-500 block uppercase tracking-[0.2em] mb-1">Critical</span>
                    <span className={`text-3xl font-black ${criticalErrors.length > 0 ? 'text-red-500' : 'text-slate-400'}`}>{criticalErrors.length}</span>
                  </div>
                  <div className={`p-5 rounded-2xl bg-white/5 border-l-4 shadow-sm hover:bg-white/10 transition-colors ${fixableErrors.length > 0 ? 'border-yellow-500' : 'border-slate-700 opacity-50'}`}>
                    <span className="text-[10px] font-bold text-slate-500 block uppercase tracking-[0.2em] mb-1">Auto-Fixable</span>
                    <span className={`text-3xl font-black ${fixableErrors.length > 0 ? 'text-yellow-400' : 'text-slate-400'}`}>{fixableErrors.length}</span>
                  </div>
                </div>

                {/* Auto-Fix Banner */}
                {fixableErrors.length > 0 && !autoFixed && (
                  <div className="p-6 rounded-2xl bg-gradient-to-r from-yellow-500/20 to-orange-500/10 border border-yellow-500/30 flex items-center justify-between shadow-lg backdrop-blur-sm animate-fade-in">
                    <div className="flex items-center gap-5">
                      <div className="bg-yellow-500/20 p-3 rounded-xl">
                        <Wrench className="w-6 h-6 text-yellow-500" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white text-lg">Format Incompatibilities Found</h4>
                        <p className="text-sm text-yellow-500/80 font-medium">AI detected {fixableErrors.length} issues we can fix automatically.</p>
                      </div>
                    </div>
                    <button 
                      onClick={handleAutoFix}
                      className="bg-yellow-500 hover:bg-yellow-400 text-[#0f172a] font-black py-3 px-6 rounded-xl shadow-[0_0_20px_rgba(234,179,8,0.3)] transition-all flex items-center gap-2 text-sm active:scale-95"
                    >
                      <Sparkles className="w-4 h-4" /> Resolve Now
                    </button>
                  </div>
                )}
                
                {autoFixed && fixableErrors.length > 0 && (
                   <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 flex items-center gap-3 text-sm font-bold animate-fade-in shadow-lg shadow-green-500/5">
                     <CheckCircle2 className="w-5 h-5" /> All format issues successfully sanitized!
                   </div>
                )}

                {/* Main Data View Shell */}
                <div className="flex-1 min-h-[400px] flex flex-col space-y-6">
                  {/* Table Shell */}
                  <div className="flex-1 bg-[#020617]/50 border border-white/5 rounded-2xl overflow-hidden relative shadow-inner">
                    <div className="overflow-x-auto absolute inset-0 custom-scrollbar">
                      <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-white/5 sticky top-0 z-10 text-slate-500 font-bold text-[10px] tracking-widest uppercase border-b border-white/10">
                          <tr>
                            <th className="px-6 py-4 border-r border-white/5">Row</th>
                            {columns.map((col, i) => (
                              <th key={i} className="px-6 py-4 border-r border-white/5">
                                <div className="flex flex-col gap-1">
                                  <span>{col}</span>
                                  {previewData.mapping && Object.entries(previewData.mapping).find(([_, v]) => v === col) && (
                                    <span className="text-[9px] text-blue-400 font-bold bg-blue-500/10 w-max px-2 py-0.5 rounded-full border border-blue-500/20">
                                      {Object.entries(previewData.mapping).find(([_, v]) => v === col)?.[0]}
                                    </span>
                                  )}
                                </div>
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-slate-400">
                          {previewData.preview
                            .slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage)
                            .map((row: any, i: number) => {
                              const rowErrors = displayErrors.filter(e => e.row === row._row);
                              const hasCritical = rowErrors.some(e => e.is_critical);
                              
                              return (
                                <tr key={i} className={`transition-colors duration-200 ${hasCritical ? 'bg-red-500/5 hover:bg-red-500/10' : 'hover:bg-white/[0.02]'}`}>
                                  <td className="px-6 py-4 font-bold text-slate-600 border-r border-white/5 bg-black/20">
                                    <div className="flex items-center justify-between gap-4">
                                      {row._row}
                                      {hasCritical && <AlertCircle className="w-4 h-4 text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.4)]" />}
                                    </div>
                                  </td>
                                  {columns.map((col, j) => {
                                    const canonicalColName = previewData.mapping ? Object.entries(previewData.mapping).find(([_, v]) => v === col)?.[0] : null;
                                    const cellError = rowErrors.find(e => e.field.toLowerCase() === canonicalColName?.toLowerCase() || e.field.toLowerCase() === col.toLowerCase() || (e.field === 'AMOUNT' && (col.toLowerCase().includes('amount') || col.toLowerCase().includes('debit') || col.toLowerCase().includes('credit'))));
                                    const cellValue = row[col] !== null ? String(row[col]) : '';
                                    
                                    return (
                                      <td key={j} className={`px-6 py-4 border-r border-white/5 last:border-r-0 relative group ${cellError ? 'text-white' : ''}`}>
                                        {cellValue ? cellValue : <span className="text-slate-700 italic opacity-50">null</span>}
                                        {cellError && (
                                          <div className="absolute inset-y-1 inset-x-1 bg-red-500/10 border border-red-500/20 rounded-lg -z-0"></div>
                                        )}
                                        {cellError && (
                                          <div className="absolute opacity-0 group-hover:opacity-100 transition-all duration-300 bottom-full left-1/2 -translate-x-1/2 mb-2 bg-[#020617] border border-red-500/50 text-white text-[11px] p-3 rounded-xl shadow-2xl whitespace-normal w-56 z-20 pointer-events-none backdrop-blur-xl">
                                            <div className="flex items-center gap-2 mb-1 text-red-500 font-bold uppercase tracking-wider">
                                               <AlertCircle className="w-3 h-3" /> Error Detected
                                            </div>
                                            {cellError.error}
                                            {cellError.suggested_fix && <div className="text-green-400 mt-2 p-1.5 rounded bg-green-500/10 border border-green-500/20">Suggestion: {cellError.suggested_fix}</div>}
                                          </div>
                                        )}
                                      </td>
                                    );
                                  })}
                                </tr>
                              );
                            })}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Pagination UI */}
                  {previewData.preview.length > rowsPerPage && (
                    <div className="flex items-center justify-between px-6 py-4 bg-[#020617]/40 border border-white/5 rounded-2xl">
                      <div className="text-xs text-slate-500 font-bold">
                        Showing <span className="text-white">{(currentPage - 1) * rowsPerPage + 1} - {Math.min(currentPage * rowsPerPage, previewData.preview.length)}</span> of <span className="text-white">{previewData.preview.length}</span> entries
                      </div>
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={currentPage === 1}
                          className="px-4 py-2 bg-white/5 rounded-lg text-xs font-bold hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                        >
                          Previous
                        </button>
                        <div className="px-4 py-2 bg-blue-600/10 border border-blue-500/20 rounded-lg text-xs font-black text-blue-400">
                           {currentPage} / {Math.ceil(previewData.preview.length / rowsPerPage)}
                        </div>
                        <button 
                          onClick={() => setCurrentPage(p => Math.min(Math.ceil(previewData.preview.length / rowsPerPage), p + 1))}
                          disabled={currentPage >= Math.ceil(previewData.preview.length / rowsPerPage)}
                          className="px-4 py-2 bg-white/5 rounded-lg text-xs font-bold hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Errors Detail View */}
                  {displayErrors.length > 0 && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 mb-2 ml-1">
                         <div className="w-1.5 h-1.5 rounded-full bg-red-500"></div>
                         <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Logic & Validation Reports</h3>
                      </div>
                      {displayErrors.map((err, i) => (
                        <div key={i} className="glass-card border-white/10 overflow-hidden group hover:border-red-500/30">
                          <div 
                            className="p-4 flex items-center justify-between cursor-pointer"
                            onClick={() => toggleError(i)}
                          >
                            <div className="flex items-center gap-4">
                              <span className={`text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-tighter ${err.is_critical ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'}`}>
                                Row {err.row}
                              </span>
                              <span className="font-bold text-white text-sm flex items-center gap-2">
                                {err.is_critical ? <AlertCircle className="w-4 h-4 text-red-500" /> : <AlertTriangle className="w-4 h-4 text-yellow-400" />}
                                <span className="text-slate-500">[{err.field}]</span> {err.error}
                              </span>
                            </div>
                            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                               {expandedErrors[i] ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                            </div>
                          </div>
                          
                          {expandedErrors[i] && (
                            <div className="p-6 border-t border-white/5 bg-white/[0.02] text-sm animate-fade-in">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                <div className="space-y-2">
                                  <span className="text-slate-500 text-[10px] font-black uppercase tracking-widest block">Original Context</span>
                                  <div className="p-4 bg-red-500/5 rounded-xl border border-red-500/10 font-mono text-red-400 line-through truncate">
                                    {String(err.current_value)}
                                  </div>
                                </div>
                                <div className="space-y-2">
                                  <span className="text-slate-500 text-[10px] font-black uppercase tracking-widest block">Standard Required</span>
                                  <div className="p-4 bg-green-500/5 rounded-xl border border-green-500/10 font-mono text-green-400">
                                    {err.expected_format}
                                  </div>
                                </div>
                              </div>
                              
                              <div className="flex flex-col md:flex-row gap-6">
                                <div className="flex-1 space-y-4">
                                  <div className="flex items-center gap-2 text-white font-bold">
                                     <Wrench className="w-4 h-4 text-blue-400" /> Resolve Recommendation
                                  </div>
                                  <ul className="space-y-3">
                                    {err.solution_steps.map((step, idx) => (
                                      <li key={idx} className="flex gap-3 text-slate-400 font-medium">
                                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
                                        {step}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                                {err.suggested_fix && (
                                  <div className="w-full md:w-64 p-5 rounded-2xl bg-gradient-to-br from-green-500/20 to-transparent border border-green-500/20 flex flex-col items-center justify-center text-center">
                                     <Lightbulb className="w-8 h-8 text-green-400 mb-3 animate-pulse" />
                                     <span className="text-[10px] text-green-500/80 font-bold uppercase mb-2">Auto-fix Result</span>
                                     <span className="text-white font-bold text-lg">{err.suggested_fix}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Dashboard Final Actions */}
                  <div className="pt-10 mt-auto border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-6">
                    <div className="flex flex-col">
                       <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-1">Status Report</span>
                       <div className="flex items-center gap-4">
                          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
                             <div className={`w-1.5 h-1.5 rounded-full ${criticalErrors.length === 0 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 animate-pulse'}`}></div>
                             {criticalErrors.length === 0 ? 'Ready for Import' : 'Critical Blocks'}
                          </div>
                       </div>
                    </div>
                    <button
                      onClick={handleGenerateXML}
                      disabled={!canGenerateXML || loading}
                      className={`btn-primary px-12 py-4 text-xl flex items-center gap-3 active:scale-95 disabled:opacity-30 disabled:grayscale disabled:cursor-not-allowed disabled:hover:shadow-none min-w-[300px] justify-center ${criticalErrors.length > 0 ? '' : 'animate-glow'}`}
                    >
                      {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <FileUp className="w-6 h-6" />}
                      {!previewData ? 'Launch Engine First' : 
                       criticalErrors.length > 0 ? 'Errors Detected' : 
                       'Generate Tally XML'}
                    </button>
                  </div>
                </div>

              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 h-full border border-white/5 rounded-3xl bg-white/[0.01] group relative overflow-hidden">
                {/* Background Decor */}
                <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:20px_20px]"></div>
                
                <div className="w-24 h-24 mb-8 rounded-3xl bg-white/5 flex items-center justify-center relative shadow-2xl group-hover:scale-110 transition-transform duration-500">
                  <div className="absolute inset-0 border border-blue-500/20 rounded-3xl animate-[spin_8s_linear_infinite]"></div>
                  <AlertCircle className="w-10 h-10 text-slate-600" />
                </div>
                <h3 className="text-2xl font-black text-white mb-3">Initialize Analysis Engine</h3>
                <p className="text-center max-w-sm text-slate-500 font-medium leading-relaxed">
                  Upload your data source to begin the professional Tally conversion sequence.
                </p>
              </div>
            )}
            
          </div>
        </div>
      </div>
      <Chatbot errors={displayErrors} fileName={file?.name} onActionTriggered={handleChatAction} />
    </div>
  );
};

export default VoucherPage;
