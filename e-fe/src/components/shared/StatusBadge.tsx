import type { ReactNode } from 'react'

interface StatusBadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral'
  children: ReactNode
  size?: 'sm' | 'md'
}

export default function StatusBadge({ variant, children, size = 'md' }: StatusBadgeProps) {
  const variantClasses = {
    success: 'bg-etest-green-bg text-etest-green border-etest-green/30',
    warning: 'bg-etest-amber-bg text-etest-amber border-etest-amber/30',
    error: 'bg-etest-red-light text-etest-red border-etest-red/30',
    info: 'bg-etest-teal-light text-etest-teal border-etest-teal/30',
    neutral: 'bg-gray-100 text-etest-subtext border-gray-200',
  }

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  }

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${variantClasses[variant]} ${sizeClasses[size]}`}
    >
      {children}
    </span>
  )
}
