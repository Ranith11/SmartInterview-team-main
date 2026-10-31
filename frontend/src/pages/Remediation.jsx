import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft, ArrowRight, Target, BookOpen, BarChart3, Download,
  Printer, Loader2, AlertCircle, CheckCircle, TrendingDown,
  Minus, Sparkles, Brain, Trophy, Zap, Shield, AlertTriangle,
  Copy, Check, CornerDownRight, RotateCcw
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../services/api';

/**
 * Remediation Page — Dedicated Adaptive Mastery & Study Workspace
 *
 * Full-page experience with tabs:
 *   - Tab 1: 📖 AI Study Guide (High-yield notes, code with copy, traps table)
 *   - Tab 2: 📊 Skill Diagnosis (Metric cards, gap analysis, score bars)
 */
export default function Remediation() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('notes'); // 'notes' | 'diagnosis'
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [notes, setNotes] = useState(null);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [starting, setStarting] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState('');

  // Reader state
  const [fontSizeLevel, setFontSizeLevel] = useState(1); // 0 = Compact, 1 = Default, 2 = Large

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      // 1. Fetch diagnosis and results in parallel
      const [diagRes, resultsRes] = await Promise.all([
        api.get(`/interviews/${id}/remediation/diagnosis`),
        api.get(`/interviews/${id}/results`),
      ]);

      setDiagnosis(diagRes.data);
      setSession(resultsRes.data.session);

      // 2. Fetch or generate notes if there are weak/borderline topics
      if (!diagRes.data.all_mastered) {
        setLoadingNotes(true);
        try {
          const notesRes = await api.get(`/interviews/${id}/remediation/notes`);
          setNotes(notesRes.data);
        } catch (notesErr) {
          console.error('Failed to load notes:', notesErr);
        } finally {
          setLoadingNotes(false);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load remediation workspace data.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNotes = async () => {
    setLoadingNotes(true);
    setError('');
    try {
      const res = await api.get(`/interviews/${id}/remediation/notes`);
      setNotes(res.data);
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
      const res = await api.post(`/interviews/${id}/remediation/start`);
      navigate(`/interview/${res.data.session_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start focused retest session.');
      setStarting(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const response = await api.get(`/interviews/${id}/remediation/notes/pdf`, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SmartInterview_StudyNotes_Session_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF study notes:', err);
      alert('Failed to generate PDF study notes. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const fontSizes = [
    { label: 'Compact', body: 'text-[14px] leading-relaxed', code: 'text-xs' },
    { label: 'Default', body: 'text-[15.5px] leading-relaxed', code: 'text-[13px]' },
    { label: 'Large', body: 'text-[17px] leading-loose', code: 'text-sm' },
  ];

  const currentFont = fontSizes[fontSizeLevel] || fontSizes[1];

  const sourceLabel = session?.mode === 'syllabus'
    ? 'Your Uploaded Syllabus'
    : 'SmartInterview Technical KB (8 Domains)';

  const sourceIcon = session?.mode === 'syllabus' ? '📖' : '🧠';

  if (loading) {
    return (
      <div className="page-container max-w-5xl py-16 flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shadow-sm">
            <Loader2 size={32} className="animate-spin text-indigo-600" />
          </div>
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-indigo-500 rounded-full animate-ping opacity-60" />
        </div>
        <div className="text-center">
          <h2 className="text-lg font-black text-slate-900">Loading Remedial Workspace…</h2>
          <p className="text-slate-500 text-sm mt-1 max-w-sm">
            Analyzing session #{id} evaluations and preparing personalized study material.
          </p>
        </div>
      </div>
    );
  }

  if (error && !diagnosis) {
    return (
      <div className="page-container max-w-lg py-16">
        <div className="card p-8 text-center bg-white border-slate-200 shadow-sm">
          <div className="w-14 h-14 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-rose-100">
            <AlertCircle size={28} />
          </div>
          <h2 className="text-xl font-black text-slate-900 mb-2">Error Loading Remediation</h2>
          <p className="text-slate-500 text-sm mb-6 leading-relaxed">{error}</p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => navigate(`/results/${id}`)} className="btn btn-secondary">
              Back to Results
            </button>
            <button onClick={loadData} className="btn btn-primary">
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container max-w-6xl py-8 space-y-8">

      {/* ── Top Header Navigation ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <button
            onClick={() => navigate(`/results/${id}`)}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-indigo-600 mb-2 transition-colors cursor-pointer uppercase tracking-wider bg-transparent border-none p-0"
          >
            <ArrowLeft size={14} /> Back to Session #{id} Results
          </button>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Adaptive Mastery &amp; Study Guide
            </h1>
            <span className="text-xs font-extrabold uppercase tracking-wider px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              Session #{id}
            </span>
            {session?.difficulty && (
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                {session.difficulty}
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Targeted AI curriculum synthesis based on verified evaluation gaps. Master your weak areas and retry.
          </p>
        </div>

        {/* Header Quick Actions */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {notes && (
            <>
              <button
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="btn btn-secondary text-xs py-2 px-3.5 flex items-center gap-1.5 shadow-xs font-semibold cursor-pointer disabled:opacity-60"
                title="Download Study Notes as PDF"
              >
                {downloadingPdf ? (
                  <>
                    <Loader2 size={14} className="animate-spin text-indigo-600" />
                    <span>Generating PDF…</span>
                  </>
                ) : (
                  <>
                    <Download size={14} className="text-indigo-600" />
                    <span>Download PDF</span>
                  </>
                )}
              </button>
              <button
                onClick={handlePrint}
                className="btn btn-secondary text-xs py-2 px-3 flex items-center gap-1.5 shadow-xs"
                title="Print study notes"
              >
                <Printer size={14} /> Print
              </button>
            </>
          )}

          {!diagnosis?.all_mastered && (
            <button
              onClick={startRemediation}
              disabled={starting}
              className="btn text-xs sm:text-sm font-bold text-white px-5 py-2.5 flex items-center gap-2 shadow-md hover:shadow-lg active:scale-[0.98] transition-all cursor-pointer disabled:opacity-60"
              style={{ background: 'linear-gradient(135deg, #e11d48, #ea580c)' }}
            >
              {starting ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Launching Retest…</span>
                </>
              ) : (
                <>
                  <Target size={16} />
                  <span>Start Focused Retest</span>
                  <ArrowRight size={14} />
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* ── All Mastered State ── */}
      {diagnosis?.all_mastered && (
        <div className="bg-gradient-to-br from-emerald-50 via-teal-50 to-white border border-emerald-200 rounded-3xl p-8 shadow-sm flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
          <div className="w-16 h-16 bg-emerald-500 text-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
            <Trophy size={32} />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-black text-emerald-950">Outstanding! All Topics Mastered 🎉</h2>
            <p className="text-emerald-800 text-sm mt-1.5 leading-relaxed max-w-2xl">
              You scored ≥ 75% across every assessed skill in this interview session. There are no weak topics requiring remediation.
              Challenge yourself with a higher difficulty level or practice another technical domain.
            </p>
          </div>
          <Link to="/setup" className="btn btn-primary px-6 whitespace-nowrap shadow-md">
            New Interview
          </Link>
        </div>
      )}

      {/* ── Main Workspace Tabs ── */}
      {!diagnosis?.all_mastered && (
        <div className="space-y-6">

          {/* Navigation Pill Bar */}
          <div className="flex items-center justify-between gap-4 border-b border-slate-200 pb-3 flex-wrap">
            <div className="flex items-center gap-2 p-1 bg-slate-100/90 rounded-2xl border border-slate-200/80">
              <button
                onClick={() => setActiveTab('notes')}
                className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                  activeTab === 'notes'
                    ? 'bg-white text-indigo-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <BookOpen size={16} />
                <span>AI Study Guide &amp; Notes</span>
                {notes && (
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                )}
              </button>

              <button
                onClick={() => setActiveTab('diagnosis')}
                className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                  activeTab === 'diagnosis'
                    ? 'bg-white text-indigo-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <BarChart3 size={16} />
                <span>Skill Diagnosis Breakdown</span>
                {diagnosis?.weak_topics?.length > 0 && (
                  <span className="text-[10px] font-black px-1.5 py-0.5 rounded-full bg-rose-100 text-rose-700 border border-rose-200">
                    {diagnosis.weak_topics.length} Weak
                  </span>
                )}
              </button>
            </div>

            {/* Reading Mode font-size toolbar (only shown on notes tab) */}
            {activeTab === 'notes' && notes && (
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-400 hidden sm:inline">Text Size:</span>
                <div className="flex items-center bg-white rounded-xl p-0.5 border border-slate-200 text-xs font-bold text-slate-600 shadow-xs">
                  <button
                    onClick={() => setFontSizeLevel(Math.max(0, fontSizeLevel - 1))}
                    disabled={fontSizeLevel === 0}
                    className="px-2.5 py-1 rounded-lg hover:bg-slate-100 disabled:opacity-40 transition-colors cursor-pointer"
                    title="Smaller font"
                  >
                    A-
                  </button>
                  <span className="px-2 text-[11px] text-slate-500 font-medium border-x border-slate-100">
                    {fontSizes[fontSizeLevel].label}
                  </span>
                  <button
                    onClick={() => setFontSizeLevel(Math.min(fontSizes.length - 1, fontSizeLevel + 1))}
                    disabled={fontSizeLevel === fontSizes.length - 1}
                    className="px-2.5 py-1 rounded-lg hover:bg-slate-100 disabled:opacity-40 transition-colors cursor-pointer"
                    title="Larger font"
                  >
                    A+
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* ══════════════════════════════════════════════════════════
              TAB 1: AI STUDY GUIDE & NOTES
          ══════════════════════════════════════════════════════════ */}
          {activeTab === 'notes' && (
            <div className="space-y-6">

              {/* Status & Metadata Bar */}
              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full">
                    <Sparkles size={12} /> Mode: High-Yield Revision
                  </span>

                  <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 bg-slate-100 text-slate-700 border border-slate-200 rounded-full">
                    {sourceIcon} {sourceLabel}
                  </span>

                  {notes?.rag_chunks_found && (
                    <span className="inline-flex items-center gap-1 text-xs text-slate-600 font-semibold px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-full">
                      <Zap size={11} className="text-amber-500" />
                      {Object.values(notes.rag_chunks_found).reduce((a, b) => a + b, 0)} Verified Knowledge Chunks
                    </span>
                  )}
                </div>

                {/* Target Topics chips */}
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-xs text-slate-400 font-medium">Target Topics:</span>
                  {diagnosis?.weak_topics?.map(t => (
                    <span key={t.skill} className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1">
                      <Target size={11} /> {t.skill} ({Math.round(t.average_score)}%)
                    </span>
                  ))}
                </div>
              </div>

              {/* Loading State for Notes */}
              {loadingNotes && (
                <div className="card p-16 text-center bg-white border-slate-200 shadow-sm flex flex-col items-center justify-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shadow-xs">
                    <Loader2 size={28} className="animate-spin text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="text-base font-extrabold text-slate-900">Synthesizing Verified Study Notes…</h3>
                    <p className="text-slate-500 text-xs sm:text-sm mt-1 max-w-md mx-auto leading-relaxed">
                      Querying knowledge base for core concepts, candidate misconceptions, and code implementations tailored to your score gaps.
                    </p>
                  </div>
                </div>
              )}

              {/* Empty / Error state for notes */}
              {!loadingNotes && !notes && (
                <div className="card p-12 text-center bg-white border-slate-200 shadow-sm space-y-4">
                  <div className="w-12 h-12 bg-amber-50 text-amber-600 rounded-2xl flex items-center justify-center mx-auto border border-amber-100">
                    <BookOpen size={24} />
                  </div>
                  <h3 className="text-base font-extrabold text-slate-900">Study Notes Not Yet Generated</h3>
                  <p className="text-sm text-slate-500 max-w-md mx-auto">
                    Click below to generate high-yield AI revision notes based on the questions you answered in this session.
                  </p>
                  <button onClick={handleGenerateNotes} className="btn btn-primary px-6 shadow-sm">
                    <Sparkles size={15} /> Generate Study Guide Now
                  </button>
                </div>
              )}

              {/* Rendered Notes Card */}
              {!loadingNotes && notes && (
                <div className="bg-white border border-slate-200/90 rounded-3xl shadow-sm overflow-hidden">
                  {/* Top Bar */}
                  <div className="px-6 py-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between border-b border-slate-800">
                    <div className="flex items-center gap-3">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="text-xs font-mono font-bold tracking-wider text-slate-200">
                        VERIFIED CURRICULUM NOTES · HIGH-YIELD REVISION
                      </span>
                    </div>
                    <span className="text-xs text-indigo-300 font-mono">
                      Session #{id}
                    </span>
                  </div>

                  {/* Main Markdown Body */}
                  <div className={`p-6 sm:p-10 ${currentFont.body} text-slate-800`}>
                    <FullNotesRenderer
                      markdown={notes.notes_markdown}
                      currentFont={currentFont}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════
              TAB 2: SKILL DIAGNOSIS BREAKDOWN
          ══════════════════════════════════════════════════════════ */}
          {activeTab === 'diagnosis' && (
            <div className="space-y-6">

              {/* 3 Summary Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white border border-rose-200 rounded-3xl p-6 shadow-xs relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-bl-full pointer-events-none" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-rose-700 bg-rose-50 border border-rose-200 px-3 py-1 rounded-full">
                      Weak Area
                    </span>
                    <TrendingDown size={20} className="text-rose-500" />
                  </div>
                  <div className="text-4xl font-black text-rose-600 mt-4 leading-none">
                    {diagnosis?.weak_topics?.length || 0}
                  </div>
                  <div className="text-sm font-bold text-slate-800 mt-2">Below 65% Score</div>
                  <div className="text-xs text-slate-400 mt-0.5">Prioritized for focused practice</div>
                </div>

                <div className="bg-white border border-amber-200 rounded-3xl p-6 shadow-xs relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-bl-full pointer-events-none" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full">
                      Borderline
                    </span>
                    <Minus size={20} className="text-amber-500" />
                  </div>
                  <div className="text-4xl font-black text-amber-600 mt-4 leading-none">
                    {diagnosis?.borderline_topics?.length || 0}
                  </div>
                  <div className="text-sm font-bold text-slate-800 mt-2">65% – 74% Score</div>
                  <div className="text-xs text-slate-400 mt-0.5">Reinforce core nuances</div>
                </div>

                <div className="bg-white border border-emerald-200 rounded-3xl p-6 shadow-xs relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full pointer-events-none" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
                      Mastered
                    </span>
                    <CheckCircle size={20} className="text-emerald-500" />
                  </div>
                  <div className="text-4xl font-black text-emerald-600 mt-4 leading-none">
                    {diagnosis?.strong_topics?.length || 0}
                  </div>
                  <div className="text-sm font-bold text-slate-800 mt-2">≥ 75% Score</div>
                  <div className="text-xs text-slate-400 mt-0.5">Excluded from retest sessions</div>
                </div>
              </div>

              {/* Skill Rows Breakdown */}
              <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">Per-Skill Evaluation Breakdown</h3>
                  <p className="text-xs sm:text-sm text-slate-500 mt-1">
                    Scores calculated from technical correctness, answer completeness, and rubric relevance in this session.
                  </p>
                </div>

                <div className="space-y-3.5">
                  {/* Weak topics */}
                  {diagnosis?.weak_topics?.map(topic => (
                    <FullSkillCard key={topic.skill} topic={topic} category="weak" />
                  ))}

                  {/* Borderline topics */}
                  {diagnosis?.borderline_topics?.map(topic => (
                    <FullSkillCard key={topic.skill} topic={topic} category="borderline" />
                  ))}

                  {/* Strong topics */}
                  {diagnosis?.strong_topics?.length > 0 && (
                    <div className="pt-4">
                      <div className="flex items-center gap-3 my-3">
                        <div className="h-px flex-1 bg-slate-100" />
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          Mastered Skills (Skipped in Retest)
                        </span>
                        <div className="h-px flex-1 bg-slate-100" />
                      </div>
                      {diagnosis.strong_topics.map(topic => (
                        <FullSkillCard key={topic.skill} topic={topic} category="strong" />
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Zero Hallucinations Guarantee Card */}
              <div className="bg-gradient-to-br from-indigo-50/80 via-white to-violet-50/60 border border-indigo-200 rounded-3xl p-6 shadow-xs flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                  <Brain size={22} />
                </div>
                <div>
                  <h4 className="text-sm font-extrabold text-indigo-950 uppercase tracking-wider">
                    Verified Technical Foundation
                  </h4>
                  <p className="text-xs sm:text-sm text-indigo-900/80 mt-1.5 leading-relaxed">
                    Study notes and retry questions are drawn strictly from <strong>{sourceLabel}</strong>.
                    Zero hallucinated questions or out-of-scope theory. The system pinpoints exactly where marks were deducted
                    and supplies production-grade answers to help you ace your retest.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════
              BOTTOM ACTION BANNER (LAUNCH RETEST)
          ══════════════════════════════════════════════════════════ */}
          <div className="rounded-3xl border border-rose-200 overflow-hidden shadow-md"
            style={{ background: 'linear-gradient(135deg, #fff1f2, #fff7ed)' }}>
            <div className="h-1.5 bg-gradient-to-r from-rose-500 via-orange-500 to-amber-500" />
            <div className="p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-4 text-center md:text-left">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-rose-500 to-orange-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                  <Target size={28} />
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-900">
                    Ready to Prove Your Mastery?
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-xl leading-relaxed">
                    Start a focused retest session consisting of 5 questions targeting only your weak topics ({diagnosis?.weak_topics?.map(t => t.skill).join(', ')}).
                    Your previously mastered scores are preserved.
                  </p>
                </div>
              </div>

              <button
                onClick={startRemediation}
                disabled={starting}
                className="btn text-sm font-extrabold text-white px-8 py-3.5 shadow-xl hover:shadow-2xl hover:brightness-105 active:scale-[0.98] transition-all cursor-pointer whitespace-nowrap flex items-center gap-2.5 flex-shrink-0"
                style={{ background: 'linear-gradient(135deg, #e11d48, #ea580c)' }}
              >
                {starting ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    <span>Launching Retest Session…</span>
                  </>
                ) : (
                  <>
                    <Target size={18} />
                    <span>Launch Focused Retest Now</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   Full Page Skill Card
───────────────────────────────────────────────────────────────── */
function FullSkillCard({ topic, category }) {
  const configs = {
    weak: {
      bg: 'bg-rose-50/40 border-rose-200/90',
      dot: 'bg-rose-500',
      badge: 'bg-rose-100 text-rose-700 border-rose-200',
      badgeLabel: 'Needs Work',
      scoreColor: 'text-rose-600',
      barColor: 'bg-rose-500',
      icon: <TrendingDown size={13} />,
    },
    borderline: {
      bg: 'bg-amber-50/40 border-amber-200/90',
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
    <div className={`border rounded-2xl p-5 transition-all shadow-xs ${c.bg}`}>
      <div className="flex items-center justify-between gap-4 mb-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className={`w-3 h-3 rounded-full flex-shrink-0 ${c.dot}`} />
          <h4 className="font-extrabold text-base text-slate-900 truncate">{topic.skill}</h4>
          <span className="text-xs font-semibold text-slate-500 bg-white px-2.5 py-0.5 rounded-lg border border-slate-200">
            {topic.questions_count} {topic.questions_count === 1 ? 'question' : 'questions'}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <span className={`inline-flex items-center gap-1 text-xs font-bold px-3 py-1 border rounded-full ${c.badge}`}>
            {c.icon} {c.badgeLabel}
          </span>
          <span className={`text-xl font-black leading-none ${c.scoreColor}`}>
            {pct}%
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-2.5 bg-slate-200/80 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${c.barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Weakness summary if available */}
      {topic.weaknesses?.length > 0 && category !== 'strong' && (
        <div className="mt-3 pt-3 border-t border-slate-200/60 flex items-start gap-2 text-xs text-slate-600">
          <CornerDownRight size={14} className="text-slate-400 flex-shrink-0 mt-0.5" />
          <span><strong>Diagnosed gap:</strong> {topic.weaknesses[0]}</span>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   Full Page Notes Markdown Renderer
───────────────────────────────────────────────────────────────── */
function FullNotesRenderer({ markdown, currentFont }) {
  return (
    <div className="space-y-4">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // H2: Topic Main Headers
          h2: ({ children }) => (
            <div className="mt-10 mb-4 pt-6 border-t-2 border-slate-200 first:mt-0 first:pt-0 first:border-t-0">
              <div className="flex items-center gap-3">
                <div className="w-3 h-7 rounded-full bg-gradient-to-b from-indigo-600 to-violet-600" />
                <h2 className="text-2xl font-black text-slate-900 tracking-tight">
                  {children}
                </h2>
              </div>
            </div>
          ),

          // H3: Section Cards & Banners (Core Concept, Traps, etc.)
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
              <div className={`mt-8 mb-3 px-4 py-3 rounded-2xl border flex items-center gap-3 font-extrabold text-sm sm:text-base shadow-xs ${badgeClass}`}>
                <span className="text-lg flex-shrink-0">{icon}</span>
                <span>{cleanedText || children}</span>
              </div>
            );
          },

          // Paragraphs
          p: ({ children }) => (
            <p className="my-3 leading-relaxed text-slate-700">
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
            <em className="text-indigo-700 not-italic font-medium bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100">
              {children}
            </em>
          ),

          // Lists
          ul: ({ children }) => (
            <ul className="my-4 space-y-2.5 list-none pl-1 text-slate-700">
              {children}
            </ul>
          ),

          ol: ({ children }) => (
            <ol className="my-4 space-y-2.5 list-decimal pl-6 text-slate-700 marker:font-bold marker:text-indigo-600">
              {children}
            </ol>
          ),

          li: ({ children }) => (
            <li className="flex items-start gap-3 text-slate-700 leading-relaxed">
              <span className="w-2 h-2 rounded-full bg-indigo-500 mt-2.5 flex-shrink-0" />
              <div className="flex-1">{children}</div>
            </li>
          ),

          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="my-5 pl-5 py-3 border-l-4 border-indigo-500 bg-indigo-50/60 rounded-r-2xl text-slate-700 italic">
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
                <FullCodeBlock
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

          // Tables
          table: ({ children }) => (
            <div className="my-6 overflow-x-auto rounded-2xl border border-slate-200 shadow-xs bg-white">
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
            <th className="px-5 py-3.5 font-extrabold uppercase tracking-wider text-xs text-slate-700 border-r border-slate-200 last:border-r-0">
              {children}
            </th>
          ),

          tbody: ({ children }) => (
            <tbody className="divide-y divide-slate-100">
              {children}
            </tbody>
          ),

          tr: ({ children }) => (
            <tr className="hover:bg-slate-50/90 transition-colors">
              {children}
            </tr>
          ),

          td: ({ children }) => (
            <td className="px-5 py-3.5 text-slate-700 align-top leading-relaxed border-r border-slate-100 last:border-r-0">
              {children}
            </td>
          ),

          hr: () => (
            <hr className="my-8 border-slate-200" />
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   Full Code Block with Clipboard Copy
───────────────────────────────────────────────────────────────── */
function FullCodeBlock({ language, codeString, fontClass }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-5 rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-md">
      {/* Code Header Bar */}
      <div className="px-5 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-rose-500/70" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
          </div>
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-indigo-400 ml-1.5">
            {language || 'PYTHON'}
          </span>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer text-xs font-medium border border-slate-700"
          title="Copy code to clipboard"
        >
          {copied ? (
            <>
              <Check size={13} className="text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Copy size={13} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Area */}
      <div className="p-5 overflow-x-auto leading-relaxed text-slate-200 font-mono">
        <pre className={`${fontClass || 'text-xs sm:text-sm'} whitespace-pre leading-relaxed`}>
          <code>{codeString}</code>
        </pre>
      </div>
    </div>
  );
}
