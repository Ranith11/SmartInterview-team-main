import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X, Target, BookOpen, Loader2, AlertCircle, CheckCircle,
  TrendingDown, TrendingUp, Minus, ChevronRight, Download,
  Sparkles, Brain, RotateCcw, Trophy, ArrowRight
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../services/api';

/**
 * RemediationModal — Adaptive Mastery Engine UI
 *
 * 3 steps rendered inside a slide-over modal:
 *   Step 1 — DIAGNOSIS: Shows skill breakdown. Button label is dynamic.
 *   Step 2 — NOTES:     Inline AI study notes (mode-aware RAG source).
 *   Step 3 — RETRY:     Spawns focused session, navigates to Interview.
 *
 * Props:
 *   sessionId  {number}  — source interview session ID
 *   mode       {string}  — "normal" or "syllabus"
 *   onClose    {fn}      — closes the modal
 */
export default function RemediationModal({ sessionId, mode, onClose }) {
  const navigate = useNavigate();

  // ── State ────────────────────────────────────────────────────────────────
  const [step, setStep] = useState('loading'); // 'loading' | 'diagnosis' | 'notes' | 'starting'
  const [diagnosis, setDiagnosis] = useState(null);
  const [notes, setNotes] = useState(null);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');

  // ── Load diagnosis on mount ───────────────────────────────────────────────
  useEffect(() => {
    loadDiagnosis();
  }, [sessionId]);

  const loadDiagnosis = async () => {
    setStep('loading');
    setError('');
    try {
      const res = await api.get(`/interviews/${sessionId}/remediation/diagnosis`);
      setDiagnosis(res.data);
      setStep('diagnosis');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load session diagnosis.');
      setStep('error');
    }
  };

  const loadNotes = async () => {
    setLoadingNotes(true);
    setError('');
    try {
      const res = await api.get(`/interviews/${sessionId}/remediation/notes`);
      setNotes(res.data);
      setStep('notes');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate study notes.');
    } finally {
      setLoadingNotes(false);
    }
  };

  const startRemediation = async () => {
    setStarting(true);
    setError('');
    try {
      const res = await api.post(`/interviews/${sessionId}/remediation/start`);
      navigate(`/interview/${res.data.session_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start focused retry session.');
      setStarting(false);
    }
  };

  // ── PDF Download ─────────────────────────────────────────────────────────
  const downloadNotesPDF = () => {
    if (!notes?.notes_markdown) return;
    const blob = new Blob([notes.notes_markdown], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SmartInterview_StudyNotes_Session_${sessionId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ── Helpers ───────────────────────────────────────────────────────────────
  const getScoreBadge = (score) => {
    if (score >= 75) return { cls: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: <TrendingUp size={12} />, label: 'Mastered' };
    if (score >= 65) return { cls: 'bg-amber-100 text-amber-700 border-amber-200', icon: <Minus size={12} />, label: 'Borderline' };
    return { cls: 'bg-red-100 text-red-700 border-red-200', icon: <TrendingDown size={12} />, label: 'Weak' };
  };

  const sourceLabel = mode === 'syllabus'
    ? '📖 Your Uploaded Syllabus'
    : '🧠 SmartInterview Technical KB (8 Domains)';

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal Panel */}
      <div className="fixed inset-y-0 right-0 w-full max-w-2xl bg-white shadow-2xl z-50
                      flex flex-col overflow-hidden transition-transform duration-300">

        {/* ── Header ── */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100
                        bg-gradient-to-r from-indigo-600 to-violet-600 text-white flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-white/20 rounded-xl flex items-center justify-center">
              {step === 'notes' ? <BookOpen size={18} /> : <Target size={18} />}
            </div>
            <div>
              <div className="font-extrabold text-base tracking-tight">
                {step === 'notes' ? 'AI Study Guide' : 'Skill Diagnosis'}
              </div>
              <div className="text-indigo-200 text-[11px] font-medium">
                {step === 'notes' ? sourceLabel : 'Adaptive Remediation Engine'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {step === 'notes' && (
              <div className="flex gap-1 mr-2">
                <div className={`w-2 h-2 rounded-full bg-white/40`} />
                <div className={`w-2 h-2 rounded-full bg-white`} />
              </div>
            )}
            {step === 'diagnosis' && (
              <div className="flex gap-1 mr-2">
                <div className={`w-2 h-2 rounded-full bg-white`} />
                <div className={`w-2 h-2 rounded-full bg-white/40`} />
              </div>
            )}
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/25 flex items-center
                         justify-center transition-colors cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* ── Body ── */}
        <div className="flex-1 overflow-y-auto">

          {/* LOADING */}
          {step === 'loading' && (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">
              <Loader2 size={36} className="animate-spin text-indigo-500" />
              <p className="font-semibold">Analysing your performance…</p>
            </div>
          )}

          {/* ERROR */}
          {step === 'error' && (
            <div className="p-8 flex flex-col items-center gap-4 text-center">
              <AlertCircle size={40} className="text-red-400" />
              <p className="font-bold text-slate-800">Something went wrong</p>
              <p className="text-sm text-slate-500">{error}</p>
              <button className="btn btn-secondary mt-2" onClick={loadDiagnosis}>
                <RotateCcw size={14} /> Retry
              </button>
            </div>
          )}

          {/* STEP 1 — DIAGNOSIS */}
          {step === 'diagnosis' && diagnosis && (
            <div className="p-6 space-y-5">

              {/* All Mastered Banner */}
              {diagnosis.all_mastered && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 flex gap-4 items-start">
                  <Trophy size={28} className="text-emerald-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-extrabold text-emerald-800 text-base">All Topics Mastered! 🎉</div>
                    <p className="text-sm text-emerald-700 mt-1">
                      You scored ≥ 75% on every topic in this session. No weak areas detected.
                      Try a harder difficulty to keep pushing your limits.
                    </p>
                  </div>
                </div>
              )}

              {/* Summary Chips */}
              {!diagnosis.all_mastered && (
                <div className="flex flex-wrap gap-2">
                  {diagnosis.weak_count > 0 && (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5
                                     bg-red-100 text-red-700 border border-red-200 rounded-full">
                      <TrendingDown size={12} />
                      {diagnosis.weak_count} Weak {diagnosis.weak_count === 1 ? 'Topic' : 'Topics'} (&lt; 65%)
                    </span>
                  )}
                  {diagnosis.borderline_topics?.length > 0 && (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5
                                     bg-amber-100 text-amber-700 border border-amber-200 rounded-full">
                      <Minus size={12} />
                      {diagnosis.borderline_topics.length} Borderline (65–74%)
                    </span>
                  )}
                  {diagnosis.strong_topics?.length > 0 && (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5
                                     bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-full">
                      <CheckCircle size={12} />
                      {diagnosis.strong_topics.length} Mastered (≥ 75%) — Skipped in Retry
                    </span>
                  )}
                </div>
              )}

              {/* Per-skill breakdown */}
              <div className="space-y-2">
                <div className="text-[11px] font-extrabold text-slate-400 uppercase tracking-widest mb-3">
                  Skill Breakdown
                </div>

                {/* Weak Topics */}
                {diagnosis.weak_topics?.map((t) => {
                  const badge = getScoreBadge(t.average_score);
                  return (
                    <div key={t.skill}
                      className="flex items-center justify-between p-3.5 rounded-xl border border-red-100
                                 bg-red-50/50 gap-3">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0" />
                        <span className="font-semibold text-sm text-slate-800 truncate">{t.skill}</span>
                        <span className="text-[10px] text-slate-400 hidden sm:block">
                          ({t.questions_count} Q{t.questions_count !== 1 ? 's' : ''})
                        </span>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5
                                          border rounded-full ${badge.cls}`}>
                          {badge.icon} {badge.label}
                        </span>
                        <span className="text-base font-black text-red-600">{t.average_score}%</span>
                      </div>
                    </div>
                  );
                })}

                {/* Borderline Topics */}
                {diagnosis.borderline_topics?.map((t) => {
                  const badge = getScoreBadge(t.average_score);
                  return (
                    <div key={t.skill}
                      className="flex items-center justify-between p-3.5 rounded-xl border border-amber-100
                                 bg-amber-50/50 gap-3">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="w-2 h-2 rounded-full bg-amber-400 flex-shrink-0" />
                        <span className="font-semibold text-sm text-slate-800 truncate">{t.skill}</span>
                        <span className="text-[10px] text-slate-400 hidden sm:block">
                          ({t.questions_count} Q{t.questions_count !== 1 ? 's' : ''})
                        </span>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5
                                          border rounded-full ${badge.cls}`}>
                          {badge.icon} {badge.label}
                        </span>
                        <span className="text-base font-black text-amber-600">{t.average_score}%</span>
                      </div>
                    </div>
                  );
                })}

                {/* Strong Topics — collapsed row */}
                {diagnosis.strong_topics?.map((t) => (
                  <div key={t.skill}
                    className="flex items-center justify-between p-3 rounded-xl border border-slate-100
                               bg-slate-50/60 gap-3 opacity-60">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0" />
                      <span className="font-medium text-sm text-slate-600 truncate">{t.skill}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-[11px] text-slate-400 font-semibold">Skipped</span>
                      <span className="text-base font-black text-emerald-600">{t.average_score}%</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* RAG Source Info */}
              {!diagnosis.all_mastered && (
                <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3.5 flex gap-2.5 items-start">
                  <Brain size={16} className="text-indigo-500 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-indigo-700 font-medium">
                    Study notes will be generated from <strong>{sourceLabel}</strong> — not synthetic data.
                    The retry session will target only your weak and borderline topics.
                  </p>
                </div>
              )}

              {error && (
                <div className="text-red-600 text-sm flex items-center gap-2 bg-red-50
                                border border-red-100 rounded-xl p-3">
                  <AlertCircle size={14} /> {error}
                </div>
              )}
            </div>
          )}

          {/* STEP 2 — NOTES */}
          {step === 'notes' && notes && (
            <div className="p-6 space-y-4">

              {/* Source badge */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5
                                 bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-full">
                  <Sparkles size={11} /> AI-Generated
                </span>
                <span className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5
                                 bg-slate-100 text-slate-600 border border-slate-200 rounded-full">
                  {sourceLabel}
                </span>
                {notes.rag_chunks_found && (
                  <span className="text-[10px] text-slate-400">
                    ({Object.values(notes.rag_chunks_found).reduce((a, b) => a + b, 0)} reference chunks used)
                  </span>
                )}
              </div>

              {/* Targeted topics reminder */}
              <div className="flex flex-wrap gap-1.5">
                {[...(notes.weak_topics || []), ...(notes.borderline_topics || [])].map(t => (
                  <span key={t} className="text-[11px] font-semibold bg-rose-50 text-rose-700
                                           border border-rose-200 px-2.5 py-1 rounded-full">
                    🎯 {t}
                  </span>
                ))}
              </div>

              {/* Notes content */}
              <div className="prose prose-sm prose-slate max-w-none
                              prose-h2:text-slate-900 prose-h2:font-extrabold prose-h2:text-base
                              prose-h3:text-slate-700 prose-h3:font-bold prose-h3:text-sm
                              prose-code:bg-slate-100 prose-code:px-1 prose-code:rounded
                              prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-pre:rounded-xl
                              prose-li:my-0.5 prose-p:my-1.5
                              border border-slate-100 rounded-2xl p-5 bg-slate-50/50">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {notes.notes_markdown}
                </ReactMarkdown>
              </div>

              {error && (
                <div className="text-red-600 text-sm flex items-center gap-2 bg-red-50
                                border border-red-100 rounded-xl p-3">
                  <AlertCircle size={14} /> {error}
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Footer Actions ── */}
        <div className="flex-shrink-0 px-6 py-4 border-t border-slate-100 bg-white">

          {/* Diagnosis Step Footer */}
          {step === 'diagnosis' && diagnosis && (
            <div className="flex gap-3">
              <button onClick={onClose} className="btn btn-secondary flex-1">
                Close
              </button>
              {diagnosis.all_mastered ? (
                <button
                  onClick={() => { onClose(); }}
                  className="btn flex-1 bg-emerald-600 hover:bg-emerald-700 text-white shadow-md"
                >
                  <Trophy size={16} /> Try Harder Mode
                </button>
              ) : (
                <button
                  onClick={loadNotes}
                  disabled={loadingNotes}
                  className="btn flex-[2] bg-gradient-to-r from-indigo-600 to-violet-600
                             hover:from-indigo-700 hover:to-violet-700 text-white shadow-lg
                             disabled:opacity-60"
                >
                  {loadingNotes
                    ? <><Loader2 size={16} className="animate-spin" /> Generating Notes…</>
                    : <><BookOpen size={16} /> Generate Study Guide <ChevronRight size={14} /></>
                  }
                </button>
              )}
            </div>
          )}

          {/* Notes Step Footer */}
          {step === 'notes' && notes && (
            <div className="flex gap-3">
              <button onClick={downloadNotesPDF} className="btn btn-secondary flex-shrink-0">
                <Download size={15} /> Save Notes
              </button>
              <button
                onClick={startRemediation}
                disabled={starting}
                className="btn flex-1 bg-gradient-to-r from-rose-500 to-orange-500
                           hover:from-rose-600 hover:to-orange-600 text-white shadow-lg font-bold
                           disabled:opacity-60"
              >
                {starting
                  ? <><Loader2 size={16} className="animate-spin" /> Starting…</>
                  : <><Target size={16} /> Start Focused Retry <ArrowRight size={14} /></>
                }
              </button>
            </div>
          )}

          {step === 'loading' && (
            <button onClick={onClose} className="btn btn-secondary w-full">Cancel</button>
          )}
        </div>
      </div>
    </>
  );
}
