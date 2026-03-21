import { useNavigate } from 'react-router-dom'
import { Calendar, Sparkles } from 'lucide-react'
import AlertCard from '../../components/parent/AlertCard'
import CountdownCard from '../../components/parent/CountdownCard'
import ProgressCard from '../../components/parent/ProgressCard'
import AchievementCard from '../../components/parent/AchievementCard'
import DigestCard from '../../components/parent/DigestCard'
import UpsellCard from '../../components/parent/UpsellCard'
import Layer2Expander from '../../components/parent/Layer2Expander'
import { useStudentData } from '../../hooks/useStudentData'
import { MOCK_UPSELL } from '../../data/mock'

export default function ParentHome() {
  const navigate = useNavigate()
  const { student, wellbeing, digest, milestones } = useStudentData()

  if (!student) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-2 border-etest-teal border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  // Get latest milestone for achievement card
  const latestMilestone = milestones.find((m) => m.status === 'completed' && m.mentorApproved)

  return (
    <div className="space-y-6">
      {/* Header Greeting */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-etest-red to-etest-red-secondary flex items-center justify-center shadow-lg">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-etest-text">Xin chào, Phụ huynh</h1>
            <p className="text-sm text-etest-subtext mt-0.5">
              Cập nhật mới nhất từ {student.name}
            </p>
          </div>
        </div>
      </section>

      {/* Layer 1 - Priority Alerts */}
      {wellbeing.alert && (
        <AlertCard
          severity={wellbeing.severity as 'high' | 'medium'}
          message={wellbeing.message}
          action={wellbeing.action}
          onChatOpen={() => navigate('/parent/chat')}
        />
      )}

      {/* Countdown to nearest deadline */}
      {student.targetSchools.length > 0 && (
        <CountdownCard school={student.targetSchools[0]} />
      )}

      {/* Progress Card - Score change */}
      <ProgressCard
        currentScore={student.ieltsScore}
        previousScore={6.0}
        skill="IELTS Overall"
      />

      {/* Achievement Card - Latest milestone */}
      {latestMilestone && <AchievementCard milestone={latestMilestone} />}

      {/* Layer 2 - Weekly Digest (expandable) */}
      <Layer2Expander title="Tuần này của con">
        <DigestCard digest={digest} />
      </Layer2Expander>

      {/* Layer 3 - Upsell Recommendations */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-etest-bg-secondary flex items-center justify-center">
            <Calendar className="w-5 h-5 text-etest-teal" />
          </div>
          <h2 className="text-base font-bold text-etest-text">Gợi ý chương trình</h2>
        </div>
        <div className="space-y-3">
          {MOCK_UPSELL.map((course, index) => (
            <UpsellCard key={index} course={course} />
          ))}
        </div>
      </section>
    </div>
  )
}
