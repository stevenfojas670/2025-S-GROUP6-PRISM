import { NextRequest, NextResponse } from "next/server"
import { jwtDecode } from "jwt-decode"

export async function middleware(request: NextRequest) {
	const currentTime = Math.floor(Date.now() / 1000)
	const access = request.cookies.get("prism-access")?.value
	const refresh = request.cookies.get("prism-refresh")?.value

	// If cookie doesn't exist then logout
	if (!access) {
		return NextResponse.redirect(new URL("/logout", request.url))
	}

	let access_exp: number | undefined
	let refresh_exp: number | undefined

	// Else check expiration
	try {
		const access_exp = jwtDecode<{ exp: number }>(access)?.exp
	} catch {
		return NextResponse.redirect(new URL("/logout", request.url))
	}

	// If the access token is expired, then check if the refresh token exists
	if (access_exp && currentTime > access_exp) {
		if (!refresh) {
			return NextResponse.redirect(new URL("/logout", request.url))
		}

		try {
			const refresh_exp = jwtDecode<{ exp: number }>(refresh)?.exp
		} catch {
			return NextResponse.redirect(new URL("/logout", request.url))
		}

		// If the refresh token is not expired then we'll call a refresh route that will call for a refresh token
		if (refresh_exp && currentTime < refresh_exp) {
			return NextResponse.redirect(new URL("/refresh", request.url))
		}

		// If the refresh token and access token are expired then we'll logout
		return NextResponse.redirect(new URL("/logout", request.url))
	}

	// If access token is not expired then we'll continue on as normal
	return NextResponse.next()
}
