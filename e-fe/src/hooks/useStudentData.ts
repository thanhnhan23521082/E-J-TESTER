import { useState, useEffect } from 'react'
import { studentApi, parentApi } from '../api'
import type { Student, Milestone, EtesterCore, WellbeingAlert, DigestData } from '../types'

export function useStudentData(studentId: string = 'student_001') {
  const [student, setStudent] = useState<Student | null>(null)
  const [wellbeing, setWellbeing] = useState<WellbeingAlert | null>(null)
  const [digest, setDigest] = useState<DigestData | null>(null)
  const [etester, setEtester] = useState<EtesterCore | null>(null)
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)

      try {
        const [studentRes, wellbeingRes, digestRes, etesterRes, milestonesRes] =
          await Promise.all([
            studentApi.getStudent(studentId),
            parentApi.getWellbeingAlerts(studentId),
            parentApi.getDigest(studentId),
            studentApi.getEtesterScore(studentId),
            studentApi.getMilestones(studentId),
          ])

        if (studentRes.error) {
          setError(studentRes.error)
        } else {
          setStudent(studentRes.data)
        }

        if (wellbeingRes.error) {
          console.warn('Failed to fetch wellbeing:', wellbeingRes.error)
        } else {
          setWellbeing(wellbeingRes.data)
        }

        if (digestRes.error) {
          console.warn('Failed to fetch digest:', digestRes.error)
        } else {
          setDigest(digestRes.data)
        }

        if (etesterRes.error) {
          console.warn('Failed to fetch etester:', etesterRes.error)
        } else {
          setEtester(etesterRes.data)
        }

        if (milestonesRes.error) {
          console.warn('Failed to fetch milestones:', milestonesRes.error)
        } else {
          setMilestones(milestonesRes.data || [])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch student data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [studentId])

  return {
    student,
    wellbeing,
    digest,
    etester,
    milestones,
    loading,
    error,
  }
}

export function useMentorData() {
  return {
    mentor: {
      id: 'mentor_001',
      name: 'Thầy Nguyễn Minh',
      students: [],
    },
    pendingEssays: 3,
    pendingNotes: 2,
  }
}
