import { useState, useEffect, useMemo, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import {
  X, Target, BookOpen, Loader2, AlertCircle, CheckCircle,
  TrendingDown, TrendingUp, Minus, Download,
  Sparkles, Brain, RotateCcw, Trophy, ArrowRight, ChevronLeft,
  Zap, Shield, AlertTriangle, Copy, Check, Printer,
  Maximize2, Minimize2, Search, CornerDownRight
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../services/api';

/**
 * RemediationModal — Adaptive Mastery Engine (v3 — Executive UI)
 *
 * Rendered via createPortal(..., document.body) to guarantee complete immunity
 * from parent CSS transforms (e.g. .fade-up) and ensure 100% viewport containment.
 *
 * Features:
 *   - Step 1: Skill Diagnosis with score bands, stat cards, and weak topic analysis
 *   - Step 2: AI Study Guide with high-contrast, card-based section rendering,
 *             language-aware code blocks with instant Copy, responsive tables,
 *             font-size zoom (A- / A+), search-in-notes, and modal width toggle.
 *   - Step 3: Retest initiation with adaptive question selection.
 */
export default function RemediationModal({ sessionId, mode, onClose }) {
  const navigate = useNavigate();

  const [step, setStep] = useState('loading'); // 'loading' | 'diagnosis' | 'notes' | 'error'
  const [diagnosis, setDiagnosis] = useState(null);
  const [notes, setNotes] = useState(null);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');

  // Reader state
  const [isExpanded, setIsExpanded] = useState(false);
  const [fontSizeLevel, setFontSizeLevel] = useState(1); // 0 = compact (14px), 1 = normal (15px), 2 = large (16.5px)
  const [searchQuery, setSearchQuery] = useState('');
  const contentRef = useRef(null);

  // Lock body scroll while modal is mounted
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, []);

  // Fetch initial diagnosis
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
      onClose();
      navigate(`/interview/${res.data.session_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start focused retry session.');
      setStarting(false);
    }
  };

  const downloadNotes = () => {
    if (!notes?.notes_markdown) return;
    const blob = new Blob([notes.notes_markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SmartInterview_StudyNotes_Session_${sessionId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const sourceLabel = mode === 'syllabus'
    ? 'Your Uploaded Syllabus'
    : 'SmartInterview Technical KB (8 Domains)';

  const sourceIcon = mode === 'syllabus' ? '📖' : '🧠';

  const fontSizes = [
    { label: 'Compact', body: 'text-[13.5px] leading-relaxed', code: 'text-xs' },
    { label: 'Default', body: 'text-[15px] leading-relaxed', code: 'text-[13px]' },
    { label: 'Large', body: 'text-[16.5px] leading-loose', code: 'text-sm' },
  ];

  const currentFont = fontSizes[fontSizeLevel] || fontSizes[1];

  // Modal content portaled to document.body
  const modalJSX = (
    <div className="fixed inset-0 z-[9999] flex justify-end">
      {/* ── Dark Backdrop ── */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* ── Slide-Over Panel ── */}
      <div
        className={`relative z-10 w-full flex flex-col bg-white shadow-2xl transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-w-5xl' : 'max-w-3xl'
        }`}
        style={{
          height: '100vh',
          animation: 'slideInDrawer 0.28s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        {/* ── Sticky Header ── */}
        <div className="flex-shrink-0 relative overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border-b border-indigo-900/40 text-white">
          {/* Subtle background glow */}
          <div className="absolute top-0 right-1/4 w-96 h-32 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="px-6 py-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0 shadow-md border border-indigo-400/30">
                {step === 'notes' ? <BookOpen size={20} className="text-white" /> : <Target size={20} className="text-white" />}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-white font-extrabold text-base tracking-tight leading-tight">
                    {step === 'notes' ? 'Adaptive AI Study Guide' : 'Session Skill Diagnosis'}
                  </h2>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Session #{sessionId}
                  </span>
                </div>
                <p className="text-slate-400 text-xs font-medium mt-0.5">
                  {step === 'notes'
                    ? `${sourceIcon} Verified Source: ${sourceLabel}`
                    : 'Targeted Remediation Engine · Personalized Mastery'}
                </p>
              </div>
            </div>

            {/* Header Controls */}
            <div className="flex items-center gap-2 flex-shrink-0">
              {/* Step Pill */}
              {(step === 'diagnosis' || step === 'notes') && (
                <div className="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-medium text-slate-300 mr-2">
                  <span className={`w-2 h-2 rounded-full ${step === 'diagnosis' ? 'bg-amber-400' : 'bg-emerald-400'}`} />
                  Step {step === 'diagnosis' ? '1 of 2: Diagnosis' : '2 of 2: Study Guide'}
                </div>
              )}

              {/* Expand / Narrow Toggle */}
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-8 h-8 rounded-lg bg-slate-800/70 hover:bg-slate-700/80 text-slate-300 hover:text-white flex items-center justify-center transition-colors cursor-pointer border border-slate-700/50"
                title={isExpanded ? 'Standard width' : 'Expand width for wider reading'}
              >
                {isExpanded ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
              </button>

              {/* Close Button */}
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-lg bg-slate-800/70 hover:bg-rose-950/80 hover:text-rose-300 text-slate-300 flex items-center justify-center transition-colors cursor-pointer border border-slate-700/50"
                title="Close modal"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* ── Scrollable Body ── */}
        <div ref={contentRef} className="flex-1 overflow-y-auto bg-slate-50/50">

          {/* LOADING STATE */}
          {step === 'loading' && (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] gap-4 p-8 text-center">
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shadow-sm">
                  <Loader2 size={30} className="animate-spin text-indigo-600" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-indigo-500 rounded-full animate-ping opacity-60" />
              </div>
              <div>
                <h3 className="font-extrabold text-slate-900 text-base">Evaluating Skill Performance…</h3>
                <p className="text-slate-500 text-sm mt-1 max-w-sm">
                  Classifying topics into Weak, Borderline, and Mastered bands based on verified scoring thresholds.
                </p>
              </div>
            </div>
          )}

          {/* ERROR STATE */}
          {step === 'error' && (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] gap-4 p-8 text-center">
              <div className="w-16 h-16 rounded-2xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600 shadow-sm">
                <AlertCircle size={32} />
              </div>
              <div>
                <h3 className="font-extrabold text-slate-900 text-base">Unable to Load Diagnosis</h3>
                <p className="text-slate-500 text-sm mt-1 max-w-sm">{error}</p>
              </div>
              <button onClick={loadDiagnosis} className="btn btn-secondary mt-2">
                <RotateCcw size={14} /> Retry Diagnosis
              </button>
            </div>
          )}

          {/* ── STEP 1: DIAGNOSIS ── */}
          {step === 'diagnosis' && diagnosis && (
            <div className="p-6 md:p-8 space-y-6 max-w-4xl mx-auto">

              {/* All Mastered Banner */}
              {diagnosis.all_mastered && (
                <div className="bg-gradient-to-br from-emerald-50 via-teal-50 to-white border border-emerald-200 rounded-2xl p-6 shadow-sm flex items-start gap-4">
                  <div className="w-12 h-12 bg-emerald-500 text-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                    <Trophy size={24} />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-emerald-950 text-lg">Outstanding Work! All Topics Mastered 🎉</h3>
                    <p className="text-emerald-800 text-sm mt-1 leading-relaxed">
                      You achieved ≥ 75% on every assessed technical topic in this session. No remediation is required.
                      You can move on to a higher difficulty or practice other domain areas.
                    </p>
                  </div>
                </div>
              )}

              {/* 3 Metric Summary Stat Cards */}
              {!diagnosis.all_mastered && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                  <div className="bg-white border border-rose-200/90 rounded-2xl p-4 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-rose-500/5 rounded-bl-full pointer-events-none" />
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold uppercase tracking-wider text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">
                        Weak Area
                      </span>
                      <TrendingDown size={18} className="text-rose-500" />
                    </div>
                    <div className="text-3xl font-black text-rose-600 mt-2.5 leading-none">
                      {diagnosis.weak_topics?.length || 0}
                    </div>
                    <div className="text-xs font-semibold text-slate-700 mt-1">Below 65% Score</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Primary focus for revision</div>
                  </div>

                  <div className="bg-white border border-amber-200/90 rounded-2xl p-4 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-amber-500/5 rounded-bl-full pointer-events-none" />
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                        Borderline
                      </span>
                      <Minus size={18} className="text-amber-500" />
                    </div>
                    <div className="text-3xl font-black text-amber-600 mt-2.5 leading-none">
                      {diagnosis.borderline_topics?.length || 0}
                    </div>
                    <div className="text-xs font-semibold text-slate-700 mt-1">65% – 74% Score</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Reinforce core nuances</div>
                  </div>

                  <div className="bg-white border border-emerald-200/90 rounded-2xl p-4 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-500/5 rounded-bl-full pointer-events-none" />
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                        Mastered
                      </span>
                      <CheckCircle size={18} className="text-emerald-500" />
                    </div>
                    <div className="text-3xl font-black text-emerald-600 mt-2.5 leading-none">
                      {diagnosis.strong_topics?.length || 0}
                    </div>
                    <div className="text-xs font-semibold text-slate-700 mt-1">≥ 75% Score</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Skipped in retry sessions</div>
                  </div>
                </div>
              )}

              {/* Skills Detailed Breakdown */}
              {!diagnosis.all_mastered && (
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-extrabold text-slate-900 text-sm">Detailed Skill Performance</h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Targeted questions will be synthesized exclusively for Weak &amp; Borderline topics.
                      </p>
                    </div>
                    <span className="text-xs font-semibold text-slate-400">
                      {(diagnosis.weak_topics?.length || 0) + (diagnosis.borderline_topics?.length || 0)} areas to study
                    </span>
                  </div>

                  <div className="space-y-3">
                    {/* Weak topics */}
                    {diagnosis.weak_topics?.map((topic) => (
                      <SkillRowCard key={topic.skill} topic={topic} category="weak" />
                    ))}

                    {/* Borderline topics */}
                    {diagnosis.borderline_topics?.map((topic) => (
                      <SkillRowCard key={topic.skill} topic={topic} category="borderline" />
                    ))}

                    {/* Mastered topics */}
                    {diagnosis.strong_topics?.length > 0 && (
                      <div className="pt-2">
                        <div className="flex items-center gap-3 my-2">
                          <div className="h-px flex-1 bg-slate-100" />
                          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                            Mastered Skills (Excluded from Retry)
                          </span>
                          <div className="h-px flex-1 bg-slate-100" />
                        </div>
                        {diagnosis.strong_topics.map((topic) => (
                          <SkillRowCard key={topic.skill} topic={topic} category="strong" />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Knowledge Source Verification Box */}
              {!diagnosis.all_mastered && (
                <div className="bg-indigo-50/70 border border-indigo-200/80 rounded-2xl p-4.5 flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
                    <Brain size={18} />
                  </div>
                  <div>
                    <h4 className="text-xs font-extrabold text-indigo-950 uppercase tracking-wide">
                      Zero Synthetic Hallucinations
                    </h4>
                    <p className="text-xs text-indigo-900/80 mt-1 leading-relaxed">
                      Study notes and retry questions are drawn strictly from <strong>{sourceLabel}</strong>.
                      Explanations follow verified engineering patterns, production edge-cases, and exact interview evaluation criteria.
                    </p>
                  </div>
                </div>
              )}

              {error && <ErrorBanner message={error} />}
            </div>
          )}

          {/* ── STEP 2: AI STUDY GUIDE ── */}
          {step === 'notes' && notes && (
            <div className="p-6 md:p-8 space-y-6 max-w-4xl mx-auto">

              {/* Control Toolbar */}
              <div className="bg-white border border-slate-200 rounded-2xl p-3.5 shadow-sm flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full">
                    <Sparkles size={12} /> AI Study Guide
                  </span>
                  {notes.rag_chunks_found && (
                    <span className="inline-flex items-center gap-1 text-xs text-slate-600 font-semibold px-2.5 py-1 bg-slate-100 rounded-full border border-slate-200">
                      <Zap size={11} className="text-amber-500" />
                      {Object.values(notes.rag_chunks_found).reduce((a, b) => a + b, 0)} Verified Reference Chunks
                    </span>
                  )}
                  {notes.weak_topics?.map(topic => (
                    <span key={topic} className="text-xs font-semibold px-2.5 py-1 bg-rose-50 text-rose-700 border border-rose-200 rounded-full flex items-center gap-1">
                      <Target size={11} /> {topic}
                    </span>
                  ))}
                </div>

                {/* Reader Controls: Font Size & Actions */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200 text-xs font-bold text-slate-600">
                    <button
                      onClick={() => setFontSizeLevel(Math.max(0, fontSizeLevel - 1))}
                      disabled={fontSizeLevel === 0}
                      className="px-2 py-1 rounded hover:bg-white disabled:opacity-40 transition-colors cursor-pointer"
                      title="Smaller font"
                    >
                      A-
                    </button>
                    <span className="px-1 text-[10px] text-slate-400">
                      {fontSizes[fontSizeLevel].label}
                    </span>
                    <button
                      onClick={() => setFontSizeLevel(Math.min(fontSizes.length - 1, fontSizeLevel + 1))}
                      disabled={fontSizeLevel === fontSizes.length - 1}
                      className="px-2 py-1 rounded hover:bg-white disabled:opacity-40 transition-colors cursor-pointer"
                      title="Larger font"
                    >
                      A+
                    </button>
                  </div>

                  <button
                    onClick={downloadNotes}
                    className="btn btn-secondary py-1 px-3 text-xs flex items-center gap-1 shadow-sm"
                    title="Download Markdown file"
                  >
                    <Download size={13} /> .md
                  </button>

                  <button
                    onClick={handlePrint}
                    className="btn btn-secondary py-1 px-2.5 text-xs flex items-center gap-1 shadow-sm"
                    title="Print study notes"
                  >
                    <Printer size={13} />
                  </button>
                </div>
              </div>

              {/* Study Notes Card */}
              <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                <div className="px-6 py-4 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between border-b border-slate-800">
                  <div className="flex items-center gap-2.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-xs font-mono font-semibold tracking-wide text-slate-200">
                      VERIFIED CURRICULUM NOTES · HIGH-YIELD REVISION
                    </span>
                  </div>
                  <span className="text-[11px] text-indigo-300 font-mono">
                    Session {sessionId}
                  </span>
                </div>

                <div className={`p-6 sm:p-8 ${currentFont.body} text-slate-800`}>
                  <NotesMarkdownRenderer
                    markdown={notes.notes_markdown}
                    currentFont={currentFont}
                  />
                </div>
              </div>

              {error && <ErrorBanner message={error} />}
            </div>
          )}
        </div>

        {/* ── Fixed Footer Actions ── */}
        <div className="flex-shrink-0 border-t border-slate-200 bg-white/95 backdrop-blur-md px-6 py-4 shadow-lg z-20">

          {/* STEP 1 FOOTER */}
          {step === 'diagnosis' && diagnosis && (
            <div className="flex items-center justify-between gap-3 max-w-4xl mx-auto">
              <button onClick={onClose} className="btn btn-secondary px-5 cursor-pointer">
                Close
              </button>

              {diagnosis.all_mastered ? (
                <button
                  onClick={onClose}
                  className="btn bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-6 shadow-md flex items-center gap-2 cursor-pointer"
                >
                  <Trophy size={16} /> Return to Results
                </button>
              ) : (
                <button
                  onClick={loadNotes}
                  disabled={loadingNotes}
                  className="btn bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold px-6 py-2.5 shadow-lg flex items-center gap-2.5 cursor-pointer disabled:opacity-60 transition-all"
                >
                  {loadingNotes ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Synthesizing AI Study Guide…</span>
                    </>
                  ) : (
                    <>
                      <BookOpen size={16} />
                      <span>Generate AI Study Guide</span>
                      <ArrowRight size={15} />
                    </>
                  )}
                </button>
              )}
            </div>
          )}

          {/* STEP 2 FOOTER */}
          {step === 'notes' && notes && (
            <div className="flex items-center justify-between gap-3 max-w-4xl mx-auto">
              <button
                onClick={() => setStep('diagnosis')}
                className="btn btn-secondary px-4 flex items-center gap-1.5 cursor-pointer"
              >
                <ChevronLeft size={16} /> Back to Diagnosis
              </button>

              <div className="flex items-center gap-3">
                <button
                  onClick={downloadNotes}
                  className="btn btn-secondary hidden sm:flex items-center gap-1.5 cursor-pointer shadow-sm"
                >
                  <Download size={15} /> Save .md Notes
                </button>

                <button
                  onClick={startRemediation}
                  disabled={starting}
                  className="btn bg-gradient-to-r from-rose-600 via-orange-600 to-amber-600 hover:from-rose-700 hover:to-amber-700 text-white font-extrabold px-6 py-2.5 shadow-xl flex items-center gap-2 cursor-pointer disabled:opacity-60 transition-transform active:scale-[0.98]"
                >
                  {starting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Launching Retest Session…</span>
                    </>
                  ) : (
                    <>
                      <Target size={16} />
                      <span>Start Focused Retest Session</span>
                      <ArrowRight size={15} />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {step === 'loading' && (
            <div className="flex justify-end">
              <button onClick={onClose} className="btn btn-secondary px-5 cursor-pointer">
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideInDrawer {
          from { transform: translateX(100%); opacity: 0; }
          to   { transform: translateX(0);    opacity: 1; }
        }
      `}</style>
    </div>
  );

  return createPortal(modalJSX, document.body);
}

