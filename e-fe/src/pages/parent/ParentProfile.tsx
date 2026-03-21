import { User, GraduationCap, Award, TrendingUp } from 'lucide-react'

export default function ParentProfile() {
  // Mock data for children profiles
  const children = [
    {
      id: 'std_001',
      name: 'Nguyễn Văn An',
      grade: 'Lớp 12',
      program: 'SAT Advanced',
      ieltsScore: 7.0,
      satScore: 1450,
      gpa: 3.8,
      status: 'Đang học',
      joinDate: '01/09/2024',
    },
    {
      id: 'std_002',
      name: 'Nguyễn Thị Bình',
      grade: 'Lớp 10',
      program: 'IELTS Foundation',
      ieltsScore: 5.5,
      satScore: null,
      gpa: 3.5,
      status: 'Đang học',
      joinDate: '15/10/2024',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-etest-text">Hồ sơ con</h1>
          <p className="text-sm text-etest-subtext mt-1">
            Xem thông tin và tiến độ học tập của con bạn
          </p>
        </div>
      </div>

      {/* Children Cards */}
      <div className="grid gap-6">
        {children.map((child) => (
          <div
            key={child.id}
            className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-6"
          >
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-etest-teal-light rounded-2xl flex items-center justify-center">
                  <span className="text-lg font-bold text-etest-teal">
                    {child.name.split(' ').pop()?.[0]}
                    {child.name.split(' ')[1]?.[0]}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-etest-text">{child.name}</h3>
                  <p className="text-sm text-etest-subtext">{child.grade}</p>
                </div>
              </div>
              <span className="px-3 py-1 bg-etest-green-light text-etest-green text-xs font-bold rounded-full">
                {child.status}
              </span>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-etest-bg rounded-xl p-4 text-center">
                <GraduationCap className="w-5 h-5 text-etest-teal mx-auto mb-2" />
                <p className="text-xs text-etest-subtext mb-1">Chương trình</p>
                <p className="text-sm font-semibold text-etest-text">{child.program}</p>
              </div>
              <div className="bg-etest-bg rounded-xl p-4 text-center">
                <Award className="w-5 h-5 text-etest-red mx-auto mb-2" />
                <p className="text-xs text-etest-subtext mb-1">IELTS</p>
                <p className="text-sm font-semibold text-etest-text">{child.ieltsScore.toFixed(1)}</p>
              </div>
              <div className="bg-etest-bg rounded-xl p-4 text-center">
                <TrendingUp className="w-5 h-5 text-etest-blue mx-auto mb-2" />
                <p className="text-xs text-etest-subtext mb-1">SAT</p>
                <p className="text-sm font-semibold text-etest-text">{child.satScore ?? '—'}</p>
              </div>
              <div className="bg-etest-bg rounded-xl p-4 text-center">
                <User className="w-5 h-5 text-etest-purple mx-auto mb-2" />
                <p className="text-xs text-etest-subtext mb-1">GPA</p>
                <p className="text-sm font-semibold text-etest-text">{child.gpa.toFixed(1)}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-etest-border/20">
              <p className="text-xs text-etest-hint">Ngày tham gia: {child.joinDate}</p>
              <div className="flex gap-2">
                <button className="px-4 py-2 text-sm font-semibold text-etest-teal bg-etest-teal-light rounded-xl hover:bg-etest-teal/20 transition-colors">
                  Xem ETESTER
                </button>
                <button className="px-4 py-2 text-sm font-semibold text-white bg-etest-teal rounded-xl hover:bg-etest-teal-dark transition-colors">
                  Xem tiến độ
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {children.length === 0 && (
        <div className="bg-white rounded-2xl border border-etest-border/40 shadow-sm p-12 text-center">
          <User className="w-12 h-12 text-etest-hint mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-etest-text mb-2">
            Chưa có hồ sơ con
          </h3>
          <p className="text-sm text-etest-subtext">
            Liên hệ ETEST để thêm học viên vào tài khoản phụ huynh của bạn
          </p>
        </div>
      )}
    </div>
  )
}
