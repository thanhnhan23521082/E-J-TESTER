import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react'
import type { AuthenticityResult } from '../../types'

interface AuthenticityCardProps {
  result: AuthenticityResult
}

export default function AuthenticityCard({ result }: AuthenticityCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-etest-green'
    if (score >= 40) return 'text-etest-amber'
    return 'text-etest-red'
  }

  const getScoreBg = (score: number) => {
    if (score >= 70) return 'bg-etest-green-bg'
    if (score >= 40) return 'bg-etest-amber-bg'
    return 'bg-etest-red-light'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 70) return CheckCircle
    if (score >= 40) return Info
    return AlertTriangle
  }

  const ScoreIcon = getScoreIcon(result.authScore)

  return (
    <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm overflow-hidden">
      <div className="p-4 border-b border-etest-border">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-5 h-5 text-etest-teal" />
          <span className="font-semibold text-etest-text">Xác thực AI</span>
        </div>

        <div className={`${getScoreBg(result.authScore)} rounded-lg p-4`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-etest-subtext">Điểm xác thực</span>
            <div className="flex items-center gap-1">
              <ScoreIcon className={`w-5 h-5 ${getScoreColor(result.authScore)}`} />
              <span className={`text-2xl font-bold ${getScoreColor(result.authScore)}`}>
                {result.authScore}%
              </span>
            </div>
          </div>
          <div className="h-2 bg-white/50 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                result.authScore >= 70
                  ? 'bg-etest-green'
                  : result.authScore >= 40
                  ? 'bg-etest-amber'
                  : 'bg-etest-red'
              }`}
              style={{ width: `${result.authScore}%` }}
            />
          </div>
          <p className="text-xs text-etest-subtext mt-2">
            Độ tin cậy: {result.confidence}%
          </p>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {result.consistentPatterns.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-etest-green mb-1.5 flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" />
              Mẫu nhất quán
            </p>
            <ul className="space-y-1">
              {result.consistentPatterns.map((pattern, index) => (
                <li
                  key={index}
                  className="text-xs text-etest-subtext pl-5 relative before:content-['•'] before:absolute before:left-2 before:text-etest-green"
                >
                  {pattern}
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.divergentPatterns.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-etest-amber mb-1.5 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              Mẫu khác biệt
            </p>
            <ul className="space-y-1">
              {result.divergentPatterns.map((pattern, index) => (
                <li
                  key={index}
                  className="text-xs text-etest-subtext pl-5 relative before:content-['•'] before:absolute before:left-2 before:text-etest-amber"
                >
                  {pattern}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="pt-3 border-t border-etest-border">
          <p className="text-xs text-etest-subtext">
            <span className="font-medium text-etest-text">Khuyến nghị:</span>{' '}
            {result.recommendation}
          </p>
        </div>
      </div>
    </div>
  )
}
