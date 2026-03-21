import { useState } from 'react'
import { X, CheckCircle, MessageSquare, ArrowDown, Link2 } from 'lucide-react'
import type { TraceLink, TraceLinkType } from '../../types'

interface MentorTraceReviewProps {
  traceLink: TraceLink
  studentName: string
  onApprove: (id: string, comment: string, linkType: TraceLinkType) => void
  onReject: (id: string) => void
}

const LINK_TYPE_OPTIONS: { value: TraceLinkType; label: string }[] = [
  { value: 'experience_source', label: 'experience source' },
  { value: 'revision_of', label: 'revision of' },
  { value: 'mentor_guided', label: 'mentor guided' },
  { value: 'skill_applied', label: 'skill applied' },
]

export default function MentorTraceReview({ traceLink, studentName, onApprove, onReject }: MentorTraceReviewProps) {
  const [linkType, setLinkType] = useState<TraceLinkType>(traceLink.linkType)
  const [comment, setComment] = useState('')

  return (
    <div className="w-full max-w-[420px] bg-white rounded-xl border border-etest-border/10 shadow-[0_12px_32px_rgba(187,0,22,0.04)] overflow-hidden flex flex-col">
      {/* Card Header */}
      <div className="px-6 pt-6 pb-4 flex justify-between items-start">
        <div>
          <h2 className="font-bold text-lg text-etest-text leading-tight">{studentName}</h2>
          <p className="text-xs text-etest-subtext mt-1">submitted 2 ngày trước</p>
        </div>
        <div className="bg-etest-bg-secondary p-2 rounded-lg">
          <Link2 className="w-5 h-5 text-etest-red" />
        </div>
      </div>

      {/* Connection Display */}
      <div className="px-6 py-4 bg-etest-bg-secondary/50 relative flex flex-col items-center gap-3">
        {/* Source Artifact */}
        <div className="w-full bg-teal-50 border-l-4 border-teal-600 rounded-lg p-3 flex justify-between items-center">
          <div>
            <div className="text-[10px] uppercase font-bold text-teal-800 tracking-wider">Source</div>
            <div className="font-semibold text-sm text-teal-900">{traceLink.sourceTitle.split(' — ')[0]}</div>
          </div>
          <div className="text-xs font-medium text-teal-700">
            {new Date(traceLink.sourceDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
          </div>
        </div>

        {/* Arrow Label */}
        <div className="flex flex-col items-center -my-1 z-10">
          <div className="bg-white border border-etest-border/20 px-3 py-0.5 rounded-full flex items-center shadow-sm">
            <Link2 className="w-3 h-3 mr-1.5 text-etest-subtext" />
            <span className="text-[10px] font-bold text-etest-subtext uppercase tracking-tighter">
              {traceLink.linkType.replace(/_/g, ' ')}
            </span>
          </div>
          <div className="h-4 w-px bg-etest-border/30" />
          <ArrowDown className="w-4 h-4 text-etest-border -mt-1" />
        </div>

        {/* Target Artifact */}
        <div className="w-full bg-amber-50 border-l-4 border-amber-400 rounded-lg p-3 flex justify-between items-center">
          <div>
            <div className="text-[10px] uppercase font-bold text-amber-800 tracking-wider">Target</div>
            <div className="font-semibold text-sm text-etest-gold">{traceLink.targetTitle.split(' — ')[0]}</div>
          </div>
          <div className="text-xs font-medium text-amber-700">
            {new Date(traceLink.targetDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
          </div>
        </div>
      </div>

      {/* AI Evidence */}
      <div className="px-6 py-4 border-b border-etest-border/5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-bold text-etest-subtext uppercase tracking-wider">AI detected:</span>
          <div className="flex items-center">
            <span className="text-[11px] font-bold text-emerald-600 mr-2">{traceLink.confidence}% Confidence</span>
            <div className="w-12 h-1.5 bg-etest-surface-container rounded-full overflow-hidden">
              <div className="bg-emerald-500 h-full" style={{ width: `${traceLink.confidence}%` }} />
            </div>
          </div>
        </div>
        <p className="text-sm text-etest-text/80 leading-relaxed italic">
          "{traceLink.aiReason}"
        </p>
      </div>

      {/* Student Note */}
      {traceLink.studentNote && (
        <div className="px-6 py-4 bg-etest-blue/5 border-y border-etest-blue/10">
          <div className="flex items-center gap-2 mb-2">
            <MessageSquare className="w-4 h-4 text-etest-blue" />
            <span className="text-[11px] font-bold text-etest-blue uppercase tracking-wider">Ghi chú từ học sinh:</span>
          </div>
          <div className="pl-2 border-l-2 border-etest-blue/30">
            <p className="text-sm font-medium text-etest-blue-dark italic leading-snug">
              "{traceLink.studentNote}"
            </p>
          </div>
        </div>
      )}

      {/* Relationship Selection */}
      <div className="px-6 py-5 space-y-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-bold text-etest-subtext uppercase tracking-wider">Loại liên kết:</label>
          <select
            value={linkType}
            onChange={e => setLinkType(e.target.value as TraceLinkType)}
            className="w-full h-11 bg-white border border-etest-border/30 rounded-lg pl-3 pr-10 text-sm font-medium focus:ring-1 focus:ring-etest-red/20 focus:border-etest-red transition-all"
          >
            {LINK_TYPE_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-bold text-etest-subtext uppercase tracking-wider">Nhận xét của Mentor:</label>
          <textarea
            value={comment}
            onChange={e => setComment(e.target.value)}
            className="w-full bg-etest-bg-secondary border-none rounded-lg p-3 text-sm focus:ring-1 focus:ring-etest-red/20 placeholder:text-etest-hint/50 resize-none transition-all"
            placeholder="Thêm nhận xét (không bắt buộc)..."
            rows={2}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="px-6 pb-6 pt-2 flex gap-3">
        <button
          onClick={() => onReject(traceLink.id)}
          className="flex-1 h-12 border border-red-400 text-red-500 font-bold rounded-xl text-sm hover:bg-red-50 active:scale-95 transition-all flex items-center justify-center gap-2"
        >
          <X className="w-4 h-4" /> Từ chối
        </button>
        <button
          onClick={() => onApprove(traceLink.id, comment, linkType)}
          className="flex-[1.5] h-12 btn-primary text-white font-bold rounded-xl text-sm shadow-md hover:shadow-lg active:scale-95 transition-all flex items-center justify-center gap-2"
        >
          <CheckCircle className="w-4 h-4" /> Xác nhận liên kết
        </button>
      </div>
    </div>
  )
}
