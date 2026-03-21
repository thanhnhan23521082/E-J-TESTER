import { RouterProvider } from 'react-router-dom'
import { RoleProvider } from './hooks/useRole'
import { router } from './router'

function App() {
  return (
    <RoleProvider>
      <RouterProvider router={router} />
    </RoleProvider>
  )
}

export default App
