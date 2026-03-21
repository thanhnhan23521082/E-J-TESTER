interface QuickChatBarProps {
  suggestions: string[]
  onSelect: (text: string) => void
}

export default function QuickChatBar({ suggestions, onSelect }: QuickChatBarProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onSelect(suggestion)}
          className="flex-shrink-0 px-3 py-1.5 bg-etest-teal-light text-etest-teal text-xs font-medium rounded-full border border-etest-teal-border hover:bg-etest-teal hover:text-white transition-colors"
        >
          {suggestion}
        </button>
      ))}
    </div>
  )
}
