import { useState, useEffect } from 'react'
import { studentApi, parentApi } from '../api'
import type { Student, Milestone, EtesterCore, WellbeingAlert, DigestData } from '../types'
import type { ParentBehavioralLog } from '../api/parent'

export function useStudentData(studentId?: string) {
  const [student, setStudent] = useState<Student | null>(null)
  const [wellbeing, setWellbeing] = useState<WellbeingAlert | null>(null)
  const [digest, setDigest] = useState<DigestData | null>(null)
  const [etester, setEtester] = useState<EtesterCore | null>(null)
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [behavioralLogs, setBehavioralLogs] = useState<ParentBehavioralLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)

      try {
        let resolvedStudentId = studentId ?? 'student_001'

        if (!studentId) {
          const meRes = await parentApi.getMe()
          if (meRes.data?.studentId) {
            resolvedStudentId = meRes.data.studentId
          } else {
            console.warn(
              'Parent account is not linked to a student. Falling back to default student_001.'
            )
          }
        }

        const [studentRes, wellbeingRes, digestRes, etesterRes, milestonesRes] =
          await Promise.all([
            studentApi.getStudent(resolvedStudentId),
            parentApi.getWellbeingAlerts(resolvedStudentId),
            parentApi.getDigest(resolvedStudentId),
            studentApi.getEtesterScore(resolvedStudentId),
            studentApi.getMilestones(resolvedStudentId),
          ])

        const logsRes = await parentApi.getBehavioralLogs(resolvedStudentId, 7)

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

        if (logsRes.error) {
          console.warn('Failed to fetch behavioral logs:', logsRes.error)
        } else {
          setBehavioralLogs(logsRes.data || [])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch student data')
      } finally {
        setLoading(false)
      }
    }

    void fetchData()
  }, [studentId])

  return {
    student,
    wellbeing,
    digest,
    etester,
    milestones,
    behavioralLogs,
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
