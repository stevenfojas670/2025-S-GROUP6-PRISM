import { NextResponse, type NextRequest } from "next/server"
import { cookies } from "next/headers"
import { auth } from "@/lib/auth"
import { status } from "@/utils/status"
import { signOut } from "next-auth/react"

export async function POST(request: NextRequest) {
	// We're going to have to clear the cookies
	const session = await auth()
	const cookieStore = await cookies()

	if (!session?.accessToken)
		return NextResponse.json(
			{ error: "Not authenticated" },
			{ status: status.HTTP_401_UNAUTHORIZED }
		)

	const response = await fetch("http://localhost:8000/api/logout", {
		method: "post",
		headers: {
			Authorization: `Bearer ${session?.accessToken}`,
		},
		credentials: "include",
	})

	if (response.ok) {
		// Delete the cookie
		// Call NextAuth signout route
	}

	return response.json()
}
