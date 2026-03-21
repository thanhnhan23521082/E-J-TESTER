import type {
  Student,
  WellbeingAlert,
  DigestData,
  EtesterCore,
  Milestone,
  UpsellCourse,
  Mentor,
} from '../types'

import studentJson from './json/student.json'
import wellbeingJson from './json/wellbeing.json'
import digestJson from './json/digest.json'
import etesterJson from './json/etester.json'
import milestonesJson from './json/milestones.json'
import upsellJson from './json/upsell.json'
import mentorJson from './json/mentor.json'

export const MOCK_STUDENT: Student = studentJson as Student
export const MOCK_WELLBEING: WellbeingAlert = wellbeingJson as WellbeingAlert
export const MOCK_DIGEST: DigestData = digestJson as DigestData
export const MOCK_ETESTER: EtesterCore = etesterJson as EtesterCore
export const MOCK_MILESTONES: Milestone[] = milestonesJson as Milestone[]
export const MOCK_UPSELL: UpsellCourse[] = upsellJson as UpsellCourse[]
export const MOCK_MENTOR: Mentor = mentorJson as Mentor

// Helper to get student by ID (for future multi-student scenarios)
export function getStudentById(id: string): Student | undefined {
  if (id === MOCK_STUDENT.id) {
    return MOCK_STUDENT
  }
  return undefined
}

// Helper to get milestones for a student
export function getMilestonesByStudentId(studentId: string): Milestone[] {
  return MOCK_MILESTONES.filter((m) => m.studentId === studentId)
}
