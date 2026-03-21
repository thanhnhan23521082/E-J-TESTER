import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Settings, LogOut, ChevronDown } from 'lucide-react'
import { useRole } from '../../hooks/useRole'

interface UserDropdownProps {
  name: string
  role: string
  initials: string
  avatarColor?: string
  textColor?: string
}

export default function UserDropdown({
  name,
  role,
  initials,
  avatarColor = 'bg-etest-red-light',
  textColor = 'text-etest-red',
}: UserDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const { setRole } = useRole()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    setRole(null)
    navigate('/login')
  }

  const handleSettings = () => {
    setIsOpen(false)
    // Navigate to settings page when implemented
  }

  const handleProfile = () => {
    setIsOpen(false)
    // Navigate to profile page when implemented
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 hover:opacity-80 transition-opacity"
      >
        <div className="text-right">
          <p className="text-sm font-semibold text-etest-text">{name}</p>
          <p className="text-xs text-etest-subtext">{role}</p>
        </div>
        <div className={`w-10 h-10 ${avatarColor} rounded-xl flex items-center justify-center`}>
          <span className={`text-sm font-semibold ${textColor}`}>{initials}</span>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-etest-subtext transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-2xl shadow-lg border border-etest-border/20 py-2 z-50">
          <div className="px-4 py-3 border-b border-etest-border/20">
            <p className="text-sm font-semibold text-etest-text">{name}</p>
            <p className="text-xs text-etest-subtext">{role}</p>
          </div>

          <div className="py-1">
            <button
              onClick={handleProfile}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-etest-text hover:bg-etest-bg transition-colors"
            >
              <User className="w-4 h-4" />
              <span>Hồ sơ của tôi</span>
            </button>
            <button
              onClick={handleSettings}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-etest-text hover:bg-etest-bg transition-colors"
            >
              <Settings className="w-4 h-4" />
              <span>Cài đặt</span>
            </button>
          </div>

          <div className="border-t border-etest-border/20 pt-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-etest-red hover:bg-etest-red-light/50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Đăng xuất</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
