import { ShieldCheck } from 'lucide-react'

interface EtesterSealProps {
  size?: 'sm' | 'md' | 'lg'
  verified?: boolean
}

export default function EtesterSeal({ size = 'md', verified = true }: EtesterSealProps) {
  const sizes = {
    sm: { container: 'w-12 h-12', icon: 'w-6 h-6', text: 'text-[8px]' },
    md: { container: 'w-20 h-20', icon: 'w-10 h-10', text: 'text-[10px]' },
    lg: { container: 'w-32 h-32', icon: 'w-16 h-16', text: 'text-xs' },
  }

  const { container, icon, text } = sizes[size]

  return (
    <div
      className={`${container} rounded-full flex flex-col items-center justify-center ${
        verified
          ? 'bg-gradient-to-br from-etest-teal to-etest-teal-dark text-white'
          : 'bg-gray-200 text-etest-hint'
      } shadow-lg`}
    >
      <ShieldCheck className={icon} />
      <span className={`${text} font-bold mt-0.5`}>ETESTER</span>
    </div>
  )
}
