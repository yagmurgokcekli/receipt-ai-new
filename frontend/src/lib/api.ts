import type { IPublicClientApplication, AccountInfo } from "@azure/msal-browser"
import { apiRequest } from "@/auth/msalConfig"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

if (!API_BASE_URL) {
    throw new Error("Missing VITE_API_BASE_URL")
}

async function getAccessToken(
    instance: IPublicClientApplication,
    account: AccountInfo
) {
    const response = await instance.acquireTokenSilent({
        ...apiRequest,
        account,
    })

    return response.accessToken
}

export async function apiFetch<T>(
    path: string,
    instance: IPublicClientApplication,
    account: AccountInfo,
    options: RequestInit = {}
): Promise<T> {
    const token = await getAccessToken(instance, account)

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            ...options.headers,
        },
    })

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
    }

    return response.json()
}