"use client"

import { useEffect } from "react"
import { signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"

export default function LogoutPage() {
	const router = useRouter()
	const { data: session } = useSession()

	useEffect(() => {
		const logoutFlow = async () => {
			try {
				const checkCookie = await fetch(
					"http://localhost:3000/api/jwt/has-cookie",
					{
						method: "get",
					}
				)

				if (checkCookie.ok) {
					const response = await fetch("http://localhost:8000/api/logout", {
						method: "POST",
						credentials: "include",
					})

					const data = await response.json()

					if (response.ok) {
						console.log("Succesfully logged out of Django: ", data)
					} else {
						throw new Error("Error logging out of Django: ", data)
					}
				}

				if (session) await signOut({ callbackUrl: "/login" })
			} catch (err) {
				console.error(err)
			}
		}

		logoutFlow()
	}, [])

	return <p>Logging you out...</p>
}
