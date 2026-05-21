import type { CSSProperties } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { SectionCards } from "@/components/section-cards"
import { SiteHeader } from "@/components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { useEffect, useState } from "react"
import { useMsal } from "@azure/msal-react"
import { apiFetch } from "@/lib/api"
import type { Receipt } from "@/types/receipt"

const sidebarStyle = {
  "--sidebar-width": "calc(var(--spacing) * 72)",
  "--header-height": "calc(var(--spacing) * 12)",
} as CSSProperties

export default function DashboardPage() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { instance, accounts } = useMsal()
  const account = accounts[0]

  useEffect(() => {
    async function fetchReceipts() {
      if (!account) return

      try {
        setLoading(true)

        const result = await apiFetch<Receipt[]>("/receipts", instance, account)

        console.log("RECEIPTS:", result)
        setReceipts(result)
      } catch (err) {
        console.error(err)
        setError("Receipts could not be loaded")
      } finally {
        setLoading(false)
      }
    }

    fetchReceipts()
  }, [instance, account])
  return (
    <SidebarProvider style={sidebarStyle}>
      <AppSidebar variant="inset" />

      <SidebarInset>
        <SiteHeader />

        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <SectionCards />

              <div className="px-4 lg:px-6">
                <ChartAreaInteractive />
              </div>

              <div className="mx-4 rounded-lg border p-4 text-sm">
                {loading ? (
                  "Loading receipts..."
                ) : error ? (
                  error
                ) : receipts.length === 0 ? (
                  "No receipts found yet."
                ) : (
                  <pre>{JSON.stringify(receipts, null, 2)}</pre>
                )}
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
