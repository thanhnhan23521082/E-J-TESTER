import { useParams, Link } from 'react-router-dom'
import { Shield, Award, CheckCircle, ArrowLeft } from 'lucide-react'
import { MOCK_STUDENT, MOCK_ETESTER } from '../../data/mock'
import EtesterSeal from '../../components/shared/EtesterSeal'
import QrBadge from '../../components/shared/QrBadge'
import AuthGauge from '../../components/shared/AuthGauge'

export default function EtesterPublic() {
  const { studentId } = useParams()

  const student = MOCK_STUDENT
  const etester = MOCK_ETESTER

  if (studentId !== student.id) {
    return (
      <div className="min-h-screen bg-etest-gray-card flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 text-center max-w-md shadow-lg">
          <Shield className="w-16 h-16 text-etest-red mx-auto mb-4" />
          <h1 className="text-xl font-bold text-etest-text mb-2">
            Không tìm thấy hồ sơ
          </h1>
          <p className="text-sm text-etest-subtext mb-6">
            ID học viên không hợp lệ hoặc hồ sơ không tồn tại.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-etest-teal font-medium hover:text-etest-teal-dark"
          >
            <ArrowLeft className="w-4 h-4" />
            Về trang chủ
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-etest-teal-light to-white py-12 px-6">
      <div className="max-w-lg mx-auto">
        <div className="text-center mb-6">
          <Shield className="w-8 h-8 text-etest-teal mx-auto mb-2" />
          <h1 className="text-lg font-bold text-etest-text">ETESTER Verify</h1>
          <p className="text-sm text-etest-subtext">Hồ sơ học tập đã xác thực</p>
        </div>

        <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm overflow-hidden shadow-lg">
          <div className="bg-gradient-to-br from-etest-teal to-etest-teal-dark p-6 text-white text-center">
            <div className="flex justify-center mb-4">
              <EtesterSeal
                verified={etester.badgeIssued}
                size="lg"
              />
            </div>
            <h2 className="text-xl font-bold">{student.name}</h2>
            <p className="text-white/80 text-sm mt-1">
              {student.program} • {student.monthsEnrolled} tháng học
            </p>
            <div className="mt-4 flex justify-center">
              <QrBadge value={`https://etest.vn/etester/verify/${student.id}`} size={80} />
            </div>
          </div>

          <div className="p-6 space-y-4">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-etest-gray-card rounded-lg p-3">
                <p className="text-2xl font-bold text-etest-teal">
                  {student.ieltsScore.toFixed(1)}
                </p>
                <p className="text-xs text-etest-subtext">IELTS</p>
              </div>
              <div className="bg-etest-gray-card rounded-lg p-3">
                <p className="text-2xl font-bold text-etest-text">
                  {student.satScore ?? '—'}
                </p>
                <p className="text-xs text-etest-subtext">SAT</p>
              </div>
              <div className="bg-etest-gray-card rounded-lg p-3">
                <p className="text-2xl font-bold text-etest-text">
                  {student.gpa.toFixed(1)}
                </p>
                <p className="text-xs text-etest-subtext">GPA</p>
              </div>
            </div>

            <div className="bg-etest-teal-light/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-etest-text">
                  Điểm xác thực
                </span>
                <span className="text-lg font-bold text-etest-teal">
                  {etester.consistencyScore}%
                </span>
              </div>
              <div className="flex justify-center">
                <AuthGauge score={etester.consistencyScore} size="sm" />
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-etest-subtext mb-2 flex items-center gap-1">
                <Award className="w-3.5 h-3.5" />
                Kỹ năng
              </p>
              <div className="flex flex-wrap gap-1.5">
                {etester.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="text-xs px-2 py-1 bg-etest-teal-light text-etest-teal rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-etest-green pt-2 border-t border-etest-border">
              <CheckCircle className="w-4 h-4" />
              <span>Đã xác thực bởi ETEST • {etester.mentorVerifications} mentor</span>
            </div>

            <p className="text-xs text-etest-hint text-center">
              Cập nhật: {new Date(etester.lastUpdated).toLocaleDateString('vi-VN')}
            </p>
          </div>
        </div>

        <div className="text-center mt-6">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm text-etest-teal font-medium hover:text-etest-teal-dark"
          >
            <ArrowLeft className="w-4 h-4" />
            Về trang chủ ETEST ONE
          </Link>
        </div>
      </div>
    </div>
  )
}
