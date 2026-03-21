import { Plus, FileText, Edit3, Trophy } from 'lucide-react'

interface QuickAction {
  icon: typeof FileText
  label: string
  onClick?: () => void
}

const quickActions: QuickAction[] = [
  { icon: FileText, label: 'Ghi chú session' },
  { icon: Edit3, label: 'Review essay' },
  { icon: Trophy, label: 'Ghi nhận milestone' },
]

interface QuickContributeBarProps {
  onActionClick?: (action: string) => void
}

export default function QuickContributeBar({ onActionClick }: QuickContributeBarProps) {
  return (
    <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4">
      <div className="flex items-center gap-2 mb-3">
        <Plus className="w-4 h-4 text-etest-teal" />
        <span className="text-sm font-semibold text-etest-text">Đóng góp nhanh</span>
      </div>
      <div className="flex gap-2">
        {quickActions.map((action, index) => {
          const Icon = action.icon
          return (
            <button
              key={index}
              onClick={() => onActionClick?.(action.label)}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-etest-teal-light text-etest-teal text-xs font-medium rounded-lg hover:bg-etest-teal hover:text-white transition-colors"
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{action.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
