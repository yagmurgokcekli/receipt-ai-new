import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { FieldDescription, FieldGroup } from "@/components/ui/field"
import { useMsal } from "@azure/msal-react"
import { loginRequest } from "@/auth/msalConfig"

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { instance } = useMsal()

  const handleMicrosoftLogin = () => {
    instance.loginRedirect({
      ...loginRequest,
      redirectStartPage: "/dashboard",
    })
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="mx-auto w-full max-w-xl overflow-hidden p-0 shadow-lg">
        <CardContent className="p-6 md:p-8">
          <FieldGroup>
            <div className="flex flex-col items-center gap-3 text-center">
              <h1 className="text-4xl font-bold tracking-tight">Receipt AI</h1>
              <p className="max-w-md text-balance text-lg text-muted-foreground">
                Upload, analyze, and manage your receipts with AI-powered
                insights.
              </p>
            </div>

            <Button
              type="button"
              size="lg"
              className="w-full"
              onClick={handleMicrosoftLogin}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 23 23"
                className="mr-2 h-5 w-5"
              >
                <path fill="#f25022" d="M1 1h10v10H1z" />
                <path fill="#00a4ef" d="M12 1h10v10H12z" />
                <path fill="#7fba00" d="M1 12h10v10H1z" />
                <path fill="#ffb900" d="M12 12h10v10H12z" />
              </svg>
              Sign in with Microsoft
            </Button>

            <FieldDescription className="text-center text-base">
              Secure login with your Microsoft account.
            </FieldDescription>
          </FieldGroup>
        </CardContent>
      </Card>

      <FieldDescription className="px-6 text-center text-base">
        AI-powered receipt processing, comparison, and expense analysis.
      </FieldDescription>
    </div>
  )
}