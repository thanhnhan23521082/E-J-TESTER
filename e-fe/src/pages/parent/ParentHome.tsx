import { useNavigate } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Calendar,
  Clock,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import { useStudentData } from '../../hooks/useStudentData'

type AlertTone = 'good' | 'warning' | 'critical'

export default function ParentHome() {
  const navigate = useNavigate()
  const { student, wellbeing, digest, behavioralLogs, upsell, loading, error } = useStudentData()

  const weekLogs = behavioralLogs.slice(0, 7)
  const studiedDaysPerWeek = weekLogs.filter((log) => log.studied).length
  const studiedDurations = weekLogs
    .filter((log) => log.studied)
    .map((log) => log.durationMin)
    .filter((duration) => duration > 0)
  const avgHoursPerDay =
    studiedDurations.length > 0
      ? studiedDurations.reduce((sum, duration) => sum + duration, 0) /
        studiedDurations.length /
        60
      : 0
  const lateNightCount = weekLogs.filter((log) => log.isLateNight && log.studied).length

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-2 border-etest-teal border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="text-etest-red text-lg font-semibold mb-2">Lỗi tải dữ liệu</div>
          <div className="text-etest-subtext">{error}</div>
        </div>
      </div>
    )
  }

  if (!student) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-etest-subtext">Không tìm thấy thông tin học sinh</div>
      </div>
    )
  }

  const isSatProgram = student.program === 'SAT'
  const scoreLabel = isSatProgram ? 'SAT' : 'IELTS'
  const maxScore = isSatProgram ? 1600 : 9
  const currentScore = isSatProgram ? (student.satScore ?? 0) : student.ieltsScore
  const scoreDisplay = isSatProgram ? String(Math.round(currentScore)) : currentScore.toFixed(1)
  const scoreRatio = Math.max(0, Math.min(currentScore / maxScore, 1))

  const summaryText =
    wellbeing?.message ||
    digest?.parentSummary?.trim() ||
    `${student.name} đang có nhịp học ổn định trong tuần này.`
  const combinedAlertText = `${summaryText} ${wellbeing?.message ?? ''}`.toLowerCase()

  const alertTone: AlertTone = combinedAlertText.includes('trầm cảm') || wellbeing?.severity === 'high'
    ? 'critical'
    : combinedAlertText.includes('cần cải thiện') || wellbeing?.severity === 'medium' || wellbeing?.alert
      ? 'warning'
      : 'good'

  const alertTheme = {
    critical: {
      container: 'bg-[#ffe8e6] border-red-300',
      iconBox: 'bg-etest-red',
      title: 'Cảnh báo cần can thiệp',
      subtitle: 'Nên ưu tiên trao đổi với con và mentor ngay hôm nay',
      button: 'bg-etest-red hover:bg-etest-red-dark',
    },
    warning: {
      container: 'bg-[#fff8e1] border-amber-300',
      iconBox: 'bg-etest-amber',
      title: 'Thông báo học tập tuần này',
      subtitle: 'Có vài dấu hiệu cần theo dõi thêm',
      button: 'bg-etest-amber hover:opacity-90',
    },
    good: {
      container: 'bg-[#e9f9f1] border-emerald-300',
      iconBox: 'bg-emerald-600',
      title: 'Tín hiệu tích cực',
      subtitle: 'Con đang duy trì tiến độ học khá tốt',
      button: 'bg-emerald-600 hover:bg-emerald-700',
    },
  }[alertTone]

  const isUrgent = (digest?.daysLeft ?? 0) > 0 && (digest?.daysLeft ?? 0) <= 14
  const programCards = upsell
    ? [
        {
          title: upsell.courseName,
          reason: upsell.reason,
          tag: 'Đề xuất chính',
          gradient: 'from-etest-teal to-blue-600',
          cta: 'Xem chương trình',
          path: upsell.ctaUrl,
        },
        {
          title: `Coaching ${digest?.weakestSkill || 'kỹ năng yếu'} 1:1`,
          reason: 'Lộ trình cá nhân hóa để cải thiện điểm yếu nhanh trong 4-6 tuần.',
          tag: 'Cá nhân hóa',
          gradient: 'from-[#ff8a4c] to-[#ff5a5f]',
          cta: 'Nhận tư vấn ngay',
          path: '/parent/chat',
        },
        {
          title: 'Sprint trước deadline',
          reason: `Tập trung mục tiêu gần nhất: ${
            digest?.nextDeadlineLabel || digest?.nextDeadline || `${digest?.daysLeft ?? 0} ngày tới`
          }.`,
          tag: isUrgent ? 'Ưu tiên cao' : 'Khuyến nghị',
          gradient: 'from-[#613bea] to-[#2a7fff]',
          cta: 'Xem lộ trình sprint',
          path: '/parent/progress',
        },
      ]
    : []

  return (
    <div className="space-y-6">
      <section className={`rounded-3xl border shadow-card p-6 ${alertTheme.container}`}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${alertTheme.iconBox}`}>
              <AlertTriangle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-etest-text">{alertTheme.title}</h2>
              <p className="text-sm text-etest-subtext mt-1">{alertTheme.subtitle}</p>
              <p className="text-base text-etest-text mt-3 leading-relaxed">{summaryText}</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/parent/chat')}
            className={`px-4 py-2 rounded-xl text-white font-semibold whitespace-nowrap transition-colors ${alertTheme.button}`}
          >
            Trao đổi ngay
          </button>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <section className="lg:col-span-5 bg-white rounded-3xl border border-etest-border/20 shadow-card p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-etest-red to-etest-red-secondary flex items-center justify-center">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-etest-text">Deadline gần nhất</h3>
                <p className="text-sm text-etest-subtext">
                  {digest?.nextDeadline || student.targetSchools[0]?.name || 'Chưa có deadline'}
                </p>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full ${isUrgent ? 'bg-[#ffdad6]' : 'bg-etest-bg'}`}>
              <span className={`text-xs font-semibold ${isUrgent ? 'text-etest-red' : 'text-etest-subtext'}`}>
                {isUrgent ? 'Urgent' : 'Bình thường'}
              </span>
            </div>
          </div>

          <div className="text-center py-8">
            <div className="text-7xl font-black text-etest-text mb-2">{digest?.daysLeft || 0}</div>
            <div className="text-xl font-semibold text-etest-subtext">Ngày</div>
          </div>

          <button
            onClick={() => navigate('/parent/progress')}
            className="w-full py-4 bg-gradient-to-r from-etest-red to-etest-red-secondary text-white font-bold rounded-2xl hover:opacity-90 transition-all shadow-button"
          >
            Xem chi tiết timeline
          </button>
        </section>

        <section className="lg:col-span-7 bg-white rounded-3xl border border-etest-border/20 shadow-card p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-etest-blue to-blue-600 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-etest-text">Tiến độ học tập</h3>
                <p className="text-sm text-etest-subtext">{scoreLabel} Overall</p>
              </div>
            </div>
            <div className="relative w-24 h-24">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="#e5e7eb" strokeWidth="8" fill="none" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="#0058be"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${scoreRatio * 251.2} 251.2`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-black text-etest-blue">{scoreDisplay}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6 pt-6 border-t border-etest-border/20">
            <div className="text-center">
              <div className="w-10 h-10 rounded-xl bg-etest-teal-light mx-auto mb-2 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-etest-teal" />
              </div>
              <div className="text-2xl font-bold text-etest-text mb-1">{studiedDaysPerWeek}</div>
              <div className="text-xs text-etest-subtext">Ngày học/tuần</div>
            </div>
            <div className="text-center">
              <div className="w-10 h-10 rounded-xl bg-etest-amber-bg mx-auto mb-2 flex items-center justify-center">
                <Clock className="w-5 h-5 text-etest-amber" />
              </div>
              <div className="text-2xl font-bold text-etest-text mb-1">{avgHoursPerDay.toFixed(1)}</div>
              <div className="text-xs text-etest-subtext">Giờ/buổi học</div>
            </div>
            <div className="text-center">
              <div className="w-10 h-10 rounded-xl bg-etest-green-bg mx-auto mb-2 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-etest-green" />
              </div>
              <div className="text-2xl font-bold text-etest-text mb-1">{lateNightCount}</div>
              <div className="text-xs text-etest-subtext">Buổi học muộn</div>
            </div>
          </div>
        </section>
      </div>

      <section className="bg-white rounded-3xl border border-etest-border/20 shadow-card p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-etest-amber to-etest-red-secondary flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-etest-text">Digest tuần này</h3>
            <p className="text-sm text-etest-subtext">Gộp tổng quan + hành động ưu tiên cho phụ huynh</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-etest-bg-secondary rounded-2xl p-5">
            <p className="text-xs text-etest-subtext mb-1">Số chính</p>
            <p className="text-3xl font-black text-etest-text">{digest?.progressPct ?? 0}%</p>
            <p className="text-sm text-etest-subtext mt-1">Tiến độ hoàn thành</p>
          </div>
          <div className="bg-etest-bg-secondary rounded-2xl p-5">
            <p className="text-xs text-etest-subtext mb-1">Action</p>
            <p className="text-sm font-semibold text-etest-text">
              {digest?.priorityAction || 'Duy trì lịch học đều mỗi ngày'}
            </p>
          </div>
          <div className="bg-etest-bg-secondary rounded-2xl p-5">
            <p className="text-xs text-etest-subtext mb-1">Deadline</p>
            <p className="text-sm font-semibold text-etest-text">
              {digest?.nextDeadlineLabel || digest?.nextDeadline || `${digest?.daysLeft ?? 0} ngày tới`}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-2xl border border-etest-border/30 p-4">
            <p className="text-xs text-etest-subtext">Milestones đạt được</p>
            <p className="text-2xl font-bold text-etest-text mt-1">{digest?.milestonesCompleted ?? 0}</p>
          </div>
          <div className="rounded-2xl border border-etest-border/30 p-4">
            <p className="text-xs text-etest-subtext">Ngày còn lại</p>
            <p className="text-2xl font-bold text-etest-text mt-1">{digest?.daysLeft ?? 0}</p>
          </div>
          <div className="rounded-2xl border border-etest-border/30 p-4">
            <p className="text-xs text-etest-subtext">Kỹ năng cần cải thiện</p>
            <p className="text-xl font-bold text-etest-text mt-1">{digest?.weakestSkill || 'Đang cập nhật'}</p>
          </div>
        </div>
      </section>

      {programCards.length > 0 && (
        <section className="bg-white rounded-3xl border border-etest-border/20 shadow-card p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-etest-teal to-etest-teal-dark flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-etest-text">Gợi ý chương trình phù hợp</h3>
              <p className="text-sm text-etest-subtext">Đề xuất theo điểm yếu và mốc thời gian hiện tại</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {programCards.map((item) => (
              <button
                key={item.title}
                onClick={() => navigate(item.path)}
                className="group text-left rounded-2xl overflow-hidden border border-etest-border/20 hover:shadow-lg transition-all"
              >
                <div className={`h-2 bg-gradient-to-r ${item.gradient}`} />
                <div className="p-5">
                  <div className="inline-flex px-2 py-1 rounded-full text-xs font-semibold bg-etest-bg-secondary text-etest-subtext">
                    {item.tag}
                  </div>
                  <h4 className="text-base font-bold text-etest-text mt-3 min-h-[48px]">{item.title}</h4>
                  <p className="text-sm text-etest-subtext mt-2 min-h-[60px]">{item.reason}</p>
                  <div className="mt-4 inline-flex items-center gap-2 text-etest-teal font-semibold text-sm group-hover:gap-3 transition-all">
                    {item.cta}
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
