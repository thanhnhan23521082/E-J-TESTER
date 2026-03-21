/**
 * useAuth — Authentication context hook
 *
 * Returns the currently authenticated user.
 * TODO: wire to real auth provider (e.g., Zustand / React Context)
 * once the login flow is implemented.
 *
 * For now: returns a hardcoded parent user for development.
 */
import { useState } from 'react'

export interface AuthUser {
  id: string
  role: 'parent' | 'mentor' | 'student' | 'admin'
  email?: string
}

export function useAuth(): AuthUser {
  // TODO: replace with real auth store / token decoding
  const [user] = useState<AuthUser>({
    id: 'parent_001',
    role: 'parent',
    email: 'parent@example.com',
  })
  return user
}
