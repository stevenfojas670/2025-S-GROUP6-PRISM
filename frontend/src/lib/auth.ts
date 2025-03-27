import type {
	GetServerSidePropsContext,
	NextApiRequest,
	NextApiResponse,
} from "next"
import type { NextAuthOptions } from "next-auth"
import { getServerSession } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import { userAgent } from "next/server"

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
		async signIn({ user, account }) {
			if (account?.id_token) {
				user.id_token = account.id_token
				return true
			}
			return false
		},
		async redirect({ url, baseUrl }) {
			console.log("Redirecting to:", url)
			return url.startsWith(baseUrl) ? url : baseUrl
		},
		async jwt({ token, user }) {
			if (user) {
				token.accessToken = user.id_token
			}
			return token
		},
		async session({ session, token }) {
			session.idToken = token.accessToken
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
