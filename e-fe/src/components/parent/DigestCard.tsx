import { Target, Clock, AlertCircle, TrendingUp } from 'lucide-react'
import type { DigestData } from '../../types'

interface DigestCardProps {
  digest: DigestData
}

export default function DigestCard({ digest }: DigestCardProps) {
  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-etest-text">Tiến độ tổng thể</span>
          <span className="text-sm font-bold text-etest-teal">{digest.progressPct}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-etest-teal rounded-full transition-all duration-500"
            style={{ width: `${digest.progressPct}%` }}
          />
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-etest-gray-card rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-4 h-4 text-etest-teal" />
            <span className="text-xs text-etest-subtext">Milestone</span>
          </div>
          <span className="text-xl font-bold text-etest-text">
            {digest.milestonesCompleted}
          </span>
        </div>
        <div className="bg-etest-gray-card rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-4 h-4 text-etest-amber" />
            <span className="text-xs text-etest-subtext">Deadline gần nhất</span>
          </div>
          <span className="text-xl font-bold text-etest-text">{digest.daysLeft}</span>
          <span className="text-xs text-etest-subtext"> ngày</span>
        </div>
      </div>

      {/* Priority action */}
      <div className="bg-etest-amber-bg rounded-lg p-3">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-etest-amber mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs font-semibold text-etest-amber mb-1">Ưu tiên hàng đầu</p>
            <p className="text-sm text-etest-text">{digest.priorityAction}</p>
          </div>
        </div>
      </div>

      {/* Weakest skill */}
      <div className="flex items-center gap-2">
        <TrendingUp className="w-4 h-4 text-etest-red" />
        <span className="text-sm text-etest-subtext">Cần cải thiện:</span>
        <span className="text-sm font-semibold text-etest-red">{digest.weakestSkill}</span>
      </div>
    </div>
  )
}