/* ─────────────────────────────────────────────────────────────────
   Skill Breakdown Row Card
───────────────────────────────────────────────────────────────── */
function SkillRowCard({ topic, category }) {
  const configs = {
    weak: {
      bg: 'bg-rose-50/50 border-rose-200/90 hover:border-rose-300',
      dot: 'bg-rose-500',
      badge: 'bg-rose-100 text-rose-700 border-rose-200',
      badgeLabel: 'Needs Work',
      scoreColor: 'text-rose-600',
      barColor: 'bg-rose-500',
      icon: <TrendingDown size={13} />,
    },
    borderline: {
      bg: 'bg-amber-50/50 border-amber-200/90 hover:border-amber-300',
      dot: 'bg-amber-500',
      badge: 'bg-amber-100 text-amber-700 border-amber-200',
      badgeLabel: 'Borderline',
      scoreColor: 'text-amber-600',
      barColor: 'bg-amber-500',
      icon: <Minus size={13} />,
    },
    strong: {
      bg: 'bg-slate-50 border-slate-200 opacity-70 hover:opacity-100',
      dot: 'bg-emerald-500',
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      badgeLabel: 'Mastered',
      scoreColor: 'text-emerald-600',
      barColor: 'bg-emerald-500',
      icon: <CheckCircle size={13} />,
    },
  };

  const c = configs[category] || configs.weak;
  const pct = Math.min(100, Math.round(topic.average_score));

  return (
    <div className={`border rounded-xl p-4 transition-all shadow-xs ${c.bg}`}>
      <div className="flex items-center justify-between gap-4 mb-2.5">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${c.dot}`} />
          <h4 className="font-extrabold text-sm text-slate-900 truncate">{topic.skill}</h4>
          <span className="text-[11px] font-semibold text-slate-400 bg-white px-2 py-0.5 rounded-md border border-slate-200">
            {topic.questions_count} {topic.questions_count === 1 ? 'question' : 'questions'}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 border rounded-full ${c.badge}`}>
            {c.icon} {c.badgeLabel}
          </span>
          <span className={`text-base font-black leading-none ${c.scoreColor}`}>
            {pct}%
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-slate-200/80 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${c.barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Weakness summary if available */}
      {topic.weaknesses?.length > 0 && category !== 'strong' && (
        <div className="mt-2.5 pt-2 border-t border-slate-200/60 flex items-start gap-1.5 text-xs text-slate-600">
          <CornerDownRight size={13} className="text-slate-400 flex-shrink-0 mt-0.5" />
          <span className="truncate">Key gap: {topic.weaknesses[0]}</span>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   Custom Notes Markdown Renderer with Card-based Section Treatment
───────────────────────────────────────────────────────────────── */
function NotesMarkdownRenderer({ markdown, currentFont }) {
  return (
    <div className="space-y-4">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // H2: Topic Main Headers
          h2: ({ children }) => (
            <div className="mt-8 mb-4 pt-4 border-t-2 border-slate-200 first:mt-0 first:pt-0 first:border-t-0">
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-6 rounded-full bg-gradient-to-b from-indigo-600 to-violet-600" />
                <h2 className="text-xl font-black text-slate-900 tracking-tight">
                  {children}
                </h2>
              </div>
            </div>
          ),

          h3: ({ children }) => {
            const rawText = Array.isArray(children) ? children.join('') : String(children || '');
            const isPitfall = rawText.includes('⚠️') || rawText.toLowerCase().includes('lost marks') || rawText.toLowerCase().includes('pitfalls');
            const isCore = rawText.includes('🎯') || rawText.toLowerCase().includes('core concept');
            const isCode = rawText.includes('💻') || rawText.toLowerCase().includes('implementation') || rawText.toLowerCase().includes('example');
            const isTrap = rawText.includes('🔥') || rawText.toLowerCase().includes('trap');
            const isKey = rawText.includes('💡') || rawText.toLowerCase().includes('key points');

            let badgeClass = 'bg-slate-100 text-slate-700 border-slate-200';
            let icon = '📌';
            if (isPitfall) {
              badgeClass = 'bg-rose-50 text-rose-800 border-rose-200';
              icon = '⚠️';
            } else if (isCore) {
              badgeClass = 'bg-indigo-50 text-indigo-800 border-indigo-200';
              icon = '🎯';
            } else if (isCode) {
              badgeClass = 'bg-slate-900 text-slate-100 border-slate-800';
              icon = '💻';
            } else if (isTrap) {
              badgeClass = 'bg-amber-50 text-amber-800 border-amber-200';
              icon = '🔥';
            } else if (isKey) {
              badgeClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
              icon = '💡';
            }

            // Safely strip any leading symbols/emojis using unicode flag to avoid dangling surrogates
            const cleanedText = rawText.replace(/^[^\w\s]+/u, '').trim();

            return (
              <div className={`mt-6 mb-3 px-3.5 py-2.5 rounded-xl border flex items-center gap-2.5 font-extrabold text-sm shadow-xs ${badgeClass}`}>
                <span className="text-base flex-shrink-0">{icon}</span>
                <span>{cleanedText || children}</span>
              </div>
            );
          },

          // Paragraphs
          p: ({ children }) => (
            <p className="my-2.5 leading-relaxed text-slate-700">
              {children}
            </p>
          ),

          // Strong / Bold
          strong: ({ children }) => (
            <strong className="font-extrabold text-slate-900">
              {children}
            </strong>
          ),

          // Emphasis / Italic
          em: ({ children }) => (
            <em className="text-indigo-700 not-italic font-medium bg-indigo-50/60 px-1 py-0.5 rounded">
              {children}
            </em>
          ),

          // Lists
          ul: ({ children }) => (
            <ul className="my-3 space-y-2 list-none pl-1 text-slate-700">
              {children}
            </ul>
          ),

          ol: ({ children }) => (
            <ol className="my-3 space-y-2 list-decimal pl-5 text-slate-700 marker:font-bold marker:text-indigo-600">
              {children}
            </ol>
          ),

          li: ({ children }) => (
            <li className="flex items-start gap-2.5 text-slate-700 leading-relaxed">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2.5 flex-shrink-0" />
              <div className="flex-1">{children}</div>
            </li>
          ),

          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="my-4 pl-4 py-2 border-l-4 border-indigo-500 bg-indigo-50/50 rounded-r-xl text-slate-700 italic">
              {children}
            </blockquote>
          ),

          // Pre & Code Blocks
          pre: ({ children }) => <>{children}</>,

          code: ({ node, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            const codeString = String(children).replace(/\n$/, '');
            const isMultiLine = codeString.includes('\n') || !!match;

            if (isMultiLine) {
              return (
                <CodeBlockCard
                  language={match ? match[1] : 'code'}
                  codeString={codeString}
                  fontClass={currentFont.code}
                />
              );
            }

            // Inline code chip
            return (
              <code className="px-1.5 py-0.5 rounded-md bg-slate-100 text-indigo-700 font-mono text-[0.88em] font-semibold border border-slate-200">
                {children}
              </code>
            );
          },

          // Tables (Common Interview Traps table, etc.)
          table: ({ children }) => (
            <div className="my-5 overflow-x-auto rounded-xl border border-slate-200 shadow-sm bg-white">
              <table className="w-full text-left border-collapse text-xs sm:text-sm">
                {children}
              </table>
            </div>
          ),

          thead: ({ children }) => (
            <thead className="bg-slate-100/90 text-slate-700 border-b border-slate-200">
              {children}
            </thead>
          ),

          th: ({ children }) => (
            <th className="px-4 py-3 font-extrabold uppercase tracking-wider text-[11px] text-slate-700 border-r border-slate-200 last:border-r-0">
              {children}
            </th>
          ),

          tbody: ({ children }) => (
            <tbody className="divide-y divide-slate-100">
              {children}
            </tbody>
          ),

          tr: ({ children }) => (
            <tr className="hover:bg-slate-50/80 transition-colors">
              {children}
            </tr>
          ),

          td: ({ children }) => (
            <td className="px-4 py-3 text-slate-700 align-top leading-relaxed border-r border-slate-100 last:border-r-0 font-normal">
              {children}
            </td>
          ),

          hr: () => (
            <hr className="my-6 border-slate-200" />
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   Interactive Code Block Card with Instant Clipboard Copy
───────────────────────────────────────────────────────────────── */
function CodeBlockCard({ language, codeString, fontClass }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-xl overflow-hidden border border-slate-800 bg-slate-950 shadow-md">
      {/* Code Header Bar */}
      <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-rose-500/70" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
          </div>
          <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-indigo-400 ml-1.5">
            {language || 'PYTHON'}
          </span>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer text-[11px] font-medium border border-slate-700"
          title="Copy code to clipboard"
        >
          {copied ? (
            <>
              <Check size={12} className="text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Copy size={12} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Area */}
      <div className="p-4 overflow-x-auto leading-relaxed text-slate-200 font-mono">
        <pre className={`${fontClass || 'text-xs'} whitespace-pre leading-relaxed`}>
          <code>{codeString}</code>
        </pre>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   Error Banner
───────────────────────────────────────────────────────────────── */
function ErrorBanner({ message }) {
  return (
    <div className="flex items-center gap-2.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl px-4 py-3 text-xs font-semibold">
      <AlertTriangle size={15} className="text-rose-500 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
}
