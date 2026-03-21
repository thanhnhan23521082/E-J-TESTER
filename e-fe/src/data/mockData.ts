/**
 * Mock Data Exports
 *
 * Centralized mock data for API layer
 */

import type {
  Student,
  WellbeingAlert,
  DigestData,
  EtesterCore,
  Milestone,
  Mentor,
} from '../types'

import studentJson from './json/student.json'
import wellbeingJson from './json/wellbeing.json'
import digestJson from './json/digest.json'
import etesterJson from './json/etester.json'
import milestonesJson from './json/milestones.json'
import mentorJson from './json/mentor.json'

export const mockStudents: Student[] = [studentJson as Student]
export const mockWellbeingAlerts: WellbeingAlert[] = [wellbeingJson as WellbeingAlert]
export const mockDigestData: DigestData[] = [digestJson as DigestData]
export const mockEtesterScores: EtesterCore[] = [etesterJson as EtesterCore]
export const mockMilestones: Milestone[] = milestonesJson as Milestone[]
export const mockMentors: Mentor[] = [mentorJson as Mentor]

// Legacy exports for backward compatibility
export const MOCK_STUDENT: Student = studentJson as Student
export const MOCK_WELLBEING: WellbeingAlert = wellbeingJson as WellbeingAlert
export const MOCK_DIGEST: DigestData = digestJson as DigestData
export const MOCK_ETESTER: EtesterCore = etesterJson as EtesterCore
export const MOCK_MILESTONES: Milestone[] = milestonesJson as Milestone[]
export const MOCK_MENTOR: Mentor = mentorJson as Mentor

// Helper to get student by ID
export function getStudentById(id: string): Student | undefined {
  return mockStudents.find((s) => s.id === id)
}

// Helper to get milestones for a student
export function getMilestonesByStudentId(studentId: string): Milestone[] {
  return mockMilestones.filter((m) => m.studentId === studentId)
}
