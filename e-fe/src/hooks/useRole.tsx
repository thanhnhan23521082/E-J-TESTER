import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import type { Role } from '../types'

interface RoleContextType {
  role: Role | null
  setRole: (role: Role | null) => void
  clearRole: () => void
}

const RoleContext = createContext<RoleContextType | undefined>(undefined)

interface RoleProviderProps {
  children: ReactNode
}

export function RoleProvider({ children }: RoleProviderProps) {
  const [role, setRoleState] = useState<Role | null>(null)

  const setRole = useCallback((newRole: Role | null) => {
    setRoleState(newRole)
  }, [])

  const clearRole = useCallback(() => {
    setRoleState(null)
  }, [])

  return (
    <RoleContext.Provider value={{ role, setRole, clearRole }}>
      {children}
    </RoleContext.Provider>
  )
}

export function useRole(): RoleContextType {
  const context = useContext(RoleContext)
  if (context === undefined) {
    throw new Error('useRole must be used within a RoleProvider')
  }
  return context
}
