import { Calendar, Award, FileCheck, TrendingUp, ChevronRight, Clock, CheckCircle, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useStudentData } from '../../hooks/useStudentData'
import EtesterSeal from '../../components/shared/EtesterSeal'

export default function StudentHome() {
  const navigate = useNavigate()
  const { student, etester, milestones, loading, error } = useStudentData()

  const recentMilestones = (milestones || []).slice(0, 3)

  const upcomingDeadlines = [
    { id: 1, title: 'Essay Common App', due: '3 ngày', type: 'essay' },
    { id: 2, title: 'Điểm thi thử IELTS', due: '1 tuần', type: 'test' },
    { id: 3, title: 'Hoạt động CSR', due: '2 tuần', type: 'activity' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-8 h-8 text-etest-teal animate-spin" />
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
        <div className="text-center">
          <div className="text-etest-subtext text-lg font-semibold mb-2">
            Chưa có hồ sơ học viên
          </div>
          <div className="text-etest-hint text-sm">
            Tài khoản của bạn chưa được liên kết với hồ sơ học viên nào.
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-12">
      {/* Hero Header Section */}
      <section className="bg-white rounded-3xl border border-etest-border/40 p-8 shadow-sm flex items-center gap-8">
        {/* Avatar with Badge */}
        <div className="relative flex-shrink-0">
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-etest-teal to-etest-teal-dark flex items-center justify-center">
            <span className="text-4xl font-bold text-white">
              {student.name.split(' ').pop()?.charAt(0)}
            </span>
          </div>
          {/* Badge */}
          {etester && (
            <div className="absolute -bottom-1 -right-1 bg-etest-red text-white text-[10px] font-bold px-3 py-1 rounded-full shadow-sm">
              Level {etester.academicScore}
            </div>
          )}
        </div>

        {/* User Info */}
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-etest-text">
            Xin chào, {student.name.split(' ').pop()}
          </h1>
          <p className="text-sm text-etest-subtext mt-1">
            {student.program} • {student.monthsEnrolled} tháng học
          </p>

          {/* Quick Stats */}
          {etester && (
            <div className="flex gap-4 mt-6">
              <div className="bg-etest-bg-secondary rounded-2xl px-6 py-4">
                <p className="text-3xl font-bold text-etest-teal">{etester.totalContributions}</p>
                <p className="text-xs text-etest-subtext mt-1">Đóng góp</p>
              </div>
              <div className="bg-amber-100 rounded-2xl px-6 py-4">
                <p className="text-3xl font-bold text-amber-600">{etester.mentorVerifications}</p>
                <p className="text-xs text-etest-subtext mt-1">Đã xác nhận</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Quick Stats Row */}
      <section className="grid grid-cols-4 gap-4">
        <div className="bg-etest-bg-secondary rounded-3xl p-6">
          <div className="flex justify-between items-start mb-6">
            <div className="w-10 h-10 rounded-xl bg-white/50 flex items-center justify-center">
              <Award className="w-5 h-5 text-etest-teal" />
            </div>
          </div>
          <p className="text-3xl font-bold text-etest-text">{student.ieltsScore.toFixed(1)}</p>
          <p className="text-sm text-etest-subtext mt-1">IELTS hiện tại</p>
        </div>

        <div className="bg-etest-bg-secondary rounded-3xl p-6">
          <div className="flex justify-between items-start mb-6">
            <div className="w-10 h-10 rounded-xl bg-white/50 flex items-center justify-center">
              <FileCheck className="w-5 h-5 text-etest-teal" />
            </div>
          </div>
          <p className="text-3xl font-bold text-etest-text">{student.satScore ?? '—'}</p>
          <p className="text-sm text-etest-subtext mt-1">Điểm SAT</p>
        </div>

        <div className="bg-etest-bg-secondary rounded-3xl p-6">
          <div className="flex justify-between items-start mb-6">
            <div className="w-10 h-10 rounded-xl bg-white/50 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-etest-teal" />
            </div>
          </div>
          <p className="text-3xl font-bold text-etest-text">{etester?.totalContributions ?? 0}</p>
          <p className="text-sm text-etest-subtext mt-1">Đóng góp</p>
        </div>

        <div className="bg-etest-red rounded-3xl p-6 shadow-button relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-etest-red to-red-500 opacity-50" />
          <div className="relative z-10">
            <div className="flex justify-between items-start mb-6">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-3xl font-bold text-white">15</p>
            <p className="text-sm text-white/80 mt-1">Ngày đến hạn</p>
          </div>
        </div>
      </section>

      {/* Main Bento Grid Layout */}
      <section className="grid grid-cols-12 gap-8">
        {/* Left Column */}
        <div className="col-span-8 space-y-8">
          {/* Contribution Grid Card */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-etest-text">Lưới đóng góp</h2>
              <button className="text-sm text-etest-teal font-medium hover:underline flex items-center gap-1">
                Chi tiết <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Contribution Grid Visualization */}
            <div className="grid grid-cols-12 gap-1.5">
              {Array.from({ length: 48 }).map((_, i) => {
                const level = Math.floor(Math.random() * 4)
                return (
                  <div
                    key={i}
                    className={`w-4 h-4 rounded-sm ${
                      level === 0
                        ? 'bg-etest-border/20'
                        : level === 1
                        ? 'bg-etest-teal/25'
                        : level === 2
                        ? 'bg-etest-teal/50'
                        : 'bg-etest-teal'
                    }`}
                  />
                )
              })}
            </div>

            {/* Legend */}
            <div className="flex items-center gap-2 mt-4 text-xs text-etest-subtext">
              <span>Ít</span>
              <div className="flex gap-1">
                <div className="w-3 h-3 rounded-sm bg-etest-border/20" />
                <div className="w-3 h-3 rounded-sm bg-etest-teal/25" />
                <div className="w-3 h-3 rounded-sm bg-etest-teal/50" />
                <div className="w-3 h-3 rounded-sm bg-etest-teal" />
              </div>
              <span>Nhiều</span>
            </div>
          </div>

          {/* ETESTER Snapshot Card */}
          {etester && (
            <div className="bg-etest-bg-secondary rounded-3xl p-8">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-lg font-bold text-etest-text">ETESTER Snapshot</h2>
                <EtesterSeal verified={etester.badgeIssued} size="sm" />
              </div>

              <div className="grid grid-cols-3 gap-6">
                <div>
                  <p className="text-3xl font-bold text-etest-teal">{etester.consistencyScore}%</p>
                  <p className="text-sm text-etest-subtext mt-1">Độ nhất quán</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-etest-text">{etester.skills.length}</p>
                  <p className="text-sm text-etest-subtext mt-1">Kỹ năng</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-etest-green">{etester.mentorVerifications}</p>
                  <p className="text-sm text-etest-subtext mt-1">Xác nhận mentor</p>
                </div>
              </div>

              <button
                onClick={() => navigate('/student/etester')}
                className="w-full mt-6 py-3 border border-etest-teal text-etest-teal font-semibold rounded-xl hover:bg-etest-teal-light transition-colors"
              >
                Xem ETESTER đầy đủ
              </button>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="col-span-4 space-y-8">
          {/* Next Deadlines Card */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <h2 className="text-lg font-bold text-etest-text mb-6">Deadline tới</h2>

            <div className="space-y-4">
              {upcomingDeadlines.map((deadline) => (
                <div
                  key={deadline.id}
                  className="flex items-center gap-3 p-3 bg-etest-bg rounded-xl"
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    deadline.type === 'essay' ? 'bg-violet-100' :
                    deadline.type === 'test' ? 'bg-blue-100' : 'bg-green-100'
                  }`}>
                    <Clock className={`w-5 h-5 ${
                      deadline.type === 'essay' ? 'text-violet-600' :
                      deadline.type === 'test' ? 'text-blue-600' : 'text-green-600'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-etest-text truncate">{deadline.title}</p>
                    <p className="text-xs text-etest-subtext">Còn {deadline.due}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Milestones */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-etest-text">Thành tựu gần đây</h2>
              <button
                onClick={() => navigate('/student/timeline')}
                className="text-sm text-etest-teal font-medium hover:underline"
              >
                Xem tất cả
              </button>
            </div>

            <div className="space-y-3">
              {recentMilestones.length > 0 ? (
                recentMilestones.map((milestone) => (
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
                ))
              ) : (
                <p className="text-sm text-etest-hint text-center py-4">
                  Chưa có thành tựu nào
                </p>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
