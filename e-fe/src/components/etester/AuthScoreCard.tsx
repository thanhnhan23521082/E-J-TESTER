import { CheckCircle, Info, FileText, History, ArrowRight } from 'lucide-react'
import type { AuthScoreBreakdown } from '../../types'

interface AuthScoreCardProps {
  data: AuthScoreBreakdown
}

export default function AuthScoreCard({ data }: AuthScoreCardProps) {
  const circumference = 2 * Math.PI * 45
  const offset = circumference - (circumference * data.overallScore) / 100

  const verdictColors: Record<string, { bg: string; text: string }> = {
    justified_growth: { bg: 'bg-emerald-100', text: 'text-emerald-700' },
    suspicious: { bg: 'bg-red-100', text: 'text-red-700' },
    verified: { bg: 'bg-etest-blue-light', text: 'text-etest-blue' },
  }

  const colors = verdictColors[data.verdict] || verdictColors.verified

  return (
    <div className="space-y-8">
      {/* Main Card */}
      <div className="bg-white rounded-[2rem] p-10 shadow-[0_12px_32px_rgba(187,0,22,0.04)] overflow-hidden relative border border-etest-border/10">
        <div className="absolute top-0 right-0 w-32 h-32 bg-etest-red/5 rounded-bl-full -mr-10 -mt-10" />

        <header className="flex flex-col md:flex-row items-center md:items-start gap-10 mb-12">
          {/* Score Gauge */}
          <div className="relative flex-shrink-0">
            <svg className="w-40 h-40" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
              <circle cx="50" cy="50" r="45" fill="none" stroke="#e2e8f8" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="45" fill="none"
                stroke="#10b981"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-black text-etest-text">{data.overallScore}%</span>
              <span className="text-[10px] uppercase tracking-tighter font-bold text-etest-outline">Auth Score</span>
            </div>
          </div>

          {/* Summary */}
          <div className="flex-1 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-black text-etest-text tracking-tight">ETESTER AuthScoreCard</h1>
                <p className="text-etest-subtext opacity-70 text-sm">Case Reference: ET-7729-B</p>
              </div>
              <span className={`inline-flex items-center px-4 py-1.5 rounded-full ${colors.bg} ${colors.text} text-xs font-bold tracking-wide uppercase border border-current/20`}>
                {data.verdict.replace(/_/g, ' ')}
              </span>
            </div>

            <div className="p-5 bg-etest-bg-secondary rounded-2xl border-l-4 border-emerald-500">
              <p className="text-etest-text leading-relaxed text-sm italic">
                "{data.summary}"
              </p>
            </div>

            {/* Artifact Chips */}
            <div className="flex flex-wrap gap-3">
              {data.relatedArtifacts.map(name => (
                <div
                  key={name}
                  className="flex items-center gap-2 px-3 py-1.5 bg-teal-50 text-teal-800 rounded-lg text-xs font-semibold border border-teal-100"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  {name}
                </div>
              ))}
            </div>
          </div>
        </header>

        {/* Score Breakdown */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-lg text-etest-text">Score breakdown</h3>
            <span className="text-xs text-etest-outline font-medium">Detailed Dimension Analysis</span>
          </div>

          <div className="space-y-4">
            {data.dimensions.map((dim, i) => (
              <div key={dim.id} className="group">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="w-8 font-black text-xs text-etest-red">D{i + 1}</span>
                    <span className="text-sm font-medium text-etest-text">{dim.label}</span>
                    <span className="text-[10px] text-etest-outline px-1.5 py-0.5 bg-etest-surface-container rounded font-bold">
                      x{dim.weight.toFixed(2)}
                    </span>
                  </div>
                  <span className="text-sm font-bold text-etest-text">{dim.score}%</span>
                </div>
                <div className="w-full bg-etest-surface-high h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-etest-red h-full rounded-full transition-all duration-1000"
                    style={{ width: `${dim.score}%` }}
                  />
                </div>
                <p className="mt-1 text-[11px] text-etest-subtext opacity-60 ml-11">{dim.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Footer Note */}
        <footer className="mt-12 pt-8 border-t border-etest-border/10 flex items-center gap-3 text-etest-subtext/60">
          <Info className="w-4 h-4" />
          <p className="text-xs font-medium tracking-tight">Analysis uses full artifact graph context, not just text comparison.</p>
        </footer>
      </div>

      {/* CTA Area */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-etest-bg-secondary p-6 rounded-2xl flex items-center justify-between hover:bg-etest-surface-container transition-colors cursor-pointer group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center text-etest-red shadow-sm">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm">View Full Essay</h4>
              <p className="text-xs text-etest-outline">Annotated version with AI insights</p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-etest-outline group-hover:text-etest-red transition-colors" />
        </div>
        <div className="bg-etest-bg-secondary p-6 rounded-2xl flex items-center justify-between hover:bg-etest-surface-container transition-colors cursor-pointer group">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center text-etest-blue shadow-sm">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm">Audit Trail</h4>
              <p className="text-xs text-etest-outline">Review all 12 verification stages</p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-etest-outline group-hover:text-etest-blue transition-colors" />
        </div>
      </div>
    </div>
  )
}
