import { FileText, Edit3, CheckSquare, BarChart2, BadgeCheck, Trophy } from 'lucide-react'
import type { ContributionType } from '../../types'

interface ContributionOption {
  type: ContributionType
  label: string
  icon: typeof FileText
}

const OPTIONS: ContributionOption[] = [
  { type: 'session_notes', label: 'Ghi chú session', icon: FileText },
  { type: 'essay_review', label: 'Essay review', icon: Edit3 },
  { type: 'readiness', label: 'Readiness assessment', icon: CheckSquare },
  { type: 'mock_review', label: 'Nhận xét bài thi thử', icon: BarChart2 },
  { type: 'program_verify', label: 'Xác nhận chương trình', icon: BadgeCheck },
  { type: 'outcome_record', label: 'Kết quả đậu trường', icon: Trophy },
]

interface ContributionTypeGridProps {
  selected: ContributionType | null
  onSelect: (type: ContributionType) => void
}

export default function ContributionTypeGrid({
  selected,
  onSelect,
}: ContributionTypeGridProps) {
  return (
    <div className="grid grid-cols-3 gap-2.5">
      {OPTIONS.map((option) => {
        const isSelected = selected === option.type
        const Icon = option.icon

        return (
          <button
            key={option.type}
            onClick={() => onSelect(option.type)}
            className={`flex flex-col items-center justify-center p-3 rounded-2xl border transition-all ${
              isSelected
                ? 'border-2 border-etest-teal bg-etest-teal-light'
                : 'border border-etest-border bg-white hover:border-etest-teal-border'
            }`}
          >
            <Icon
              className={`w-6 h-6 mb-1.5 ${
                isSelected ? 'text-etest-teal' : 'text-etest-subtext'
              }`}
            />
            <span
              className={`text-xs font-medium text-center ${
                isSelected ? 'text-etest-teal' : 'text-etest-text'
              }`}
            >
              {option.label}
            </span>
          </button>
        )
      })}
    </div>
  )
}
