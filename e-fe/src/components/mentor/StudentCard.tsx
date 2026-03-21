import { ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import type { Student } from '../../types'

interface StudentCardProps {
  student: Student
}

export default function StudentCard({ student }: StudentCardProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate(`/mentor/etester/${student.id}`)
  }

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-2xl p-4 border border-etest-border/40 shadow-sm hover:shadow-md cursor-pointer transition-shadow"
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="w-12 h-12 rounded-full bg-etest-teal-light flex items-center justify-center flex-shrink-0">
          <span className="text-sm font-semibold text-etest-teal">
            {student.name
              .split(' ')
              .map((n) => n[0])
              .join('')
              .slice(0, 2)}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-etest-text truncate">{student.name}</p>
          <p className="text-xs text-etest-subtext">
            {student.program} • {student.monthsEnrolled} tháng
          </p>
        </div>
        <ChevronRight className="w-5 h-5 text-etest-subtext" />
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-etest-gray-card rounded-lg p-2 text-center">
          <p className="text-xs text-etest-subtext mb-0.5">IELTS</p>
          <p className="font-bold text-etest-text">{student.ieltsScore.toFixed(1)}</p>
        </div>
        <div className="bg-etest-gray-card rounded-lg p-2 text-center">
          <p className="text-xs text-etest-subtext mb-0.5">SAT</p>
          <p className="font-bold text-etest-text">{student.satScore ?? '—'}</p>
        </div>
        <div className="bg-etest-gray-card rounded-lg p-2 text-center">
          <p className="text-xs text-etest-subtext mb-0.5">GPA</p>
          <p className="font-bold text-etest-text">{student.gpa.toFixed(1)}</p>
        </div>
      </div>

      <div className="flex items-center gap-1 text-[11px]">
        <span
          className={`px-2 py-0.5 rounded-full ${
            student.skillBreakdown.L >= 7
              ? 'bg-etest-green-bg text-etest-green'
              : student.skillBreakdown.L >= 6
              ? 'bg-etest-teal-light text-etest-teal'
              : 'bg-etest-amber-bg text-etest-amber'
          }`}
        >
          L {student.skillBreakdown.L}
        </span>
        <span
          className={`px-2 py-0.5 rounded-full ${
            student.skillBreakdown.R >= 7
              ? 'bg-etest-green-bg text-etest-green'
              : student.skillBreakdown.R >= 6
              ? 'bg-etest-teal-light text-etest-teal'
              : 'bg-etest-amber-bg text-etest-amber'
          }`}
        >
          R {student.skillBreakdown.R}
        </span>
        <span
          className={`px-2 py-0.5 rounded-full ${
            student.skillBreakdown.W >= 7
              ? 'bg-etest-green-bg text-etest-green'
              : student.skillBreakdown.W >= 6
              ? 'bg-etest-teal-light text-etest-teal'
              : 'bg-etest-amber-bg text-etest-amber'
          }`}
        >
          W {student.skillBreakdown.W}
        </span>
        <span
          className={`px-2 py-0.5 rounded-full ${
            student.skillBreakdown.S >= 7
              ? 'bg-etest-green-bg text-etest-green'
              : student.skillBreakdown.S >= 6
              ? 'bg-etest-teal-light text-etest-teal'
              : 'bg-etest-amber-bg text-etest-amber'
          }`}
        >
          S {student.skillBreakdown.S}
        </span>
      </div>

      <div className="mt-3 pt-3 border-t border-etest-border">
        <span className="text-xs text-etest-subtext">
          {student.targetSchools.length} trường mục tiêu
        </span>
      </div>
    </div>
  )
}
