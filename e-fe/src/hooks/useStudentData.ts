import { useState, useEffect } from 'react'
import { studentApi, parentApi, authApi } from '../api'
import type {
  Student,
  Milestone,
  EtesterCore,
  WellbeingAlert,
  DigestData,
  UpsellCourse,
} from '../types'
import type { ParentBehavioralLog } from '../api/parent'

export function useStudentData(studentId?: string) {
  const [student, setStudent] = useState<Student | null>(null)
  const [wellbeing, setWellbeing] = useState<WellbeingAlert | null>(null)
  const [digest, setDigest] = useState<DigestData | null>(null)
  const [etester, setEtester] = useState<EtesterCore | null>(null)
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [behavioralLogs, setBehavioralLogs] = useState<ParentBehavioralLog[]>([])
  const [upsell, setUpsell] = useState<UpsellCourse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)

      try {
        let resolvedStudentId = studentId

        // If no studentId was passed, resolve from logged-in user
        if (!resolvedStudentId) {
          try {
            const me = await authApi.getMe()

            if (me.role === 'student' && me.student_id) {
              // Current user IS a student
              resolvedStudentId = me.student_id
            } else if (me.role === 'parent') {
              // Current user is a parent — fetch their linked student
              const meRes = await parentApi.getMe()
              if (meRes.data?.studentId) {
                resolvedStudentId = meRes.data.studentId
              }
            }
          } catch {
            console.warn('Could not resolve student ID from auth context')
          }
        }

        if (!resolvedStudentId) {
          setError('Không tìm thấy thông tin học viên liên kết với tài khoản này')
          setLoading(false)
          return
        }

        const [studentRes, wellbeingRes, digestRes, etesterRes, milestonesRes, upsellRes] =
          await Promise.all([
            studentApi.getStudent(resolvedStudentId),
            parentApi.getWellbeingAlerts(resolvedStudentId),
            parentApi.getDigest(resolvedStudentId),
            studentApi.getEtesterScore(resolvedStudentId),
            studentApi.getMilestones(resolvedStudentId),
            parentApi.getUpsellSuggestion(resolvedStudentId),
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

        if (upsellRes.error) {
          console.warn('Failed to fetch upsell suggestion:', upsellRes.error)
        } else {
          setUpsell(upsellRes.data || null)
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
    upsell,
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
