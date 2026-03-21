import { useState } from 'react'
import { MOCK_MILESTONES } from '../../data/mock'
import EssayListItem from '../../components/mentor/EssayListItem'
import EssayDetailPanel from '../../components/mentor/EssayDetailPanel'
import type { Milestone, AuthenticityResult } from '../../types'

const mockAuthResult: AuthenticityResult = {
  authScore: 91,
  confidence: 94,
  consistentPatterns: [
    'Giọng văn cá nhân nhất quán với các bài trước',
    'Cấu trúc câu và từ vựng đặc trưng',
    'Phong cách viết phản biện tương tự',
  ],
  divergentPatterns: ['Một số đoạn có độ dài bất thường'],
  recommendation: 'Bài viết thể hiện giọng văn cá nhân rõ ràng. Khuyến nghị xác nhận.',
}

export default function EssayReview() {
  const [selectedEssay, setSelectedEssay] = useState<Milestone | null>(null)
  const pendingEssays = MOCK_MILESTONES.filter(
    (m) => m.type === 'essay_review' && m.mentorApproved
  )

  const handleApprove = (essayId: string) => {
    console.log('Approved essay:', essayId)
    setSelectedEssay(null)
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-etest-text">Duyệt essay</h1>
        <p className="text-sm text-etest-subtext mt-1">
          {pendingEssays.length} essay chờ xem xét
        </p>
      </div>

      <div className="space-y-3">
        {pendingEssays.map((essay) => (
          <EssayListItem
            key={essay.id}
            essay={essay}
            onClick={() => setSelectedEssay(essay)}
          />
        ))}
      </div>

      {pendingEssays.length === 0 && (
        <div className="text-center py-12 bg-white rounded-2xl border border-etest-border/40 shadow-sm">
          <p className="text-etest-subtext">Không có essay nào chờ duyệt</p>
        </div>
      )}

      {selectedEssay && (
        <EssayDetailPanel
          essay={selectedEssay}
          authResult={mockAuthResult}
          onClose={() => setSelectedEssay(null)}
          onApprove={handleApprove}
        />
      )}
    </div>
  )
}
