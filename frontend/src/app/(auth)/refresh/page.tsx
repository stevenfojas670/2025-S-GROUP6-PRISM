"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function RefreshToken() {
	const router = useRouter()

	useEffect(() => {
		const refresh = async () => {
			try {
				const response = await fetch(
					"http://localhost:8000/api/token/refresh",
					{
						method: "post",
						credentials: "include",
					}
				)

				const data = await response.json()

				console.log("Token refreshed: ", data)

				// I'd like to reroute to where the user was
			} catch (err) {
				console.error(err)
				router.push("/login")
			}
		}

		refresh()
	}, [router])

	return <>Refreshing session...</>
}
