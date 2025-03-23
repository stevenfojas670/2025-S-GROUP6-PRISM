import { status } from "@/utils/status"
import { NextRequest, NextResponse } from "next/server"
import { jwtDecode } from "jwt-decode"

export async function HasCookie(request: NextRequest) {
	const currentTime = Math.floor(Date.now() / 1000)
	const access = request.cookies.get("prism-access")?.value
	const refresh = request.cookies.get("prism-refresh")?.value

	if (!(access && refresh)) {
		return NextResponse.json({ status: status.HTTP_404_NOT_FOUND })
	}

	const access_exp = jwtDecode(access)["exp"]

	if (access_exp && currentTime > access_exp) {
		return NextResponse.json({ status: status.HTTP_401_UNAUTHORIZED })
	}

	return NextResponse.json({ status: status.HTTP_200_OK })
}
