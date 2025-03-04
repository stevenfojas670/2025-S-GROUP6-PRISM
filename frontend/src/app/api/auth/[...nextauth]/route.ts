import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import type { NextApiRequest, NextApiResponse } from "next"

export default async function auth(req: NextApiRequest, res: NextApiResponse) {
	return await NextAuth({
		// Auth Options go here
		providers: [
			GoogleProvider({
				clientId: process.env.AUTH_GOOGLE_ID,
				clientSecret: process.env.AUTH_GOOGLE_SECRET,
			}),
		],
		callbacks: {
			async signIn({ user }) {
				// Only allow users with unlv domains to sign in
				if (
					user.email?.includes("@unlv.edu") ||
					user.email?.includes("@unlv.nevada.edu")
				)
					return true
				return false
			},
			async redirect({ url, baseUrl }) {
				// Return baseUrl for now
				return baseUrl
			},
			async jwt({ token }) {
				// Send to Django to be validated
				return token
			},
			async session({ session, token }) {
				// jwt() is called first and forwards the token here
				// Whatever has been added to the token will appear here
				// The session callback is called everytime the session is checked
				return session
			},
		},
	})
}
