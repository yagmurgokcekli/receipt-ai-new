import type { Configuration } from "@azure/msal-browser"

const clientId = import.meta.env.VITE_AZURE_CLIENT_ID
const authority = import.meta.env.VITE_AZURE_AUTHORITY
const redirectUri = import.meta.env.VITE_REDIRECT_URI

if (!clientId || !authority || !redirectUri) {
  throw new Error("Missing Azure AD environment variables")
}

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority,
    redirectUri,
  },

  cache: {
    cacheLocation: "localStorage",
  },
}

export const loginRequest = {
  scopes: ["User.Read"],
}

export const apiRequest = {
  scopes: [`api://${clientId}/access_as_user`],
}
