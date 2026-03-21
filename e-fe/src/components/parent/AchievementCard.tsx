import { Award, ShieldCheck } from 'lucide-react'
import type { Milestone } from '../../types'
import { formatDate } from '../../utils/formatDate'

interface AchievementCardProps {
  milestone: Milestone
}

export default function AchievementCard({ milestone }: AchievementCardProps) {
  return (
    <div className="bg-gradient-to-br from-etest-teal-light to-white rounded-2xl p-4 border border-etest-teal-border shadow-sm">
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 bg-etest-teal rounded-xl flex items-center justify-center flex-shrink-0">
          <Award className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-etest-teal font-semibold uppercase tracking-wide">
              Thành tựu mới
            </span>
            {milestone.mentorApproved && (
              <ShieldCheck className="w-4 h-4 text-etest-teal" />
            )}
          </div>
          <h3 className="font-semibold text-etest-text">{milestone.title}</h3>
          <p className="text-sm text-etest-subtext mt-1">
            {formatDate(milestone.date)}
            {milestone.scoreLabel && ` • ${milestone.scoreLabel}`}
          </p>
        </div>
      </div>

      {milestone.aiSummary.summary && (
        <p className="text-sm text-etest-subtext mt-3 pl-15">
          {milestone.aiSummary.summary}
        </p>
      )}
    </div>
  )
}
