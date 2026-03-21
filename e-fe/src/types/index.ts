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

// ─── ETESTER Module Types ────────────────────────────────────────────

export type ManagerRole = 'manager'
export type AllRoles = Role | ManagerRole

export type ActivityType =
  | 'mock_test'
  | 'essay_draft'
  | 'essay_final'
  | 'camp'
  | 'csr'
  | 'mentor_session'
  | 'consultation'
  | 'recommendation'
  | 'award'

export type DifficultyLevel = 'easy' | 'medium' | 'hard'

export type TraceLinkType =
  | 'experience_source'
  | 'revision_of'
  | 'mentor_guided'
  | 'skill_applied'

export type TraceLinkStatus = 'pending' | 'mentor_approved' | 'rejected'

export type CredentialType = 'jwt_rs256' | 'w3c_vc_ed25519'

export interface Artifact {
  id: string
  studentId: string
  type: ActivityType
  title: string
  date: string
  score: number | null
  authScore: number | null
  mentorApproved: boolean
  skills: string[]
  notes: string
  difficulty: DifficultyLevel
  aiSummary: string
  leadershipRole?: string
  leadershipPeople?: number
  leadershipOutcome?: string
}

export interface TraceLink {
  id: string
  sourceArtifactId: string
  sourceTitle: string
  sourceType: ActivityType
  sourceDate: string
  targetArtifactId: string
  targetTitle: string
  targetType: ActivityType
  targetDate: string
  linkType: TraceLinkType
  confidence: number
  aiReason: string
  studentNote: string
  mentorComment: string
  status: TraceLinkStatus
}

export interface TraceLinkSuggestion {
  id: string
  artifactTitle: string
  artifactType: ActivityType
  linkType: TraceLinkType
  confidence: number
  aiReason: string
  iconName: string
}

export interface AuthScoreDimension {
  id: string
  label: string
  weight: number
  score: number
  description: string
}

export interface AuthScoreBreakdown {
  overallScore: number
  verdict: 'justified_growth' | 'suspicious' | 'verified'
  summary: string
  dimensions: AuthScoreDimension[]
  relatedArtifacts: string[]
}

export interface GraphNode {
  id: string
  type: 'experience' | 'draft' | 'final' | 'mentor_session' | 'award' | 'test' | 'core'
  title: string
  subtitle?: string
  date: string
  x: number
  y: number
  authScore?: number
  mentorApproved?: boolean
  leadershipBadge?: boolean
}

export interface GraphEdge {
  sourceId: string
  targetId: string
  type: TraceLinkType
  color: string
}

export interface ReadinessCheckItem {
  label: string
  passed: boolean
}

export interface BadgePayload {
  studentName: string
  program: string
  months: number
  milestones: number
  mentorVerified: number
  ielts: number
  sat: number | null
  authAvg: number
  leadership: string
  requirementsCovered: string
  expires: string
  issuer: string
}

export interface SigningChainStep {
  step: number
  label: string
  status: 'verified' | 'pending' | 'not_started'
}

export interface RequirementItem {
  icon: string
  label: string
  covered: boolean
}
