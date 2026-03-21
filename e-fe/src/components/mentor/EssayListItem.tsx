import { FileText, Clock, ChevronRight } from 'lucide-react'
import type { Milestone } from '../../types'
import { formatDate } from '../../utils/formatDate'

interface EssayListItemProps {
  essay: Milestone
  onClick?: () => void
}

export default function EssayListItem({ essay, onClick }: EssayListItemProps) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-3 p-3 bg-white rounded-2xl border border-etest-border/40 shadow-sm ${
        onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
    >
      <div className="w-10 h-10 rounded-lg bg-etest-amber-bg flex items-center justify-center flex-shrink-0">
        <FileText className="w-5 h-5 text-etest-amber" />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-etest-text text-sm truncate">{essay.title}</h4>
        <div className="flex items-center gap-2 text-xs text-etest-subtext mt-0.5">
          <Clock className="w-3 h-3" />
          <span>{formatDate(essay.date)}</span>
          {essay.authScore !== null && (
            <span
              className={`px-1.5 py-0.5 rounded ${
                essay.authScore >= 70
                  ? 'bg-etest-green-bg text-etest-green'
                  : essay.authScore >= 40
                  ? 'bg-etest-amber-bg text-etest-amber'
                  : 'bg-etest-red-light text-etest-red'
              }`}
            >
              Auth: {essay.authScore}%
            </span>
          )}
        </div>
      </div>
      <ChevronRight className="w-5 h-5 text-etest-subtext" />
    </div>
  )
}
