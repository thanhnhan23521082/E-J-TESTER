import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { MOCK_STUDENT, MOCK_ETESTER, MOCK_MILESTONES, MOCK_TRACE_LINKS, MOCK_ARTIFACTS } from '../../data/mock'
import MilestoneTimeline from '../../components/shared/MilestoneTimeline'
import MentorTraceReview from '../../components/etester/MentorTraceReview'
import MilestoneDetailPanel from '../../components/etester/MilestoneDetailPanel'
import { ArrowUpRight, CheckCircle, Link2, FileText, ExternalLink } from 'lucide-react'
import type { TraceLinkType, Artifact } from '../../types'

type ReviewTab = 'trace_links' | 'artifact_approvals'

const MOCK_STUDENTS = [
  { id: 'student_001', name: 'Minh Anh', initials: 'MA', program: 'AMP Scholar Program', contributions: 23, verified: 18, pendingCount: 2, progress: 82, progressColor: 'text-etest-gold' },
  { id: 'student_002', name: 'Hoàng Việt', initials: 'HV', program: 'Ivy League Intensive', contributions: 15, verified: 12, pendingCount: 0, progress: 44, progressColor: 'text-etest-blue' },
  { id: 'student_003', name: 'Phúc Lâm', initials: 'PL', program: 'Standard Academic Track', contributions: 0, verified: 0, pendingCount: 0, progress: 0, progressColor: 'text-etest-hint' },
  { id: 'student_004', name: 'Thảo Tâm', initials: 'TT', program: 'Portfolio Building', contributions: 0, verified: 0, pendingCount: 0, progress: 0, progressColor: 'text-etest-hint' },
]

