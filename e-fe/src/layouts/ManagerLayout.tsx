import { Outlet } from 'react-router-dom'
import { Award, Search } from 'lucide-react'
import UserDropdown from '../components/shared/UserDropdown'
import NotificationDropdown from '../components/shared/NotificationDropdown'

export default function ManagerLayout() {
  return (
    <div className="min-h-screen bg-etest-bg">
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-etest-border/10">
        <div className="max-w-[1200px] mx-auto h-16 flex items-center justify-between px-8">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-etest-red flex items-center justify-center">
                <Award className="w-4 h-4 text-white" />
              </div>
              <div>
                <span className="text-sm font-black text-etest-red tracking-widest uppercase">ETEST</span>
                <span className="text-sm font-bold text-etest-text ml-1.5">Digital Badges</span>
              </div>
            </div>
            <div className="h-6 w-px bg-etest-border/20 mx-2" />
            <div className="relative">
              <Search className="w-4 h-4 text-etest-hint absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search student..."
                className="pl-9 pr-4 py-2 bg-etest-bg-secondary border-none rounded-xl w-56 text-sm focus:ring-2 focus:ring-etest-red/20 placeholder:text-etest-hint"
              />
            </div>
          </div>

          <div className="flex items-center gap-5">
            <NotificationDropdown />
            <div className="h-6 w-px bg-etest-border/20" />
            <UserDropdown
              name="Manager Admin"
              role="Manager"
              initials="MA"
              avatarColor="bg-etest-pink-light"
              textColor="text-etest-red"
            />
          </div>
        </div>
      </header>

      <main className="max-w-[1200px] mx-auto px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
