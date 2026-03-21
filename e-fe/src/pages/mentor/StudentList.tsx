import { useState } from 'react'
import { Search } from 'lucide-react'
import { MOCK_STUDENT } from '../../data/mock'
import StudentTableRow from '../../components/mentor/StudentTableRow'
import StudentCard from '../../components/mentor/StudentCard'

export default function StudentList() {
  const [searchQuery, setSearchQuery] = useState('')
  const students = [MOCK_STUDENT]

  const filteredStudents = students.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-etest-text">Danh sách học viên</h1>
        <p className="text-sm text-etest-subtext mt-1">
          {students.length} học viên đang theo dõi
        </p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-etest-hint" />
        <input
          type="text"
          placeholder="Tìm kiếm học viên..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-etest-border rounded-lg text-sm focus:ring-2 focus:ring-etest-teal focus:outline-none"
        />
      </div>

      {/* Desktop table view */}
      <div className="hidden lg:block bg-white rounded-2xl border border-etest-border/40 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-etest-gray-card border-b border-etest-border">
            <tr>
              <th className="text-left py-3 px-4 text-xs font-semibold text-etest-subtext uppercase tracking-wider">
                Học viên
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-etest-subtext uppercase tracking-wider">
                IELTS
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-etest-subtext uppercase tracking-wider">
                SAT
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-etest-subtext uppercase tracking-wider">
                GPA
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-etest-subtext uppercase tracking-wider">
                Kỹ năng
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-etest-subtext uppercase tracking-wider">
                Mục tiêu
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map((student) => (
              <StudentTableRow key={student.id} student={student} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile card view */}
      <div className="lg:hidden space-y-3">
        {filteredStudents.map((student) => (
          <StudentCard key={student.id} student={student} />
        ))}
      </div>

      {filteredStudents.length === 0 && (
        <div className="text-center py-12">
          <p className="text-etest-subtext">Không tìm thấy học viên nào</p>
        </div>
      )}
    </div>
  )
}
