import { useNavigate } from 'react-router-dom'
import { Clock, AlertTriangle, TrendingUp, Calendar, Users, Target } from 'lucide-react'
import { useStudentData } from '../../hooks/useStudentData'

export default function ParentHome() {
  const navigate = useNavigate()
  const { student, wellbeing, digest, behavioralLogs, loading, error } = useStudentData()

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

  const lateNightByDate = new Map(
    weekLogs.filter((log) => log.isLateNight).map((log) => [log.date.slice(0, 10), true])
  )
  const dayOrder = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
  const formatLocalDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  const today = new Date()
  const monday = new Date(today)
  monday.setDate(today.getDate() - ((today.getDay() + 6) % 7))
  const isUrgent = (digest?.daysLeft ?? 0) > 0 && (digest?.daysLeft ?? 0) <= 14

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
  const scoreDisplay = isSatProgram
    ? String(Math.round(currentScore))
    : currentScore.toFixed(1)
  const scoreRatio = Math.max(0, Math.min(currentScore / maxScore, 1))

  return (
    <div className="space-y-6">
      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Large Deadline Card - Left Column */}
        <div className="lg:col-span-5">
          <div className="bg-white rounded-3xl border border-etest-border/20 shadow-card p-8 h-full">
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
                <span
                  className={`text-xs font-semibold ${isUrgent ? 'text-etest-red' : 'text-etest-subtext'}`}
                >
                  {isUrgent ? 'Urgent' : 'Bình thường'}
                </span>
              </div>
            </div>

            <div className="text-center py-8">
              <div className="text-7xl font-black text-etest-text mb-2">
                {digest?.daysLeft || 0}
              </div>
              <div className="text-xl font-semibold text-etest-subtext">Ngày</div>
            </div>

            <button
              onClick={() => navigate('/parent/progress')}
              className="w-full py-4 bg-gradient-to-r from-etest-red to-etest-red-secondary text-white font-bold rounded-2xl hover:opacity-90 transition-all shadow-button"
            >
              Xem chi tiết timeline
            </button>
          </div>
        </div>

        {/* Right Column - Wellbeing Alert + Progress */}
        <div className="lg:col-span-7 space-y-6">
          {/* Wellbeing Alert Card - Medium */}
          {wellbeing?.alert && (
            <div className="bg-[#fff8e1] rounded-3xl border border-amber-200 shadow-card p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-6 h-6 text-etest-amber" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-etest-text mb-2">Cảnh báo học tập</h3>
                  <p className="text-sm text-etest-subtext mb-4">{wellbeing.message}</p>

                  {/* Day indicators */}
                  <div className="flex gap-2 mb-4">
                    {dayOrder.map((day, idx) => {
                      const date = new Date(monday)
                      date.setDate(monday.getDate() + idx)
                      const key = formatLocalDate(date)
                      const lateNight = lateNightByDate.get(key) === true

                      return (
                        <div
                          key={day}
                          className={`w-10 h-10 rounded-xl flex items-center justify-center text-xs font-semibold ${
                            lateNight
                              ? 'bg-etest-red text-white'
                              : 'bg-white text-etest-subtext border border-etest-border/30'
                          }`}
                        >
                          {day}
                        </div>
                      )
                    })}
                  </div>

                  <button
                    onClick={() => navigate('/parent/chat')}
                    className="px-6 py-2 bg-etest-amber text-white font-semibold rounded-xl hover:opacity-90 transition-all"
                  >
                    {wellbeing.action}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Progress Card - Wide */}
          <div className="bg-white rounded-3xl border border-etest-border/20 shadow-card p-8">
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

              {/* Circular Progress Indicator */}
              <div className="relative w-24 h-24">
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
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

            {/* Detailed Stats Section */}
            <div className="grid grid-cols-3 gap-6 pt-6 border-t border-etest-border/20">
              <div className="text-center">
                <div className="w-10 h-10 rounded-xl bg-etest-teal-light mx-auto mb-2 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-etest-teal" />
                </div>
                <div className="text-2xl font-bold text-etest-text mb-1">{studiedDaysPerWeek}</div>
                <div className="text-xs text-etest-subtext">Ngày/tuần</div>
              </div>

              <div className="text-center">
                <div className="w-10 h-10 rounded-xl bg-etest-amber-bg mx-auto mb-2 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-etest-amber" />
                </div>
                <div className="text-2xl font-bold text-etest-text mb-1">{avgHoursPerDay.toFixed(1)}</div>
                <div className="text-xs text-etest-subtext">Giờ/ngày</div>
              </div>

              <div className="text-center">
                <div className="w-10 h-10 rounded-xl bg-etest-green-bg mx-auto mb-2 flex items-center justify-center">
                  <Target className="w-5 h-5 text-etest-green" />
                </div>
                <div className="text-2xl font-bold text-etest-text mb-1">75-85%</div>
                <div className="text-xs text-etest-subtext">Học bổng</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Weekly Summary Section */}
      <div className="bg-white rounded-3xl border border-etest-border/20 shadow-card p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-etest-teal to-etest-teal-dark flex items-center justify-center">
            <Users className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-etest-text">Tổng quan tuần này</h3>
            <p className="text-sm text-etest-subtext">Hoạt động và tiến độ của {student.name}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-etest-bg-secondary rounded-2xl p-6">
            <div className="text-3xl font-bold text-etest-text mb-2">{digest?.progressPct || 0}%</div>
            <div className="text-sm text-etest-subtext">Tiến độ hoàn thành</div>
          </div>

          <div className="bg-etest-bg-secondary rounded-2xl p-6">
            <div className="text-3xl font-bold text-etest-text mb-2">{digest?.milestonesCompleted || 0}</div>
            <div className="text-sm text-etest-subtext">Milestones đạt được</div>
          </div>

          <div className="bg-etest-bg-secondary rounded-2xl p-6">
            <div className="text-3xl font-bold text-etest-text mb-2">{digest?.daysLeft || 0}</div>
            <div className="text-sm text-etest-subtext">Ngày còn lại</div>
          </div>
        </div>
      </div>
    </div>
  )
}
