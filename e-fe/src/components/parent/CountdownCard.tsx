import { Clock, MapPin } from 'lucide-react'
import type { TargetSchool } from '../../types'

interface CountdownCardProps {
  school: TargetSchool
}

export default function CountdownCard({ school }: CountdownCardProps) {
  const isEligible = school.isEligible
  const showGap = !isEligible && school.gapIelts > 0

  return (
    <div className="bg-white rounded-2xl p-4 border border-etest-border/40 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <MapPin className="w-4 h-4 text-etest-subtext flex-shrink-0" />
            <span className="text-sm text-etest-subtext">{school.country}</span>
          </div>
          <h3 className="font-semibold text-etest-text truncate">{school.name}</h3>
        </div>
        <div
          className={`flex flex-col items-center px-3 py-2 rounded-lg ${
            isEligible ? 'bg-etest-green-bg' : 'bg-etest-amber-bg'
          }`}
        >
          <span
            className={`text-2xl font-bold ${
              isEligible ? 'text-etest-green' : 'text-etest-amber'
            }`}
          >
            {school.daysUntilDeadline}
          </span>
          <span className="text-xs text-etest-subtext">ngày</span>
        </div>
      </div>

      {showGap && (
        <div className="flex items-center gap-2 text-sm">
          <Clock className="w-4 h-4 text-etest-amber" />
          <span className="text-etest-subtext">Cần thêm</span>
          <span className="font-semibold text-etest-amber">
            {school.gapIelts} band IELTS
          </span>
        </div>
      )}

      {isEligible && (
        <div className="flex items-center gap-2 text-sm text-etest-green">
          <Clock className="w-4 h-4" />
          <span className="font-medium">Đã đủ điều kiện nộp hồ sơ</span>
        </div>
      )}
    </div>
  )
}
