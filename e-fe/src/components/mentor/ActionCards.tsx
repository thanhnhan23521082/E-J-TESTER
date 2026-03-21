import { FileCheck, Clock, Award } from 'lucide-react'

interface ActionCardProps {
  icon: typeof FileCheck
  label: string
  value: number | string
  color: 'teal' | 'amber' | 'green'
  onClick?: () => void
}

function ActionCard({ icon: Icon, label, value, color, onClick }: ActionCardProps) {
  const colorClasses = {
    teal: {
      bg: 'bg-etest-teal-light',
      icon: 'text-etest-teal',
      text: 'text-etest-teal',
    },
    amber: {
      bg: 'bg-etest-amber-bg',
      icon: 'text-etest-amber',
      text: 'text-etest-amber',
    },
    green: {
      bg: 'bg-etest-green-bg',
      icon: 'text-etest-green',
      text: 'text-etest-green',
    },
  }

  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-3 p-4 ${colorClasses[color].bg} rounded-2xl border border-etest-border/40 shadow-sm ${
        onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
    >
      <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
        <Icon className={`w-5 h-5 ${colorClasses[color].icon}`} />
      </div>
      <div>
        <p className="text-2xl font-bold text-etest-text">{value}</p>
        <p className="text-xs text-etest-subtext">{label}</p>
      </div>
    </div>
  )
}

interface ActionCardsProps {
  pendingEssays: number
  pendingNotes: number
  verifiedCount: number
  onEssayClick?: () => void
  onNotesClick?: () => void
}

export default function ActionCards({
  pendingEssays,
  pendingNotes,
  verifiedCount,
  onEssayClick,
  onNotesClick,
}: ActionCardsProps) {
  return (
    <div className="grid grid-cols-3 gap-3">
      <ActionCard
        icon={FileCheck}
        label="Essay chờ duyệt"
        value={pendingEssays}
        color="amber"
        onClick={onEssayClick}
      />
      <ActionCard
        icon={Clock}
        label="Ghi chú chờ"
        value={pendingNotes}
        color="teal"
        onClick={onNotesClick}
      />
      <ActionCard
        icon={Award}
        label="Đã xác nhận tháng này"
        value={verifiedCount}
        color="green"
      />
    </div>
  )
}
