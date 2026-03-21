import { useNavigate } from 'react-router-dom'
import { CheckCircle, Clock, ChevronRight, Users, Shield } from 'lucide-react'

interface BadgeCandidate {
  id: string
  name: string
  program: string
  months: number
  milestones: number
  mentorVerified: number
  authScore: number
  status: 'ready' | 'pending_review' | 'partial'
  readinessCount: string
}

const CANDIDATES: BadgeCandidate[] = [
  {
    id: 'student_001',
    name: 'Nguyễn Hà Minh Anh',
    program: 'AMP',
    months: 14,
    milestones: 23,
    mentorVerified: 18,
    authScore: 94,
    status: 'ready',
    readinessCount: '6/7',
  },
  {
    id: 'student_002',
    name: 'Trần Đức Huy',
    program: 'Foundation',
    months: 10,
    milestones: 15,
    mentorVerified: 12,
    authScore: 87,
    status: 'pending_review',
    readinessCount: '5/7',
  },
  {
    id: 'student_003',
    name: 'Lê Thị Phương Linh',
    program: 'AMP',
    months: 18,
    milestones: 28,
    mentorVerified: 24,
    authScore: 96,
    status: 'ready',
    readinessCount: '7/7',
  },
  {
    id: 'student_004',
    name: 'Phạm Quốc Bảo',
    program: 'Foundation',
    months: 6,
    milestones: 8,
    mentorVerified: 5,
    authScore: 72,
    status: 'partial',
    readinessCount: '3/7',
  },
]

const STATUS_CONFIG = {
  ready: { label: 'Ready to sign', bg: 'bg-etest-green-bg', text: 'text-etest-green', border: 'border-etest-green/20', icon: CheckCircle },
  pending_review: { label: 'Pending review', bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200', icon: Clock },
  partial: { label: 'Incomplete', bg: 'bg-slate-100', text: 'text-slate-500', border: 'border-slate-200', icon: Clock },
}

export default function ManagerHome() {
  const navigate = useNavigate()

  const readyCount = CANDIDATES.filter(c => c.status === 'ready').length
  const pendingCount = CANDIDATES.filter(c => c.status === 'pending_review').length

  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-5">
        <div className="bg-white rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-etest-red/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-etest-red" />
            </div>
            <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">Total Candidates</p>
          </div>
          <p className="text-3xl font-black text-etest-text">{CANDIDATES.length}</p>
        </div>
        <div className="bg-white rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-etest-green/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-etest-green" />
            </div>
            <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">Ready to Sign</p>
          </div>
          <p className="text-3xl font-black text-etest-green">{readyCount}</p>
        </div>
        <div className="bg-white rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
              <Clock className="w-5 h-5 text-amber-500" />
            </div>
            <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">Pending Review</p>
          </div>
          <p className="text-3xl font-black text-amber-600">{pendingCount}</p>
        </div>
      </div>

      {/* Student List */}
      <section>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-etest-red" />
            <h2 className="text-xl font-bold text-etest-text">Badge Candidates</h2>
          </div>
          <span className="text-xs text-etest-hint font-medium">{CANDIDATES.length} students</span>
        </div>

        <div className="space-y-3">
          {CANDIDATES.map(candidate => {
            const config = STATUS_CONFIG[candidate.status]
            const StatusIcon = config.icon
            return (
              <button
                key={candidate.id}
                onClick={() => navigate(`/manager/badges/${candidate.id}`)}
                className="w-full bg-white rounded-2xl p-5 flex items-center gap-5 hover:shadow-md transition-all group text-left"
              >
                <div className="w-12 h-12 rounded-xl bg-etest-blue text-white flex items-center justify-center text-lg font-black flex-shrink-0">
                  {candidate.name.split(' ').pop()?.[0]}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <h3 className="font-bold text-etest-text truncate">{candidate.name}</h3>
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${config.bg} ${config.text} border ${config.border}`}>
                      <StatusIcon className="w-3 h-3" />
                      {config.label}
                    </span>
                  </div>
                  <p className="text-xs text-etest-hint mt-1">
                    {candidate.program} · {candidate.months} months · {candidate.milestones} milestones
                  </p>
                </div>

                <div className="flex items-center gap-6 flex-shrink-0">
                  <div className="text-center">
                    <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">Verified</p>
                    <p className="text-sm font-black text-etest-blue">{candidate.mentorVerified}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">Auth</p>
                    <p className={`text-sm font-black ${candidate.authScore >= 90 ? 'text-etest-green' : candidate.authScore >= 80 ? 'text-amber-600' : 'text-slate-500'}`}>
                      {candidate.authScore}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">Readiness</p>
                    <p className="text-sm font-black text-etest-text">{candidate.readinessCount}</p>
                  </div>
                  <div className="w-8 h-8 rounded-lg bg-etest-bg-secondary flex items-center justify-center text-etest-hint group-hover:bg-etest-red group-hover:text-white transition-all">
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </section>
    </div>
  )
}
