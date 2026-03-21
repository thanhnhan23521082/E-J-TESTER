import { useState } from 'react'
import { MOCK_MILESTONES } from '../../data/mock'
import MilestoneTimeline from '../../components/shared/MilestoneTimeline'
import { Filter } from 'lucide-react'

type FilterType = 'all' | 'academic' | 'essay' | 'activity' | 'verified'

const filterOptions: { value: FilterType; label: string }[] = [
  { value: 'all', label: 'Tất cả' },
  { value: 'academic', label: 'Học tập' },
  { value: 'essay', label: 'Bài luận' },
  { value: 'activity', label: 'Hoạt động' },
  { value: 'verified', label: 'Đã xác nhận' },
]

export default function StudentTimeline() {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')

  const filteredMilestones = MOCK_MILESTONES.filter((m) => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'academic')
      return ['mock_test', 'readiness', 'outcome_record'].includes(m.type)
    if (activeFilter === 'essay')
      return ['essay_review', 'essay_draft'].includes(m.type)
    if (activeFilter === 'activity') return ['camp', 'csr', 'other'].includes(m.type)
    if (activeFilter === 'verified') return m.mentorApproved
    return true
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-etest-text">Cột mốc Thành tựu</h1>
            <p className="text-sm text-etest-subtext mt-1">
              {MOCK_MILESTONES.length} thành tựu đã ghi nhận
            </p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-etest-bg-secondary flex items-center justify-center">
            <Filter className="w-6 h-6 text-etest-teal" />
          </div>
        </div>
      </section>

      {/* Filter Pills */}
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
        {filterOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => setActiveFilter(option.value)}
            className={`flex-shrink-0 px-5 py-2.5 text-sm font-semibold rounded-full border transition-all ${
              activeFilter === option.value
                ? 'bg-etest-teal text-white border-etest-teal shadow-sm'
                : 'bg-white text-etest-subtext border-etest-border/40 hover:border-etest-teal hover:text-etest-teal'
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {/* Timeline Content */}
      <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
        {filteredMilestones.length > 0 ? (
          <MilestoneTimeline milestones={filteredMilestones} activeFilter={activeFilter} />
        ) : (
          <div className="text-center py-16">
            <div className="w-16 h-16 rounded-full bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
              <Filter className="w-8 h-8 text-etest-hint" />
            </div>
            <p className="text-etest-subtext font-medium">Không có thành tựu nào trong danh mục này</p>
            <p className="text-sm text-etest-hint mt-1">Thử chọn bộ lọc khác</p>
          </div>
        )}
      </div>
    </div>
  )
}
