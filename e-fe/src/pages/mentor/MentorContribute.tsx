import { useState } from 'react'
import { ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import ContributionTypeGrid from '../../components/mentor/ContributionTypeGrid'
import type { ContributionType } from '../../types'

export default function MentorContribute() {
  const navigate = useNavigate()
  const [selectedType, setSelectedType] = useState<ContributionType | null>(null)
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!selectedType || !notes.trim()) return

    setIsSubmitting(true)
    await new Promise((resolve) => setTimeout(resolve, 1200))
    setIsSubmitting(false)
    setSelectedType(null)
    setNotes('')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-etest-gray-card rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-etest-subtext" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-etest-text">Nộp đánh giá</h1>
          <p className="text-sm text-etest-subtext">
            Ghi nhận đóng góp cho học viên
          </p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-etest-text mb-2">
          Loại đóng góp
        </label>
        <ContributionTypeGrid selected={selectedType} onSelect={setSelectedType} />
      </div>

      {selectedType && (
        <div className="space-y-4 animate-slideDown">
          <div>
            <label className="block text-sm font-medium text-etest-text mb-2">
              Nội dung
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-etest-border rounded-lg text-sm focus:ring-2 focus:ring-etest-teal focus:outline-none resize-none"
              placeholder="Mô tả chi tiết đóng góp này..."
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setSelectedType(null)}
              className="flex-1 px-4 py-2.5 border border-etest-border rounded-lg text-sm font-medium text-etest-subtext hover:bg-etest-gray-card transition-colors"
            >
              Hủy
            </button>
            <button
              onClick={handleSubmit}
              disabled={!notes.trim() || isSubmitting}
              className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-bold transition-all ${
                isSubmitting
                  ? 'bg-etest-teal/70 text-white cursor-wait'
                  : notes.trim()
                  ? 'bg-etest-teal text-white hover:bg-etest-teal-dark'
                  : 'bg-etest-gray-card text-etest-hint cursor-not-allowed'
              }`}
            >
              {isSubmitting ? 'Đang lưu...' : 'Lưu đóng góp'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
