import { ShieldCheck, FileText, Award, Clock } from 'lucide-react'
import type { Milestone } from '../../types'
import { formatDate } from '../../utils/formatDate'

interface MilestoneTimelineProps {
  milestones: Milestone[]
  activeFilter?: 'all' | 'academic' | 'essay' | 'activity' | 'verified'
  showMentorActions?: boolean
  onApprove?: (milestoneId: string) => void
}

const contributorColors: Record<string, string> = {
  student: 'bg-blue-500',
  mentor: 'bg-etest-teal',
  parent: 'bg-purple-500',
  institution: 'bg-etest-amber',
}

export default function MilestoneTimeline({
  milestones,
  activeFilter = 'all',
  showMentorActions = false,
  onApprove,
}: MilestoneTimelineProps) {
  const filteredMilestones = milestones.filter((m) => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'verified') return m.mentorApproved
    if (activeFilter === 'academic') return ['mock_test', 'readiness'].includes(m.type)
    if (activeFilter === 'essay') return ['essay_review', 'essay_draft'].includes(m.type)
    if (activeFilter === 'activity') return ['csr', 'camp'].includes(m.type)
    return true
  })

  const getIcon = (type: string) => {
    switch (type) {
      case 'essay_review':
      case 'essay_draft':
        return FileText
      case 'mock_test':
      case 'readiness':
        return Clock
      default:
        return Award
    }
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-[17px] top-0 bottom-0 w-px border-l-2 border-dashed border-etest-border" />

      <div className="space-y-4">
        {filteredMilestones.map((milestone, index) => {
          const Icon = getIcon(milestone.type)
          const dotColor = contributorColors[milestone.contributorType]

          return (
            <div
              key={milestone.id}
              className="relative pl-10 animate-slideUp"
              style={{ animationDelay: `${index * 80}ms` }}
            >
              {/* Dot */}
              <div
                className={`absolute left-2 top-1 w-4 h-4 rounded-full ${dotColor} border-2 border-white shadow-sm z-10`}
              />

              {/* Content card */}
              <div className="bg-etest-gray-card rounded-lg p-3 border border-etest-border">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-etest-subtext" />
                    <span className="text-sm font-medium text-etest-text">
                      {milestone.title}
                    </span>
                  </div>
                  {milestone.mentorApproved && (
                    <ShieldCheck className="w-4 h-4 text-etest-teal flex-shrink-0" />
                  )}
                </div>

                <div className="flex items-center gap-3 text-xs text-etest-subtext">
                  <span>{formatDate(milestone.date)}</span>
                  {milestone.scoreLabel && (
                    <span className="font-semibold text-etest-teal">
                      {milestone.scoreLabel}
                    </span>
                  )}
                  {milestone.authScore !== null && (
                    <span className="text-etest-green">
                      Auth: {milestone.authScore}%
                    </span>
                  )}
                </div>

                {milestone.aiSummary.summary && (
                  <p className="text-xs text-etest-subtext mt-2 line-clamp-2">
                    {milestone.aiSummary.summary}
                  </p>
                )}

                {showMentorActions && !milestone.mentorApproved && onApprove && (
                  <button
                    onClick={() => onApprove(milestone.id)}
                    className="mt-2 text-xs font-semibold text-etest-teal hover:text-etest-teal-dark"
                  >
                    Xác nhận đóng góp này
                  </button>
                )}
              </div>
            </div>
          )
        })}

        {filteredMilestones.length === 0 && (
          <div className="text-center py-8 text-etest-subtext text-sm">
            Không có hoạt động nào
          </div>
        )}
      </div>
    </div>
  )
}
