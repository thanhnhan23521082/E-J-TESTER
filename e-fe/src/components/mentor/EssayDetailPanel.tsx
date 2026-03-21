import { useState } from 'react'
import { X, Check, MessageSquare } from 'lucide-react'
import type { Milestone, AuthenticityResult } from '../../types'
import AuthenticityCard from './AuthenticityCard'
import { formatDate } from '../../utils/formatDate'

interface EssayDetailPanelProps {
  essay: Milestone
  authResult: AuthenticityResult
  onClose: () => void
  onApprove: (essayId: string) => void
}

export default function EssayDetailPanel({
  essay,
  authResult,
  onClose,
  onApprove,
}: EssayDetailPanelProps) {
  const [feedback, setFeedback] = useState('')
  const [approveState, setApproveState] = useState<'idle' | 'loading' | 'success'>('idle')

  const handleApprove = async () => {
    setApproveState('loading')
    await new Promise((resolve) => setTimeout(resolve, 1200))
    setApproveState('success')
    onApprove(essay.id)
    setTimeout(() => setApproveState('idle'), 3000)
  }

  return (
    <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-end">
      <div className="w-full max-w-xl h-full bg-white shadow-xl overflow-y-auto animate-slideDown">
        <div className="sticky top-0 bg-white border-b border-etest-border p-4 flex items-center justify-between z-10">
          <h2 className="font-bold text-etest-text">Chi tiết essay</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-etest-gray-card rounded-lg transition-colors"
            aria-label="Đóng"
          >
            <X className="w-5 h-5 text-etest-subtext" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <h3 className="font-semibold text-etest-text mb-1">{essay.title}</h3>
            <p className="text-sm text-etest-subtext">{formatDate(essay.date)}</p>
          </div>

          <div className="bg-etest-gray-card rounded-lg p-4">
            <p className="text-sm text-etest-text leading-relaxed whitespace-pre-wrap">
              {essay.notes || 'Không có nội dung'}
            </p>
          </div>

          <AuthenticityCard result={authResult} />

          {essay.aiSummary.summary && (
            <div className="bg-etest-teal-light/50 rounded-lg p-4">
              <p className="text-xs font-semibold text-etest-teal mb-1">Tóm tắt AI</p>
              <p className="text-sm text-etest-text">{essay.aiSummary.summary}</p>
              {essay.aiSummary.skillsDemonstrated.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {essay.aiSummary.skillsDemonstrated.map((skill, index) => (
                    <span
                      key={index}
                      className="text-xs px-2 py-0.5 bg-white rounded-full text-etest-teal border border-etest-teal-border"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-etest-text mb-2">
              <MessageSquare className="w-4 h-4 inline mr-1" />
              Ghi chú cho học viên
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-etest-border rounded-lg text-sm focus:ring-2 focus:ring-etest-teal focus:outline-none resize-none"
              placeholder="Nhập phản hồi cho học viên..."
            />
          </div>

          <div className="flex gap-3 pt-4 border-t border-etest-border">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-etest-border rounded-lg text-sm font-medium text-etest-subtext hover:bg-etest-gray-card transition-colors"
            >
              Hủy
            </button>
            <button
              onClick={handleApprove}
              disabled={approveState !== 'idle'}
              className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-bold transition-all ${
                approveState === 'success'
                  ? 'bg-etest-green text-white'
                  : approveState === 'loading'
                  ? 'bg-etest-teal/70 text-white cursor-wait'
                  : 'bg-etest-teal text-white hover:bg-etest-teal-dark'
              }`}
            >
              {approveState === 'success' ? (
                <span className="flex items-center justify-center gap-1">
                  <Check className="w-4 h-4" /> Đã cập nhật
                </span>
              ) : approveState === 'loading' ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Đang xử lý...
                </span>
              ) : (
                'Xác nhận & Cập nhật ETESTER'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
