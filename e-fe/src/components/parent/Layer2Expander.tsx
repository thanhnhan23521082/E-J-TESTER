import { useState, type ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'

interface Layer2ExpanderProps {
  title: string
  children: ReactNode
}

export default function Layer2Expander({ title, children }: Layer2ExpanderProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left"
        aria-expanded={isOpen}
      >
        <span className="font-semibold text-etest-text">{title}</span>
        <ChevronDown
          className={`w-5 h-5 text-etest-subtext transition-transform duration-250 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      <div
        className={`transition-all duration-300 ease-out ${
          isOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
        }`}
      >
        <div className="px-4 pb-4">{children}</div>
      </div>
    </div>
  )
}
