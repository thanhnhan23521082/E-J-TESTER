export function formatScore(score: number | null, label: string = ''): string {
  if (score === null) return label || '-'
  if (label) return label
  return score.toString()
}

export function getScoreColor(score: number, maxScore: number = 9): string {
  const ratio = score / maxScore
  if (ratio >= 0.8) return 'text-etest-green'
  if (ratio >= 0.6) return 'text-etest-teal'
  if (ratio >= 0.4) return 'text-etest-amber'
  return 'text-etest-red'
}

export function getScoreBgColor(score: number, maxScore: number = 9): string {
  const ratio = score / maxScore
  if (ratio >= 0.8) return 'bg-etest-green-bg'
  if (ratio >= 0.6) return 'bg-etest-teal-light'
  if (ratio >= 0.4) return 'bg-etest-amber-bg'
  return 'bg-etest-red-light'
}

export function calculateGap(current: number, required: number): number {
  return Math.max(0, required - current)
}

export function isEligible(current: number, required: number): boolean {
  return current >= required
}
