import { useParams, Link, useSearchParams } from 'react-router-dom'
import { Shield, CheckCircle, ArrowLeft, ArrowRight, Minus, Quote, Award, Globe, AlertTriangle } from 'lucide-react'
import { MOCK_STUDENT, MOCK_ETESTER } from '../../data/mock'

const REQUIREMENTS = [
  { label: 'English proficiency', covered: true },
  { label: 'Standardized test', covered: true },
  { label: 'Personal essay', covered: true },
  { label: 'Extracurricular', covered: true },
  { label: 'Community service', covered: true },
  { label: 'Leadership evidence', covered: true },
  { label: 'Academic record', covered: true },
  { label: 'Recommendation', covered: true },
  { label: 'Awards/honors', covered: false },
]

export default function EtesterPublic() {
  const { studentId } = useParams()
  const [searchParams] = useSearchParams()
  const isPreview = searchParams.get('preview') === 'true'
  const student = MOCK_STUDENT
  const etester = MOCK_ETESTER

  if (studentId !== student.id) {
    return (
      <div className="min-h-screen bg-etest-bg flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 text-center max-w-md shadow-lg">
          <Shield className="w-16 h-16 text-etest-red mx-auto mb-4" />
          <h1 className="text-xl font-bold text-etest-text mb-2">Không tìm thấy hồ sơ</h1>
          <p className="text-sm text-etest-subtext mb-6">ID học viên không hợp lệ hoặc hồ sơ không tồn tại.</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-etest-teal font-medium hover:text-etest-teal-dark"
          >
            <ArrowLeft className="w-4 h-4" /> Về trang chủ
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-etest-bg flex flex-col">
      {/* Preview Banner */}
      {isPreview && (
        <div className="bg-amber-50 border-b border-amber-200">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-center gap-3">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <p className="text-sm font-bold text-amber-700">
              PREVIEW — Badge chưa được phát hành. Đây là bản xem trước.
            </p>
          </div>
        </div>
      )}

      {/* Top Navigation */}
      <header className="bg-etest-bg sticky top-0 z-50">
        <div className="flex justify-between items-center w-full px-6 py-4 max-w-7xl mx-auto">
          <div className="text-2xl font-black text-etest-red tracking-tight">ETESTER</div>
          <div className="flex items-center gap-6">
            <button className="text-etest-hint font-medium hover:bg-etest-bg-secondary transition-colors px-4 py-2 rounded-lg text-sm">
              Verify Another
            </button>
            {isPreview ? (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-50 text-amber-700 rounded-full border border-amber-200">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Preview Mode</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-100">
                <CheckCircle className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Official Verification</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="flex-grow max-w-5xl mx-auto w-full px-6 py-12 space-y-12">
        {/* Trust Header */}
        <section className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pb-8 border-b border-etest-border/10">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold text-etest-text tracking-tight">Verified by ETEST Vietnam</h1>
            <p className="text-etest-hint font-medium">
              Issued: {new Date(etester.lastUpdated).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} · Valid
            </p>
          </div>
          <div className="flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 text-emerald-600">
            <CheckCircle className="w-10 h-10" />
          </div>
        </section>

        {/* Student Identity + Leadership */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          <div className="lg:col-span-2 bg-etest-bg-secondary rounded-xl p-8 flex items-center gap-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-etest-red/5 rounded-full -mr-16 -mt-16" />
            <div className="w-24 h-24 rounded-xl bg-white shadow-[0_12px_32px_rgba(187,0,22,0.04)] flex items-center justify-center overflow-hidden border border-etest-border/10">
              <div className="w-full h-full bg-etest-red flex items-center justify-center text-white font-black text-3xl">
                {student.name.split(' ').map(n => n[0]).slice(-2).join('')}
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-bold text-etest-text">{student.name}</h2>
                <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-200 uppercase tracking-tighter">
                  ETEST Verified
                </span>
              </div>
              <p className="text-etest-muted font-medium">{student.program} Program · {student.monthsEnrolled} months enrolled</p>
              <div className="flex gap-2 pt-2">
                <span className="text-xs bg-white px-2 py-1 rounded-md text-etest-hint border border-etest-border/5">
                  ID: ET-2026-8812
                </span>
                <span className="text-xs bg-white px-2 py-1 rounded-md text-etest-hint border border-etest-border/5">
                  Cohort: Spring 2025
                </span>
              </div>
            </div>
          </div>

          <div className="bg-teal-50 border border-teal-100 rounded-xl p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-teal-900 font-bold flex items-center gap-2 mb-3">
                <Award className="w-5 h-5 text-teal-600" />
                Leadership Summary
              </h3>
              <p className="text-teal-800/80 text-sm mb-4 leading-relaxed">
                Leadership documented across 4 activities · 6 months
              </p>
              <ul className="space-y-2">
                {['President, Debate Club', 'Team Lead, Green Earth Project'].map(item => (
                  <li key={item} className="text-xs font-semibold text-teal-900 flex items-center gap-2">
                    <span className="w-1 h-1 rounded-full bg-teal-500" /> {item}
                  </li>
                ))}
              </ul>
            </div>
            <button className="mt-6 text-teal-700 text-xs font-bold uppercase tracking-widest hover:underline text-left">
              View details
            </button>
          </div>
        </section>

        {/* Requirements Coverage */}
        <section className="space-y-6">
          <h3 className="text-xl font-bold text-etest-text">
            Profile requirements covered: {REQUIREMENTS.filter(r => r.covered).length} of {REQUIREMENTS.length}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {REQUIREMENTS.map(req => (
              <div
                key={req.label}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg ${
                  req.covered
                    ? 'bg-emerald-50 border border-emerald-100/50'
                    : 'bg-slate-100 border border-slate-200 opacity-60'
                }`}
              >
                {req.covered ? (
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                ) : (
                  <Minus className="w-5 h-5 text-slate-400" />
                )}
                <span className={`text-sm font-medium ${req.covered ? 'text-emerald-900' : 'text-slate-500'}`}>
                  {req.label}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Verified Stats + Trace Chain */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-etest-text">Verified Performance Metrics</h3>
            <div className="overflow-hidden rounded-xl bg-etest-bg-secondary">
              <table className="w-full text-left border-collapse">
                <tbody>
                  {[
                    { label: 'Time enrolled', value: `${student.monthsEnrolled} months` },
                    { label: 'Milestones', value: String(etester.totalContributions) },
                    { label: 'Mentor verified', value: String(etester.mentorVerifications) },
                    { label: 'IELTS Score', value: student.ieltsScore.toFixed(1), highlight: true },
                    { label: 'SAT Score', value: student.satScore?.toString() ?? '—', highlight: true },
                    { label: 'Authenticity Score', value: `${etester.consistencyScore}%`, color: 'text-emerald-600' },
                    { label: 'Essays Finalized', value: '6' },
                  ].map((row, i) => (
                    <tr key={row.label} className={`border-b border-white/50 ${i % 2 === 1 ? 'bg-white/20' : ''}`}>
                      <td className="px-6 py-4 text-sm font-medium text-etest-hint">{row.label}</td>
                      <td className={`px-6 py-4 text-sm font-bold text-right ${row.color || (row.highlight ? 'text-etest-red' : 'text-etest-text')}`}>
                        {row.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="space-y-6">
            <h3 className="text-xl font-bold text-etest-text">Verification Integrity</h3>
            <div className="bg-indigo-50 border-l-4 border-indigo-500 p-8 rounded-r-xl space-y-4">
              <div className="flex items-center gap-3 text-indigo-900 font-bold">
                <Globe className="w-5 h-5" />
                Trace Chain Summary
              </div>
              <p className="text-indigo-800 text-sm leading-relaxed">
                Personal Statement verified through 9 connected artifacts, all mentor-confirmed. This ensures that every milestone in the student's journey is anchored by physical evidence and professional assessment.
              </p>
              <button className="inline-flex items-center gap-2 text-indigo-700 font-bold text-xs uppercase tracking-widest hover:text-indigo-900 transition-colors">
                View full learning graph
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Narrative Card */}
            <div className="bg-white shadow-[0_12px_32px_rgba(187,0,22,0.04)] rounded-xl p-8 border border-etest-border/5 relative">
              <Quote className="absolute top-4 right-4 w-10 h-10 text-slate-200" />
              <h4 className="text-xs font-bold text-etest-hint uppercase tracking-widest mb-4">Academic Narrative</h4>
              <p className="text-etest-text leading-relaxed italic mb-4">
                "{student.name} demonstrates exceptional analytical growth, particularly in connecting environmental policy with local community initiatives. Her ability to synthesize complex data into actionable leadership strategies has been a consistent highlight of her {student.monthsEnrolled}-month engagement."
              </p>
              <p className="text-[10px] text-etest-hint font-medium">From verified activity records</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-etest-bg-secondary mt-12 border-t border-etest-border/5">
        <div className="w-full py-12 px-6 flex flex-col md:flex-row justify-between items-center gap-4 max-w-7xl mx-auto">
          <div className="flex flex-col gap-1">
            <div className="font-semibold text-slate-900">ETEST Vietnam</div>
            <div className="text-[10px] text-etest-hint uppercase font-bold tracking-widest">Digital Credential Service</div>
          </div>
          <div className="text-etest-hint text-sm text-center md:text-left">
            © 2024 ETEST Academic Atelier. Official Digital Credential Verification Service.
            <div className="mt-2 text-[11px] text-etest-hint italic">This page is for verification purposes only</div>
          </div>
          <div className="flex gap-6">
            {['Privacy Policy', 'Terms of Service', 'Contact Support'].map(link => (
              <a key={link} href="#" className="text-etest-hint hover:text-etest-red transition-all text-sm font-medium">
                {link}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  )
}
