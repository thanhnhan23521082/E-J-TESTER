import { AlertTriangle, MessageCircle } from 'lucide-react'

interface AlertCardProps {
  severity: 'high' | 'medium'
  message: string
  action: string
  onChatOpen: () => void
}

export default function AlertCard({ severity, message, action, onChatOpen }: AlertCardProps) {
  const isHigh = severity === 'high'

  return (
    <div
      className={`rounded-2xl p-4 animate-slideDown ${
        isHigh
          ? 'bg-etest-red-light border border-red-200 border-l-4 border-l-etest-red'
          : 'bg-etest-amber-bg border border-amber-200 border-l-4 border-l-etest-amber'
      }`}
    >
      <div className="flex items-start gap-3">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
            isHigh ? 'bg-etest-red' : 'bg-etest-amber'
          }`}
        >
          <AlertTriangle className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[15px] font-bold text-etest-text">
            {isHigh ? 'Cảnh báo quan trọng' : 'Lưu ý'}
          </p>
          <p className="text-[14px] text-etest-subtext leading-relaxed mt-1">
            {message}
          </p>
          <button
            onClick={onChatOpen}
            className={`w-full h-11 mt-3 text-white text-[14px] font-bold rounded-[10px] flex items-center justify-center gap-2 transition-colors ${
              isHigh
                ? 'bg-etest-red hover:bg-etest-red-dark'
                : 'bg-etest-amber hover:bg-etest-amber/90'
            }`}
          >
            <MessageCircle className="w-4 h-4" />
            {action}
          </button>
        </div>
      </div>
    </div>
  )
}
