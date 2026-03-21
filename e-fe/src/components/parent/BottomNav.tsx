import { Home, MessageCircle, BarChart3, User } from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'

const navItems = [
  { icon: Home, label: 'Trang chủ', path: '/parent' },
  { icon: MessageCircle, label: 'Chat', path: '/parent/chat' },
  { icon: BarChart3, label: 'Tiến độ', path: '/parent/progress' },
  { icon: User, label: 'Cá nhân', path: '/parent/profile' },
]

export default function BottomNav() {
  const location = useLocation()

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-etest-border z-50">
      <div className="max-w-[430px] mx-auto flex justify-around items-center h-14 pb-[env(safe-area-inset-bottom)]">
        {navItems.map((item) => {
          const isActive =
            item.path === '/parent'
              ? location.pathname === '/parent'
              : location.pathname.startsWith(item.path)

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center w-16 py-1 ${
                isActive ? 'text-etest-teal' : 'text-etest-subtext'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5 font-medium">{item.label}</span>
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}
