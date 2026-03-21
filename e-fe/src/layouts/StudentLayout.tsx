import { Outlet, NavLink } from 'react-router-dom'
import {
  Home,
  Award,
  FileText,
  Clock,
  Upload,
  Search,
  ChevronDown,
} from 'lucide-react'
import { useState } from 'react'
import UserDropdown from '../components/shared/UserDropdown'
import NotificationDropdown from '../components/shared/NotificationDropdown'

const navItems = [
  { icon: Home, label: 'Tổng qua', path: '/student' },
  { icon: Award, label: 'ETESTER của tôi', path: '/student/etester' },
  { icon: Upload, label: 'Nộp bài', path: '/student/contribute' },
  { icon: Clock, label: 'Timeline', path: '/student/timeline' },
  { icon: FileText, label: 'Essay Check', path: '/student/essay-check' },
]

export default function StudentLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-etest-bg flex">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-full bg-etest-bg-secondary border-r border-etest-border/5 z-40 transition-all duration-300 ${
          sidebarCollapsed ? 'w-16' : 'w-64'
        } hidden lg:flex flex-col justify-between py-6`}
      >
        {/* Logo Section */}
        <div className={`px-6 ${sidebarCollapsed ? 'px-4 text-center' : ''}`}>
          {!sidebarCollapsed ? (
            <div className="flex flex-col gap-1.5">
              <span className="text-2xl font-semibold text-etest-red tracking-tight leading-8">
                ETEST ONE
              </span>
              <span className="text-[10px] font-bold text-etest-subtext tracking-widest uppercase">
                Academic Atelier
              </span>
            </div>
          ) : (
            <span className="text-sm font-semibold text-etest-red">E</span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-0 mt-10">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/student'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 transition-all relative ${
                  isActive
                    ? 'bg-white text-etest-red font-bold rounded-l-full mr-3.5 shadow-sm'
                    : 'text-etest-nav-text hover:bg-white/30 hover:text-etest-text'
                } ${!sidebarCollapsed ? 'mx-0 px-4' : 'justify-center'}`
              }
            >
              <item.icon className="w-[18px] h-[18px] flex-shrink-0" />
              {!sidebarCollapsed && (
                <span className="text-sm font-bold">{item.label}</span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom CTA Button */}
        <div className={`px-6 ${sidebarCollapsed ? 'px-4 text-center' : ''}`}>
          {!sidebarCollapsed && (
            <button
              onClick={() => {}}
              className="w-full btn-primary text-white font-semibold py-3 px-4 rounded-xl shadow-button hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
            >
              <Award className="w-4 h-4" />
              <span>Level Up</span>
            </button>
          )}
          {sidebarCollapsed && (
            <button
              onClick={() => {}}
              className="p-2 text-etest-subtext hover:text-etest-text rounded-lg hover:bg-white/50 mx-auto flex"
              aria-label="Level Up"
            >
              <Award className="w-4 h-4" />
            </button>
          )}
        </div>
      </aside>

      {/* Main content area */}
      <div className={`flex-1 flex flex-col ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'}`}>
        {/* Top bar with glass effect */}
        <header className="h-16 flex items-center justify-between px-8 sticky top-0 z-30 glass-navbar border-b border-etest-border/5">
          {/* Search Bar */}
          <div className="flex items-center gap-4 flex-1">
            <div className="flex items-center gap-2 bg-etest-bg-secondary rounded-full px-4 py-1.5 max-w-md flex-1">
              <Search className="w-4 h-4 text-etest-subtext" />
              <input
                type="text"
                placeholder="Tìm kiếm..."
                className="bg-transparent border-none outline-none text-sm text-etest-text placeholder:text-etest-hint w-full"
              />
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4">
              <NotificationDropdown />
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="p-2 text-etest-subtext hover:text-etest-text rounded-lg hover:bg-white/50 hidden lg:flex"
                aria-label={sidebarCollapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'}
              >
                <ChevronDown
                  className={`w-5 h-5 transition-transform ${sidebarCollapsed ? 'rotate-180' : '-rotate-90'}`}
                />
              </button>
            </div>

            {/* Divider */}
            <div className="h-8 w-px bg-etest-border/30" />

            {/* User Profile Dropdown */}
            <UserDropdown
              name="Nguyễn Văn A"
              role="Học viên"
              initials="NV"
              avatarColor="bg-etest-red-light"
              textColor="text-etest-red"
            />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-10 overflow-auto">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-etest-border/5 z-50 lg:hidden pb-safe shadow-glass">
        <div className="flex justify-around items-center h-14">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/student'}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center px-3 py-2 min-w-[44px] min-h-[44px] transition-colors ${
                  isActive
                    ? 'text-etest-red'
                    : 'text-etest-subtext hover:text-etest-text'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
