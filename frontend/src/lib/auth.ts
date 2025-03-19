import type {
	GetServerSidePropsContext,
	NextApiRequest,
	NextApiResponse,
} from "next"
import type { NextAuthOptions } from "next-auth"
import { getServerSession } from "next-auth"
import GoogleProvider from "next-auth/providers/google"

export const authOptions: NextAuthOptions = {
	providers: [
		GoogleProvider({
			clientId: process.env.AUTH_GOOGLE_ID,
			clientSecret: process.env.AUTH_GOOGLE_SECRET,
			authorization: {
				params: {
					access_type: "offline",
					prompt: "consent",
				},
			},
		}),
	],
	pages: {
		signIn: "/login",
	},
	callbacks: {
		async signIn({ user, account }) {
			if (
				!(
					user.email?.toLowerCase().includes("unlv.edu") ||
					user.email?.toLowerCase().includes("unlv.nevada.edu")
				)
			)
				return false
			console.log(account?.id_token)
			if (account?.id_token) {
				const response = await fetch(
					"http://localhost:8000/api/validate-token/",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({ token: account.id_token }),
					}
				)

				const data = await response.json()

				if (response.status == 401) {
					console.log("Token validation failed.", data)
					return false
				} else if (response.status == 200) {
					console.log("Token validation successful.", data)
					return true
				}
			}

			return false
		},
		async redirect({ url, baseUrl }) {
			console.log("Redirecting to:", url)
			return url.startsWith(baseUrl) ? url : baseUrl
		},
		async jwt({ token, account }) {
			if (account) {
				// First-time login, save the `access_token`, its expiry and the `refresh_token`
				return {
					...token,
					access_token: account.access_token,
					expires_at: account.expires_at,
					refresh_token: account.refresh_token,
				}
			} else if (Date.now() < token.expires_at * 1000) {
				// Subsequent logins, but the `access_token` is still valid
				return token
			} else {
				// Subsequent logins, but the `access_token` has expired, try to refresh it
				if (!token.refresh_token) throw new TypeError("Missing refresh_token")

				try {
					// The `token_endpoint` can be found in the provider's documentation. Or if they support OIDC,
					// at their `/.well-known/openid-configuration` endpoint.
					// i.e. https://accounts.google.com/.well-known/openid-configuration
					const response = await fetch("https://oauth2.googleapis.com/token", {
						method: "POST",
						body: new URLSearchParams({
							clientId: process.env.AUTH_GOOGLE_ID,
							clientSecret: process.env.AUTH_GOOGLE_SECRET,
							grant_type: "refresh_token",
							refresh_token: token.refresh_token!,
						}),
					})

					const tokensOrError = await response.json()

					if (!response.ok) throw tokensOrError

					const newTokens = tokensOrError as {
						access_token: string
						expires_in: number
						refresh_token?: string
					}

					return {
						...token,
						access_token: newTokens.access_token,
						expires_at: Math.floor(Date.now() / 1000 + newTokens.expires_in),
						// Some providers only issue refresh tokens once, so preserve if we did not get a new one
						refresh_token: newTokens.refresh_token
							? newTokens.refresh_token
							: token.refresh_token,
					}
				} catch (error) {
					console.error("Error refreshing access_token", error)
					// If we fail to refresh the token, return an error so we can handle it on the page
					token.error = "RefreshTokenError"
					return token
				}
			}
		},
		async session({ session, token }) {
			session.error = token.error
			return session
		},
	},
}

export function auth(
	...args:
		| [GetServerSidePropsContext["req"], GetServerSidePropsContext["res"]]
		| [NextApiRequest, NextApiResponse]
		| []
) {
	return getServerSession(...args, authOptions)
}
