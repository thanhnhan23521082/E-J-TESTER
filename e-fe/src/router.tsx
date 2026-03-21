import { createBrowserRouter } from 'react-router-dom'
import PublicLayout from './layouts/PublicLayout'
import ParentLayout from './layouts/ParentLayout'
import MentorLayout from './layouts/MentorLayout'
import StudentLayout from './layouts/StudentLayout'

// Public pages
import Homepage from './pages/Homepage'
import Login from './pages/Login'

// Parent pages
import ParentHome from './pages/parent/ParentHome'
import ParentChat from './pages/parent/ParentChat'
import StudentProgress from './pages/parent/StudentProgress'
import ParentProfile from './pages/parent/ParentProfile'

// Mentor pages
import MentorHome from './pages/mentor/MentorHome'
import StudentList from './pages/mentor/StudentList'
import MentorContribute from './pages/mentor/MentorContribute'
import EssayReview from './pages/mentor/EssayReview'
import MentorEtester from './pages/mentor/MentorEtester'

// Student pages
import StudentHome from './pages/student/StudentHome'
import StudentEtester from './pages/student/StudentEtester'
import StudentContribute from './pages/student/StudentContribute'
import StudentTimeline from './pages/student/StudentTimeline'
import EssayCheck from './pages/student/EssayCheck'

// Shared pages
import EtesterPublic from './pages/shared/EtesterPublic'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: <Homepage /> },
      { path: 'login', element: <Login /> },
    ],
  },
  {
    path: '/parent',
    element: <ParentLayout />,
    children: [
      { index: true, element: <ParentHome /> },
      { path: 'chat', element: <ParentChat /> },
      { path: 'progress', element: <StudentProgress /> },
      { path: 'profile', element: <ParentProfile /> },
    ],
  },
  {
    path: '/mentor',
    element: <MentorLayout />,
    children: [
      { index: true, element: <MentorHome /> },
      { path: 'students', element: <StudentList /> },
      { path: 'contribute', element: <MentorContribute /> },
      { path: 'review', element: <EssayReview /> },
      { path: 'etester/:studentId', element: <MentorEtester /> },
    ],
  },
  {
    path: '/student',
    element: <StudentLayout />,
    children: [
      { index: true, element: <StudentHome /> },
      { path: 'etester', element: <StudentEtester /> },
      { path: 'contribute', element: <StudentContribute /> },
      { path: 'timeline', element: <StudentTimeline /> },
      { path: 'essay-check', element: <EssayCheck /> },
    ],
  },
  {
    path: '/etester/verify/:studentId',
    element: <EtesterPublic />,
  },
])
