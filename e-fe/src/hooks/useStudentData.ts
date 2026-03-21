import { useMemo } from 'react'
import {
  MOCK_STUDENT,
  MOCK_WELLBEING,
  MOCK_DIGEST,
  MOCK_ETESTER,
  getMilestonesByStudentId,
} from '../data/mock'

export function useStudentData(studentId: string = 'student_001') {
  const student = useMemo(() => {
    if (studentId === MOCK_STUDENT.id) {
      return MOCK_STUDENT
    }
    return null
  }, [studentId])

  const etester = useMemo(() => {
    if (studentId === MOCK_ETESTER.studentId) {
      return MOCK_ETESTER
    }
    return null
  }, [studentId])

  const milestones = useMemo(() => {
    return getMilestonesByStudentId(studentId)
  }, [studentId])

  return {
    student,
    wellbeing: MOCK_WELLBEING,
    digest: MOCK_DIGEST,
    etester,
    milestones,
  }
}

export function useMentorData() {
  return {
    mentor: {
      id: 'mentor_001',
      name: 'Thầy Nguyễn Minh',
      students: [MOCK_STUDENT],
    },
    pendingEssays: 3,
    pendingNotes: 2,
  }
}
