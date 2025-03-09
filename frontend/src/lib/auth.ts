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
			if (
				!user.email?.includes("@unlv.edu") &&
				!user.email?.includes("@unlv.nevada.edu")
			)
				return false

			// const response = await fetch(
			// 	"http://localhost:8000/api/validate-token/",
			// 	{
			// 		method: "GET", // Or POST if your Django expects it that way
			// 		headers: {
			// 			Authorization: `Bearer ${account?.access_token}`, // Google token
			// 			"Content-Type": "application/json",
			// 		},
			// 	}
			// )
		},
		async redirect({ url, baseUrl }) {
			if (url) return url
			return baseUrl
		},
		async jwt({ token }) {
			return token
		},
		async session({ session }) {
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
