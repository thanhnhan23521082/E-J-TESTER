import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Users,
  Heart,
  Mic,
  MessageSquare,
  ClipboardCheck,
  Sparkles,
  ChevronRight,
  TrendingUp,
  X,
  Plus,
} from 'lucide-react'
import type { ActivityType, DifficultyLevel } from '../../types'
import TraceLinkSuggestions from '../../components/etester/TraceLinkSuggestions'

const ACTIVITY_TYPES: { type: ActivityType; label: string; icon: typeof FileText }[] = [
  { type: 'mock_test', label: 'Mock test', icon: ClipboardCheck },
  { type: 'essay_draft', label: 'Essay / Draft', icon: FileText },
  { type: 'camp', label: 'Camp / Workshop', icon: Users },
  { type: 'csr', label: 'Community service', icon: Heart },
  { type: 'mentor_session', label: 'Mentor session', icon: Mic },
  { type: 'consultation', label: 'Consultation', icon: MessageSquare },
]

const SKILLS = ['Writing', 'Critical thinking', 'Leadership', 'Research', 'Public speaking', 'Time management']

const DIFFICULTIES: { level: DifficultyLevel; label: string }[] = [
  { level: 'easy', label: 'Dễ' },
  { level: 'medium', label: 'Trung bình' },
  { level: 'hard', label: 'Khó' },
]

