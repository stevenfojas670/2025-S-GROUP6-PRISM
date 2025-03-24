import NextAuth, { DefaultSession, DefaultUser } from "next-auth"
import { DefaultJWT } from "next-auth/jwt"

declare module "next-auth" {
	interface Session extends DefaultSession {
		idToken?: string
	}

	interface User extends DefaultUser {
		accessToken?: string
		refreshToken?: string
		user_id?: number
	}
}

declare module "next-auth/jwt" {
	interface JWT extends DefaultJWT {
		accessToken?: string
		refreshToken?: string
		user_id?: number
		email?: string | null
	}
}
