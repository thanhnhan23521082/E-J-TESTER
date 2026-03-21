import { useState, useEffect, useCallback } from 'react'
import { authApi } from '../api'
import type { MeResponse } from '../api/auth'

export interface AuthState {
  user: MeResponse | null
  loading: boolean
  error: string | null
  isLoggedIn: boolean
  refetch: () => Promise<void>
}

/**
 * Hook that fetches the authenticated user's profile from GET /api/auth/me.
 * Only fetches when an access_token exists in localStorage.
 */
export function useAuth(): AuthState {
  const [user, setUser] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMe = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const me = await authApi.getMe()
      setUser(me)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch user')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchMe()
  }, [fetchMe])

  return {
    user,
    loading,
    error,
    isLoggedIn: !!user,
    refetch: fetchMe,
  }
}
