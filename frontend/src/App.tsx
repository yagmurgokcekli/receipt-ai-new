import { BrowserRouter, Route, Routes } from "react-router-dom"
import { TooltipProvider } from "@/components/ui/tooltip"

import ProtectedRoute from "@/auth/ProtectedRoute"
import LoginPage from "@/pages/loginpage"
import DashboardPage from "@/pages/dashboardpage"

export default function App() {
  return (
    <TooltipProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LoginPage />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  )
}