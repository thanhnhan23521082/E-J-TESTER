import { useParams } from 'react-router-dom'
import { MOCK_STUDENT, MOCK_ETESTER, MOCK_MILESTONES } from '../../data/mock'
import EtesterSeal from '../../components/shared/EtesterSeal'
import AuthGauge from '../../components/shared/AuthGauge'
import ContributorDonut from '../../components/shared/ContributorDonut'
import MilestoneTimeline from '../../components/shared/MilestoneTimeline'

export default function MentorEtester() {
  const { studentId } = useParams()
  const student = MOCK_STUDENT
  const etester = MOCK_ETESTER
  const milestones = MOCK_MILESTONES

  if (studentId !== student.id) {
    return (
      <div className="text-center py-12">
        <p className="text-etest-subtext">Không tìm thấy học viên</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-etest-text">ETESTER của {student.name}</h1>
        <p className="text-sm text-etest-subtext mt-1">
          Hồ sơ học tập và thành tựu
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-6">
            <div className="flex items-center justify-center mb-4">
              <EtesterSeal
                verified={etester.badgeIssued}
                size="lg"
              />
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-etest-text">Điểm ETESTER</h3>
              <p className="text-3xl font-bold text-etest-teal mt-1">
                {etester.academicScore}
              </p>
              <p className="text-xs text-etest-subtext mt-1">
                Cập nhật: {new Date(etester.lastUpdated).toLocaleDateString('vi-VN')}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4">
            <h3 className="font-semibold text-etest-text mb-4">Xác thực nội dung</h3>
            <div className="flex items-center justify-center">
              <AuthGauge score={etester.consistencyScore} size="lg" />
            </div>
            <p className="text-xs text-center text-etest-subtext mt-3">
              Độ nhất quán trong giọng viết
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4">
            <h3 className="font-semibold text-etest-text mb-4">Nguồn đóng góp</h3>
            <ContributorDonut
              data={[
                { name: 'Học viên', value: etester.totalContributions - etester.mentorVerifications, color: '#3B82F6' },
                { name: 'Mentor', value: etester.mentorVerifications, color: '#0D9488' },
                ...(etester.institutionalStamp ? [{ name: 'Trường', value: 1, color: '#F59E0B' }] : []),
              ]}
            />
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4">
            <h3 className="font-semibold text-etest-text mb-3">Kỹ năng</h3>
            <div className="flex flex-wrap gap-2">
              {etester.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-etest-teal-light text-etest-teal text-sm font-medium rounded-full border border-etest-teal-border"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-etest-teal-light to-white rounded-2xl border border-etest-teal-border shadow-sm p-4">
            <h3 className="font-semibold text-etest-text mb-3">Câu chuyện học tập</h3>
            <p className="text-sm text-etest-subtext leading-relaxed whitespace-pre-line">
              {etester.narrativeCache}
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-4">
            <h3 className="font-semibold text-etest-text mb-3">Thành tựu gần đây</h3>
            <MilestoneTimeline
              milestones={milestones}
              activeFilter="all"
              showMentorActions={true}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
