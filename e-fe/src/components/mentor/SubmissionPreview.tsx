import { FileText, Calendar, Clock } from 'lucide-react'
import { formatDate } from '../../utils/formatDate'

interface SubmissionPreviewProps {
  title: string
  type: string
  submittedAt: string
  wordCount: number
  preview: string
  onClick?: () => void
}

export default function SubmissionPreview({
  title,
  type,
  submittedAt,
  wordCount,
  preview,
  onClick,
}: SubmissionPreviewProps) {
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4 ${
        onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
    >
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-lg bg-etest-teal-light flex items-center justify-center flex-shrink-0">
          <FileText className="w-5 h-5 text-etest-teal" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-etest-text text-sm truncate">{title}</h4>
          <p className="text-xs text-etest-subtext">{type}</p>
        </div>
      </div>

      <p className="text-sm text-etest-subtext line-clamp-3 mb-3">{preview}</p>

      <div className="flex items-center gap-4 text-xs text-etest-hint">
        <div className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5" />
          <span>{formatDate(submittedAt)}</span>
        </div>
        <div className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5" />
          <span>{wordCount} từ</span>
        </div>
      </div>
    </div>
  )
}
