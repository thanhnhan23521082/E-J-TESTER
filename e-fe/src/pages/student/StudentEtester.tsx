import { useState } from 'react'
import { MOCK_STUDENT, MOCK_ETESTER, MOCK_MILESTONES, MOCK_TRACE_LINKS } from '../../data/mock'
import ContributorDonut from '../../components/shared/ContributorDonut'
import NarrativeCard from '../../components/etester/NarrativeCard'
import MiniArtifactGraph from '../../components/etester/MiniArtifactGraph'
import { Link } from 'react-router-dom'
import {
  Share2,
  Download,
  X,
  AlertCircle,
  ExternalLink,
  CheckCircle,
  ArrowRight,
} from 'lucide-react'

type TimelineFilter = 'all' | 'essay' | 'academic' | 'activities' | 'verified'

export default function StudentEtester() {
  const student = MOCK_STUDENT
  const etester = MOCK_ETESTER
  const traceLinks = MOCK_TRACE_LINKS
  const milestones = MOCK_MILESTONES
  const [activeFilter, setActiveFilter] = useState<TimelineFilter>('all')
  const [showMentorBanner, setShowMentorBanner] = useState(true)

  const pendingLinks = traceLinks.filter(tl => tl.status === 'pending').length

  const filters: { key: TimelineFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'essay', label: 'Essay' },
    { key: 'academic', label: 'Academic' },
    { key: 'activities', label: 'Activities' },
    { key: 'verified', label: 'Verified' },
  ]

  const filteredMilestones = milestones.filter(m => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'essay') return m.type === 'essay_draft' || m.type === 'essay_review'
    if (activeFilter === 'academic') return m.type === 'mock_test'
    if (activeFilter === 'activities') return m.type === 'camp' || m.type === 'csr' || m.type === 'other'
    if (activeFilter === 'verified') return m.mentorApproved
    return true
  })

  return (
    <div className="space-y-10">
      {/* Hero Profile Header */}
      <section className="bg-white rounded-3xl overflow-hidden relative">
        <div className="absolute right-0 -top-24 w-96 h-96 bg-etest-red/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative flex items-center gap-6 p-8">
          <div className="relative flex-shrink-0">
            <div className="w-14 h-14 rounded-2xl bg-etest-red flex items-center justify-center shadow-lg">
              <span className="text-white font-black text-lg">E</span>
            </div>
            {etester.badgeIssued && (
              <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-etest-green border-2 border-white flex items-center justify-center">
                <CheckCircle className="w-3 h-3 text-white" />
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-etest-text truncate">{student.name}</h1>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-etest-green-bg text-etest-green text-[10px] font-bold rounded-full border border-etest-green/20">
                ETEST Verified Learner
              </span>
            </div>
            <p className="text-sm text-etest-subtext mt-0.5">
              {student.monthsEnrolled} months · {student.program}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-etest-subtext bg-etest-bg-secondary rounded-xl hover:bg-etest-surface-container transition-colors">
              <Share2 className="w-4 h-4" /> Share
            </button>
            <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-bold text-white btn-primary rounded-xl shadow-button hover:opacity-90 transition-opacity">
              <Download className="w-4 h-4" /> Download QR
            </button>
          </div>
        </div>
      </section>

      {/* Mentor Review Banner */}
      {showMentorBanner && pendingLinks > 0 && (
        <div className="flex items-center justify-between px-5 py-3 bg-etest-gold-light/60 rounded-2xl">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-etest-gold" />
            <p className="text-sm font-medium text-etest-gold-dark">
              Your mentor has {pendingLinks} connections to review
            </p>
          </div>
          <button onClick={() => setShowMentorBanner(false)}>
            <X className="w-4 h-4 text-etest-gold-dark/50" />
          </button>
        </div>
      )}

      {/* Stats Row */}
      <section className="grid grid-cols-4 gap-5">
        {[
          { label: 'Total Progress', value: etester.totalContributions.toString(), sub: 'Contributions', color: 'text-etest-red' },
          { label: 'Validation', value: etester.mentorVerifications.toString(), sub: 'Mentor verified', color: 'text-etest-blue' },
          { label: 'Reliability', value: `${etester.consistencyScore}%`, sub: 'Authenticity', color: 'text-etest-green' },
          { label: 'Duration', value: student.monthsEnrolled.toString(), sub: 'Months active', color: 'text-etest-text' },
        ].map(stat => (
          <div key={stat.label} className="bg-white rounded-2xl p-5">
            <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest mb-1">{stat.label}</p>
            <p className={`text-3xl font-black ${stat.color}`}>{stat.value}</p>
            <p className="text-xs text-etest-subtext mt-0.5">{stat.sub}</p>
          </div>
        ))}
      </section>

      {/* Contributor Breakdown + Narrative */}
      <section className="grid grid-cols-12 gap-6">
        <div className="col-span-5 bg-white rounded-3xl p-8">
          <h3 className="font-bold text-etest-text mb-6">Contributor Breakdown</h3>
          <div className="flex justify-center mb-4">
            <ContributorDonut
              data={[
                { name: 'Student (45%)', value: etester.totalContributions - etester.mentorVerifications, color: '#3B82F6' },
                { name: 'Mentor (25%)', value: etester.mentorVerifications, color: '#0D9488' },
                { name: 'Parent (10%)', value: 2, color: '#F59E0B' },
                ...(etester.institutionalStamp ? [{ name: 'Institution (20%)', value: 4, color: '#7C3AED' }] : []),
              ]}
            />
          </div>
          <div className="space-y-2 mt-4">
            {[
              { name: 'Student (45%)', color: 'bg-blue-500' },
              { name: 'Mentor (25%)', color: 'bg-etest-teal' },
              { name: 'Parent (10%)', color: 'bg-amber-500' },
              { name: 'Institution (20%)', color: 'bg-etest-purple' },
            ].map(item => (
              <div key={item.name} className="flex items-center gap-2 text-sm">
                <div className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                <span className="text-etest-subtext">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="col-span-7">
          <NarrativeCard
            narrative={etester.narrativeCache}
            studentName={student.name.split(' ').pop()}
            onRefresh={() => {}}
          />
        </div>
      </section>

      {/* Learning Graph */}
      <section className="space-y-3">
        <MiniArtifactGraph />
        <div className="flex justify-end px-2">
          <Link
            to="/student/etester/graph"
            className="inline-flex items-center gap-2 text-sm font-semibold text-etest-blue hover:text-etest-blue-dark transition-colors"
          >
            View full graph <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Milestone Timeline */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-etest-text">Milestone Timeline</h2>
          <div className="flex gap-2">
            {filters.map(f => (
              <button
                key={f.key}
                onClick={() => setActiveFilter(f.key)}
                className={`px-4 py-1.5 text-sm font-semibold rounded-lg transition-all ${
                  activeFilter === f.key
                    ? 'text-etest-red bg-etest-red-light'
                    : 'text-etest-hint hover:text-etest-text hover:bg-etest-bg-secondary'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        <div className="relative space-y-0">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-etest-border/20" />

          {filteredMilestones.slice(0, 5).map((milestone) => {
            const relatedLinks = traceLinks.filter(tl => tl.targetTitle === milestone.title || tl.sourceTitle === milestone.title)
            const dotColor = milestone.mentorApproved ? 'bg-etest-red' : 'bg-etest-blue'

            return (
              <div key={milestone.id} className="relative pl-12 pb-8 group">
                <div className={`absolute left-[11px] top-2 w-3 h-3 rounded-full ${dotColor} border-2 border-white shadow-sm z-10`} />

                <div className="bg-white rounded-2xl p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-3">
                        <h4 className="font-bold text-etest-text">{milestone.title}</h4>
                        {milestone.mentorApproved && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-etest-green-bg text-etest-green text-[10px] font-bold rounded-full">
                            <CheckCircle className="w-3 h-3" /> Mentor
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-etest-hint mt-1">
                        {new Date(milestone.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                        {' · '}
                        <span className="capitalize">{milestone.type.replace(/_/g, ' ')}</span>
                      </p>
                    </div>
                    {milestone.authScore && (
                      <span className="text-xs font-bold text-etest-subtext bg-etest-bg-secondary px-2 py-1 rounded">
                        {milestone.status === 'in_progress' ? '⏳ Pending' : `${milestone.authScore}% Auth`}
                      </span>
                    )}
                  </div>

                  {/* Trace Links */}
                  {relatedLinks.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-etest-border/10">
                      <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest mb-2">Trace Links</p>
                      <div className="flex flex-wrap gap-2">
                        {relatedLinks.map(link => (
                          <div
                            key={link.id}
                            className="inline-flex items-center gap-2 px-3 py-1.5 bg-etest-bg rounded-lg text-xs"
                          >
                            <ExternalLink className="w-3 h-3 text-etest-hint" />
                            <span className="font-medium text-etest-text">{link.sourceTitle === milestone.title ? link.targetTitle : link.sourceTitle}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Public Profile CTA */}
      <section className="bg-white rounded-3xl p-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-etest-purple-light flex items-center justify-center">
              <ExternalLink className="w-6 h-6 text-etest-purple" />
            </div>
            <div>
              <p className="font-bold text-etest-text">ETESTER Public Profile</p>
              <p className="text-xs text-etest-hint mt-0.5">Verified credential page for university submissions</p>
            </div>
          </div>
          <Link
            to={`/etester/verify/${student.id}`}
            className="inline-flex items-center gap-2 px-6 py-3 text-sm font-bold text-white bg-etest-purple rounded-xl shadow-lg shadow-etest-purple/20 hover:bg-etest-purple/90 transition-all"
          >
            View public profile <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-xs text-etest-hint py-4">
        ETESTER Digital Passport System © 2024 · Blockchain Verified Credentials
      </footer>
    </div>
  )
}
