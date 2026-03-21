import { MOCK_STUDENT, MOCK_ETESTER, MOCK_MILESTONES } from '../../data/mock'
import EtesterSeal from '../../components/shared/EtesterSeal'
import ContributorDonut from '../../components/shared/ContributorDonut'
import QrBadge from '../../components/shared/QrBadge'
import { Award, CheckCircle, TrendingUp, Zap } from 'lucide-react'

export default function StudentEtester() {
  const student = MOCK_STUDENT
  const etester = MOCK_ETESTER
  const recentMilestones = MOCK_MILESTONES.slice(0, 3)

  return (
    <div className="space-y-12">
      {/* Header Section: Hero Profile */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm overflow-hidden relative">
        {/* Decorative blurred circles */}
        <div className="absolute right-0 -top-24 w-96 h-96 bg-etest-red/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-24 top-44 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex items-center gap-8 p-10">
          {/* Avatar & Stamp */}
          <div className="relative flex-shrink-0">
            {/* Rotated stamp effect behind avatar */}
            <div className="absolute -right-4 -bottom-4 w-48 h-48 bg-white rounded-3xl shadow-lg rotate-[-3deg] opacity-80" />
            <div className="relative w-48 h-48 rounded-full bg-gradient-to-br from-etest-red to-red-800 flex items-center justify-center shadow-lg">
              <EtesterSeal verified={etester.badgeIssued} size="lg" />
            </div>
          </div>

          {/* Identity Info */}
          <div className="flex-1">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-etest-red-light px-3 py-1.5 rounded-full mb-4">
              <span className="text-xs font-bold text-etest-red">
                Level {etester.academicScore}
              </span>
            </div>

            {/* Name */}
            <h1 className="text-3xl font-bold text-etest-text mb-2">
              {student.name}
            </h1>

            {/* Program info */}
            <p className="text-sm text-etest-subtext mb-6">
              {student.program} • {student.monthsEnrolled} tháng học
            </p>

            {/* Quick stats row */}
            <div className="flex gap-4">
              <div className="bg-etest-bg-secondary rounded-2xl px-6 py-4 min-w-[140px]">
                <p className="text-3xl font-bold text-etest-teal">{etester.totalContributions}</p>
                <p className="text-xs text-etest-subtext mt-1">Đóng góp</p>
              </div>
              <div className="bg-amber-100 rounded-2xl px-6 py-4 min-w-[140px]">
                <p className="text-3xl font-bold text-amber-600">{etester.mentorVerifications}</p>
                <p className="text-xs text-etest-subtext mt-1">Xác nhận mentor</p>
              </div>
              <div className="bg-etest-green-bg rounded-2xl px-6 py-4 min-w-[140px]">
                <p className="text-3xl font-bold text-etest-green">{etester.consistencyScore}%</p>
                <p className="text-xs text-etest-subtext mt-1">Độ nhất quán</p>
              </div>
            </div>
          </div>
        </div>

        {/* Background branding */}
        <div className="absolute right-10 top-10 opacity-10 pointer-events-none">
          <span className="text-6xl font-black text-etest-red">ETEST</span>
        </div>
      </section>

      {/* Stats & Insights Bento Grid */}
      <section className="grid grid-cols-12 gap-8">
        {/* Left Column - Core Stats */}
        <div className="col-span-8 space-y-8">
          {/* 4 Stat Cards Row */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white rounded-3xl border border-etest-border/10 p-6 text-center">
              <div className="w-12 h-12 rounded-2xl bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
                <Award className="w-6 h-6 text-etest-teal" />
              </div>
              <p className="text-3xl font-bold text-etest-text">{student.ieltsScore.toFixed(1)}</p>
              <p className="text-xs text-etest-subtext mt-1">IELTS</p>
            </div>
            <div className="bg-white rounded-3xl border border-etest-border/10 p-6 text-center">
              <div className="w-12 h-12 rounded-2xl bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-etest-teal" />
              </div>
              <p className="text-3xl font-bold text-etest-text">{student.satScore ?? '—'}</p>
              <p className="text-xs text-etest-subtext mt-1">SAT</p>
            </div>
            <div className="bg-white rounded-3xl border border-etest-border/10 p-6 text-center">
              <div className="w-12 h-12 rounded-2xl bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-etest-teal" />
              </div>
              <p className="text-3xl font-bold text-etest-text">{etester.mentorVerifications}</p>
              <p className="text-xs text-etest-subtext mt-1">Xác nhận</p>
            </div>
            <div className="bg-white rounded-3xl border border-etest-border/10 p-6 text-center">
              <div className="w-12 h-12 rounded-2xl bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
                <Zap className="w-6 h-6 text-etest-teal" />
              </div>
              <p className="text-3xl font-bold text-etest-text">{etester.skills.length}</p>
              <p className="text-xs text-etest-subtext mt-1">Kỹ năng</p>
            </div>
          </div>

          {/* AI Narrative Card */}
          <div className="bg-[#d8e2ff] rounded-3xl p-8">
            <h3 className="font-bold text-etest-text mb-4">Câu chuyện của bạn</h3>
            <p className="text-sm text-etest-subtext leading-relaxed whitespace-pre-line">
              {etester.narrativeCache}
            </p>
          </div>

          {/* Skills Tags */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <h3 className="font-bold text-etest-text mb-4">Kỹ năng đã xác thực</h3>
            <div className="flex flex-wrap gap-3">
              {etester.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-etest-teal-light text-etest-teal text-sm font-medium rounded-full border border-etest-teal-border"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Donut & QR */}
        <div className="col-span-4 space-y-8">
          {/* Contributor Breakdown Donut */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <h3 className="font-bold text-etest-text mb-6">Nguồn đóng góp</h3>
            <div className="flex justify-center mb-6">
              <ContributorDonut
                data={[
                  { name: 'Học viên', value: etester.totalContributions - etester.mentorVerifications, color: '#3B82F6' },
                  { name: 'Mentor', value: etester.mentorVerifications, color: '#0D9488' },
                  ...(etester.institutionalStamp ? [{ name: 'Trường', value: 1, color: '#F59E0B' }] : []),
                ]}
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span className="text-etest-subtext">Học viên</span>
                </div>
                <span className="font-medium text-etest-text">{etester.totalContributions - etester.mentorVerifications}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-etest-teal" />
                  <span className="text-etest-subtext">Mentor</span>
                </div>
                <span className="font-medium text-etest-text">{etester.mentorVerifications}</span>
              </div>
              {etester.institutionalStamp && (
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-amber-500" />
                    <span className="text-etest-subtext">Trường</span>
                  </div>
                  <span className="font-medium text-etest-text">1</span>
                </div>
              )}
            </div>
          </div>

          {/* QR Code Profile Card */}
          <div className="bg-white rounded-3xl border-2 border-etest-red/5 shadow-sm p-8">
            <h3 className="font-bold text-etest-text mb-6">Mã xác thực QR</h3>
            <div className="flex justify-center mb-4">
              <QrBadge value={`https://etest.vn/etester/verify/${student.id}`} size={140} />
            </div>
            <p className="text-xs text-center text-etest-subtext">
              Quét để xác thực hồ sơ ETESTER
            </p>
          </div>

          {/* Recent Milestones */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <h3 className="font-bold text-etest-text mb-4">Thành tựu gần đây</h3>
            <div className="space-y-3">
              {recentMilestones.map((milestone) => (
                <div
                  key={milestone.id}
                  className="flex items-center gap-3 p-3 bg-etest-bg rounded-xl"
                >
                  <div className="w-8 h-8 rounded-full bg-etest-green-bg flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-4 h-4 text-etest-green" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-etest-text truncate">{milestone.title}</p>
                    <p className="text-xs text-etest-subtext">{milestone.date}</p>
                  </div>
                  {milestone.mentorApproved && (
                    <span className="text-[10px] font-bold text-etest-green bg-etest-green-bg px-2 py-0.5 rounded-full">
                      Đã xác nhận
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
