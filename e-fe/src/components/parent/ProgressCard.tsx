import { TrendingUp, TrendingDown } from 'lucide-react'

interface ProgressCardProps {
  currentScore: number
  previousScore: number
  skill: string
}

export default function ProgressCard({ currentScore, previousScore, skill }: ProgressCardProps) {
  const change = currentScore - previousScore
  const isImprovement = change > 0

  return (
    <div className="bg-white rounded-2xl p-4 border border-etest-border/40 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-etest-subtext mb-1">{skill}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-etest-text">{currentScore}</span>
            <span className="text-sm text-etest-subtext">trước đó {previousScore}</span>
          </div>
        </div>
        <div
          className={`flex items-center gap-1 px-3 py-1.5 rounded-full ${
            isImprovement ? 'bg-etest-green-bg text-etest-green' : 'bg-etest-red-light text-etest-red'
          }`}
        >
          {isImprovement ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span className="text-sm font-semibold">
            {isImprovement ? '+' : ''}
            {change.toFixed(1)}
          </span>
        </div>
      </div>
    </div>
  )
}
