import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import type { AllRoles } from '../types'

interface RoleContextType {
  role: AllRoles | null
  setRole: (role: AllRoles | null) => void
  clearRole: () => void
}

const RoleContext = createContext<RoleContextType | undefined>(undefined)

interface RoleProviderProps {
  children: ReactNode
}

export function RoleProvider({ children }: RoleProviderProps) {
  const [role, setRoleState] = useState<AllRoles | null>(null)

  const setRole = useCallback((newRole: AllRoles | null) => {
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
