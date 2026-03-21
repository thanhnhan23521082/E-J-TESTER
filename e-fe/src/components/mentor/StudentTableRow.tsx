import { ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import type { Student } from '../../types'

interface StudentTableRowProps {
  student: Student
}

export default function StudentTableRow({ student }: StudentTableRowProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate(`/mentor/etester/${student.id}`)
  }

  return (
    <tr
      onClick={handleClick}
      className="border-b border-etest-border hover:bg-etest-gray-card cursor-pointer transition-colors"
    >
      <td className="py-3 px-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-etest-teal-light flex items-center justify-center">
            <span className="text-sm font-semibold text-etest-teal">
              {student.name
                .split(' ')
                .map((n) => n[0])
                .join('')
                .slice(0, 2)}
            </span>
          </div>
          <div>
            <p className="font-medium text-etest-text">{student.name}</p>
            <p className="text-xs text-etest-subtext">
              {student.program} • {student.monthsEnrolled} tháng
            </p>
          </div>
        </div>
      </td>
      <td className="py-3 px-4">
        <span className="font-semibold text-etest-text">
          {student.ieltsScore.toFixed(1)}
        </span>
      </td>
      <td className="py-3 px-4">
        <span className="font-semibold text-etest-text">
          {student.satScore ?? '—'}
        </span>
      </td>
      <td className="py-3 px-4">
        <span className="font-semibold text-etest-text">
          {student.gpa.toFixed(1)}
        </span>
      </td>
      <td className="py-3 px-4">
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
      </td>
      <td className="py-3 px-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-etest-subtext">
            {student.targetSchools.length} trường
          </span>
          <ChevronRight className="w-4 h-4 text-etest-subtext" />
        </div>
      </td>
    </tr>
  )
}
