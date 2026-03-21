import { X, CheckCircle, Clock, Link2, Sparkles, QrCode, ExternalLink } from 'lucide-react'
import type { Artifact, TraceLink } from '../../types'

interface MilestoneDetailPanelProps {
  artifact: Artifact
  traceLinks: TraceLink[]
  onClose: () => void
}

const LINK_TYPE_COLORS: Record<string, { border: string; bg: string; text: string }> = {
  experience_source: { border: 'border-teal-500', bg: 'bg-teal-50', text: 'text-teal-700' },
  revision_of: { border: 'border-etest-purple', bg: 'bg-etest-purple-light', text: 'text-etest-purple' },
  mentor_guided: { border: 'border-amber-500', bg: 'bg-etest-amber-bg', text: 'text-amber-700' },
  skill_applied: { border: 'border-etest-blue', bg: 'bg-etest-blue-light', text: 'text-etest-blue' },
}

export default function MilestoneDetailPanel({ artifact, traceLinks, onClose }: MilestoneDetailPanelProps) {
  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-etest-text/20 z-[60] backdrop-blur-sm" onClick={onClose} />

      {/* Side Panel */}
      <div className="fixed top-0 right-0 h-full w-full max-w-xl bg-white z-[70] shadow-2xl border-l-[6px] border-etest-purple flex flex-col overflow-hidden animate-slideDown">
        {/* Header */}
        <div className="px-8 pt-10 pb-6">
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <h2 className="text-2xl font-bold text-etest-text">{artifact.title}</h2>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-sm text-etest-hint font-medium">
                  {new Date(artifact.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-etest-purple-light text-etest-purple border border-etest-purple-border">
                  {artifact.type.replace(/_/g, ' ')}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="h-10 w-10 flex items-center justify-center rounded-full hover:bg-etest-bg-secondary transition-colors text-etest-hint"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {artifact.mentorApproved && (
            <div className="flex items-center gap-2 mt-4 text-etest-green font-semibold text-sm">
              <CheckCircle className="w-4 h-4" />
              <span>Mentor approved</span>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-8 space-y-8 pb-10">
          {/* Scores Row */}
          <section className="flex gap-4">
            {artifact.score !== null && (
              <div className="flex-1 bg-etest-bg-secondary p-4 rounded-xl border border-etest-border/5">
                <p className="text-[10px] font-bold uppercase tracking-wider text-etest-hint mb-1">Score</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-black text-etest-text">{artifact.score}</span>
                  <span className="text-etest-hint text-sm">/ 100</span>
                </div>
              </div>
            )}
            {artifact.authScore !== null && (
              <div className="flex-1 bg-etest-green-bg p-4 rounded-xl border border-etest-green/20">
                <p className="text-[10px] font-bold uppercase tracking-wider text-etest-green mb-1">Authenticity</p>
                <div className="flex items-center gap-2">
                  <span className="text-3xl font-black text-etest-green">{artifact.authScore}%</span>
                  <CheckCircle className="w-5 h-5 text-etest-green" />
                </div>
              </div>
            )}
          </section>

          {/* Leadership Badge */}
          {artifact.leadershipRole && (
            <section className="bg-etest-teal-light border border-etest-teal-border rounded-lg p-3 flex items-center gap-3">
              <div className="w-7 h-7 bg-teal-400 rounded flex items-center justify-center text-white font-black text-xs">L</div>
              <div className="text-xs font-medium text-teal-800">
                <span className="font-bold">Leadership role:</span> {artifact.leadershipRole} · {artifact.leadershipPeople} people · Outcome: {artifact.leadershipOutcome}
              </div>
            </section>
          )}

          {/* AI Summary */}
          <section className="space-y-3">
            <div className="flex items-center gap-2 text-etest-subtext">
              <Sparkles className="w-5 h-5" />
              <h3 className="text-sm font-bold uppercase tracking-widest">AI Summary</h3>
            </div>
            <div className="bg-etest-bg p-5 rounded-2xl border border-etest-border/5 italic text-etest-muted leading-relaxed text-sm">
              "{artifact.aiSummary}"
            </div>
          </section>

          {/* Trace Links */}
          {traceLinks.length > 0 && (
            <section className="space-y-4">
              <div className="flex items-center gap-2 text-etest-subtext">
                <Link2 className="w-5 h-5" />
                <h3 className="text-sm font-bold uppercase tracking-widest">Connected to</h3>
              </div>
              <div className="space-y-3">
                {traceLinks.map(link => {
                  const colors = LINK_TYPE_COLORS[link.linkType] || LINK_TYPE_COLORS.skill_applied
                  const isSource = link.targetArtifactId === artifact.id
                  const connectedTitle = isSource ? link.sourceTitle : link.targetTitle
                  return (
                    <div key={link.id} className={`p-4 bg-white rounded-xl shadow-[0_12px_32px_rgba(187,0,22,0.04)] border-l-4 ${colors.border}`}>
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-sm font-bold text-etest-text">{connectedTitle}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-[10px] ${colors.bg} ${colors.text} px-1.5 py-0.5 rounded font-bold`}>
                              {link.linkType.replace(/_/g, ' ')}
                            </span>
                            <span className="text-[10px] text-etest-hint font-medium">{link.confidence}% match</span>
                          </div>
                        </div>
                        <div className={`text-[10px] font-bold flex items-center gap-1 ${
                          link.status === 'mentor_approved' ? 'text-etest-green' : 'text-amber-600'
                        }`}>
                          {link.status === 'mentor_approved' ? (
                            <><CheckCircle className="w-3 h-3" /> Mentor verified</>
                          ) : (
                            <><Clock className="w-3 h-3" /> ⏳ Awaiting mentor</>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
              {traceLinks.some(l => l.studentNote) && (
                <p className="text-[11px] text-etest-hint italic mt-2">
                  Student note: {traceLinks.find(l => l.studentNote)?.studentNote}
                </p>
              )}
            </section>
          )}

          {/* Writing Consistency */}
          {artifact.authScore !== null && (
            <section className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-etest-text uppercase tracking-widest">Writing consistency</h3>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-etest-green-bg text-etest-green text-[10px] font-bold rounded-full border border-etest-green/20">
                    justified_growth
                  </span>
                  <span className="text-xl font-black text-etest-text">{artifact.authScore}%</span>
                </div>
              </div>
              <div className="h-2 w-full bg-etest-bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-etest-green rounded-full" style={{ width: `${artifact.authScore}%` }} />
              </div>
              <ul className="space-y-2">
                <li className="flex gap-3 text-sm text-etest-muted">
                  <CheckCircle className="w-4 h-4 text-etest-green flex-shrink-0 mt-0.5" />
                  <span>Paragraph structure maintains historical rhythm established in early modules.</span>
                </li>
                <li className="flex gap-3 text-sm text-etest-muted">
                  <CheckCircle className="w-4 h-4 text-etest-green flex-shrink-0 mt-0.5" />
                  <span>Vocabulary density aligns with the student's known lexical fingerprint (+2% variation).</span>
                </li>
              </ul>
            </section>
          )}
        </div>

        {/* Bottom Actions */}
        <div className="p-8 bg-etest-bg-secondary/30 border-t border-etest-border/10 flex gap-4">
          <button className="flex-1 h-12 flex items-center justify-center gap-2 rounded-xl bg-white border border-etest-outline text-etest-text font-bold text-sm hover:bg-etest-bg-secondary transition-all shadow-[0_12px_32px_rgba(187,0,22,0.04)]">
            View artifact <ExternalLink className="w-4 h-4" />
          </button>
          <button className="flex-1 h-12 flex items-center justify-center gap-2 rounded-xl bg-etest-purple text-white font-bold text-sm hover:bg-etest-purple/90 transition-all shadow-lg shadow-etest-purple/20">
            <QrCode className="w-4 h-4" />
            Add to QR
          </button>
        </div>
      </div>
    </>
  )
}
