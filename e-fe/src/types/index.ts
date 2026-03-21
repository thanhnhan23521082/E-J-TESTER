export type Role = 'student' | 'parent' | 'mentor'
export type Severity = 'high' | 'medium' | 'low'
export type ContributorType = 'student' | 'mentor' | 'parent' | 'institution'
export type EvidenceStrength = 'low' | 'medium' | 'high' | 'highest'
export type ContributionType =
  | 'session_notes'
  | 'essay_review'
  | 'readiness'
  | 'mock_review'
  | 'program_verify'
  | 'outcome_record'
  | 'mock_test'
  | 'essay_draft'
  | 'camp'
  | 'csr'
  | 'other'

export interface Student {
  id: string
  name: string
  program: 'AMP' | 'IELTS' | 'SAT'
  monthsEnrolled: number
  ieltsScore: number
  satScore: number | null
  gpa: number
  skillBreakdown: { L: number; R: number; W: number; S: number }
  targetSchools: TargetSchool[]
  parentId: string
  mentorId: string
}

export interface TargetSchool {
  name: string
  country: string
  deadline: string
  ieltsRequired: number
  satRequired: number | null
  daysUntilDeadline: number
  isEligible: boolean
  gapIelts: number
  gapSat: number | null
}

export interface BehavioralLog {
  date: string
  durationMin: number
  sessionStart: string
  studied: boolean
  streakDay: number
  scoreDelta: number
}

export interface WellbeingAlert {
  alert: boolean
  severity: Severity
  message: string
  action: string
}

export interface Milestone {
  id: string
  studentId: string
  type: ContributionType
  title: string
  date: string
  score: number | null
  scoreLabel: string
  mentorId: string | null
  mentorApproved: boolean
  authScore: number | null
  notes: string
  status: 'completed' | 'in_progress' | 'upcoming'
  contributorType: ContributorType
  aiSummary: {
    summary: string
    skillsDemonstrated: string[]
    evidenceStrength: EvidenceStrength
  }
}

export interface EtesterCore {
  studentId: string
  academicScore: number
  writingGrowth: number
  skills: string[]
  mentorVerifications: number
  parentSupportLevel: 'low' | 'medium' | 'active' | 'high'
  institutionalStamp: boolean
  consistencyScore: number
  totalContributions: number
  lastUpdated: string
  narrativeCache: string
  badgeIssued: boolean
}

export interface DigestData {
  progressPct: number
  milestonesCompleted: number
  nextDeadline: string
  daysLeft: number
  priorityAction: string
  weakestSkill: string
}

export interface UpsellCourse {
  courseName: string
  reason: string
  ctaUrl: string
  tag: 'Trại hè' | 'Khóa học' | 'Workshop'
}

export interface AuthenticityResult {
  authScore: number
  confidence: number
  consistentPatterns: string[]
  divergentPatterns: string[]
  recommendation: string
}

export interface Mentor {
  id: string
  name: string
  studentIds: string[]
  pendingEssayCount: number
  pendingSessionNoteCount: number
}

export interface ChatMessage {
  id: string
  sender: 'parent' | 'ai'
  content: string
  timestamp: string
}
