interface SkeletonCardProps {
  lines?: number
  hasImage?: boolean
  className?: string
}

export default function SkeletonCard({ lines = 3, hasImage = false, className = '' }: SkeletonCardProps) {
  return (
    <div className={`bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4 ${className}`}>
      {hasImage && (
        <div className="w-full h-32 bg-gray-200 rounded-lg mb-4 animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]" />
      )}
      <div className="space-y-3">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className="h-4 bg-gray-200 rounded animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]"
            style={{ width: index === lines - 1 ? '60%' : '100%' }}
          />
        ))}
      </div>
    </div>
  )
}
