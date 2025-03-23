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
			const response = await fetch("http://localhost:8000/api/logout", {
				method: "POST",
				credentials: "include",
			})

			const data = await response.json()

			if (session) await signOut({ callbackUrl: "/login" })

			if (!response.ok) {
				console.log("Error logging out of Django.", data)
				router.push("/login")
			}
		}

		logoutFlow()
	}, [])

	return <p>Logging you out...</p>
}
