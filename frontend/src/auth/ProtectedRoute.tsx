import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { InteractionStatus } from "@azure/msal-browser"
import { useIsAuthenticated, useMsal } from "@azure/msal-react"

type ProtectedRouteProps = {
    children: ReactNode
}

export default function ProtectedRoute({
    children,
}: ProtectedRouteProps) {
    const isAuthenticated = useIsAuthenticated()
    const { inProgress } = useMsal()

    if (inProgress !== InteractionStatus.None) {
        return (
            <div className="flex min-h-svh items-center justify-center">
                Loading...
            </div>
        )
    }

    if (!isAuthenticated) {
        return <Navigate to="/" replace />
    }

    return children
}