interface AuthGaugeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

export default function AuthGauge({ score, size = 'md' }: AuthGaugeProps) {
  const sizes = {
    sm: { width: 80, height: 44, strokeWidth: 6 },
    md: { width: 120, height: 66, strokeWidth: 8 },
    lg: { width: 160, height: 88, strokeWidth: 10 },
  }

  const { width, height, strokeWidth } = sizes[size]
  const radius = (width - strokeWidth) / 2
  const circumference = Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  // Determine color based on score
  const getColor = (value: number): string => {
    if (value >= 70) return '#10B981' // green
    if (value >= 40) return '#F59E0B' // amber
    return '#E8242A' // red
  }

  const color = getColor(score)

  return (
    <div className="relative inline-flex flex-col items-center">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth / 2} ${height - strokeWidth / 2} A ${radius} ${radius} 0 0 1 ${width - strokeWidth / 2} ${height - strokeWidth / 2}`}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Score arc */}
        <path
          d={`M ${strokeWidth / 2} ${height - strokeWidth / 2} A ${radius} ${radius} 0 0 1 ${width - strokeWidth / 2} ${height - strokeWidth / 2}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
        />
      </svg>
      {/* Score text */}
      <div className="absolute bottom-0 text-center">
        <span className="text-xl font-bold" style={{ color }}>
          {score}
        </span>
      </div>
    </div>
  )
}
