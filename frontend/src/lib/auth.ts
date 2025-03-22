import type {
	GetServerSidePropsContext,
	NextApiRequest,
	NextApiResponse,
} from "next"
import type { NextAuthOptions } from "next-auth"
import { getServerSession } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import { JWT } from "next-auth/jwt"
import { Session, User, Account } from "next-auth"

interface JwtResponse {
	refresh: string
	access: string
	user: {
		id: number
		email: string
	}
}

export const authOptions: NextAuthOptions = {
	providers: [
		GoogleProvider({
			clientId: process.env.AUTH_GOOGLE_ID as string,
			clientSecret: process.env.AUTH_GOOGLE_SECRET as string,
		}),
	],
	pages: {
		signIn: "/login",
	},
	callbacks: {
		async signIn({ user, account }: { user: User; account: Account | null }) {
			// Uncomment if you want to use the backend
			// return true
			if (account?.id_token) {
				const id_token = account.id_token
				const formData = new FormData()
				formData.append("id_token", id_token)

				const response = await fetch("http://localhost:8000/api/token/verify", {
					method: "POST",
					body: formData,
				})

				const data = (await response.json()) as JwtResponse

				if (response.status == 200) {
					console.log("Token validation successful.", data)
					user.accessToken = data.access
					user.refreshToken = data.refresh
					user.user_id = data.user.id
					user.email = data.user.email

					return true
				}

				console.log("Failure", data)
			}

			return false
		},
		async redirect({ url, baseUrl }) {
			console.log("Redirecting to:", url)
			return url.startsWith(baseUrl) ? url : baseUrl
		},
		async jwt({ token, user }: { token: JWT; user: User }) {
			// This persists state with the session on refresh
			if (user) {
				token = {
					accessToken: user.accessToken,
					refreshToken: user.refreshToken,
					user_id: user.user_id,
					email: user.email,
				}
			}
			return token
		},
		async session({ session, token }: { session: Session; token: JWT }) {
			// Setting the accessToken in the session so that we can make direct calls to Django with the token
			session.accessToken = token.accessToken
			session.user_id = token.user_id
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