export default function MentorEtester() {
  const { studentId } = useParams()
  const [activeTab, setActiveTab] = useState<ReviewTab>('trace_links')
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null)

  const pendingLinks = MOCK_TRACE_LINKS.filter(tl => tl.status === 'pending')
  const pendingArtifacts = MOCK_ARTIFACTS.filter(a => !a.mentorApproved && a.type.includes('essay'))

  const handleApproveLink = (id: string, comment: string, linkType: TraceLinkType) => {
    console.log('Approve link:', id, comment, linkType)
  }

  const handleRejectLink = (id: string) => {
    console.log('Reject link:', id)
  }

  return (
    <div className="space-y-12">
      {/* Pending Reviews Section */}
      <section className="space-y-6">
        <div className="flex items-end gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-etest-text">Needs your review</h1>
          <span className="mb-1.5 px-2.5 py-0.5 rounded-full bg-etest-pink-light text-etest-red font-bold text-xs">
            {pendingLinks.length + pendingArtifacts.length}
          </span>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-8 border-b border-etest-border/10">
          <button
            onClick={() => setActiveTab('trace_links')}
            className={`pb-4 text-sm font-bold flex items-center gap-2 transition-colors ${
              activeTab === 'trace_links'
                ? 'text-etest-red border-b-2 border-etest-red'
                : 'text-etest-subtext hover:text-etest-red'
            }`}
          >
            Trace Links <span className="opacity-60 font-medium">({pendingLinks.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('artifact_approvals')}
            className={`pb-4 text-sm font-medium flex items-center gap-2 transition-colors ${
              activeTab === 'artifact_approvals'
                ? 'text-etest-red border-b-2 border-etest-red'
                : 'text-etest-subtext hover:text-etest-red'
            }`}
          >
            Artifact Approvals <span className="opacity-60 font-medium">({pendingArtifacts.length})</span>
          </button>
        </div>

        {/* Review Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {activeTab === 'trace_links' && pendingLinks.map(link => (
            <div key={link.id} className="lg:col-span-2">
              {/* Trace Link Review Card */}
              <div className="p-6 rounded-2xl bg-white shadow-[0_12px_32px_rgba(187,0,22,0.04)] hover:shadow-md transition-shadow group relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4">
                  <Link2 className="w-5 h-5 text-etest-border/30 group-hover:text-etest-red/20 transition-colors" />
                </div>
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 rounded-full bg-etest-blue-light flex items-center justify-center text-etest-blue font-bold text-lg">
                    MA
                  </div>
                  <div>
                    <h3 className="font-bold text-etest-text">Minh Anh</h3>
                    <p className="text-xs text-etest-subtext">Applied Ivy League Track</p>
                  </div>
                </div>

                <div className="flex items-center justify-between gap-4 p-4 rounded-xl bg-etest-bg-secondary">
                  <div className="flex-1 space-y-1">
                    <p className="text-[10px] uppercase font-bold text-etest-subtext tracking-widest">Source Artifact</p>
                    <p className="text-sm font-semibold">{link.sourceTitle}</p>
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-etest-red flex-shrink-0 rotate-90" />
                  <div className="flex-1 space-y-1 text-right">
                    <p className="text-[10px] uppercase font-bold text-etest-subtext tracking-widest">Target Artifact</p>
                    <p className="text-sm font-semibold">{link.targetTitle}</p>
                  </div>
                </div>

                <div className="mt-6 flex justify-end gap-3">
                  <button
                    onClick={() => handleRejectLink(link.id)}
                    className="px-4 py-2 text-sm font-bold text-etest-subtext hover:bg-etest-surface-container rounded-lg transition-colors"
                  >
                    Dismiss
                  </button>
                  <button
                    onClick={() => handleApproveLink(link.id, '', link.linkType)}
                    className="px-6 py-2 btn-primary text-white text-sm font-bold rounded-lg shadow-lg shadow-etest-red/20 hover:scale-[1.02] active:scale-95 transition-all"
                  >
                    Verify Connection
                  </button>
                </div>
              </div>
            </div>
          ))}

          {activeTab === 'artifact_approvals' && (
            <div className="lg:col-span-3 p-8 rounded-2xl bg-white border-2 border-etest-gold-light/30 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-etest-gold-light/10 rounded-full -mr-16 -mt-16 blur-3xl" />
              <div className="flex flex-col md:flex-row gap-8 items-start">
                <div className="flex-1 space-y-6">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-etest-red text-white flex items-center justify-center font-black text-xl shadow-lg shadow-etest-red/20">
                      MA
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-etest-text">
                        Minh Anh - <span className="text-etest-subtext font-medium">Personal Statement</span>
                      </h3>
                      <p className="text-sm text-etest-subtext">Submitted 4 hours ago · Editorial Review Required</p>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-etest-bg border border-etest-border/10 italic text-etest-subtext text-sm leading-relaxed">
                    "This draft focuses on my journey in traditional Vietnamese music and how it shaped my perspective on cultural preservation..."
                  </div>

                  <div className="flex flex-wrap gap-4">
                    {[
                      { label: 'Auth Score', value: '78%', color: 'text-etest-blue' },
                      { label: 'Word Count', value: '642', color: 'text-etest-text' },
                      { label: 'Status', value: 'Pending', color: 'text-etest-gold' },
                    ].map(stat => (
                      <div key={stat.label} className="px-4 py-3 rounded-xl bg-etest-bg flex flex-col gap-1 min-w-[120px]">
                        <span className="text-[10px] font-bold text-etest-subtext uppercase tracking-tighter">{stat.label}</span>
                        <span className={`text-xl font-black ${stat.color}`}>{stat.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="w-full md:w-80 space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-etest-subtext uppercase ml-1">Mentor Comments</label>
                    <textarea
                      className="w-full rounded-xl border-none bg-etest-bg-secondary focus:ring-2 focus:ring-etest-red/20 text-sm placeholder:text-etest-hint"
                      placeholder="Type your feedback here..."
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <button className="py-3 px-4 rounded-xl border-2 border-etest-border/20 font-bold text-sm text-etest-subtext hover:bg-etest-pink-light hover:text-etest-red hover:border-transparent transition-all">
                      Reject
                    </button>
                    <button className="py-3 px-4 rounded-xl btn-primary text-white font-bold text-sm shadow-xl shadow-etest-red/20 hover:scale-[1.02] active:scale-95 transition-all">
                      Approve
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Students Section */}
      <section className="space-y-6 pb-20">
        <div className="flex items-center justify-between">
          <div className="flex items-end gap-3">
            <h2 className="text-2xl font-extrabold tracking-tight text-etest-text">Your students</h2>
            <span className="mb-1 px-2 py-0.5 rounded-full bg-etest-surface-high text-etest-subtext font-bold text-[10px]">
              {MOCK_STUDENTS.length} TOTAL
            </span>
          </div>
          <button className="text-sm font-bold text-etest-red flex items-center gap-1 hover:underline">
            View all roster <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {MOCK_STUDENTS.map(s => (
            <div
              key={s.id}
              className="p-6 rounded-2xl bg-etest-bg-secondary flex items-center gap-6 relative group border-2 border-transparent hover:border-white hover:bg-white transition-all cursor-pointer"
            >
              {s.pendingCount > 0 && (
                <div className="absolute top-4 right-4 h-3 w-3 rounded-full bg-etest-gold shadow-[0_0_10px_rgba(111,93,33,0.4)]" />
              )}

              {/* Avatar with progress ring */}
              <div className="relative">
                <div className="w-16 h-16 rounded-full bg-etest-surface-highest flex items-center justify-center font-black text-xl text-etest-red border-4 border-white shadow-sm">
                  {s.initials}
                </div>
                {s.progress > 0 && (
                  <svg className="absolute -inset-1 w-[72px] h-[72px] -rotate-90">
                    <circle className="text-etest-surface-high" cx="36" cy="36" r="34" fill="none" stroke="currentColor" strokeWidth="3" />
                    <circle
                      className={s.progressColor}
                      cx="36" cy="36" r="34" fill="none" stroke="currentColor" strokeWidth="3"
                      strokeDasharray="213"
                      strokeDashoffset={213 - (213 * s.progress) / 100}
                    />
                  </svg>
                )}
              </div>

              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-lg">{s.name}</h4>
                  {s.pendingCount > 0 && (
                    <span className="px-1.5 py-0.5 rounded bg-etest-gold-light text-etest-gold text-[9px] font-black uppercase">
                      {s.pendingCount} pending
                    </span>
                  )}
                </div>
                <p className="text-xs text-etest-subtext">{s.program}</p>
                {s.contributions > 0 ? (
                  <div className="flex items-center gap-4 mt-3">
                    <div className="text-[10px]">
                      <span className="font-bold text-etest-text">{s.contributions}</span> contributions
                    </div>
                    <div className="text-[10px]">
                      <span className="font-bold text-etest-blue">{s.verified}</span> verified
                    </div>
                  </div>
                ) : (
                  <div className="text-[10px] text-etest-subtext mt-3">
                    {s.name === 'Thảo Tâm' ? 'Last contribution: Yesterday' : 'No new activity'}
                  </div>
                )}
              </div>

              <div className="h-10 w-10 rounded-full bg-etest-surface-container flex items-center justify-center text-etest-red group-hover:bg-etest-red group-hover:text-white transition-all">
                <ArrowUpRight className="w-5 h-5" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Milestone Detail Panel */}
      {selectedArtifact && (
        <MilestoneDetailPanel
          artifact={selectedArtifact}
          traceLinks={MOCK_TRACE_LINKS.filter(
            tl => tl.sourceArtifactId === selectedArtifact.id || tl.targetArtifactId === selectedArtifact.id
          )}
          onClose={() => setSelectedArtifact(null)}
        />
      )}
    </div>
  )
}