export default function ArtifactForm() {
  const navigate = useNavigate()
  const [selectedType, setSelectedType] = useState<ActivityType>('essay_draft')
  const [selectedSkills, setSelectedSkills] = useState<string[]>(['Critical thinking'])
  const [difficulty, setDifficulty] = useState<DifficultyLevel>('medium')
  const [note, setNote] = useState('')
  const [showTraceLinkModal, setShowTraceLinkModal] = useState(false)

  const toggleSkill = (skill: string) => {
    setSelectedSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setShowTraceLinkModal(true)
  }

  return (
    <>
      <div className="space-y-8">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-2 text-xs font-medium text-etest-hint">
          <button onClick={() => navigate('/student')} className="hover:text-etest-red">Trang chủ</button>
          <ChevronRight className="w-3 h-3" />
          <button onClick={() => navigate('/student/contribute')} className="hover:text-etest-red">Nộp đóng góp</button>
          <ChevronRight className="w-3 h-3" />
          <span className="text-etest-text">Ghi nhận hoạt động</span>
        </nav>

        {/* Form Container */}
        <div className="bg-white rounded-[2rem] p-10 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-etest-red/5 rounded-full -mr-32 -mt-32 blur-3xl" />

          <header className="mb-12 relative z-10">
            <h1 className="text-3xl font-extrabold text-etest-text tracking-tight">
              Ghi nhận hoạt động học tập
            </h1>
            <p className="text-etest-hint mt-2 font-medium">
              Lưu lại hành trình rèn luyện và phát triển của bạn tại Academic Atelier.
            </p>
          </header>

          <form onSubmit={handleSubmit} className="space-y-12 relative z-10">
            {/* Section 1: Activity Type */}
            <section>
              <h3 className="text-sm font-bold uppercase tracking-widest text-etest-red mb-6">
                1. Loại hình hoạt động
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {ACTIVITY_TYPES.map(item => {
                  const isSelected = selectedType === item.type
                  return (
                    <label key={item.type} className="group relative cursor-pointer">
                      <input
                        type="radio"
                        name="activity"
                        className="peer sr-only"
                        checked={isSelected}
                        onChange={() => setSelectedType(item.type)}
                      />
                      <div className={`p-5 rounded-2xl transition-all flex items-center gap-4 ${
                        isSelected
                          ? 'bg-etest-pink-light border border-etest-red/20'
                          : 'bg-etest-bg border border-transparent hover:bg-etest-surface-high'
                      }`}>
                        <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center text-etest-red shadow-sm">
                          <item.icon className="w-5 h-5" />
                        </div>
                        <span className={`font-bold ${isSelected ? 'text-etest-red' : 'text-etest-text'}`}>
                          {item.label}
                        </span>
                      </div>
                      {isSelected && (
                        <div className="absolute -top-2 -right-2 bg-etest-red text-white w-6 h-6 rounded-full flex items-center justify-center shadow-lg">
                          <span className="text-xs">✓</span>
                        </div>
                      )}
                    </label>
                  )
                })}
              </div>
            </section>

            {/* Section 2: Skills & Section 3: Level */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              <section>
                <h3 className="text-sm font-bold uppercase tracking-widest text-etest-red mb-6">
                  2. Kỹ năng rèn luyện
                </h3>
                <div className="flex flex-wrap gap-3">
                  {SKILLS.map(skill => {
                    const isSelected = selectedSkills.includes(skill)
                    return (
                      <button
                        key={skill}
                        type="button"
                        onClick={() => toggleSkill(skill)}
                        className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${
                          isSelected
                            ? 'bg-etest-red text-white shadow-md'
                            : 'bg-etest-surface-container text-etest-text hover:bg-etest-surface-highest'
                        }`}
                      >
                        {isSelected && <span className="mr-1">✕</span>}
                        {skill}
                      </button>
                    )
                  })}
                </div>
              </section>

              <section>
                <h3 className="text-sm font-bold uppercase tracking-widest text-etest-red mb-6">
                  3. Chỉ số cấp độ
                </h3>
                <div className="bg-etest-bg p-6 rounded-2xl">
                  <div className="flex justify-between items-end mb-4">
                    <div>
                      <p className="text-xs text-etest-hint font-bold uppercase tracking-tighter">Cấp độ hiện tại</p>
                      <p className="text-xl font-black text-etest-text">
                        Áp dụng <span className="text-etest-red">(3/6)</span>
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-etest-red" />
                  </div>
                  <div className="h-3 w-full bg-etest-surface-highest rounded-full overflow-hidden flex">
                    <div className="h-full btn-primary w-1/2 rounded-full" />
                  </div>
                  <div className="flex justify-between mt-2 text-[10px] font-bold text-etest-hint">
                    <span>KHỞI ĐẦU</span>
                    <span>THÀNH THẠO</span>
                  </div>
                </div>
              </section>
            </div>

            {/* Section 4: Difficulty */}
            <section>
              <h3 className="text-sm font-bold uppercase tracking-widest text-etest-red mb-6">
                4. Mức độ thử thách
              </h3>
              <div className="flex gap-4">
                {DIFFICULTIES.map(d => (
                  <label key={d.level} className="flex-1 cursor-pointer">
                    <input
                      type="radio"
                      name="difficulty"
                      className="peer sr-only"
                      checked={difficulty === d.level}
                      onChange={() => setDifficulty(d.level)}
                    />
                    <div className={`py-4 text-center rounded-xl font-bold transition-all ${
                      difficulty === d.level
                        ? 'btn-primary text-white shadow-lg'
                        : 'bg-etest-bg border border-transparent text-etest-subtext hover:bg-etest-surface-high'
                    }`}>
                      {d.label}
                    </div>
                  </label>
                ))}
              </div>
            </section>

            {/* Section 5: AI Smart Link */}
            <section className="p-6 bg-etest-blue/5 rounded-2xl border border-etest-blue/10">
              <div className="flex items-center gap-3 mb-6">
                <Sparkles className="w-5 h-5 text-etest-blue" />
                <h3 className="text-sm font-bold uppercase tracking-widest text-etest-blue">
                  5. AI Gợi ý liên kết hoạt động
                </h3>
              </div>
              <div className="space-y-3">
                <label className="flex items-center gap-4 p-4 bg-white rounded-xl border border-transparent hover:border-etest-blue/30 cursor-pointer transition-all">
                  <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-etest-blue-light text-etest-blue focus:ring-etest-blue" />
                  <div className="flex-1">
                    <p className="text-sm font-bold text-etest-text">Writing Camp - July 2025</p>
                    <p className="text-xs text-etest-hint">Workshop chuyên sâu về học thuật</p>
                  </div>
                  <span className="px-2 py-1 bg-etest-blue-light text-etest-blue-dark text-[10px] font-bold rounded">
                    PHÙ HỢP 95%
                  </span>
                </label>
                <label className="flex items-center gap-4 p-4 bg-white rounded-xl border border-transparent hover:border-etest-blue/30 cursor-pointer transition-all">
                  <input type="checkbox" className="w-5 h-5 rounded border-etest-blue-light text-etest-blue focus:ring-etest-blue" />
                  <div className="flex-1">
                    <p className="text-sm font-bold text-etest-text">Mentor Session - Oct 2025</p>
                    <p className="text-xs text-etest-hint">Buổi tư vấn cá nhân cùng Chuyên gia</p>
                  </div>
                </label>
              </div>
            </section>

            {/* Section 6: Quick Note */}
            <section>
              <h3 className="text-sm font-bold uppercase tracking-widest text-etest-red mb-6">
                6. Ghi chú nhanh (Quick Note)
              </h3>
              <div className="relative">
                <textarea
                  value={note}
                  onChange={e => setNote(e.target.value)}
                  className="w-full h-32 p-5 bg-white border-none ring-1 ring-etest-border/20 rounded-2xl focus:ring-2 focus:ring-etest-red focus:outline-none text-etest-text font-medium resize-none"
                  placeholder="Bạn đã học được gì từ hoạt động này?..."
                />
                <div className="absolute bottom-4 right-4 text-[10px] font-bold text-etest-hint">
                  {note.split(/\s+/).filter(Boolean).length} / 250 WORDS
                </div>
              </div>
            </section>

            {/* Submit */}
            <div className="pt-8 flex justify-end">
              <button
                type="submit"
                className="btn-primary text-white px-10 py-5 rounded-2xl font-black shadow-xl shadow-etest-red/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-3"
              >
                <Plus className="w-5 h-5" />
                Thêm vào ETESTER
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* TraceLinkSuggestions Modal */}
      {showTraceLinkModal && (
        <TraceLinkSuggestions onClose={() => setShowTraceLinkModal(false)} />
      )}
    </>
  )
}
