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
		}),
	],
	pages: {
		signIn: "/login",
	},
	callbacks: {
		async signIn({ user, account }) {
			// Uncomment if you want to use the backend
			// return true
			if (account?.provider === "google") {
				const response = await fetch("http://localhost:8000/api/token/verify", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ token: account.id_token }),
				})

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
		async session({ session, user, token }) {
			return session
		},
		async jwt({ token, user, account, profile }) {
			return token
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
