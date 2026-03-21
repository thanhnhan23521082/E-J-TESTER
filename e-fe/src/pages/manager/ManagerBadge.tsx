import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MOCK_STUDENT, MOCK_ETESTER, MOCK_AUTH_SCORE } from '../../data/mock'
import AuthScoreCard from '../../components/etester/AuthScoreCard'
import {
  ChevronRight,
  CheckCircle,
  XCircle,
  Lock,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Shield,
  Globe,
  BookOpen,
  Heart,
  Users,
  GraduationCap,
  FileText,
  Award as AwardIcon,
  Medal,
  X,
  ExternalLink,
} from 'lucide-react'
import type { CredentialType } from '../../types'

const READINESS_ITEMS = [
  { label: '23 milestones completed', passed: true },
  { label: '18 mentor verified', passed: true },
  { label: 'Avg authenticity 91%', passed: true },
  { label: 'Final essay mentor approved', passed: true },
  { label: 'Admin process verified', passed: true },
  { label: '0 pending trace links', passed: true },
  { label: 'Badge not yet issued', passed: false },
]

const REQUIREMENTS = [
  { icon: Globe, label: 'English Proficiency', covered: true },
  { icon: FileText, label: 'Standardized Test', covered: true },
  { icon: BookOpen, label: 'Personal Essay', covered: true },
  { icon: GraduationCap, label: 'Extracurricular', covered: true },
  { icon: Heart, label: 'Community Service', covered: true },
  { icon: Users, label: 'Leadership Evidence', covered: true },
  { icon: BookOpen, label: 'Academic Record', covered: true },
  { icon: AwardIcon, label: 'Recommendation', covered: true },
  { icon: Medal, label: 'Awards/Honors', covered: false },
]

const SIGNING_CHAIN = [
  { step: 1, label: 'Mentor sign', status: 'verified' as const },
  { step: 2, label: 'Admin sign', status: 'verified' as const },
  { step: 3, label: 'Manager seal', status: 'pending' as const },
]

