import { Navigate } from 'react-router-dom'

export default function Homepage() {
  // The design shows the login page as the pre-login landing page
  // Redirect to login which matches the homepage.pen and login.pen designs
  return <Navigate to="/login" replace />
}
