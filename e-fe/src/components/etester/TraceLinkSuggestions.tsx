import { useState } from 'react'
import { X, Lightbulb, ArrowRight, GraduationCap, Users, FileText } from 'lucide-react'
import type { TraceLinkType } from '../../types'

interface Suggestion {
  id: string
  title: string
  type: TraceLinkType
  confidence: number
  aiReason: string
  icon: typeof GraduationCap
  colorClass: string
  badgeBg: string
  badgeText: string
}

const MOCK_SUGGESTIONS: Suggestion[] = [
  {
    id: 's1',
    title: 'Writing Camp — Jul 2025',
    type: 'experience_source',
    confidence: 94,
    aiReason: '"Essay references thesis workshop from Writing Camp in paragraph 2"',
    icon: GraduationCap,
    colorClass: 'text-etest-blue',
    badgeBg: 'bg-etest-blue-light text-etest-blue-dark',
    badgeText: 'experience source',
  },
  {
    id: 's2',
    title: 'Mentor Session #5 — Oct 2025',
    type: 'mentor_guided',
    confidence: 88,
    aiReason: '"Vocabulary choices align with suggestions made during this session."',
    icon: Users,
    colorClass: 'text-etest-gold',
    badgeBg: 'bg-etest-gold-light text-etest-gold-dark',
    badgeText: 'mentor guided',
  },
  {
    id: 's3',
    title: 'Essay Draft #1 — Oct 2025',
    type: 'revision_of',
    confidence: 98,
    aiReason: '"Direct structural overlap with previous draft."',
    icon: FileText,
    colorClass: 'text-etest-red',
    badgeBg: 'bg-etest-pink-light text-etest-red',
    badgeText: 'revision of',
  },
]

interface TraceLinkSuggestionsProps {
  onClose: () => void
}

export default function TraceLinkSuggestions({ onClose }: TraceLinkSuggestionsProps) {
  const [notes, setNotes] = useState<Record<string, string>>({})

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-etest-text/40 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] relative z-10">
        {/* Header */}
        <div className="px-8 pt-8 pb-6 bg-etest-bg-secondary/30">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-2xl font-bold text-etest-text">
              AI found {MOCK_SUGGESTIONS.length} possible connections
            </h3>
            <button
              onClick={onClose}
              className="p-1 hover:bg-etest-surface-high rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-etest-subtext" />
            </button>
          </div>
          <p className="text-etest-subtext text-sm leading-relaxed max-w-lg">
            These are suggestions only — your mentor will verify them. Add a note if you want to provide context.
          </p>
        </div>

        {/* Suggestion Cards */}
        <div className="px-8 py-4 overflow-y-auto space-y-4 flex-1">
          {MOCK_SUGGESTIONS.map(suggestion => (
            <div
              key={suggestion.id}
              className="bg-etest-bg border border-etest-border/10 rounded-xl p-5 hover:bg-white transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full ${suggestion.id === 's1' ? 'bg-etest-blue-light' : suggestion.id === 's2' ? 'bg-etest-gold-light' : 'bg-etest-pink-light'} flex items-center justify-center`}>
                    <suggestion.icon className={`w-5 h-5 ${suggestion.colorClass}`} />
                  </div>
                  <div>
                    <h4 className="font-bold text-etest-text">{suggestion.title}</h4>
                    <span className={`inline-block px-2 py-0.5 ${suggestion.badgeBg} text-[10px] font-bold uppercase tracking-wider rounded-full mt-0.5`}>
                      {suggestion.badgeText}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-etest-subtext">Confidence</span>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="w-16 h-1.5 bg-etest-surface-high rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${suggestion.id === 's1' ? 'bg-etest-blue' : suggestion.id === 's2' ? 'bg-etest-gold' : 'bg-etest-red'}`}
                        style={{ width: `${suggestion.confidence}%` }}
                      />
                    </div>
                    <span className={`text-xs font-bold ${suggestion.colorClass}`}>
                      {suggestion.confidence}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-etest-bg-secondary p-3 rounded-lg flex gap-3 items-start mb-4">
                <Lightbulb className={`w-4 h-4 mt-0.5 flex-shrink-0 ${suggestion.colorClass}`} />
                <p className="text-xs text-etest-subtext italic leading-relaxed">
                  {suggestion.aiReason}
                </p>
              </div>

              <textarea
                value={notes[suggestion.id] || ''}
                onChange={e => setNotes(prev => ({ ...prev, [suggestion.id]: e.target.value }))}
                className="w-full bg-white border-none ring-1 ring-etest-border/20 rounded-lg p-3 text-sm focus:ring-etest-red/40 focus:ring-2 transition-all min-h-[80px] placeholder:text-etest-hint/40"
                placeholder="e.g. I used PEEL method I learned here..."
              />
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-8 py-6 border-t border-etest-surface-high bg-etest-bg-secondary/10 flex items-center justify-between">
          <p className="text-[11px] text-etest-subtext max-w-[200px] leading-tight font-medium opacity-70">
            You are not confirming these — your mentor will review and confirm or reject each connection.
          </p>
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl border border-etest-border/30 text-etest-text font-semibold text-sm hover:bg-etest-surface-container transition-all"
            >
              Skip — send without notes
            </button>
            <button
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl btn-primary text-white font-semibold text-sm shadow-md hover:shadow-etest-red/20 transition-all flex items-center gap-2 group"
            >
              Send to mentor
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
