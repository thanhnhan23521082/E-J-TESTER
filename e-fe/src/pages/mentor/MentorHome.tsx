import { MOCK_MENTOR, MOCK_STUDENT } from '../../data/mock'
import ActionCards from '../../components/mentor/ActionCards'
import QuickContributeBar from '../../components/mentor/QuickContributeBar'
import StudentCard from '../../components/mentor/StudentCard'
import { useNavigate } from 'react-router-dom'

export default function MentorHome() {
  const navigate = useNavigate()
  const student = MOCK_STUDENT

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-etest-text">
          Xin chào, {MOCK_MENTOR.name}
        </h1>
        <p className="text-sm text-etest-subtext mt-1">
          Tổng quan hoạt động hôm nay
        </p>
      </div>

      <ActionCards
        pendingEssays={MOCK_MENTOR.pendingEssayCount}
        pendingNotes={MOCK_MENTOR.pendingSessionNoteCount}
        verifiedCount={12}
        onEssayClick={() => navigate('/mentor/review')}
        onNotesClick={() => navigate('/mentor/contribute')}
      />

      <QuickContributeBar
        onActionClick={(action) => {
          if (action === 'Review essay') {
            navigate('/mentor/review')
          } else {
            navigate('/mentor/contribute')
          }
        }}
      />

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-etest-text">Học viên của bạn</h2>
          <button
            onClick={() => navigate('/mentor/students')}
            className="text-sm text-etest-teal font-medium hover:text-etest-teal-dark"
          >
            Xem tất cả
          </button>
        </div>
        <StudentCard student={student} />
      </div>
    </div>
  )
}
