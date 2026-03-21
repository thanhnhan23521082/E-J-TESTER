import { Target, Clock, CheckCircle, TrendingUp, Award, BookOpen } from 'lucide-react'
import { useStudentData } from '../../hooks/useStudentData'
import MilestoneTimeline from '../../components/shared/MilestoneTimeline'
import { formatDate } from '../../utils/formatDate'

export default function StudentProgress() {
  const { student, milestones } = useStudentData()

  if (!student) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-2 border-etest-teal border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Student Info Header */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-etest-red to-etest-red-secondary flex items-center justify-center shadow-lg">
            <span className="text-xl font-bold text-white">
              {student.name.split(' ').map((n) => n[0]).join('').slice(-2)}
            </span>
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-etest-text">{student.name}</h2>
            <p className="text-sm text-etest-subtext mt-0.5">
              Chương trình {student.program} • {student.monthsEnrolled} tháng
            </p>
          </div>
        </div>

        {/* Score Summary Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-etest-bg-secondary rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-lg bg-white/50 flex items-center justify-center">
                <Award className="w-4 h-4 text-etest-teal" />
              </div>
              <span className="text-xs text-etest-subtext">IELTS</span>
            </div>
            <p className="text-3xl font-bold text-etest-teal">{student.ieltsScore.toFixed(1)}</p>
          </div>
          <div className="bg-etest-bg-secondary rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-lg bg-white/50 flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-etest-teal" />
              </div>
              <span className="text-xs text-etest-subtext">GPA</span>
            </div>
            <p className="text-3xl font-bold text-etest-teal">{student.gpa.toFixed(1)}</p>
          </div>
        </div>
      </section>

      {/* Target Schools */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-etest-red-light flex items-center justify-center">
            <Target className="w-5 h-5 text-etest-red" />
          </div>
          <h3 className="text-base font-bold text-etest-text">Trường mục tiêu</h3>
        </div>
        <div className="space-y-3">
          {student.targetSchools.map((school, index) => (
            <div
              key={index}
              className={`p-4 rounded-2xl border-2 transition-colors ${
                school.isEligible
                  ? 'bg-etest-green-bg border-etest-green/30'
                  : 'bg-etest-bg border-etest-border/30'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-etest-text truncate">{school.name}</p>
                  <p className="text-xs text-etest-subtext mt-1">
                    Deadline: {formatDate(school.deadline)} • {school.country}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {school.isEligible ? (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-etest-green rounded-full">
                      <CheckCircle className="w-4 h-4 text-white" />
                      <span className="text-xs font-bold text-white">Đủ điều kiện</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-etest-amber-bg rounded-full">
                      <Clock className="w-4 h-4 text-etest-amber" />
                      <span className="text-xs font-bold text-etest-amber">{school.daysUntilDeadline} ngày</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* IELTS Skills Breakdown */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-etest-teal-light flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-etest-teal" />
          </div>
          <h3 className="text-base font-bold text-etest-text">Kỹ năng IELTS</h3>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {Object.entries(student.skillBreakdown).map(([skill, score]) => (
            <div key={skill} className="bg-etest-bg rounded-2xl p-3 text-center">
              <p className="text-xs text-etest-subtext mb-1">{skill}</p>
              <p className="text-2xl font-bold text-etest-text">{score}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Milestone Timeline */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <h3 className="text-base font-bold text-etest-text mb-4">Timeline hoạt động</h3>
        <MilestoneTimeline milestones={milestones} activeFilter="all" />
      </section>
    </div>
  )
}
