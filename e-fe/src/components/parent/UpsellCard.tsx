import { ExternalLink, Calendar, BookOpen, Users } from 'lucide-react'
import type { UpsellCourse } from '../../types'

interface UpsellCardProps {
  course: UpsellCourse
}

const tagIcons = {
  'Trại hè': Calendar,
  'Khóa học': BookOpen,
  'Workshop': Users,
}

const tagColors = {
  'Trại hè': 'bg-etest-green-bg text-etest-green border-etest-green/30',
  'Khóa học': 'bg-etest-teal-light text-etest-teal border-etest-teal/30',
  'Workshop': 'bg-etest-amber-bg text-etest-amber border-etest-amber/30',
}

export default function UpsellCard({ course }: UpsellCardProps) {
  const Icon = tagIcons[course.tag]

  return (
    <div className="bg-etest-bg rounded-2xl p-4 border border-etest-border/40">
      <div className="flex items-start gap-3">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
            course.tag === 'Trại hè'
              ? 'bg-etest-green-bg'
              : course.tag === 'Khóa học'
              ? 'bg-etest-teal-light'
              : 'bg-etest-amber-bg'
          }`}
        >
          <Icon
            className={`w-5 h-5 ${
              course.tag === 'Trại hè'
                ? 'text-etest-green'
                : course.tag === 'Khóa học'
                ? 'text-etest-teal'
                : 'text-etest-amber'
            }`}
          />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${tagColors[course.tag]}`}
            >
              {course.tag}
            </span>
          </div>
          <h3 className="font-semibold text-etest-text text-sm">{course.courseName}</h3>
          <p className="text-xs text-etest-subtext mt-1">{course.reason}</p>
        </div>
        <a
          href={course.ctaUrl}
          className="p-2 text-etest-teal hover:text-etest-teal-dark"
          aria-label={`Xem ${course.courseName}`}
        >
          <ExternalLink className="w-5 h-5" />
        </a>
      </div>
    </div>
  )
}