export default function ManagerBadge() {
  const navigate = useNavigate()
  const student = MOCK_STUDENT
  const etester = MOCK_ETESTER
  const [credentialType, setCredentialType] = useState<CredentialType>('jwt_rs256')
  const [showAuthScore, setShowAuthScore] = useState(false)

  return (
    <div className="space-y-8">
      {/* AuthScore Side Panel */}
      {showAuthScore && (
        <>
          <div className="fixed inset-0 bg-etest-text/20 z-[60] backdrop-blur-sm" onClick={() => setShowAuthScore(false)} />
          <div className="fixed top-0 right-0 h-full w-full max-w-2xl bg-etest-bg z-[70] shadow-2xl flex flex-col overflow-hidden">
            <div className="px-8 pt-8 pb-4 flex items-center justify-between bg-white border-b border-etest-border/10">
              <div>
                <h2 className="text-lg font-bold text-etest-text">Authenticity Score Breakdown</h2>
                <p className="text-xs text-etest-hint mt-0.5">{student.name}</p>
              </div>
              <button
                onClick={() => setShowAuthScore(false)}
                className="h-10 w-10 flex items-center justify-center rounded-full hover:bg-etest-bg-secondary transition-colors text-etest-hint"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-8">
              <AuthScoreCard data={MOCK_AUTH_SCORE} />
            </div>
          </div>
        </>
      )}
      {/* Back + Breadcrumbs */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/manager')}
          className="h-9 w-9 flex items-center justify-center rounded-xl hover:bg-etest-bg-secondary transition-colors text-etest-hint"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <nav className="flex text-sm text-etest-hint gap-2 items-center">
          <span className="hover:text-etest-text cursor-pointer" onClick={() => navigate('/manager')}>Badge Candidates</span>
          <ChevronRight className="w-3 h-3" />
          <span className="text-etest-red font-bold">{student.name}</span>
        </nav>
      </div>

      <div className="grid grid-cols-12 gap-8 items-start">
        {/* LEFT COLUMN */}
        <div className="col-span-12 lg:col-span-5 space-y-6">
          {/* Student Card */}
          <section className="bg-white rounded-3xl p-6 shadow-[0_12px_32px_rgba(187,0,22,0.04)] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-etest-red/5 rounded-bl-full" />
            <div className="flex items-center gap-5 relative z-10">
              <div className="w-20 h-20 rounded-2xl bg-etest-blue text-white flex items-center justify-center text-2xl font-black shadow-lg shadow-blue-900/20">
                MA
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-etest-text leading-tight">{student.name}</h1>
                <div className="flex items-center gap-2 mt-1">
                  <span className="px-3 py-0.5 bg-etest-blue-light text-etest-blue-dark rounded-full text-xs font-bold uppercase tracking-wider">
                    {student.program}
                  </span>
                  <span className="text-etest-hint text-sm">· {student.monthsEnrolled} months duration</span>
                </div>
              </div>
            </div>
          </section>

          {/* Readiness Checklist */}
          <section className="bg-etest-bg-secondary rounded-3xl p-6 space-y-4">
            <h3 className="font-bold text-lg text-etest-text flex items-center gap-2">
              <Shield className="w-5 h-5 text-etest-blue" />
              Readiness Checklist
            </h3>
            <div className="space-y-3">
              {READINESS_ITEMS.map((item, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 text-sm font-medium ${
                    item.passed
                      ? 'text-slate-700'
                      : 'text-red-500 bg-red-50/50 p-3 rounded-xl border border-red-500/10'
                  }`}
                >
                  {item.passed ? (
                    <CheckCircle className="w-5 h-5 text-etest-green flex-shrink-0" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  )}
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Requirements Coverage */}
          <section className="bg-white rounded-3xl p-6 border border-etest-border/10 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-etest-text">Requirements Coverage</h3>
              <span className="text-xs font-bold text-etest-blue bg-etest-blue/10 px-2 py-1 rounded">
                {REQUIREMENTS.filter(r => r.covered).length}/{REQUIREMENTS.length} Covered
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {REQUIREMENTS.map((req, i) => (
                <div
                  key={i}
                  className={`aspect-square rounded-xl flex flex-col items-center justify-center p-2 text-center transition-all ${
                    req.covered
                      ? 'bg-green-50 hover:bg-green-100'
                      : 'bg-slate-100 opacity-50 grayscale'
                  }`}
                >
                  <req.icon className={`w-5 h-5 ${req.covered ? 'text-green-600' : 'text-slate-400'}`} />
                  <span className="text-[9px] mt-1 font-bold text-slate-600">{req.label}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Signing Chain */}
          <section className="bg-etest-bg-secondary rounded-3xl p-6">
            <h3 className="font-bold text-etest-text mb-4">Signing Chain Status</h3>
            <div className="space-y-6 relative">
              <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-slate-200" />
              {SIGNING_CHAIN.map(step => (
                <div key={step.step} className="flex items-center gap-4 relative z-10">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center ${
                    step.status === 'verified'
                      ? 'bg-green-600 text-white'
                      : 'bg-amber-400'
                  }`}>
                    {step.status === 'verified' ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-etest-text">Step {step.step}: {step.label}</p>
                    <p className={`text-[10px] font-bold uppercase tracking-widest ${
                      step.status === 'verified' ? 'text-green-600' : 'text-amber-600'
                    }`}>
                      {step.status === 'verified' ? 'Verified' : 'Pending Action'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* RIGHT COLUMN */}
        <div className="col-span-12 lg:col-span-7 space-y-6">
          {/* Badge Payload Preview */}
          <section className="bg-etest-text text-white rounded-3xl p-8 shadow-2xl relative">
            <div className="absolute top-6 right-8">
              <Shield className="w-12 h-12 text-white/20" />
            </div>
            <div className="mb-8">
              <h2 className="text-xl font-bold mb-1">Badge payload — preview before signing</h2>
              <p className="text-slate-400 text-sm">Review the cryptographic data structure that will be permanently issued.</p>
            </div>
            <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm">
              {[
                { label: 'Student', value: student.name },
                { label: 'Program', value: student.program },
                { label: 'Months', value: String(student.monthsEnrolled) },
                { label: 'Milestones', value: String(etester.totalContributions) },
                { label: 'Mentor sign', value: `${etester.mentorVerifications} verified` },
                { label: 'IELTS / SAT', value: `${student.ieltsScore} / ${student.satScore || '—'}` },
                { label: 'Auth avg', value: `${etester.consistencyScore}%` },
                { label: 'Leadership', value: 'Yes — 4 activities, max 8 people' },
                { label: 'Requirements', value: `${REQUIREMENTS.filter(r => r.covered).length}/${REQUIREMENTS.length} covered` },
                { label: 'Expires', value: 'March 21 2028' },
              ].map(item => (
                <div key={item.label} className="flex flex-col gap-1 border-b border-white/10 pb-2">
                  <span className="text-slate-500 font-bold text-[10px] uppercase tracking-widest">{item.label}</span>
                  <span className="font-medium">{item.value}</span>
                </div>
              ))}
              <div className="col-span-2 flex flex-col gap-1 pt-2">
                <span className="text-slate-500 font-bold text-[10px] uppercase tracking-widest">Issuer</span>
                <span className="font-medium text-etest-pink-dim">ETEST Vietnam (Academic Atelier Certificate Authority)</span>
              </div>
            </div>
          </section>

          {/* Credential Type Selector */}
          <section className="bg-etest-bg-secondary rounded-3xl p-6">
            <h3 className="font-bold text-etest-text mb-4">Credential Type Selector</h3>
            <div className="grid grid-cols-2 gap-4">
              <label className={`relative flex flex-col gap-2 p-4 rounded-2xl border-2 cursor-pointer ${
                credentialType === 'jwt_rs256' ? 'border-etest-red bg-white' : 'border-slate-200 bg-slate-50'
              }`}>
                <input
                  type="radio"
                  className="sr-only"
                  checked={credentialType === 'jwt_rs256'}
                  onChange={() => setCredentialType('jwt_rs256')}
                />
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-bold ${credentialType === 'jwt_rs256' ? 'text-etest-red' : 'text-slate-400'}`}>
                    JWT RS256
                  </span>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center p-0.5 ${
                    credentialType === 'jwt_rs256' ? 'border-etest-red' : 'border-slate-200'
                  }`}>
                    {credentialType === 'jwt_rs256' && <div className="w-full h-full bg-etest-red rounded-full" />}
                  </div>
                </div>
                <p className="text-xs text-etest-hint">Standard demo and current production signature.</p>
              </label>

              <label className="relative flex flex-col gap-2 p-4 rounded-2xl border-2 border-slate-200 bg-slate-50 opacity-60 cursor-not-allowed">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-400">W3C VC Ed25519</span>
                  <div className="w-5 h-5 rounded-full border-2 border-slate-200" />
                </div>
                <span className="text-[10px] bg-slate-200 text-slate-500 font-bold self-start px-2 py-0.5 rounded uppercase tracking-tighter">
                  Coming Soon
                </span>
              </label>
            </div>
          </section>

          {/* Auth Score Quick Action */}
          <button
            onClick={() => setShowAuthScore(true)}
            className="w-full bg-white rounded-2xl p-5 flex items-center justify-between hover:shadow-md transition-all group border border-etest-border/10"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-etest-green/10 flex items-center justify-center">
                <Shield className="w-6 h-6 text-etest-green" />
              </div>
              <div className="text-left">
                <p className="font-bold text-etest-text">Authenticity Score</p>
                <p className="text-xs text-etest-hint">View 7-dimension breakdown</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-black text-etest-green">{MOCK_AUTH_SCORE.overallScore}%</span>
              <ArrowRight className="w-4 h-4 text-etest-hint group-hover:text-etest-red transition-colors" />
            </div>
          </button>

          {/* Issue Action */}
          <div className="space-y-4">
            <button className="w-full h-[64px] bg-gradient-to-r from-[#6200EE] to-[#3700B3] text-white rounded-2xl font-extrabold text-lg shadow-xl shadow-indigo-900/20 active:scale-[0.98] transition-all hover:brightness-110 flex items-center justify-center gap-3">
              <Lock className="w-5 h-5" />
              Issue ETESTER Badge
            </button>
            <div className="flex items-start gap-3 px-4">
              <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
              <p className="text-xs text-etest-hint leading-relaxed">
                <span className="font-bold text-slate-700">Permanent action.</span> Badge can be revoked but not deleted. Issuance creates a permanent ledger entry.
              </p>
            </div>
          </div>

          {/* Preview Public Profile */}
          <button
            onClick={() => navigate(`/etester/verify/${student.id}?preview=true`)}
            className="w-full bg-etest-bg-secondary rounded-2xl p-4 flex items-center justify-center gap-2 text-sm font-semibold text-etest-blue hover:bg-etest-blue-light transition-all"
          >
            <ExternalLink className="w-4 h-4" />
            Preview public profile
            <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-full uppercase tracking-wider">Preview</span>
          </button>
        </div>
      </div>
    </div>
  )
}
