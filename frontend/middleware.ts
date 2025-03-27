import { NextRequest, NextResponse } from "next/server"
import { jwtDecode } from "jwt-decode"

export async function middleware(request: NextRequest) {
	console.log("Middleware checking tokens for: ", request.nextUrl.pathname)
	const currentTime = Math.floor(Date.now() / 1000)
	const access = request.cookies.get("prism-access")?.value
	const refresh = request.cookies.get("prism-refresh")?.value

	// If both tokens missing then we just go to the login screen. We can't make any requests for new tokens
	// Django won't know who we are so we'll have to login again
	if (!access && !refresh) {
		return NextResponse.redirect(new URL("/login", request.url))
	}

	// Otherwise we will move on

	let access_exp: number | undefined
	let refresh_exp: number | undefined

	// If the access token exists then we'll check if its expired
	if (access) {
		// check expiration
		try {
			access_exp = jwtDecode<{ exp: number }>(access)?.exp
		} catch {
			return NextResponse.redirect(new URL("/logout", request.url))
		}
	}

	// If the access token is expired, then check if the refresh token exists
	if (access_exp && currentTime > access_exp) {
		// If the refresh token doesn't exist then we'll have to just go back to the login page, because we
		// can't request another from Django without any tokens unless we login again
		if (!refresh) {
			return NextResponse.redirect(new URL("/login", request.url))
		}

		// If the refresh token does exist, we'll check its expiration
		try {
			refresh_exp = jwtDecode<{ exp: number }>(refresh)?.exp
		} catch {
			return NextResponse.redirect(new URL("/logout", request.url))
		}

		// If the refresh token is not expired then we'll call a refresh route that will call for a refresh token
		if (refresh_exp && currentTime < refresh_exp) {
			return NextResponse.redirect(new URL("/refresh", request.url))
		}

		// If the refresh token and access token are expired then we'll have to login again
		return NextResponse.redirect(new URL("/login", request.url))
	}

	// If access token is not expired then we'll continue on as normal
	return NextResponse.next()
}

export const config = {
	matcher: [
		"/((?!_next|static|favicon.ico|logo.*\\.svg|login|logout|refresh|callback).*)",
	],
}
