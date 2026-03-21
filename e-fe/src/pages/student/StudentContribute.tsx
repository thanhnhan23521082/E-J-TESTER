import { useState } from 'react'
import { Upload, FileText, Edit3, Trophy, ArrowLeft, Check, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

type ContributionOption = {
  type: string
  label: string
  icon: typeof FileText
  description: string
  color: string
  bgColor: string
}

const OPTIONS: ContributionOption[] = [
  {
    type: 'mock_test',
    label: 'Điểm thi thử',
    icon: FileText,
    description: 'Ghi nhận điểm thi thử IELTS/SAT',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
  },
  {
    type: 'essay_draft',
    label: 'Bài luận mới',
    icon: Edit3,
    description: 'Nộp bài luận cho mentor review',
    color: 'text-violet-600',
    bgColor: 'bg-violet-100',
  },
  {
    type: 'activity',
    label: 'Hoạt động ngoại khóa',
    icon: Trophy,
    description: 'Ghi nhận hoạt động tình nguyện, CSR',
    color: 'text-etest-green',
    bgColor: 'bg-etest-green-bg',
  },
]

export default function StudentContribute() {
  const navigate = useNavigate()
  const [selectedType, setSelectedType] = useState<string | null>(null)
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

  const selectedOption = OPTIONS.find((o) => o.type === selectedType)

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="w-10 h-10 rounded-xl bg-etest-bg-secondary flex items-center justify-center hover:bg-etest-border/20 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-etest-subtext" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-etest-text">Đóng góp mới</h1>
            <p className="text-sm text-etest-subtext mt-1">
              Ghi nhận hoạt động học tập của bạn
            </p>
          </div>
        </div>
      </section>

      {/* Contribution Type Selection */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
        <h2 className="text-lg font-bold text-etest-text mb-6">Chọn loại đóng góp</h2>
        <div className="space-y-4">
          {OPTIONS.map((option) => {
            const Icon = option.icon
            const isSelected = selectedType === option.type

            return (
              <button
                key={option.type}
                onClick={() => setSelectedType(option.type)}
                className={`w-full flex items-center gap-4 p-5 rounded-2xl border-2 transition-all ${
                  isSelected
                    ? 'border-etest-teal bg-etest-teal-light'
                    : 'border-etest-border/30 bg-white hover:border-etest-teal-border hover:bg-etest-bg'
                }`}
              >
                <div
                  className={`w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'bg-etest-teal' : option.bgColor
                  }`}
                >
                  <Icon
                    className={`w-7 h-7 ${isSelected ? 'text-white' : option.color}`}
                  />
                </div>
                <div className="flex-1 text-left">
                  <p
                    className={`font-semibold ${
                      isSelected ? 'text-etest-teal' : 'text-etest-text'
                    }`}
                  >
                    {option.label}
                  </p>
                  <p className="text-sm text-etest-subtext mt-0.5">
                    {option.description}
                  </p>
                </div>
                {isSelected && (
                  <div className="w-8 h-8 rounded-full bg-etest-teal flex items-center justify-center">
                    <Check className="w-5 h-5 text-white" />
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </section>

      {/* Contribution Form */}
      {selectedType && selectedOption && (
        <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8 animate-slideDown">
          <div className="flex items-center gap-3 mb-6">
            <div className={`w-10 h-10 rounded-xl ${selectedOption.bgColor} flex items-center justify-center`}>
              <selectedOption.icon className={`w-5 h-5 ${selectedOption.color}`} />
            </div>
            <h2 className="text-lg font-bold text-etest-text">{selectedOption.label}</h2>
          </div>

          <div className="space-y-6">
            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-etest-text mb-2">
                Mô tả chi tiết
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={5}
                className="w-full px-4 py-3 border border-etest-border/40 rounded-2xl text-sm text-etest-text placeholder:text-etest-hint focus:ring-2 focus:ring-etest-teal/20 focus:border-etest-teal focus:outline-none resize-none transition-all"
                placeholder="Mô tả hoạt động của bạn..."
              />
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-semibold text-etest-text mb-2">
                Tệp đính kèm <span className="text-etest-hint font-normal">(tùy chọn)</span>
              </label>
              <div className="border-2 border-dashed border-etest-border/40 rounded-2xl p-8 text-center hover:border-etest-teal hover:bg-etest-bg/50 transition-all cursor-pointer">
                <div className="w-14 h-14 rounded-2xl bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
                  <Upload className="w-7 h-7 text-etest-hint" />
                </div>
                <p className="text-sm font-medium text-etest-text mb-1">
                  Kéo thả hoặc nhấp để tải lên
                </p>
                <p className="text-xs text-etest-hint">PDF, DOC, JPG (tối đa 10MB)</p>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={() => {
                  setSelectedType(null)
                  setNotes('')
                }}
                className="flex-1 px-6 py-3.5 border border-etest-border/40 rounded-2xl text-sm font-semibold text-etest-subtext hover:bg-etest-bg transition-colors flex items-center justify-center gap-2"
              >
                <X className="w-4 h-4" />
                Hủy
              </button>
              <button
                onClick={handleSubmit}
                disabled={!notes.trim() || isSubmitting}
                className={`flex-1 px-6 py-3.5 rounded-2xl text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                  isSubmitting
                    ? 'bg-etest-teal/70 text-white cursor-wait'
                    : notes.trim()
                    ? 'btn-primary text-white shadow-button hover:opacity-90'
                    : 'bg-etest-border/30 text-etest-hint cursor-not-allowed'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Đang gửi...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Gửi đóng góp
                  </>
                )}
              </button>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
